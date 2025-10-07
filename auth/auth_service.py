"""
Authentication Service for User Management
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import uuid

from .models import (
    User,
    UserInDB,
    UserCreate,
    UserRole,
    RefreshToken,
    Session,
    AuditLogEntry,
    OAuth2Provider,
)
from .security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_reset_token,
    generate_session_id,
    generate_mfa_secret,
    verify_mfa_token,
    generate_qr_code,
    hash_token,
)
from ..core.logger import get_logger
from ..billing.subscription_manager import SubscriptionManager, SubscriptionTier

logger = get_logger(__name__)


class AuthService:
    """
    Authentication service for managing users and authentication

    Features:
    - User registration and login
    - Password management
    - JWT token generation
    - Role-based access control
    - In-memory user storage (can be extended to use database)
    """

    def __init__(self):
        """Initialize authentication service"""
        self.users: Dict[str, UserInDB] = {}
        self.subscription_manager = SubscriptionManager()
        self.refresh_tokens: Dict[str, RefreshToken] = {}
        self.sessions: Dict[str, Session] = {}
        self.audit_logs: List[AuditLogEntry] = []

        # Create default admin user
        self._create_default_admin()
        logger.info("Authentication service initialized")

    def _create_default_admin(self):
        """Create default admin user for initial setup"""
        admin_username = "admin"
        if admin_username not in self.users:
            admin_user = UserInDB(
                username=admin_username,
                email="admin@sentio.com",
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True,
                created_at=datetime.now(),
                hashed_password=get_password_hash("admin123"),  # Change in production!
            )
            self.users[admin_username] = admin_user

            # Create enterprise subscription for admin
            self.subscription_manager.create_subscription(
                user_id=admin_username, tier=SubscriptionTier.ENTERPRISE, trial_days=0
            )
            logger.info("Default admin user created")

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user

        Args:
            user_data: User creation data

        Returns:
            Created user (without password hash)

        Raises:
            ValueError: If username or email already exists
        """
        # Check if username exists
        if user_data.username in self.users:
            self._log_audit(
                "user_creation_failed",
                user_data.username,
                success=False,
                details={"reason": "username_exists"},
            )
            raise ValueError("Username already exists")

        # Check if email exists
        if any(u.email == user_data.email for u in self.users.values()):
            self._log_audit(
                "user_creation_failed",
                user_data.username,
                success=False,
                details={"reason": "email_exists"},
            )
            raise ValueError("Email already exists")

        # Create user with hashed password
        user_in_db = UserInDB(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            is_active=True,
            created_at=datetime.now(),
            hashed_password=get_password_hash(user_data.password),
            email_consent=user_data.email_consent if hasattr(user_data, 'email_consent') else True,
        )

        self.users[user_data.username] = user_in_db

        # Create free subscription for new user
        if user_data.role == UserRole.USER:
            self.subscription_manager.create_subscription(
                user_id=user_data.username, tier=SubscriptionTier.FREE, trial_days=14
            )

        self._log_audit("user_created", user_data.username, success=True)
        logger.info(f"User created: {user_data.username}")

        # Return user without password hash
        return User(
            username=user_in_db.username,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            role=user_in_db.role,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at,
            email_consent=user_in_db.email_consent,
        )

    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate a user with username and password

        Args:
            username: Username to authenticate
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.users.get(username)
        if not user:
            self._log_audit(
                "login_failed",
                username,
                success=False,
                details={"reason": "user_not_found"},
            )
            return None
        if not verify_password(password, user.hashed_password):
            self._log_audit(
                "login_failed",
                username,
                success=False,
                details={"reason": "invalid_password"},
            )
            return None
        if not user.is_active:
            self._log_audit(
                "login_failed",
                username,
                success=False,
                details={"reason": "user_inactive"},
            )
            return None

        self._log_audit("login_success", username, success=True)
        return user

    def get_user(self, username: str) -> Optional[User]:
        """
        Get user by username

        Args:
            username: Username to retrieve

        Returns:
            User object (without password hash) if found, None otherwise
        """
        user_in_db = self.users.get(username)
        if not user_in_db:
            return None

        return User(
            username=user_in_db.username,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            role=user_in_db.role,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at,
            email_consent=getattr(user_in_db, 'email_consent', True),
        )

    def update_user(
        self,
        username: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Optional[User]:
        """
        Update user information

        Args:
            username: Username to update
            email: New email (optional)
            full_name: New full name (optional)
            password: New password (optional)

        Returns:
            Updated user object if successful, None if user not found
        """
        user = self.users.get(username)
        if not user:
            return None

        if email:
            user.email = email
        if full_name:
            user.full_name = full_name
        if password:
            user.hashed_password = get_password_hash(password)

        logger.info(f"User updated: {username}")

        return User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    def deactivate_user(self, username: str) -> bool:
        """
        Deactivate a user account

        Args:
            username: Username to deactivate

        Returns:
            True if successful, False if user not found
        """
        user = self.users.get(username)
        if not user:
            return False

        user.is_active = False
        logger.info(f"User deactivated: {username}")
        return True

    def activate_user(self, username: str) -> bool:
        """
        Activate a user account

        Args:
            username: Username to activate

        Returns:
            True if successful, False if user not found
        """
        user = self.users.get(username)
        if not user:
            return False

        user.is_active = True
        logger.info(f"User activated: {username}")
        return True

    def change_password(
        self, username: str, current_password: str, new_password: str
    ) -> bool:
        """
        Change user password

        Args:
            username: Username
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            True if successful, False otherwise
        """
        user = self.authenticate_user(username, current_password)
        if not user:
            return False

        user.hashed_password = get_password_hash(new_password)
        logger.info(f"Password changed for user: {username}")
        return True

    def create_token_for_user(self, username: str) -> str:
        """
        Create JWT token for a user

        Args:
            username: Username to create token for

        Returns:
            JWT token string
        """
        user = self.users.get(username)
        if not user:
            raise ValueError("User not found")

        token_data = {
            "sub": username,
            "username": username,
            "role": user.role.value,
            "email": user.email,
        }

        return create_access_token(token_data)

    def check_permission(self, user_role: UserRole, required_role: UserRole) -> bool:
        """
        Check if user has required permission level

        Args:
            user_role: Current user's role
            required_role: Required role for access

        Returns:
            True if user has permission, False otherwise
        """
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.USER: 1,
            UserRole.TRADER: 2,
            UserRole.ADMIN: 3,
        }

        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

    # ============================================================================
    # Refresh Token Management
    # ============================================================================

    def create_refresh_token_for_user(self, username: str) -> str:
        """
        Create a refresh token for a user

        Args:
            username: Username to create refresh token for

        Returns:
            Refresh token string
        """
        user = self.users.get(username)
        if not user:
            raise ValueError("User not found")

        token_data = {"sub": username, "username": username, "type": "refresh"}

        token = create_refresh_token(token_data)

        # Store refresh token
        refresh_token = RefreshToken(
            token=hash_token(token),
            user_id=username,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        self.refresh_tokens[refresh_token.token] = refresh_token

        self._log_audit("refresh_token_created", username, success=True)
        return token

    def verify_refresh_token(self, token: str) -> Optional[str]:
        """
        Verify a refresh token and return username

        Args:
            token: Refresh token to verify

        Returns:
            Username if token is valid, None otherwise
        """
        from .security import verify_token as verify_jwt_token

        payload = verify_jwt_token(token)
        if not payload or payload.get("type") != "refresh":
            return None

        hashed = hash_token(token)
        stored_token = self.refresh_tokens.get(hashed)

        if not stored_token:
            return None

        if stored_token.is_revoked:
            return None

        if stored_token.expires_at < datetime.utcnow():
            return None

        return stored_token.user_id

    def revoke_refresh_token(self, token: str) -> bool:
        """
        Revoke a refresh token

        Args:
            token: Refresh token to revoke

        Returns:
            True if successful, False otherwise
        """
        hashed = hash_token(token)
        stored_token = self.refresh_tokens.get(hashed)

        if not stored_token:
            return False

        stored_token.is_revoked = True
        self._log_audit("refresh_token_revoked", stored_token.user_id, success=True)
        return True

    # ============================================================================
    # Multi-Factor Authentication
    # ============================================================================

    def enable_mfa(self, username: str) -> tuple[str, str]:
        """
        Enable MFA for a user

        Args:
            username: Username to enable MFA for

        Returns:
            Tuple of (secret, qr_code_url)
        """
        user = self.users.get(username)
        if not user:
            raise ValueError("User not found")

        secret = generate_mfa_secret()
        qr_code = generate_qr_code(username, secret)

        user.mfa_secret = secret
        user.mfa_enabled = False  # Requires verification first

        self._log_audit("mfa_enrollment_started", username, success=True)
        return secret, qr_code

    def verify_and_enable_mfa(self, username: str, token: str) -> bool:
        """
        Verify MFA token and enable MFA for user

        Args:
            username: Username
            token: TOTP token

        Returns:
            True if successful, False otherwise
        """
        user = self.users.get(username)
        if not user or not user.mfa_secret:
            return False

        if verify_mfa_token(user.mfa_secret, token):
            user.mfa_enabled = True
            self._log_audit("mfa_enabled", username, success=True)
            logger.info(f"MFA enabled for user: {username}")
            return True

        return False

    def disable_mfa(self, username: str, password: str) -> bool:
        """
        Disable MFA for a user

        Args:
            username: Username
            password: User password for verification

        Returns:
            True if successful, False otherwise
        """
        user = self.authenticate_user(username, password)
        if not user:
            return False

        user.mfa_enabled = False
        user.mfa_secret = None

        self._log_audit("mfa_disabled", username, success=True)
        logger.info(f"MFA disabled for user: {username}")
        return True

    def verify_mfa(self, username: str, token: str) -> bool:
        """
        Verify MFA token for a user

        Args:
            username: Username
            token: TOTP token

        Returns:
            True if valid, False otherwise
        """
        user = self.users.get(username)
        if not user or not user.mfa_enabled or not user.mfa_secret:
            return False

        return verify_mfa_token(user.mfa_secret, token)

    # ============================================================================
    # Session Management
    # ============================================================================

    def create_session(
        self,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """
        Create a new session for a user

        Args:
            username: Username
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Session ID
        """
        session_id = generate_session_id()

        session = Session(
            session_id=session_id,
            user_id=username,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
        )

        self.sessions[session_id] = session
        self._log_audit(
            "session_created",
            username,
            details={"session_id": session_id},
            success=True,
        )
        return session_id

    def get_user_sessions(self, username: str) -> List[Session]:
        """
        Get all active sessions for a user

        Args:
            username: Username

        Returns:
            List of active sessions
        """
        return [
            session
            for session in self.sessions.values()
            if session.user_id == username and session.is_active
        ]

    def revoke_session(self, session_id: str) -> bool:
        """
        Revoke a session

        Args:
            session_id: Session ID to revoke

        Returns:
            True if successful, False otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.is_active = False
        self._log_audit(
            "session_revoked",
            session.user_id,
            details={"session_id": session_id},
            success=True,
        )
        return True

    def revoke_all_user_sessions(self, username: str) -> int:
        """
        Revoke all sessions for a user

        Args:
            username: Username

        Returns:
            Number of sessions revoked
        """
        count = 0
        for session in self.sessions.values():
            if session.user_id == username and session.is_active:
                session.is_active = False
                count += 1

        self._log_audit(
            "all_sessions_revoked", username, details={"count": count}, success=True
        )
        return count

    # ============================================================================
    # Password Reset
    # ============================================================================

    def request_password_reset(self, email: str) -> Optional[str]:
        """
        Generate a password reset token for a user

        Args:
            email: User email

        Returns:
            Reset token if user found, None otherwise
        """
        # Find user by email
        user = None
        for u in self.users.values():
            if u.email == email:
                user = u
                break

        if not user:
            # Don't reveal if email exists
            return None

        reset_token = generate_reset_token()
        user.password_reset_token = hash_token(reset_token)
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)

        self._log_audit("password_reset_requested", user.username, success=True)
        logger.info(f"Password reset requested for: {user.username}")

        # In production, send email here
        return reset_token

    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using reset token

        Args:
            token: Reset token
            new_password: New password

        Returns:
            True if successful, False otherwise
        """
        hashed = hash_token(token)

        # Find user with matching token
        user = None
        for u in self.users.values():
            if u.password_reset_token == hashed:
                user = u
                break

        if not user:
            return False

        if (
            not user.password_reset_expires
            or user.password_reset_expires < datetime.utcnow()
        ):
            return False

        user.hashed_password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None

        # Revoke all sessions
        self.revoke_all_user_sessions(user.username)

        self._log_audit("password_reset_completed", user.username, success=True)
        logger.info(f"Password reset completed for: {user.username}")
        return True

    # ============================================================================
    # Audit Logging
    # ============================================================================

    def _log_audit(
        self,
        action: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
    ):
        """
        Log an audit event

        Args:
            action: Action performed
            user_id: User ID
            resource: Resource accessed
            details: Additional details
            ip_address: Client IP
            user_agent: Client user agent
            success: Whether action was successful
        """
        entry = AuditLogEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            success=success,
        )

        self.audit_logs.append(entry)

        # Keep only last 1000 entries
        if len(self.audit_logs) > 1000:
            self.audit_logs = self.audit_logs[-1000:]

    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """
        Get audit logs

        Args:
            user_id: Filter by user ID
            action: Filter by action
            limit: Maximum number of entries

        Returns:
            List of audit log entries
        """
        logs = self.audit_logs

        if user_id:
            logs = [log for log in logs if log.user_id == user_id]

        if action:
            logs = [log for log in logs if log.action == action]

        # Return most recent first
        logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]

    # ============================================================================
    # OAuth2 Integration
    # ============================================================================

    def create_oauth_user(
        self,
        provider: OAuth2Provider,
        provider_user_id: str,
        email: str,
        name: Optional[str] = None,
    ) -> User:
        """
        Create or get user from OAuth2 login

        Args:
            provider: OAuth2 provider
            provider_user_id: User ID from provider
            email: User email
            name: User full name

        Returns:
            User object
        """
        # Check if user already exists by email
        existing_user = None
        for user in self.users.values():
            if user.email == email:
                existing_user = user
                break

        if existing_user:
            self._log_audit(
                "oauth_login",
                existing_user.username,
                details={"provider": provider.value},
                success=True,
            )
            return User(
                username=existing_user.username,
                email=existing_user.email,
                full_name=existing_user.full_name,
                role=existing_user.role,
                is_active=existing_user.is_active,
                created_at=existing_user.created_at,
            )

        # Create new user
        username = f"{provider.value}_{provider_user_id}"
        user_in_db = UserInDB(
            username=username,
            email=email,
            full_name=name or email,
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.now(),
            hashed_password="",  # OAuth users don't have passwords
        )

        self.users[username] = user_in_db

        # Create free subscription
        self.subscription_manager.create_subscription(
            user_id=username, tier=SubscriptionTier.FREE, trial_days=14
        )

        self._log_audit(
            "oauth_user_created",
            username,
            details={"provider": provider.value},
            success=True,
        )
        logger.info(f"OAuth user created: {username}")

        return User(
            username=user_in_db.username,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            role=user_in_db.role,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at,
        )


# Singleton instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get or create the authentication service singleton"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
