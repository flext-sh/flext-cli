"""REAL tests for cli_utils.py - NO MOCKING!

Tests ALL cli_utils functions with ACTUAL execution and real data processing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import yaml
from flext_core import FlextResult

from flext_cli.cli_utils import (
    cli_batch_process_files,
    cli_create_table,
    cli_format_output,
    cli_load_data_file,
    cli_quick_setup,
    cli_run_command,
    cli_save_data_file,
)


class TestCliUtilsFileOperations:
    """Test REAL file operations without mocking."""

    def test_cli_load_data_file_json_real(self) -> None:
        """Test REAL JSON file loading."""
        test_data = {
            "name": "test-project",
            "version": "1.0.0",
            "features": ["auth", "api", "cli"],
            "config": {"debug": True, "timeout": 30},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "test.json"

            # Write REAL JSON file
            json_file.write_text(json.dumps(test_data, indent=2), encoding="utf-8")

            # Test REAL loading
            result = cli_load_data_file(str(json_file))

            assert result.is_success, f"JSON loading should succeed: {result.error}"
            loaded_data = result.value
            assert loaded_data == test_data, "Loaded data should match original"

    def test_cli_load_data_file_yaml_real(self) -> None:
        """Test REAL YAML file loading."""
        test_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "users": ["REDACTED_LDAP_BIND_PASSWORD", "readonly"],
            },
            "features": {
                "auth": True,
                "logging": True,
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_file = Path(temp_dir) / "config.yaml"

            # Write REAL YAML file
            yaml_file.write_text(yaml.dump(test_data), encoding="utf-8")

            # Test REAL loading
            result = cli_load_data_file(str(yaml_file))

            assert result.is_success, f"YAML loading should succeed: {result.error}"
            loaded_data = result.value
            assert loaded_data == test_data, "YAML data should match original"

    def test_cli_load_data_file_csv_real(self) -> None:
        """Test REAL CSV file loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_file = Path(temp_dir) / "data.csv"

            # Write REAL CSV file
            csv_content = "name,age,department\nAlice,30,Engineering\nBob,25,Sales\nCarol,35,Marketing\n"
            csv_file.write_text(csv_content, encoding="utf-8")

            # Test REAL loading
            result = cli_load_data_file(str(csv_file))

            assert result.is_success, f"CSV loading should succeed: {result.error}"
            loaded_data = result.value

            assert isinstance(loaded_data, list), "CSV should load as list"
            assert len(loaded_data) == 3, "Should have 3 rows"

            # Check ACTUAL content
            assert loaded_data[0]["name"] == "Alice", "First row name should be Alice"
            assert loaded_data[1]["age"] == "25", "Second row age should be 25"
            assert loaded_data[2]["department"] == "Marketing", (
                "Third row department should be Marketing"
            )

    def test_cli_save_data_file_json_real(self) -> None:
        """Test REAL JSON file saving."""
        test_data = {
            "users": [
                {"id": 1, "name": "Alice", "roles": ["REDACTED_LDAP_BIND_PASSWORD", "user"]},
                {"id": 2, "name": "Bob", "roles": ["user"]},
            ],
            "settings": {"theme": "dark", "notifications": True},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "output.json"

            # Test REAL saving
            result = cli_save_data_file(test_data, str(json_file), "json")

            assert result.is_success, f"JSON saving should succeed: {result.error}"

            # Verify ACTUAL file was created
            assert json_file.exists(), "JSON file should exist"

            # Verify ACTUAL content
            saved_content = json.loads(json_file.read_text(encoding="utf-8"))
            assert saved_content == test_data, "Saved content should match original"

    def test_cli_save_data_file_yaml_real(self) -> None:
        """Test REAL YAML file saving."""
        test_data = {
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "workers": 4,
            },
            "database": {
                "url": "postgresql://localhost:5432/mydb",
                "pool_size": 10,
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_file = Path(temp_dir) / "config.yml"

            # Test REAL saving
            result = cli_save_data_file(test_data, str(yaml_file), "yaml")

            assert result.is_success, f"YAML saving should succeed: {result.error}"

            # Verify ACTUAL file was created
            assert yaml_file.exists(), "YAML file should exist"

            # Verify ACTUAL content by loading it back
            saved_content = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            assert saved_content == test_data, "Saved YAML should match original"

    def test_cli_save_data_file_csv_real(self) -> None:
        """Test REAL CSV file saving."""
        test_data = [
            {"product": "Widget A", "price": 19.99, "stock": 100},
            {"product": "Widget B", "price": 29.99, "stock": 50},
            {"product": "Widget C", "price": 39.99, "stock": 25},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_file = Path(temp_dir) / "products.csv"

            # Test REAL saving
            result = cli_save_data_file(test_data, str(csv_file), "csv")

            assert result.is_success, f"CSV saving should succeed: {result.error}"

            # Verify ACTUAL file was created
            assert csv_file.exists(), "CSV file should exist"

            # Verify ACTUAL content
            content = csv_file.read_text(encoding="utf-8")
            assert "Widget A" in content, "CSV should contain Widget A"
            assert "19.99" in content, "CSV should contain price 19.99"
            assert "product,price,stock" in content, "CSV should have header"


class TestCliUtilsFormatting:
    """Test REAL formatting functions without mocking."""

    def test_cli_format_output_json_real(self) -> None:
        """Test REAL JSON output formatting."""
        test_data = {
            "status": "success",
            "data": [
                {"id": 1, "status": "active"},
                {"id": 2, "status": "inactive"},
            ],
            "meta": {"total": 2, "page": 1},
        }

        # Test REAL JSON formatting
        result = cli_format_output(test_data, "json")

        assert result.is_success, f"JSON formatting should succeed: {result.error}"
        formatted = result.value

        # Should be VALID JSON
        parsed = json.loads(formatted)
        assert parsed == test_data, "JSON formatting should preserve data"

    def test_cli_format_output_yaml_real(self) -> None:
        """Test REAL YAML output formatting."""
        test_data = {
            "application": {
                "name": "flext-cli",
                "version": "0.9.0",
            },
            "dependencies": ["flext-core", "click", "rich"],
        }

        # Test REAL YAML formatting
        result = cli_format_output(test_data, "yaml")

        assert result.is_success, f"YAML formatting should succeed: {result.error}"
        formatted = result.value

        # Should be VALID YAML
        parsed = yaml.safe_load(formatted)
        assert parsed == test_data, "YAML formatting should preserve data"

    def test_cli_format_output_table_real(self) -> None:
        """Test REAL table output formatting."""
        test_data = [
            {"name": "Alice", "role": "Engineer", "experience": "5 years"},
            {"name": "Bob", "role": "Designer", "experience": "3 years"},
            {"name": "Carol", "role": "Manager", "experience": "8 years"},
        ]

        # Test REAL table formatting
        result = cli_format_output(test_data, "table")

        assert result.is_success, f"Table formatting should succeed: {result.error}"
        formatted = result.value

        assert isinstance(formatted, str), "Table should be formatted as string"
        assert "Alice" in formatted, "Table should contain Alice"
        assert "Engineer" in formatted, "Table should contain Engineer"
        assert "│" in formatted or "|" in formatted, "Should contain table borders"

    def test_cli_create_table_real(self) -> None:
        """Test REAL table creation."""
        test_data = [
            {"server": "web-01", "status": "healthy", "load": "12%"},
            {"server": "web-02", "status": "warning", "load": "87%"},
            {"server": "db-01", "status": "healthy", "load": "34%"},
        ]

        # Test REAL table creation
        result = cli_create_table(test_data, "Server Status")

        assert result.is_success, f"Table creation should succeed: {result.error}"
        table = result.value

        # Should be ACTUAL Rich table
        assert hasattr(table, "title"), "Should be Rich table with title"
        assert str(table.title) == "Server Status", "Table title should match"


class TestCliUtilsCommandExecution:
    """Test REAL command execution without mocking."""

    def test_cli_run_command_success_real(self) -> None:
        """Test REAL command execution - success case."""
        # Test REAL command that should always work
        result = cli_run_command(["echo", "Hello, World!"])

        assert result.is_success, f"Echo command should succeed: {result.error}"
        output = result.value

        assert isinstance(output, dict), "Command result should be dict"
        assert "stdout" in output, "Should have stdout"
        assert "stderr" in output, "Should have stderr"
        assert "returncode" in output, "Should have returncode"

        assert output["returncode"] == 0, "Echo should return 0"
        assert "Hello, World!" in output["stdout"], "Should contain expected output"

    def test_cli_run_command_with_args_real(self) -> None:
        """Test REAL command execution with arguments."""
        # Test REAL command with multiple arguments
        result = cli_run_command(["python", "-c", "print('test'); print(1+1)"])

        assert result.is_success, f"Python command should succeed: {result.error}"
        output = result.value

        assert output["returncode"] == 0, "Python command should succeed"
        assert "test" in output["stdout"], "Should contain 'test'"
        assert "2" in output["stdout"], "Should contain result of 1+1"

    def test_cli_run_command_failure_real(self) -> None:
        """Test REAL command execution - failure case."""
        # Test REAL command that should fail
        result = cli_run_command(["python", "-c", "raise ValueError('test error')"])

        # Command should fail but result should still be success (we got output)
        assert result.is_success, "Should get result even for failing command"
        output = result.value

        assert output["returncode"] != 0, "Should have non-zero return code"
        assert "ValueError" in output["stderr"], "Should contain error in stderr"


class TestCliUtilsBatchProcessing:
    """Test REAL batch processing without mocking."""

    def test_cli_batch_process_files_real(self) -> None:
        """Test REAL batch file processing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create REAL test files
            files_data = {
                "file1.txt": "Hello from file 1\nLine 2",
                "file2.txt": "Hello from file 2\nAnother line",
                "file3.txt": "Hello from file 3\nFinal line",
            }

            file_paths = []
            for filename, content in files_data.items():
                file_path = temp_path / filename
                file_path.write_text(content, encoding="utf-8")
                file_paths.append(str(file_path))

            # Define REAL processing function (must return FlextResult)
            def count_lines(file_path: Path) -> FlextResult[dict[str, object]]:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    lines = content.split("\n")
                    return FlextResult.ok(
                        {
                            "file": file_path.name,
                            "lines": len(lines),
                            "chars": len(content),
                        }
                    )
                except Exception as e:
                    return FlextResult.fail(f"Error processing {file_path}: {e}")

            # Test REAL batch processing (convert strings to Path objects)
            path_objects = [Path(p) for p in file_paths]
            result = cli_batch_process_files(path_objects, count_lines)

            assert result.is_success, f"Batch processing should succeed: {result.error}"
            results = result.value

            assert isinstance(results, dict), "Results should be dict with summary"
            assert "successful" in results, "Should have successful results"
            assert "processed" in results, "Should have processed count"

            # Check ACTUAL processing results - successful contains file paths, not detailed results
            successful_results = results["successful"]
            assert len(successful_results) == 3, (
                "Should process all 3 files successfully"
            )

            # Verify file paths are in the successful list
            for file_path in path_objects:
                assert str(file_path) in successful_results, (
                    f"File {file_path} should be in successful results"
                )

            # Verify no errors occurred
            assert results["failed"] == 0, "Should have no failed files"
            assert len(results["errors"]) == 0, "Should have no error list"
            assert results["processed"] == 3, "Should have processed count of 3"

    def test_cli_quick_setup_real(self) -> None:
        """Test REAL quick setup functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp dir for the setup to work properly
            import os

            original_cwd = Path.cwd()
            try:
                os.chdir(temp_dir)

                # Test REAL project setup (check correct signature)
                result = cli_quick_setup("test-project")

                assert result.is_success, f"Quick setup should succeed: {result.error}"
                setup_info = result.value

                assert isinstance(setup_info, dict), "Setup result should be dict"
                assert "project_path" in setup_info, "Should have project path"
                # Fix: Check for actual keys returned by the function
                assert "config_file" in setup_info, "Should have config file info"
                assert "dir_src" in setup_info, "Should have src directory"

                # Verify ACTUAL files were created
                project_path = Path(setup_info["project_path"])
                assert project_path.exists(), "Project directory should exist"

                # Check for expected files
                pyproject_file = Path(setup_info["config_file"])
                assert pyproject_file.exists(), "pyproject.toml should exist"
                content = pyproject_file.read_text(encoding="utf-8")
                assert "test-project" in content, (
                    "pyproject.toml should contain project name"
                )
            finally:
                os.chdir(original_cwd)


class TestCliUtilsErrorHandling:
    """Test REAL error handling without mocking."""

    def test_load_nonexistent_file_real(self) -> None:
        """Test REAL error handling for nonexistent files."""
        # Test loading ACTUALLY nonexistent file
        result = cli_load_data_file("/nonexistent/path/file.json")

        assert not result.is_success, "Should fail for nonexistent file"
        assert result.error is not None, "Should have error message"
        assert "not" in result.error.lower() or "exist" in result.error.lower(), (
            "Error should mention file doesn't exist"
        )

    def test_save_to_invalid_path_real(self) -> None:
        """Test REAL error handling for invalid save paths."""
        test_data = {"test": "data"}

        # Test saving to ACTUALLY invalid path
        result = cli_save_data_file(test_data, "/root/forbidden/file.json", "json")

        assert not result.is_success, "Should fail for invalid path"
        assert result.error is not None, "Should have error message"

    def test_format_invalid_data_real(self) -> None:
        """Test REAL error handling for invalid format types."""
        test_data = {"test": "data"}

        # Test REAL invalid format
        result = cli_format_output(test_data, "invalid_format")

        assert not result.is_success, "Should fail for invalid format"
        assert result.error is not None, "Should have error message"
        assert "format" in result.error.lower(), "Error should mention format"


class TestCliUtilsDataTypes:
    """Test REAL data type handling without mocking."""

    def test_complex_data_structures_real(self) -> None:
        """Test REAL handling of complex data structures."""
        complex_data = {
            "metadata": {
                "created": "2025-01-15T10:00:00Z",
                "version": "1.0",
                "tags": ["production", "api", "v1"],
            },
            "data": [
                {
                    "id": "item-1",
                    "attributes": {
                        "name": "First Item",
                        "values": [1, 2, 3, 4, 5],
                        "enabled": True,
                    },
                },
                {
                    "id": "item-2",
                    "attributes": {
                        "name": "Second Item",
                        "values": [10, 20, 30],
                        "enabled": False,
                    },
                },
            ],
            "summary": {
                "total_items": 2,
                "active_items": 1,
                "categories": {"type_a": 1, "type_b": 1},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test JSON round-trip
            json_file = Path(temp_dir) / "complex.json"

            save_result = cli_save_data_file(complex_data, str(json_file), "json")
            assert save_result.is_success, "Should save complex data as JSON"

            load_result = cli_load_data_file(str(json_file))
            assert load_result.is_success, "Should load complex data from JSON"

            loaded_data = load_result.value
            assert loaded_data == complex_data, (
                "Complex data should round-trip correctly"
            )

            # Test YAML round-trip
            yaml_file = Path(temp_dir) / "complex.yaml"

            save_yaml_result = cli_save_data_file(complex_data, str(yaml_file), "yaml")
            assert save_yaml_result.is_success, "Should save complex data as YAML"

            load_yaml_result = cli_load_data_file(str(yaml_file))
            assert load_yaml_result.is_success, "Should load complex data from YAML"

            loaded_yaml_data = load_yaml_result.value
            assert loaded_yaml_data == complex_data, (
                "Complex YAML data should round-trip correctly"
            )

    def test_unicode_and_special_chars_real(self) -> None:
        """Test REAL handling of Unicode and special characters."""
        unicode_data = {
            "english": "Hello World",
            "spanish": "Hola Mundo",
            "chinese": "你好世界",
            "emoji": "🎉🚀💯",
            "special": "Special chars: !@#$%^&*()_+-={}[]|\\:;\"'<>,.?/",
            "quotes": "Both \"double\" and 'single' quotes",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test Unicode in JSON
            json_file = Path(temp_dir) / "unicode.json"

            save_result = cli_save_data_file(unicode_data, str(json_file), "json")
            assert save_result.is_success, "Should save Unicode data as JSON"

            load_result = cli_load_data_file(str(json_file))
            assert load_result.is_success, "Should load Unicode data from JSON"

            loaded_data = load_result.value
            assert loaded_data == unicode_data, "Unicode data should be preserved"

            # Verify ACTUAL file content contains Unicode
            file_content = json_file.read_text(encoding="utf-8")
            assert "你好世界" in file_content, "File should contain Chinese characters"
            assert "🎉" in file_content, "File should contain emoji"
