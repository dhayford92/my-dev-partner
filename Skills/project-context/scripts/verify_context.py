#!/usr/bin/env python3
"""
Audit .claude/context/ against the actual codebase and report staleness. Read-only.
Cross-platform. Exit code is 0 unless --strict (then non-zero when drift is found).

Checks:
  - context files present
  - every Tortoise table (models) is mentioned in SCHEMA.md
  - every route (routers) is mentioned in API.md
  - CHANGELOG.md newest date vs newest src/ modification (possible missing entry)

Usage:
    python verify_context.py --project <ROOT> [--strict]
"""
import argparse
import datetime
import re
from pathlib import Path

CTX_FILES = ["OVERVIEW.md", "ARCHITECTURE.md", "SCHEMA.md", "API.md", "DECISIONS.md", "CHANGELOG.md"]
METHODS = "get|post|put|patch|delete"


def find_tables(project: Path) -> list[str]:
    tables = []
    for f in (project / "src" / "apps").rglob("models/*.py"):
        for m in re.finditer(r'table\s*=\s*["\']([^"\']+)["\']', f.read_text(encoding="utf-8")):
            tables.append(m.group(1))
    return sorted(set(tables))


def find_routes(project: Path) -> list[str]:
    """Return list of '<router_prefix><route_path>' fragments, e.g. /client/auth/login."""
    routes = []
    for f in (project / "src" / "apps").rglob("routers/*.py"):
        text = f.read_text(encoding="utf-8")
        # map router variable -> prefix
        prefixes = {}
        for m in re.finditer(r'(\w+)\s*=\s*APIRouter\(([^)]*)\)', text):
            var, args = m.group(1), m.group(2)
            pm = re.search(r'prefix\s*=\s*["\']([^"\']*)["\']', args)
            prefixes[var] = pm.group(1) if pm else ""
        for m in re.finditer(rf'@(\w+)\.({METHODS})\(\s*["\']([^"\']*)["\']', text):
            var, _method, path = m.group(1), m.group(2), m.group(3)
            prefix = prefixes.get(var, "")
            routes.append(f"{prefix}{path}")
    return sorted(set(routes))


def newest_src_mtime(project: Path) -> datetime.date | None:
    latest = None
    for f in (project / "src").rglob("*.py"):
        if "__pycache__" in str(f):
            continue
        d = datetime.date.fromtimestamp(f.stat().st_mtime)
        if latest is None or d > latest:
            latest = d
    return latest


def newest_changelog_date(changelog: Path) -> datetime.date | None:
    if not changelog.exists():
        return None
    dates = re.findall(r'(\d{4}-\d{2}-\d{2})', changelog.read_text(encoding="utf-8"))
    parsed = []
    for d in dates:
        try:
            parsed.append(datetime.date.fromisoformat(d))
        except ValueError:
            pass
    return max(parsed) if parsed else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    ctx = project / ".claude" / "context"
    problems = 0

    print(f"== Context audit: {project} ==\n")

    # 1. files present
    missing_files = [f for f in CTX_FILES if not (ctx / f).exists()]
    if missing_files:
        problems += len(missing_files)
        print("MISSING context files:")
        for f in missing_files:
            print(f"  - {f}")
        print("  (run init_context.py)\n")
    else:
        print("context files: all present\n")

    schema_text = (ctx / "SCHEMA.md").read_text(encoding="utf-8") if (ctx / "SCHEMA.md").exists() else ""
    api_text = (ctx / "API.md").read_text(encoding="utf-8") if (ctx / "API.md").exists() else ""

    # 2. tables vs SCHEMA.md
    tables = find_tables(project)
    undoc_tables = [t for t in tables if t not in schema_text]
    print(f"tables in code: {len(tables)}")
    if undoc_tables:
        problems += len(undoc_tables)
        print("  NOT documented in SCHEMA.md:")
        for t in undoc_tables:
            print(f"    - {t}")
    else:
        print("  all tables documented in SCHEMA.md")
    print()

    # 3. routes vs API.md
    routes = find_routes(project)
    undoc_routes = [r for r in routes if r and r not in api_text]
    print(f"routes in code: {len(routes)}")
    if undoc_routes:
        problems += len(undoc_routes)
        print("  NOT documented in API.md:")
        for r in undoc_routes:
            print(f"    - {r}")
    else:
        print("  all routes documented in API.md")
    print()

    # 4. changelog staleness
    src_date = newest_src_mtime(project)
    cl_date = newest_changelog_date(ctx / "CHANGELOG.md")
    print(f"newest src change: {src_date}   newest CHANGELOG date: {cl_date}")
    if src_date and cl_date and src_date > cl_date:
        problems += 1
        print(f"  WARNING: code changed after the last CHANGELOG entry — add one?")
    print()

    if problems:
        print(f"RESULT: {problems} staleness issue(s) found. Update the affected context file(s).")
        raise SystemExit(1 if args.strict else 0)
    print("RESULT: context is in sync with the codebase.")


if __name__ == "__main__":
    main()
