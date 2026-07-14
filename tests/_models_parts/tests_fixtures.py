"""Concrete field-only models for flext-cli public contract fixtures."""

from __future__ import annotations

from typing import Annotated

from flext_cli import m


class TestsFlextCliModelsFixtures:
    """Consumer-owned immutable records used by public integration flows."""

    # mro-wkii.17.26 (codex): own CLI field-metadata fixtures as validated data.

    class CustomDeclarationInput(m.FrozenModel):
        """Validated command input with explicit CLI option declarations."""

        flag: Annotated[
            bool,
            m.Field(
                description="Custom boolean option",
                validate_default=True,
                json_schema_extra={"typer_param_decls": ("-f", "--flaggy")},
            ),
        ] = False

    class ExcludedFieldInput(m.FrozenModel):
        """Validated command input with one excluded internal field."""

        visible: Annotated[str, m.Field(description="Visible command value")]
        hidden: Annotated[
            str,
            m.Field(
                description="Internal value excluded from command options",
                exclude=True,
                validate_default=True,
            ),
        ] = "secret"

    class TemplateEmpty(m.FrozenModel):
        """Validated empty template context."""

    class TemplateValue(m.FrozenModel):
        """Validated scalar template context."""

        value: Annotated[int, m.Field(description="Rendered test value")]

    class TemplateServer(m.FrozenModel):
        """Validated server data rendered by template tests."""

        port: Annotated[int, m.Field(description="Server port")]

    class TemplateServerContext(m.FrozenModel):
        """Validated nested server template context."""

        server: Annotated[
            TestsFlextCliModelsFixtures.TemplateServer,
            m.Field(description="Server rendered by the template"),
        ]

    class SampleInputPatch(m.FrozenModel):
        """Canonical source patch for model derivation tests."""

        name: Annotated[str, m.Field(description="Patched target name")]
        count: Annotated[int, m.Field(description="Patched repetition count")]

    class ReportRow(m.FrozenModel):
        """Serializable row consumed by the output example."""

        id: Annotated[int, m.Field(description="Report row identifier")]
        name: Annotated[str, m.Field(description="Report row name")]
        status: Annotated[str, m.Field(description="Report row status")]

    class UserPreferences(m.FrozenModel):
        """User preference payload persisted by the file example."""

        theme: Annotated[str, m.Field(description="Selected visual theme")]
        notifications: Annotated[
            bool, m.Field(description="Notification activation flag")
        ]

    class DeploymentConfig(m.FrozenModel):
        """Deployment payload persisted by the YAML example."""

        environment: Annotated[str, m.Field(description="Deployment environment")]
        replicas: Annotated[int, m.Field(description="Requested replica count")]

    class ImportRecord(m.FrozenModel):
        """Validated record consumed by the JSON import example."""

        id: Annotated[int, m.Field(description="Imported record identifier")]
        name: Annotated[str, m.Field(description="Imported record name")]
        value: Annotated[str, m.Field(description="Imported record value")]


__all__: tuple[str, ...] = ("TestsFlextCliModelsFixtures",)
