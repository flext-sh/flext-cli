"""Core API functionality tests."""

import csv
import json

from flext_cli.api import CliApi


class TestCliApiCore:
    """Test core CliApi functionality."""

    def test_init(self, mock_flext_core) -> None:
        """Test CliApi initialization."""
        api = CliApi()

        assert api._formats == {"json", "csv", "yaml", "table"}
        assert api._commands == {}
        assert "INFO: CliApi initialized" in mock_flext_core["logger"].messages

    def test_supported_formats(self, mock_flext_core) -> None:
        """Test supported formats are correct."""
        api = CliApi()

        expected_formats = {"json", "csv", "yaml", "table"}
        assert api._formats == expected_formats

    def test_health_check_success(self, mock_flext_core) -> None:
        """Test successful health check."""
        api = CliApi()

        result = api.health()

        assert result.is_success
        assert result.data["status"] == "healthy"
        assert result.data["commands"] == 0
        assert result.data["version"] == "2.0.0"
        assert set(result.data["formats"]) == {"json", "csv", "yaml", "table"}

    def test_health_check_data_structure(self, mock_flext_core) -> None:
        """Test health check returns expected data structure."""
        api = CliApi()

        result = api.health()
        health_data = result.data

        required_keys = {"status", "commands", "formats", "version"}
        assert set(health_data.keys()) == required_keys
        assert isinstance(health_data["formats"], list)
        assert isinstance(health_data["commands"], int)


