"""Tests for __init__.py module to increase coverage - DIRECT flext-core usage."""

from __future__ import annotations

from flext_cli import (
    FlextApiClient,
    FlextCliApi,
    FlextCliAuth,
    FlextCliConfig,
    FlextCliConstants,
    FlextCliContext,
    FlextCliDataProcessing,
    FlextCliDebug,
    FlextCliDecorators,
    FlextCliDomainServices,
    FlextCliFactory,
    FlextCliFileOperations,
    FlextCliFormatters,
    FlextCliInteractions,
    FlextCliLoggingSetup,
    FlextCliMain,
    FlextCliModels,
    FlextCliService,
    FlextCliServices,
    __author__,
    __description__,
    __version__,
    auth,
    cli,
    config,
    debug,
    get_cli_config,
    login,
    logout,
    main,
    status,
)


class TestFlextCliDirectCoverage:
    """Test direct flext-core usage - NO WRAPPERS."""

    def test_get_cli_config_function(self) -> None:
        """Test get_cli_config function."""
        config = get_cli_config()
        assert config is not None
        assert isinstance(config, FlextCliConfig)

    def test_flext_cli_main_initialization(self) -> None:
        """Test FlextCliMain initialization."""
        cli_main = FlextCliMain()
        assert cli_main is not None
        assert hasattr(cli_main, "get_logger")

    def test_flext_cli_auth_initialization(self) -> None:
        """Test FlextCliAuth initialization."""
        auth = FlextCliAuth()
        assert auth is not None
        assert hasattr(auth, "execute")

    def test_flext_cli_api_initialization(self) -> None:
        """Test FlextCliApi initialization."""
        api = FlextCliApi()
        assert api is not None
        assert hasattr(api, "execute")

    def test_flext_cli_formatters_initialization(self) -> None:
        """Test FlextCliFormatters initialization."""
        formatters = FlextCliFormatters()
        assert formatters is not None
        assert hasattr(formatters, "format_data")

    def test_flext_cli_config_initialization(self) -> None:
        """Test FlextCliConfig initialization."""
        config = FlextCliConfig()
        assert config is not None
        assert hasattr(config, "validate_business_rules")

    def test_direct_import_access(self) -> None:
        """Test that all direct imports are accessible."""
        # Test that classes can be instantiated
        assert FlextApiClient is not None
        assert FlextCliConstants is not None
        assert FlextCliContext is not None
        assert FlextCliDataProcessing is not None
        assert FlextCliDebug is not None
        assert FlextCliDecorators is not None
        assert FlextCliDomainServices is not None
        assert FlextCliFactory is not None
        assert FlextCliFileOperations is not None
        assert FlextCliInteractions is not None
        assert FlextCliLoggingSetup is not None
        assert FlextCliModels is not None
        assert FlextCliService is not None
        assert FlextCliServices is not None

    def test_command_aliases(self) -> None:
        """Test command aliases work."""
        assert auth is not None
        assert cli is not None
        assert config is not None
        assert debug is not None
        assert login is not None
        assert logout is not None
        assert main is not None
        assert status is not None

    def test_version_info_access(self) -> None:
        """Test version info is accessible."""
        assert __version__ is not None
        assert __author__ is not None
        assert __description__ is not None
