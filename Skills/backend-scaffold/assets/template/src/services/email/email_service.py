"""
Email service — Resend + Jinja2 templates. Send via BackgroundTasks so responses stay fast.
"""
import logging

from jinja2 import Environment, PackageLoader, select_autoescape
import resend

from configs.settings import settings

logger = logging.getLogger(__name__)

resend.api_key = settings.MAIL_API_KEY

_env = Environment(
    loader=PackageLoader("src", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


class EmailService:
    @staticmethod
    async def send_email(to: str | list[str], subject: str, template_name: str,
                         body: dict) -> bool:
        """Render `template_name` with `body` and send via Resend. Returns success bool."""
        template = _env.get_template(template_name)
        html_body = template.render(**body)
        if isinstance(to, str):
            to = [to]
        try:
            params = {
                "from": f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>",
                "to": to,
                "subject": subject,
                "html": html_body,
            }
            email = resend.Emails.send(params)
            logger.info(f"Email sent to {to} id={email.get('id') if isinstance(email, dict) else email}")
            return True
        except Exception as e:  # noqa: BLE001
            logger.error(f"Email send error: {e}")
            return False


email_service = EmailService()