class TestCliApiExport:
    """Test export functionality."""

    def test_export_json_success(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test successful JSON export."""
        api = CliApi()
        filepath = temp_dir / "test.json"

        result = api.export(sample_data, str(filepath), "json")

        assert result.is_success
        assert "Exported 3 records to" in result.data
        assert filepath.exists()

        # Verify file content
        with filepath.open() as f:
            data = json.load(f)
        assert data == sample_data

    def test_export_csv_success(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test successful CSV export."""
        api = CliApi()
        filepath = temp_dir / "test.csv"

        result = api.export(sample_data, str(filepath), "csv")

        assert result.is_success
        assert filepath.exists()

        # Verify file content
        with filepath.open() as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)

        # Convert back to original types for comparison
        for row in csv_data:
            row["id"] = int(row["id"])
            row["age"] = int(row["age"])

        assert csv_data == sample_data

    def test_export_no_data_fails(self, mock_flext_core, temp_dir) -> None:
        """Test export fails with no data."""
        api = CliApi()
        filepath = temp_dir / "test.json"

        result = api.export(None, str(filepath), "json")

        assert not result.is_success
        assert "No data provided" in result.error

    def test_export_empty_list_fails(self, mock_flext_core, temp_dir) -> None:
        """Test export fails with empty list."""
        api = CliApi()
        filepath = temp_dir / "test.json"

        result = api.export([], str(filepath), "json")

        assert not result.is_success
        assert "No data provided" in result.error

    def test_export_csv_invalid_data_fails(self, mock_flext_core, temp_dir) -> None:
        """Test CSV export fails with invalid data structure."""
        api = CliApi()
        filepath = temp_dir / "test.csv"

        # Test with non-dict list
        result = api.export(["string1", "string2"], str(filepath), "csv")
        assert not result.is_success
        assert "CSV requires list of dictionaries" in result.error

    def test_export_unsupported_format_fails(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test export fails with unsupported format."""
        api = CliApi()
        filepath = temp_dir / "test.xyz"

        result = api.export(sample_data, str(filepath), "xyz")

        assert not result.is_success
        assert "Unsupported format: xyz" in result.error

    def test_export_creates_parent_directories(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test export creates parent directories."""
        api = CliApi()
        filepath = temp_dir / "subdir" / "nested" / "test.json"

        result = api.export(sample_data, str(filepath), "json")

        assert result.is_success
        assert filepath.exists()
        assert filepath.parent.exists()

    def test_export_single_dict_to_list(self, mock_flext_core, single_record, temp_dir) -> None:
        """Test export converts single dict to list format."""
        api = CliApi()
        filepath = temp_dir / "single.json"

        result = api.export(single_record, str(filepath), "json")

        assert result.is_success

        with filepath.open() as f:
            data = json.load(f)
        assert data == single_record  # Should preserve original structure


class TestCliApiFomatting:
    """Test formatting functionality."""

    def test_format_json_success(self, mock_flext_core, sample_data) -> None:
        """Test successful JSON formatting."""
        api = CliApi()

        result = api.format_data(sample_data, "json")

        assert result.is_success
        # Verify it's valid JSON
        parsed = json.loads(result.data)
        assert parsed == sample_data

    def test_format_table_success(self, mock_flext_core, sample_data) -> None:
        """Test successful table formatting."""
        api = CliApi()

        result = api.format_data(sample_data, "table")

        assert result.is_success
        output = result.data

        # Check table structure
        lines = output.split("\n")
        assert len(lines) >= 5  # Header + separator + 3 data rows
        assert "id" in lines[0]  # Header contains column names
        assert "Alice" in output  # Data is present

    def test_format_table_single_dict(self, mock_flext_core, single_record) -> None:
        """Test table formatting with single dictionary."""
        api = CliApi()

        result = api.format_data(single_record, "table")

        assert result.is_success
        output = result.data

        lines = output.split("\n")
        assert "id" in lines[0]
        assert "Test User" in output

    def test_format_unsupported_style_fails(self, mock_flext_core, sample_data) -> None:
        """Test formatting fails with unsupported style."""
        api = CliApi()

        result = api.format_data(sample_data, "xml")

        assert not result.is_success
        assert "Unsupported style: xml" in result.error

    def test_format_table_with_non_dict_data(self, mock_flext_core) -> None:
        """Test table formatting with non-dict data falls back to JSON."""
        api = CliApi()
        simple_data = ["item1", "item2", "item3"]

        result = api.format_data(simple_data, "table")

        assert result.is_success
        # Should fall back to JSON format
        parsed = json.loads(result.data)
        assert parsed == simple_data


class TestCliApiCommands:
    """Test command functionality."""

    def test_add_command_success(self, mock_flext_core) -> None:
        """Test successful command addition."""
        api = CliApi()

        def test_func() -> str:
            return "test result"

        result = api.add_command("test_cmd", test_func)

        assert result.is_success
        assert "Command test_cmd added" in result.data
        assert "test_cmd" in api._commands

    def test_add_command_duplicate_fails(self, mock_flext_core) -> None:
        """Test adding duplicate command fails."""
        api = CliApi()

        def test_func() -> str:
            return "test"

        # Add first command
        api.add_command("test_cmd", test_func)

        # Try to add duplicate
        result = api.add_command("test_cmd", test_func)

        assert not result.is_success
        assert "Command test_cmd already exists" in result.error

    def test_add_command_invalid_name_fails(self, mock_flext_core) -> None:
        """Test adding command with invalid name fails."""
        api = CliApi()

        def test_func() -> str:
            return "test"

        result = api.add_command("", test_func)

        assert not result.is_success
        assert "Invalid command name or function" in result.error

    def test_add_command_non_callable_fails(self, mock_flext_core) -> None:
        """Test adding non-callable as command fails."""
        api = CliApi()

        result = api.add_command("test_cmd", "not_a_function")

        assert not result.is_success
        assert "Invalid command name or function" in result.error

    def test_execute_command_success(self, mock_flext_core) -> None:
        """Test successful command execution."""
        api = CliApi()

        def test_func(x: int, y: int) -> int:
            return x + y

        api.add_command("add", test_func)
        result = api.execute("add", 2, 3)

        assert result.is_success
        assert result.data == 5

    def test_execute_command_not_found_fails(self, mock_flext_core) -> None:
        """Test executing non-existent command fails."""
        api = CliApi()

        result = api.execute("nonexistent")

        assert not result.is_success
        assert "Command nonexistent not found" in result.error

    def test_execute_command_with_kwargs(self, mock_flext_core) -> None:
        """Test command execution with keyword arguments."""
        api = CliApi()

        def test_func(name: str, age: int = 25) -> str:
            return f"{name} is {age} years old"

        api.add_command("greet", test_func)
        result = api.execute("greet", "Alice", age=30)

        assert result.is_success
        assert result.data == "Alice is 30 years old"
