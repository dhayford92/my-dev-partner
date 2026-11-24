"""
Example resource model — demonstrates the full model→schema→controller→router stack.
DELETE this (and its schema/controller/router + the ORM_MODELS entry) once you add real domains.
"""
from tortoise import fields
from tortoise.models import Model


class ExampleModel(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)

    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "examples"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Example({self.name})"

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
