"""Generic filesystem helpers shared through ``u.Cli``."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from flext_cli import c, t

from ._files_parts.flextcliutilitiesfiles_part_01 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart01,
)
from ._files_parts.flextcliutilitiesfiles_part_02 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart02,
)
from ._files_parts.flextcliutilitiesfiles_part_03 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart03,
)
from ._files_parts.flextcliutilitiesfiles_part_04 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart04,
)
from ._files_parts.flextcliutilitiesfiles_part_05 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart05,
)
from ._files_parts.flextcliutilitiesfiles_part_06 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart06,
)
from .runtime import FlextCliUtilitiesRuntime


class FlextCliUtilitiesFiles(
    FlextCliUtilitiesFilesPart01,
    FlextCliUtilitiesFilesPart02,
    FlextCliUtilitiesFilesPart03,
    FlextCliUtilitiesFilesPart04,
    FlextCliUtilitiesFilesPart05,
    FlextCliUtilitiesFilesPart06,
):
    """Public facade for FlextCliUtilitiesFiles."""

    @staticmethod
    def files_matching(
        root: Path, *, includes: t.StrSequence, excludes: t.StrSequence = ()
    ) -> t.SequenceOf[Path]:
        """Select tracked and untracked files in Git, or files on disk outside Git."""
        if not root.is_dir():
            return []
        scope = root.resolve()
        probe = FlextCliUtilitiesRuntime.run_bytes(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=scope,
            timeout=c.DEFAULT_TIMEOUT_SECONDS,
            env={"LC_ALL": "C"},
        ).value
        outcome = probe.outcome
        if outcome.timed_out or outcome.forwarded_signal is not None:
            msg = f"Git worktree probe interrupted: {scope}"
            raise RuntimeError(msg)
        if outcome.raw_return_code == 0:
            if probe.stdout.strip() != b"true":
                msg = f"Git worktree probe returned unexpected output: {scope}"
                raise RuntimeError(msg)
            listed = FlextCliUtilitiesRuntime.run_bytes(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                cwd=scope,
                timeout=c.DEFAULT_TIMEOUT_SECONDS,
            ).value
            if (
                listed.outcome.raw_return_code != 0
                or listed.outcome.timed_out
                or listed.outcome.forwarded_signal is not None
            ):
                msg = listed.stderr.decode(c.Cli.ENCODING_DEFAULT, errors="strict")
                raise OSError(msg)
            candidates = (
                scope / Path(relative.decode(c.Cli.ENCODING_DEFAULT, errors="strict"))
                for relative in listed.stdout.split(b"\0")
                if relative
            )
        elif (
            outcome.raw_return_code == 128
            and b"not a git repository" in probe.stderr
        ):
            candidates = scope.rglob("*")
        else:
            msg = probe.stderr.decode(c.Cli.ENCODING_DEFAULT, errors="strict")
            raise OSError(msg)
        return sorted({
            path
            for path in candidates
            if path.is_file()
            if not includes
            or any(
                fnmatch.fnmatchcase(path.relative_to(scope).as_posix(), pattern)
                for pattern in includes
            )
            if not any(
                fnmatch.fnmatchcase(path.relative_to(scope).as_posix(), pattern)
                for pattern in excludes
            )
        })


__all__: list[str] = ["FlextCliUtilitiesFiles"]
