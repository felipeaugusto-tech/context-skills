#!/usr/bin/env python3
"""
QA-GenDD CI/CD Orchestrator

Chains QA-GenDD prompts through an LLM API to automate the AI testing stream (this order only):
  1. Evidence Review (engine/prompts/11-evidence.md)
  2. Defect Triage (engine/prompts/10-triage.md)
  3. Defect Drafting (engine/prompts/09-defects.md)
  4. Release Readiness (engine/prompts/12-release.md)

With --stack, also injects stack_context and the guidance markdown named in knowledge/stacks/{stack}.yml (guidance: field).

Outputs: qa-summary.md, defects.json, release-assessment.json
Exit code: 0 = release recommended, 1 = not recommended / insufficient evidence

Environment variables:
  QA_LLM_PROVIDER  - "anthropic" or "openai" (required)
  ANTHROPIC_API_KEY - required when provider is anthropic
  OPENAI_API_KEY    - required when provider is openai
  QA_MODEL          - optional model override
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from junitparser import JUnitXml
except ImportError:
    JUnitXml = None

try:
    import yaml
except ImportError:
    yaml = None


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMPTS_DIR = REPO_ROOT / "engine" / "prompts"
PROFILES_DIR = REPO_ROOT / "knowledge" / "stacks"

PROMPT_FILES = {
    "evidence": PROMPTS_DIR / "11-evidence.md",
    "triage": PROMPTS_DIR / "10-triage.md",
    "defects": PROMPTS_DIR / "09-defects.md",
    "release": PROMPTS_DIR / "12-release.md",
}

AVAILABLE_STACKS = ["python", "typescript", "java", "go", "cpp", "dotnet"]

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
}

SYSTEM_INSTRUCTION = (
    "You are a QA automation agent following the HatchWorks GenDD QA Operating Standards. "
    "Your outputs must be risk-first, evidence-based, traceable, and include confidence labels "
    "(High / Medium / Low) for every finding. Structure responses as valid JSON when instructed."
)


def load_prompt(key: str) -> str:
    path = PROMPT_FILES[key]
    text = path.read_text(encoding="utf-8")
    for header in (r"^## Prompt\s*\n", r"^## Instructions\s*\n"):
        match = re.search(header, text, re.MULTILINE)
        if match:
            return text[match.end():].strip()
    return text.strip()


def load_stack_profile(stack_name: str) -> dict:
    profile_path = PROFILES_DIR / f"{stack_name}.yml"
    if not profile_path.exists():
        print(f"WARNING: Stack profile not found: {profile_path}", file=sys.stderr)
        return {}

    if yaml is None:
        text = profile_path.read_text(encoding="utf-8")
        profile = {}
        for key in ("name", "stack_context", "artifact_format", "ci_example", "guidance"):
            match = re.search(rf"^{key}:\s*[|>]?\s*\n((?:\s+.+\n)*)", text, re.MULTILINE)
            if match:
                profile[key] = "\n".join(line.strip() for line in match.group(1).strip().split("\n"))
            else:
                match = re.search(rf'^{key}:\s*["\']?(.+?)["\']?\s*$', text, re.MULTILINE)
                if match:
                    profile[key] = match.group(1)
        return profile

    return yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}


def parse_junit(path: str) -> dict:
    if JUnitXml is None:
        return {"raw": Path(path).read_text(encoding="utf-8", errors="replace")[:8000]}

    xml = JUnitXml.fromfile(path)
    passed, failed, errored, skipped = [], [], [], []
    for suite in xml:
        for case in suite:
            entry = {"classname": case.classname or "", "name": case.name or "", "time": case.time or 0}
            if case.result is None:
                passed.append(entry)
            else:
                for r in case.result:
                    rtype = type(r).__name__
                    entry["message"] = getattr(r, "message", "") or ""
                    entry["text"] = (getattr(r, "text", "") or "")[:500]
                    if rtype == "Failure":
                        failed.append(entry)
                    elif rtype == "Error":
                        errored.append(entry)
                    elif rtype == "Skipped":
                        skipped.append(entry)
                    else:
                        failed.append(entry)

    return {
        "total": len(passed) + len(failed) + len(errored) + len(skipped),
        "passed": len(passed),
        "failed": len(failed),
        "errored": len(errored),
        "skipped": len(skipped),
        "failures": failed[:30],
        "errors": errored[:10],
    }


def parse_trx(path: str) -> dict:
    """Parse .NET TRX (Visual Studio Test Results) format."""
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        ns = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}

        results = root.findall(".//t:UnitTestResult", ns)
        if not results:
            results = root.findall(".//{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}UnitTestResult")

        passed, failed, errored, skipped = [], [], [], []
        for r in results:
            entry = {
                "classname": r.get("testName", "").rsplit(".", 1)[0] if "." in r.get("testName", "") else "",
                "name": r.get("testName", ""),
                "time": 0,
            }
            duration = r.get("duration", "")
            if duration:
                parts = duration.split(":")
                try:
                    entry["time"] = float(parts[-1]) if parts else 0
                except ValueError:
                    pass

            outcome = r.get("outcome", "").lower()
            if outcome == "passed":
                passed.append(entry)
            elif outcome in ("failed", "error"):
                output_el = r.find("t:Output/t:ErrorInfo/t:Message", ns)
                stacktrace_el = r.find("t:Output/t:ErrorInfo/t:StackTrace", ns)
                entry["message"] = (output_el.text or "")[:500] if output_el is not None else ""
                entry["text"] = (stacktrace_el.text or "")[:500] if stacktrace_el is not None else ""
                if outcome == "error":
                    errored.append(entry)
                else:
                    failed.append(entry)
            elif outcome in ("notexecuted", "inconclusive"):
                skipped.append(entry)
            else:
                passed.append(entry)

        return {
            "total": len(passed) + len(failed) + len(errored) + len(skipped),
            "passed": len(passed),
            "failed": len(failed),
            "errored": len(errored),
            "skipped": len(skipped),
            "failures": failed[:30],
            "errors": errored[:10],
        }
    except Exception as e:
        return {"raw": f"TRX parse error: {e}\n" + Path(path).read_text(encoding="utf-8", errors="replace")[:6000]}


def parse_test_results(path: str, artifact_format: str = "junit_xml") -> dict:
    if artifact_format == "trx" or path.endswith(".trx"):
        return parse_trx(path)
    return parse_junit(path)


def read_file_truncated(path: str, max_chars: int = 6000) -> str:
    if not path or not Path(path).exists():
        return ""
    return Path(path).read_text(encoding="utf-8", errors="replace")[:max_chars]


def build_system_instruction(stack_profile: dict) -> str:
    instruction = SYSTEM_INSTRUCTION
    stack_name = stack_profile.get("name", "unknown")
    blocks: list[str] = []

    stack_context = (stack_profile.get("stack_context") or "").strip()
    if stack_context:
        blocks.append(
            f"STACK CONTEXT ({stack_name}):\n{stack_context}\n"
            "Use this stack context to make your analysis framework-specific. "
            "Reference the specific test runners, assertion libraries, and common failure patterns "
            "for this stack when drafting defects and triage recommendations."
        )

    guidance_name = (stack_profile.get("guidance") or "").strip()
    if guidance_name:
        gpath = PROFILES_DIR / guidance_name
        if gpath.is_file():
            gtext = read_file_truncated(str(gpath), max_chars=8000)
            if gtext.strip():
                blocks.append(
                    f"STACK TESTING GUIDANCE ({guidance_name}):\n{gtext}\n"
                    "Use this guidance when interpreting failures, flakiness, and automation vs. manual tradeoffs."
                )

    if blocks:
        instruction += "\n\n" + "\n\n".join(blocks)
    return instruction


def call_llm(provider: str, model: str, system: str, user_message: str) -> str:
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    elif provider == "openai":
        import openai
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def run_stage(provider: str, model: str, system: str, prompt_key: str, context: str, json_output: bool = False) -> str:
    prompt_text = load_prompt(prompt_key)
    instruction = prompt_text.replace("[PASTE", "The following CI artifacts are the input. [PASTE")

    if json_output:
        instruction += "\n\nIMPORTANT: Return your response as valid JSON only, no markdown fences."

    user_message = f"{instruction}\n\n---\nCI ARTIFACTS:\n{context}"

    print(f"  Running {prompt_key} stage...", flush=True)
    return call_llm(provider, model, system, user_message)


def main():
    parser = argparse.ArgumentParser(description="QA-GenDD CI/CD AI Orchestrator")
    parser.add_argument("--test-results", required=True, help="Path to test results file (JUnit XML or TRX)")
    parser.add_argument("--coverage", default="", help="Path to coverage report (optional)")
    parser.add_argument("--logs", default="", help="Path to failure logs (optional)")
    parser.add_argument("--output", default="./qa-output", help="Output directory (default: ./qa-output)")
    parser.add_argument(
        "--stack", default="", choices=[""] + AVAILABLE_STACKS,
        help="Tech stack profile (optional). Loads knowledge/stacks/{stack}.yml for framework-aware analysis."
    )
    args = parser.parse_args()

    provider = os.environ.get("QA_LLM_PROVIDER", "").lower()
    if provider not in ("anthropic", "openai"):
        print("ERROR: Set QA_LLM_PROVIDER to 'anthropic' or 'openai'", file=sys.stderr)
        sys.exit(2)

    model = os.environ.get("QA_MODEL", DEFAULT_MODELS[provider])

    for pkey, ppath in PROMPT_FILES.items():
        if not ppath.exists():
            print(f"ERROR: Prompt file not found: {ppath}", file=sys.stderr)
            sys.exit(2)

    stack_profile = {}
    if args.stack:
        stack_profile = load_stack_profile(args.stack)
        if stack_profile:
            print(f"QA Orchestrator | provider={provider} model={model} stack={stack_profile.get('name', args.stack)}")
        else:
            print(f"QA Orchestrator | provider={provider} model={model} stack={args.stack} (profile not loaded)")
    else:
        print(f"QA Orchestrator | provider={provider} model={model} stack=(generic)")

    print(f"  test-results: {args.test_results}")
    print(f"  coverage: {args.coverage or '(none)'}")
    print(f"  logs: {args.logs or '(none)'}")

    system_instruction = build_system_instruction(stack_profile)
    artifact_format = stack_profile.get("artifact_format", "junit_xml")

    # --- Parse artifacts ---
    print("\n[1/5] Parsing test artifacts...")
    test_data = parse_test_results(args.test_results, artifact_format)
    coverage_text = read_file_truncated(args.coverage)
    logs_text = read_file_truncated(args.logs)

    artifact_context = f"TEST RESULTS:\n{json.dumps(test_data, indent=2)}\n"
    if coverage_text:
        artifact_context += f"\nCOVERAGE REPORT:\n{coverage_text}\n"
    if logs_text:
        artifact_context += f"\nFAILURE LOGS:\n{logs_text}\n"

    # --- Stage 1: Evidence Review ---
    print("\n[2/5] Evidence Review...")
    evidence_result = run_stage(provider, model, system_instruction, "evidence", artifact_context)

    # --- Stage 2: Defect Triage ---
    print("\n[3/5] Defect Triage...")
    triage_context = f"EVIDENCE REVIEW:\n{evidence_result}\n\nORIGINAL ARTIFACTS:\n{artifact_context}"
    triage_result = run_stage(provider, model, system_instruction, "triage", triage_context)

    # --- Stage 3: Defect Drafting ---
    print("\n[4/5] Defect Drafting...")
    defect_context = (
        f"TRIAGE RESULTS:\n{triage_result}\n\n"
        f"EVIDENCE REVIEW:\n{evidence_result}\n\n"
        "Draft defects ONLY for findings with High or Medium confidence that are recommended for bug creation. "
        "Skip Low-confidence findings — flag them for human review instead.\n"
        "Return the result as a JSON array of defect objects."
    )
    defects_result = run_stage(provider, model, system_instruction, "defects", defect_context, json_output=True)

    # --- Stage 4: Release Readiness ---
    print("\n[5/5] Release Readiness...")
    release_context = (
        f"PIPELINE SUMMARY:\n"
        f"- Stack: {stack_profile.get('name', 'generic')}\n"
        f"- Total tests: {test_data.get('total', 'unknown')}\n"
        f"- Passed: {test_data.get('passed', 'unknown')}\n"
        f"- Failed: {test_data.get('failed', 'unknown')}\n"
        f"- Errored: {test_data.get('errored', 'unknown')}\n"
        f"- Skipped: {test_data.get('skipped', 'unknown')}\n\n"
        f"EVIDENCE REVIEW:\n{evidence_result}\n\n"
        f"TRIAGE SUMMARY:\n{triage_result}\n\n"
        f"DEFECT DRAFTS:\n{defects_result}\n"
    )
    release_result = run_stage(provider, model, system_instruction, "release", release_context)

    # --- Write outputs ---
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    stack_label = stack_profile.get("name", "generic")
    summary_md = (
        "# QA Orchestrator Summary\n\n"
        f"**Provider:** {provider} | **Model:** {model} | **Stack:** {stack_label}\n\n"
        "---\n\n"
        "## Evidence Review\n\n"
        f"{evidence_result}\n\n"
        "---\n\n"
        "## Defect Triage\n\n"
        f"{triage_result}\n\n"
        "---\n\n"
        "## Release Readiness\n\n"
        f"{release_result}\n"
    )

    ci_example = stack_profile.get("ci_example", "")
    if ci_example:
        summary_md += (
            "\n---\n\n"
            f"## Stack CI Example ({stack_label})\n\n"
            f"```bash\n{ci_example.strip()}\n```\n"
        )

    (out_dir / "qa-summary.md").write_text(summary_md, encoding="utf-8")
    (out_dir / "defects.json").write_text(defects_result, encoding="utf-8")

    release_json = json.dumps({
        "assessment": release_result,
        "provider": provider,
        "model": model,
        "stack": stack_label,
        "test_total": test_data.get("total"),
        "test_passed": test_data.get("passed"),
        "test_failed": test_data.get("failed"),
    }, indent=2)
    (out_dir / "release-assessment.json").write_text(release_json, encoding="utf-8")

    print(f"\nOutputs written to {out_dir}/")
    print(f"  - qa-summary.md")
    print(f"  - defects.json")
    print(f"  - release-assessment.json")

    # --- Exit code ---
    release_lower = release_result.lower()
    if "release recommended" in release_lower and "not recommended" not in release_lower:
        print("\nResult: RELEASE RECOMMENDED (exit 0)")
        sys.exit(0)
    else:
        print("\nResult: RELEASE NOT RECOMMENDED or INSUFFICIENT EVIDENCE (exit 1)")
        sys.exit(1)


if __name__ == "__main__":
    main()
