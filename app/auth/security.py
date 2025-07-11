import datetime as dt
import os
from typing import Any, Dict

from fastapi import HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT configuration
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_ME")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password reset token configuration
PWD_RESET_SECRET_KEY: str = os.getenv("PWD_RESET_SECRET_KEY", JWT_SECRET_KEY)
PWD_RESET_SALT: str = os.getenv("PWD_RESET_SALT", "password-reset-salt")
PWD_RESET_EXPIRES_MINUTES: int = int(os.getenv("PWD_RESET_EXPIRES_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Serializer para tokens de restablecimiento de contraseña
pwd_reset_serializer = URLSafeTimedSerializer(PWD_RESET_SECRET_KEY)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash for a plaintext password."""
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], expires_minutes: int | None = None
) -> str:
    """Create a signed JWT with expiration."""
    to_encode = data.copy()
    expire = dt.datetime.utcnow() + dt.timedelta(
        minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode a JWT and return its payload, raising 401 if invalid or expired."""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def generate_password_reset_token(email: str) -> str:
    """Generate a secure token for password reset using itsdangerous.

    Args:
        email: The user's email address

    Returns:
        A URL-safe string token
    """
    return pwd_reset_serializer.dumps(email, salt=PWD_RESET_SALT)


def verify_password_reset_token(token: str, max_age: int = None) -> str:
    """Verify a password reset token and return the email if valid.

    Args:
        token: The token to verify
        max_age: Maximum age in seconds (default is PWD_RESET_EXPIRES_MINUTES * 60)

    Returns:
        The email address encoded in the token

    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        # Si no se especifica max_age, usar el valor predeterminado
        if max_age is None:
            max_age = PWD_RESET_EXPIRES_MINUTES * 60

        email = pwd_reset_serializer.loads(token, salt=PWD_RESET_SALT, max_age=max_age)
        return email
    except SignatureExpired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token ha expirado",
        )
    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido",
        )
