#!/usr/bin/env python3
"""
analyze_test_gaps.py — inventory tests, map them to sources, and rank untested code
by risk using evidence from git. No dependencies.

    python3 analyze_test_gaps.py .
    python3 analyze_test_gaps.py src/payments --format json
    python3 analyze_test_gaps.py . --coverage coverage/coverage-summary.json
    python3 analyze_test_gaps.py . --months 12 --top 25

Risk is exposure × (likelihood + cost), where likelihood comes from change frequency
and past bug-fix churn, and cost comes from fan-in and data-mutation signals. The
score is a sort order, not a measurement — every underlying signal is reported so
the ranking can be argued with.

Also flags tests that cannot fail (no assertions, mock-only, snapshot-only, skipped,
focused). Coverage tools count these as covered, which is why reported coverage and
actual protection diverge.
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".py", ".rb", ".go", ".rs", ".java",
            ".kt", ".cs", ".php", ".swift", ".scala", ".ex", ".exs"}

TEST_HINTS = re.compile(r"(^|/)(tests?|specs?|__tests__)(/|$)|"
                        r"[._-](test|spec)s?\.[a-z]+$|"
                        r"(^|/)test_[^/]+$", re.I)

SKIP_DIRS = re.compile(r"(^|/)(node_modules|\.git|dist|build|vendor|target|"
                       r"\.venv|venv|__pycache__|coverage|\.next|out)(/|$)")

FIX_COMMIT = re.compile(r"(?i)\b(fix|bug|hotfix|revert|patch|regress|broken|"
                        r"incident|outage)\b")

ASSERT_PAT = re.compile(r"\b(expect|assert|assertEqual|assertTrue|assertRaises|"
                        r"should|require\.(Equal|NoError)|assert_that|"
                        r"toBe|toEqual|toThrow|assertThat)\b")
MOCK_ASSERT = re.compile(r"(toHaveBeenCalled|assert_called|verify\(|\.calledWith|"
                         r"toHaveBeenNthCalled|assertCalled)")
SNAPSHOT = re.compile(r"(toMatchSnapshot|toMatchInlineSnapshot|assert_snapshot)")
SKIPPED = re.compile(r"(\.skip\s*\(|\bxit\s*\(|\bxdescribe\s*\(|"
                     r"@pytest\.mark\.skip|\bt\.Skip\(|@Ignore\b|\bpending\s*\()")
FOCUSED = re.compile(r"(\.only\s*\(|\bfdescribe\s*\(|\bfit\s*\()")
TAUTOLOGY = re.compile(r"expect\(\s*(true|1|'.'|\"\.\")\s*\)\s*\.\s*(toBe|toEqual)"
                       r"\(\s*(true|1|'.'|\"\.\")\s*\)|assert\s+True\s*$")
FAILURE_CASE = re.compile(r"(?i)(throw|error|reject|invalid|fail|denied|forbidden|"
                          r"unauthor|404|403|401|409|422|500|timeout|empty|null|"
                          r"missing|expired|duplicate)")
MUTATES = re.compile(r"(?i)\b(INSERT|UPDATE|DELETE|DROP|save\(|create\(|destroy\(|"
                     r"\.write\(|commit\(|persist\()")


def git(*args, cwd="."):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True,
                              check=True, cwd=cwd).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def tracked_files(root, scope):
    out = git("ls-files", cwd=root)
    if out:
        files = [f for f in out.splitlines() if f]
    else:
        files = [str(p.relative_to(root)) for p in Path(root).rglob("*") if p.is_file()]
    files = [f for f in files if not SKIP_DIRS.search(f)]
    if scope and scope != ".":
        files = [f for f in files if f.startswith(scope.rstrip("/") + "/") or f == scope]
    return files


def is_test(path):
    return bool(TEST_HINTS.search(path))


def base_name(path):
    n = Path(path).name
    for suf in (".test", ".spec", "_test", "_spec", "-test", "-spec"):
        stem = Path(n).stem
        if stem.endswith(suf):
            stem = stem[: -len(suf)]
            return stem.lower()
    stem = Path(n).stem
    if stem.startswith("test_"):
        return stem[5:].lower()
    if stem.startswith("test"):
        return stem[4:].lower() or stem.lower()
    return stem.lower()


def churn(root, path, months):
    since = f"--since={months}.months.ago"
    log = git("log", since, "--format=%s", "--", path, cwd=root)
    subjects = [s for s in log.splitlines() if s]
    fixes = [s for s in subjects if FIX_COMMIT.search(s)]
    authors = git("log", since, "--format=%an", "--", path, cwd=root).splitlines()
    return len(subjects), len(fixes), len(set(a for a in authors if a))


def fan_in(root, path, all_code):
    """Crude but useful: how many other files reference this module's name."""
    stem = Path(path).stem
    if len(stem) < 4 or stem in ("index", "main", "utils", "types", "__init__"):
        return 0
    out = git("grep", "-l", "--fixed-strings", stem, "--", cwd=root)
    if not out:
        return 0
    refs = {f for f in out.splitlines()
            if f and f != path and not is_test(f) and not SKIP_DIRS.search(f)}
    return len(refs)


