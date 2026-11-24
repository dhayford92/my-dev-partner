#!/usr/bin/env python3
"""
Generate a Tortoise model stub and register it in configs/database.py ORM_MODELS.
Cross-platform. Does NOT run migrations — you review the model, then migrate.

Usage:
    python new_model.py --project <ROOT> --domain core --resource order [--plural orders] [--seeder]
"""
import argparse
import re
from pathlib import Path

STUBS = Path(__file__).resolve().parent.parent / "assets" / "stubs"


def pascal(snake: str) -> str:
    return "".join(p.capitalize() for p in re.split(r"[_\s]+", snake) if p)


def render(name: str, tokens: dict[str, str]) -> str:
    text = (STUBS / name).read_text(encoding="utf-8")
    for k, v in tokens.items():
        text = text.replace(k, v)
    return text


def register_orm_model(project: Path, domain: str, resource: str) -> None:
    db = project / "configs" / "database.py"
    text = db.read_text(encoding="utf-8")
    entry = f'    "src.apps.{domain}.models.{resource}_model",'
    if entry.strip() in text:
        print("  ORM_MODELS: already present")
        return
    text = text.replace('    "aerich.models",', f'{entry}\n    "aerich.models",', 1)
    db.write_text(text, encoding="utf-8")
    print("  ORM_MODELS: inserted")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--domain", required=True, choices=["core", "users", "utils"])
    ap.add_argument("--resource", required=True)
    ap.add_argument("--plural")
    ap.add_argument("--seeder", action="store_true", help="also emit scripts/seed_<resource>.py")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    if not (project / "configs" / "database.py").exists():
        raise SystemExit(f"No configs/database.py in {project} — scaffold the project first.")

    resource = args.resource.lower()
    tokens = {
        "__Resource__": pascal(resource),
        "__resources__": (args.plural or f"{resource}s").lower(),
        "__resource__": resource,
        "__domain__": args.domain,
    }

    model_path = project / "src" / "apps" / args.domain / "models" / f"{resource}_model.py"
    if model_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite {model_path} (use --force)")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(render("model.py.tmpl", tokens), encoding="utf-8")
    print(f"  wrote {model_path}")

    register_orm_model(project, args.domain, resource)

    if args.seeder:
        seed_path = project / "scripts" / f"seed_{resource}.py"
        seed_path.write_text(render("seeder.py.tmpl", tokens), encoding="utf-8")
        print(f"  wrote {seed_path}")

    print("\nNext:")
    print("  1. Edit the model - add fields, relations, indexes.")
    print(f'  2. aerich migrate --name "add_{resource}_table"')
    print("  3. REVIEW the generated SQL in migrations/models/ before applying.")
    print("  4. aerich upgrade")


if __name__ == "__main__":
    main()
