#!/usr/bin/env python3
"""
Generate route + controller + schema (validator) [+ model] [+ service] stubs for a new
resource, matching the canonical conventions. Cross-platform.

Usage:
    python new_resource.py --project <ROOT> --domain core --persona admin --resource order \
        [--plural orders] [--with-model] [--with-service] [--wire]

- --project   project root (folder containing main.py)
- --domain    core | users | utils
- --persona   client | admin | vendor | ...  (maps to Current<Persona>User)
- --resource  singular snake_case, e.g. "order"
- --plural    plural snake_case (default: <resource>s)
- --with-model    also emit apps/<domain>/models/<resource>_model.py
- --with-service  also emit services/<resource>/<resource>_service.py
- --wire      insert model into ORM_MODELS and the router include into views/<domain>.py
"""
import argparse
import re
from pathlib import Path

STUBS = Path(__file__).resolve().parent.parent / "assets" / "stubs"


def render(template_name: str, tokens: dict[str, str]) -> str:
    text = (STUBS / template_name).read_text(encoding="utf-8")
    for k, v in tokens.items():
        text = text.replace(k, v)
    return text


def write(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"Refusing to overwrite existing file: {path} (use --force)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path}")


def pascal(snake: str) -> str:
    return "".join(p.capitalize() for p in re.split(r"[_\s]+", snake) if p)


def wire_orm_models(project: Path, domain: str, resource: str) -> None:
    db = project / "configs" / "database.py"
    text = db.read_text(encoding="utf-8")
    entry = f'    "src.apps.{domain}.models.{resource}_model",'
    if entry.strip() in text:
        print("  ORM_MODELS: already present")
        return
    text = text.replace('    "aerich.models",', f'{entry}\n    "aerich.models",', 1)
    db.write_text(text, encoding="utf-8")
    print("  ORM_MODELS: inserted")


def wire_view_include(project: Path, domain: str, resource: str, persona: str) -> None:
    view = project / "src" / "views" / f"{domain}.py"
    text = view.read_text(encoding="utf-8")
    imp = (f"from src.apps.{domain}.routers.{persona}_{resource}_router "
           f"import router as {persona}_{resource}_router")
    inc = f"app.include_router({persona}_{resource}_router, prefix=API_V1)"
    if inc in text:
        print(f"  views/{domain}.py: already wired")
        return
    text = text.rstrip() + f"\n\n{imp}\n{inc}\n"
    view.write_text(text, encoding="utf-8")
    print(f"  views/{domain}.py: include appended")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--domain", required=True, choices=["core", "users", "utils"])
    ap.add_argument("--persona", required=True)
    ap.add_argument("--resource", required=True)
    ap.add_argument("--plural")
    ap.add_argument("--with-model", action="store_true")
    ap.add_argument("--with-service", action="store_true")
    ap.add_argument("--wire", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    if not (project / "main.py").exists():
        raise SystemExit(f"No main.py in {project} — is this a scaffolded project root?")

    resource = args.resource.lower()
    tokens = {
        "__Resource__": pascal(resource),
        "__resources__": (args.plural or f"{resource}s").lower(),
        "__resource__": resource,
        "__Persona__": args.persona.capitalize(),
        "__persona__": args.persona.lower(),
        "__domain__": args.domain,
    }
    print(f"Generating '{resource}' in domain '{args.domain}' (persona '{args.persona}')")

    src = project / "src"
    write(src / "schemas" / args.domain / f"{resource}_schemas.py",
          render("schema.py.tmpl", tokens), args.force)
    write(src / "apps" / args.domain / "controllers" / f"{resource}_controller.py",
          render("controller.py.tmpl", tokens), args.force)
    write(src / "apps" / args.domain / "routers" / f"{args.persona}_{resource}_router.py",
          render("router.py.tmpl", tokens), args.force)
    if args.with_model:
        write(src / "apps" / args.domain / "models" / f"{resource}_model.py",
              render("model.py.tmpl", tokens), args.force)
    if args.with_service:
        svc = src / "services" / resource
        (svc).mkdir(parents=True, exist_ok=True)
        (svc / "__init__.py").touch()
        write(svc / f"{resource}_service.py", render("service.py.tmpl", tokens), args.force)

    if args.wire:
        if args.with_model:
            wire_orm_models(project, args.domain, resource)
        wire_view_include(project, args.domain, resource, args.persona)

    print("\nNext:")
    if not args.with_model:
        print(f"  - create the model apps/{args.domain}/models/{resource}_model.py (backend-database)")
        print(f"    and add it to configs/database.py ORM_MODELS")
    if not args.wire:
        print(f"  - add the include to src/views/{args.domain}.py")
    print(f'  - aerich migrate --name "add_{resource}_table" && aerich upgrade')


if __name__ == "__main__":
    main()
