"""Runtime settings for flext-cli tests."""

from __future__ import annotations

from flext_tests import FlextTestsSettings

from flext_cli import FlextCliSettings


class TestsFlextCliSettings(FlextCliSettings, FlextTestsSettings):
    """CLI settings extended with the shared test namespace."""


__all__: list[str] = ["TestsFlextCliSettings"]
