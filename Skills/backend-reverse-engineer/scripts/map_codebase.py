#!/usr/bin/env python3
"""
Map an existing FastAPI + Tortoise codebase: inventory the real structure (as built) and flag
drift from the canonical conventions. Read-only. Cross-platform.

Usage:
    python map_codebase.py --project <ROOT> [--json]

Reports:
  - sub-apps, models (+tables), routers (+routes), controllers, services
  - models not registered in ORM_MODELS
  - convention drift: settings style, print() vs logger, pagination shape, error style,
    missing /api/v1, Float-for-money, missing soft delete, duplicate related_name
This is a FACT-FINDER. It reports "what is" — judgement ("what should be") is the reviewer's.
"""
import argparse
import json
import re
from pathlib import Path


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


def inventory(project: Path) -> dict:
    src = project / "src"
    inv: dict = {"sub_apps": [], "models": [], "model_files_with_table": [], "routers": [],
                 "controllers": [], "services": [], "tables": [], "orm_models": []}

    views = src / "views"
    if views.exists():
        inv["sub_apps"] = sorted(f.stem for f in views.glob("*.py") if f.stem != "__init__")

    for f in iter_py(src):
        rel = f.relative_to(project).as_posix()
        if "/models/" in rel:
            found = re.findall(r'table\s*=\s*["\']([^"\']+)["\']', read(f))
            inv["tables"].extend(found)
            inv["models"].append(rel)
            if found:  # only files that actually define a Tortoise model (has Meta.table)
                inv["model_files_with_table"].append(rel)
        elif "/routers/" in rel:
            inv["routers"].append(rel)
        elif "/controller" in rel:
            inv["controllers"].append(rel)
        elif "/services/" in rel:
            inv["services"].append(rel)

    db = project / "configs" / "database.py"
    if db.exists():
        inv["orm_models"] = re.findall(r'["\'](src\.apps\.[\w.]+)["\']', read(db))

    inv["tables"] = sorted(set(inv["tables"]))
    return inv


def routes(project: Path) -> list[dict]:
    out = []
    for f in (project / "src").rglob("routers/*.py"):
        if "__pycache__" in str(f):
            continue
        text = read(f)
        prefixes = {}
        for m in re.finditer(r'(\w+)\s*=\s*APIRouter\(([^)]*)\)', text):
            pm = re.search(r'prefix\s*=\s*["\']([^"\']*)["\']', m.group(2))
            prefixes[m.group(1)] = pm.group(1) if pm else ""
        for m in re.finditer(r'@(\w+)\.(get|post|put|patch|delete)\(\s*["\']([^"\']*)["\']', text):
            out.append({"path": f"{prefixes.get(m.group(1), '')}{m.group(3)}",
                        "method": m.group(2).upper(), "file": f.name})
    return out


