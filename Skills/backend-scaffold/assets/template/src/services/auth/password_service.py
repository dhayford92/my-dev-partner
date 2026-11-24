"""
Password service — bcrypt hashing/verification (cost factor 12).
"""
import bcrypt


class PasswordService:
    COST_FACTOR = 12

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=PasswordService.COST_FACTOR)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    @staticmethod
    def is_password_strong(password: str) -> tuple[bool, str | None]:
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        return True, None
