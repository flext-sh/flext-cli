"""FlextCliValidator - Input validation using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Consolidated validation eliminating duplications with flext-core.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

# Import centralized helpers to eliminate duplication
from flext_cli.core._helpers import (
    flext_cli_fail as _fail,
    flext_cli_success as _success,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from flext_core import FlextResult


class FlextCliValidator:
    """Input validation with built-in patterns and custom validators.

    Built on flext-core FlextResult patterns, no duplications.
    """

    # Comprehensive validation patterns (no duplication with external libs)
    PATTERNS: dict[str, str] = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "url": r"^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:\w)*)?)?$",
        "phone": r"^\+?1?-?\.?\s?\(?([0-9]{3})\)?[-\.\s]?([0-9]{3})[-\.\s]?([0-9]{4})$",
        "ipv4": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        "ipv6": r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$",
        "mac": r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        "password": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
        "username": r"^[a-zA-Z0-9_]{3,20}$",
        "slug": r"^[a-z0-9-]+$",
        "hex_color": r"^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
        "date_iso": r"^\d{4}-\d{2}-\d{2}$",
        "datetime_iso": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?(?:Z|[+-]\d{2}:\d{2})$",
        "time_24h": r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        "semantic_version": r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$",
        "jwt": r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$",
        "base64": r"^[A-Za-z0-9+/]*={0,2}$",
        "json": r"^[\{\[].*[\}\]]$",
        "credit_card": r"^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})$",
        "ssn": r"^\d{3}-?\d{2}-?\d{4}$",
        "zip_code": r"^\d{5}(-\d{4})?$",
        "isbn": r"^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$",
        "domain": r"^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$",
        "file_path": r"^[^\0<>:\"/\\|?*]+$",
    }

    def __init__(self, validations: dict[str, str | Callable[..., Any]] | None = None) -> None:
        self.validations = validations or {}
        self._compiled_patterns: dict[str, re.Pattern[str]] = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns after initialization."""
        self._compiled_patterns = {}
        for field, rule in self.validations.items():
            if isinstance(rule, str):
                pattern = self.PATTERNS.get(rule, rule)
                try:
                    self._compiled_patterns[field] = re.compile(pattern)
                except re.error as e:
                    msg = f"Invalid regex for '{field}': {e}"
                    raise ValueError(msg) from e

    def validate(self, field: str, value: Any) -> FlextResult[Any]:
        """Validate single field using flext-core FlextResult."""
        if field not in self.validations:
            return _success(value)

        rule = self.validations[field]

        try:
            if callable(rule):
                if rule(value):
                    return _success(value)
                return _fail(f"Validation failed for {field}")

            if isinstance(rule, str):
                str_value = str(value)
                pattern = self._compiled_patterns.get(field)
                if pattern and pattern.match(str_value):
                    return _success(value)
                rule_name = rule if rule in self.PATTERNS else "custom pattern"
                return _fail(f"'{str_value}' doesn't match {rule_name} for {field}")

            return _fail(f"Invalid validation rule for {field}")

        except Exception as e:
            return _fail(f"Validation error for {field}: {e}")

    def validate_dict(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Validate multiple fields using flext-core patterns."""
        errors = []
        validated_data = {}

        for field, value in data.items():
            result = self.validate(field, value)
            if result.success:
                validated_data[field] = result.unwrap()
            else:
                errors.append(result.error)

        if errors:
            return _fail("; ".join(errors))
        return _success(validated_data)

    def add_validation(self, field: str, rule: str | Callable[..., Any]) -> None:
        """Add validation rule dynamically."""
        self.validations[field] = rule

        if isinstance(rule, str):
            pattern = self.PATTERNS.get(rule, rule)
            try:
                self._compiled_patterns[field] = re.compile(pattern)
            except re.error as e:
                msg = f"Invalid regex for '{field}': {e}"
                raise ValueError(msg) from e

    def has_validations(self) -> bool:
        """Check if any validations are configured."""
        return bool(self.validations)

    def get_available_patterns(self) -> list[str]:
        """Get available validation patterns."""
        return list(self.PATTERNS.keys())

    @classmethod
    def create_web_validator(cls) -> FlextCliValidator:
        """Create validator for web inputs."""
        return cls({
            "url": "url",
            "email": "email",
            "color": "hex_color",
            "slug": "slug",
        })

    @classmethod
    def create_security_validator(cls) -> FlextCliValidator:
        """Create validator for security inputs."""
        return cls({
            "password": "password",
            "username": "username",
            "uuid": "uuid",
        })

    @classmethod
    def create_network_validator(cls) -> FlextCliValidator:
        """Create validator for network inputs."""
        return cls({
            "ip": "ipv4",
            "mac": "mac",
            "port": lambda x: 1 <= int(x) <= 65535,
        })
