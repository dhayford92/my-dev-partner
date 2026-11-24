# Code Style & Naming

## Files & symbols

| Thing | Convention | Example |
|-------|-----------|---------|
| Model file / class | `<resource>_model.py` / `<Resource>Model` | `order_model.py` → `OrderModel` |
| Controller file / class | `<resource>_controller.py` / `<Resource>Controller` | `order_controller.py` → `OrderController` |
| Router file | `<persona>_<feature>_router.py` | `client_orders_router.py` |
| Service file / class | `<name>_service.py` / `<Name>Service` | `email_service.py` → `EmailService` |
| Enum file | `<domain>_enum.py` (users: `user_enum.py`) | `ClientStatus`, `UserType`, `ActivityAction` |
| Schema file | `<resource>_schemas.py` in `schemas/<domain>/` | `schemas/users/client_schemas.py` |

- **Imports:** absolute, from the `src.` prefix. No relative imports across packages.
- **Async:** every handler, controller method, and DB call is `async`/`await`.
- **Type hints** everywhere; `X | None` union syntax; `list[T]` / `dict[str, Any]` builtins.
- **JSON keys are snake_case** end to end (matches the frontend).
- **Datetimes** are UTC: `datetime.now(timezone.utc)`.

## Pydantic schema taxonomy (canonical naming)

One schema class per role. Names are strict so intent is obvious:

| Suffix | Purpose |
|--------|---------|
| `Create{Entity}Schema` | POST request body |
| `Update{Entity}Schema` | PATCH/PUT body (all fields optional) |
| `{Entity}DetailSchema` | single-item detail response |
| `{Entity}TableSchema` | list-row item (lighter than Detail) |
| `{Entity}ListSchema(PaginatedResponse)` | paginated list response |
| `Select{Entity}Schema` | dropdown/reference `(id, name)` only |

Example:

```python
# src/schemas/core/order_schemas.py
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, use_enum_values=True)

class CreateOrderSchema(BaseModel):
    item_id: UUID
    quantity: int = Field(ge=1)

class UpdateOrderSchema(BaseModel):
    quantity: int | None = Field(default=None, ge=1)
    status: str | None = None

class OrderTableSchema(BaseSchema):
    id: UUID
    reference: str
    status: str
    created_at: datetime

class OrderDetailSchema(OrderTableSchema):
    item_id: UUID
    quantity: int
    total_amount: float

class SelectOrderSchema(BaseSchema):
    id: UUID
    reference: str
```

- Enum → string in responses via `use_enum_values=True` (or `status=obj.status.value`).
- Request schemas validate with `Field(...)` constraints (`ge`, `le`, `min_length`,
  `pattern`, `EmailStr`).

## Helper placement

- Cross-cutting, HTTP/framework-aware helpers → `src/libs/` (`auth.py`, `generators.py`,
  `redaction.py`, `request_id.py`, `formatters.py`).
- Reusable **domain** capabilities → `src/services/<domain>/<name>_service.py`.
- One-resource pure functions used by a single controller → keep them near the controller,
  not in `libs`.
- Random codes / references / tokens → a `generators.py` (`code_generators.generate_referral_code()`),
  not inline.

## Docstrings & comments

- Module docstring at the top of each file (one line describing the file's role).
- Public controller/service methods get a short docstring stating what they do and, when
  non-obvious, what they raise.
- Section banners (`# ==== Section ====`) are used to group related routes/methods — match
  the surrounding file's density; don't over-comment obvious lines.

## Error messages

- Client-facing `message` is human-readable and safe (no stack traces, no internal IDs).
- Machine `code` comes from `ErrorCodes` (see [response-contract.md](response-contract.md)).
- Never leak secrets, tokens, or raw exception text to the client — log those, return
  generic 500 copy.

## General

- Keep routers thin, controllers fat, services reusable, models dumb.
- Prefer the existing convention over "best practice." If a convention seems wrong, note it
  in the Phase 4 optimisation report — don't silently deviate in generated code.
