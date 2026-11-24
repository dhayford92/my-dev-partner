# First-run troubleshooting

The `/health` endpoint returns `{"status": "healthy", "checks": {"database": "ok",
"redis": "ok"}}` only when both dependencies are reachable. Diagnose by the `checks` map.

## `database: "error: ..."`
- **Postgres not running / wrong URL.** Start it: `docker compose -f docker-compose.dev.yml
  up -d`, or point `DATABASE_URL` in `.env` at your own instance.
- **Tables not created.** Run `aerich init -t configs.database.tortoise_config` then
  `aerich init-db`.
- **Zero-infra option:** set `DATABASE_URL=sqlite://db.sqlite3` in `.env` and re-run
  `aerich init-db`. Good for a first smoke test; not for production.
- **`asyncpg` URL scheme:** Tortoise accepts `postgres://...`. If you copied a SQLAlchemy URL
  like `postgresql+asyncpg://...`, strip `+asyncpg`.

## `redis: "error: ..."` or `"not initialized"`
- **Redis not running.** `docker compose -f docker-compose.dev.yml up -d` or start your own,
  and confirm `REDIS_URL` in `.env`.
- `"not initialized"` means the lifespan hasn't set the client — you're likely hitting
  `/health` before startup finished, or an earlier startup step raised. Check the boot logs.

## App won't boot at all
- **`ModuleNotFoundError: src...`** — run uvicorn from the **project root** (where `main.py`
  is), not from inside `src/`.
- **`ImportError` on a model** — a new model file isn't listed in `configs/database.py`
  `ORM_MODELS`, or a duplicate `related_name` on two FKs to the same model (see
  `../../_shared-backend/database.md`).
- **Aerich "No app found"** — `pyproject.toml` `[tool.aerich] tortoise_orm` must be
  `configs.database.tortoise_config` and you must run aerich from the project root.
- **bcrypt / jose install issues on Windows** — ensure you're on the venv's Python
  (`.\venv\Scripts\python.exe`), not a global interpreter.

## Rate-limit errors during testing
SlowAPI is Redis-backed. If Redis is down, decorated endpoints error. For local testing
without Redis, set `RATE_LIMIT_ENABLED=false` in `.env` (auth still needs Redis for the
denylist, so prefer just running Redis).

## Docker not installed
Pass `-WithDocker:$false` to `scaffold.ps1` (or omit it — it auto-detects) and provide your
own Postgres + Redis via `.env`. The script will still migrate, seed, and health-check.
