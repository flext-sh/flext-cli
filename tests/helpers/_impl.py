"""Implementation of test helpers - factories, validation, scenarios.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
import re
from collections.abc import (
    MutableSequence,
)
from typing import Self, override

from tests import c, m, p, r, t

from flext_cli import FlextCliPrompts


class FlextCliTestHelpers:
    """Centralized test helpers for flext-cli test modules."""

    class VersionTestFactory:
        """Factory for version validation tests."""

        @staticmethod
        def validate_version_string(version: str) -> p.Result[str]:
            """Validate version string against semver pattern."""
            if not version:
                return r[str].fail(c.Cli.Tests.EMPTY_STRING)
            pattern: str = c.Cli.Tests.SEMVER_PATTERN
            if not re.match(pattern, version):
                return r[str].fail(f"Version '{version}' does not match semver pattern")
            return r[str].ok(version)

        @staticmethod
        def validate_version_info(
            version_info: tuple[int | str, ...],
        ) -> p.Result[tuple[int | str, ...]]:
            """Validate version info tuple structure."""
            if len(version_info) < 3:
                return r[tuple[int | str, ...]].fail(
                    c.Cli.Tests.INFO_TOO_SHORT,
                )
            for i, part in enumerate(version_info):
                if isinstance(part, int) and part < 0:
                    return r[tuple[int | str, ...]].fail(
                        f"Version part {i} must be non-negative int",
                    )
                if isinstance(part, str) and (not part):
                    return r[tuple[int | str, ...]].fail(
                        f"Version part {i} must be non-empty string",
                    )
            return r[tuple[int | str, ...]].ok(version_info)

        @staticmethod
        def validate_consistency(
            version_string: str,
            version_info: tuple[int | str, ...],
        ) -> p.Result[tuple[str, tuple[int | str, ...]]]:
            """Validate consistency between version string and info tuple."""
            string_result = (
                FlextCliTestHelpers.VersionTestFactory.validate_version_string(
                    version_string,
                )
            )
            if string_result.failure:
                return r[tuple[str, tuple[int | str, ...]]].fail(
                    f"Invalid version string: {string_result.error}",
                )
            info_result = FlextCliTestHelpers.VersionTestFactory.validate_version_info(
                version_info,
            )
            if info_result.failure:
                return r[tuple[str, tuple[int | str, ...]]].fail(
                    f"Invalid version info: {info_result.error}",
                )
            version_without_metadata = version_string.split("+", maxsplit=1)[0]
            version_base_and_prerelease = version_without_metadata.split("-")
            base_parts = version_base_and_prerelease[0].split(".")
            prerelease_parts = (
                version_base_and_prerelease[1].split(".")
                if len(version_base_and_prerelease) > 1
                else []
            )
            version_parts_raw = base_parts + prerelease_parts
            version_parts: MutableSequence[int | str] = []
            for part in version_parts_raw:
                try:
                    version_parts.append(int(part))
                except ValueError:
                    logging.getLogger(__name__).debug(
                        "version part non-int, keep as str: %s",
                        part,
                    )
                    version_parts.append(part)
            info_parts = list(version_info)
            min_length = min(len(version_parts), len(info_parts))
            for i in range(min_length):
                version_part = version_parts[i]
                info_part = info_parts[i]
                if (isinstance(info_part, int) and isinstance(version_part, int)) or (
                    isinstance(info_part, str) and isinstance(version_part, str)
                ):
                    if version_part != info_part:
                        return r[tuple[str, tuple[int | str, ...]]].fail(
                            f"Mismatch at position {i}: {version_part} != {info_part}",
                        )
                else:
                    return r[tuple[str, tuple[int | str, ...]]].fail(
                        f"Type mismatch at position {i}: {type(version_part).__name__} != {type(info_part).__name__}",
                    )
            return r[tuple[str, tuple[int | str, ...]]].ok((
                version_string,
                version_info,
            ))


class FlextCliScriptedPrompts(FlextCliPrompts):
    """Prompt service with typed scripting helpers for tests."""

    def use_input_values(self, values: t.StrSequence) -> Self:
        values_iter = iter(values)
        self._input_reader = lambda _prompt: next(values_iter)
        return self

    def use_input_error(self, error: Exception) -> Self:
        def raise_input(_prompt: str) -> str:
            raise error

        self._input_reader = raise_input
        return self

    def use_password(self, password: str) -> Self:
        self._password_reader = lambda _prompt: password
        return self

    def use_password_error(self, error: Exception) -> Self:
        def raise_password(_prompt: str) -> str:
            raise error

        self._password_reader = raise_password
        return self

    def configure_state(
        self,
        *,
        interactive: bool = True,
        quiet: bool = False,
    ) -> Self:
        return self.configure(
            m.Cli.PromptRuntimeState(
                interactive=interactive,
                quiet=quiet,
            ),
        )


class FlextCliCaptureLogPrompts(FlextCliScriptedPrompts):
    """Prompt service that captures log calls without writing to the real logger."""

    _records: list[tuple[str, str]] = m.PrivateAttr(default_factory=list)

    @property
    def records(self) -> list[tuple[str, str]]:
        return self._records

    @override
    def _log(
        self,
        log_level: str,
        message: str,
        **context: t.LogValue,
    ) -> None:
        self._records.append((log_level, message))


class FlextCliFailingLogPrompts(FlextCliScriptedPrompts):
    """Prompt service that fails on one selected log level."""

    _failure_level: str = m.PrivateAttr(default_factory=lambda: "")
    _failure_message: str = m.PrivateAttr(default_factory=lambda: "logger failure")

    def fail_on_log(self, *, level: str, message: str) -> Self:
        self._failure_level = level
        self._failure_message = message
        return self

    @override
    def _log(
        self,
        log_level: str,
        message: str,
        **context: t.LogValue,
    ) -> None:
        if log_level == self._failure_level:
            raise ValueError(self._failure_message)
        super()._log(log_level, message, **context)


__all__: list[str] = [
    "FlextCliCaptureLogPrompts",
    "FlextCliFailingLogPrompts",
    "FlextCliScriptedPrompts",
    "FlextCliTestHelpers",
]
