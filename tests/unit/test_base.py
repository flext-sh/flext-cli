"""Behavioral tests for the FLEXT CLI service base through the public facade.

Exercises the OBSERVABLE public contract of the ``cli`` facade
(``flext_cli.api.FlextCli``): clean instantiation, the settings singleton
contract, the fresh-settings factory contract, and the ``r[T]`` outcomes of
the settings validation / snapshot operations. Also verifies the test service
base exposes the CLI+Tests namespaced settings tree.

Modules tested: flext_cli.api (public ``cli`` facade), tests.base
Scope: Public base-service behavior — no private attributes, no internal spies.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import FlextCli, cli
from tests.base import s
from tests.models import m
from tests.protocols import p


class TestsFlextCliBase:
    """Verify base-service public guarantees through the CLI facade."""

    @pytest.fixture
    def facade(self) -> FlextCli:
        """Return a fresh instance of the public CLI facade type."""
        return type(cli)()

    def test_facade_instantiates_as_its_own_type(self) -> None:
        """A freshly constructed facade is a usable instance of the facade type."""
        service = type(cli)()
        tm.that(service, none=False)
        tm.that(service, is_=type(cli))

    def test_settings_property_returns_typed_settings(self, facade: FlextCli) -> None:
        """`settings` returns an object satisfying the public Cli settings protocol."""
        settings = facade.settings
        tm.that(settings, none=False)
        tm.that(settings, is_=p.Cli.Settings)

    def test_settings_property_is_stable_within_instance(
        self, facade: FlextCli
    ) -> None:
        """Repeated `settings` reads return the same singleton (idempotent access)."""
        first = facade.settings
        second = facade.settings
        assert first is second

    def test_settings_singleton_shared_across_instances(self) -> None:
        """Two independent facades observe the same shared settings singleton."""
        service1 = type(cli)()
        service2 = type(cli)()
        assert service1.settings is service2.settings

    def test_new_settings_returns_fresh_typed_instances(self, facade: FlextCli) -> None:
        """`new_settings` is a factory: each call yields a distinct typed instance."""
        first = facade.new_settings()
        second = facade.new_settings()
        tm.that(first, is_=p.Cli.Settings)
        tm.that(second, is_=p.Cli.Settings)
        assert first is not second
        assert first is not facade.settings

    def test_validate_settings_reports_success_outcome(self, facade: FlextCli) -> None:
        """`validate_settings` returns a successful r[bool] carrying True."""
        result = facade.validate_settings()
        assert result.success
        assert result.unwrap() is True

    def test_settings_snapshot_exposes_public_state(self, facade: FlextCli) -> None:
        """`settings_snapshot` returns r[Snapshot] whose public fields are populated."""
        result = facade.settings_snapshot()
        assert result.success
        snapshot = result.unwrap()
        dumped = snapshot.model_dump()
        assert set(dumped) >= {
            "settings_dir",
            "settings_exists",
            "settings_readable",
            "settings_writable",
            "timestamp",
        }
        assert isinstance(snapshot.settings_exists, bool)
        assert isinstance(snapshot.settings_dir, str)
        assert snapshot.settings_dir

    def test_snapshot_map_composes_over_success(self, facade: FlextCli) -> None:
        """The r[T] snapshot value flows through `map` without losing success."""
        directory = facade.settings_snapshot().map(lambda snap: snap.settings_dir)
        assert directory.success
        assert directory.unwrap() == facade.settings_snapshot().unwrap().settings_dir

    @pytest.mark.parametrize("namespace", ["Cli", "Tests"])
    def test_service_base_exposes_namespaced_settings_tree(
        self, namespace: str
    ) -> None:
        """The test service base surfaces both Cli and Tests settings namespaces."""
        settings = s.fetch_settings()
        tm.that(settings, is_=p.Cli.Settings)
        section = getattr(settings, namespace)
        assert isinstance(section, m.SettingsValue)
