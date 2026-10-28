"""Behavioral contract tests for flext_cli ``u.Cli`` cmd/runtime/validation helpers.

Exercises only the public surface exposed through ``u.Cli``: the ``r[T]``
outcome of fallible operations, the public model state they produce, and the
observable contract of environment resolution. No private attributes, no
internal-collaborator spying, no line-coverage pokes.

Copyright (c) 2026 FLEXT Team. All rights reserved.
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

from tests import c, t, tm, u


class TestsFlextCliCmdRuntimeValidationBranchCov:
    """Public-contract behavior of cmd, runtime, and validation helpers."""

    # ------------------------------------------------------------- runtime
    @staticmethod
    def test_process_env_inherits_and_applies_override() -> None:
        """Verify that process env inherits and applies override."""
        env = u.Cli.process_env(overrides={"FLEXT_CLI_TEST_KEY": "present"})

        tm.that(env["FLEXT_CLI_TEST_KEY"], eq="present")

    @staticmethod
    def test_process_env_removes_inherited_key() -> None:
        """Verify that process env removes inherited key."""
        inherited = u.Cli.process_env()
        present_key = next(iter(inherited))

        pruned = u.Cli.process_env(remove_keys=(present_key,))

        tm.that(pruned, lacks=present_key)

    @staticmethod
    def test_process_env_removing_unknown_key_is_a_noop() -> None:
        """Verify that process env removing unknown key is a noop."""
        baseline = u.Cli.process_env()
        pruned = u.Cli.process_env(remove_keys=("__definitely_missing__",))

        tm.that(pruned, eq=baseline)

    # ---------------------------------------------------------- validation
    @staticmethod
    @pytest.mark.parametrize("output_format", tuple(c.Cli.OUTPUT_FORMATS))
    def test_validate_format_accepts_every_supported_format(
        output_format: str,
    ) -> None:
        """Verify that validate format accepts every supported format."""
        result = u.Cli.validate_format(output_format)

        tm.ok(result)
        tm.that(result.unwrap(), eq=output_format.lower())

    @staticmethod
    def test_validate_format_normalizes_case_on_success() -> None:
        """Verify that validate format normalizes case on success."""
        canonical = next(iter(c.Cli.OUTPUT_FORMATS))

        result = u.Cli.validate_format(canonical.upper())

        tm.ok(result)
        tm.that(result.unwrap(), eq=canonical.lower())

    @staticmethod
    def test_validate_format_rejects_unknown_and_echoes_original_input() -> None:
        """Verify that validate format rejects unknown and echoes original input."""
        result = u.Cli.validate_format("BAD")

        tm.fail(result)
        tm.that((result.error or ""), has="BAD")

    @staticmethod
    @pytest.mark.parametrize("value", ["ok", "  padded  ", 0, 1])
    def test_validate_not_empty_accepts_meaningful_values(
        value: t.Cli.CliValue,
    ) -> None:
        """Verify that validate not empty accepts meaningful values."""
        result = u.Cli.validate_not_empty(value, name="field")

        tm.ok(result)
        tm.ok(result.unwrap())

    @staticmethod
    @pytest.mark.parametrize("value", [None, "", "   "])
    def test_validate_not_empty_rejects_empty_and_names_the_field(
        value: t.Cli.CliValue | None,
    ) -> None:
        """Verify that validate not empty rejects empty and names the field."""
        result = u.Cli.validate_not_empty(value, name="myfield")

        tm.fail(result)
        tm.that((result.error or ""), has="myfield")
