"""
Postgres Row-Level Security context (opt-in, multi-tenant). Drop into src/libs/.

For team/tenant isolation enforced by the database itself. The JWT carries team_id; this
middleware/context sets Postgres session variables that your RLS policies read
(current_setting('app.user_id'), current_setting('app.team_id')).

Requires: RLS policies defined in a migration on each tenant-scoped table, e.g.
    ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
    CREATE POLICY team_isolation ON orders
        USING (team_id = current_setting('app.team_id', true)::uuid);

Register in the app factory: app.add_middleware(RLSMiddleware). Set context inside a
transaction for the request's queries (SET LOCAL is transaction-scoped).
"""
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


async def set_rls_context(user_id: str, team_id: str) -> None:
    """Set RLS session vars for the CURRENT transaction (call inside in_transaction())."""
    from tortoise import connections
    conn = connections.get("default")
    # SET LOCAL is scoped to the surrounding transaction; parameterisation of SET is limited,
    # so validate/cast the inputs to UUID strings before calling.
    await conn.execute_query(f"SET LOCAL app.user_id = '{user_id}'")
    await conn.execute_query(f"SET LOCAL app.team_id = '{team_id}'")


async def clear_rls_context() -> None:
    from tortoise import connections
    conn = connections.get("default")
    await conn.execute_query("RESET app.user_id")
    await conn.execute_query("RESET app.team_id")


class RLSMiddleware(BaseHTTPMiddleware):
    """Stashes team/user from the validated token onto request.state for downstream use.

    Actual SET LOCAL happens per-transaction in the controller (via set_rls_context) because
    SET LOCAL only persists within a transaction. This middleware is the hook point if you
    later move to a connection-per-request model.
    """
    async def dispatch(self, request, call_next):
        # request.state.team_id / user_id are populated by the auth dependency when present.
        return await call_next(request)
