"""Normal-exit descendant containment contract."""

from __future__ import annotations

import sys
import time
from typing import TYPE_CHECKING

from flext_tests import tm
from tests import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliRuntimeProcessDescendants:
    """Prove root completion is not mistaken for boundary completion."""

    def test_normal_root_exit_leaves_no_descendant(self, tmp_path: Path) -> None:
        output_file = tmp_path / "normal-exit.log"
        heartbeat = tmp_path / "normal-heartbeat"
        child = (
            "import pathlib,sys,time;"
            "path=pathlib.Path(sys.argv[1]);"
            "\nwhile True:\n path.write_text(str(time.monotonic()));time.sleep(.02)"
        )
        parent = (
            "import pathlib,subprocess,sys,time;"
            f"subprocess.Popen([sys.executable,'-c',{child!r},sys.argv[1]]);"
            "path=pathlib.Path(sys.argv[1]);"
            "\nwhile not path.exists():\n time.sleep(.01)"
        )
        started = time.monotonic()

        result = u.Cli().run_to_file(
            [sys.executable, "-c", parent, str(heartbeat)], output_file
        )

        tm.ok(result)
        tm.that(result.value, eq=0)
        stopped_value = heartbeat.stat().st_mtime_ns
        tm.that(heartbeat.stat().st_mtime_ns, eq=stopped_value)
        tm.that(time.monotonic() - started, lt=5.0)


__all__: list[str] = ["TestsFlextCliRuntimeProcessDescendants"]
