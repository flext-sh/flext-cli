"""Behavioral tests for public flext-cli example models and utilities.

Contract under test (public API only):
- ``m.Examples.MyAppSettings`` / ``AppSettingsAdvanced`` / ``AdvancedDatabaseConfig``
  construction, field validation, and ``validate_to_mapping`` returning ``r[T]``.
- ``u.to_json_dict`` normalization and the void rendering helpers rendering without
  raising through their public signatures.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from examples import c, m, u
from flext_cli import cli
from flext_tests import tm
from tests import c as tc, t


class TestsFlextCliExampleModelsUtilitiesCov:
    """Exercise the public examples model and utility contracts."""

    # ------------------------------------------------------------------
    # MyAppSettings: explicit typed input contract
    # ------------------------------------------------------------------

    def test_my_app_settings_uses_canonical_defaults(self) -> None:
        """Build the pure model without reading ambient process state."""
        settings = m.Examples.MyAppSettings()

        tm.that(settings.app_name, eq=c.EXAMPLE_DEFAULT_TOOL_NAME)
        tm.that(settings.max_workers, eq=c.EXAMPLE_DEFAULT_MAX_WORKERS)
        tm.that(settings.timeout, eq=c.EXAMPLE_DEFAULT_TIMEOUT_SECONDS)

    def test_my_app_settings_accepts_explicit_typed_values(self) -> None:
        """Explicit values cross the model boundary without ambient overrides."""
        settings = m.Examples.MyAppSettings(
            app_name="explicit-tool",
            api_key="explicit-secret",
            max_workers=9,
            timeout=45,
        )

        tm.that(settings.app_name, eq="explicit-tool")
        tm.that(settings.api_key, eq="explicit-secret")
        tm.that(settings.max_workers, eq=9)
        tm.that(settings.timeout, eq=45)

    # ------------------------------------------------------------------
    # AppSettingsAdvanced.validate_to_mapping: r[T] outcomes
    # ------------------------------------------------------------------

    def test_advanced_settings_fail_when_api_key_missing_in_production(
        self, tmp_path: Path
    ) -> None:
        """Verify that advanced settings fail when api key missing in production."""
        outcome = m.Examples.AppSettingsAdvanced(
            environment=c.DeploymentEnvironment.PRODUCTION,
            temp_dir=tmp_path / "created-temp-dir",
        ).validate_to_mapping()

        tm.fail(outcome, has="API_KEY is required in production")

    def test_advanced_settings_fail_when_temp_dir_is_a_file(
        self, tmp_path: Path
    ) -> None:
        """Verify that advanced settings fail when temp dir is a file."""
        bad_temp_dir = tmp_path / "not-a-dir"
        bad_temp_dir.write_text("broken", encoding="utf-8")
        outcome = m.Examples.AppSettingsAdvanced(
            api_key="valid-api-key", temp_dir=bad_temp_dir
        ).validate_to_mapping()

        tm.fail(outcome, has="TEMP_DIR must be a directory")

    def test_advanced_settings_success_masks_api_key(self, tmp_path: Path) -> None:
        """Verify that advanced settings success masks api key."""
        good_temp_dir = tmp_path / "temp-ok"
        mapping: t.JsonMapping = tm.ok(
            m.Examples.AppSettingsAdvanced(
                api_key="super-secret",
                environment=c.DeploymentEnvironment.PRODUCTION,
                temp_dir=good_temp_dir,
            ).validate_to_mapping()
        )

        # Success payload masks the secret and creates the temp directory.
        tm.that(mapping["api_key"], eq="***")
        tm.that(mapping["temp_dir"], eq=str(good_temp_dir))
        tm.that(good_temp_dir.is_dir(), eq=True)

    # ------------------------------------------------------------------
    # Field validation raises from the model boundary
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("kwargs", "match"),
        [
            ({"log_level": "verbose"}, "LOG_LEVEL must be one of"),
            ({"database_url": "http://nope"}, c.EXAMPLE_ERR_INVALID_DB_URL),
            ({"redis_url": "http://nope"}, c.EXAMPLE_ERR_INVALID_REDIS_URL),
        ],
    )
    def test_advanced_settings_rejects_invalid_field(
        self, kwargs: dict[str, str], match: str
    ) -> None:
        """Verify that advanced settings rejects invalid field."""
        with pytest.raises(ValueError, match=match):
            m.Examples.AppSettingsAdvanced(**kwargs)

    @pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "db.example.com"])
    def test_database_config_accepts_valid_host(self, host: str) -> None:
        """Verify that database config accepts valid host."""
        config = m.Examples.AdvancedDatabaseConfig(
            host=host,
            name="production",
            username="db-user",
            password=tc.Tests.CREDENTIAL_SAMPLE_VALUE,
        )

        tm.that(config.host, eq=host)

    def test_database_config_rejects_invalid_host(self) -> None:
        """Verify that database config rejects invalid host."""
        with pytest.raises(ValueError, match=c.EXAMPLE_ERR_INVALID_HOST):
            m.Examples.AdvancedDatabaseConfig(
                host="invalid-host",
                name="production",
                username="db-user",
                password=tc.Tests.CREDENTIAL_SAMPLE_VALUE,
            )

    # ------------------------------------------------------------------
    # Utilities: to_json_dict normalization + void renderers
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        ("payload", "key", "expected"),
        [
            ({"workers": 4, "enabled": True}, "workers", 4),
            ({"workers": 4, "enabled": True}, "enabled", True),
            ({"name": "demo"}, "name", "demo"),
        ],
    )
    def test_to_json_dict_preserves_values(
        self, payload: t.JsonMapping, key: str, expected: t.JsonValue
    ) -> None:
        """Verify that to json dict preserves values."""
        display = u.to_json_dict(payload)

        tm.that(display.data[key] == expected, eq=True)

    def test_public_renderers_do_not_raise(self) -> None:
        """Verify that public renderers do not raise."""
        settings = m.Examples.MyAppSettings(
            app_name="demo", api_key="demo-secret", max_workers=4, timeout=30
        )

        # Void public rendering helpers must complete through their public
        # signatures without raising.
        settings.display(cli)
        u.display_config_table(u.to_json_dict({"workers": 4}))
        u.display_config_table(settings)
        u.print_demo_completion("Demo", ("feature-a", "feature-b"))
        u.display_success_summary(
            "Database configuration",
            m.Cli.SuccessSummaryDetails({"host": "db.example.com", "port": "5432"}),
        )
