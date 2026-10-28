"""Service base for flext-cli tests.

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

from typing import override

from flext_tests import FlextTestsServiceBase

from tests import TestsFlextCliSettings, m, p


class TestsFlextCliServiceBase[TDomainResult: p.Base](
    FlextTestsServiceBase[TDomainResult],
):
    """CLI test service base with source and test settings namespaces."""

    # NOTE (multi-agent, mro-wkii.19.4): flext-tests owns fetch_settings;
    # this project declares only its more-specific bootstrap settings type.
    @classmethod
    @override
    def runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextCliSettings)


s = TestsFlextCliServiceBase

__all__: list[str] = ["TestsFlextCliServiceBase", "s"]
