"""Behavioral tests for JSON-carried options of ``cli.model_command``.

A model field without a native CLI form (a mapping, a nested model, or a
collection of them) is exposed as one option carrying JSON text that Pydantic
validates into the field's declared type. Every assertion registers the
generated command in a real app and observes it through ``cli.invoke_app`` or
``cli.execute_app``; nothing is patched or introspected.
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import c, cli
from tests import m, p, t, u


class TestsFlextCliModelCommandJsonOptions:
    """Mapping and nested-model fields travel as validated JSON options."""

    class MappingModel(m.BaseModel):
        """Request whose only field is a required mapping."""

        labels: dict[str, int]

    class NestedModel(m.BaseModel):
        """Request carrying a nested model and a sequence of nested models."""

        prefs: m.Tests.UserPreferences
        others: list[m.Tests.UserPreferences] = m.Field(default_factory=list)

    class JsonDefaultsModel(m.BaseModel):
        """Request whose JSON options all carry defaults."""

        labels: t.MappingKV[str, int] = m.Field(
            default_factory=lambda: {"seed": 1}, description="Label weights."
        )
        prefs: m.Tests.UserPreferences = m.Field(
            default_factory=lambda: m.Tests.UserPreferences(
                theme="light", notifications=False
            )
        )

    @staticmethod
    def _app[M: t.Cli.ModelLike](
        model_cls: t.ModelClass[M],
        received: list[M],
        *,
        settings: t.Cli.ModelLike | None = None,
    ) -> p.Cli.Application:
        """Register the model command in a real app that records its input."""

        def _capture(params: M) -> bool:
            received.append(params)
            return True

        app = cli.create_app_with_common_params(name="json-app", help_text="JSON app")
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(model_cls, _capture, settings=settings),
        )
        return app

    def _invoke[M: t.Cli.ModelLike](
        self,
        model_cls: t.ModelClass[M],
        args: t.StrSequence,
        *,
        settings: t.Cli.ModelLike | None = None,
    ) -> tuple[m.Cli.InvocationResult, list[M]]:
        received: list[M] = []
        app = self._app(model_cls, received, settings=settings)
        invocation = cli.invoke_app(app, args=["run", *args])
        tm.ok(invocation)
        return invocation.value, received

    @staticmethod
    def _json(value: t.JsonPayload) -> str:
        return u.to_json(value).decode()

    def test_mapping_option_json_reaches_model(self) -> None:
        """A JSON object passed to a mapping option is the model's mapping."""
        expected = self.MappingModel(labels={"alpha": 1, "beta": 2})
        invocation, received = self._invoke(
            self.MappingModel, ["--labels", self._json(expected.labels)]
        )
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received, eq=[expected])

    def test_nested_model_options_json_reach_model(self) -> None:
        """Nested models and their sequences validate from JSON options."""
        expected = self.NestedModel(
            prefs=m.Tests.UserPreferences(theme="dark", notifications=True),
            others=[m.Tests.UserPreferences(theme="solar", notifications=False)],
        )
        invocation, received = self._invoke(
            self.NestedModel,
            [
                "--prefs",
                self._json(expected.prefs),
                "--others",
                self._json(expected.others),
            ],
        )
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received, eq=[expected])

    def test_omitted_json_options_deliver_model_defaults(self) -> None:
        """Omitted JSON options deliver the model's own defaults."""
        invocation, received = self._invoke(self.JsonDefaultsModel, [])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received, eq=[self.JsonDefaultsModel()])

    def test_omitted_json_options_take_settings_values(self) -> None:
        """A settings model seeds omitted JSON options with its values."""
        settings = self.JsonDefaultsModel(
            labels={"from-settings": 7},
            prefs=m.Tests.UserPreferences(theme="settings", notifications=True),
        )
        invocation, received = self._invoke(
            self.JsonDefaultsModel, [], settings=settings
        )
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(received, eq=[settings])

    @pytest.mark.parametrize(
        ("raw", "error_type"),
        [("{not json", "json_invalid"), ('{"alpha": "one"}', "int_parsing")],
    )
    def test_invalid_json_option_fails_loud_with_cause(
        self, raw: str, error_type: str
    ) -> None:
        """Malformed JSON or a schema mismatch fails before the handler runs."""
        invocation, received = self._invoke(self.MappingModel, ["--labels", raw])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=False)
        tm.that(received, empty=True)

        executed: list[TestsFlextCliModelCommandJsonOptions.MappingModel] = []
        app = self._app(self.MappingModel, executed)
        result = cli.execute_app(
            app, prog_name="json-app", args=["run", "--labels", raw]
        )
        tm.fail(result, has=error_type)
        tm.that(executed, empty=True)

    def test_help_renders_json_options(self) -> None:
        """Help renders every JSON option with the JSON format marker."""
        invocation, received = self._invoke(self.JsonDefaultsModel, ["--help"])
        tm.that(u.Cli.process_succeeded(invocation.outcome), eq=True)
        tm.that(invocation.stdout, has=["--labels", "--prefs"])
        tm.that(invocation.stdout, has=c.Cli.CLI_JSON_OPTION_METAVAR)
        tm.that(received, empty=True)
