"""Service base for flext-cli tests."""

from __future__ import annotations

from typing import override

from flext_tests import s as tests_s

from flext_cli import m
from tests.settings import TestsFlextCliSettings


class TestsFlextCliServiceBase(tests_s):
    """CLI test service base with source and test settings namespaces."""

    # NOTE (multi-agent, mro-wkii.19.4): flext-tests owns fetch_settings;
    # this project declares only its more-specific bootstrap settings type.
    @classmethod
    @override
    def _runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextCliSettings)


s = TestsFlextCliServiceBase

__all__: list[str] = ["TestsFlextCliServiceBase", "s"]
