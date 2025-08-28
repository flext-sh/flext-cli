"""Tests for providers.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextConstants, FlextResult

from flext_cli.providers import FlextCliArgsProvider, FlextConstantsProvider


class TestFlextCliArgsProvider:
    """Test FlextCliArgsProvider configuration provider."""

    def test_init_with_args(self) -> None:
        """Test provider initialization with CLI arguments."""
        args = {"debug": True, "profile": "production", "timeout": 30}
        provider = FlextCliArgsProvider(args)

        assert provider.args == args

    def test_init_empty_args(self) -> None:
        """Test provider initialization with empty arguments."""
        args: dict[str, object] = {}
        provider = FlextCliArgsProvider(args)

        assert provider.args == {}

    def test_get_config_existing_key(self) -> None:
        """Test getting existing configuration key."""
        args = {"debug": True, "timeout": 60, "profile": "development"}
        provider = FlextCliArgsProvider(args)

        result = provider.get_config("debug")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value is True

    def test_get_config_existing_key_string(self) -> None:
        """Test getting existing string configuration key."""
        args = {"profile": "production", "output_format": "json"}
        provider = FlextCliArgsProvider(args)

        result = provider.get_config("profile")

        assert result.is_success
        assert result.value == "production"

    def test_get_config_existing_key_number(self) -> None:
        """Test getting existing numeric configuration key."""
        args = {"timeout": 120, "max_retries": 5}
        provider = FlextCliArgsProvider(args)

        result = provider.get_config("timeout")

        assert result.is_success
        assert result.value == 120

    def test_get_config_missing_key_with_default(self) -> None:
        """Test getting missing key with default value."""
        args = {"debug": False}
        provider = FlextCliArgsProvider(args)

        result = provider.get_config("missing_key", "default_value")

        assert result.is_success
        assert result.value == "default_value"

    def test_get_config_missing_key_no_default(self) -> None:
        """Test getting missing key without default value."""
        args = {"existing": "value"}
        provider = FlextCliArgsProvider(args)

        result = provider.get_config("missing_key")

        assert result.is_success
        assert result.value is None

    def test_get_config_missing_key_none_default(self) -> None:
        """Test getting missing key with explicit None default."""
        args = {"key": "value"}
        provider = FlextCliArgsProvider(args)

        result = provider.get_config("missing", None)

        assert result.is_success
        assert result.value is None

    def test_get_priority(self) -> None:
        """Test getting provider priority."""
        args = {"test": "value"}
        provider = FlextCliArgsProvider(args)

        priority = provider.get_priority()

        assert priority == FlextConstants.Config.CLI_PRIORITY

    def test_get_all(self) -> None:
        """Test getting all CLI arguments."""
        args = {"debug": True, "profile": "test", "timeout": 45}
        provider = FlextCliArgsProvider(args)

        all_args = provider.get_all()

        assert all_args == args
        # Should return a copy, not the original
        assert all_args is not provider.args

    def test_get_all_empty(self) -> None:
        """Test getting all arguments when empty."""
        provider = FlextCliArgsProvider({})

        all_args = provider.get_all()

        assert all_args == {}

    def test_get_all_copy_independence(self) -> None:
        """Test that get_all returns independent copy."""
        args = {"modifiable": "value"}
        provider = FlextCliArgsProvider(args)

        copied_args = provider.get_all()
        copied_args["new_key"] = "new_value"

        # Original should be unchanged
        assert provider.args == {"modifiable": "value"}
        assert "new_key" not in provider.args


class TestFlextConstantsProvider:
    """Test FlextConstantsProvider configuration provider."""

    def test_init_with_constants(self) -> None:
        """Test provider initialization with constants."""
        constants = {"DEFAULT_TIMEOUT": 30, "DEFAULT_PROFILE": "default"}
        provider = FlextConstantsProvider(constants)

        assert provider.constants == constants

    def test_init_empty_constants(self) -> None:
        """Test provider initialization with empty constants."""
        constants: dict[str, object] = {}
        provider = FlextConstantsProvider(constants)

        assert provider.constants == {}

    def test_get_config_existing_constant(self) -> None:
        """Test getting existing constant."""
        constants = {"DEFAULT_TIMEOUT": 60, "MAX_RETRIES": 3}
        provider = FlextConstantsProvider(constants)

        result = provider.get_config("DEFAULT_TIMEOUT")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == 60

    def test_get_config_existing_string_constant(self) -> None:
        """Test getting existing string constant."""
        constants = {"APP_NAME": "FlextCLI", "VERSION": "1.0.0"}
        provider = FlextConstantsProvider(constants)

        result = provider.get_config("APP_NAME")

        assert result.is_success
        assert result.value == "FlextCLI"

    def test_get_config_existing_boolean_constant(self) -> None:
        """Test getting existing boolean constant."""
        constants = {"DEBUG_MODE": False, "PRODUCTION": True}
        provider = FlextConstantsProvider(constants)

        result = provider.get_config("DEBUG_MODE")

        assert result.is_success
        assert result.value is False

    def test_get_config_missing_constant_with_default(self) -> None:
        """Test getting missing constant with default value."""
        constants = {"EXISTING": "value"}
        provider = FlextConstantsProvider(constants)

        result = provider.get_config("MISSING", "fallback")

        assert result.is_success
        assert result.value == "fallback"

    def test_get_config_missing_constant_no_default(self) -> None:
        """Test getting missing constant without default."""
        constants = {"KEY": "value"}
        provider = FlextConstantsProvider(constants)

        result = provider.get_config("OTHER_KEY")

        assert result.is_success
        assert result.value is None

    def test_get_config_missing_constant_explicit_none(self) -> None:
        """Test getting missing constant with explicit None default."""
        constants = {"present": "here"}
        provider = FlextConstantsProvider(constants)

        result = provider.get_config("absent", None)

        assert result.is_success
        assert result.value is None

    def test_get_priority(self) -> None:
        """Test getting constants provider priority."""
        constants = {"test": "constant"}
        provider = FlextConstantsProvider(constants)

        priority = provider.get_priority()

        assert priority == FlextConstants.Config.CONSTANTS_PRIORITY

    def test_get_all(self) -> None:
        """Test getting all constants."""
        constants = {"TIMEOUT": 30, "RETRIES": 5, "DEBUG": False}
        provider = FlextConstantsProvider(constants)

        all_constants = provider.get_all()

        assert all_constants == constants
        # Should return a copy, not the original
        assert all_constants is not provider.constants

    def test_get_all_empty(self) -> None:
        """Test getting all constants when empty."""
        provider = FlextConstantsProvider({})

        all_constants = provider.get_all()

        assert all_constants == {}

    def test_get_all_copy_independence(self) -> None:
        """Test that get_all returns independent copy."""
        constants = {"ORIGINAL": "value"}
        provider = FlextConstantsProvider(constants)

        copied_constants = provider.get_all()
        copied_constants["ADDED"] = "new"

        # Original should be unchanged
        assert provider.constants == {"ORIGINAL": "value"}
        assert "ADDED" not in provider.constants


class TestProviderComparison:
    """Test comparison and integration between providers."""

    def test_priority_comparison(self) -> None:
        """Test that CLI args have higher priority than constants."""
        args_provider = FlextCliArgsProvider({})
        constants_provider = FlextConstantsProvider({})

        args_priority = args_provider.get_priority()
        constants_priority = constants_provider.get_priority()

        # CLI args should have higher priority (lower number = higher priority)
        assert args_priority < constants_priority

    def test_same_key_different_providers(self) -> None:
        """Test same key in different providers."""
        args_provider = FlextCliArgsProvider({"config_key": "from_args"})
        constants_provider = FlextConstantsProvider({"config_key": "from_constants"})

        args_result = args_provider.get_config("config_key")
        constants_result = constants_provider.get_config("config_key")

        assert args_result.value == "from_args"
        assert constants_result.value == "from_constants"

    def test_provider_type_consistency(self) -> None:
        """Test that both providers return consistent FlextResult types."""
        args_provider = FlextCliArgsProvider({"key": "value"})
        constants_provider = FlextConstantsProvider({"key": "value"})

        args_result = args_provider.get_config("key")
        constants_result = constants_provider.get_config("key")

        assert isinstance(args_result, FlextResult)
        assert isinstance(constants_result, FlextResult)
        assert args_result.is_success
        assert constants_result.is_success


class TestProvidersEdgeCases:
    """Test edge cases for configuration providers."""

    def test_args_provider_none_values(self) -> None:
        """Test args provider with None values."""
        args = {"none_value": None, "empty_string": ""}
        provider = FlextCliArgsProvider(args)

        none_result = provider.get_config("none_value")
        empty_result = provider.get_config("empty_string")

        assert none_result.is_success
        assert none_result.value is None
        assert empty_result.is_success
        assert empty_result.value == ""

    def test_constants_provider_none_values(self) -> None:
        """Test constants provider with None values."""
        constants = {"none_constant": None, "zero_value": 0}
        provider = FlextConstantsProvider(constants)

        none_result = provider.get_config("none_constant")
        zero_result = provider.get_config("zero_value")

        assert none_result.is_success
        assert none_result.value is None
        assert zero_result.is_success
        assert zero_result.value == 0

    def test_complex_data_types(self) -> None:
        """Test providers with complex data types."""
        complex_args = {
            "list_value": [1, 2, 3],
            "dict_value": {"nested": "data"},
            "tuple_value": (1, "two", 3),
        }

        args_provider = FlextCliArgsProvider(complex_args)
        constants_provider = FlextConstantsProvider(complex_args.copy())

        for key in complex_args:
            args_result = args_provider.get_config(key)
            constants_result = constants_provider.get_config(key)

            assert args_result.is_success
            assert constants_result.is_success
            assert args_result.value == complex_args[key]
            assert constants_result.value == complex_args[key]


class TestModuleExports:
    """Test module __all__ exports."""

    def test_all_exports_present(self) -> None:
        """Test that all declared exports are present."""
        from flext_cli import providers

        for export_name in providers.__all__:
            assert hasattr(providers, export_name), (
                f"Export {export_name} not found in module"
            )

    def test_expected_exports(self) -> None:
        """Test that expected classes are exported."""
        from flext_cli import providers

        expected_exports = {"FlextCliArgsProvider", "FlextConstantsProvider"}

        assert set(providers.__all__) == expected_exports

    def test_exported_classes_are_classes(self) -> None:
        """Test that exported items are actually classes."""
        from flext_cli import providers

        for export_name in providers.__all__:
            export_obj = getattr(providers, export_name)
            assert isinstance(export_obj, type), f"Export {export_name} is not a class"
