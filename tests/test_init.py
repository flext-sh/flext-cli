"""Comprehensive tests for flext_cli.__init__ module to achieve high coverage.

Tests the FlextCliEcosystem class and module-level compatibility functions
that provide ecosystem integration and backward compatibility.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from flext_cli import (
    FlextCliAuth,
    FlextCliEcosystem,
    get_auth_headers,
    require_auth,
    save_auth_token,
)
from flext_cli.exceptions import FlextCliError
from flext_core import FlextResult


class TestFlextCliEcosystem:
    """Tests for FlextCliEcosystem unified compatibility class."""

    def setup_method(self) -> None:
        """Set up ecosystem instance for each test."""
        self.ecosystem = FlextCliEcosystem()

    def test_init_success(self) -> None:
        """Test successful ecosystem initialization."""
        ecosystem = FlextCliEcosystem()
        assert ecosystem is not None
        assert isinstance(ecosystem, FlextCliEcosystem)
        # Initially auth service should be None (lazy loading)
        assert ecosystem._auth_service is None

    def test_auth_service_lazy_loading(self) -> None:
        """Test auth service lazy loading property."""
        # First access should create the auth service
        auth_service = self.ecosystem.auth_service
        assert auth_service is not None
        assert isinstance(auth_service, FlextCliAuth)
        assert self.ecosystem._auth_service is auth_service

        # Second access should return the same instance
        auth_service_2 = self.ecosystem.auth_service
        assert auth_service_2 is auth_service

    def test_save_auth_token_success(self) -> None:
        """Test successful auth token saving."""
        with patch.object(FlextCliAuth, 'save_auth_token') as mock_save:
            mock_save.return_value = FlextResult[None].ok(None)

            result = self.ecosystem.save_auth_token("test_token_123")

            assert result.is_success
            mock_save.assert_called_once_with("test_token_123")

    def test_save_auth_token_failure(self) -> None:
        """Test auth token saving failure."""
        with patch.object(FlextCliAuth, 'save_auth_token') as mock_save:
            mock_save.return_value = FlextResult[None].fail("Save failed")

            result = self.ecosystem.save_auth_token("invalid_token")

            assert result.is_failure
            assert "Save failed" in str(result.error)

    def test_get_auth_headers_success(self) -> None:
        """Test successful auth headers retrieval."""
        expected_headers = {"Authorization": "Bearer test_token"}
        with patch.object(FlextCliAuth, 'get_auth_headers') as mock_headers:
            mock_headers.return_value = FlextResult[dict].ok(expected_headers)

            headers = self.ecosystem.get_auth_headers()

            assert headers == expected_headers
            mock_headers.assert_called_once()

    def test_get_auth_headers_failure(self) -> None:
        """Test auth headers retrieval failure returns empty dict."""
        with patch.object(FlextCliAuth, 'get_auth_headers') as mock_headers:
            mock_headers.return_value = FlextResult[dict].fail("Headers failed")

            headers = self.ecosystem.get_auth_headers()

            assert headers == {}
            mock_headers.assert_called_once()

    def test_require_auth_decorator_authenticated(self) -> None:
        """Test require_auth decorator with authenticated user."""
        with patch.object(FlextCliAuth, 'is_authenticated') as mock_auth:
            mock_auth.return_value = True

            @self.ecosystem.require_auth()
            def test_function(value: str) -> str:
                return f"Result: {value}"

            result = test_function("test")
            assert result == "Result: test"
            mock_auth.assert_called_once()

    def test_require_auth_decorator_unauthenticated(self) -> None:
        """Test require_auth decorator with unauthenticated user."""
        with patch.object(FlextCliAuth, 'is_authenticated') as mock_auth:
            mock_auth.return_value = False

            @self.ecosystem.require_auth()
            def test_function(value: str) -> str:
                return f"Result: {value}"

            with pytest.raises(FlextCliError):
                test_function("test")
            mock_auth.assert_called_once()

    def test_require_auth_decorator_with_roles(self) -> None:
        """Test require_auth decorator with roles requirement."""
        with patch.object(FlextCliAuth, 'is_authenticated') as mock_auth:
            mock_auth.return_value = True

            @self.ecosystem.require_auth(roles=["admin", "user"])
            def test_function(value: str) -> str:
                return f"Result: {value}"

            # Should pass authentication check and execute function
            result = test_function("test")
            assert result == "Result: test"
            mock_auth.assert_called_once()

    def test_require_auth_decorator_preserves_function_signature(self) -> None:
        """Test require_auth decorator preserves original function signature."""
        with patch.object(FlextCliAuth, 'is_authenticated') as mock_auth:
            mock_auth.return_value = True

            @self.ecosystem.require_auth()
            def test_function(a: int, b: str, c: bool = True) -> dict:
                return {"a": a, "b": b, "c": c}

            result = test_function(42, "hello", c=False)
            assert result == {"a": 42, "b": "hello", "c": False}


class TestModuleLevelCompatibilityFunctions:
    """Tests for module-level compatibility functions."""

    def test_save_auth_token_module_function(self) -> None:
        """Test module-level save_auth_token function."""
        with patch('flext_cli._ecosystem.save_auth_token') as mock_save:
            mock_save.return_value = FlextResult[None].ok(None)

            result = save_auth_token("module_token_123")

            assert result.is_success
            mock_save.assert_called_once_with("module_token_123")

    def test_get_auth_headers_module_function(self) -> None:
        """Test module-level get_auth_headers function."""
        expected_headers = {"Authorization": "Bearer module_token"}
        with patch('flext_cli._ecosystem.get_auth_headers') as mock_headers:
            mock_headers.return_value = expected_headers

            headers = get_auth_headers()

            assert headers == expected_headers
            mock_headers.assert_called_once()

    def test_require_auth_module_function_no_roles(self) -> None:
        """Test module-level require_auth function without roles."""
        mock_decorator = Mock()
        with patch('flext_cli._ecosystem.require_auth') as mock_require:
            mock_require.return_value = mock_decorator

            result = require_auth()

            assert result is mock_decorator
            mock_require.assert_called_once_with(None)

    def test_require_auth_module_function_with_roles(self) -> None:
        """Test module-level require_auth function with roles."""
        mock_decorator = Mock()
        roles = ["admin", "moderator"]
        with patch('flext_cli._ecosystem.require_auth') as mock_require:
            mock_require.return_value = mock_decorator

            result = require_auth(roles=roles)

            assert result is mock_decorator
            mock_require.assert_called_once_with(roles)

    def test_require_auth_module_function_integration(self) -> None:
        """Test module-level require_auth function integration."""
        with patch.object(FlextCliAuth, 'is_authenticated') as mock_auth:
            mock_auth.return_value = True

            @require_auth(roles=["user"])
            def protected_function(data: str) -> str:
                return f"Protected: {data}"

            result = protected_function("test_data")
            assert result == "Protected: test_data"


class TestModuleImports:
    """Tests for module import functionality and exports."""

    def test_flext_cli_ecosystem_available(self) -> None:
        """Test FlextCliEcosystem is importable."""
        # Import should work without errors
        ecosystem = FlextCliEcosystem()
        assert ecosystem is not None

    def test_compatibility_functions_available(self) -> None:
        """Test all compatibility functions are importable."""
        # These imports should work without errors
        assert callable(save_auth_token)
        assert callable(get_auth_headers)
        assert callable(require_auth)

    def test_ecosystem_instance_created(self) -> None:
        """Test that the module-level ecosystem instance exists."""
        # The _ecosystem instance should be created at module level
        import flext_cli
        assert hasattr(flext_cli, '_ecosystem')
        assert isinstance(flext_cli._ecosystem, FlextCliEcosystem)


class TestErrorHandling:
    """Tests for error handling in ecosystem functions."""

    def test_ecosystem_auth_service_error_handling(self) -> None:
        """Test ecosystem handles auth service creation errors."""
        ecosystem = FlextCliEcosystem()

        # Even if auth service creation fails, property should handle gracefully
        with patch('flext_cli.FlextCliAuth') as mock_auth_class:
            mock_auth_class.side_effect = Exception("Auth creation failed")

            # Should raise the exception since we're not catching it in the property
            with pytest.raises(Exception, match="Auth creation failed"):
                _ = ecosystem.auth_service

    def test_save_auth_token_with_none_input(self) -> None:
        """Test save_auth_token handles None input gracefully."""
        with patch('flext_cli._ecosystem.save_auth_token') as mock_save:
            mock_save.return_value = FlextResult[None].fail("Token cannot be None")

            # Should pass None and let the ecosystem handle it
            result = save_auth_token(None)

            assert result.is_failure
            mock_save.assert_called_once_with(None)

    def test_require_auth_decorator_error_propagation(self) -> None:
        """Test require_auth decorator propagates function errors."""
        with patch.object(FlextCliAuth, 'is_authenticated') as mock_auth:
            mock_auth.return_value = True

            @require_auth()
            def failing_function() -> None:
                raise ValueError("Function error")

            # Should propagate the original function error
            with pytest.raises(ValueError, match="Function error"):
                failing_function()


class TestEcosystemCompatibilityPatterns:
    """Tests for ecosystem compatibility and integration patterns."""

    def test_ecosystem_singleton_pattern(self) -> None:
        """Test that module-level ecosystem acts as singleton."""
        import flext_cli

        # Multiple accesses should return the same instance
        ecosystem1 = flext_cli._ecosystem
        ecosystem2 = flext_cli._ecosystem
        assert ecosystem1 is ecosystem2

    def test_auth_service_caching(self) -> None:
        """Test that auth service is properly cached within ecosystem instance."""
        ecosystem = FlextCliEcosystem()

        # Multiple property accesses should return the same auth service
        auth1 = ecosystem.auth_service
        auth2 = ecosystem.auth_service
        assert auth1 is auth2
        assert ecosystem._auth_service is auth1

    def test_module_level_function_delegation(self) -> None:
        """Test that module-level functions properly delegate to ecosystem."""
        # All module-level functions should delegate to the _ecosystem instance
        with patch('flext_cli._ecosystem') as mock_ecosystem:
            mock_ecosystem.save_auth_token.return_value = FlextResult[None].ok(None)
            mock_ecosystem.get_auth_headers.return_value = {}
            mock_ecosystem.require_auth.return_value = lambda f: f

            # Test delegation
            save_auth_token("test")
            get_auth_headers()
            require_auth(["role"])

            # Verify calls were delegated
            mock_ecosystem.save_auth_token.assert_called_once_with("test")
            mock_ecosystem.get_auth_headers.assert_called_once()
            mock_ecosystem.require_auth.assert_called_once_with(["role"])
