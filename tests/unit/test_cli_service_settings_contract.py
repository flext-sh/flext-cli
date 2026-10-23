"""Service settings contract for services built on the flext-cli service base.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from io import StringIO

import pytest
from flext_core import FlextContext
from structlog.contextvars import bound_contextvars

from flext_cli import FlextCli, settings
from tests import c, m, p, r, t, tm, u


@pytest.mark.usefixtures("preserve_logging")
class TestsFlextCliServiceSettingsContract:
    """A real CLI elects its injected Core policy without losing DI bindings."""

    @staticmethod
    def test_service_settings_satisfy_cli_settings() -> None:
        """The facade settings satisfy the CLI settings protocol and SSOT."""
        supplied = settings.clone()
        service = FlextCli.with_settings(supplied)
        resolved: p.Cli.Settings = service.settings
        tm.that(resolved, is_=p.Cli.Settings)
        tm.that(resolved.model_dump(), eq=supplied.model_dump())
        tm.ok(service.container.settings is resolved)
        status = tm.ok(service.execute())
        tm.that(status, is_=p.Cli.RuntimeStatus)
        tm.that(status.components, is_=p.Cli.RuntimeComponents)

    @staticmethod
    def _elected_native_composition(
        streams: t.Pair[StringIO, StringIO],
        records: t.MutableSequenceOf[p.LoggingRecord],
        stages: t.MutableSequenceOf[str],
        exception: BaseException,
        initial_context: p.Context | None = None,
    ) -> tuple[m.StructlogOptions, FlextCli, p.Cli.Application]:
        """Build a real service electing two native sinks sharing one stage.

        Returns:
            The elected options, the service, and its registered Typer app.

        """
        native_json, native_console = streams

        def enrich(
            logger: p.OutputLogger,
            method_name: str,
            event_dict: p.LoggingEvent,
        ) -> p.LoggingEvent:
            _ = logger, method_name
            if event_dict["event"] == "cli-native-event":
                stages.append("processed")
                event_dict["application_stage"] = "selected"
            return event_dict

        def observe(event: p.LoggingRecord) -> None:
            records.append(event)

        options = m.StructlogOptions(
            log_level=u.level_number(c.LogLevel.WARNING),
            handlers=(
                u.create_logging_handler(stream=native_json),
                u.create_logging_handler(
                    stream=native_console,
                    console_renderer=True,
                ),
            ),
            processing_stages=(enrich,),
            observers=(observe,),
        )
        service = FlextCli(
            runtime_settings=settings.clone(
                log_level=c.LogLevel.WARNING,
                debug=False,
                trace=False,
            ),
            initial_context=initial_context,
            logging_options=options,
        )
        app = service.create_app_with_common_params(
            name="native",
            help_text="Native",
        )

        def emit() -> bool:
            u.debug("cli-native-debug")
            u.failure("cli-native-event", exception=exception)
            u.Cli.commands_emit_success_message(
                '{"actual":"result"}',
                c.Cli.MessageTypes.SUCCESS,
            )
            return True

        service.register_command(app, name="emit", help_text="Emit", command=emit)
        return options, service, app

    def test_cli_severity_updates_flow_through_selected_native_sinks(self) -> None:
        """Severity updates keep both native sinks fed by one shared stage."""
        native_json = StringIO()
        native_console = StringIO()
        records: t.MutableSequenceOf[p.LoggingRecord] = []
        stages: t.MutableSequenceOf[str] = []
        original_exception = ValueError("selected cause")
        _options, service, app = self._elected_native_composition(
            (native_json, native_console),
            records,
            stages,
            exception=original_exception,
        )
        with bound_contextvars(correlation_id="cli-contract"):
            first = tm.ok(service.invoke_app(app, args=["--debug", "emit"]))
            second = tm.ok(
                service.invoke_app(app, args=["--log-level", c.LogLevel.ERROR, "emit"]),
            )

        for invocation in (first, second):
            tm.ok(u.Cli.process_succeeded(invocation.outcome))
            tm.that(
                m.ConfigMap.model_validate_json(invocation.stdout).root,
                eq={"actual": "result"},
            )
        emitted = [record for record in records if record.message == "cli-native-event"]
        tm.that(len(emitted), eq=2)
        tm.that(stages, eq=["processed", "processed"])
        tm.that(
            len([record for record in records if record.message == "cli-native-debug"]),
            eq=1,
        )
        for record in emitted:
            tm.that(record.context[c.ContextKey.CORRELATION_ID], eq="cli-contract")
            tm.that(record.context["application_stage"], eq="selected")
            tm.ok(record.exception is original_exception)
        native_events = [
            m.ConfigMap.model_validate_json(line).root
            for line in native_json.getvalue().splitlines()
        ]
        tm.that(
            len([
                event for event in native_events if event["event"] == "cli-native-event"
            ]),
            eq=len(emitted),
        )
        tm.that(native_console.getvalue().count("cli-native-event"), eq=len(emitted))

    def test_cli_severity_updates_preserve_selected_composition_and_di(self) -> None:
        """Executed invocations keep the elected composition and DI bindings."""
        singleton_before = settings.model_dump()
        native_json = StringIO()
        native_console = StringIO()
        records: t.MutableSequenceOf[p.LoggingRecord] = []
        stages: t.MutableSequenceOf[str] = []
        original_exception = ValueError("selected cause")
        original_context = FlextContext.create()
        options, service, app = self._elected_native_composition(
            (native_json, native_console),
            records,
            stages,
            exception=original_exception,
            initial_context=original_context,
        )
        selected_provider = m.ConfigMap(root={c.ContextScope.APPLICATION: "selected"})
        _ = service.container.bind("application-provider", selected_provider)
        original_dispatcher = tm.ok(service.container.dispatcher())
        with bound_contextvars(correlation_id="cli-contract"):
            invocation = tm.ok(service.invoke_app(app, args=["--debug", "emit"]))

        tm.ok(u.Cli.process_succeeded(invocation.outcome))
        tm.that(
            m.ConfigMap.model_validate_json(invocation.stdout).root,
            eq={"actual": "result"},
        )
        emitted = [record for record in records if record.message == "cli-native-event"]
        tm.that(len(emitted), eq=1)
        tm.that(stages, eq=["processed"])
        tm.ok(emitted[0].exception is original_exception)
        tm.ok(u.logging_options().handlers[0] is options.handlers[0])
        tm.ok(u.logging_options().handlers[1] is options.handlers[1])
        tm.that(
            u.logging_options().processing_stages[0] is options.processing_stages[0],
            eq=True,
        )
        tm.ok(u.logging_options().observers[0] is options.observers[0])
        tm.ok(service.logging_options is options)
        tm.fail("logging_options" in service.model_dump())
        tm.that(
            "logging_options"
            in service.model_json_schema(mode="serialization")["properties"],
            eq=False,
        )
        tm.ok(u.logging_settings() is service.settings)
        tm.ok(service.container.settings is service.settings)
        tm.ok(service.context is original_context)
        tm.ok(tm.ok(service.container.dispatcher()) is original_dispatcher)
        tm.that(
            tm.ok(service.container.resolve("application-provider"))
            is selected_provider,
            eq=True,
        )
        tm.that(settings.model_dump(), eq=singleton_before)

    @staticmethod
    def test_public_constructor_rejects_nonconforming_logging_port() -> None:
        """The model-owned native collaborator is validated at the API boundary."""
        with pytest.raises(c.ValidationError):
            _ = FlextCli.model_validate({"logging_options": "not a logging port"})

    @staticmethod
    @pytest.mark.parametrize(
        ("flags", "initial_level", "expected_level", "trace"),
        [
            (["--debug"], c.LogLevel.WARNING, c.LogLevel.DEBUG, False),
            (["--trace"], c.LogLevel.DEBUG, c.LogLevel.DEBUG, True),
            (["--verbose"], c.LogLevel.ERROR, c.LogLevel.ERROR, False),
            (
                ["--log-level", c.LogLevel.ERROR, "--debug", "--trace"],
                c.LogLevel.WARNING,
                c.LogLevel.ERROR,
                True,
            ),
        ],
    )
    def test_cli_flags_control_actual_emission_and_keep_original_failure(
        flags: t.StrSequence,
        initial_level: t.LogLevel,
        expected_level: t.LogLevel,
        capsys: pytest.CaptureFixture[str],
        *,
        trace: bool,
    ) -> None:
        """Explicit severity wins shorthand while trace controls failure detail."""
        service = FlextCli.with_settings(
            settings.clone(
                log_level=initial_level,
                debug=False,
                trace=False,
                cli_verbose=False,
            ),
        )
        records: t.MutableSequenceOf[p.LoggingRecord] = []

        def observe(event: p.LoggingRecord) -> None:
            records.append(event)

        u.configure_structlog(
            settings=m.StructlogOptions(async_logging=False, observers=(observe,)),
            runtime_settings=service.settings,
        )
        original_cause = ValueError("original CLI cause")
        with pytest.raises(ValueError, match="original CLI cause") as caught:
            raise original_cause
        failed = r[t.JsonPayload].fail(
            "cli-original-failure",
            exception=caught.value,
            error_code="selected_failure",
            error_data={"source": "cli"},
        )

        def fail(params: m.Tests.SampleInput) -> p.Result[t.JsonPayload]:
            u.debug("cli-debug-event", input_name=params.name)
            return failed

        app = service.create_app_with_common_params(name="policy", help_text="Policy")
        service.register_result_route(
            app,
            route=m.Cli.ResultCommandRoute(
                name="fail",
                help_text="Fail",
                model_cls=m.Tests.SampleInput,
                handler=fail,
            ),
        )
        outcome = service.execute_app(
            app,
            prog_name="policy",
            args=[*flags, "fail", "--name", "sample"],
        )

        tm.fail(outcome)
        tm.ok(outcome.exception is caught.value)
        tm.that(outcome.error_code, eq=failed.error_code)
        tm.that(outcome.error_data, eq=failed.error_data)
        tm.that(service.settings.log_level, eq=expected_level)
        tm.that(service.settings.trace, eq=trace)
        tm.that(service.settings.cli_verbose, eq="--verbose" in flags)
        if "--trace" in flags and "--debug" not in flags:
            tm.fail(service.settings.debug)
        debug_events = [
            record for record in records if record.message == "cli-debug-event"
        ]
        tm.that(bool(debug_events), eq=expected_level == c.LogLevel.DEBUG)
        failure_events = [
            record for record in records if record.message == "cli-original-failure"
        ]
        tm.that(len(failure_events), eq=1)
        tm.ok(failure_events[0].exception is caught.value)
        tm.that("stack_trace" in failure_events[0].context, eq=trace)
        captured = capsys.readouterr()
        tm.that(captured.out, eq="")
        tm.that(captured.err, has="cli-original-failure")

    @staticmethod
    def test_invalid_level_leaves_settings_and_business_effects_unchanged(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Rejected policy never rebinds DI or reaches the application command."""
        service = FlextCli.with_settings(settings.clone())
        provider = service.settings
        container = service.container
        before = provider.model_dump()
        options = m.StructlogOptions(async_logging=False)
        u.configure_structlog(settings=options, runtime_settings=provider)
        calls: t.MutableSequenceOf[str] = []
        app = service.create_app_with_common_params(name="invalid", help_text="Invalid")

        def execute() -> bool:
            calls.append("business effect")
            return True

        service.register_command(app, name="run", help_text="Run", command=execute)
        result = service.execute_app(
            app,
            prog_name="invalid",
            args=["--log-level", "INVALID", "--debug", "--verbose", "run"],
        )

        tm.fail(result)
        tm.that(result.exception, is_=ValueError)
        tm.that(calls, eq=[])
        tm.ok(service.settings is provider)
        tm.that(service.settings.model_dump(), eq=before)
        tm.ok(service.container is container)
        tm.ok(u.logging_settings() is provider)
        tm.ok(u.logging_options() is options)
        captured = capsys.readouterr()
        tm.that(captured.out, eq="")
        tm.that(captured.err, has="INVALID")

    @staticmethod
    @pytest.mark.parametrize(
        "output_format",
        [c.Cli.OutputFormats.JSON, c.Cli.OutputFormats.TABLE],
    )
    @pytest.mark.parametrize("profile", ["console", "json"])
    def test_result_stdout_remains_clean_with_selected_diagnostic_profile(
        output_format: c.Cli.OutputFormats,
        profile: str,
    ) -> None:
        """No-option invocations preserve app policy and separate result/diagnostics."""
        service = FlextCli.with_settings(
            settings.clone(
                log_level=c.LogLevel.WARNING,
                debug=False,
                trace=False,
                logging_profile=profile,
                cli_output_format=output_format,
            ),
        )
        provider = service.settings
        before = provider.model_dump()
        u.configure_structlog(
            settings=m.StructlogOptions(async_logging=False),
            runtime_settings=provider,
        )
        app = service.create_app_with_common_params(name="result", help_text="Result")

        def render() -> bool:
            u.warning("cli-only-diagnostic")
            if service.settings.cli_output_format == c.Cli.OutputFormats.JSON:
                u.Cli.commands_emit_success_message(
                    '{"actual":"result"}',
                    c.Cli.MessageTypes.SUCCESS,
                )
            else:
                service.show_table([{"actual": "result"}])
            return True

        service.register_command(app, name="render", help_text="Render", command=render)
        outcome = tm.ok(service.invoke_app(app, args=["render"]))

        tm.ok(u.Cli.process_succeeded(outcome.outcome))
        tm.ok(service.settings is provider)
        tm.that(service.settings.model_dump(), eq=before)
        tm.fail("cli-only-diagnostic" in outcome.stdout)
        tm.that(outcome.stderr, has="cli-only-diagnostic")
        if output_format == c.Cli.OutputFormats.JSON:
            tm.that(
                m.ConfigMap.model_validate_json(outcome.stdout).root,
                eq={"actual": "result"},
            )
        else:
            tm.that(outcome.stdout, has=["actual", "result"])
        if profile == "json":
            diagnostic = m.ConfigMap.model_validate_json(outcome.stderr).root
            tm.that(diagnostic["event"], eq="cli-only-diagnostic")
