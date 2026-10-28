"""FLEXT CLI Common Parameters Tests - behavioral contract of FlextCliCommonParams.

Exercises only the observable public contract: return values, ``r[T]`` outcomes,
raised exceptions, applied public model state, and CLI-runner output. No private
attribute/method access, no patching of internal collaborators.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

import pytest

from flext_cli import cli
from tests import c, p, tm, u


@pytest.mark.usefixtures("preserve_logging")
class TestsFlextCliCliParams:
    """Behavioral tests for FlextCliCommonParams public contract."""

    @staticmethod
    @pytest.fixture
    def settings() -> p.Cli.Settings:
        """Fresh CLI settings instance built through the public factory.

        Returns:
            The resulting ``p.Cli.Settings``.

        """
        result = u.Tests.create_test_settings()
        tm.ok(result)
        return result.value

    # ── apply_to_config: success paths ───────────────────────────────

    @staticmethod
    def test_apply_to_config_applies_flags_and_log_level(
        settings: p.Cli.Settings,
    ) -> None:
        """apply_to_config returns updated settings reflecting each applied value."""
        result = cli.apply_to_config(
            settings,
            verbose=True,
            debug=True,
            log_level=c.LogLevel.DEBUG,
        )

        tm.ok(result)
        updated = result.value
        tm.ok(updated.cli_verbose is True)
        tm.ok(updated.debug is True)
        tm.that(updated.log_level, eq=c.LogLevel.DEBUG)

    @staticmethod
    def test_apply_to_config_trace_with_debug_enables_trace(
        settings: p.Cli.Settings,
    ) -> None:
        """Trace is accepted and applied when debug is also enabled."""
        result = cli.apply_to_config(settings, debug=True, trace=True)

        tm.ok(result)
        updated = result.value
        tm.ok(updated.debug is True)
        tm.ok(updated.trace is True)

    @staticmethod
    def test_apply_to_config_is_idempotent_for_same_values(
        settings: p.Cli.Settings,
    ) -> None:
        """Applying the same values twice yields the same observable state."""
        first = cli.apply_to_config(settings, verbose=True, log_level=c.LogLevel.DEBUG)
        tm.ok(first)
        second = cli.apply_to_config(
            first.value,
            verbose=True,
            log_level=c.LogLevel.DEBUG,
        )
        tm.ok(second)
        tm.ok(second.value.cli_verbose is True)
        tm.that(second.value.log_level, eq=c.LogLevel.DEBUG)

    # ── apply_to_config: failure paths ───────────────────────────────

    @staticmethod
    def test_apply_to_config_trace_without_debug_preserves_severity(
        settings: p.Cli.Settings,
    ) -> None:
        """Diagnostic detail does not require debug or lower an explicit level."""
        current = settings.clone(log_level=c.LogLevel.ERROR, debug=False)
        result = cli.apply_to_config(current, trace=True)

        tm.ok(result)
        tm.ok(result.value.trace)
        tm.that(result.value.debug, eq=current.debug)
        tm.that(result.value.log_level, eq=current.log_level)

    @staticmethod
    def test_apply_to_config_unknown_parameter_fails_carrying_validation_error(
        settings: p.Cli.Settings,
    ) -> None:
        """A parameter the params model rejects fails and keeps its cause."""
        result = cli.apply_to_config(settings, not_a_param=True)

        tm.fail(result)
        tm.that((result.error or ""), has="not_a_param")
        tm.that(result.exception, is_=c.ValidationError)

    @staticmethod
    @pytest.mark.parametrize(
        ("field_name", "expected_fragments"),
        [
            ("log_level", ("invalid", "log")),
            ("log_format", ("invalid", "log format")),
            ("output_format", ("invalid", "output format")),
        ],
    )
    def test_apply_to_config_rejects_invalid_enum_value(
        settings: p.Cli.Settings, field_name: str, expected_fragments: tuple[str, ...]
    ) -> None:
        """Each choice-bound field rejects an out-of-domain value with a clear error."""
        match field_name:
            case "log_level":
                result = cli.apply_to_config(settings, log_level="INVALID")
            case "log_format":
                result = cli.apply_to_config(settings, log_format="INVALID")
            case _:
                result = cli.apply_to_config(settings, output_format="INVALID")

        tm.fail(result)
        error_msg = (result.error or "").lower()
        for fragment in expected_fragments:
            tm.that(error_msg, has=fragment)
