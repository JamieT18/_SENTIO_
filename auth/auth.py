"""
Authentication and Authorization Dependencies
Provides FastAPI dependencies for role-based access control
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .roles import UserRole, Permission, get_role_manager
from ..core.logger import get_logger

logger = get_logger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Extract and verify user from JWT token
    Returns user_id

    In production: implement proper JWT verification with user extraction
    For now, we'll use a simple format: token = "user_id:role" for demo purposes
    Or just "user_id" which defaults to USER role
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    # Simple token parsing (in production, use JWT with proper signing)
    # Expected format: "user_id" or "user_id:role"
    parts = token.split(":")
    user_id = parts[0]

    # If role is provided in token, assign it
    if len(parts) > 1:
        try:
            role = UserRole(parts[1])
            role_manager = get_role_manager()
            role_manager.assign_role(user_id, role)
        except ValueError:
            logger.warning(f"Invalid role in token: {parts[1]}")

    return user_id


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory to require specific roles

    Usage:
        @app.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
        async def admin_endpoint():
            ...
    """

    async def role_checker(user_id: str = Depends(get_current_user)) -> str:
        role_manager = get_role_manager()
        user_role = role_manager.get_user_role(user_id)

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {[r.value for r in allowed_roles]}",
            )

        return user_id

    return role_checker


def require_permission(*required_permissions: Permission):
    """
    Dependency factory to require specific permissions

    Usage:
        @app.post("/trade", dependencies=[Depends(require_permission(Permission.EXECUTE_TRADE))])
        async def execute_trade():
            ...
    """

    async def permission_checker(user_id: str = Depends(get_current_user)) -> str:
        role_manager = get_role_manager()

        for permission in required_permissions:
            if not role_manager.has_permission(user_id, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission.value}",
                )

        return user_id

    return permission_checker
