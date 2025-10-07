"""
Security utilities for password hashing and JWT token management
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib
import pyotp
import qrcode
import io
import base64
from passlib.context import CryptContext
from jose import JWTError, jwt

from ..core.config import get_config

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    config = get_config()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token string to verify

    Returns:
        Decoded token payload if valid, None otherwise
    """
    config = get_config()
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> Optional[dict]:
    """
    Decode a JWT token without verification (for debugging)

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token with longer expiration

    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional expiration time delta (default: 7 days)

    Returns:
        Encoded JWT refresh token string
    """
    config = get_config()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm="HS256")
    return encoded_jwt


def generate_reset_token() -> str:
    """
    Generate a secure password reset token

    Returns:
        Secure random token string
    """
    return secrets.token_urlsafe(32)


def generate_session_id() -> str:
    """
    Generate a unique session ID

    Returns:
        Unique session ID string
    """
    return secrets.token_urlsafe(32)


def generate_mfa_secret() -> str:
    """
    Generate a TOTP secret for MFA

    Returns:
        Base32 encoded secret string
    """
    return pyotp.random_base32()


def verify_mfa_token(secret: str, token: str) -> bool:
    """
    Verify a TOTP token

    Args:
        secret: Base32 encoded TOTP secret
        token: 6-digit TOTP token

    Returns:
        True if token is valid, False otherwise
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)


def generate_qr_code(username: str, secret: str, issuer: str = "Sentio 2.0") -> str:
    """
    Generate a QR code for TOTP setup

    Args:
        username: User's username
        secret: TOTP secret
        issuer: Application name

    Returns:
        Base64 encoded QR code image
    """
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username, issuer_name=issuer
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def hash_token(token: str) -> str:
    """
    Hash a token for secure storage

    Args:
        token: Token to hash

    Returns:
        SHA256 hashed token
    """
    return hashlib.sha256(token.encode()).hexdigest()
