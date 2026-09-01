from __future__ import annotations

import random
import string
import time


def random_email(prefix: str = "autotest", domain: str = "example.com") -> str:
    token = f"{int(time.time() * 1000)}{random.randint(100, 999)}"
    return f"{prefix}.{token}@{domain}"


def random_password(length: int = 12) -> str:
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")

    alphabet = string.ascii_letters + string.digits
    while True:
        password = "".join(random.choice(alphabet) for _ in range(length))
        if any(ch.islower() for ch in password) and any(ch.isupper() for ch in password) and any(ch.isdigit() for ch in password):
            return password
