"""Test utilities for flext-cli tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult


class FlextTestsMatchers:
    """Simple test matchers for flext-cli tests."""

    def assert_result_success(self, result: FlextResult) -> None:
        """Assert that a FlextResult is successful."""
        assert result.is_success, f"Expected success but got failure: {result.error}"

    def assert_result_failure(self, result: FlextResult) -> None:
        """Assert that a FlextResult is a failure."""
        assert result.is_failure, f"Expected failure but got success: {result.value}"


class FlextTestsDomains:
    """Simple test domains for flext-cli tests."""

    def get_auth_domain(self) -> dict[str, object]:
        """Get auth domain test data."""
        return {
            "domain": "auth",
            "operations": ["login", "logout", "status", "token"],
        }

    def create_user(
        self,
        username: str = "testuser",
        email: str = "test@example.com",
        role: str = "user",
    ) -> dict[str, object]:
        """Create test user data."""
        return {
            "username": username,
            "email": email,
            "role": role,
            "id": "test_user_id_123",
        }


class FlextTestsBuilders:
    """Simple test builders for flext-cli tests."""

    def build_auth_token(self, token_type: str = "valid") -> str:
        """Build an auth token for testing."""
        tokens = {
            "valid": "test_auth_token_12345",
            "special_chars": "token_with_!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/",
            "long": "x" * 1000,
            "empty": "",
        }
        return tokens.get(token_type, tokens["valid"])

    def success_result(self, data: object) -> FlextResult[object]:
        """Build a successful FlextResult for testing."""
        return FlextResult[object].ok(data)

    def failure_result(self, error: str) -> FlextResult[object]:
        """Build a failed FlextResult for testing."""
        return FlextResult[object].fail(error)
