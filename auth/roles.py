"""
Role-based Access Control (RBAC) System
Defines roles, permissions, and role management
"""

from typing import Dict, Set, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from ..core.logger import get_logger

logger = get_logger(__name__)


class UserRole(str, Enum):
    """User role levels"""

    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"


class Permission(str, Enum):
    """System permissions"""

    # Trading permissions
    EXECUTE_TRADE = "execute_trade"
    VIEW_TRADES = "view_trades"
    CLOSE_POSITION = "close_position"

    # Analysis permissions
    VIEW_ANALYSIS = "view_analysis"
    ADVANCED_ANALYSIS = "advanced_analysis"

    # Strategy permissions
    VIEW_STRATEGIES = "view_strategies"
    MODIFY_STRATEGIES = "modify_strategies"

    # Dashboard permissions
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_PERFORMANCE = "view_performance"
    VIEW_TRADE_JOURNAL = "view_trade_journal"

    # Subscription permissions
    VIEW_SUBSCRIPTION = "view_subscription"
    MODIFY_SUBSCRIPTION = "modify_subscription"

    # Administrative permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_SYSTEM_STATUS = "view_system_status"
    MODIFY_SYSTEM_CONFIG = "modify_system_config"


# Role-to-permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.USER: {
        Permission.EXECUTE_TRADE,
        Permission.VIEW_TRADES,
        Permission.CLOSE_POSITION,
        Permission.VIEW_ANALYSIS,
        Permission.VIEW_STRATEGIES,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_PERFORMANCE,
        Permission.VIEW_TRADE_JOURNAL,
        Permission.VIEW_SUBSCRIPTION,
    },
    UserRole.ANALYST: {
        Permission.VIEW_TRADES,
        Permission.VIEW_ANALYSIS,
        Permission.ADVANCED_ANALYSIS,
        Permission.VIEW_STRATEGIES,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_PERFORMANCE,
        Permission.VIEW_TRADE_JOURNAL,
        Permission.VIEW_SUBSCRIPTION,
        Permission.VIEW_SYSTEM_STATUS,
    },
    UserRole.ADMIN: {
        # Admins have all permissions
        Permission.EXECUTE_TRADE,
        Permission.VIEW_TRADES,
        Permission.CLOSE_POSITION,
        Permission.VIEW_ANALYSIS,
        Permission.ADVANCED_ANALYSIS,
        Permission.VIEW_STRATEGIES,
        Permission.MODIFY_STRATEGIES,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_PERFORMANCE,
        Permission.VIEW_TRADE_JOURNAL,
        Permission.VIEW_SUBSCRIPTION,
        Permission.MODIFY_SUBSCRIPTION,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.VIEW_SYSTEM_STATUS,
        Permission.MODIFY_SYSTEM_CONFIG,
    },
}


@dataclass
class UserInfo:
    """User information with role"""

    user_id: str
    role: UserRole
    created_at: datetime
    metadata: Optional[Dict] = None


class RoleManager:
    """Manages user roles and permissions"""

    def __init__(self):
        # In-memory storage (in production, use a database)
        self._user_roles: Dict[str, UserRole] = {}
        self._user_info: Dict[str, UserInfo] = {}
        logger.info("RoleManager initialized")

    def assign_role(self, user_id: str, role: UserRole) -> None:
        """Assign a role to a user"""
        self._user_roles[user_id] = role
        if user_id not in self._user_info:
            self._user_info[user_id] = UserInfo(
                user_id=user_id, role=role, created_at=datetime.now()
            )
        else:
            self._user_info[user_id].role = role
        logger.info(f"Assigned role {role.value} to user {user_id}")

    def get_user_role(self, user_id: str) -> UserRole:
        """Get user's role (defaults to USER if not assigned)"""
        return self._user_roles.get(user_id, UserRole.USER)

    def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        """Get user information"""
        return self._user_info.get(user_id)

    def has_permission(self, user_id: str, permission: Permission, regime=None, external_context=None, diagnostics=None) -> bool:
        """Check if user has a specific permission, with regime/context/diagnostics support"""
        role = self.get_user_role(user_id)
        allowed = permission in ROLE_PERMISSIONS.get(role, set())
        # Example: restrict advanced analysis in bear regime or high error rate
        if permission == Permission.ADVANCED_ANALYSIS:
            if regime == "bear":
                return False
            if diagnostics and diagnostics.get("error_rate", 0) > 0.2:
                return False
        return allowed

    def has_role(self, user_id: str, role: UserRole) -> bool:
        """Check if user has a specific role"""
        return self.get_user_role(user_id) == role

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for a user"""
        role = self.get_user_role(user_id)
        return ROLE_PERMISSIONS.get(role, set())

    def list_users_by_role(self, role: UserRole) -> List[str]:
        """List all users with a specific role"""
        return [
            user_id
            for user_id, user_role in self._user_roles.items()
            if user_role == role
        ]

    def revoke_role(self, user_id: str) -> None:
        """Revoke user's role (resets to default USER)"""
        if user_id in self._user_roles:
            del self._user_roles[user_id]
            logger.info(f"Revoked custom role for user {user_id}")


# Global instance
_role_manager: Optional[RoleManager] = None


def get_role_manager() -> RoleManager:
    """Get or create the global RoleManager instance"""
    global _role_manager
    if _role_manager is None:
        _role_manager = RoleManager()
    return _role_manager
