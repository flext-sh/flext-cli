"""Coverage tests for public flext-cli example models and utilities."""

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

    def test_example_models_apply_env_overrides_and_display(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_APP_NAME, "env-tool")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_API_KEY, "env-secret")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_MAX_WORKERS, "9")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_TIMEOUT, "45")

        settings = m.Examples.MyAppSettings()

        tm.that(settings.app_name, eq="env-tool")
        tm.that(settings.api_key, eq="env-secret")
        tm.that(settings.max_workers, eq=9)
        tm.that(settings.timeout, eq=45)

        merged = m.Examples.merge_env_overrides(
            {"timeout": 10},
            {"timeout": c.EXAMPLE_ENV_KEY_TIMEOUT},
            {"timeout": int},
        )
        tm.that(merged["timeout"], eq=10)
        tm.that(
            m.Examples.merge_env_overrides(
                ["raw"],
                {"timeout": c.EXAMPLE_ENV_KEY_TIMEOUT},
                {"timeout": int},
            ),
            eq=["raw"],
        )

        settings.display(cli)

        database = m.Examples.AdvancedDatabaseConfig(
            host="127.0.0.1",
            name="production",
            username="db-user",
            password="secret-pass",
        )
        tm.that(database.host, eq="127.0.0.1")

    def test_example_models_report_validation_failures(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        monkeypatch.setenv(
            c.EXAMPLE_ENV_KEY_ENVIRONMENT, c.EXAMPLE_ENV_VALUE_PRODUCTION
        )
        monkeypatch.setenv(
            c.EXAMPLE_ENV_KEY_TEMP_DIR,
            str(tmp_path / "created-temp-dir"),
        )

        production_settings = m.Examples.AppSettingsAdvanced()
        missing_api_key = production_settings.validate_to_mapping()
        tm.fail(missing_api_key)

        bad_temp_dir = tmp_path / "not-a-dir"
        bad_temp_dir.write_text("broken", encoding="utf-8")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_ENVIRONMENT, "development")
        monkeypatch.setenv(c.EXAMPLE_ENV_KEY_TEMP_DIR, str(bad_temp_dir))
        broken_settings = m.Examples.AppSettingsAdvanced(
            api_key="valid-api-key",
        )
        broken_temp = broken_settings.validate_to_mapping()
        tm.fail(broken_temp)

        with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
            m.Examples.AppSettingsAdvanced(log_level="verbose")

        with pytest.raises(ValueError, match=c.EXAMPLE_ERR_INVALID_HOST):
            m.Examples.AdvancedDatabaseConfig(
                host="invalid-host",
                name="production",
                username="db-user",
                password="secret-pass",
            )

    def test_example_utilities_build_and_render_public_payloads(self) -> None:
        payload = u.to_json_dict({"workers": 4, "enabled": True})

        tm.that(payload.data["workers"], eq=4)
        tm.that(payload.data["enabled"], eq=True)

        u.display_config_table(payload)
        u.display_config_table(
            m.Examples.MyAppSettings(
                app_name="demo",
                api_key="demo-secret",
                max_workers=4,
                timeout=30,
            )
        )
        u.print_demo_completion("Demo", ("feature-a", "feature-b"))
        u.display_success_summary(
            "Database configuration",
            m.Cli.SuccessSummaryDetails({
                "host": "db.example.com",
                "port": "5432",
            }),
        )
