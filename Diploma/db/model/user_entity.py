import re
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    surname: str
    email: str
    password_hash: str

    def __post_init__(self):
        if not self.validate_email(self.email):
            raise ValueError("Invalid email format")

    @staticmethod
    def validate_email(email):
        # Регулярное выражение для проверки формата email
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_regex.match(email))


