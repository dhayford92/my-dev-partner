"""
RBAC seeder (opt-in) — creates the DEFAULT_ROLE_LIST for a given organization. Idempotent.

Run: python -m scripts.seed_rbac  (adapt to loop over your organizations, or pass an org id)
"""
import asyncio

from tortoise import Tortoise

from configs.database import tortoise_config
from src.apps.users.models.role_model import UserRoleModel, DEFAULT_ROLE_LIST
from src.apps.users.models.organization_model import OrganizationModel


async def seed_roles_for_org(organization_id) -> None:
    for role in DEFAULT_ROLE_LIST:
        obj, created = await UserRoleModel.get_or_create(
            organization_id=organization_id, name=role["name"],
            defaults={"description": role["description"], "permissions": role["permissions"]},
        )
        if not created:
            obj.permissions = role["permissions"]
            obj.description = role["description"]
            await obj.save()
        print(f"  [{organization_id}] role: {role['name']} {'(created)' if created else '(updated)'}")


async def main() -> None:
    await Tortoise.init(config=tortoise_config)
    orgs = await OrganizationModel.all().only("id")
    for org in orgs:
        await seed_roles_for_org(org.id)
    await Tortoise.close_connections()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
