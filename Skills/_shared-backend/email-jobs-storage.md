# Email · Background Jobs · Storage

## Email — Resend + Jinja2, via BackgroundTasks

**Provider:** Resend (`resend.Emails.send`). **Templates:** Jinja2 HTML in `src/templates/`.
**Dispatch:** through `BackgroundTasks` so responses stay fast.

`src/services/email/email_service.py`:

```python
import logging
from jinja2 import Environment, select_autoescape, PackageLoader
from configs.settings import settings
import resend

logger = logging.getLogger(__name__)
resend.api_key = settings.MAIL_API_KEY

env = Environment(
    loader=PackageLoader("src", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

class EmailService:
    @staticmethod
    async def send_email(to: str | list[str], subject: str, template_name: str, body: dict) -> bool:
        template = env.get_template(template_name)
        html_body = template.render(**body)
        if isinstance(to, str):
            to = [to]
        try:
            params = {
                "from": f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>",
                "to": to, "subject": subject, "html": html_body,
            }
            email = resend.Emails.send(params)
            logger.info(f"Email sent to {to} id={email['id']}")
            return True
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False

email_service = EmailService()
```

Call from a controller via background task (never block the response on email):

```python
background_tasks.add_task(
    email_service.send_email,
    to=user.email, subject="Verify your email",
    template_name="email_verification.html",
    body={"full_name": user.full_name, "verify_url": url},
)
```

- Templates live in `src/templates/*.html`; a shared `logo.png` may sit alongside.
- **No queue, no automatic retry** — failures are logged and swallowed (`return False`).
  If a message is critical, the caller checks the return and reacts.
- Template variables are passed as the `body` dict and rendered with `**body`.

## Background jobs — APScheduler (NOT Celery)

Periodic work runs on an `AsyncIOScheduler` started in the lifespan. **Never introduce
Celery** — it appears in one repo's settings but nothing uses it.

`configs/lifespan.py`:

```python
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
import redis.asyncio as aioredis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from configs.settings import settings
from configs.database import init_db, close_db
from configs.rate_limiting import limiter

logger = logging.getLogger(__name__)
redis_client: aioredis.Redis | None = None
scheduler = AsyncIOScheduler()


async def init_redis() -> aioredis.Redis:
    global redis_client
    redis_client = await aioredis.from_url(
        settings.REDIS_URL, max_connections=settings.REDIS_MAX_CONNECTIONS,
        encoding="utf-8", decode_responses=True,
    )
    return redis_client


def _register_scheduled_jobs() -> None:
    from src.services.subscription.subscription_scheduler import SubscriptionScheduler
    scheduler.add_job(SubscriptionScheduler.expire_subscriptions, trigger="cron",
                      hour=0, minute=10, id="expire_subscriptions", replace_existing=True)
    scheduler.add_job(SubscriptionScheduler.send_payment_reminders, trigger="interval",
                      minutes=10, id="payment_reminders", replace_existing=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    await init_redis()
    app.state.limiter = limiter
    _register_scheduled_jobs()
    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))
    yield
    scheduler.shutdown(wait=False)
    if redis_client:
        await redis_client.close()
    await close_db()
```

- Triggers: `"interval"` (minutes=/seconds=) for polling work; `"cron"` (hour=/minute=) for
  daily/scheduled work.
- Every job: stable `id=`, `replace_existing=True`, and jobs point at a `*Scheduler` /
  service static method — never inline logic in `lifespan.py`.
- Job functions are async and must own their own error handling (a raised exception in one
  job must not kill the scheduler).

## Storage — boto3 → DigitalOcean Spaces

S3-compatible. `endpoint_url` is the DO Spaces region host.

`src/services/storage/storage_service.py`:

```python
from boto3 import Session
from fastapi import File, UploadFile, status, HTTPException
from configs.settings import settings

_ALLOWED = {"jpg", "jpeg", "png", "pdf", "doc", "docx", "ppt", "pptx", "txt", "csv", "xlsx"}

class StorageService:
    def __init__(self):
        self.session = Session(aws_access_key_id=settings.BUCKET_KEY,
                               aws_secret_access_key=settings.BUCKET_SECRET)
        self.s3_client = self.session.client("s3", endpoint_url="https://lon1.digitaloceanspaces.com")

    def upload(self, file: UploadFile = File(...)) -> str:
        extension = file.filename.split(".")[-1].lower()
        if extension not in _ALLOWED:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "File extension is not supported")
        self.s3_client.upload_fileobj(
            file.file, settings.BUCKET_NAME, file.filename,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type},
        )
        return f"{settings.BUCKET_URL}/{file.filename}"

    def delete(self, file_url: str) -> None:
        key = file_url.split("/")[-1]
        self.s3_client.delete_object(Bucket=settings.BUCKET_NAME, Key=key)

storage_service = StorageService()
```

- Validate the extension against the allow-list before upload; reject unsupported types with
  400.
- Uploads are `public-read`; the stored value is the public `BUCKET_URL`-based URL.
- All file I/O goes through `storage_service` — controllers never touch boto3 directly.
- The `endpoint_url` region host (`lon1`) is the one convention worth parameterising per
  project if the Space lives in another region.
