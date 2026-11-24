"""
Optional shared abstract base — removes the repeated id/timestamps/deleted_at boilerplate.

The four reference repos repeat these fields inline in every model (there is NO base model).
Introduce this ONLY when the owner opts in for a new project; otherwise keep fields inline to
match existing style. To adopt: drop this file at src/apps/base_model.py, then have models
`class Foo(TimestampedModel)` and delete the inline id/created_at/updated_at/deleted_at lines.
"""
from tortoise import fields
from tortoise.models import Model


class TimestampedModel(Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
