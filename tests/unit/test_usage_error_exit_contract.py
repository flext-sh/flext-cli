"""Behavioral tests for the CLI exit-code contract of result routes.

A usage error (missing or unknown option, input the request model rejects)
keeps Click's native usage exit code and one clean message naming the option as
typed; a domain failure keeps the failure exit code and renders once. Each case
runs a real app through ``cli.execute_app`` and ``cli.finalize_result``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli import cli
from tests import c, m, p, r, t, tm, u


class TestsFlextCliUsageErrorExitContract:
    """Usage errors and domain failures exit with distinct native codes."""

    class Request(m.BaseModel):
        """Request with a required option and a bounded one."""

        folder: str
        block: int = m.Field(default=1, gt=0)
        explode: bool = False

    @staticmethod
    def _handler(request: t.Cli.ModelLike) -> p.Result[str]:
        if not isinstance(request, TestsFlextCliUsageErrorExitContract.Request):
            msg = "unexpected request type"
            raise TypeError(msg)
        if request.explode:
            return r[str].fail("domain failure")
        return r[str].ok(request.folder)

    @classmethod
    def _run(cls, args: t.StrSequence) -> int:
        app = cli.create_app_with_common_params(name="usage-app", help_text="Usage")
        cli.register_result_command(
            app,
            route=cli.result_route(
                metadata=m.Cli.CommandMetadata(name="run", help_text="Run"),
                model_cls=cls.Request,
                handler=cls._handler,
                success_formatter=str,
            ),
        )
        return cli.finalize_result(
            cli.execute_app(app, prog_name="usage-app", args=["run", *args]),
        )

    @pytest.mark.parametrize(
        ("args", "fragment"),
        [
            u.Tests.param([], "--folder", id="missing-required-option"),
            u.Tests.param(["--folder", "x", "--nope"], "--nope", id="unknown-option"),
            u.Tests.param(
                ["--folder", "x", "--block", "0"], "--block", id="model-validation"
            ),
        ],
    )
    def test_usage_error_exits_with_usage_code(
        self,
        args: t.StrSequence,
        fragment: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """A usage error exits with the usage code and one clean message."""
        tm.that(self._run(args), eq=c.Cli.EXIT_CODE_USAGE)

        stderr = capsys.readouterr().err
        tm.that(stderr, has=fragment)
        tm.that(stderr, lacks="Traceback")
        tm.that(stderr.count("Error:"), eq=1)

    def test_domain_failure_exits_with_failure_code(
        self,
        capsys: t.Tests.CaptureFixture[str],
    ) -> None:
        """A domain failure keeps the failure exit code and renders once."""
        tm.that(
            self._run(["--folder", "x", "--explode"]),
            eq=c.Cli.EXIT_CODE_FAILURE,
        )
        captured = capsys.readouterr()
        tm.that(captured.out, eq="")
        tm.that(captured.err.count("domain failure"), eq=1)

    def test_success_exits_with_success_code(self) -> None:
        """A valid invocation exits zero."""
        tm.that(self._run(["--folder", "x"]), eq=c.Cli.EXIT_CODE_SUCCESS)
