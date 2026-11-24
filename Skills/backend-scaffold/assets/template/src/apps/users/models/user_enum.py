"""
Shared enums for users + activity. Keep in sync with the frontend's constants.
"""
from enum import StrEnum


class UserType(StrEnum):
    CLIENT = "client"
    ADMIN = "admin"


class AdminRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class ActivityAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SHARE = "share"
    REVOKE = "revoke"
    LOGIN = "login"
