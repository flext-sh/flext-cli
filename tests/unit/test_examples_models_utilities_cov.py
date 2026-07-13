"""Behavioral tests for public flext-cli example models and utilities.

Contract under test (public API only):
- ``m.Examples.MyAppSettings`` / ``AppSettingsAdvanced`` / ``AdvancedDatabaseConfig``
  construction, env-override merging, field validation, and ``validate_to_mapping``
  returning ``r[T]``.
- ``m.Examples.merge_env_overrides`` pure merge behavior.
- ``u.to_json_dict`` normalization and the void rendering helpers rendering without
  raising through their public signatures.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from flext_tests import tm

from flext_cli import cli

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

examples_pkg = importlib.import_module("examples")
c = examples_pkg.c
m = examples_pkg.m
u = examples_pkg.u


class TestsFlextCliExampleModelsUtilitiesCov:
    """Exercise the public examples model and utility contracts."""

    # ------------------------------------------------------------------
    # MyAppSettings: environment override contract
    # ------------------------------------------------------------------

    def test_my_app_settings_defaults_when_no_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for env_key in (
            c.EXAMPLE_ENV_KEY_APP_NAME,
            c.EXAMPLE_ENV_KEY_API_KEY,
            c.EXAMPLE_ENV_KEY_MAX_WORKERS,
            c.EXAMPLE_ENV_KEY_TIMEOUT,
        ):
            monkeypatch.delenv(env_key, raising=False)

        settings = m.Examples.MyAppSettings()

        tm.that(settings.app_name, eq=c.EXAMPLE_DEFAULT_TOOL_NAME)
        tm.that(settings.max_workers, eq=c.EXAMPLE_DEFAULT_MAX_WORKERS)
        tm.that(settings.timeout, eq=c.EXAMPLE_DEFAULT_TIMEOUT_SECONDS)

    def test_my_app_settings_reads_and_coerces_env_overrides(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_APP_NAME, "env-tool")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_API_KEY, "env-secret")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_MAX_WORKERS, "9")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_TIMEOUT, "45")

        settings = m.Examples.MyAppSettings()

        tm.that(settings.app_name, eq="env-tool")
        tm.that(settings.api_key, eq="env-secret")
        # Strings from the environment are coerced to the declared int fields.
        tm.that(settings.max_workers, eq=9)
        tm.that(settings.timeout, eq=45)

    def test_my_app_settings_explicit_arg_overrides_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_APP_NAME, "env-tool")

        settings = m.Examples.MyAppSettings(app_name="explicit-tool")

        # Explicit constructor input wins over the environment override.
        tm.that(settings.app_name, eq="explicit-tool")

    # ------------------------------------------------------------------
    # merge_env_overrides: pure merge behavior
    # ------------------------------------------------------------------

    def test_merge_env_overrides_applies_env_over_defaults(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_TIMEOUT, "77")

        merged = m.Examples.merge_env_overrides(
            {"timeout": 10}, {"timeout": c.EXAMPLE_ENV_KEY_TIMEOUT}, {"timeout": int}
        )

        # Explicit mapping value takes precedence over the env override.
        tm.that(merged, eq={"timeout": 10})

    def test_merge_env_overrides_fills_missing_field_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_TIMEOUT, "77")

        merged = m.Examples.merge_env_overrides(
            {}, {"timeout": c.EXAMPLE_ENV_KEY_TIMEOUT}, {"timeout": int}
        )

        tm.that(merged, eq={"timeout": 77})

    def test_merge_env_overrides_passes_non_mapping_through_unchanged(self) -> None:
        merged = m.Examples.merge_env_overrides(
            ["raw"], {"timeout": c.EXAMPLE_ENV_KEY_TIMEOUT}, {"timeout": int}
        )

        tm.that(merged, eq=["raw"])

    # ------------------------------------------------------------------
    # AppSettingsAdvanced.validate_to_mapping: r[T] outcomes
    # ------------------------------------------------------------------

    def test_advanced_settings_fail_when_api_key_missing_in_production(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv(
            c.EXAMPLE_ENV_KEY_ENVIRONMENT, c.EXAMPLE_ENV_VALUE_PRODUCTION
        )
        monkeypatch.setenv(
            c.EXAMPLE_ENV_KEY_TEMP_DIR, str(tmp_path / "created-temp-dir")
        )

        outcome = m.Examples.AppSettingsAdvanced().validate_to_mapping()

        tm.fail(outcome, has="API_KEY is required in production")

    def test_advanced_settings_fail_when_temp_dir_is_a_file(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        bad_temp_dir = tmp_path / "not-a-dir"
        bad_temp_dir.write_text("broken", encoding="utf-8")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_ENVIRONMENT, "development")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_TEMP_DIR, str(bad_temp_dir))

        outcome = m.Examples.AppSettingsAdvanced(
            api_key="valid-api-key"
        ).validate_to_mapping()

        tm.fail(outcome, has="TEMP_DIR must be a directory")

    def test_advanced_settings_success_masks_api_key(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        good_temp_dir = tmp_path / "temp-ok"
        monkeypatch.setenv(
            c.EXAMPLE_ENV_KEY_ENVIRONMENT, c.EXAMPLE_ENV_VALUE_PRODUCTION
        )
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_TEMP_DIR, str(good_temp_dir))

        mapping = tm.ok(
            m.Examples.AppSettingsAdvanced(api_key="super-secret").validate_to_mapping()
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
        self, monkeypatch: pytest.MonkeyPatch, kwargs: dict[str, str], match: str
    ) -> None:
        monkeypatch.delenv(c.EXAMPLE_ENV_KEY_ENVIRONMENT, raising=False)

        with pytest.raises(ValueError, match=match):
            m.Examples.AppSettingsAdvanced(**kwargs)

    @pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "db.example.com"])
    def test_database_config_accepts_valid_host(self, host: str) -> None:
        config = m.Examples.AdvancedDatabaseConfig(
            host=host, name="production", username="db-user", password="secret-pass"
        )

        tm.that(config.host, eq=host)

    def test_database_config_rejects_invalid_host(self) -> None:
        with pytest.raises(ValueError, match=c.EXAMPLE_ERR_INVALID_HOST):
            m.Examples.AdvancedDatabaseConfig(
                host="invalid-host",
                name="production",
                username="db-user",
                password="secret-pass",
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
        self, payload: dict[str, object], key: str, expected: object
    ) -> None:
        display = u.to_json_dict(payload)

        tm.that(display.data[key], eq=expected)

    def test_public_renderers_do_not_raise(self) -> None:
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
