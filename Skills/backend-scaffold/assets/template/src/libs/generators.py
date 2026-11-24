"""
Shared generators for codes, references, and tokens. Import `code_generators`.
"""
import random
import string
import uuid


class CodeGenerators:
    @staticmethod
    def generate_code(length: int = 6, digits_only: bool = True) -> str:
        alphabet = string.digits if digits_only else (string.ascii_uppercase + string.digits)
        return "".join(random.choices(alphabet, k=length))

    @staticmethod
    def generate_reference(prefix: str = "REF") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"

    @staticmethod
    def generate_referral_code(length: int = 8) -> str:
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


code_generators = CodeGenerators()
