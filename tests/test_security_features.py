"""
Tests for Enhanced Security Features
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import time

from sentio.ui.api import app, auth_service
from sentio.auth import UserRole, UserCreate


# Test client
client = TestClient(app)


class TestRefreshTokens:
    """Test refresh token functionality"""

    def test_login_with_refresh_token(self):
        """Test login and receive both access and refresh tokens"""
        login_data = {"username": "admin", "password": "admin123"}

        response = client.post("/api/v1/auth/login-with-refresh", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_refresh_access_token(self):
        """Test refreshing access token using refresh token"""
        # Login to get refresh token
        login_response = client.post(
            "/api/v1/auth/login-with-refresh",
            json={"username": "admin", "password": "admin123"},
        )
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token to get new access token
        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_with_invalid_token(self):
        """Test refreshing with invalid token fails"""
        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid_token"}
        )

        assert response.status_code == 401
        assert "Invalid or expired" in response.json()["detail"]

    def test_revoke_refresh_token(self):
        """Test revoking a refresh token"""
        # Login to get tokens
        login_response = client.post(
            "/api/v1/auth/login-with-refresh",
            json={"username": "admin", "password": "admin123"},
        )
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]

        # Revoke refresh token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post(
            "/api/v1/auth/revoke-refresh-token",
            json={"refresh_token": refresh_token},
            headers=headers,
        )

        assert response.status_code == 200
        assert "revoked successfully" in response.json()["message"]

        # Try to use revoked token - should fail
        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert response.status_code == 401


class TestMultiFactorAuthentication:
    """Test MFA functionality"""

    def test_mfa_enrollment(self):
        """Test enrolling in MFA"""
        # Create test user
        if "mfatest" in auth_service.users:
            del auth_service.users["mfatest"]

        client.post(
            "/api/v1/auth/register",
            json={
                "username": "mfatest",
                "email": "mfa@test.com",
                "password": "testpassword123",
            },
        )

        # Login to get token
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "mfatest", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Enroll in MFA
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/v1/auth/mfa/enroll", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "secret" in data
        assert "qr_code_url" in data
        assert data["qr_code_url"].startswith("data:image/png;base64,")

    def test_mfa_verification_and_enable(self):
        """Test verifying MFA token and enabling MFA"""
        # Enroll in MFA first
        if "mfaverify" in auth_service.users:
            del auth_service.users["mfaverify"]

        client.post(
            "/api/v1/auth/register",
            json={
                "username": "mfaverify",
                "email": "mfaverify@test.com",
                "password": "testpassword123",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "mfaverify", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        enroll_response = client.post("/api/v1/auth/mfa/enroll", headers=headers)
        secret = enroll_response.json()["secret"]

        # Generate valid TOTP token
        import pyotp

        totp = pyotp.TOTP(secret)
        mfa_token = totp.now()

        # Verify and enable MFA
        response = client.post(
            "/api/v1/auth/mfa/verify", json={"token": mfa_token}, headers=headers
        )

        assert response.status_code == 200
        assert "enabled successfully" in response.json()["message"]

    def test_mfa_login(self):
        """Test login with MFA"""
        # Create user with MFA enabled
        if "mfalogin" in auth_service.users:
            del auth_service.users["mfalogin"]

        user = auth_service.create_user(
            UserCreate(
                username="mfalogin",
                email="mfalogin@test.com",
                password="testpassword123",
            )
        )

        # Enable MFA manually
        secret, _ = auth_service.enable_mfa("mfalogin")
        import pyotp

        totp = pyotp.TOTP(secret)
        mfa_token = totp.now()
        auth_service.verify_and_enable_mfa("mfalogin", mfa_token)

        # Try regular login - should fail
        response = client.post(
            "/api/v1/auth/login-with-refresh",
            json={"username": "mfalogin", "password": "testpassword123"},
        )
        assert response.status_code == 403
        assert "MFA verification required" in response.json()["detail"]

        # Login with MFA
        mfa_token = totp.now()
        response = client.post(
            "/api/v1/auth/login-mfa",
            json={
                "username": "mfalogin",
                "password": "testpassword123",
                "mfa_token": mfa_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_disable_mfa(self):
        """Test disabling MFA"""
        # Create user with MFA
        if "mfadisable" in auth_service.users:
            del auth_service.users["mfadisable"]

        user = auth_service.create_user(
            UserCreate(
                username="mfadisable",
                email="mfadisable@test.com",
                password="testpassword123",
            )
        )

        secret, _ = auth_service.enable_mfa("mfadisable")
        import pyotp

        totp = pyotp.TOTP(secret)
        mfa_token = totp.now()
        auth_service.verify_and_enable_mfa("mfadisable", mfa_token)

        # Login with MFA
        mfa_token = totp.now()
        login_response = client.post(
            "/api/v1/auth/login-mfa",
            json={
                "username": "mfadisable",
                "password": "testpassword123",
                "mfa_token": mfa_token,
            },
        )
        token = login_response.json()["access_token"]

        # Disable MFA
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/auth/mfa/disable",
            json={
                "current_password": "testpassword123",
                "new_password": "testpassword123",  # Not changing password
            },
            headers=headers,
        )

        assert response.status_code == 200
        assert "disabled successfully" in response.json()["message"]


class TestSessionManagement:
    """Test session management functionality"""

    def test_get_user_sessions(self):
        """Test getting user sessions"""
        # Create test user and session
        if "sessiontest" in auth_service.users:
            del auth_service.users["sessiontest"]

        client.post(
            "/api/v1/auth/register",
            json={
                "username": "sessiontest",
                "email": "session@test.com",
                "password": "testpassword123",
            },
        )

        # Login to create session
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "sessiontest", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Manually create a session
        session_id = auth_service.create_session(
            "sessiontest", "127.0.0.1", "test-agent"
        )

        # Get sessions
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/sessions", headers=headers)

        assert response.status_code == 200
        sessions = response.json()
        assert isinstance(sessions, list)
        assert len(sessions) >= 1

    def test_revoke_session(self):
        """Test revoking a specific session"""
        # Create session
        if "revoketest" in auth_service.users:
            del auth_service.users["revoketest"]

        client.post(
            "/api/v1/auth/register",
            json={
                "username": "revoketest",
                "email": "revoke@test.com",
                "password": "testpassword123",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "revoketest", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        session_id = auth_service.create_session("revoketest")

        # Revoke session
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/api/v1/auth/sessions/{session_id}", headers=headers)

        assert response.status_code == 200
        assert "revoked successfully" in response.json()["message"]

    def test_revoke_all_sessions(self):
        """Test revoking all user sessions"""
        # Create multiple sessions
        if "revokeall" in auth_service.users:
            del auth_service.users["revokeall"]

        client.post(
            "/api/v1/auth/register",
            json={
                "username": "revokeall",
                "email": "revokeall@test.com",
                "password": "testpassword123",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "revokeall", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Create multiple sessions
        auth_service.create_session("revokeall")
        auth_service.create_session("revokeall")
        auth_service.create_session("revokeall")

        # Revoke all sessions
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete("/api/v1/auth/sessions", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] >= 3


class TestPasswordReset:
    """Test password reset functionality"""

    def test_request_password_reset(self):
        """Test requesting password reset"""
        response = client.post(
            "/api/v1/auth/password-reset/request", json={"email": "admin@sentio.com"}
        )

        assert response.status_code == 200
        assert "password reset link" in response.json()["message"].lower()

    def test_request_password_reset_invalid_email(self):
        """Test password reset with invalid email still returns success"""
        # Should not reveal if email exists
        response = client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "nonexistent@example.com"},
        )

        assert response.status_code == 200
        assert "password reset link" in response.json()["message"].lower()

    def test_confirm_password_reset(self):
        """Test confirming password reset"""
        # Request reset
        token = auth_service.request_password_reset("admin@sentio.com")
        assert token is not None

        # Confirm reset with valid token
        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": token, "new_password": "newpassword123"},
        )

        assert response.status_code == 200
        assert "reset successfully" in response.json()["message"]

        # Verify can login with new password
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "newpassword123"},
        )
        assert login_response.status_code == 200

        # Reset password back
        token = auth_service.request_password_reset("admin@sentio.com")
        auth_service.reset_password(token, "admin123")

    def test_confirm_password_reset_invalid_token(self):
        """Test password reset with invalid token fails"""
        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": "invalid_token", "new_password": "newpassword123"},
        )

        assert response.status_code == 400
        assert "Invalid or expired" in response.json()["detail"]


class TestAuditLogging:
    """Test audit logging functionality"""

    def test_get_user_audit_logs(self):
        """Test getting audit logs for current user"""
        # Login
        login_response = client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Get audit logs
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/audit-logs", headers=headers)

        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
        assert len(logs) > 0

        # Check log structure
        log = logs[0]
        assert "id" in log
        assert "action" in log
        assert "timestamp" in log

    def test_get_all_audit_logs_admin(self):
        """Test admin getting all audit logs"""
        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Get all audit logs
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/audit-logs/all", headers=headers)

        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)

    def test_audit_log_filters(self):
        """Test filtering audit logs"""
        # Login as admin
        login_response = client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Get audit logs with action filter
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(
            "/api/v1/auth/audit-logs/all?action=login_success&limit=10", headers=headers
        )

        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)


class TestOAuth2Integration:
    """Test OAuth2 integration"""

    def test_oauth_login_initiation_google(self):
        """Test initiating OAuth2 login with Google"""
        response = client.get("/api/v1/auth/oauth/google/login")

        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "accounts.google.com" in data["authorization_url"]

    def test_oauth_login_initiation_github(self):
        """Test initiating OAuth2 login with GitHub"""
        response = client.get("/api/v1/auth/oauth/github/login")

        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "github.com" in data["authorization_url"]

    def test_oauth_callback_not_implemented(self):
        """Test OAuth2 callback returns not implemented (needs config)"""
        response = client.post(
            "/api/v1/auth/oauth/callback",
            json={
                "provider": "google",
                "code": "test_code",
                "redirect_uri": "http://localhost:8000/callback",
            },
        )

        assert response.status_code == 501
        assert "implementation requires" in response.json()["detail"].lower()


class TestSecurityIntegration:
    """Integration tests for security features"""

    def test_password_reset_revokes_sessions(self):
        """Test that password reset revokes all sessions"""
        # Create user with sessions
        if "resettest" in auth_service.users:
            del auth_service.users["resettest"]

        user = auth_service.create_user(
            UserCreate(
                username="resettest",
                email="resettest@test.com",
                password="oldpassword123",
            )
        )

        # Create sessions
        session1 = auth_service.create_session("resettest")
        session2 = auth_service.create_session("resettest")

        # Request password reset
        token = auth_service.request_password_reset("resettest@test.com")
        auth_service.reset_password(token, "newpassword123")

        # Check sessions are revoked
        sessions = auth_service.get_user_sessions("resettest")
        active_sessions = [s for s in sessions if s.is_active]
        assert len(active_sessions) == 0

    def test_failed_login_audit_log(self):
        """Test that failed login attempts are logged"""
        # Attempt failed login
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
        )
        assert response.status_code == 401

        # Check audit logs
        logs = auth_service.get_audit_logs(user_id="admin", action="login_failed")
        assert len(logs) > 0
        assert not logs[0].success
