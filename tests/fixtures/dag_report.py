"""Report dependency-graph query results for hash-seed independence tests.

Run as ``python -m tests.fixtures.dag_report``; the parent test compares the
report of interpreters started with different ``PYTHONHASHSEED`` values.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
import json
import sys

from flext_cli import u


def report() -> str:
    """Return the canonical JSON report of every dependency-graph query.

    Returns:
        The waves, cycle failure, components and closure as sorted JSON.

    """
    cyclic = {
        "b": ("c",),
        "c": ("a",),
        "a": ("b",),
        "y": ("x",),
        "x": ("y",),
        "z": ("x",),
    }
    acyclic = {"q": ("r", "p"), "p": (), "r": ("p",), "s": ()}
    return json.dumps(
        {
            "cycle": u.Cli.dag_waves(cyclic).error,
            "components": [
                sorted(component) for component in u.Cli.dag_strongly_connected(cyclic)
            ],
            "waves": u.Cli.dag_waves(acyclic).value,
            "closure": sorted(
                u.Cli.dag_closure(acyclic, frozenset({"q"})).value,
            ),
        },
        sort_keys=True,
    )


def main() -> None:
    """Write the report to standard output."""
    sys.stdout.write(report() + "\n")


if __name__ == "__main__":
    main()
