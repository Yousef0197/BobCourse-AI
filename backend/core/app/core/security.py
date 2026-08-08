"""
Password hashing utilities.
Uses bcrypt directly (cost factor 12) to avoid passlib compatibility issues
with bcrypt >= 4.1 (which removed __about__).
"""
import bcrypt


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt cost=12."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False
