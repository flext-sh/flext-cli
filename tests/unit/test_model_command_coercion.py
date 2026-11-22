"""The request model is the one validator of a model command's option values.

Why (aihub-vkb1j.25): Typer 0.29 coerced Path, number and enum options by
itself before the model ran, so a rejected value got Typer's message without
the input and every such option was validated twice. Typer now parses those
options as text, the model validates them, and the help shows the same types.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, MutableSequence, Sequence
from pathlib import Path

from flext_cli import cli
from tests import c, m, t, tm, u


class TestsFlextCliModelCommandCoercion:
    """Model command options run through a real application, in process."""

    @staticmethod
    def _entrypoint(
        model_cls: t.ModelClass[t.Cli.ModelLike],
        bound: MutableSequence[t.Cli.ModelLike],
    ) -> Callable[[Sequence[str]], int]:
        """Build the CLI entry point of one model command named ``run``.

        Returns:
            The entry point returning the application's exit code.

        """

        def handler(model: t.Cli.ModelLike) -> int:
            bound.append(model)
            return 0

        app = cli.create_app_with_common_params(name="typed-app", help_text="Typed app")
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(model_cls, handler),
        )
        return lambda argv: cli.finalize_result(
            cli.execute_app(app, prog_name="typed-app", args=list(argv))
        )

    def test_values_bind_to_their_declared_types(self) -> None:
        """Path, number, list and enum text becomes the model's declared types."""
        bound: list[t.Cli.ModelLike] = []
        outcome = u.Tests.cli_in_process(
            self._entrypoint(m.Tests.ModelCommandTyped, bound),
            [
                "run",
                "--root",
                "/srv/data",
                "--count",
                "3",
                "--ratio",
                "0.25",
                "--roots",
                "/a",
                "--roots",
                "/b",
                "--output",
                "yaml",
            ],
        )

        tm.that(outcome.outcome.raw_return_code, eq=0)
        model = m.Tests.ModelCommandTyped.model_validate(bound[0].model_dump())
        tm.that(model.root, eq=Path("/srv/data"))
        tm.that(model.count, eq=3)
        tm.that(model.ratio, eq=0.25)
        tm.that(model.roots, eq=(Path("/a"), Path("/b")))
        tm.that(model.output, eq=c.Cli.OutputFormats.YAML)

    def test_help_shows_the_declared_types(self) -> None:
        """The help type column names the declared type, not Typer's text."""
        outcome = u.Tests.cli_in_process(
            self._entrypoint(m.Tests.ModelCommandTyped, []),
            ["run", "--help"],
            env={"COLUMNS": "200", "NO_COLOR": "1", "TERM": "dumb"},
        )

        tm.that(outcome.outcome.raw_return_code, eq=0)
        choices = "|".join(member.value for member in c.Cli.OutputFormats)
        tm.that(
            outcome.stdout,
            has=["<path>", "<int>", "<float>", "<list[Path]>", f"<{choices}>"],
        )

    def test_a_bad_choice_is_the_models_message_with_the_input(self) -> None:
        """An unknown or wrongly cased choice is refused by the model, naming it."""
        for value in ("bogus", "YAML"):
            bound: list[t.Cli.ModelLike] = []
            outcome = u.Tests.cli_in_process(
                self._entrypoint(m.Tests.ModelCommandTyped, bound),
                ["run", "--root", "/srv", "--output", value],
            )

            tm.that(outcome.outcome.raw_return_code, eq=2)
            tm.that(outcome.stderr, has=["--output", repr(value), "Input should be"])
            tm.that(bound, empty=True)

    def test_a_missing_required_option_still_names_the_option(self) -> None:
        """The help type never replaces the option name in a usage error."""
        outcome = u.Tests.cli_in_process(
            self._entrypoint(m.Tests.ModelCommandTyped, []),
            ["run"],
        )

        tm.that(outcome.outcome.raw_return_code, eq=2)
        tm.that(outcome.stderr, has="--root")
        tm.that(outcome.stderr, lacks="<path>")

    def test_a_model_hiding_its_input_keeps_it_out_of_the_message(self) -> None:
        """A model with ``hide_input_in_errors`` never has its input echoed."""
        outcome = u.Tests.cli_in_process(
            self._entrypoint(m.Tests.ModelCommandHiddenInput, []),
            ["run", "--count", "secret-not-a-number"],
        )

        tm.that(outcome.outcome.raw_return_code, eq=2)
        tm.that(outcome.stderr, has="--count")
        tm.that(outcome.stderr, lacks="secret-not-a-number")
