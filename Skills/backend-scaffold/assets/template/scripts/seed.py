"""
Seeder — default roles + a super-admin account. Idempotent (safe to re-run).

Run from the project root (venv active):
    python -m scripts.seed
"""
import asyncio

from tortoise import Tortoise

from configs.database import tortoise_config
from configs.settings import settings
from src.apps.users.models.admin_models import AdminModel
from src.apps.users.models.role_model import RoleModel
from src.apps.users.models.user_enum import AdminRole, AccountStatus
from src.services.auth import PasswordService


DEFAULT_ROLES = [
    {
        "name": "Super Admin",
        "description": "Full platform control.",
        "permissions": {m: {"read": True, "write": True, "delete": True}
                        for m in ["users", "core", "utils"]},
    },
    {
        "name": "Admin",
        "description": "Manage core resources; read users.",
        "permissions": {
            "users": {"read": True, "write": False, "delete": False},
            "core": {"read": True, "write": True, "delete": True},
            "utils": {"read": True, "write": True, "delete": False},
        },
    },
    {
        "name": "Viewer",
        "description": "Read-only across modules.",
        "permissions": {m: {"read": True, "write": False, "delete": False}
                        for m in ["users", "core", "utils"]},
    },
]


async def seed_roles() -> None:
    for role in DEFAULT_ROLES:
        obj, created = await RoleModel.get_or_create(
            name=role["name"],
            defaults={"description": role["description"], "permissions": role["permissions"]},
        )
        if not created:
            obj.permissions = role["permissions"]
            obj.description = role["description"]
            await obj.save()
        print(f"  role: {role['name']} {'(created)' if created else '(updated)'}")


async def seed_super_admin() -> None:
    email = settings.SEED_ADMIN_EMAIL
    existing = await AdminModel.get_or_none(email=email)
    if existing:
        print(f"  super admin already exists: {email}")
        return
    admin = await AdminModel.create(
        full_name="Super Admin",
        email=email,
        password_hashed=PasswordService.hash_password(settings.SEED_ADMIN_PASSWORD),
        role=AdminRole.SUPER_ADMIN,
        status=AccountStatus.ACTIVE,
        is_verified=True,
    )
    role = await RoleModel.get_or_none(name="Super Admin")
    if role:
        await admin.roles.add(role)
    print(f"  super admin created: {email} (password from SEED_ADMIN_PASSWORD)")


async def main() -> None:
    await Tortoise.init(config=tortoise_config)
    print("Seeding...")
    await seed_roles()
    await seed_super_admin()
    await Tortoise.close_connections()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
