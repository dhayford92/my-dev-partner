#!/usr/bin/env python3
"""
Heuristic security scan of a FastAPI + Tortoise project. Read-only. Cross-platform.

Flags the mechanical security smells; a real audit still reads the code (see the checklist).
Findings carry HIGH / MED / LOW severity.

Usage:
    python security_scan.py --project <ROOT> [--json]

Checks: permissive CORS, committed/hardcoded secrets, .env gitignore, raw-SQL injection,
mutating routes without an auth guard, auth endpoints without rate limits, PII in logs,
secrets leaked in response schemas, privilege-escalation (role from request body), debug/docs.
"""
import argparse
import json
import re
from pathlib import Path

HIGH, MED, LOW = "HIGH", "MED", "LOW"
PUBLIC = re.compile(r'login|register|signup|otp|forgot|reset|verify|refresh|webhook|health|'
                    r'public|activate|activation|accept-invite|/urls', re.I)


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def iter_py(root: Path):
    for f in root.rglob("*.py"):
        if "__pycache__" in str(f) or "/venv/" in str(f).replace("\\", "/"):
            continue
        yield f


def scan(project: Path) -> list[dict]:
    F = []
    def add(sev, cat, loc, msg): F.append({"severity": sev, "category": cat, "location": loc, "message": msg})

    src = project / "src"

    # CORS
    for f in [project / "main.py", *((src / "views").glob("*.py") if (src / "views").exists() else [])]:
        t = read(f)
        if "CORSMiddleware" in t:
            origins = re.search(r'allow_origins\s*=\s*(\[[^\]]*\])', t)
            creds = re.search(r'allow_credentials\s*=\s*True', t)
            if origins and '"*"' in origins.group(1) and creds:
                add(HIGH, "cors", f.name,
                    'allow_origins=["*"] with allow_credentials=True — wildcard + credentials is unsafe')

    # Secrets: .env gitignored?
    gi = read(project / ".gitignore")
    if (project / ".env").exists() and ".env" not in gi:
        add(HIGH, "secrets", ".env", ".env exists but is not in .gitignore — risk of committing secrets")

    # Hardcoded secrets in code
    for f in iter_py(project):
        t = read(f)
        for m in re.finditer(r'(sk_live_[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA )?PRIVATE KEY)', t):
            add(HIGH, "secrets", f.name, f"hardcoded secret/key: {m.group(1)[:14]}...")
        for m in re.finditer(r'(?<![A-Za-z_])(secret|api_key|password)\s*=\s*["\']([^"\']{8,})["\']', t):
            v = m.group(2)
            near = t[max(0, m.start()-50):m.start()]
            if re.fullmatch(r'[A-Z0-9_]+', v) or "os.environ" in near or "getenv" in near or "Field(" in m.group(0):
                continue
            add(MED, "secrets", f.name, f"hardcoded-looking credential: {m.group(0)[:40]}...")

    # Raw SQL injection (string-built SQL into execute_query/raw)
    for f in iter_py(src) if src.exists() else []:
        t = read(f)
        for m in re.finditer(r'(execute_query|\.raw)\(\s*(f["\']|["\'][^"\']*["\']\s*[%+]|.*\.format\()', t):
            snippet = t[m.start():m.start()+80].splitlines()[0]
            add(HIGH, "injection", f.name, f"string-built SQL into {m.group(1)}: {snippet.strip()[:60]}")

    # Mutating routes without an auth guard
    for f in (src.rglob("routers/*.py") if src.exists() else []):
        t = read(f)
        for m in re.finditer(r'@\w+\.(post|put|patch|delete)\(\s*["\']([^"\']*)["\'].*?\n(?:@[^\n]+\n)*\s*async def \w+\((.*?)\):',
                             t, re.DOTALL):
            method, path_, params = m.group(1), m.group(2), m.group(3)
            has_guard = re.search(r'Current\w*User|PortalUser|PortalAdmin|PortalFinance|Depends\(|get_current', params)
            if not has_guard and not PUBLIC.search(path_) and not PUBLIC.search(f.name):
                add(HIGH, "authz", f.name, f"{method.upper()} '{path_}' has no auth guard dependency")

    # Auth endpoints missing rate limit
    for f in (src.rglob("routers/*.py") if src.exists() else []):
        t = read(f)
        for m in re.finditer(r'@\w+\.post\(\s*["\']([^"\']*)["\']', t):
            if re.search(r'login|register|otp|forgot|reset', m.group(1), re.I):
                if "limiter.limit" not in t[max(0, m.start()-160):m.start()+300]:
                    add(MED, "rate-limit", f.name, f"auth route '{m.group(1)}' missing @limiter.limit")

    # PII in logs
    for f in iter_py(src) if src.exists() else []:
        t = read(f)
        for m in re.finditer(r'logger\.\w+\(\s*f["\'][^"\']*\{[^}]*(email|phone|password|token|otp|card)[^}]*\}', t, re.I):
            if "redact(" not in t[m.start():m.start()+120]:
                add(MED, "pii", f.name, f"possible PII in a log line ({m.group(1)}) without redact()")
                break

    # Secrets in response schemas
    for f in (src.rglob("schemas/**/*.py") if src.exists() else []):
        t = read(f)
        for m in re.finditer(r'class (\w*(Response|Out|Detail|Table)\w*)\b[^\n]*:\n((?:\s+\w+\s*:[^\n]*\n)+)', t):
            body = m.group(3)
            # password/hash/secret in a response is always a leak; bare `token` is often the
            # intended auth-response payload, so don't flag it here.
            leak = re.search(r'\b(password|password_hashed|hashed_password|secret|api_key|password_hash)\s*:', body)
            if leak:
                add(HIGH, "leak", f.name, f"response schema '{m.group(1)}' exposes '{leak.group(1)}'")

    # Privilege escalation: role assigned from request body
    for f in (src.rglob("controllers/*.py") if src.exists() else []):
        t = read(f)
        for m in re.finditer(r'role\s*=\s*(body|data|payload|request)\.\w*role', t):
            add(MED, "priv-esc", f.name, f"role set from client input ({m.group(0)}) — verify it can't self-escalate")

    # Debug / docs exposure
    st = read(project / "configs" / "settings.py")
    if re.search(r'DEBUG[^\n]*default\s*=\s*True', st):
        add(LOW, "config", "settings.py", "DEBUG defaults to True — ensure prod .env sets it False (docs are debug-gated)")

    return F


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    if not (project / "src").exists():
        raise SystemExit(f"No src/ in {project}")

    findings = scan(project)
    if args.json:
        print(json.dumps(findings, indent=2)); return

    print(f"== Security scan: {project} ==\n")
    for sev in (HIGH, MED, LOW):
        g = [x for x in findings if x["severity"] == sev]
        print(f"{sev} ({len(g)}):")
        for x in g:
            print(f"  - [{x['category']}] {x['location']}: {x['message']}")
        print()
    print("(Heuristic pre-scan. A real audit reads auth flows, ownership scoping, and deps — "
          "run `pip-audit` for dependency CVEs. See the audit checklist.)")
    raise SystemExit(1 if any(x["severity"] == HIGH for x in findings) else 0)


if __name__ == "__main__":
    main()
