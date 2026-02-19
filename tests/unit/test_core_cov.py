from __future__ import annotations

from collections.abc import Mapping

from flext_core import r

from flext_cli.models import m
from flext_cli.services.core import FlextCliCore


def test_cache_stats_hit_miss_and_rate() -> None:
    stats = FlextCliCore._CacheStats()
    assert stats.get_hit_rate() == 0.0

    stats.record_miss()
    stats.record_hit(1.5)

    assert stats.cache_hits == 1
    assert stats.cache_misses == 1
    assert stats.total_time_saved == 1.5
    assert stats.get_hit_rate() == 0.5


def test_get_command_missing_and_invalid_type_paths() -> None:
    core = FlextCliCore()
    object.__setattr__(core, "_commands", {"present": {"name": "present"}})
    import flext_cli.services.core as core_module

    original_mapper = core_module.u.mapper
    core_module.u.mapper = lambda: type(
        "M", (), {"get": staticmethod(lambda *_a, **_k: None)}
    )()
    missing = core.get_command("missing")
    assert missing.is_failure
    core_module.u.mapper = original_mapper

    object.__setattr__(core, "_commands", {"bad": "oops"})
    invalid = core.get_command("bad")
    assert invalid.is_failure


def test_build_execution_context_fallback_and_execute_exception(monkeypatch) -> None:
    core = FlextCliCore()
    assert core._build_execution_context(123) == {}

    object.__setattr__(core, "_commands", {"ok": {"name": "ok"}})
    monkeypatch.setattr(
        core,
        "_build_execution_context",
        lambda _ctx: (_ for _ in ()).throw(RuntimeError("ctx boom")),
    )
    result = core.execute_command("ok")
    assert result.is_failure


def test_validate_and_update_configuration_error_paths(monkeypatch) -> None:
    core = FlextCliCore()

    invalid = core._validate_config_input("nope")
    assert invalid.is_failure

    not_mapping = core.update_configuration("nope")
    assert not_mapping.is_failure

    object.__setattr__(core, "_cli_config", {"a": 1})
    monkeypatch.setattr(
        "flext_cli.services.core.FlextCliUtilities.merge",
        lambda *_args, **_kwargs: r.fail("merge failed"),
    )
    merge_fail = core._merge_configurations({"b": 2})
    assert merge_fail.is_failure

    monkeypatch.setattr(
        core,
        "_validate_existing_config",
        lambda: (_ for _ in ()).throw(RuntimeError("merge boom")),
    )
    merge_exc = core._merge_configurations({"b": 2})
    assert merge_exc.is_failure


def test_get_configuration_failure_branches(monkeypatch) -> None:
    core = FlextCliCore()
    object.__setattr__(core, "_cli_config", "bad")
    not_initialized = core.get_configuration()
    assert not_initialized.is_failure

    monkeypatch.setattr(
        "flext_cli.services.core.u.is_type",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("is_type boom")),
    )
    exception_path = core.get_configuration()
    assert exception_path.is_failure


def test_create_profile_and_session_failure_branches(monkeypatch) -> None:
    core = FlextCliCore()
    object.__setattr__(core, "_cli_config", {"profiles": {}})

    monkeypatch.setattr(
        "flext_cli.services.core.FlextCliUtilities.extract",
        lambda *_args, **_kwargs: r.fail("extract fail"),
    )
    profile_extract_fail = core.create_profile("p", {"x": 1})
    assert profile_extract_fail.is_failure

    object.__setattr__(core, "_cli_config", 123)
    profile_exc = core.create_profile("p", {"x": 1})
    assert profile_exc.is_failure

    object.__setattr__(core, "_cli_config", {"profiles": {}})
    monkeypatch.setattr(
        "flext_cli.services.core.FlextCliUtilities.extract",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("extract boom")),
    )
    profile_exception = core.create_profile("p", {"x": 1})
    assert profile_exception.is_failure

    object.__setattr__(core, "_session_active", False)
    monkeypatch.setattr(
        "flext_cli.services.core.FlextLogger.info",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("log fail")),
    )
    session_fail = core.start_session()
    assert session_fail.is_failure


def test_end_session_success_and_followup_failures() -> None:
    import builtins

    core = FlextCliCore()
    object.__setattr__(core, "_session_active", True)
    object.__setattr__(core, "_sessions", {})
    object.__setattr__(core, "_session_start_time", "2020-01-01T00:00:00")

    original_delattr = builtins.delattr
    builtins.delattr = lambda *_args, **_kwargs: None

    ended = core.end_session()
    assert ended.is_success

    builtins.delattr = original_delattr

    no_active = core.end_session()
    assert no_active.is_failure


def test_statistics_and_service_info_failure_branches(monkeypatch) -> None:
    core = FlextCliCore()

    monkeypatch.setattr(
        m.Cli,
        "CommandStatistics",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("stats boom")),
    )
    cmd_stats = core.get_command_statistics()
    assert cmd_stats.is_failure

    monkeypatch.setattr(
        "flext_cli.services.core.FlextCliUtilities.generate",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("gen boom")),
    )
    info = core.get_service_info()
    assert "message" in info


def test_session_statistics_and_execute_failure_branches(monkeypatch) -> None:
    core = FlextCliCore()
    object.__setattr__(core, "_session_active", False)
    inactive = core.get_session_statistics()
    assert inactive.is_failure

    object.__setattr__(core, "_session_active", True)
    object.__setattr__(core, "_session_start_time", "not-iso")
    active_fail = core.get_session_statistics()
    assert active_fail.is_failure

    object.__setattr__(core, "_commands", {"x": {"k": "v"}})
    monkeypatch.setattr(
        m.Cli,
        "ServiceExecutionResult",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("execute boom")),
    )
    execute_fail = core.execute()
    assert execute_fail.is_failure


def test_get_config_and_get_dict_keys_exception_paths() -> None:
    core = FlextCliCore()

    class BoolBoom:
        def __bool__(self) -> bool:
            raise RuntimeError("bool boom")

    object.__setattr__(core, "_cli_config", BoolBoom())
    config_fail = core.get_config()
    assert config_fail.is_failure

    class BadMapping(Mapping[str, object]):
        def __getitem__(self, key: str) -> object:
            raise KeyError(key)

        def __iter__(self):
            return iter([])

        def __len__(self) -> int:
            return 0

        def keys(self):
            raise RuntimeError("keys boom")

    keys_fail = FlextCliCore._get_dict_keys(BadMapping(), "err: {error}")
    assert keys_fail.is_failure
