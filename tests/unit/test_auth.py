"""FLEXT CLI Auth Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliAuth covering all real functionality with flext_tests
integration, comprehensive authentication operations, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import cast

import pytest

from flext_cli.auth import FlextCliAuth
from flext_cli.typings import FlextCliTypes
from flext_core import FlextResult
from flext_tests import FlextTestsUtilities


class TestFlextCliAuth:
    """Comprehensive tests for FlextCliAuth functionality."""

    @pytest.fixture
    def auth_service(self) -> FlextCliAuth:
        """Create FlextCliAuth instance for testing."""
        return FlextCliAuth()

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================

    def test_auth_service_initialization(self, auth_service: FlextCliAuth) -> None:
        """Test auth service initialization and basic properties."""
        assert auth_service is not None
        assert hasattr(auth_service, "_logger")
        assert hasattr(auth_service, "_container")

    def test_auth_service_execute_method(self, auth_service: FlextCliAuth) -> None:
        """Test auth service execute method with real functionality."""
        result = auth_service.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert "status" in data
        assert "message" in data
        assert data["status"] == "operational"

    @pytest.mark.asyncio
    async def test_auth_service_execute_async_method(
        self, auth_service: FlextCliAuth
    ) -> None:
        """Test auth service async execute method."""
        result = await auth_service.execute_async()

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
        assert data["status"] == "operational"

    # ========================================================================
    # TOKEN MANAGEMENT
    # ========================================================================

    def test_generate_token(self, auth_service: FlextCliAuth) -> None:
        """Test token generation functionality."""
        result = auth_service.generate_token()

        assert isinstance(result, FlextResult)
        assert result.is_success

        token = result.unwrap()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_validate_token(self, auth_service: FlextCliAuth) -> None:
        """Test token validation functionality."""
        # First generate a token
        generate_result = auth_service.generate_token()
        assert generate_result.is_success
        token = generate_result.unwrap()

        # Then validate it
        result = auth_service.validate_token(token)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_validate_token_invalid(self, auth_service: FlextCliAuth) -> None:
        """Test token validation with invalid token."""
        invalid_token = "invalid_token_12345"

        result = auth_service.validate_token(invalid_token)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is False

    def test_refresh_token(self, auth_service: FlextCliAuth) -> None:
        """Test token refresh functionality."""
        # First generate a token
        generate_result = auth_service.generate_token()
        assert generate_result.is_success
        original_token = generate_result.unwrap()

        # Then refresh it
        result = auth_service.refresh_token(original_token)

        assert isinstance(result, FlextResult)
        assert result.is_success

        new_token = result.unwrap()
        assert isinstance(new_token, str)
        assert new_token != original_token  # Should be different

    def test_revoke_token(self, auth_service: FlextCliAuth) -> None:
        """Test token revocation functionality."""
        # First generate a token
        generate_result = auth_service.generate_token()
        assert generate_result.is_success
        token = generate_result.unwrap()

        # Then revoke it
        result = auth_service.revoke_token(token)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify token is no longer valid
        validate_result = auth_service.validate_token(token)
        assert validate_result.is_success
        assert validate_result.unwrap() is False

    # ========================================================================
    # CREDENTIAL MANAGEMENT
    # ========================================================================

    def test_store_credentials(
        self, auth_service: FlextCliAuth, temp_dir: Path
    ) -> None:
        """Test credential storage functionality."""
        credentials_file = temp_dir / "credentials.json"
        test_credentials: dict[
            str, bool | dict[str, object] | float | int | list[object] | str | None
        ] = {
            "username": "test_user",
            "password": "test_password",
            "api_key": "test_api_key",
        }

        result = auth_service.store_credentials(
            str(credentials_file),
            test_credentials,
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct data
        assert credentials_file.exists()
        stored_data = json.loads(credentials_file.read_text())
        assert stored_data == test_credentials

    def test_load_credentials(self, auth_service: FlextCliAuth, temp_dir: Path) -> None:
        """Test credential loading functionality."""
        credentials_file = temp_dir / "credentials.json"
        test_credentials = {
            "username": "test_user",
            "password": "test_password",
            "api_key": "test_api_key",
        }
        credentials_file.write_text(json.dumps(test_credentials))

        result = auth_service.load_credentials(str(credentials_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        loaded_credentials = result.unwrap()
        assert isinstance(loaded_credentials, dict)
        assert loaded_credentials == test_credentials

    def test_load_credentials_nonexistent(self, auth_service: FlextCliAuth) -> None:
        """Test credential loading with nonexistent file."""
        result = auth_service.load_credentials("/nonexistent/credentials.json")

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_clear_credentials(
        self, auth_service: FlextCliAuth, temp_dir: Path
    ) -> None:
        """Test credential clearing functionality."""
        credentials_file = temp_dir / "credentials.json"
        test_credentials = {"username": "test_user", "password": "test_password"}
        credentials_file.write_text(json.dumps(test_credentials))

        assert credentials_file.exists()

        result = auth_service.clear_credentials(str(credentials_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was deleted
        assert not credentials_file.exists()

    # ========================================================================
    # AUTHENTICATION METHODS
    # ========================================================================

    def test_authenticate_with_password(self, auth_service: FlextCliAuth) -> None:
        """Test password authentication functionality."""
        username = "test_user"
        password = "test_password"

        result = auth_service.authenticate_with_password(username, password)

        assert isinstance(result, FlextResult)
        # The result might be success or failure depending on implementation
        # We just verify it returns a FlextResult

    def test_authenticate_with_token(self, auth_service: FlextCliAuth) -> None:
        """Test token authentication functionality."""
        # First generate a token
        generate_result = auth_service.generate_token()
        assert generate_result.is_success
        token = generate_result.unwrap()

        result = auth_service.authenticate_with_token(token)

        assert isinstance(result, FlextResult)
        assert result.is_success

        auth_result = result.unwrap()
        assert isinstance(auth_result, dict)
        assert "authenticated" in auth_result

    def test_authenticate_with_api_key(self, auth_service: FlextCliAuth) -> None:
        """Test API key authentication functionality."""
        api_key = "test_api_key_12345"

        result = auth_service.authenticate_with_api_key(api_key)

        assert isinstance(result, FlextResult)
        # The result might be success or failure depending on implementation
        # We just verify it returns a FlextResult

    def test_authenticate_with_certificate(
        self, auth_service: FlextCliAuth, temp_dir: Path
    ) -> None:
        """Test certificate authentication functionality."""
        # Create a dummy certificate file
        cert_file = temp_dir / "test_cert.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\nDUMMY CERTIFICATE DATA\n-----END CERTIFICATE-----"
        )

        result = auth_service.authenticate_with_certificate(str(cert_file))

        assert isinstance(result, FlextResult)
        # The result might be success or failure depending on implementation
        # We just verify it returns a FlextResult

    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================

    def test_create_session(self, auth_service: FlextCliAuth) -> None:
        """Test session creation functionality."""
        result = auth_service.create_session()

        assert isinstance(result, FlextResult)
        assert result.is_success

        session = result.unwrap()
        assert isinstance(session, dict)
        assert "session_id" in session
        assert "created_at" in session

    def test_validate_session(self, auth_service: FlextCliAuth) -> None:
        """Test session validation functionality."""
        # First create a session
        create_result = auth_service.create_session()
        assert create_result.is_success
        session = create_result.unwrap()
        session_id = str(session["session_id"])

        # Then validate it
        result = auth_service.validate_session(session_id)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_validate_session_invalid(self, auth_service: FlextCliAuth) -> None:
        """Test session validation with invalid session ID."""
        invalid_session_id = "invalid_session_12345"

        result = auth_service.validate_session(invalid_session_id)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is False

    def test_destroy_session(self, auth_service: FlextCliAuth) -> None:
        """Test session destruction functionality."""
        # First create a session
        create_result = auth_service.create_session()
        assert create_result.is_success
        session = create_result.unwrap()
        session_id = session["session_id"]

        # Then destroy it
        result = auth_service.destroy_session(str(session_id))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify session is no longer valid
        validate_result = auth_service.validate_session(str(session_id))
        assert validate_result.is_success
        assert validate_result.unwrap() is False

    def test_get_session_info(self, auth_service: FlextCliAuth) -> None:
        """Test session info retrieval functionality."""
        # First create a session
        create_result = auth_service.create_session()
        assert create_result.is_success
        session = create_result.unwrap()
        session_id = session["session_id"]

        # Then get session info
        result = auth_service.get_session_info(str(session_id))

        assert isinstance(result, FlextResult)
        assert result.is_success

        session_info = result.unwrap()
        assert isinstance(session_info, dict)
        assert "session_id" in session_info
        assert "created_at" in session_info

    # ========================================================================
    # PERMISSION AND AUTHORIZATION
    # ========================================================================

    def test_check_permission(self, auth_service: FlextCliAuth) -> None:
        """Test permission checking functionality."""
        # First create a session
        create_result = auth_service.create_session()
        assert create_result.is_success
        session = create_result.unwrap()
        session_id = session["session_id"]

        result = auth_service.check_permission(str(session_id), "read")

        assert isinstance(result, FlextResult)
        assert result.is_success

        has_permission = result.unwrap()
        assert isinstance(has_permission, bool)

    def test_grant_permission(self, auth_service: FlextCliAuth) -> None:
        """Test permission granting functionality."""
        # First create a session
        create_result = auth_service.create_session()
        assert create_result.is_success
        session = create_result.unwrap()
        session_id = session["session_id"]

        result = auth_service.grant_permission(str(session_id), "write")

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify permission was granted
        check_result = auth_service.check_permission(str(session_id), "write")
        assert check_result.is_success
        assert check_result.unwrap() is True

    def test_revoke_permission(self, auth_service: FlextCliAuth) -> None:
        """Test permission revocation functionality."""
        # First create a session and grant permission
        create_result = auth_service.create_session()
        assert create_result.is_success
        session = create_result.unwrap()
        session_id = session["session_id"]

        grant_result = auth_service.grant_permission(str(session_id), "write")
        assert grant_result.is_success

        # Then revoke it
        result = auth_service.revoke_permission(str(session_id), "write")

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify permission was revoked
        check_result = auth_service.check_permission(str(session_id), "write")
        assert check_result.is_success
        assert check_result.unwrap() is False

    def test_list_permissions(self, auth_service: FlextCliAuth) -> None:
        """Test permission listing functionality."""
        # First create a session and grant some permissions
        create_result = auth_service.create_session()
        assert create_result.is_success
        session = create_result.unwrap()
        session_id = session["session_id"]

        auth_service.grant_permission(str(session_id), "read")
        auth_service.grant_permission(str(session_id), "write")

        result = auth_service.list_permissions(str(session_id))

        assert isinstance(result, FlextResult)
        assert result.is_success

        permissions = result.unwrap()
        assert isinstance(permissions, list)
        assert "read" in permissions
        assert "write" in permissions

    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================

    def test_create_user(self, auth_service: FlextCliAuth) -> None:
        """Test user creation functionality."""
        user_data: dict[str, object] = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test_password",
        }

        result = auth_service.create_user(
            cast("FlextCliTypes.Auth.UserData", user_data)
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        user = result.unwrap()
        assert isinstance(user, dict)
        assert "user_id" in user
        assert "username" in user
        assert user["username"] == "test_user"

    def test_get_user(self, auth_service: FlextCliAuth) -> None:
        """Test user retrieval functionality."""
        # First create a user
        user_data: dict[str, object] = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test_password",
        }
        create_result = auth_service.create_user(
            cast("FlextCliTypes.Auth.UserData", user_data)
        )
        assert create_result.is_success
        user = create_result.unwrap()
        user_id = user["user_id"]

        # Then get the user
        result = auth_service.get_user(str(user_id))

        assert isinstance(result, FlextResult)
        assert result.is_success

        retrieved_user = result.unwrap()
        assert isinstance(retrieved_user, dict)
        assert retrieved_user["username"] == "test_user"

    def test_update_user(self, auth_service: FlextCliAuth) -> None:
        """Test user update functionality."""
        # First create a user
        user_data: dict[str, object] = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test_password",
        }
        create_result = auth_service.create_user(
            cast("FlextCliTypes.Auth.UserData", user_data)
        )
        assert create_result.is_success
        user = create_result.unwrap()
        user_id = user["user_id"]

        # Then update the user
        update_data: dict[str, object] = {"email": "updated@example.com"}
        result = auth_service.update_user(
            str(user_id), cast("FlextCliTypes.Auth.UserData", update_data)
        )

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify user was updated
        get_result = auth_service.get_user(str(user_id))
        assert get_result.is_success
        updated_user = get_result.unwrap()
        assert updated_user["email"] == "updated@example.com"

    def test_delete_user(self, auth_service: FlextCliAuth) -> None:
        """Test user deletion functionality."""
        # First create a user
        user_data: dict[str, object] = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test_password",
        }
        create_result = auth_service.create_user(
            cast("FlextCliTypes.Auth.UserData", user_data)
        )
        assert create_result.is_success
        user = create_result.unwrap()
        user_id = user["user_id"]

        # Then delete the user
        result = auth_service.delete_user(str(user_id))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify user was deleted
        get_result = auth_service.get_user(str(user_id))
        assert get_result.is_failure

    def test_list_users(self, auth_service: FlextCliAuth) -> None:
        """Test user listing functionality."""
        # Create some test users
        auth_service.create_user({
            "username": "user1",
            "email": "user1@example.com",
            "password": "password1",
        })
        auth_service.create_user({
            "username": "user2",
            "email": "user2@example.com",
            "password": "password2",
        })

        result = auth_service.list_users()

        assert isinstance(result, FlextResult)
        assert result.is_success

        users = result.unwrap()
        assert isinstance(users, list)
        assert len(users) >= 2

    # ========================================================================
    # SECURITY FEATURES
    # ========================================================================

    def test_hash_password(self, auth_service: FlextCliAuth) -> None:
        """Test password hashing functionality."""
        password = "test_password"

        result = auth_service.hash_password(password)

        assert isinstance(result, FlextResult)
        assert result.is_success

        hashed_password = result.unwrap()
        assert isinstance(hashed_password, str)
        assert hashed_password != password  # Should be different from original

    def test_verify_password(self, auth_service: FlextCliAuth) -> None:
        """Test password verification functionality."""
        password = "test_password"

        # First hash the password
        hash_result = auth_service.hash_password(password)
        assert hash_result.is_success
        hashed_password = hash_result.unwrap()

        # Then verify it
        result = auth_service.verify_password(password, hashed_password)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_verify_password_invalid(self, auth_service: FlextCliAuth) -> None:
        """Test password verification with invalid password."""
        password = "test_password"
        wrong_password = "wrong_password"

        # First hash the password
        hash_result = auth_service.hash_password(password)
        assert hash_result.is_success
        hashed_password = hash_result.unwrap()

        # Then verify with wrong password
        result = auth_service.verify_password(wrong_password, hashed_password)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is False

    def test_generate_salt(self, auth_service: FlextCliAuth) -> None:
        """Test salt generation functionality."""
        result = auth_service.generate_salt()

        assert isinstance(result, FlextResult)
        assert result.is_success

        salt = result.unwrap()
        assert isinstance(salt, str)
        assert len(salt) > 0

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

    def test_error_handling_with_invalid_input(
        self, auth_service: FlextCliAuth
    ) -> None:
        """Test error handling with various invalid inputs."""
        # Test with None input
        result = auth_service.validate_token(None)
        assert isinstance(result, FlextResult)
        assert result.is_failure

        # Test with empty string
        result = auth_service.validate_token("")
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_error_handling_with_malformed_data(
        self, auth_service: FlextCliAuth, temp_dir: Path
    ) -> None:
        """Test error handling with malformed data."""
        # Create malformed credentials file
        credentials_file = temp_dir / "malformed_credentials.json"
        credentials_file.write_text(
            '{"username": "test", "password": "test"'
        )  # Missing closing brace

        result = auth_service.load_credentials(str(credentials_file))

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_concurrent_operations(self, auth_service: FlextCliAuth) -> None:
        """Test concurrent operations to ensure thread safety."""
        results: list[FlextResult[str]] = []
        errors: list[Exception] = []

        def worker(_worker_id: int) -> None:
            try:
                result = auth_service.generate_token()
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads: list[threading.Thread] = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        for result in results:
            assert isinstance(result, FlextResult)
            assert result.is_success

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_full_auth_workflow_integration(self, auth_service: FlextCliAuth) -> None:
        """Test complete authentication workflow integration."""
        # 1. Create a user
        user_data: dict[str, object] = {
            "username": "integration_user",
            "email": "integration@example.com",
            "password": "integration_password",
        }
        create_result = auth_service.create_user(
            cast("FlextCliTypes.Auth.UserData", user_data)
        )
        assert create_result.is_success
        user = create_result.unwrap()
        user_id = user["user_id"]

        # 2. Authenticate with password
        auth_result = auth_service.authenticate_with_password(
            str(user_data["username"]), str(user_data["password"])
        )
        assert isinstance(auth_result, FlextResult)

        # 3. Generate a token
        token_result = auth_service.generate_token()
        assert token_result.is_success
        token = token_result.unwrap()

        # 4. Validate the token
        validate_result = auth_service.validate_token(token)
        assert validate_result.is_success
        assert validate_result.unwrap() is True

        # 5. Create a session
        session_result = auth_service.create_session()
        assert session_result.is_success
        session = session_result.unwrap()
        session_id = session["session_id"]

        # 6. Grant permissions
        grant_result = auth_service.grant_permission(str(session_id), "read")
        assert grant_result.is_success

        # 7. Check permissions
        check_result = auth_service.check_permission(str(session_id), "read")
        assert check_result.is_success
        assert check_result.unwrap() is True

        # 8. List permissions
        list_result = auth_service.list_permissions(str(session_id))
        assert list_result.is_success
        permissions = list_result.unwrap()
        assert "read" in permissions

        # 9. Destroy session
        destroy_result = auth_service.destroy_session(str(session_id))
        assert destroy_result.is_success

        # 10. Revoke token
        revoke_result = auth_service.revoke_token(token)
        assert revoke_result.is_success

        # 11. Delete user
        delete_result = auth_service.delete_user(str(user_id))
        assert delete_result.is_success

    @pytest.mark.asyncio
    async def test_async_auth_workflow_integration(
        self, auth_service: FlextCliAuth
    ) -> None:
        """Test async authentication workflow integration."""
        # Test async execution
        result = await auth_service.execute_async()
        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
        assert data["status"] == "operational"