def detect_drift(project: Path, inv: dict) -> list[str]:
    findings = []
    src = project / "src"

    # settings style
    settings = read(project / "configs" / "settings.py")
    if settings:
        if "BaseSettings" not in settings and "os.environ" in settings:
            findings.append("CONFIG: uses plain os.environ class, not pydantic-settings BaseSettings.")
        low = re.search(r'^\s*[a-z_]+\s*[:=].*Field\(', settings, re.MULTILINE)
        if "BaseSettings" in settings and low:
            findings.append("CONFIG: settings fields appear snake_case; canonical is UPPER_CASE.")

    # print() vs logger
    print_files = [str(f.relative_to(project)) for f in iter_py(src)
                   if re.search(r'\bprint\(', read(f))]
    if print_files:
        findings.append(f"LOGGING: print() used in {len(print_files)} file(s) instead of logger "
                        f"(e.g. {print_files[0]}).")

    # pagination shape
    joined = " ".join(read(f) for f in iter_py(src) if "schema" in f.name.lower())
    if re.search(r'\bpage_size\b|\bitems\s*:', joined) or re.search(r'\btotal\s*:\s*int', joined):
        if "current_page" not in joined or "page_limit" not in joined:
            findings.append("RESPONSE: pagination shape differs from canonical "
                            "{data,current_page,page_limit,total_count}.")

    # error style: global {error:{...}} handler
    if any("register_exception_handlers" in read(f) or re.search(r'"error"\s*:\s*ErrorDetail', read(f))
           for f in iter_py(src)):
        findings.append("ERRORS: global {error:{...}} handler present; canonical is raise "
                        "HTTPException(detail, headers X-Error-Code).")

    # missing /api/v1 in view includes
    for vf in (src / "views").glob("*.py") if (src / "views").exists() else []:
        vt = read(vf)
        if "include_router" in vt and "api/v1" not in vt and "API_V1" not in vt and "API_PREFIX" not in vt:
            findings.append(f"ROUTING: {vf.name} includes routers without an /api/v1 prefix.")

    # Float for money
    for f in src.rglob("models/*.py") if src.exists() else []:
        for m in re.finditer(r'(\w*(amount|price|balance|total|fee)\w*)\s*=\s*fields\.FloatField', read(f)):
            findings.append(f"DB: money-like column '{m.group(1)}' uses FloatField "
                            f"({f.name}); prefer DecimalField.")
            break

    # models missing soft delete
    no_soft = []
    for f in src.rglob("models/*.py") if src.exists() else []:
        t = read(f)
        if "class" in t and "Model)" in t and "deleted_at" not in t and "abstract = True" not in t:
            no_soft.append(f.name)
    if no_soft:
        findings.append(f"DB: {len(no_soft)} model file(s) without a deleted_at soft-delete column "
                        f"(e.g. {no_soft[0]}).")

    # duplicate related_name to the SAME target model (real Tortoise clash)
    for f in src.rglob("models/*.py") if src.exists() else []:
        # capture ForeignKeyField/ManyToManyField calls: target ref + related_name
        pairs = []
        for m in re.finditer(r'(?:ForeignKeyField|ManyToManyField)\(\s*["\']([^"\']+)["\']([^)]*)', read(f)):
            target, rest = m.group(1), m.group(2)
            rn = re.search(r'related_name\s*=\s*["\']([^"\']+)["\']', rest)
            if rn:
                pairs.append((target, rn.group(1)))
        clashes = sorted({p for p in pairs if pairs.count(p) > 1})
        if clashes:
            findings.append(f"DB: duplicate related_name to same target in {f.name}: "
                            f"{[f'{t}->{n}' for t, n in clashes]} (backward-relation clash).")

    # real model files (with a Meta.table) not registered in ORM_MODELS
    registered = set(inv["orm_models"])
    for mf in inv["model_files_with_table"]:
        mod = mf.replace("/", ".").removesuffix(".py")   # src/apps/.../x_model.py -> src.apps...x_model
        if mod not in registered:
            findings.append(f"DB: model {mf} (defines a table) not in configs/database.py ORM_MODELS.")

    return findings


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    if not (project / "src").exists():
        raise SystemExit(f"No src/ in {project} — not a recognised project root.")

    inv = inventory(project)
    rts = routes(project)
    drift = detect_drift(project, inv)

    if args.json:
        print(json.dumps({"inventory": inv, "routes": rts, "drift": drift}, indent=2))
        return

    print(f"== Codebase map: {project} ==\n")
    print(f"sub-apps ({len(inv['sub_apps'])}): {', '.join(inv['sub_apps']) or '-'}")
    print(f"models: {len(inv['models'])}   tables: {len(inv['tables'])}   "
          f"routers: {len(inv['routers'])}   routes: {len(rts)}   "
          f"controllers: {len(inv['controllers'])}   services: {len(inv['services'])}\n")
    print("tables:", ", ".join(inv["tables"]) or "-", "\n")
    print("routes:")
    for r in sorted(rts, key=lambda x: x["path"]):
        print(f"  {r['method']:6} {r['path']}   ({r['file']})")
    print(f"\n== Convention drift ({len(drift)}) ==")
    if not drift:
        print("  none detected")
    for d in drift:
        print(f"  - {d}")
    print("\n(Fact-finder only. 'What should be' is the reviewer's call - see the report template.)")


if __name__ == "__main__":
    main()
