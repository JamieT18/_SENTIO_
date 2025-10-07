"""
User and Token Data Models
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration for RBAC"""

    ADMIN = "admin"
    USER = "user"
    TRADER = "trader"
    VIEWER = "viewer"


class User(BaseModel):
    """User model for API responses"""

    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    email_consent: bool = True  # Consent to receive emails


class UserInDB(User):
    """User model with password hash for database storage"""

    hashed_password: str
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None


class UserCreate(BaseModel):
    """User creation request model"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    email_consent: bool = True  # Consent to receive emails


class UserLogin(BaseModel):
    """User login request model"""

    username: str
    password: str


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""

    username: Optional[str] = None
    role: Optional[UserRole] = None
    sub: Optional[str] = None


class UserUpdate(BaseModel):
    """User update request model"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class PasswordChange(BaseModel):
    """Password change request model"""

    current_password: str
    new_password: str = Field(..., min_length=8)


class RefreshToken(BaseModel):
    """Refresh token model"""

    token: str
    user_id: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    is_revoked: bool = False


class TokenPair(BaseModel):
    """Access token and refresh token pair"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""

    refresh_token: str


class MFAEnrollment(BaseModel):
    """MFA enrollment response"""

    secret: str
    qr_code_url: str


class MFAVerification(BaseModel):
    """MFA verification request"""

    token: str


class MFALogin(BaseModel):
    """MFA login request"""

    username: str
    password: str
    mfa_token: str


class Session(BaseModel):
    """User session model"""

    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


class AuditLogEntry(BaseModel):
    """Audit log entry model"""

    id: str
    user_id: Optional[str] = None
    action: str
    resource: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = True


class PasswordResetRequest(BaseModel):
    """Password reset request model"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""

    token: str
    new_password: str = Field(..., min_length=8)


class OAuth2Provider(str, Enum):
    """OAuth2 provider enumeration"""

    GOOGLE = "google"
    GITHUB = "github"


class OAuth2Login(BaseModel):
    """OAuth2 login request"""

    provider: OAuth2Provider
    code: str
    redirect_uri: str
