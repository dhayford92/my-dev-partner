#!/usr/bin/env python3
"""
Pre-commit mechanical review of changed files. Read-only. Cross-platform.

Runs the deterministic subset of the review checklist so the human/AI review can focus on
correctness + logic. Findings are grouped blocking / should-fix / nitpick.

Usage:
    python review_changes.py --project <ROOT> [--base HEAD] [--all]

- default: reviews files changed vs --base (git). --all reviews every src/*.py.
This is a PRE-FILTER, not the whole review. Correctness/security/logic still need reading.
"""
import argparse
import ast
import re
import subprocess
from pathlib import Path

BLOCK, SHOULD, NIT = "BLOCKING", "SHOULD-FIX", "NITPICK"


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def changed_py_files(project: Path, base: str, review_all: bool) -> list[Path]:
    if not review_all:
        try:
            out = subprocess.run(["git", "-C", str(project), "diff", "--name-only", base],
                                 capture_output=True, text=True, timeout=15)
            files = [project / f for f in out.stdout.splitlines()
                     if f.endswith(".py") and (project / f).exists()]
            if files:
                return files
        except Exception:
            pass
    return [f for f in (project / "src").rglob("*.py") if "__pycache__" not in str(f)]


def check_file(path: Path, project: Path) -> list[tuple[str, str, str]]:
    """Return list of (severity, location, message)."""
    findings = []
    rel = path.relative_to(project).as_posix()
    text = read(path)

    # 1. Compiles (syntax) — blocking
    try:
        ast.parse(text)
    except SyntaxError as e:
        findings.append((BLOCK, f"{rel}:{e.lineno}", f"syntax error: {e.msg}"))
        return findings  # can't analyse further

    # 2. Hardcoded secrets — blocking
    for m in re.finditer(r'(sk_live_[A-Za-z0-9]+|AKIA[0-9A-Z]{16}|-----BEGIN (RSA )?PRIVATE KEY)', text):
        findings.append((BLOCK, rel, f"possible hardcoded secret: {m.group(1)[:12]}..."))
    # lowercase identifier only (skips ErrorCodes-style UPPER_CASE constants), value not an
    # enum-like ALL_CAPS token, not sourced from env/Field.
    for m in re.finditer(r'(?<![A-Za-z_])(password|secret|api_key)\s*=\s*["\']([^"\']{6,})["\']', text):
        value = m.group(2)
        near = text[max(0, m.start()-50):m.start()]
        if re.fullmatch(r'[A-Z0-9_]+', value):        # e.g. WEAK_PASSWORD (a code constant)
            continue
        if "os.environ" in near or "getenv" in near or "Field(" in m.group(0):
            continue
        findings.append((SHOULD, rel, f"hardcoded-looking credential: {m.group(0)[:40]}..."))

    # 3. print() instead of logger — should-fix
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(r'\bprint\(', line) and not line.strip().startswith("#"):
            findings.append((SHOULD, f"{rel}:{i}", "print() used; use the stdlib logger"))
            break

    # Router-specific
    if "/routers/" in rel:
        # 4. route without response_model — should-fix
        for m in re.finditer(r'@\w+\.(get|post|put|patch|delete)\((.*?)\)\s*\n(?:@[^\n]+\n)*\s*async def (\w+)',
                             text, re.DOTALL):
            deco_args, fn = m.group(2), m.group(3)
            if "response_model" not in deco_args:
                findings.append((NIT, rel, f"route '{fn}' has no response_model"))
        # 5. auth-sensitive route without a rate limit — should-fix
        # @limiter.limit may sit ABOVE or BELOW the @router.post line — check both sides.
        for m in re.finditer(r'@\w+\.(post)\(\s*["\']([^"\']*)["\']', text):
            path_ = m.group(2)
            if re.search(r'login|register|otp|forgot|reset|refresh', path_, re.I):
                window = text[max(0, m.start()-160):m.start()+300]
                if "limiter.limit" not in window:
                    findings.append((SHOULD, rel, f"auth route '{path_}' missing @limiter.limit"))

    # Controller-specific
    if "controller" in rel:
        # 6. except Exception without logging — should-fix
        for m in re.finditer(r'except Exception[^\n]*:\n((?:\s+[^\n]*\n){1,4})', text):
            body = m.group(1)
            if "logger." not in body and "raise" not in body:
                findings.append((SHOULD, rel, "except Exception block without logger/raise (swallowed error)"))
                break
        # 7. mutation without activity logging — nitpick
        if re.search(r'\.create\(|\.save\(|\.delete\(', text) and "ActivityService" not in text:
            findings.append((NIT, rel, "mutation present but no ActivityService logging in this controller"))

    # Model-specific
    if "/models/" in rel:
        if re.search(r'(amount|price|balance|fee)\w*\s*=\s*fields\.FloatField', text, re.I):
            findings.append((NIT, rel, "money-like column uses FloatField; prefer DecimalField"))
        names = re.findall(r'related_name\s*=\s*["\']([^"\']+)["\']', text)
        # (target-aware clash detection is in backend-reverse-engineer/map_codebase.py)
        if "Model)" in text and "deleted_at" not in text and "abstract = True" not in text and "table =" in text:
            findings.append((NIT, rel, "model has no deleted_at soft-delete column"))

    # Error style drift — should-fix
    if "register_exception_handlers" in text or re.search(r'detail\s*=\s*\{', text):
        findings.append((SHOULD, rel, "non-canonical error style (global handler / dict detail); "
                                      "use HTTPException(detail=str, headers=X-Error-Code)"))

    return findings


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--base", default="HEAD")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    files = changed_py_files(project, args.base, args.all)

    all_findings = []
    for f in files:
        all_findings.extend(check_file(f, project))

    print(f"== Mechanical review: {len(files)} file(s) ==\n")
    for sev in (BLOCK, SHOULD, NIT):
        group = [x for x in all_findings if x[0] == sev]
        print(f"{sev} ({len(group)}):")
        for _, loc, msg in group:
            print(f"  - {loc}: {msg}")
        print()
    print("(Mechanical pre-filter only. Correctness, security, and logic still require reading.)")
    # Non-zero exit if any blocking finding, for CI hooks.
    raise SystemExit(1 if any(x[0] == BLOCK for x in all_findings) else 0)


if __name__ == "__main__":
    main()
