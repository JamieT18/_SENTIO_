"""
FastAPI REST API for Sentio Trading System
Provides endpoints for trading operations, analysis, and monitoring
"""

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    status,
    Request,
    Response,
    WebSocket,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import asyncio
import csv
import json
import io
import time

from ..core.config import get_config
from ..core.logger import get_logger
from ..core.constants import (
    DEFAULT_SYMBOLS,
    DEFAULT_TIMEFRAME,
    DEFAULT_TRADE_JOURNAL_LIMIT,
    STATUS_SUCCESS,
    STATUS_WARNING,
    STATUS_OPERATIONAL,
    STATUS_HEALTHY,
    SIGNAL_ERROR,
    PORTFOLIO_STATUS_ACTIVE,
    PORTFOLIO_STATUS_IDLE,
    MARKET_OVERVIEW_GENERAL,
)
from ..execution.trading_engine import TradingEngine
from ..strategies.tjr_strategy import TJRStrategy
from ..strategies.momentum_strategy import MomentumStrategy
from ..strategies.mean_reversion_strategy import MeanReversionStrategy
from ..strategies.breakout_strategy import BreakoutStrategy
from ..risk.risk_manager import RiskManager
from ..analysis.technical_analysis import TechnicalAnalysisEngine
from ..political.insider_tracker import InsiderTracker
from ..longtermInvestment.fundamental_analysis import FundamentalAnalysisEngine
from ..billing.subscription_manager import SubscriptionManager, SubscriptionTier
from ..auth import (
    AuthService,
    get_auth_service,
    User,
    UserRole,
    UserCreate,
    UserLogin,
    Token,
    UserUpdate,
    PasswordChange,
    verify_token as verify_jwt_token,
    TokenPair,
    RefreshTokenRequest,
    MFAEnrollment,
    MFAVerification,
    MFALogin,
    Session,
    AuditLogEntry,
    PasswordResetRequest,
    PasswordResetConfirm,
    OAuth2Provider,
    OAuth2Login,
)
from .api_utils import (
    format_timestamp,
    create_success_response,
    create_error_response,
    create_warning_response,
    parse_symbol_list,
    format_journal_entry,
)
from .strength_signal_service import StrengthSignalService
from ..data.market_data import MarketDataManager
from ..data.websocket_service import ws_manager
from ..data.dashboard_websocket_service import dashboard_ws_manager

# Try to import rate limiter and monitor, use None if not available
try:
    from .rate_limiter import get_rate_limiter
except ImportError:

    def get_rate_limiter(*args, **kwargs):
        return None


try:
    from .api_monitor import get_api_monitor
except ImportError:

    def get_api_monitor(*args, **kwargs):
        return None


logger = get_logger(__name__)
config = get_config()

# Initialize rate limiter and monitor
rate_limiter = (
    get_rate_limiter(
        requests_per_minute=config.rate_limit.requests_per_minute,
        requests_per_hour=config.rate_limit.requests_per_hour,
        requests_per_day=config.rate_limit.requests_per_day,
    )
    if config.rate_limit.enabled
    else None
)

api_monitor = (
    get_api_monitor(max_history=config.monitoring.max_history)
    if config.monitoring.enabled
    else None
)

# Initialize strength signal service
strength_signal_service = StrengthSignalService()

# Initialize market data manager with real data
market_data_manager = MarketDataManager(use_real_data=True)

# Simple in-memory cache for API responses
from collections import OrderedDict
from datetime import timedelta


class ResponseCache:
    """Simple LRU cache for API responses"""

    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None

        # Check TTL
        if key in self.ttl and datetime.now() > self.ttl[key]:
            del self.cache[key]
            del self.ttl[key]
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key: str, value: Any, ttl_seconds: int = 60):
        self.cache[key] = value
        self.ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)

        # Remove oldest if cache is full
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            if oldest_key in self.ttl:
                del self.ttl[oldest_key]

    def clear(self):
        self.cache.clear()
        self.ttl.clear()


response_cache = ResponseCache(
    max_size=config.cache.max_cache_size if hasattr(config, "cache") else 1000
)

