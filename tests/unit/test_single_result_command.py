"""Behavioral tests for ``cli.run_result_command``.

One request model and one handler run as the whole CLI: options follow the
program name with no subcommand token, help is the model docstring,
success output comes only from the formatter, and the exit code is returned
(success, domain failure once on stderr, Click usage error).

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests import c, cli, m, p, r, t, tm, u


class TestsFlextCliSingleResultCommand:
    """A single result command runs without a subcommand and returns its code."""

    class Request(m.EnforcedModel):
        """Copy one source folder into the base."""

        fontes: str
        base: str

    @staticmethod
    def _handler(
        request: TestsFlextCliSingleResultCommand.Request,
    ) -> p.Result[TestsFlextCliSingleResultCommand.Request]:
        if request.fontes == request.base:
            return r[TestsFlextCliSingleResultCommand.Request].fail(
                "fontes and base must differ",
            )
        return r[TestsFlextCliSingleResultCommand.Request].ok(request)

    @classmethod
    def _run(
        cls,
        args: t.StrSequence,
        *,
        success_formatter: t.Cli.SuccessMessageFormatter[
            TestsFlextCliSingleResultCommand.Request
        ]
        | None = None,
    ) -> int:
        return cli.run_result_command(
            cls.Request,
            cls._handler,
            prog_name="copy-fontes",
            args=args,
            success_formatter=success_formatter,
        )

    def test_options_run_without_a_subcommand_token(
        self,
        capsys: t.Tests.CaptureFixture[str],
    ) -> None:
        """Options follow the program name directly and reach the handler."""
        code = self._run(
            ["--fontes", "a", "--base", "b"],
            success_formatter=lambda request: request.model_dump_json(),
        )

        tm.that(code, eq=c.Cli.EXIT_CODE_SUCCESS)
        out = capsys.readouterr().out
        tm.that(
            self.Request.model_validate_json(out),
            eq=self.Request(fontes="a", base="b"),
        )

    def test_default_formatter_prints_nothing(
        self,
        capsys: t.Tests.CaptureFixture[str],
    ) -> None:
        """A success without a formatter writes nothing."""
        tm.that(
            self._run(["--fontes", "a", "--base", "b"]),
            eq=c.Cli.EXIT_CODE_SUCCESS,
        )
        captured = capsys.readouterr()
        tm.that(captured.out, eq="")
        tm.that(captured.err, eq="")

    def test_custom_formatter_renders_the_value(
        self,
        capsys: t.Tests.CaptureFixture[str],
    ) -> None:
        """A formatter's text is the success output."""
        tm.that(
            self._run(
                ["--fontes", "a", "--base", "b"],
                success_formatter=lambda request: request.fontes,
            ),
            eq=c.Cli.EXIT_CODE_SUCCESS,
        )
        tm.that(capsys.readouterr().out, has="a")

    def test_domain_failure_prints_one_line_and_exits_failure(
        self,
        capsys: t.Tests.CaptureFixture[str],
    ) -> None:
        """A handler failure returns the failure code with one stderr line."""
        code = self._run(["--fontes", "a", "--base", "a"])

        tm.that(code, eq=c.Cli.EXIT_CODE_FAILURE)
        captured = capsys.readouterr()
        tm.that(captured.out, eq="")
        tm.that(captured.err.count("fontes and base must differ"), eq=1)
        tm.that(captured.err.strip().count("\n"), eq=0)

    @c.Tests.MARK.parametrize(
        ("args", "fragment"),
        [
            u.Tests.param(["--fontes", "a"], "--base", id="missing-option"),
            u.Tests.param(
                ["copy-fontes", "--fontes", "a", "--base", "b"],
                "copy-fontes",
                id="subcommand-token-is-unexpected",
            ),
        ],
    )
    def test_usage_error_keeps_click_message_and_code(
        self,
        args: t.StrSequence,
        fragment: str,
        capsys: t.Tests.CaptureFixture[str],
    ) -> None:
        """A usage error returns Click's usage code and one Click message."""
        tm.that(self._run(args), eq=c.Cli.EXIT_CODE_USAGE)
        stderr = capsys.readouterr().err
        tm.that(stderr, has=fragment)
        tm.that(stderr.count("Error:"), eq=1)
        tm.that(stderr, lacks="Traceback")

    def test_help_is_the_model_docstring(
        self,
        capsys: t.Tests.CaptureFixture[str],
    ) -> None:
        """The request model docstring is the command help."""
        tm.that(self._run(["--help"]), eq=c.Cli.EXIT_CODE_SUCCESS)
        tm.that(capsys.readouterr().out, has=self.Request.__doc__)
