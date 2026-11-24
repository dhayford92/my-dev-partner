# Controllers & Services

Three tiers: **router → controller → (services + models)**. There is **no repository
layer** — controllers call Tortoise models directly.

## Controller = class of `@staticmethod`s

- Holds **all business logic and orchestration**.
- Raises `HTTPException` directly (with structured `detail` — see
  [response-contract.md](response-contract.md)).
- Wraps multi-write operations in `async with in_transaction()`.
- Returns pydantic response models (never raw dicts, never ORM objects).
- Uses the standard try/except ladder.

Real example (`src/apps/users/controllers/client_auth_controller.py`, trimmed):

```python
import logging, uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status, BackgroundTasks
from tortoise.transactions import in_transaction

from src.apps.users.models.client_model import ClientModel
from src.apps.users.models.user_enum import ClientStatus, UserType
from src.schemas.shared.responses import SuccessResponse
from src.services.auth import token_denylist
from src.services.auth.jwt_service import JWTService

logger = logging.getLogger(__name__)


class ClientAuthController:

    @staticmethod
    async def verify_otp(body: OTPVerifySchema, background_tasks: BackgroundTasks) -> ClientAuthResponse:
        """Verify OTP and create/login a client user."""
        try:
            payload = JWTService.verify_token(body.token, token_type="otp_request")
            phone_number = payload.get("phone")
            await OTPService.verify_otp(phone_number, body.code)

            async with in_transaction():                       # multi-write → transaction
                user = await ClientModel.get_or_none(phone=phone_number)
                if not user:
                    user = await ClientModel.create(
                        phone=phone_number,
                        is_phone_verified=True,
                        status=ClientStatus.ACTIVE,
                    )
                else:
                    user.last_login_at = datetime.now(timezone.utc)
                    await user.save()

            access_token, _, access_exp = JWTService.create_access_token(
                user_id=user.id, user_type=UserType.CLIENT,
                additional_claims={"phone": phone_number},
            )
            refresh_token, _, _ = JWTService.create_refresh_token(
                user_id=user.id, user_type=UserType.CLIENT,
            )
            return ClientAuthResponse(access_token=access_token, refresh_token=refresh_token)

        except HTTPException:
            raise                                              # never swallow HTTPException
        except ValueError as e:                                # typed domain error → 4xx
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:                                 # unexpected → log + 500
            logger.error(f"OTP verify error: {e}")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Verification failed")
```

### The try/except ladder (mandatory shape)

```python
try:
    ...  # happy path
except HTTPException:
    raise                        # 1. re-raise HTTPExceptions untouched
except ValueError as e:          # 2. expected domain errors → specific 4xx
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
except Exception as e:           # 3. everything else → log + generic 500
    logger.error(f"<context>: {e}")
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="<user-safe message>")
```

Errors are always raised as `HTTPException(status_code, detail, headers?)` — `detail` is a
string, and a machine code goes in `headers={"X-Error-Code": ErrorCodes.X}` when the client
needs to branch on it. There are **no global exception handlers**; the ladder above is the
error contract. See [response-contract.md](response-contract.md).

Never `print()` in the except block — always `logger.error` (see [logging.md](logging.md)).

## Data access

Controllers use Tortoise directly:

```python
user = await ClientModel.get_or_none(id=user_id).only("id", "status")   # narrow columns
existing = await ClientModel.filter(phone=phone).first()
await ClientModel.create(**data)
user.field = value; await user.save()
await Model.filter(...).prefetch_related("relation")                     # avoid N+1
```

See [database.md](database.md) for query/transaction/N+1 rules.

## Service = reusable capability

A service is domain logic reused across controllers. Two shapes:

**Static-method class** (stateless helpers):

```python
class JWTService:
    ALGORITHM = "HS256"
    @staticmethod
    def create_access_token(user_id: uuid.UUID, ...) -> tuple[str, str, datetime]: ...
```

**Module-level singleton** (holds a client/connection):

```python
class StorageService:
    def __init__(self): self.s3_client = ...
storage_service = StorageService()      # import the instance, don't re-instantiate
```

Controllers import and call services; they never re-implement service logic (don't call
`bcrypt`/`jose`/`boto3` directly — go through `PasswordService`/`JWTService`/`storage_service`).

## Activity logging is part of the mutation

Every create/update/delete/share/revoke should log an audit entry **in the same
controller** via `ActivityService` — see [logging.md](logging.md). Do not defer it to a
separate pass.

## Division of responsibility

| Concern | Router | Controller | Service | Model |
|---------|:------:|:----------:|:-------:|:-----:|
| HTTP shape, status, `response_model` | ✅ | | | |
| Auth dependency | ✅ | | | |
| Business rules / orchestration | | ✅ | | |
| Transactions | | ✅ | | |
| Raising `HTTPException` | | ✅ | (may) | |
| Reusable capability (JWT, email, storage) | | | ✅ | |
| Persistence / schema | | | | ✅ |
