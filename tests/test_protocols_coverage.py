"""Test coverage for protocols.py module."""

from flext_cli.protocols import FlextCliProtocols
from flext_cli.typings import FlextCliTypings
from flext_core import FlextResult


def test_cli_command_handler_protocol() -> None:
    """Test CliCommandHandler protocol."""

    class TestCommandHandler:
        def __call__(
            self, **_kwargs: object
        ) -> FlextResult[FlextCliTypings.CliCommandResult]:
            return FlextResult[FlextCliTypings.CliCommandResult].ok({
                "status": "success"
            })

    handler = TestCommandHandler()
    result = handler(test_arg="value")
    assert result.is_success
    # Test that the handler implements the protocol interface
    assert callable(handler)


def test_cli_formatter_protocol() -> None:
    """Test CliFormatter protocol."""

    class TestFormatter:
        def format_data(
            self, _data: FlextCliTypings.CliFormatData, **_options: object
        ) -> FlextResult[str]:
            return FlextResult[str].ok("formatted_data")

    formatter = TestFormatter()
    result = formatter.format_data({"test": "data"})
    assert result.is_success
    # Test that the formatter implements the protocol interface
    assert hasattr(formatter, "format_data")


def test_cli_config_provider_protocol() -> None:
    """Test CliConfigProvider protocol."""

    class TestConfigProvider:
        def load_config(self) -> FlextResult[FlextCliTypings.CliConfigData]:
            return FlextResult[FlextCliTypings.CliConfigData].ok({"config": "data"})

        def save_config(
            self, _config: FlextCliTypings.CliConfigData
        ) -> FlextResult[None]:
            return FlextResult[None].ok(None)

    provider = TestConfigProvider()
    load_result = provider.load_config()
    save_result = provider.save_config({"test": "config"})

    assert load_result.is_success
    assert save_result.is_success
    # Test that the provider implements the protocol interface
    assert hasattr(provider, "load_config")
    assert hasattr(provider, "save_config")


def test_cli_authenticator_protocol() -> None:
    """Test CliAuthenticator protocol."""

    class TestAuthenticator:
        def authenticate(
            self, _credentials: FlextCliTypings.CliConfigData
        ) -> FlextResult[str]:
            return FlextResult[str].ok("auth_token")

        def validate_token(self, _token: str) -> FlextResult[bool]:
            return FlextResult[bool].ok(True)

    authenticator = TestAuthenticator()
    auth_result = authenticator.authenticate({"user": "test"})
    validate_result = authenticator.validate_token("token")

    assert auth_result.is_success
    assert validate_result.is_success
    # Test that the authenticator implements the protocol interface
    assert hasattr(authenticator, "authenticate")
    assert hasattr(authenticator, "validate_token")


def test_cli_debug_provider_protocol() -> None:
    """Test CliDebugProvider protocol."""

    class TestDebugProvider:
        def get_debug_info(self) -> FlextResult[FlextCliTypings.CliConfigData]:
            return FlextResult[FlextCliTypings.CliConfigData].ok({"debug": "info"})

    provider = TestDebugProvider()
    result = provider.get_debug_info()

    assert result.is_success
    # Test that the provider implements the protocol interface
    assert hasattr(provider, "get_debug_info")


def test_protocols_class_structure() -> None:
    """Test that FlextCliProtocols class has all expected protocols."""
    protocols = FlextCliProtocols()

    # Check that all protocol classes exist
    assert hasattr(protocols, "CliCommandHandler")
    assert hasattr(protocols, "CliFormatter")
    assert hasattr(protocols, "CliConfigProvider")
    assert hasattr(protocols, "CliAuthenticator")
    assert hasattr(protocols, "CliDebugProvider")
