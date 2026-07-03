"""FLEXT CLI base-behavior tests through the public facade.

Tests the shared service-base guarantees via the public ``cli`` facade:
instantiation, configuration access, and singleton settings behavior.

Modules tested: flext_cli.api.cli
Scope: Shared base-service functionality exposed by the public facade

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from flext_cli import cli
from tests.base import s
from tests.models import m
from tests.protocols import p


class TestsFlextCliServiceBaseBehavior:
    """Verify base-service guarantees through the public CLI facade."""

    def test_service_base_initialization(self) -> None:
        """Test the public CLI facade can be instantiated cleanly."""
        service = type(cli)()
        tm.that(service, none=False)
        tm.that(service, is_=type(cli))

    def test_settings_property(self) -> None:
        """Test settings property returns the public CLI settings singleton."""
        service = type(cli)()
        settings = service.settings
        tm.that(settings, none=False)
        tm.that(settings, is_=p.Cli.Settings)
        config2 = service.settings
        tm.that(settings is config2, eq=True)

    def test_config_singleton_consistency(self) -> None:
        """Test that settings returns same singleton across instances."""
        service1 = type(cli)()
        service2 = type(cli)()
        tm.that(service1.settings is service2.settings, eq=True)

    def test_test_service_settings_tree(self) -> None:
        """Test base helper should expose the CLI+Tests namespaced settings tree."""
        settings = s.fetch_settings()
        tm.that(settings, is_=p.Cli.Settings)
        assert isinstance(settings.Cli, m.SettingsValue)
        assert isinstance(settings.Tests, m.SettingsValue)
