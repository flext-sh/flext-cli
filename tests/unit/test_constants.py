"""Behavioral tests for the ``flext_cli.constants`` public facade.

Every test asserts an OBSERVABLE part of the constants contract that
consumers depend on: concrete values, enum membership, mapping coverage,
authority-tuple/enum agreement, and the runtime classification behavior
of the compiled regex authorities. No private attributes, no mocking of
internal collaborators — only the public ``c.Cli.*`` / ``u.*`` surface.

Modules tested: flext_cli.constants.FlextCliConstants (``c.Cli``)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum

import pytest
from flext_tests import tm

from tests import c
from tests import u


class TestsFlextCliConstants:
    """Public-contract behavior of the flext-cli constants facade."""

    # ---- identity / metadata contract -------------------------------------

    def test_cli_version_is_the_published_semver(self) -> None:
        """CLI_VERSION exposes the shipped 3-part semver string."""
        version = c.Cli.CLI_VERSION
        tm.that(version, eq="2.0.0")
        major, minor, patch = version.split(".")[:3]
        for part in (major, minor, patch):
            tm.that(part.isdigit(), eq=True)

    def test_flext_cli_identifier_value(self) -> None:
        """FLEXT_CLI names the distribution consumers key on."""
        tm.that(c.Cli.FLEXT_CLI, eq="flext-cli")

    def test_flext_dir_name_is_hidden_dotfile(self) -> None:
        """PATH_FLEXT_DIR_NAME is the hidden ``.flext`` home directory."""
        name = c.Cli.PATH_FLEXT_DIR_NAME
        tm.that(name, eq=".flext")
        tm.that(name.startswith("."), eq=True)

    def test_standard_subdirs_expose_cache_and_logs(self) -> None:
        """STANDARD_SUBDIRS enumerates exactly the managed subdirectories."""
        tm.that(c.Cli.STANDARD_SUBDIRS, eq=(c.Cli.SUBDIR_CACHE, c.Cli.SUBDIR_LOGS))
        tm.that(c.Cli.STANDARD_SUBDIRS, contains="cache")
        tm.that(c.Cli.STANDARD_SUBDIRS, contains="logs")

    # ---- default flags contract -------------------------------------------

    @pytest.mark.parametrize(
        "flag",
        [
            c.Cli.CLI_DEFAULT_VERBOSE,
            c.Cli.CLI_DEFAULT_QUIET,
            c.Cli.CLI_DEFAULT_NO_COLOR,
        ],
    )
    def test_cli_verbosity_flags_default_off(self, *, flag: bool) -> None:
        """Every CLI verbosity/color default ships disabled."""
        tm.that(flag, eq=False)

    # ---- enum value contract ----------------------------------------------

    @pytest.mark.parametrize(
        ("member", "expected"),
        [
            (c.Cli.ServiceStatus.OPERATIONAL, "operational"),
            (c.Cli.MessageTypes.INFO, "info"),
            (c.Cli.MessageTypes.ERROR, "error"),
            (c.Cli.MessageTypes.WARNING, "warning"),
            (c.Cli.MessageTypes.SUCCESS, "success"),
            (c.Cli.MessageTypes.DEBUG, "debug"),
            (c.Cli.LogVerbosity.COMPACT, "compact"),
            (c.Cli.LogVerbosity.DETAILED, "detailed"),
            (c.Cli.LogVerbosity.FULL, "full"),
            (c.Cli.OutputFormats.TABLE, "table"),
            (c.Cli.OutputFormats.JSON, "json"),
        ],
    )
    def test_enum_member_wire_value(self, member: str, expected: str) -> None:
        """StrEnum members serialize to their documented wire strings."""
        tm.that(member, eq=expected)

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
        tm.that(values, is_=frozenset)
        tm.that(
            values,
            eq=frozenset(member.value for member in enum_cls.__members__.values()),
        )

    def test_enum_values_is_cached_idempotent(self) -> None:
        """Repeated u.enum_values calls yield an equal, stable frozenset."""
        first = u.enum_values(c.Cli.MessageTypes)
        second = u.enum_values(c.Cli.MessageTypes)
        tm.that(first, eq=second)

    # ---- authority tuple <-> enum agreement -------------------------------

    def test_output_formats_authority_mirrors_enum(self) -> None:
        """OUTPUT_FORMATS is the ordered tuple of OutputFormats members."""
        tm.that(c.Cli.OUTPUT_FORMATS, eq=tuple(c.Cli.OutputFormats))

    def test_message_types_authority_mirrors_enum(self) -> None:
        """MESSAGE_TYPES is the ordered tuple of MessageTypes members."""
        tm.that(c.Cli.MESSAGE_TYPES, eq=tuple(c.Cli.MessageTypes))

    def test_log_levels_authority_contract(self) -> None:
        """LOG_LEVELS lists the canonical logging severities in order."""
        tm.that(c.Cli.LOG_LEVELS, eq=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"))

    # ---- output defaults resolve to enum members --------------------------

    def test_output_defaults_point_at_enum_members(self) -> None:
        """Output defaults reuse the canonical enum members, not loose strings."""
        tm.that(c.Cli.OUTPUT_DEFAULT_FORMAT_TYPE, eq=c.Cli.OutputFormats.TABLE)
        tm.that(c.Cli.OUTPUT_DEFAULT_MESSAGE_TYPE, eq=c.Cli.MessageTypes.INFO)

    # ---- message map coverage invariants ----------------------------------

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

    # ---- error message templates ------------------------------------------

    def test_static_error_message_is_populated(self) -> None:
        """A static error message exposes stable non-empty text."""
        tm.that(c.Cli.ERR_AUTH_FILE_NOT_FOUND, eq="Token file does not exist")

    def test_format_error_template_interpolates_placeholder(self) -> None:
        """A templated error message interpolates its named placeholder."""
        rendered = c.Cli.ERR_INVALID_OUTPUT_FORMAT.format(format="qzz")
        tm.that(rendered, contains="qzz")

    # ---- visual glyph distinctness ----------------------------------------

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
        tm.that(c.Cli.SYMBOL_SUCCESS_MARK, eq="✓")
        tm.that(c.Cli.SYMBOL_FAILURE_MARK, eq="✗")
        tm.that(c.Cli.SYMBOL_SUCCESS_MARK != c.Cli.SYMBOL_FAILURE_MARK, eq=True)

    # ---- regex authority classification behavior --------------------------

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

    def test_regex_authorities_agree_with_classifier_helpers(self) -> None:
        """Compiled regex tuples and their helper wrappers classify consistently."""
        fnf_hit = any(
            pattern.search("No such file or directory")
            for pattern in c.Cli.FILE_NOT_FOUND_REGEXES
        )
        usage_hit = any(
            pattern.search("No such option: --bad")
            for pattern in c.Cli.CLI_USAGE_ERROR_REGEXES
        )
        tm.that(fnf_hit, eq=True)
        tm.that(usage_hit, eq=True)
        tm.that(u.Cli.file_not_found_error("No such file or directory"), eq=True)
        tm.that(u.Cli.cli_usage_error("No such option: --bad"), eq=True)
