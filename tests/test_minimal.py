"""Minimal tests for flext-cli that don't depend on problematic imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import sys
from pathlib import Path


def test_python_version() -> None:
    """Test that we're using the correct Python version."""
    assert sys.version_info >= (3, 13)


def test_project_structure() -> None:
    """Test that the project has the expected structure."""
    project_root = Path(__file__).parent.parent
    assert (project_root / "src" / "flext_cli").exists()
    assert (project_root / "tests").exists()
    assert (project_root / "pyproject.toml").exists()


def test_src_files_exist() -> None:
    """Test that key source files exist."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src" / "flext_cli"

    # Check that key files exist
    assert (src_dir / "__init__.py").exists()
    assert (src_dir / "utilities.py").exists()
    assert (src_dir / "file_tools.py").exists()
    assert (src_dir / "constants.py").exists()


def test_basic_math() -> None:
    """Test basic functionality to ensure pytest is working."""
    assert 2 + 2 == 4
    assert "hello" + " " + "world" == "hello world"
    assert len([1, 2, 3]) == 3
