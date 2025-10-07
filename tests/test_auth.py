"""
Tests for Authentication System
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from sentio.ui.api import app, auth_service
from sentio.auth import UserRole, UserCreate


# Test client
client = TestClient(app)


class TestAuthenticationEndpoints:
    """Test authentication endpoints"""

    def test_register_user(self):
        """Test user registration"""
        # Clear existing test user if exists
        if "testuser" in auth_service.users:
            del auth_service.users["testuser"]

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "role": "user",
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        user_data = {
            "username": "admin",
            "email": "admin2@example.com",
            "password": "testpassword123",
            "full_name": "Admin 2",
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_login_success(self):
        """Test successful login"""
        login_data = {"username": "admin", "password": "admin123"}

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {"username": "admin", "password": "wrongpassword"}

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        login_data = {"username": "nonexistent", "password": "password123"}

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    def test_get_current_user(self):
        """Test getting current user info"""
        # Login first
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]

        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"

    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403  # No credentials provided

    def test_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_update_user(self):
        """Test updating user information"""
        # Login
        login_response = client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Update user
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {"full_name": "Updated Admin Name"}

        response = client.put("/api/v1/auth/me", json=update_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Admin Name"

    def test_change_password(self):
        """Test changing password"""
        # Create a test user
        if "passwordtest" in auth_service.users:
            del auth_service.users["passwordtest"]

        auth_service.create_user(
            UserCreate(
                username="passwordtest",
                email="password@test.com",
                password="oldpassword123",
            )
        )

        # Login with old password
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "passwordtest", "password": "oldpassword123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Change password
        headers = {"Authorization": f"Bearer {token}"}
        password_data = {
            "current_password": "oldpassword123",
            "new_password": "newpassword456",
        }

        response = client.post(
            "/api/v1/auth/change-password", json=password_data, headers=headers
        )
        assert response.status_code == 200

        # Try login with new password
        new_login = client.post(
            "/api/v1/auth/login",
            json={"username": "passwordtest", "password": "newpassword456"},
        )
        assert new_login.status_code == 200


class TestUserManagement:
    """Test user management endpoints (admin only)"""

    def test_list_users_as_admin(self):
        """Test listing users as admin"""
        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_list_users_as_non_admin(self):
        """Test listing users as non-admin (should fail)"""
        # Create and login as regular user
        if "regularuser" in auth_service.users:
            del auth_service.users["regularuser"]

        auth_service.create_user(
            UserCreate(
                username="regularuser",
                email="regular@test.com",
                password="password123",
                role=UserRole.USER,
            )
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "regularuser", "password": "password123"},
        )
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == 403  # Forbidden

    def test_deactivate_user_as_admin(self):
        """Test deactivating user as admin"""
        # Create test user
        if "deactivatetest" in auth_service.users:
            del auth_service.users["deactivatetest"]

        auth_service.create_user(
            UserCreate(
                username="deactivatetest",
                email="deactivate@test.com",
                password="password123",
            )
        )

        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Deactivate user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/users/deactivatetest/deactivate", headers=headers
        )

        assert response.status_code == 200

        # Verify user is deactivated
        user = auth_service.get_user("deactivatetest")
        assert user.is_active is False

    def test_activate_user_as_admin(self):
        """Test activating user as admin"""
        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Activate user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/v1/users/deactivatetest/activate", headers=headers)

        assert response.status_code == 200

        # Verify user is activated
        user = auth_service.get_user("deactivatetest")
        assert user.is_active is True


class TestRoleBasedAccess:
    """Test role-based access control"""

    def test_admin_can_access_admin_endpoints(self):
        """Test admin can access admin-only endpoints"""
        login_response = client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == 200

    def test_user_cannot_access_admin_endpoints(self):
        """Test regular user cannot access admin-only endpoints"""
        # Create regular user
        if "rbactest" in auth_service.users:
            del auth_service.users["rbactest"]

        auth_service.create_user(
            UserCreate(
                username="rbactest",
                email="rbac@test.com",
                password="password123",
                role=UserRole.USER,
            )
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "rbactest", "password": "password123"},
        )
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users", headers=headers)

        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