def read(root, path):
    try:
        return (Path(root) / path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def audit_test_file(text):
    """Return the reasons this test file may not be able to fail."""
    problems = []
    body = re.sub(r"^\s*(//|#).*$", "", text, flags=re.M)
    has_assert = bool(ASSERT_PAT.search(body))
    only_mock = has_assert and MOCK_ASSERT.search(body) and \
        not re.search(r"(toBe|toEqual|assertEqual|assert_that|toThrow|assert\s+\w+\s*==)", body)
    if not has_assert:
        problems.append("no assertions — passes as long as nothing throws")
    if only_mock:
        problems.append("asserts only on mocks — verifies the doubles, not the system")
    if SNAPSHOT.search(body) and not re.search(r"(toBe|toEqual|assertEqual)", body):
        problems.append("snapshot-only — detects change, not correctness")
    if FOCUSED.search(body):
        problems.append("FOCUSED (.only/fit) — silently disables sibling tests")
    if SKIPPED.search(body):
        problems.append("contains skipped tests")
    if TAUTOLOGY.search(body):
        problems.append("tautological assertion")
    if has_assert and not FAILURE_CASE.search(body):
        problems.append("no failure/error case — only the happy path")
    return problems


def load_coverage(path):
    """Accept Istanbul json-summary or Python coverage.json. Returns {file: fraction}."""
    try:
        data = json.loads(Path(path).read_text())
    except Exception as e:
        print(f"! Could not read coverage from {path}: {e}", file=sys.stderr)
        return {}
    cov = {}
    if "files" in data and isinstance(data["files"], dict):        # coverage.py
        for f, v in data["files"].items():
            s = (v.get("summary") or {})
            tot = s.get("num_statements") or 0
            if tot:
                cov[f.lstrip("./")] = (s.get("covered_lines") or 0) / tot
    else:                                                          # istanbul
        for f, v in data.items():
            if f == "total" or not isinstance(v, dict):
                continue
            pct = ((v.get("lines") or {}).get("pct"))
            if isinstance(pct, (int, float)):
                cov[f.lstrip("./")] = pct / 100.0
    return cov


def norm(v, mx):
    return 0.0 if not mx else v / mx


def _test_label(r):
    if not r["tests"]:
        return "NO"
    if r["weak_tests"] and len(r["weak_tests"]) == len(r["tests"]):
        return "weak"
    return "yes"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--format", choices=["table", "json"], default="table")
    ap.add_argument("--coverage", help="Istanbul json-summary or coverage.py json")
    ap.add_argument("--months", type=int, default=6)
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args()

    p = Path(a.path)
    root = str(p if p.is_dir() and (p / ".git").exists() else Path("."))
    root = str(Path(git("rev-parse", "--show-toplevel", cwd=str(p) if p.is_dir() else ".").strip()
                    or "."))
    scope = "" if Path(a.path).resolve() == Path(root).resolve() else \
        str(Path(a.path).resolve().relative_to(Path(root).resolve()))

    files = tracked_files(root, scope)
    tests = [f for f in files if is_test(f)]
    sources = [f for f in files if not is_test(f) and Path(f).suffix in CODE_EXT]

    test_index = defaultdict(list)
    for t in tests:
        test_index[base_name(t)].append(t)

    coverage = load_coverage(a.coverage) if a.coverage else {}

    weak = []
    weak_files = set()
    for t in tests:
        problems = audit_test_file(read(root, t))
        if problems:
            weak.append({"file": t, "problems": problems})
            weak_files.add(t)

    rows = []
    for s in sources:
        commits, fixes, authors = churn(root, s, a.months)
        text = read(root, s)
        lines = text.count("\n") + 1
        mapped = test_index.get(base_name(s), [])
        cov = coverage.get(s)
        rows.append({
            "file": s, "lines": lines, "commits": commits, "fix_commits": fixes,
            "authors": authors, "tests": mapped,
            "coverage": None if cov is None else round(cov, 3),
            "mutates": bool(MUTATES.search(text)),
            "fan_in": fan_in(root, s, sources),
            # A mapped test that cannot fail is not protection. Tracking this here is
            # what stops "has a test file" from being read as "covered".
            "weak_tests": [t for t in mapped if t in weak_files],
        })

    mx = {k: max([r[k] for r in rows], default=0)
          for k in ("commits", "fix_commits", "lines", "fan_in")}
    for r in rows:
        all_weak = r["tests"] and len(r["weak_tests"]) == len(r["tests"])
        if all_weak:
            # Every mapped test was flagged as unable to fail. Treat this as nearly
            # untested even when a coverage tool reports the lines as executed —
            # execution without assertion is exactly what coverage cannot see.
            exposure = 0.9
        elif r["coverage"] is not None:
            # Measurement beats the naming heuristic: a file may be exercised by a
            # test whose filename does not map to it.
            exposure = 1.0 - r["coverage"]
        elif not r["tests"]:
            exposure = 1.0
        else:
            exposure = 0.4          # a test exists; its quality is unverified
        likelihood = (norm(r["commits"], mx["commits"])
                      + 2 * norm(r["fix_commits"], mx["fix_commits"])
                      + 0.5 * norm(r["lines"], mx["lines"]))
        cost = norm(r["fan_in"], mx["fan_in"]) + (0.5 if r["mutates"] else 0.0)
        r["exposure"] = round(exposure, 2)
        r["risk"] = round(exposure * (likelihood + cost), 3)

    rows.sort(key=lambda r: -r["risk"])
    untested = [r for r in rows if not r["tests"]]

    if a.format == "json":
        print(json.dumps({
            "scope": scope or ".", "months": a.months,
            "coverage_data": bool(coverage),
            "totals": {"source_files": len(sources), "test_files": len(tests),
                       "untested_source_files": len(untested),
                       "weak_test_files": len(weak)},
            "weak_tests": weak, "ranked": rows[: a.top],
        }, indent=2))
        return 0

    print(f"\nTest gap analysis — {root}{'/' + scope if scope else ''}")
    print(f"Window: last {a.months} months of git history")
    print("=" * 78)
    print(f"\n{len(sources)} source file(s), {len(tests)} test file(s), "
          f"{len(untested)} source file(s) with no mapped test")
    if coverage:
        print("Coverage data: loaded — exposure uses measured line coverage.")
    else:
        print("Coverage data: NONE — exposure inferred from test-file mapping only.")
        print("  Run the project's coverage tool and pass --coverage for a real basis.")

    if weak:
        print(f"\nTESTS THAT MAY NOT BE ABLE TO FAIL ({len(weak)})")
        print("-" * 78)
        print("Coverage tools count these as covered. Confirm by reading them.")
        for w in weak[:15]:
            print(f"\n  {w['file']}")
            for prob in w["problems"]:
                flag = "  ⚠ " if "FOCUSED" in prob else "    "
                print(f"{flag}{prob}")
    else:
        print("\nNo weak-test patterns detected in the test files scanned.")

    print(f"\nHIGHEST-RISK FILES (top {min(a.top, len(rows))})")
    print("-" * 78)
    print(f"{'risk':>6}  {'exp':>4}  {'chg':>4}  {'fix':>4}  {'fan':>4}  "
          f"{'cov':>5}  {'test':>5}  file")
    for r in rows[: a.top]:
        cov = "—" if r["coverage"] is None else f"{int(r['coverage']*100)}%"
        print(f"{r['risk']:>6.2f}  {r['exposure']:>4.2f}  {r['commits']:>4}  "
              f"{r['fix_commits']:>4}  {r['fan_in']:>4}  {cov:>5}  "
              f"{_test_label(r):>5}  {r['file']}"
              f"{'  [mutates data]' if r['mutates'] else ''}"
              f"{'  [mapped test cannot fail]' if r['weak_tests'] and len(r['weak_tests']) == len(r['tests']) else ''}")

    print("\n" + "-" * 78)
    print("risk = exposure × (churn + 2×fix-churn + 0.5×size + fan-in + mutation)")
    print("Fix-churn is doubled: it reflects defects that actually happened.")
    print("This is a sort order, not a measurement — the signals are shown so the")
    print("ranking can be argued with. A high-churn untested file that mutates data")
    print("is where to look first; confirm against the critical flows the team named.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
