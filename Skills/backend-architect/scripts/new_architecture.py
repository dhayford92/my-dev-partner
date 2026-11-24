#!/usr/bin/env python3
"""
Start a new architecture document from ARCHITECTURE_TEMPLATE.md (the template bundled in
this skill's assets/ folder). Cross-platform. Does NOT design anything — it just lays down the template for you
(or the interviewing AI) to fill in.

Usage:
    python new_architecture.py --name "My API" [--out <path>]

Default --out: ./ARCHITECTURE.md in the current directory. To feed project-context, point it at
<project>/.claude/context/ARCHITECTURE.md (but note: the context ARCHITECTURE.md has its own
lighter template; use this fuller one for up-front design/brainstorming).
"""
import argparse
from datetime import date
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "ARCHITECTURE_TEMPLATE.md"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--out")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        raise SystemExit(f"Template not found at {TEMPLATE}")

    out = Path(args.out).resolve() if args.out else (Path.cwd() / "ARCHITECTURE.md")
    if out.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite {out} (use --force)")

    text = TEMPLATE.read_text(encoding="utf-8")
    # Title + snapshot header
    header = f"# {args.name} — Architecture\n\n_Started: {date.today().isoformat()}_\n\n"
    body = text.split("\n", 1)[1] if text.startswith("# ") else text
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header + body, encoding="utf-8")
    print(f"Wrote architecture doc: {out}")
    print("Now run the interview (see references/interview-guide.md) and fill each section.")


if __name__ == "__main__":
    main()
