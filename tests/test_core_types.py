"""Tests for core types in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

import click
import pytest

from flext_cli import (
    URL,
    ClickPath,
    ExistingDir,
    ExistingFile,
    NewFile,
    PositiveInt,
    PositiveIntType,
    URLType,
)


class TestPositiveIntType:
    """Test cases for PositiveIntType."""

    def test_valid_positive_integers(self) -> None:
        """Test valid positive integer conversion."""
        param_type = PositiveIntType()

        # Test various positive integers
        if param_type.convert(1, None, None) != 1:
            raise AssertionError(
                f"Expected {1}, got {param_type.convert(1, None, None)}",
            )
        assert param_type.convert(42, None, None) == 42
        if param_type.convert(1000, None, None) != 1000:
            raise AssertionError(
                f"Expected {1000}, got {param_type.convert(1000, None, None)}",
            )
        assert param_type.convert("5", None, None) == 5
        if param_type.convert("999", None, None) != 999:
            raise AssertionError(
                f"Expected {999}, got {param_type.convert('999', None, None)}",
            )

    def test_invalid_values(self) -> None:
        """Test invalid values raise click.BadParameter."""
        param_type = PositiveIntType()

        # Test zero and negative numbers
        with pytest.raises(click.BadParameter):
            param_type.convert(0, None, None)

        with pytest.raises(click.BadParameter):
            param_type.convert(-1, None, None)

        with pytest.raises(click.BadParameter):
            param_type.convert(-100, None, None)

    def test_non_numeric_values(self) -> None:
        """Test non-numeric values raise click.BadParameter."""
        param_type = PositiveIntType()

        with pytest.raises(click.BadParameter):
            param_type.convert("abc", None, None)

        with pytest.raises(click.BadParameter):
            param_type.convert("12.5", None, None)

        with pytest.raises(click.BadParameter):
            param_type.convert(None, None, None)

    def test_convenience_instance(self) -> None:
        """Test convenience PositiveInt instance."""
        assert isinstance(PositiveInt, PositiveIntType)
        if PositiveInt.name != "positive_int":
            raise AssertionError(f"Expected {'positive_int'}, got {PositiveInt.name}")


class TestURLType:
    """Test cases for URLType."""

    def test_valid_urls(self) -> None:
        """Test valid URL conversion."""
        url_type = URLType()

        valid_urls = [
            "http://example.com",
            "https://www.example.com",
            "https://api.example.com/v1",
            f"http://{__import__('flext_core.constants').flext_core.constants.FlextConstants.Platform.DEFAULT_HOST}:{__import__('flext_core.constants').flext_core.constants.FlextConstants.Platform.FLEXT_API_PORT}",
            "https://subdomain.example.com/path?query=value",
            "ftp://files.example.com",
        ]

        for url in valid_urls:
            if url_type.convert(url, None, None) != url:
                raise AssertionError(
                    f"Expected {url}, got {url_type.convert(url, None, None)}",
                )

    def test_invalid_urls(self) -> None:
        """Test invalid URLs raise click.BadParameter."""
        url_type = URLType()

        invalid_urls = [
            "not-a-url",
            "example.com",  # Missing scheme
            "http://",  # Missing netloc
            "://example.com",  # Missing scheme
            "",
            "   ",
        ]

        for invalid_url in invalid_urls:
            with pytest.raises(click.BadParameter):
                url_type.convert(invalid_url, None, None)

    def test_non_string_values(self) -> None:
        """Test non-string values raise click.BadParameter."""
        url_type = URLType()

        with pytest.raises(click.BadParameter):
            url_type.convert(123, None, None)

        with pytest.raises(click.BadParameter):
            url_type.convert(None, None, None)

        with pytest.raises(click.BadParameter):
            url_type.convert(["http://example.com"], None, None)

    def test_convenience_instance(self) -> None:
        """Test convenience URL instance."""
        assert isinstance(URL, URLType)
        if URL.name != "url":
            raise AssertionError(f"Expected {'url'}, got {URL.name}")


class TestClickPath:
    """Test cases for ClickPath."""

    def test_enhanced_path_creation(self) -> None:
        """Test enhanced ClickPath creation."""
        path_type = ClickPath(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        )

        assert isinstance(path_type, click.Path)
        if not (path_type.exists):
            raise AssertionError(f"Expected True, got {path_type.exists}")
        assert path_type.file_okay is True
        if path_type.dir_okay:
            raise AssertionError(f"Expected False, got {path_type.dir_okay}")
        if not (path_type.readable):
            raise AssertionError(f"Expected True, got {path_type.readable}")

    def test_path_type_parameter(self) -> None:
        """Test path_type parameter configuration."""

        # Test with Path type (default)
        @click.command()
        @click.argument("path", type=ClickPath(path_type=str))
        def cmd_with_path(path: Path) -> None:
            assert isinstance(path, Path)

        # Test with str type
        @click.command()
        @click.argument("path", type=ClickPath(path_type=str))
        def cmd_with_str(path: str) -> None:
            assert isinstance(path, str)

        # Test that both commands are properly configured
        assert isinstance(cmd_with_path.params[0].type, ClickPath)
        assert isinstance(cmd_with_str.params[0].type, ClickPath)

    def test_convenience_instances(self) -> None:
        """Test convenience path instances."""
        # ExistingFile
        assert isinstance(ExistingFile, ClickPath)
        if not (ExistingFile.exists):
            raise AssertionError(f"Expected True, got {ExistingFile.exists}")
        assert ExistingFile.file_okay is True
        if ExistingFile.dir_okay:
            raise AssertionError(f"Expected False, got {ExistingFile.dir_okay}")
        # ExistingDir
        assert isinstance(ExistingDir, ClickPath)
        if not (ExistingDir.exists):
            raise AssertionError(f"Expected True, got {ExistingDir.exists}")
        if ExistingDir.file_okay:
            raise AssertionError(f"Expected False, got {ExistingDir.file_okay}")
        if not (ExistingDir.dir_okay):
            raise AssertionError(f"Expected True, got {ExistingDir.dir_okay}")

        # NewFile
        assert isinstance(NewFile, ClickPath)
        if NewFile.exists:
            raise AssertionError(f"Expected False, got {NewFile.exists}")
        if not (NewFile.file_okay):
            raise AssertionError(f"Expected True, got {NewFile.file_okay}")
        if NewFile.dir_okay:
            raise AssertionError(f"Expected False, got {NewFile.dir_okay}")

    def test_path_resolution(self, temp_dir: Path) -> None:
        """Test path resolution functionality."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        # Test existing file
        existing_file_type = ClickPath(exists=True, file_okay=True, dir_okay=False)

        # This would normally be tested with click's testing utilities
        # For unit testing, we verify the configuration is correct
        if not (existing_file_type.exists):
            raise AssertionError(f"Expected True, got {existing_file_type.exists}")
        assert existing_file_type.file_okay is True
        if existing_file_type.dir_okay:
            raise AssertionError(f"Expected False, got {existing_file_type.dir_okay}")

    def test_writable_readable_options(self) -> None:
        """Test writable and readable options."""
        writable_path = ClickPath(writable=True, readable=False)
        if not (writable_path.writable):
            raise AssertionError(f"Expected True, got {writable_path.writable}")
        if writable_path.readable:
            raise AssertionError(f"Expected False, got {writable_path.readable}")
        readable_path = ClickPath(writable=False, readable=True)
        if readable_path.writable:
            raise AssertionError(f"Expected False, got {readable_path.writable}")
        if not (readable_path.readable):
            raise AssertionError(f"Expected True, got {readable_path.readable}")

    def test_allow_dash_option(self) -> None:
        """Test allow_dash option."""
        dash_path = ClickPath(allow_dash=True)
        if not (dash_path.allow_dash):
            raise AssertionError(f"Expected True, got {dash_path.allow_dash}")

        no_dash_path = ClickPath(allow_dash=False)
        if no_dash_path.allow_dash:
            raise AssertionError(f"Expected False, got {no_dash_path.allow_dash}")

    def test_resolve_path_option(self) -> None:
        """Test resolve_path option."""
        resolve_path = ClickPath(resolve_path=True)
        if not (resolve_path.resolve_path):
            raise AssertionError(f"Expected True, got {resolve_path.resolve_path}")

        no_resolve_path = ClickPath(resolve_path=False)
        if no_resolve_path.resolve_path:
            raise AssertionError(f"Expected False, got {no_resolve_path.resolve_path}")


