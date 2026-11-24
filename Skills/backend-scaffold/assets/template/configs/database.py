"""
Tortoise ORM database configuration + Aerich migration config.
Register every new model module in ORM_MODELS or its table is never created.
"""
from configs.settings import settings


ORM_MODELS = [
    # users
    "src.apps.users.models.admin_models",
    "src.apps.users.models.client_model",
    "src.apps.users.models.role_model",
    # utils
    "src.apps.utils.models.activity_model",
    "src.apps.utils.models.notification_model",
    # core (example resource — delete once you add real domains)
    "src.apps.core.models.example_model",
    # required by aerich
    "aerich.models",
]

tortoise_config = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ORM_MODELS,
            "default_connection": "default",
        },
    },
}


async def init_db() -> None:
    """Initialize Tortoise ORM. Called during FastAPI startup."""
    from tortoise import Tortoise
    await Tortoise.init(config=tortoise_config)


async def close_db() -> None:
    """Close database connections. Called during FastAPI shutdown."""
    from tortoise import Tortoise
    await Tortoise.close_connections()
