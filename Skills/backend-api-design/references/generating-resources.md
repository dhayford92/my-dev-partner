# Generating resources

The generator lives in `scripts/new_resource.py` (engine) with `scripts/new_resource.ps1`
as the Windows wrapper (it calls the same engine, so behaviour is identical). Templates are
in `assets/stubs/*.tmpl` and use `__Token__` placeholders.

## Tokens

| Token | Example (`--resource order --persona admin --domain core`) |
|-------|------------------------------------------------------------|
| `__Resource__` | `Order` |
| `__resource__` | `order` |
| `__resources__` | `orders` (or `--plural`) |
| `__Persona__` | `Admin` → `CurrentAdminUser` |
| `__persona__` | `admin` |
| `__domain__` | `core` |

## Flags

| Flag | Effect |
|------|--------|
| `--project` | project root (folder with `main.py`) — required |
| `--domain` | `core` \| `users` \| `utils` — required |
| `--persona` | `client` \| `admin` \| `vendor` \| … → `Current<Persona>User` — required |
| `--resource` | singular snake_case — required |
| `--plural` | override the naive `<resource>s` |
| `--with-model` | also emit `models/<resource>_model.py` |
| `--with-service` | also emit `services/<resource>/<resource>_service.py` |
| `--wire` | insert model into `ORM_MODELS` + router include into `views/<domain>.py` |
| `--force` | overwrite existing files |

## What each stub contains
- **schema** — `Create/Update/*Table/*Detail/*List/Select` classes (the taxonomy).
- **controller** — static-method class: `list` (canonical pagination), `get`, `create`,
  `update` (partial via `model_dump(exclude_none=True)`), `delete` (soft-delete); the
  try/except ladder; `ActivityService` logging on every mutation.
- **router** — thin `APIRouter(prefix="/<persona>/<resources>")`, `response_model=` per route,
  persona guard, `@limiter.limit(RateLimitConfig.CREATE_RESOURCE)` on create.
- **model** (opt) — UUID PK, timestamps, soft delete, `Meta.table = "<resources>"`.
- **service** (opt) — empty capability class to fill when logic is shared.

## The generator does NOT
- Guess your fields — every schema/model ships with a `name` placeholder + `TODO`s.
- Run migrations — you run `aerich migrate` / `upgrade` yourself.
- Add non-CRUD routes — extend the generated controller/router by hand.

## Manual path (no script)
Copy the four `assets/stubs/*.tmpl` files, replace the tokens by hand, drop them into the
matching directories, add the model to `ORM_MODELS`, add the include to `views/<domain>.py`,
and migrate. The script is just this, mechanised + idempotent.

## Verification
Generated files compile immediately (proven in the skill's own test). After filling fields:
```powershell
python -m py_compile src/apps/<domain>/controllers/<resource>_controller.py
uvicorn main:app --reload   # confirm routes under /<domain>/docs
```
