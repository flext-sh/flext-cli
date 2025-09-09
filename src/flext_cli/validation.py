"""FLEXT CLI Validation - Validation utilities using flext-core directly.

Provides FlextCliValidation class that leverages flext-core validation
instead of reimplementing validation logic.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from flext_core import FlextResult, FlextUtilities, FlextValidations

from flext_cli.constants import FlextCliConstants


class FlextCliValidation:
    """Consolidated validation utilities using flext-core validation directly.

    Leverages flext-core validation capabilities instead of reimplementing
    validation logic, following DRY principles and maximizing library usage.

    Features:
        - Email validation via FlextValidations
        - URL validation with basic pattern matching
        - Path validation with existence checks
        - File/directory validation
        - Filename sanitization via FlextUtilities
    """

    def __init__(self) -> None:
        """Initialize validation utilities."""

    def validate_email(self, email: str | None) -> FlextResult[str]:
        """Validate email address using flext-core validation.

        Args:
            email: Email address to validate

        Returns:
            FlextResult containing validated email or error

        """
        if email is None or not email.strip():
            return FlextResult[str].fail("Email cannot be empty")
        return FlextValidations.validate_email(email.strip())

    def validate_url(self, url: str | None) -> FlextResult[str]:
        """Validate URL using basic pattern validation.

        Args:
            url: URL to validate

        Returns:
            FlextResult containing validated URL or error

        """
        if url is None or not url.strip():
            return FlextResult[str].fail("URL cannot be empty")

        url_stripped = url.strip()

        # Basic URL validation - check if it starts with http/https and has a domain
        if not (url_stripped.startswith(("http://", "https://"))):
            return FlextResult[str].fail("URL must start with http:// or https://")

        # Basic domain validation - must have valid domain or be localhost
        try:
            parsed = urlparse(url_stripped)
            if not parsed.netloc:
                return FlextResult[str].fail("URL must have a valid domain")

            # Allow localhost or domains with dots
            if (
                parsed.netloc.split(":")[0].lower() not in {"localhost", "127.0.0.1"}
                and "." not in parsed.netloc
            ):
                return FlextResult[str].fail("URL must have a valid domain")

            return FlextResult[str].ok(url_stripped)
        except Exception as e:
            return FlextResult[str].fail(f"Invalid URL format: {e}")

    def validate_path(
        self,
        path: str | Path,
        *,
        must_exist: bool = True,
        must_be_file: bool | None = None,
        must_be_dir: bool | None = None,
    ) -> FlextResult[Path]:
        """Validate filesystem path with existence and type checks.

        Args:
            path: Path to validate
            must_exist: Whether path must exist
            must_be_file: Whether path must be a file
            must_be_dir: Whether path must be a directory

        Returns:
            FlextResult containing validated Path object

        """
        try:
            p = Path(path)

            if must_exist and not p.exists():
                return FlextResult[Path].fail(f"Path does not exist: {path}")

            if must_be_file and not p.is_file():
                return FlextResult[Path].fail(f"Path is not a file: {path}")

            if must_be_dir and not p.is_dir():
                return FlextResult[Path].fail(f"Path is not a directory: {path}")

            return FlextResult[Path].ok(p)
        except Exception as e:
            return FlextResult[Path].fail(f"Path validation failed: {e}")

    def sanitize_filename(self, name: str) -> FlextResult[str]:
        """Sanitize filename using flext-core utilities.

        Args:
            name: Filename to sanitize

        Returns:
            FlextResult containing sanitized filename

        """
        try:
            sanitized = FlextUtilities.TextProcessor.sanitize_filename(name)
            max_len = FlextCliConstants.MAX_FILENAME_LENGTH

            if len(sanitized) > max_len:
                sanitized = sanitized[:max_len]

            return FlextResult[str].ok(sanitized)
        except Exception as e:
            return FlextResult[str].fail(f"Filename sanitization failed: {e}")

    def validate_config_value(
        self, value: object, expected_type: type, *, allow_none: bool = False
    ) -> FlextResult[object]:
        """Validate configuration value against expected type.

        Args:
            value: Value to validate
            expected_type: Expected type for the value
            allow_none: Whether None values are allowed

        Returns:
            FlextResult containing validated value

        """
        try:
            if value is None:
                if allow_none:
                    return FlextResult[object].ok(None)
                return FlextResult[object].fail("Value cannot be None")

            if not isinstance(value, expected_type):
                return FlextResult[object].fail(
                    f"Expected {expected_type.__name__}, got {type(value).__name__}"
                )

            return FlextResult[object].ok(value)
        except Exception as e:
            return FlextResult[object].fail(f"Config validation failed: {e}")

    def validate_timeout(self, timeout: int) -> FlextResult[int]:
        """Validate timeout value within acceptable limits.

        Args:
            timeout: Timeout value in seconds

        Returns:
            FlextResult containing validated timeout

        """
        if timeout < FlextCliConstants.MIN_COMMAND_TIMEOUT:
            return FlextResult[int].fail(
                f"Timeout must be at least {FlextCliConstants.MIN_COMMAND_TIMEOUT} seconds"
            )

        if timeout > FlextCliConstants.MAX_TIMEOUT_SECONDS:
            return FlextResult[int].fail(
                f"Timeout cannot exceed {FlextCliConstants.MAX_TIMEOUT_SECONDS} seconds"
            )

        return FlextResult[int].ok(timeout)


__all__ = ["FlextCliValidation"]
