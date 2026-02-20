from __future__ import annotations

import json
from pathlib import Path

import yaml

from flext_core import r

from flext_cli.constants import c
from flext_cli.settings import FlextCliSettings


def test_ensure_config_directory_error_path(monkeypatch) -> None:
    settings = FlextCliSettings()
    monkeypatch.setattr(
        Path,
        "mkdir",
        lambda self, parents=True, exist_ok=True: (_ for _ in ()).throw(
            PermissionError("no perm")
        ),
    )

    result = settings._ensure_config_directory()

    assert result.is_failure


def test_propagate_context_fail_and_recovery_paths(monkeypatch) -> None:
    settings = FlextCliSettings()

    class ModuleWithoutContext:
        pass

    monkeypatch.setattr(
        "flext_cli.settings.importlib.import_module",
        lambda _name: ModuleWithoutContext(),
    )
    fail_result = settings._propagate_to_context()
    assert fail_result.is_failure

    monkeypatch.setattr(
        "flext_cli.settings.importlib.import_module",
        lambda _name: (_ for _ in ()).throw(RuntimeError("ctx down")),
    )
    recovered = settings._propagate_to_context()
    assert recovered.is_success


def test_register_in_container_recovery_path(monkeypatch) -> None:
    settings = FlextCliSettings()
    monkeypatch.setattr(
        "flext_cli.settings.FlextContainer",
        lambda: (_ for _ in ()).throw(RuntimeError("container down")),
    )

    result = settings._register_in_container()

    assert result.is_success


def test_validate_configuration_raises_when_chain_fails(monkeypatch) -> None:
    settings = FlextCliSettings()
    monkeypatch.setattr(settings, "_ensure_config_directory", lambda: r.fail("boom"))

    raised = False
    try:
        settings.validate_configuration()
    except ValueError:
        raised = True
    assert raised


def test_computed_fields_error_and_branches(monkeypatch) -> None:
    settings = FlextCliSettings(no_color=False)

    monkeypatch.setattr("flext_cli.settings.os.isatty", lambda _fd: True)
    monkeypatch.setattr(
        "flext_cli.settings.FlextCliSettings._try_terminal_width", lambda _self: 50
    )
    assert settings.auto_output_format == "plain"
    assert settings.optimal_table_format == c.Cli.TableFormats.SIMPLE

    monkeypatch.setattr(
        "flext_cli.settings.FlextCliSettings._try_terminal_width", lambda _self: 100
    )
    assert settings.optimal_table_format == "github"

    monkeypatch.setattr(
        "flext_cli.settings.FlextCliSettings._try_terminal_width", lambda _self: None
    )
    assert settings.optimal_table_format == "simple"

    monkeypatch.setattr(
        "flext_cli.settings.os.isatty",
        lambda _fd: (_ for _ in ()).throw(RuntimeError("tty")),
    )
    assert settings.auto_output_format == "json"


def test_load_from_config_file_paths(tmp_path: Path) -> None:
    missing = FlextCliSettings.load_from_config_file(tmp_path / "missing.json")
    assert missing.is_failure

    unsupported = tmp_path / "cfg.txt"
    unsupported.write_text("x", encoding="utf-8")
    bad_suffix = FlextCliSettings.load_from_config_file(unsupported)
    assert bad_suffix.is_failure

    json_path = tmp_path / "cfg.json"
    json_path.write_text(json.dumps({"profile": "x"}), encoding="utf-8")
    ok_json = FlextCliSettings.load_from_config_file(json_path)
    assert ok_json.is_success

    yaml_path = tmp_path / "cfg.yaml"
    yaml_path.write_text(yaml.safe_dump({"profile": "y"}), encoding="utf-8")
    ok_yaml = FlextCliSettings.load_from_config_file(yaml_path)
    assert ok_yaml.is_success


def test_update_and_validate_overrides_error_paths(monkeypatch) -> None:
    settings = FlextCliSettings()

    update_result = settings.update_from_cli_args(max_width="bad")
    assert update_result.is_failure

    invalid = settings.validate_cli_overrides(max_width="bad")
    assert invalid.is_failure

    monkeypatch.setattr(
        FlextCliSettings,
        "model_copy",
        lambda self: (_ for _ in ()).throw(RuntimeError("copy fail")),
    )
    outer = settings.validate_cli_overrides(profile="x")
    assert outer.is_failure


def test_load_config_error_path(monkeypatch) -> None:
    settings = FlextCliSettings()

    monkeypatch.setattr(
        FlextCliSettings,
        "model_dump",
        lambda self, *args, **kwargs: (_ for _ in ()).throw(RuntimeError("dump fail")),
    )
    load_result = settings.load_config()
    assert load_result.is_failure


def test_save_config_error_path() -> None:
    settings = FlextCliSettings()

    save_result = settings.save_config({"max_width": "bad"})
    assert save_result.is_failure


def test_parse_bool_env_vars_string_and_fallback_paths() -> None:
    assert FlextCliSettings.parse_bool_env_vars("yes") is True
    assert FlextCliSettings.parse_bool_env_vars("off") is False
    assert FlextCliSettings.parse_bool_env_vars(1) is True


def test_computed_fields_remaining_branches() -> None:
    settings = FlextCliSettings(verbose=False, quiet=True, no_color=True)

    assert settings.auto_output_format in {"json", "table", "plain"}
    assert settings.auto_verbosity == c.Cli.CliGlobalDefaults.QUIET_VERBOSITY


def test_auto_output_format_wide_tty_table_branch(monkeypatch) -> None:
    settings = FlextCliSettings(no_color=False)

    monkeypatch.setattr("flext_cli.settings.os.isatty", lambda _fd: True)
    monkeypatch.setattr(
        "flext_cli.settings.FlextCliSettings._try_terminal_width", lambda _self: 200
    )

    assert settings.auto_output_format == c.Cli.OutputFormats.TABLE.value


def test_validate_cli_overrides_outer_exception_branch(monkeypatch) -> None:
    settings = FlextCliSettings()

    monkeypatch.setattr(
        "flext_cli.settings.hasattr",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("hasattr boom")),
        raising=False,
    )

    result = settings.validate_cli_overrides(profile="x")

    assert result.is_failure


def test_auto_output_format_wide_tty_no_color_returns_json(monkeypatch) -> None:
    settings = FlextCliSettings(no_color=True)

    monkeypatch.setattr("flext_cli.settings.os.isatty", lambda _fd: True)
    monkeypatch.setattr(
        "flext_cli.settings.FlextCliSettings._try_terminal_width", lambda _self: 200
    )

    assert settings.auto_output_format == c.Cli.OutputFormats.JSON.value