class TestIntegrationWithClick:
    """Integration tests with Click framework."""

    def test_positive_int_in_click_command(self) -> None:
        """Test PositiveInt integration with Click commands."""

        @click.command()
        @click.option("--count", type=PositiveInt)
        def test_command(count: int) -> int:
            return count

        # Test the command is properly configured
        assert test_command.params[0].type is PositiveInt

    def test_url_in_click_command(self) -> None:
        """Test URL integration with Click commands."""

        @click.command()
        @click.option("--endpoint", type=URL)
        def test_command(endpoint: str) -> str:
            return endpoint

        # Test the command is properly configured
        assert test_command.params[0].type is URL

    def test_path_in_click_command(self) -> None:
        """Test ClickPath integration with Click commands."""

        @click.command()
        @click.option("--input-file", type=ExistingFile)
        @click.option("--output-dir", type=ExistingDir)
        @click.option("--new-file", type=NewFile)
        def test_command(
            input_file: Path,
            output_dir: Path,
            new_file: Path,
        ) -> tuple[Path, Path, Path]:
            return input_file, output_dir, new_file

        # Test the command is properly configured
        params = test_command.params
        assert params[0].type is ExistingFile
        assert params[1].type is ExistingDir
        assert params[2].type is NewFile

    def test_type_names_for_help(self) -> None:
        """Test type names appear correctly in help."""
        if PositiveInt.name != "positive_int":
            raise AssertionError(f"Expected {'positive_int'}, got {PositiveInt.name}")
        assert URL.name == "url"

        # Click.Path doesn't have a specific name attribute in the same way,
        # but we can verify it's properly configured
        assert isinstance(ExistingFile, click.Path)
        assert isinstance(ExistingDir, click.Path)
        assert isinstance(NewFile, click.Path)
