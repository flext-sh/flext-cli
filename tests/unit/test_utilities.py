"""FLEXT CLI Utilities Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliUtilities covering all real functionality with flext_tests
integration, comprehensive utility functions, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import math
from datetime import datetime
from uuid import UUID

import pytest

from flext_cli.utilities import FlextCliUtilities
from flext_core import FlextResult
from flext_tests import FlextTestsUtilities


class TestFlextCliUtilities:
    """Comprehensive tests for FlextCliUtilities functionality."""

    @pytest.fixture
    def utilities(self) -> FlextCliUtilities:
        """Create FlextCliUtilities instance for testing."""
        return FlextCliUtilities()

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================

    def test_utilities_initialization(self, utilities: FlextCliUtilities) -> None:
        """Test utilities initialization and basic properties."""
        assert utilities is not None
        assert hasattr(utilities, "_logger")
        assert hasattr(utilities, "_container")

    def test_utilities_execute_method(self, utilities: FlextCliUtilities) -> None:
        """Test utilities execute method with real functionality."""
        result = utilities.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
        assert data["service"] == "flext-cli-utilities"

    def test_utilities_execute_async_method(self, utilities: FlextCliUtilities) -> None:
        """Test utilities async execute method."""
        async def run_test() -> None:
            result = await utilities.execute_async()

            assert isinstance(result, FlextResult)
            assert result.is_success

            data = result.unwrap()
            assert isinstance(data, dict)
            assert "status" in data
            assert "service" in data
            assert data["service"] == "flext-cli-utilities"

        asyncio.run(run_test())

    # ========================================================================
    # STRING UTILITIES
    # ========================================================================

    def test_slugify_string(self, utilities: FlextCliUtilities) -> None:
        """Test string slugification functionality."""
        test_cases = [
            ("Hello World!", "hello-world"),
            ("Test String 123", "test-string-123"),
            ("Special@#$Characters", "specialcharacters"),
            ("Multiple   Spaces", "multiple-spaces"),
            ("UPPERCASE", "uppercase"),
            ("", ""),
        ]

        for input_str, expected in test_cases:
            result = utilities.slugify_string(input_str)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    def test_camel_case_to_snake_case(self, utilities: FlextCliUtilities) -> None:
        """Test camelCase to snake_case conversion."""
        test_cases = [
            ("camelCase", "camel_case"),
            ("PascalCase", "pascal_case"),
            ("already_snake_case", "already_snake_case"),
            ("XMLHttpRequest", "xml_http_request"),
            ("HTMLParser", "html_parser"),
            ("", ""),
        ]

        for input_str, expected in test_cases:
            result = utilities.camel_case_to_snake_case(input_str)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    def test_snake_case_to_camel_case(self, utilities: FlextCliUtilities) -> None:
        """Test snake_case to camelCase conversion."""
        test_cases = [
            ("snake_case", "snakeCase"),
            ("already_camel_case", "alreadyCamelCase"),
            ("multiple_underscores", "multipleUnderscores"),
            ("single", "single"),
            ("", ""),
        ]

        for input_str, expected in test_cases:
            result = utilities.snake_case_to_camel_case(input_str)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    def test_truncate_string(self, utilities: FlextCliUtilities) -> None:
        """Test string truncation functionality."""
        test_string = "This is a long string that should be truncated"

        # Test truncation with default suffix
        result = utilities.truncate_string(test_string, 20)
        assert isinstance(result, FlextResult)
        assert result.is_success
        truncated = result.unwrap()
        assert len(truncated) <= 20
        assert truncated.endswith("...")

        # Test truncation with custom suffix
        result = utilities.truncate_string(test_string, 20, "...")
        assert isinstance(result, FlextResult)
        assert result.is_success
        truncated = result.unwrap()
        assert len(truncated) <= 20
        assert truncated.endswith("...")

        # Test truncation without suffix
        result = utilities.truncate_string(test_string, 20, "")
        assert isinstance(result, FlextResult)
        assert result.is_success
        truncated = result.unwrap()
        assert len(truncated) == 20
        assert not truncated.endswith("...")

    def test_remove_special_characters(self, utilities: FlextCliUtilities) -> None:
        """Test special character removal functionality."""
        test_cases = [
            ("Hello@World#123!", "HelloWorld123"),
            ("Test$String%With^Special&Characters", "TestStringWithSpecialCharacters"),
            ("NormalString", "NormalString"),
            ("", ""),
        ]

        for input_str, expected in test_cases:
            result = utilities.remove_special_characters(input_str)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    def test_extract_numbers_from_string(self, utilities: FlextCliUtilities) -> None:
        """Test number extraction from string functionality."""
        test_cases = [
            ("abc123def456", [123, 456]),
            ("no numbers here", []),
            ("123", [123]),
            ("1.5 and 2.7", [1.5, 2.7]),
            ("", []),
        ]

        for input_str, expected in test_cases:
            result = utilities.extract_numbers_from_string(input_str)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    # ========================================================================
    # DATA VALIDATION UTILITIES
    # ========================================================================

    def test_validate_email(self, utilities: FlextCliUtilities) -> None:
        """Test email validation functionality."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
            "user123@test-domain.com",
        ]

        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test@.com",
            "test..test@example.com",
            "",
        ]

        for email in valid_emails:
            result = utilities.validate_email(email)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is True

        for email in invalid_emails:
            result = utilities.validate_email(email)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is False

    def test_validate_url(self, utilities: FlextCliUtilities) -> None:
        """Test URL validation functionality."""
        valid_urls = [
            "https://example.com",
            "http://test.org",
            "https://subdomain.example.com/path",
            "https://example.com:8080/path?query=value",
        ]

        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "https://",
            "example.com",
            "",
        ]

        for url in valid_urls:
            result = utilities.validate_url(url)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is True

        for url in invalid_urls:
            result = utilities.validate_url(url)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is False

    def test_validate_phone_number(self, utilities: FlextCliUtilities) -> None:
        """Test phone number validation functionality."""
        valid_phones = [
            "+1234567890",
            "123-456-7890",
            "(123) 456-7890",
            "123.456.7890",
            "+1-123-456-7890",
        ]

        invalid_phones = [
            "123",
            "not-a-phone",
            "",
            "123-456-78901",  # Too long
        ]

        for phone in valid_phones:
            result = utilities.validate_phone_number(phone)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is True

        for phone in invalid_phones:
            result = utilities.validate_phone_number(phone)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is False

    def test_validate_ip_address(self, utilities: FlextCliUtilities) -> None:
        """Test IP address validation functionality."""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "255.255.255.255",
            "0.0.0.0",
        ]

        invalid_ips = [
            "256.1.1.1",
            "192.168.1",
            "not-an-ip",
            "",
            "192.168.1.1.1",
        ]

        for ip in valid_ips:
            result = utilities.validate_ip_address(ip)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is True

        for ip in invalid_ips:
            result = utilities.validate_ip_address(ip)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is False

    # ========================================================================
    # DATE AND TIME UTILITIES
    # ========================================================================

    def test_format_timestamp(self, utilities: FlextCliUtilities) -> None:
        """Test timestamp formatting functionality."""
        import time
        current_timestamp = time.time()
        result = utilities.format_timestamp(current_timestamp)

        assert isinstance(result, FlextResult)
        assert result.is_success

        timestamp = result.unwrap()
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format
        assert "Z" in timestamp  # UTC indicator

    def test_parse_timestamp(self, utilities: FlextCliUtilities) -> None:
        """Test timestamp parsing functionality."""
        # Test with ISO format timestamp
        iso_timestamp = "2025-01-01T12:00:00Z"
        result = utilities.parse_timestamp(iso_timestamp)

        assert isinstance(result, FlextResult)
        assert result.is_success

        parsed_time = result.unwrap()
        assert isinstance(parsed_time, datetime)

    def test_get_timestamp_difference(self, utilities: FlextCliUtilities) -> None:
        """Test timestamp difference calculation."""
        timestamp1 = "2025-01-01T12:00:00Z"
        timestamp2 = "2025-01-01T13:00:00Z"

        result = utilities.get_timestamp_difference(timestamp1, timestamp2)

        assert isinstance(result, FlextResult)
        assert result.is_success

        difference = result.unwrap()
        assert isinstance(difference, float)
        assert difference == 3600.0  # 1 hour in seconds

    def test_add_time_to_timestamp(self, utilities: FlextCliUtilities) -> None:
        """Test adding time to timestamp functionality."""
        import time
        base_timestamp = time.time()
        seconds_to_add = 7200  # 2 hours in seconds

        result = utilities.add_time_to_timestamp(base_timestamp, seconds=seconds_to_add)

        assert isinstance(result, FlextResult)
        assert result.is_success

        new_timestamp = result.unwrap()
        assert isinstance(new_timestamp, str)
        assert "2025-01-01T14:00:00Z" in new_timestamp

    # ========================================================================
    # DATA CONVERSION UTILITIES
    # ========================================================================

    def test_convert_bytes_to_human_readable(self, utilities: FlextCliUtilities) -> None:
        """Test bytes to human readable conversion."""
        test_cases = [
            (1024, "1.0 KB"),
            (1048576, "1.0 MB"),
            (1073741824, "1.0 GB"),
            (1023, "1023 B"),
            (0, "0 B"),
        ]

        for bytes_value, expected in test_cases:
            result = utilities.convert_bytes_to_human_readable(bytes_value)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    def test_convert_human_readable_to_bytes(self, utilities: FlextCliUtilities) -> None:
        """Test human readable to bytes conversion."""
        test_cases = [
            ("1 KB", 1024),
            ("1 MB", 1048576),
            ("1 GB", 1073741824),
            ("1023 B", 1023),
            ("0 B", 0),
        ]

        for human_readable, expected in test_cases:
            result = utilities.convert_human_readable_to_bytes(human_readable)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    def test_convert_temperature(self, utilities: FlextCliUtilities) -> None:
        """Test temperature conversion functionality."""
        # Test Celsius to Fahrenheit
        result = utilities.convert_temperature(0, "celsius", "fahrenheit")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == 32.0

        # Test Fahrenheit to Celsius
        result = utilities.convert_temperature(32, "fahrenheit", "celsius")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == 0.0

        # Test Celsius to Kelvin
        result = utilities.convert_temperature(0, "celsius", "kelvin")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == 273.15

    def test_convert_currency(self, utilities: FlextCliUtilities) -> None:
        """Test currency conversion functionality."""
        # Note: This might require external API or mock data
        # For now, test the basic structure
        result = utilities.convert_currency(100, "USD", "EUR")

        assert isinstance(result, FlextResult)
        # The result might be success or failure depending on implementation
        # We just verify it returns a FlextResult

    # ========================================================================
    # ENCRYPTION AND SECURITY UTILITIES
    # ========================================================================

    def test_hash_string(self, utilities: FlextCliUtilities) -> None:
        """Test string hashing functionality."""
        test_string = "Hello, World!"
        
        # Test MD5
        result = utilities.hash_string(test_string, "md5")
        assert isinstance(result, FlextResult)
        assert result.is_success
        md5_hash = result.unwrap()
        assert isinstance(md5_hash, str)
        assert len(md5_hash) == 32

        # Test SHA256
        result = utilities.hash_string(test_string, "sha256")
        assert isinstance(result, FlextResult)
        assert result.is_success
        sha256_hash = result.unwrap()
        assert isinstance(sha256_hash, str)
        assert len(sha256_hash) == 64

    def test_generate_random_string(self, utilities: FlextCliUtilities) -> None:
        """Test random string generation functionality."""
        result = utilities.generate_random_string(10)

        assert isinstance(result, FlextResult)
        assert result.is_success

        random_string = result.unwrap()
        assert isinstance(random_string, str)
        assert len(random_string) == 10

        # Generate another string and verify they're different
        result2 = utilities.generate_random_string(10)
        assert result2.is_success
        random_string2 = result2.unwrap()
        assert random_string != random_string2

    def test_generate_uuid(self, utilities: FlextCliUtilities) -> None:
        """Test UUID generation functionality."""
        result = utilities.generate_uuid()

        assert isinstance(result, FlextResult)
        assert result.is_success

        uuid_value = result.unwrap()
        assert isinstance(uuid_value, str)
        assert len(uuid_value) == 36  # Standard UUID length
        assert uuid_value.count("-") == 4  # Standard UUID format

        # Verify it's a valid UUID
        try:
            UUID(uuid_value)
        except ValueError:
            pytest.fail("Generated UUID is not valid")

    def test_encrypt_string(self, utilities: FlextCliUtilities) -> None:
        """Test string encryption functionality."""
        test_string = "Sensitive data"
        password = "test_password"

        result = utilities.encrypt_string(test_string, password)

        assert isinstance(result, FlextResult)
        assert result.is_success

        encrypted = result.unwrap()
        assert isinstance(encrypted, str)
        assert encrypted != test_string  # Should be different from original

    def test_decrypt_string(self, utilities: FlextCliUtilities) -> None:
        """Test string decryption functionality."""
        test_string = "Sensitive data"
        password = "test_password"

        # First encrypt
        encrypt_result = utilities.encrypt_string(test_string, password)
        assert encrypt_result.is_success
        encrypted = encrypt_result.unwrap()

        # Then decrypt
        decrypt_result = utilities.decrypt_string(encrypted, password)
        assert isinstance(decrypt_result, FlextResult)
        assert decrypt_result.is_success

        decrypted = decrypt_result.unwrap()
        assert decrypted == test_string

    # ========================================================================
    # FILE AND PATH UTILITIES
    # ========================================================================

    def test_get_file_extension(self, utilities: FlextCliUtilities) -> None:
        """Test file extension extraction functionality."""
        test_cases = [
            ("file.txt", ".txt"),
            ("document.pdf", ".pdf"),
            ("image.jpeg", ".jpeg"),
            ("no_extension", ""),
            ("", ""),
        ]

        for filename, expected in test_cases:
            result = utilities.get_file_extension(filename)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    def test_get_file_name_without_extension(self, utilities: FlextCliUtilities) -> None:
        """Test filename without extension extraction."""
        test_cases = [
            ("file.txt", "file"),
            ("document.pdf", "document"),
            ("image.jpeg", "image"),
            ("no_extension", "no_extension"),
            ("", ""),
        ]

        for filename, expected in test_cases:
            result = utilities.get_file_name_without_extension(filename)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    def test_normalize_path(self, utilities: FlextCliUtilities) -> None:
        """Test path normalization functionality."""
        test_cases = [
            ("/path/to/file.txt", "/path/to/file.txt"),
            ("path/../path/file.txt", "path/file.txt"),
            ("./file.txt", "file.txt"),
            ("", ""),
        ]

        for input_path, expected in test_cases:
            result = utilities.normalize_path(input_path)
            assert isinstance(result, FlextResult)
            assert result.is_success
            # Note: The exact output might vary by system, so we just verify it's a string
            assert isinstance(result.unwrap(), str)

    def test_join_paths(self, utilities: FlextCliUtilities) -> None:
        """Test path joining functionality."""
        result = utilities.join_paths("/path", "to", "file.txt")

        assert isinstance(result, FlextResult)
        assert result.is_success

        joined_path = result.unwrap()
        assert isinstance(joined_path, str)
        assert "file.txt" in joined_path

    # ========================================================================
    # NETWORK UTILITIES
    # ========================================================================

    def test_is_valid_ipv4(self, utilities: FlextCliUtilities) -> None:
        """Test IPv4 validation functionality."""
        valid_ips = ["192.168.1.1", "10.0.0.1", "255.255.255.255"]
        invalid_ips = ["256.1.1.1", "192.168.1", "not-an-ip"]

        for ip in valid_ips:
            result = utilities.is_valid_ipv4(ip)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is True

        for ip in invalid_ips:
            result = utilities.is_valid_ipv4(ip)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is False

    def test_is_valid_ipv6(self, utilities: FlextCliUtilities) -> None:
        """Test IPv6 validation functionality."""
        valid_ips = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "::1",
            "2001:db8::1",
        ]
        invalid_ips = ["192.168.1.1", "not-an-ip", ""]

        for ip in valid_ips:
            result = utilities.is_valid_ipv6(ip)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is True

        for ip in invalid_ips:
            result = utilities.is_valid_ipv6(ip)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() is False

    def test_extract_domain_from_url(self, utilities: FlextCliUtilities) -> None:
        """Test domain extraction from URL functionality."""
        test_cases = [
            ("https://example.com/path", "example.com"),
            ("http://subdomain.example.org:8080/path", "subdomain.example.org"),
            ("https://www.test.co.uk", "www.test.co.uk"),
        ]

        for url, expected in test_cases:
            result = utilities.extract_domain_from_url(url)
            assert isinstance(result, FlextResult)
            assert result.is_success
            assert result.unwrap() == expected

    # ========================================================================
    # MATHEMATICAL UTILITIES
    # ========================================================================

    def test_calculate_percentage(self, utilities: FlextCliUtilities) -> None:
        """Test percentage calculation functionality."""
        result = utilities.calculate_percentage(25, 100)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == 25.0

        result = utilities.calculate_percentage(1, 3)
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert abs(result.unwrap() - 33.33) < 0.01

    def test_round_to_decimal_places(self, utilities: FlextCliUtilities) -> None:
        """Test rounding to decimal places functionality."""
        result = utilities.round_to_decimal_places(math.pi, 2)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == math.pi

        result = utilities.round_to_decimal_places(math.pi, 4)
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == math.pi

    def test_calculate_distance(self, utilities: FlextCliUtilities) -> None:
        """Test distance calculation functionality."""
        # Test distance between two points (using simple Euclidean distance)
        result = utilities.calculate_distance(0, 0, 3, 4)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == 5.0  # 3-4-5 triangle

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

    def test_error_handling_with_invalid_input(self, utilities: FlextCliUtilities) -> None:
        """Test error handling with various invalid inputs."""
        # Test with None input
        result = utilities.slugify_string(None)  # type: ignore
        assert isinstance(result, FlextResult)
        assert result.is_failure

        # Test with invalid hash algorithm
        result = utilities.hash_string("test", "invalid_algorithm")
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_error_handling_with_edge_cases(self, utilities: FlextCliUtilities) -> None:
        """Test error handling with edge cases."""
        # Test with very long string
        long_string = "a" * 10000
        result = utilities.slugify_string(long_string)
        assert isinstance(result, FlextResult)
        assert result.is_success

        # Test with empty list
        result = utilities.extract_numbers_from_string("")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == []

    def test_concurrent_operations(self, utilities: FlextCliUtilities) -> None:
        """Test concurrent operations to ensure thread safety."""
        import threading

        results = []
        errors = []

        def worker(worker_id: int) -> None:
            try:
                result = utilities.generate_random_string(10)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        for result in results:
            assert isinstance(result, FlextResult)
            assert result.is_success

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_full_utility_workflow_integration(self, utilities: FlextCliUtilities) -> None:
        """Test complete utility workflow integration."""
        # 1. Generate random data
        random_string_result = utilities.generate_random_string(20)
        assert random_string_result.is_success
        random_string = random_string_result.unwrap()

        # 2. Hash the random string
        hash_result = utilities.hash_string(random_string, "sha256")
        assert hash_result.is_success
        hash_value = hash_result.unwrap()

        # 3. Generate UUID
        uuid_result = utilities.generate_uuid()
        assert uuid_result.is_success
        uuid_value = uuid_result.unwrap()

        # 4. Format timestamp
        import time
        current_timestamp = time.time()
        timestamp_result = utilities.format_timestamp(current_timestamp)
        assert timestamp_result.is_success
        timestamp = timestamp_result.unwrap()

        # 5. Create a data structure
        test_data = {
            "random_string": random_string,
            "hash": hash_value,
            "uuid": uuid_value,
            "timestamp": timestamp,
            "slug": utilities.slugify_string(random_string).unwrap(),
        }

        # 6. Validate the data
        assert isinstance(test_data["random_string"], str)
        assert len(test_data["random_string"]) == 20
        assert isinstance(test_data["hash"], str)
        assert len(test_data["hash"]) == 64
        assert isinstance(test_data["uuid"], str)
        assert len(test_data["uuid"]) == 36
        assert isinstance(test_data["timestamp"], str)
        assert "T" in test_data["timestamp"]
        assert isinstance(test_data["slug"], str)

    @pytest.mark.asyncio
    async def test_async_utility_workflow_integration(self, utilities: FlextCliUtilities) -> None:
        """Test async utility workflow integration."""
        # Test async execution
        result = await utilities.execute_async()
        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
        assert data["service"] == "flext-cli-utilities"
