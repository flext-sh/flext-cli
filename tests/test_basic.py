"""Basic tests for flext-cli.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_cli.config import FlextCliConfig


def test_imports() -> None:
    """Test that basic imports work."""
    config = FlextCliConfig.MainConfig()
    assert config.project_name == "flext-cli"


def test_config_creation() -> None:
    """Test that config creation works."""
    config = FlextCliConfig.MainConfig()
    # Config should be created successfully with valid attributes
    assert hasattr(config, "project_name")
    assert hasattr(config, "config_dir")
    assert config.project_name == "flext-cli"