# Initialize FastAPI app
app = FastAPI(
    title="Sentio 2.0 Trading API",
    description="Intelligent Multi-Strategy Trading System",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression middleware for better performance
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB


# Monitoring middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Middleware to monitor API requests and apply rate limiting"""
    start_time = time.time()
    error_msg = None

    # Apply rate limiting if enabled
    if rate_limiter and config.rate_limit.enabled:
        try:
            # Skip rate limiting for health check and metrics endpoints
            if request.url.path not in ["/api/v1/health", "/api/v1/metrics"]:
                await rate_limiter.check_rate_limit(request)
        except HTTPException as e:
            # Return rate limit error immediately
            return Response(
                content=str(e.detail), status_code=e.status_code, headers=e.headers
            )

    # Process request
    try:
        response = await call_next(request)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Request error: {error_msg}", exc_info=True)
        response = Response(
            content=f'{{"detail": "{error_msg}"}}',
            status_code=500,
            media_type="application/json",
        )

    # Calculate response time
    response_time_ms = (time.time() - start_time) * 1000

    # Add performance headers
    response.headers["X-Response-Time"] = f"{response_time_ms:.2f}ms"

    # Record metrics if monitoring is enabled
    if api_monitor and config.monitoring.enabled:
        await api_monitor.record_request(
            request=request,
            response=response,
            response_time_ms=response_time_ms,
            error=error_msg,
        )

    return response


# API error handler decorator
def api_error_handler(func):
    """Decorator to handle API errors consistently"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"API error in {func.__name__}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    return wrapper


# Security
security = HTTPBearer()


# Request/Response models
class AnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "5min"


class TradeRequest(BaseModel):
    symbol: str
    action: str  # 'buy', 'sell', 'close'
    quantity: Optional[float] = None


class StrategyConfig(BaseModel):
    name: str
    enabled: bool
    min_confidence: float


class SystemStatus(BaseModel):
    status: str
    mode: str
    active_strategies: int
    open_positions: int
    portfolio_value: float
    daily_pnl: float


class ProfitSharingRequest(BaseModel):
    user_id: str
    trading_profit: float


class TradeJournalEntry(BaseModel):
    symbol: str
    action: str
    quantity: float
    price: float
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class UpdatePricingRequest(BaseModel):
    tier: str
    new_price: float


class UpdateSubscriptionRequest(BaseModel):
    user_id: str
    new_tier: str


# Dependency for authentication
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify JWT token and return user information

    Args:
        credentials: HTTP Authorization credentials with bearer token

    Returns:
        Token payload with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify JWT token
    payload = verify_jwt_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    user = auth_service.get_user(username)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_user(token_data: dict = Depends(verify_token)) -> User:
    """
    Get current user from token

    Args:
        token_data: Token payload from verify_token

    Returns:
        Current user object
    """
    username = token_data.get("sub")
    user = auth_service.get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def require_role(required_role: UserRole):
    """
    Dependency factory for role-based access control

    Args:
        required_role: Minimum required role for access

    Returns:
        Dependency function that checks user role
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not auth_service.check_permission(current_user.role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker


# Dependency for admin authentication
async def verify_admin_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Verify admin JWT token (placeholder)"""
    # In production: implement proper admin JWT verification with role checking
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    # In production: verify token has admin role
    # For now, accept any token with "admin" in it as a placeholder
    if "admin" not in token.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return token


# Initialize components (in production, use dependency injection)
trading_engine: Optional[TradingEngine] = None
ta_engine = TechnicalAnalysisEngine()
insider_tracker = InsiderTracker()
fundamental_engine = FundamentalAnalysisEngine()
subscription_manager = SubscriptionManager()
auth_service = get_auth_service()


def get_trading_engine() -> TradingEngine:
    """Get or create trading engine"""
    global trading_engine
    if trading_engine is None:
        strategies = [
            TJRStrategy(),
            MomentumStrategy(),
            MeanReversionStrategy(),
            BreakoutStrategy(),
        ]
        trading_engine = TradingEngine(strategies=strategies)
    return trading_engine


# API Endpoints

# ============================================================================
# Authentication Endpoints
# ============================================================================


@app.post(
    "/api/v1/auth/register", response_model=User, status_code=status.HTTP_201_CREATED
)
async def register_user(user_data: UserCreate) -> User:
    """
    Register a new user

    Args:
        user_data: User registration data

    Returns:
        Created user object

    Raises:
        HTTPException: If username or email already exists
    """
    try:
        user = auth_service.create_user(user_data)
        logger.info(f"User registered: {user.username}")
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_credentials: UserLogin) -> Token:
    """
    Login with username and password

    Args:
        user_credentials: Login credentials

    Returns:
        JWT token for authentication

    Raises:
        HTTPException: If authentication fails
    """
    user = auth_service.authenticate_user(
        user_credentials.username, user_credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_token_for_user(user.username)

    logger.info(f"User logged in: {user.username}")

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=config.access_token_expire_minutes * 60,
    )


@app.post("/api/v1/auth/token", response_model=Token)
async def login_oauth(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    OAuth2 compatible token endpoint

    Args:
        form_data: OAuth2 form with username and password

    Returns:
        JWT token for authentication
    """
    user = auth_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_token_for_user(user.username)

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=config.access_token_expire_minutes * 60,
    )


@app.get("/api/v1/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        Current user object
    """
    return current_user


@app.put("/api/v1/auth/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate, current_user: User = Depends(get_current_user)
) -> User:
    """
    Update current user information

    Args:
        user_update: User update data
        current_user: Current authenticated user

    Returns:
        Updated user object
    """
    try:
        updated_user = auth_service.update_user(
            username=current_user.username,
            email=user_update.email,
            full_name=user_update.full_name,
            password=user_update.password,
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        logger.info(f"User updated: {current_user.username}")
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )


@app.post("/api/v1/auth/change-password")
async def change_password(
    password_change: PasswordChange, current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Change user password

    Args:
        password_change: Password change data
        current_user: Current authenticated user

    Returns:
        Success message
    """
    success = auth_service.change_password(
        username=current_user.username,
        current_password=password_change.current_password,
        new_password=password_change.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    logger.info(f"Password changed for user: {current_user.username}")
    return {"message": "Password changed successfully"}


# ============================================================================
# Refresh Token Endpoints
# ============================================================================


@app.post("/api/v1/auth/login-with-refresh", response_model=TokenPair)
async def login_with_refresh(user_credentials: UserLogin) -> TokenPair:
    """
    Login and get both access and refresh tokens

    Args:
        user_credentials: Login credentials

    Returns:
        Access token and refresh token pair
    """
    user = auth_service.authenticate_user(
        user_credentials.username, user_credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check MFA if enabled
    if user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MFA verification required. Use /api/v1/auth/login-mfa endpoint",
        )

    access_token = auth_service.create_token_for_user(user.username)
    refresh_token = auth_service.create_refresh_token_for_user(user.username)

    logger.info(f"User logged in with refresh token: {user.username}")

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.access_token_expire_minutes * 60,
    )


@app.post("/api/v1/auth/refresh", response_model=Token)
async def refresh_access_token(refresh_request: RefreshTokenRequest) -> Token:
    """
    Get a new access token using a refresh token

    Args:
        refresh_request: Refresh token request

    Returns:
        New access token
    """
    username = auth_service.verify_refresh_token(refresh_request.refresh_token)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_token_for_user(username)

    logger.info(f"Access token refreshed for user: {username}")

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=config.access_token_expire_minutes * 60,
    )


@app.post("/api/v1/auth/revoke-refresh-token")
async def revoke_refresh_token(
    refresh_request: RefreshTokenRequest, current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Revoke a refresh token

    Args:
        refresh_request: Refresh token to revoke
        current_user: Current authenticated user

    Returns:
        Success message
    """
    success = auth_service.revoke_refresh_token(refresh_request.refresh_token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found"
        )

    logger.info(f"Refresh token revoked for user: {current_user.username}")
    return {"message": "Refresh token revoked successfully"}


# ============================================================================
# Multi-Factor Authentication Endpoints
# ============================================================================


@app.post("/api/v1/auth/mfa/enroll", response_model=MFAEnrollment)
async def enroll_mfa(current_user: User = Depends(get_current_user)) -> MFAEnrollment:
    """
    Enroll in multi-factor authentication

    Args:
        current_user: Current authenticated user

    Returns:
        MFA secret and QR code
    """
    try:
        secret, qr_code = auth_service.enable_mfa(current_user.username)

        logger.info(f"MFA enrollment started for user: {current_user.username}")

        return MFAEnrollment(secret=secret, qr_code_url=qr_code)
    except Exception as e:
        logger.error(f"Error enrolling MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enroll MFA",
        )


@app.post("/api/v1/auth/mfa/verify")
async def verify_and_enable_mfa(
    verification: MFAVerification, current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Verify MFA token and complete enrollment

    Args:
        verification: MFA verification request
        current_user: Current authenticated user

    Returns:
        Success message
    """
    success = auth_service.verify_and_enable_mfa(
        current_user.username, verification.token
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA token"
        )

    logger.info(f"MFA enabled for user: {current_user.username}")
    return {"message": "MFA enabled successfully"}


@app.post("/api/v1/auth/mfa/disable")
async def disable_mfa(
    password_verification: PasswordChange,
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Disable multi-factor authentication

    Args:
        password_verification: Current password for verification
        current_user: Current authenticated user

    Returns:
        Success message
    """
    success = auth_service.disable_mfa(
        current_user.username, password_verification.current_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password"
        )

    logger.info(f"MFA disabled for user: {current_user.username}")
    return {"message": "MFA disabled successfully"}


@app.post("/api/v1/auth/login-mfa", response_model=TokenPair)
async def login_with_mfa(mfa_credentials: MFALogin) -> TokenPair:
    """
    Login with username, password, and MFA token

    Args:
        mfa_credentials: MFA login credentials

    Returns:
        Access token and refresh token pair
    """
    user = auth_service.authenticate_user(
        mfa_credentials.username, mfa_credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled for this user",
        )

    # Verify MFA token
    if not auth_service.verify_mfa(mfa_credentials.username, mfa_credentials.mfa_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_token_for_user(user.username)
    refresh_token = auth_service.create_refresh_token_for_user(user.username)

    logger.info(f"User logged in with MFA: {user.username}")

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.access_token_expire_minutes * 60,
    )


# ============================================================================
# Session Management Endpoints
# ============================================================================


@app.get("/api/v1/auth/sessions", response_model=List[Session])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
) -> List[Session]:
    """
    Get all active sessions for current user

    Args:
        current_user: Current authenticated user

    Returns:
        List of active sessions
    """
    sessions = auth_service.get_user_sessions(current_user.username)
    return sessions


@app.delete("/api/v1/auth/sessions/{session_id}")
async def revoke_session(
    session_id: str, current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Revoke a specific session

    Args:
        session_id: Session ID to revoke
        current_user: Current authenticated user

    Returns:
        Success message
    """
    success = auth_service.revoke_session(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    logger.info(f"Session revoked: {session_id} for user: {current_user.username}")
    return {"message": "Session revoked successfully"}


@app.delete("/api/v1/auth/sessions")
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Revoke all sessions for current user

    Args:
        current_user: Current authenticated user

    Returns:
        Number of sessions revoked
    """
    count = auth_service.revoke_all_user_sessions(current_user.username)

    logger.info(f"All sessions revoked for user: {current_user.username}")
    return {"message": "All sessions revoked successfully", "count": count}


# ============================================================================
# Password Reset Endpoints
# ============================================================================


@app.post("/api/v1/auth/password-reset/request")
async def request_password_reset(reset_request: PasswordResetRequest) -> Dict[str, str]:
    """
    Request a password reset token

    Args:
        reset_request: Password reset request with email

    Returns:
        Success message (always returns success to prevent email enumeration)
    """
    token = auth_service.request_password_reset(reset_request.email)

    # In production, send email here
    # For now, log the token (DO NOT DO THIS IN PRODUCTION!)
    if token:
        logger.info(
            f"Password reset token generated: {token[:10]}... for email: {reset_request.email}"
        )

    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@app.post("/api/v1/auth/password-reset/confirm")
async def confirm_password_reset(reset_confirm: PasswordResetConfirm) -> Dict[str, str]:
    """
    Reset password using reset token

    Args:
        reset_confirm: Password reset confirmation with token and new password

    Returns:
        Success message
    """
    success = auth_service.reset_password(
        reset_confirm.token, reset_confirm.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    logger.info("Password reset completed successfully")
    return {"message": "Password reset successfully"}


# ============================================================================
# Audit Log Endpoints
# ============================================================================


@app.get("/api/v1/auth/audit-logs", response_model=List[AuditLogEntry])
async def get_audit_logs(
    action: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> List[AuditLogEntry]:
    """
    Get audit logs for current user

    Args:
        action: Filter by action type
        limit: Maximum number of entries to return
        current_user: Current authenticated user

    Returns:
        List of audit log entries
    """
    logs = auth_service.get_audit_logs(
        user_id=current_user.username, action=action, limit=limit
    )
    return logs


@app.get("/api/v1/auth/audit-logs/all", response_model=List[AuditLogEntry])
async def get_all_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> List[AuditLogEntry]:
    """
    Get all audit logs (Admin only)

    Args:
        user_id: Filter by user ID
        action: Filter by action type
        limit: Maximum number of entries to return
        current_user: Current authenticated user (must be admin)

    Returns:
        List of audit log entries
    """
    logs = auth_service.get_audit_logs(user_id=user_id, action=action, limit=limit)
    return logs


# ============================================================================
# OAuth2 Integration Endpoints
# ============================================================================


@app.get("/api/v1/auth/oauth/{provider}/login")
async def oauth_login(provider: OAuth2Provider) -> Dict[str, str]:
    """
    Initiate OAuth2 login flow

    Args:
        provider: OAuth2 provider (google or github)

    Returns:
        Authorization URL to redirect user to
    """
    # OAuth2 configuration (in production, use environment variables)
    oauth_configs = {
        OAuth2Provider.GOOGLE: {
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "client_id": "YOUR_GOOGLE_CLIENT_ID",
            "redirect_uri": f"{config.api_base_url}/api/v1/auth/oauth/google/callback",
            "scope": "openid email profile",
        },
        OAuth2Provider.GITHUB: {
            "auth_url": "https://github.com/login/oauth/authorize",
            "client_id": "YOUR_GITHUB_CLIENT_ID",
            "redirect_uri": f"{config.api_base_url}/api/v1/auth/oauth/github/callback",
            "scope": "user:email",
        },
    }

    config_data = oauth_configs.get(provider)
    if not config_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth provider"
        )

    # Build authorization URL
    auth_url = (
        f"{config_data['auth_url']}?"
        f"client_id={config_data['client_id']}&"
        f"redirect_uri={config_data['redirect_uri']}&"
        f"scope={config_data['scope']}&"
        f"response_type=code"
    )

    return {
        "authorization_url": auth_url,
        "message": "Redirect user to this URL for OAuth login",
    }


@app.post("/api/v1/auth/oauth/callback", response_model=TokenPair)
async def oauth_callback(oauth_login: OAuth2Login) -> TokenPair:
    """
    Handle OAuth2 callback

    Args:
        oauth_login: OAuth2 callback data

    Returns:
        Access token and refresh token pair
    """
    # In production, exchange code for access token with OAuth provider
    # Then fetch user info and create/update user

    # Mock implementation - in production, implement proper OAuth flow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth2 callback implementation requires provider-specific configuration. "
        "Please configure OAuth2 credentials in environment variables.",
    )


# ============================================================================
# User Management Endpoints (Admin Only)
# ============================================================================


@app.get("/api/v1/users", response_model=List[User])
async def list_users(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> List[User]:
    """
    List all users (Admin only)

    Args:
        current_user: Current authenticated admin user

    Returns:
        List of all users
    """
    return [auth_service.get_user(username) for username in auth_service.users.keys()]


@app.get("/api/v1/users/{username}", response_model=User)
async def get_user(
    username: str, current_user: User = Depends(require_role(UserRole.ADMIN))
) -> User:
    """
    Get user by username (Admin only)

    Args:
        username: Username to retrieve
        current_user: Current authenticated admin user

    Returns:
        User object
    """
    user = auth_service.get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@app.post("/api/v1/users/{username}/deactivate")
async def deactivate_user(
    username: str, current_user: User = Depends(require_role(UserRole.ADMIN))
) -> Dict[str, str]:
    """
    Deactivate a user account (Admin only)

    Args:
        username: Username to deactivate
        current_user: Current authenticated admin user

    Returns:
        Success message
    """
    if username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    success = auth_service.deactivate_user(username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    logger.info(f"User deactivated by {current_user.username}: {username}")
    return {"message": f"User {username} deactivated successfully"}


@app.post("/api/v1/users/{username}/activate")
async def activate_user(
    username: str, current_user: User = Depends(require_role(UserRole.ADMIN))
) -> Dict[str, str]:
    """
    Activate a user account (Admin only)

    Args:
        username: Username to activate
        current_user: Current authenticated admin user

    Returns:
        Success message
    """
    success = auth_service.activate_user(username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    logger.info(f"User activated by {current_user.username}: {username}")
    return {"message": f"User {username} activated successfully"}


# ============================================================================
# Trading and Analysis Endpoints
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Sentio 2.0 Trading API",
        "version": "2.0.0",
        "status": STATUS_OPERATIONAL,
    }


@app.get("/api/v1/status")
async def get_status(token: str = Depends(verify_token)) -> SystemStatus:
    """Get system status"""
    engine = get_trading_engine()
    health = engine.get_health_report()

    return SystemStatus(
        status=STATUS_OPERATIONAL,
        mode=health["mode"],
        active_strategies=len([s for s in engine.strategies.values() if s.enabled]),
        open_positions=len(engine.open_positions),
        portfolio_value=engine.portfolio_value,
        daily_pnl=engine.daily_pnl,
    )


@app.post("/api/v1/analyze")
@api_error_handler
async def analyze_symbol(
    request: AnalysisRequest, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Perform comprehensive analysis on a symbol

    Analyzes a trading symbol using multiple strategies and technical indicators,
    returning aggregated signals and confidence scores.

    Args:
        request: Analysis request containing:
            - symbol: Stock ticker symbol (e.g., 'AAPL')
            - timeframe: Trading timeframe (e.g., '5min', '1h', '1d')
        token: Authentication token (provided via Depends)

    Returns:
        Dictionary containing:
            - symbol: Analyzed symbol
            - timeframe: Analysis timeframe
            - signals: Individual strategy signals with confidence
            - aggregated_signal: Voting result from all strategies
            - technical_analysis: Technical indicators (RSI, MACD, etc.)
            - timestamp: Analysis timestamp

    Raises:
        HTTPException: If symbol is invalid or analysis fails

    Example:
        POST /api/v1/analyze
        {
            "symbol": "AAPL",
            "timeframe": "5min"
        }

        Response:
        {
            "symbol": "AAPL",
            "aggregated_signal": "BUY",
            "confidence": 0.85,
            "signals": [...]
        }
    """
    engine = get_trading_engine()

    # Run analysis
    voting_result = engine.analyze_symbol(request.symbol)

    # Get technical analysis
    data = engine.data_manager.get_data(request.symbol, request.timeframe)
    technical = ta_engine.analyze_comprehensive(data, request.symbol)

    # Get insider activity
    insider_analysis = insider_tracker.analyze_symbol(request.symbol)

    return {
        "symbol": request.symbol,
        "timestamp": format_timestamp(),
        "voting_result": voting_result.to_dict(),
        "technical_analysis": technical,
        "insider_activity": insider_analysis,
    }


@app.post("/api/v1/trade")
@api_error_handler
async def execute_trade(
    request: TradeRequest, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Execute a trade order

    Executes a buy, sell, or close trade order after running risk checks
    and strategy validation.

    Args:
        request: Trade request containing:
            - symbol: Stock ticker symbol
            - action: Trade action ('buy', 'sell', or 'close')
            - quantity: Optional quantity (calculated if not provided)
        token: Authentication token

    Returns:
        Dictionary containing:
            - status: 'success', 'warning', or 'error'
            - message: Status message
            - order_details: Order execution information (order_id, status, price, etc.)
            - recommendation: Strategy recommendation (if conflict detected)

    Raises:
        HTTPException: If trade execution fails

    Example:
        POST /api/v1/trade
        {
            "symbol": "AAPL",
            "action": "buy",
            "quantity": 100
        }
    """
    engine = get_trading_engine()

    if request.action == "close":
        if request.symbol not in engine.open_positions:
            return create_error_response(f"No open position found for {request.symbol}")

        engine.close_position(request.symbol, reason="manual")
        return create_success_response(
            f"Position closed for {request.symbol}", {"symbol": request.symbol}
        )

    # For buy/sell, run analysis first
    voting_result = engine.analyze_symbol(request.symbol)

    if voting_result.final_signal.value != request.action:
        return create_warning_response(
            f"Manual action conflicts with strategy recommendation: {voting_result.final_signal.value}",
            {"recommendation": voting_result.to_dict()},
        )

    # Execute signal and get order details
    order = engine.execute_signal(request.symbol, voting_result)

    # Check order status and format response
    if order["status"] == "filled":
        response_data = {
            "order_details": {
                "order_id": order.get("order_id"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "quantity": order.get("quantity"),
                "filled_price": order.get("filled_price"),
                "filled_qty": order.get("filled_qty"),
                "status": order.get("status"),
                "timestamp": (
                    order.get("timestamp").isoformat()
                    if order.get("timestamp")
                    else None
                ),
            },
            "voting_result": voting_result.to_dict(),
        }

        # Broadcast notification to user
        try:
            from ..data.dashboard_websocket_service import dashboard_ws_manager

            notification = {
                "type": "success",
                "title": "Trade Executed",
                "message": f'{request.action.upper()} order for {order.get("quantity")} shares of {request.symbol} executed at ${order.get("filled_price")}',
                "data": response_data,
            }
            # Extract user_id from token for notification broadcasting
            try:
                payload = verify_jwt_token(token)
                user_id = (
                    payload.get("sub", "unknown_user") if payload else "unknown_user"
                )
            except Exception:
                user_id = "unknown_user"
            asyncio.create_task(
                dashboard_ws_manager.broadcast_notification(user_id, notification)
            )
        except Exception as ws_error:
            logger.warning(
                f"Failed to broadcast trade notification via WebSocket: {ws_error}"
            )

        return create_success_response(
            f"Trade executed successfully for {request.symbol}", response_data
        )
    elif order["status"] == "rejected":
        return create_error_response(
            f'Trade rejected: {order.get("message", "Unknown reason")}',
            order.get("message"),
        )
    elif order["status"] == "pending":
        return create_success_response(
            f"Order placed and pending execution",
            {
                "order_details": {
                    "order_id": order.get("order_id"),
                    "symbol": order.get("symbol"),
                    "status": order.get("status"),
                    "message": order.get("message"),
                }
            },
        )
    else:
        return create_error_response(
            f'Unknown order status: {order.get("status")}', str(order)
        )


@app.get("/api/v1/positions")
async def get_positions(token: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get open positions"""
    engine = get_trading_engine()
    return {"positions": engine.open_positions, "count": len(engine.open_positions)}


@app.get("/api/v1/orders/{order_id}")
@api_error_handler
async def get_order_status(
    order_id: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get status of a specific order

    Args:
        order_id: Order identifier
        token: Authentication token

    Returns:
        Order details including current status
    """
    engine = get_trading_engine()
    order = engine.get_order_status(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found"
        )

    return create_success_response(
        f"Order status retrieved",
        {
            "order": {
                "order_id": order.get("order_id"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "quantity": order.get("quantity"),
                "price": order.get("price"),
                "filled_price": order.get("filled_price"),
                "filled_qty": order.get("filled_qty"),
                "status": order.get("status"),
                "message": order.get("message"),
                "timestamp": (
                    order.get("timestamp").isoformat()
                    if order.get("timestamp")
                    else None
                ),
            }
        },
    )


@app.get("/api/v1/orders")
@api_error_handler
async def get_orders(
    symbol: Optional[str] = None, limit: int = 100, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get order history

    Args:
        symbol: Optional symbol filter
        limit: Maximum number of orders to return
        token: Authentication token

    Returns:
        List of orders
    """
    engine = get_trading_engine()
    orders = engine.get_all_orders(symbol=symbol, limit=limit)

    formatted_orders = []
    for order in orders:
        formatted_orders.append(
            {
                "order_id": order.get("order_id"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "quantity": order.get("quantity"),
                "price": order.get("price"),
                "filled_price": order.get("filled_price"),
                "filled_qty": order.get("filled_qty"),
                "status": order.get("status"),
                "message": order.get("message"),
                "timestamp": (
                    order.get("timestamp").isoformat()
                    if order.get("timestamp")
                    else None
                ),
            }
        )

    return create_success_response(
        f"Retrieved {len(formatted_orders)} orders",
        {"orders": formatted_orders, "count": len(formatted_orders)},
    )


@app.get("/api/v1/performance")
async def get_performance(token: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get performance metrics"""
    engine = get_trading_engine()
    return engine.get_performance_summary()


@app.get("/api/v1/strategies")
async def get_strategies(token: str = Depends(verify_token)) -> List[Dict[str, Any]]:
    """Get active strategies and their performance"""
    engine = get_trading_engine()

    strategies_info = []
    for name, strategy in engine.strategies.items():
        strategies_info.append(
            {
                "name": name,
                "type": strategy.strategy_type.value,
                "enabled": strategy.enabled,
                "timeframe": strategy.timeframe,
                "min_confidence": strategy.min_confidence,
                "performance": strategy.get_performance_metrics(),
            }
        )

    return strategies_info


@app.post("/api/v1/strategies/{strategy_name}/toggle")
async def toggle_strategy(
    strategy_name: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Enable or disable a strategy"""
    engine = get_trading_engine()

    if strategy_name not in engine.strategies:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy = engine.strategies[strategy_name]
    strategy.enabled = not strategy.enabled

    return {"strategy": strategy_name, "enabled": strategy.enabled}


@app.get("/api/v1/insider-trades/{symbol}")
async def get_insider_trades(
    symbol: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get insider trading activity for a symbol"""
    analysis = insider_tracker.analyze_symbol(symbol)
    return analysis


@app.get("/api/v1/insider-trades/top")
async def get_top_traded_symbols(
    days: int = 30, token: str = Depends(verify_token)
) -> List[Dict[str, Any]]:
    """Get most traded symbols by insiders"""
    return insider_tracker.get_top_traded_symbols(days=days)


@app.get("/api/v1/fundamental/{symbol}")
async def get_fundamental_analysis(
    symbol: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get fundamental analysis for long-term investment"""
    # In production: fetch real financial data
    mock_data = {
        "symbol": symbol,
        "current_price": 100.0,
        "pe_ratio": 20.0,
        "pb_ratio": 3.0,
        "revenue_growth_yoy": 0.15,
        "roe": 0.20,
        "debt_to_equity": 0.5,
        "current_ratio": 2.0,
    }

    score = fundamental_engine.analyze_company(symbol, mock_data)

    return {
        "symbol": symbol,
        "overall_score": score.overall_score,
        "recommendation": score.recommendation,
        "target_price": score.target_price,
        "scores": {
            "value": score.value_score,
            "growth": score.growth_score,
            "profitability": score.profitability_score,
            "financial_health": score.financial_health_score,
            "moat": score.moat_score,
            "management": score.management_score,
            "esg": score.esg_score,
        },
        "timestamp": score.timestamp.isoformat(),
    }


@app.get("/api/v1/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": STATUS_HEALTHY}


# ============================================================================
# API Monitoring & Analytics Endpoints
# ============================================================================


@app.get("/api/v1/metrics/overview")
async def get_metrics_overview(token: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get overall API metrics and statistics"""
    if not api_monitor or not config.monitoring.enabled:
        raise HTTPException(status_code=503, detail="Monitoring is not enabled")

    return api_monitor.get_overall_statistics()


@app.get("/api/v1/metrics/endpoints")
async def get_endpoint_metrics(token: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get per-endpoint statistics"""
    if not api_monitor or not config.monitoring.enabled:
        raise HTTPException(status_code=503, detail="Monitoring is not enabled")

    return api_monitor.get_endpoint_statistics()


@app.get("/api/v1/metrics/users")
async def get_user_metrics(
    user_id: Optional[str] = None, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get user-specific API usage statistics"""
    if not api_monitor or not config.monitoring.enabled:
        raise HTTPException(status_code=503, detail="Monitoring is not enabled")

    return api_monitor.get_user_statistics(user_id)


@app.get("/api/v1/metrics/hourly")
async def get_hourly_metrics(
    hours: int = 24, token: str = Depends(verify_token)
) -> List[Dict[str, Any]]:
    """
    Get hourly API usage statistics

    Args:
        hours: Number of hours to look back (default: 24)
    """
    if not api_monitor or not config.monitoring.enabled:
        raise HTTPException(status_code=503, detail="Monitoring is not enabled")

    return api_monitor.get_hourly_statistics(hours)


@app.get("/api/v1/metrics/errors")
async def get_recent_errors(
    limit: int = 50, token: str = Depends(verify_token)
) -> List[Dict[str, Any]]:
    """
    Get recent API errors

    Args:
        limit: Maximum number of errors to return (default: 50)
    """
    if not api_monitor or not config.monitoring.enabled:
        raise HTTPException(status_code=503, detail="Monitoring is not enabled")

    return api_monitor.get_recent_errors(limit)


@app.get("/api/v1/rate-limit/status")
async def get_rate_limit_status(
    request: Request, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get current rate limit status for the requester"""
    if not rate_limiter or not config.rate_limit.enabled:
        raise HTTPException(status_code=503, detail="Rate limiting is not enabled")

    identifier = rate_limiter._get_identifier(request)
    usage = rate_limiter.get_usage_stats(identifier)

    return {
        **usage,
        "rate_limit_config": {
            "requests_per_minute": config.rate_limit.requests_per_minute,
            "requests_per_hour": config.rate_limit.requests_per_hour,
            "requests_per_day": config.rate_limit.requests_per_day,
        },
    }


# ============================================================================
# Dashboard & User Features Endpoints
# ============================================================================


@app.get("/api/v1/dashboard/trade-signals")
@api_error_handler
async def get_trade_signals(
    symbols: Optional[str] = None, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get trade signals summary for dashboard with caching

    Args:
        symbols: Comma-separated list of symbols (optional)
    """
    # Parse symbol list
    symbol_list = parse_symbol_list(symbols, DEFAULT_SYMBOLS)

    # Create cache key based on symbols
    cache_key = f"trade_signals:{','.join(sorted(symbol_list))}"

    # Check cache first
    cached_result = response_cache.get(cache_key)
    if cached_result:
        logger.debug(f"Returning cached trade signals for {len(symbol_list)} symbols")
        return cached_result

    engine = get_trading_engine()

    # Process symbols concurrently for better performance
    signals = []

    # Use asyncio gather for concurrent analysis
    async def analyze_symbol_async(symbol: str) -> Dict[str, Any]:
        try:
            voting_result = engine.analyze_symbol(symbol.strip())
            return {
                "symbol": symbol.strip(),
                "signal": voting_result.final_signal.value,
                "confidence": voting_result.confidence,
                "consensus_strength": voting_result.consensus_strength,
                "timestamp": format_timestamp(),
            }
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {"symbol": symbol.strip(), "signal": SIGNAL_ERROR, "error": str(e)}

    # Analyze all symbols concurrently
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_symbol = {
            executor.submit(engine.analyze_symbol, symbol.strip()): symbol
            for symbol in symbol_list
        }

        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                voting_result = future.result()
                signals.append(
                    {
                        "symbol": symbol.strip(),
                        "signal": voting_result.final_signal.value,
                        "confidence": voting_result.confidence,
                        "consensus_strength": voting_result.consensus_strength,
                        "timestamp": format_timestamp(),
                    }
                )
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                signals.append(
                    {"symbol": symbol.strip(), "signal": SIGNAL_ERROR, "error": str(e)}
                )

    result = {
        "signals": signals,
        "count": len(signals),
        "timestamp": format_timestamp(),
    }

    # Cache the result (30 seconds TTL as configured)
    cache_ttl = config.cache.strategy_ttl if hasattr(config, "cache") else 30
    response_cache.set(cache_key, result, ttl_seconds=cache_ttl)

    # Broadcast trade signals to WebSocket clients
    try:
        from ..data.dashboard_websocket_service import dashboard_ws_manager

        asyncio.create_task(dashboard_ws_manager.broadcast_trade_signals(signals))
    except Exception as ws_error:
        logger.warning(f"Failed to broadcast trade signals via WebSocket: {ws_error}")

    return result


@app.get("/api/v1/dashboard/earnings")
@api_error_handler
async def get_earnings_summary(
    user_id: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get earnings and performance summary for user dashboard

    Args:
        user_id: User identifier
    """
    try:
        engine = get_trading_engine()
        performance = engine.get_performance_summary()

        # Get subscription info for profit sharing
        subscription = subscription_manager.get_subscription(user_id)

        profit_sharing_total = 0.0
        profit_sharing_rate = 0.0

        if subscription:
            profit_sharing_total = subscription.total_profits_shared
            features = subscription_manager.get_tier_features(subscription.tier)
            profit_sharing_rate = features.profit_sharing_rate

        earnings_data = {
            "user_id": user_id,
            "portfolio_value": performance.get("portfolio_value", 0.0),
            "total_return": performance.get("total_return", 0.0),
            "total_return_pct": performance.get("total_return_pct", 0.0),
            "daily_pnl": performance.get("daily_pnl", 0.0),
            "total_trades": performance.get("total_trades", 0),
            "win_rate": performance.get("win_rate", 0.0),
            "profit_sharing": {
                "total_shared": profit_sharing_total,
                "rate": profit_sharing_rate,
                "enabled": profit_sharing_rate > 0,
            },
            "timestamp": datetime.now().isoformat(),
        }

        # Broadcast earnings to WebSocket clients
        try:
            from ..data.dashboard_websocket_service import dashboard_ws_manager

            asyncio.create_task(
                dashboard_ws_manager.broadcast_earnings(user_id, earnings_data)
            )
        except Exception as ws_error:
            logger.warning(f"Failed to broadcast earnings via WebSocket: {ws_error}")

        return earnings_data

    except Exception as e:
        logger.error(f"Error getting earnings summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/dashboard/ai-summary")
@api_error_handler
async def get_ai_trade_summary(
    symbol: Optional[str] = None, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get AI-generated summary of trading recommendations

    Args:
        symbol: Optional symbol to focus on
    """
    try:
        engine = get_trading_engine()

        if symbol:
            # Get specific symbol analysis
            voting_result = engine.analyze_symbol(symbol)

            # Generate AI summary based on voting results
            summary = {
                "symbol": symbol,
                "recommendation": voting_result.final_signal.value,
                "confidence": voting_result.confidence,
                "reasoning": f"Based on {len(voting_result.votes)} strategy votes, "
                f"the system recommends {voting_result.final_signal.value.upper()} "
                f"with {voting_result.confidence:.1%} confidence. "
                f"Consensus strength: {voting_result.consensus_strength:.1%}.",
                "key_factors": [
                    f"Strategy consensus: {voting_result.consensus_strength:.1%}",
                    f"Signal confidence: {voting_result.confidence:.1%}",
                    f"Active strategies: {len(voting_result.votes)}",
                ],
                "timestamp": datetime.now().isoformat(),
            }
        else:
            # Get general market summary
            performance = engine.get_performance_summary()
            daily_pnl = performance.get("daily_pnl", 0.0)
            open_positions = performance.get("open_positions", 0)
            win_rate = performance.get("win_rate", 0.0)
            total_return_pct = performance.get("total_return_pct", 0.0)

            summary = {
                "market_overview": "general",
                "portfolio_status": "active" if open_positions > 0 else "idle",
                "summary": f"Portfolio is {('up' if daily_pnl > 0 else 'down')} "
                f"${abs(daily_pnl):.2f} today. "
                f"{open_positions} positions open. "
                f"Win rate: {win_rate:.1%}.",
                "key_metrics": {
                    "daily_pnl": daily_pnl,
                    "open_positions": open_positions,
                    "win_rate": win_rate,
                    "total_return_pct": total_return_pct,
                },
                "timestamp": datetime.now().isoformat(),
            }

        return summary
    except Exception as e:
        logger.error(f"Error getting AI summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/dashboard/strength-signal")
@api_error_handler
async def get_strength_signal(
    symbol: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get market strength signal for a symbol

    Args:
        symbol: Trading symbol
    """
    engine = get_trading_engine()

    # Get market data
    data = engine.data_manager.get_data(symbol, timeframe=DEFAULT_TIMEFRAME)

    # Get technical analysis
    technical = ta_engine.analyze_comprehensive(data, symbol)

    # Use strength signal service for calculation
    strength_analysis = strength_signal_service.analyze_strength(technical)

    return {
        "symbol": symbol,
        "strength_score": strength_analysis["strength_score"],
        "signal": strength_analysis["signal"],
        "components": strength_analysis["components"],
        "timestamp": format_timestamp(),
    }


@app.get("/api/v1/dashboard/trade-journal")
@api_error_handler
async def get_trade_journal(
    user_id: str,
    limit: int = DEFAULT_TRADE_JOURNAL_LIMIT,
    token: str = Depends(verify_token),
) -> Dict[str, Any]:
    """
    Get trade journal entries for user

    Args:
        user_id: User identifier
        limit: Maximum number of entries to return
    """
    engine = get_trading_engine()

    # Get recent trades from history
    recent_trades = engine.trade_history[-limit:] if engine.trade_history else []

    # Format entries using utility function
    journal_entries = [format_journal_entry(trade) for trade in recent_trades]

    return {
        "user_id": user_id,
        "entries": journal_entries,
        "count": len(journal_entries),
        "timestamp": format_timestamp(),
    }


@app.post("/api/v1/dashboard/trade-journal")
async def add_trade_journal_entry(
    entry: TradeJournalEntry, user_id: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Add a manual trade journal entry

    Args:
        entry: Trade journal entry data
        user_id: User identifier
    """
    try:
        # Create journal entry
        journal_entry = {
            "user_id": user_id,
            "symbol": entry.symbol,
            "action": entry.action,
            "quantity": entry.quantity,
            "price": entry.price,
            "notes": entry.notes,
            "tags": entry.tags or [],
            "timestamp": datetime.now().isoformat(),
        }

        # In production: save to database
        logger.info(f"Trade journal entry added for {user_id}: {entry.symbol}")

        return {"status": "success", "entry": journal_entry}

    except Exception as e:
        logger.error(f"Error adding trade journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/dashboard/performance-cards")
async def get_performance_cards(
    user_id: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get performance metrics cards for dashboard

    Args:
        user_id: User identifier
    """
    try:
        engine = get_trading_engine()
        performance = engine.get_performance_summary()

        # Get subscription info
        subscription = subscription_manager.get_subscription(user_id)
        tier = subscription.tier.value if subscription else "free"

        # Get values with defaults for missing keys
        total_return_pct = performance.get("total_return_pct", 0.0)
        daily_pnl = performance.get("daily_pnl", 0.0)
        win_rate = performance.get("win_rate", 0.0)
        wins = performance.get("wins", 0)
        losses = performance.get("losses", 0)
        open_positions = performance.get("open_positions", 0)

        cards = [
            {
                "id": "portfolio_value",
                "title": "Portfolio Value",
                "value": f"${performance['portfolio_value']:,.2f}",
                "change": total_return_pct,
                "change_label": f"{total_return_pct:+.2f}%",
                "trend": "up" if total_return_pct > 0 else "down",
            },
            {
                "id": "daily_pnl",
                "title": "Daily P&L",
                "value": f"${daily_pnl:,.2f}",
                "change": daily_pnl,
                "change_label": f"${daily_pnl:+,.2f}",
                "trend": "up" if daily_pnl > 0 else "down",
            },
            {
                "id": "win_rate",
                "title": "Win Rate",
                "value": f"{win_rate:.1%}",
                "subtitle": f"{wins}W / {losses}L",
            },
            {
                "id": "total_trades",
                "title": "Total Trades",
                "value": str(performance["total_trades"]),
                "subtitle": f"{open_positions} open",
            },
            {
                "id": "subscription",
                "title": "Subscription Tier",
                "value": tier.title(),
                "subtitle": "Active",
            },
        ]

        return {
            "user_id": user_id,
            "cards": cards,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting performance cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Subscription & Billing Endpoints
# ============================================================================


@app.get("/api/v1/subscription/pricing")
async def get_pricing() -> Dict[str, Any]:
    """Get pricing information for all subscription tiers"""
    try:
        pricing_info = subscription_manager.get_pricing_info()

        return {"tiers": pricing_info, "timestamp": datetime.now().isoformat()}

    except Exception as e:
        logger.error(f"Error getting pricing info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/subscription/{user_id}")
async def get_user_subscription(
    user_id: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get user's subscription details"""
    try:
        subscription = subscription_manager.get_subscription(user_id)

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        features = subscription_manager.get_tier_features(subscription.tier)

        return {
            "user_id": user_id,
            "tier": subscription.tier.value,
            "status": subscription.status.value,
            "start_date": subscription.start_date.isoformat(),
            "profit_sharing": {
                "balance": subscription.profit_sharing_balance,
                "total_shared": subscription.total_profits_shared,
                "rate": features.profit_sharing_rate,
            },
            "features": {
                "max_concurrent_trades": features.max_concurrent_trades,
                "max_strategies": features.max_strategies,
                "day_trading": features.day_trading,
                "api_access": features.api_access,
                "advanced_analytics": features.advanced_analytics,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/subscription/profit-sharing/calculate")
async def calculate_profit_sharing(
    request: ProfitSharingRequest, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Calculate profit-sharing amount for a trade

    Args:
        request: Profit sharing request with user_id and trading_profit
    """
    try:
        sharing_amount = subscription_manager.calculate_profit_sharing(
            user_id=request.user_id, trading_profit=request.trading_profit
        )

        subscription = subscription_manager.get_subscription(request.user_id)

        return {
            "user_id": request.user_id,
            "trading_profit": request.trading_profit,
            "sharing_amount": sharing_amount,
            "profit_sharing_balance": (
                subscription.profit_sharing_balance if subscription else 0.0
            ),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error calculating profit sharing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/subscription/profit-sharing/{user_id}")
async def get_profit_sharing_balance(
    user_id: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """Get user's profit-sharing balance"""
    try:
        subscription = subscription_manager.get_subscription(user_id)

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        features = subscription_manager.get_tier_features(subscription.tier)

        return {
            "user_id": user_id,
            "balance": subscription.profit_sharing_balance,
            "total_shared": subscription.total_profits_shared,
            "rate": features.profit_sharing_rate,
            "enabled": features.profit_sharing_enabled,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profit sharing balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Admin Endpoints
# ============================================================================


@app.get("/api/v1/admin/users")
async def get_all_users(token: str = Depends(verify_admin_token)) -> Dict[str, Any]:
    """Get all users with their subscription details (admin only)"""
    try:
        users = []
        for user_id, subscription in subscription_manager.subscriptions.items():
            users.append(
                {
                    "user_id": user_id,
                    "tier": subscription.tier.value,
                    "status": subscription.status.value,
                    "start_date": subscription.start_date.isoformat(),
                    "end_date": (
                        subscription.end_date.isoformat()
                        if subscription.end_date
                        else None
                    ),
                    "profit_sharing_balance": subscription.profit_sharing_balance,
                    "total_profits_shared": subscription.total_profits_shared,
                }
            )

        return {
            "users": users,
            "total_users": len(users),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/admin/analytics/revenue")
async def get_revenue_analytics(
    token: str = Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Get revenue analytics (admin only)"""
    try:
        from ..billing.subscription_manager import TIER_PRICING

        # Calculate revenue by tier
        revenue_by_tier = {}
        total_mrr = 0.0
        tier_counts = {}

        for user_id, subscription in subscription_manager.subscriptions.items():
            tier = subscription.tier
            tier_name = tier.value

            if subscription.status.value in ["active", "trial"]:
                revenue = TIER_PRICING.get(tier, 0.0)
                revenue_by_tier[tier_name] = (
                    revenue_by_tier.get(tier_name, 0.0) + revenue
                )
                total_mrr += revenue
                tier_counts[tier_name] = tier_counts.get(tier_name, 0) + 1

        return {
            "monthly_recurring_revenue": total_mrr,
            "revenue_by_tier": revenue_by_tier,
            "subscribers_by_tier": tier_counts,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/admin/analytics/users")
async def get_user_analytics(
    token: str = Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Get user growth analytics (admin only)"""
    try:
        total_users = len(subscription_manager.subscriptions)

        # Count by status
        status_counts = {}
        tier_counts = {}

        for user_id, subscription in subscription_manager.subscriptions.items():
            status = subscription.status.value
            tier = subscription.tier.value

            status_counts[status] = status_counts.get(status, 0) + 1
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        return {
            "total_users": total_users,
            "by_status": status_counts,
            "by_tier": tier_counts,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/admin/pricing/update")
async def update_pricing(
    request: UpdatePricingRequest, token: str = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """Update pricing for a tier (admin only)"""
    try:
        from ..billing.subscription_manager import TIER_PRICING

        # Validate tier
        try:
            tier = SubscriptionTier(request.tier)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tier: {request.tier}")

        # Validate price
        if request.new_price < 0:
            raise HTTPException(status_code=400, detail="Price must be non-negative")

        # Update pricing
        old_price = TIER_PRICING[tier]
        TIER_PRICING[tier] = request.new_price

        logger.info(
            f"Admin updated {tier.value} pricing from ${old_price} to ${request.new_price}"
        )

        return {
            "tier": tier.value,
            "old_price": old_price,
            "new_price": request.new_price,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/admin/subscription/update")
async def admin_update_subscription(
    request: UpdateSubscriptionRequest, token: str = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """Update user's subscription tier (admin only)"""
    try:
        # Validate tier
        try:
            new_tier = SubscriptionTier(request.new_tier)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid tier: {request.new_tier}"
            )

        # Get existing subscription
        subscription = subscription_manager.get_subscription(request.user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="User subscription not found")

        old_tier = subscription.tier

        # Update subscription
        updated = subscription_manager.upgrade_subscription(request.user_id, new_tier)

        logger.info(
            f"Admin updated user {request.user_id} from {old_tier.value} to {new_tier.value}"
        )

        return {
            "user_id": request.user_id,
            "old_tier": old_tier.value,
            "new_tier": updated.tier.value,
            "status": updated.status.value,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/admin/subscribers")
async def get_subscribers(
    tier: Optional[str] = None,
    status: Optional[str] = None,
    token: str = Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Get filtered list of subscribers (admin only)"""
    try:
        subscribers = []

        for user_id, subscription in subscription_manager.subscriptions.items():
            # Apply filters
            if tier and subscription.tier.value != tier:
                continue
            if status and subscription.status.value != status:
                continue

            features = subscription_manager.get_tier_features(subscription.tier)

            subscribers.append(
                {
                    "user_id": user_id,
                    "tier": subscription.tier.value,
                    "status": subscription.status.value,
                    "start_date": subscription.start_date.isoformat(),
                    "end_date": (
                        subscription.end_date.isoformat()
                        if subscription.end_date
                        else None
                    ),
                    "profit_sharing_balance": subscription.profit_sharing_balance,
                    "total_profits_shared": subscription.total_profits_shared,
                    "features": {
                        "max_concurrent_trades": features.max_concurrent_trades,
                        "max_strategies": features.max_strategies,
                        "day_trading": features.day_trading,
                        "api_access": features.api_access,
                    },
                }
            )

        return {
            "subscribers": subscribers,
            "count": len(subscribers),
            "filters": {"tier": tier, "status": status},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting subscribers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Enhanced Analytics Endpoints
# ============================================================================


@app.get("/api/v1/analytics/portfolio-history")
async def get_portfolio_history(
    user_id: str, days: int = 30, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get historical portfolio performance data

    Args:
        user_id: User identifier
        days: Number of days of history (default: 30)

    Returns:
        Historical portfolio values and performance metrics
    """
    try:
        # Generate historical data points (mock data for demonstration)
        from datetime import timedelta

        history = []
        current_date = datetime.now()
        base_value = 100000.0

        # Generate daily portfolio values with some variance
        import random

        for i in range(days, -1, -1):
            date = current_date - timedelta(days=i)
            # Simulate portfolio growth with random daily changes
            daily_change = random.uniform(-0.02, 0.03)  # -2% to +3%
            base_value *= 1 + daily_change

            history.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "timestamp": date.isoformat(),
                    "portfolio_value": round(base_value, 2),
                    "daily_change": round(base_value * daily_change, 2),
                    "daily_change_pct": round(daily_change * 100, 2),
                }
            )

        # Calculate summary statistics
        initial_value = history[0]["portfolio_value"]
        final_value = history[-1]["portfolio_value"]
        total_return = final_value - initial_value
        total_return_pct = (total_return / initial_value) * 100

        return {
            "user_id": user_id,
            "period_days": days,
            "history": history,
            "summary": {
                "initial_value": round(initial_value, 2),
                "final_value": round(final_value, 2),
                "total_return": round(total_return, 2),
                "total_return_pct": round(total_return_pct, 2),
                "best_day": max(history, key=lambda x: x["daily_change_pct"]),
                "worst_day": min(history, key=lambda x: x["daily_change_pct"]),
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting portfolio history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/trade-performance")
async def get_trade_performance(
    user_id: str, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get detailed trade performance analytics

    Args:
        user_id: User identifier

    Returns:
        Trade performance metrics and distributions
    """
    try:
        # Mock trade performance data
        import random

        # Generate sample trade data
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA"]
        trade_data = []

        for symbol in symbols:
            num_trades = random.randint(5, 20)
            wins = random.randint(int(num_trades * 0.4), int(num_trades * 0.8))
            losses = num_trades - wins

            total_pnl = random.uniform(-500, 2000)

            trade_data.append(
                {
                    "symbol": symbol,
                    "total_trades": num_trades,
                    "wins": wins,
                    "losses": losses,
                    "win_rate": round(wins / num_trades, 2),
                    "total_pnl": round(total_pnl, 2),
                    "avg_win": round(random.uniform(100, 500), 2),
                    "avg_loss": round(random.uniform(-300, -50), 2),
                }
            )

        # Calculate overall statistics
        total_trades = sum(t["total_trades"] for t in trade_data)
        total_wins = sum(t["wins"] for t in trade_data)
        total_losses = sum(t["losses"] for t in trade_data)
        total_pnl = sum(t["total_pnl"] for t in trade_data)

        return {
            "user_id": user_id,
            "by_symbol": trade_data,
            "overall": {
                "total_trades": total_trades,
                "total_wins": total_wins,
                "total_losses": total_losses,
                "overall_win_rate": round(total_wins / total_trades, 2),
                "total_pnl": round(total_pnl, 2),
                "best_performer": max(trade_data, key=lambda x: x["total_pnl"]),
                "worst_performer": min(trade_data, key=lambda x: x["total_pnl"]),
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting trade performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/user-activity")
async def get_user_activity(
    user_id: str, days: int = 30, token: str = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get user activity trends and patterns

    Args:
        user_id: User identifier
        days: Number of days to analyze (default: 30)

    Returns:
        User activity metrics including trades per day, session times, etc.
    """
    try:
        from datetime import timedelta
        import random

        # Generate daily activity data
        activity = []
        current_date = datetime.now()

        for i in range(days, -1, -1):
            date = current_date - timedelta(days=i)

            # Simulate activity (more activity on weekdays)
            is_weekday = date.weekday() < 5
            base_trades = random.randint(2, 8) if is_weekday else random.randint(0, 3)

            activity.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "day_of_week": date.strftime("%A"),
                    "trades_executed": base_trades,
                    "session_duration_minutes": (
                        random.randint(15, 180) if base_trades > 0 else 0
                    ),
                    "api_calls": base_trades * random.randint(5, 15),
                }
            )

        # Calculate statistics
        total_trades = sum(a["trades_executed"] for a in activity)
        avg_trades_per_day = total_trades / len(activity)
        most_active_day = max(activity, key=lambda x: x["trades_executed"])

        # Activity by day of week
        day_of_week_stats = {}
        for entry in activity:
            day = entry["day_of_week"]
            if day not in day_of_week_stats:
                day_of_week_stats[day] = {"trades": 0, "count": 0}
            day_of_week_stats[day]["trades"] += entry["trades_executed"]
            day_of_week_stats[day]["count"] += 1

        for day in day_of_week_stats:
            day_of_week_stats[day]["avg_trades"] = round(
                day_of_week_stats[day]["trades"] / day_of_week_stats[day]["count"], 2
            )

        return {
            "user_id": user_id,
            "period_days": days,
            "daily_activity": activity,
            "summary": {
                "total_trades": total_trades,
                "avg_trades_per_day": round(avg_trades_per_day, 2),
                "most_active_day": most_active_day,
                "total_session_time_hours": round(
                    sum(a["session_duration_minutes"] for a in activity) / 60, 2
                ),
                "total_api_calls": sum(a["api_calls"] for a in activity),
            },
            "by_day_of_week": day_of_week_stats,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/admin/analytics/historical-growth")
async def get_historical_growth(
    days: int = 90, token: str = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """
    Get historical growth analytics (admin only)

    Args:
        days: Number of days of history (default: 90)

    Returns:
        Historical user growth, revenue growth, and other metrics
    """
    try:
        from datetime import timedelta
        import random

        history = []
        current_date = datetime.now()

        # Generate historical metrics
        base_users = 10
        base_revenue = 500.0

        for i in range(days, -1, -1):
            date = current_date - timedelta(days=i)

            # Simulate growth
            user_growth = random.randint(0, 3)
            base_users += user_growth
            base_revenue += random.uniform(0, 200)

            history.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "timestamp": date.isoformat(),
                    "total_users": base_users,
                    "new_users": user_growth,
                    "total_revenue": round(base_revenue, 2),
                    "active_users": random.randint(int(base_users * 0.6), base_users),
                }
            )

        return {
            "period_days": days,
            "history": history,
            "summary": {
                "starting_users": history[0]["total_users"],
                "current_users": history[-1]["total_users"],
                "total_growth": history[-1]["total_users"] - history[0]["total_users"],
                "starting_revenue": history[0]["total_revenue"],
                "current_revenue": history[-1]["total_revenue"],
                "revenue_growth": round(
                    history[-1]["total_revenue"] - history[0]["total_revenue"], 2
                ),
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting historical growth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/export/analytics-report")
async def export_analytics_report(
    user_id: str,
    format: str = "json",
    include_charts: bool = True,
    token: str = Depends(verify_token),
) -> StreamingResponse:
    """
    Export comprehensive analytics report

    Args:
        user_id: User identifier
        format: Export format (json, csv)
        include_charts: Include chart data (default: True)

    Returns:
        Downloadable analytics report
    """
    try:
        # Gather all analytics data
        from datetime import timedelta

        # Get subscription info
        subscription = subscription_manager.get_subscription(user_id)

        report_data = {
            "report_metadata": {
                "user_id": user_id,
                "generated_at": datetime.now().isoformat(),
                "report_type": "comprehensive_analytics",
                "period": "30_days",
            },
            "subscription": {
                "tier": subscription.tier.value if subscription else "unknown",
                "status": subscription.status.value if subscription else "unknown",
            },
            "portfolio_summary": {
                "current_value": 105000.00,
                "total_return": 5000.00,
                "total_return_pct": 5.0,
                "ytd_return": 12.5,
            },
            "trading_statistics": {
                "total_trades": 125,
                "win_rate": 0.68,
                "avg_profit": 285.50,
                "largest_win": 1250.00,
                "largest_loss": -450.00,
            },
        }

        if include_charts:
            # Add chart data
            import random

            chart_data = []
            for i in range(30):
                date = datetime.now() - timedelta(days=30 - i)
                chart_data.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "value": round(100000 + random.uniform(-2000, 5000), 2),
                    }
                )
            report_data["chart_data"] = {"portfolio_history": chart_data}

        if format == "csv":
            # Convert to CSV format
            output = io.StringIO()
            writer = csv.writer(output)

            # Write headers and data
            writer.writerow(["Metric", "Value"])
            writer.writerow(["User ID", report_data["report_metadata"]["user_id"]])
            writer.writerow(
                ["Generated At", report_data["report_metadata"]["generated_at"]]
            )
            writer.writerow(["Subscription Tier", report_data["subscription"]["tier"]])
            writer.writerow(
                ["Portfolio Value", report_data["portfolio_summary"]["current_value"]]
            )
            writer.writerow(
                ["Total Return", report_data["portfolio_summary"]["total_return"]]
            )
            writer.writerow(
                ["Total Trades", report_data["trading_statistics"]["total_trades"]]
            )
            writer.writerow(["Win Rate", report_data["trading_statistics"]["win_rate"]])

            output.seek(0)
            filename = (
                f"analytics_report_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv"
            )

            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )
        else:
            # Return JSON format
            filename = (
                f"analytics_report_{user_id}_{datetime.now().strftime('%Y%m%d')}.json"
            )
            json_str = json.dumps(report_data, indent=2)

            return StreamingResponse(
                iter([json_str]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )

    except Exception as e:
        logger.error(f"Error exporting analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Real-Time Market Data Endpoints
# ============================================================================

# Market data manager is initialized at the top of the file


@app.get("/api/v1/market/quote/{symbol}")
async def get_market_quote(symbol: str) -> Dict[str, Any]:
    """
    Get real-time quote for a symbol

    Args:
        symbol: Trading symbol (e.g., AAPL, GOOGL)

    Returns:
        Real-time quote data including price, volume, change

    Example:
        GET /api/v1/market/quote/AAPL
    """
    try:
        quote = market_data_manager.get_quote(symbol.upper())
        return {"status": STATUS_SUCCESS, "quote": quote}
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quote: {str(e)}")


@app.get("/api/v1/market/quotes")
async def get_multiple_quotes(symbols: str = "AAPL,GOOGL,MSFT,TSLA") -> Dict[str, Any]:
    """
    Get real-time quotes for multiple symbols

    Args:
        symbols: Comma-separated list of trading symbols

    Returns:
        Dictionary of quotes for each symbol

    Example:
        GET /api/v1/market/quotes?symbols=AAPL,GOOGL,MSFT
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        quotes = market_data_manager.get_multiple_quotes(symbol_list)

        return {
            "status": STATUS_SUCCESS,
            "quotes": quotes,
            "count": len(quotes),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error fetching multiple quotes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quotes: {str(e)}")


@app.websocket("/ws/market-data")
async def market_data_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market data streaming

    Protocol:
    - Client sends: {"action": "subscribe", "symbols": ["AAPL", "GOOGL"]}
    - Client sends: {"action": "unsubscribe", "symbols": ["AAPL"]}
    - Server sends: {"type": "update", "data": [...quotes...], "timestamp": "..."}

    Example JavaScript client:
        const ws = new WebSocket('ws://localhost:8000/ws/market-data');

        ws.onopen = () => {
            ws.send(JSON.stringify({
                action: 'subscribe',
                symbols: ['AAPL', 'GOOGL', 'MSFT']
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Market update:', data);
        };
    """
    await ws_manager.connect(websocket)

    # Start broadcasting if not already running
    await ws_manager.start_broadcasting()

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            action = message.get("action", "")
            symbols = message.get("symbols", [])

            if action == "subscribe" and symbols:
                await ws_manager.subscribe(websocket, symbols)
            elif action == "unsubscribe" and symbols:
                await ws_manager.unsubscribe(websocket, symbols)
            elif action == "ping":
                # Respond to ping with pong
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )
            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(websocket)


@app.get("/api/v1/market/history/{symbol}")
async def get_market_history(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    timeframe: str = "1day",
) -> Dict[str, Any]:
    """
    Get historical market data for a symbol

    Args:
        symbol: Trading symbol
        start_date: Start date (YYYY-MM-DD), defaults to 1 year ago
        end_date: End date (YYYY-MM-DD), defaults to today
        timeframe: Data timeframe (1min, 5min, 1hour, 1day)

    Returns:
        Historical OHLCV data

    Example:
        GET /api/v1/market/history/AAPL?start_date=2024-01-01&end_date=2024-12-31
    """
    try:
        from datetime import timedelta

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        data = market_data_manager.get_historical(symbol.upper(), start_date, end_date)

        # Convert DataFrame to list of dicts
        history = []
        for idx, row in data.iterrows():
            history.append(
                {
                    "timestamp": (
                        idx.isoformat() if hasattr(idx, "isoformat") else str(idx)
                    ),
                    "open": float(row.get("open", 0)),
                    "high": float(row.get("high", 0)),
                    "low": float(row.get("low", 0)),
                    "close": float(row.get("close", 0)),
                    "volume": int(row.get("volume", 0)),
                }
            )

        return {
            "status": STATUS_SUCCESS,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "start_date": start_date,
            "end_date": end_date,
            "data": history,
            "count": len(history),
        }
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch historical data: {str(e)}"
        )


# ============================================================================
# Real-Time Dashboard WebSocket Endpoints
# ============================================================================


@app.websocket("/ws/trade-signals")
async def trade_signals_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time trade signals streaming

    Protocol:
    - Client sends: {"action": "subscribe", "symbols": ["AAPL", "GOOGL"], "user_id": "user_001"}
    - Client sends: {"action": "unsubscribe", "symbols": ["AAPL"]}
    - Server sends: {"type": "trade_signals", "data": [...signals...], "timestamp": "..."}

    Example JavaScript client:
        const ws = new WebSocket('ws://localhost:8000/ws/trade-signals');

        ws.onopen = () => {
            ws.send(JSON.stringify({
                action: 'subscribe',
                symbols: ['AAPL', 'GOOGL', 'MSFT'],
                user_id: 'user_001'
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Trade signals update:', data);
        };
    """
    user_id = None

    try:
        # Accept connection and get initial message
        data = await websocket.receive_text()
        message = json.loads(data)
        user_id = message.get("user_id", "anonymous")

        await dashboard_ws_manager.connect(websocket, "trade_signals", user_id)

        # Start broadcasting if not already running
        await dashboard_ws_manager.start_broadcasting()

        # Handle initial subscription if symbols provided
        symbols = message.get("symbols", [])
        if symbols:
            await dashboard_ws_manager.subscribe_symbols(websocket, symbols)

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            action = message.get("action", "")
            symbols = message.get("symbols", [])

            if action == "subscribe" and symbols:
                await dashboard_ws_manager.subscribe_symbols(websocket, symbols)
            elif action == "unsubscribe" and symbols:
                await dashboard_ws_manager.unsubscribe_symbols(websocket, symbols)
            elif action == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )
            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
    except Exception as e:
        logger.error(f"Trade signals WebSocket error: {e}")
    finally:
        dashboard_ws_manager.disconnect(websocket)


@app.websocket("/ws/earnings")
async def earnings_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time earnings updates

    Protocol:
    - Client sends: {"action": "subscribe", "user_id": "user_001"}
    - Server sends: {"type": "earnings", "data": {...earnings_data...}, "timestamp": "..."}

    Example JavaScript client:
        const ws = new WebSocket('ws://localhost:8000/ws/earnings');

        ws.onopen = () => {
            ws.send(JSON.stringify({
                action: 'subscribe',
                user_id: 'user_001'
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Earnings update:', data);
        };
    """
    user_id = None

    try:
        # Accept connection and get initial message
        data = await websocket.receive_text()
        message = json.loads(data)
        user_id = message.get("user_id")

        if not user_id:
            await websocket.close(code=1008, reason="user_id required")
            return

        await dashboard_ws_manager.connect(websocket, "earnings", user_id)

        # Start broadcasting if not already running
        await dashboard_ws_manager.start_broadcasting()

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            action = message.get("action", "")

            if action == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )
            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
    except Exception as e:
        logger.error(f"Earnings WebSocket error: {e}")
    finally:
        dashboard_ws_manager.disconnect(websocket)


@app.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications

    Protocol:
    - Client sends: {"action": "subscribe", "user_id": "user_001"}
    - Server sends: {"type": "notification", "data": {...notification...}, "timestamp": "..."}

    Example JavaScript client:
        const ws = new WebSocket('ws://localhost:8000/ws/notifications');

        ws.onopen = () => {
            ws.send(JSON.stringify({
                action: 'subscribe',
                user_id: 'user_001'
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Notification:', data);
        };
    """
    user_id = None

    try:
        # Accept connection and get initial message
        data = await websocket.receive_text()
        message = json.loads(data)
        user_id = message.get("user_id")

        if not user_id:
            await websocket.close(code=1008, reason="user_id required")
            return

        await dashboard_ws_manager.connect(websocket, "notifications", user_id)

        # Start broadcasting if not already running
        await dashboard_ws_manager.start_broadcasting()

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            action = message.get("action", "")

            if action == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )
            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
    except Exception as e:
        logger.error(f"Notifications WebSocket error: {e}")
    finally:
        dashboard_ws_manager.disconnect(websocket)


@app.websocket("/ws/admin")
async def admin_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time admin dashboard updates

    Protocol:
    - Client sends: {"action": "subscribe", "admin_token": "admin-token"}
    - Server sends: {"type": "admin_users", "data": {...}, "timestamp": "..."}
    - Server sends: {"type": "admin_revenue", "data": {...}, "timestamp": "..."}

    Example JavaScript client:
        const ws = new WebSocket('ws://localhost:8000/ws/admin');

        ws.onopen = () => {
            ws.send(JSON.stringify({
                action: 'subscribe',
                admin_token: 'admin-token'
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Admin update:', data);
        };
    """
    try:
        # Accept connection and get initial message
        data = await websocket.receive_text()
        message = json.loads(data)
        admin_token = message.get("admin_token")

        # Verify admin token (basic check - enhance as needed)
        if admin_token != "admin-token":
            await websocket.close(code=1008, reason="Invalid admin token")
            return

        await dashboard_ws_manager.connect(websocket, "admin", "admin")

        # Start broadcasting if not already running
        await dashboard_ws_manager.start_broadcasting()

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            action = message.get("action", "")

            if action == "ping":
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )
            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
    except Exception as e:
        logger.error(f"Admin WebSocket error: {e}")
    finally:
        dashboard_ws_manager.disconnect(websocket)


# ============================================================================
# End of Real-Time Dashboard WebSocket Endpoints
# ============================================================================


# ============================================================================
# End of Real-Time Market Data Endpoints
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=config.api_host, port=config.api_port, workers=config.api_workers
    )
