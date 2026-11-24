#!/usr/bin/env python3
"""
Cross-platform scaffolder (macOS/Linux/Windows). Copies the template, sets APP_NAME, and
prints the remaining first-run steps. Use scaffold.ps1 on Windows for the fully-automated
venv/install/migrate/seed/health flow.

Usage:
    python scaffold.py --name "My API" [--path /abs/target/my-api]
"""
import argparse
import re
import shutil
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help='Project name, e.g. "My API"')
    ap.add_argument("--path", help="Target directory (default: ./<slug>-api)")
    args = ap.parse_args()

    script_dir = Path(__file__).resolve().parent
    template_dir = script_dir.parent / "assets" / "template"
    if not template_dir.is_dir():
        raise SystemExit(f"Template not found at {template_dir}")

    slug = re.sub(r"[^a-z0-9]+", "-", args.name.lower()).strip("-")
    target = Path(args.path).resolve() if args.path else (Path.cwd() / f"{slug}-api")
    if target.exists():
        raise SystemExit(f"Target path already exists: {target}")

    shutil.copytree(template_dir, target,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # .env from .env.example, set APP_NAME
    env_example = target / ".env.example"
    env_file = target / ".env"
    text = env_example.read_text(encoding="utf-8")
    text = re.sub(r"^APP_NAME=.*$", f"APP_NAME={args.name}", text, flags=re.MULTILINE)
    env_file.write_text(text, encoding="utf-8")

    readme = target / "README.md"
    if readme.exists():
        readme.write_text(readme.read_text(encoding="utf-8").replace("{{APP_NAME}}", args.name),
                          encoding="utf-8")

    print(f"Scaffolded '{args.name}' into {target}\n")
    print("Next steps:")
    print(f"  cd {target}")
    print("  python -m venv venv && source venv/bin/activate")
    print("  pip install -r requirements.txt")
    print("  # edit .env, then start Postgres + Redis:")
    print("  docker compose -f docker-compose.dev.yml up -d")
    print("  aerich init -t configs.database.tortoise_config && aerich init-db")
    print("  python -m scripts.seed")
    print("  uvicorn main:app --reload    # then GET http://localhost:8000/health")


if __name__ == "__main__":
    main()
