#!/usr/bin/env python3
"""
Initialize .claude/context/ for a project from the templates. Cross-platform. Idempotent:
existing files are left untouched unless --force.

Usage:
    python init_context.py --project <ROOT> [--name "My API"] [--force]
"""
import argparse
import datetime
import re
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "context-templates"
FILES = ["OVERVIEW.md", "ARCHITECTURE.md", "SCHEMA.md", "API.md", "DECISIONS.md", "CHANGELOG.md"]
# COMPONENTS.md / SCREENS.md are optional inventories — created only with --with-frontend / --with-mobile.
FRONTEND_FILES = ["COMPONENTS.md"]
MOBILE_FILES = ["SCREENS.md"]


def guess_name(project: Path) -> str:
    # Try APP_NAME from .env, else derive from folder name.
    env = project / ".env"
    if env.exists():
        m = re.search(r"^APP_NAME=(.+)$", env.read_text(encoding="utf-8"), re.MULTILINE)
        if m:
            return m.group(1).strip()
    return project.name.replace("-", " ").title()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--name")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--with-frontend", action="store_true",
                    help="also create COMPONENTS.md (web frontend component/page inventory)")
    ap.add_argument("--with-mobile", action="store_true",
                    help="also create SCREENS.md (mobile screen/navigation inventory)")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    name = args.name or guess_name(project)
    today = datetime.date.today().isoformat()
    ctx = project / ".claude" / "context"
    ctx.mkdir(parents=True, exist_ok=True)

    files = FILES + (FRONTEND_FILES if args.with_frontend else []) + (MOBILE_FILES if args.with_mobile else [])
    for fname in files:
        dest = ctx / fname
        if dest.exists() and not args.force:
            print(f"  skip (exists): {dest}")
            continue
        text = (TEMPLATES / fname).read_text(encoding="utf-8")
        text = text.replace("{{PROJECT_NAME}}", name).replace("{{DATE}}", today)
        dest.write_text(text, encoding="utf-8")
        print(f"  wrote {dest}")

    print(f"\nContext initialized for '{name}' at {ctx}")
    print("Next: fill OVERVIEW.md, then run verify_context.py to check SCHEMA/API against code.")


if __name__ == "__main__":
    main()
