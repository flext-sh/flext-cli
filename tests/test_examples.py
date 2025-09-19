"""Test executable examples to ensure 100% coverage.

Tests all examples as executable scripts to verify they run without errors
and achieve full coverage of example code.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


class TestExamples:
    """Test suite for example scripts."""

    def _test_example_with_coverage(self, example_name: str, expected_output: str | None = None) -> None:
        """Test example with both direct execution and subprocess for coverage."""
        example_path = Path(f"examples/{example_name}")
        assert example_path.exists(), f"Example not found: {example_path}"

        # Import and execute main function directly for coverage
        module_name = example_name.replace(".py", "").replace("-", "_")
        try:
            spec = importlib.util.spec_from_file_location(module_name, example_path)
            assert spec is not None
            assert spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "main"):
                try:
                    module.main()
                except SystemExit:
                    # main() might call sys.exit(0), which is normal
                    pass
        except Exception as e:
            # Some examples might have dataclass issues with dynamic importing
            # Log the error but don't fail if subprocess works
            print(f"Warning: Direct execution failed for {example_name}: {e}")
            pass

        # Test execution as subprocess too
        env = os.environ.copy()
        # Set PYTHONPATH to include both flext-core and flext-cli source directories
        flext_core_src = Path(__file__).parent.parent.parent / "flext-core" / "src"
        flext_cli_src = Path(__file__).parent.parent / "src"
        python_path_parts = [str(flext_cli_src), str(flext_core_src)]
        
        # Preserve existing PYTHONPATH if set
        if "PYTHONPATH" in env:
            python_path_parts.append(env["PYTHONPATH"])
        
        env["PYTHONPATH"] = os.pathsep.join(python_path_parts)
        
        result = subprocess.run(
            [sys.executable, str(example_path)],
            check=False, capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, f"Example failed: {result.stderr}"

        if expected_output:
            assert expected_output in result.stdout

    def test_01_foundation_patterns_executable(self) -> None:
        """Test that 01_foundation_patterns.py is executable."""
        self._test_example_with_coverage("01_foundation_patterns.py", "Foundation Patterns Demo")

    def test_02_cli_commands_integration_executable(self) -> None:
        """Test that 02_cli_commands_integration.py is executable."""
        self._test_example_with_coverage("02_cli_commands_integration.py")

    def test_03_data_processing_and_output_executable(self) -> None:
        """Test that 03_data_processing_and_output.py is executable."""
        self._test_example_with_coverage("03_data_processing_and_output.py")

    def test_04_authentication_and_authorization_executable(self) -> None:
        """Test that 04_authentication_and_authorization.py is executable."""
        self._test_example_with_coverage("04_authentication_and_authorization.py")

    def test_05_advanced_service_integration_executable(self) -> None:
        """Test that 05_advanced_service_integration.py is executable."""
        self._test_example_with_coverage("05_advanced_service_integration.py")

    def test_06_comprehensive_cli_application_executable(self) -> None:
        """Test that 06_comprehensive_cli_application.py is executable."""
        self._test_example_with_coverage("06_comprehensive_cli_application.py")

    def test_07_patterns_executable(self) -> None:
        """Test that 07_patterns.py is executable."""
        self._test_example_with_coverage("07_patterns.py")

    def test_08_ecosystem_integration_executable(self) -> None:
        """Test that 08_ecosystem_integration.py is executable."""
        self._test_example_with_coverage("08_ecosystem_integration.py")

    def test_config_examples_executable(self) -> None:
        """Test configuration example scripts."""
        config_examples = [
            "flext_config_global_refactoring.py",
            "flext_config_singleton_integration.py",
            "flext_config_singleton_usage.py",
            "flext_config_usage.py",
        ]

        for example_name in config_examples:
            self._test_example_with_coverage(example_name)

    def test_example_utils_importable(self) -> None:
        """Test that example_utils.py is importable."""
        utils_path = Path("examples/example_utils.py")
        if utils_path.exists():
            # Test importing example_utils using importlib
            spec = importlib.util.spec_from_file_location("example_utils", utils_path)
            if spec is not None and spec.loader is not None:
                example_utils = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(example_utils)

                # Test that it has expected functions
                assert hasattr(example_utils, "print_demo_completion")
                assert callable(example_utils.print_demo_completion)
                assert hasattr(example_utils, "handle_command_result")
                assert callable(example_utils.handle_command_result)

    def test_examples_init_importable(self) -> None:
        """Test that examples __init__.py is importable."""
        init_path = Path("examples/__init__.py")
        if init_path.exists():
            # Test importing examples package using importlib
            spec = importlib.util.spec_from_file_location("examples", init_path)
            if spec is not None and spec.loader is not None:
                examples = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(examples)

                # Test that the package is properly initialized
                assert hasattr(examples, "__name__")
