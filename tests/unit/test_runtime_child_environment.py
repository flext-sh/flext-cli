"""Child-environment contract for runtime command execution.

The overlay-versus-removal distinction is load bearing: ``env`` can only add or
replace keys, so a caller that needs a variable GONE from the child must say so
with ``remove_env_keys``. Passing a pre-cleaned mapping to ``env`` silently
reinstated every omitted key from the parent environment, and the command then
ran against the wrong target while reporting success (mro-wt8qp).
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping, Sequence

from flext_cli import u
from flext_tests import tm

_MARKER = "FLEXT_CLI_CHILD_ENV_PROBE"
_ECHO = "import os,sys; sys.stdout.write(os.environ.get(sys.argv[1], '<unset>'))"


class TestsFlextCliRuntimeChildEnvironment:
    """u.Cli command execution honors overrides and removals exactly."""

    @staticmethod
    def _echo(
        key: str,
        *,
        env: Mapping[str, str] | None = None,
        remove_env_keys: Sequence[str] = (),
    ) -> str:
        """Return the child's view of one environment variable."""
        return tm.ok(
            u.Cli.capture(
                [sys.executable, "-c", _ECHO, key],
                env=env,
                remove_env_keys=remove_env_keys,
            )
        )

    def test_override_reaches_the_child(self) -> None:
        probe = TestsFlextCliRuntimeChildEnvironment._echo(
            _MARKER, env={_MARKER: "overridden"}
        )

        tm.that(probe, eq="overridden")

    def test_override_does_not_discard_the_inherited_environment(self) -> None:
        """An overlay adds one key; PATH and the rest of the parent survive."""
        probe = TestsFlextCliRuntimeChildEnvironment._echo(
            "PATH", env={_MARKER: "overridden"}
        )

        tm.that(probe, eq=os.environ["PATH"])

    def test_remove_env_keys_unsets_the_variable_in_the_child(self) -> None:
        probe = TestsFlextCliRuntimeChildEnvironment._echo(
            _MARKER, env={_MARKER: "inherited"}, remove_env_keys=(_MARKER,)
        )

        tm.that(probe, eq="<unset>")

    def test_an_omitted_key_in_env_is_not_a_removal(self) -> None:
        """``env`` is an overlay: omitting a key never unsets it.

        Removal is expressed exclusively through ``remove_env_keys``; relying on
        omission is the failure mode that let poisoned GIT_DIR/GIT_WORK_TREE
        values survive into repository-construction commands.
        """
        probe = TestsFlextCliRuntimeChildEnvironment._echo(
            _MARKER, env={_MARKER: "inherited"}
        )

        tm.that(probe, eq="inherited")

    def test_removal_wins_over_an_inherited_value_with_overrides_present(self) -> None:
        probe = TestsFlextCliRuntimeChildEnvironment._echo(
            _MARKER,
            env={_MARKER: "inherited", "FLEXT_CLI_CHILD_ENV_OTHER": "1"},
            remove_env_keys=(_MARKER,),
        )

        tm.that(probe, eq="<unset>")
