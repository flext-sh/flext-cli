"""Behavioral tests for the ``flext_cli.constants`` public facade.

Every test asserts an invariant consumers depend on — mapping coverage,
template interpolation, glyph distinctness, and the runtime classification
behavior of the diagnostic classifiers. No owned value is restated as a
literal: the constants owner may change any value without breaking a test.

Modules tested: flext_cli.constants.FlextCliConstants (``c.Cli``)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum

import pytest
from flext_tests import tm

from tests import c, u


class TestsFlextCliConstants:
    """Public-contract behavior of the flext-cli constants facade."""

    @pytest.mark.parametrize(
        "enum_cls",
        [
            c.Cli.MessageTypes,
            c.Cli.OutputFormats,
            c.Cli.LogVerbosity,
            c.Cli.ServiceStatus,
            c.Cli.CommandStatus,
        ],
    )
    def test_enum_values_matches_member_values(self, enum_cls: type[StrEnum]) -> None:
        """u.enum_values returns exactly the frozenset of member .value strings."""
        values = u.enum_values(enum_cls)
        tm.that(
            values,
            eq=frozenset(member.value for member in enum_cls.__members__.values()),
        )

    def test_table_formats_is_mapping_keyed_by_tabular_format(self) -> None:
        """TABLE_FORMATS maps a subset of TabularFormat members to descriptions."""
        table_formats = c.Cli.TABLE_FORMATS
        tm.that(table_formats, is_=Mapping)
        tm.that(table_formats, empty=False)
        for key, description in table_formats.items():
            tm.that(key in c.Cli.TabularFormat, eq=True)
            tm.that(description, is_=str)
            tm.that(description, empty=False)

    @pytest.mark.parametrize(
        "message_map", [c.Cli.MESSAGE_STYLE_MAP, c.Cli.MESSAGE_EMOJI_MAP]
    )
    def test_message_maps_cover_every_message_type(
        self, message_map: Mapping[c.Cli.MessageTypes, object]
    ) -> None:
        """Style/emoji maps expose an entry for every MessageTypes member."""
        tm.that(set(message_map), eq=set(c.Cli.MessageTypes))

    def test_format_error_template_interpolates_placeholder(self) -> None:
        """A templated error message interpolates its named placeholder."""
        rendered = c.Cli.ERR_INVALID_OUTPUT_FORMAT.format(format="qzz")
        tm.that(rendered, contains="qzz")

    def test_status_emojis_are_distinct(self) -> None:
        """Each status emoji is a distinct non-empty glyph."""
        emojis = (
            c.Cli.EMOJI_SUCCESS,
            c.Cli.EMOJI_ERROR,
            c.Cli.EMOJI_WARNING,
            c.Cli.EMOJI_INFO,
            c.Cli.EMOJI_DEBUG,
        )
        for emoji in emojis:
            tm.that(emoji, empty=False)
        tm.that(len(set(emojis)), eq=len(emojis))

    def test_success_and_failure_symbols_differ(self) -> None:
        """Success and failure marks are different observable symbols."""
        tm.that(c.Cli.SYMBOL_SUCCESS_MARK, empty=False)
        tm.that(c.Cli.SYMBOL_SUCCESS_MARK != c.Cli.SYMBOL_FAILURE_MARK, eq=True)

    @pytest.mark.parametrize(
        ("message", "expected"),
        [
            ("No such file or directory", True),
            ("config.yml not found", True),
            ("path does not exist", True),
            ("[Errno 2] cannot open", True),
            ("everything is fine", False),
            ("permission denied", False),
        ],
    )
    def test_file_not_found_classifier(self, message: str, *, expected: bool) -> None:
        """u.Cli.file_not_found_error flags file-absence diagnostics only."""
        tm.that(u.Cli.file_not_found_error(message), eq=expected)

    @pytest.mark.parametrize(
        ("message", "expected"),
        [
            ("No such option: --bad", True),
            ("Missing argument 'NAME'", True),
            ("Got unexpected extra argument", True),
            ("CLI exited with code 2", True),
            ("everything is fine", False),
            ("No such file or directory", False),
        ],
    )
    def test_cli_usage_error_classifier(self, message: str, *, expected: bool) -> None:
        """u.Cli.cli_usage_error flags CLI-usage diagnostics only."""
        tm.that(u.Cli.cli_usage_error(message), eq=expected)
