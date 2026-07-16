"""Model-only YAML egress contract tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import tm

from flext_cli import cli, m

from pathlib import Path



def test_write_yaml_model_round_trips_the_same_model_contract(tmp_path: Path) -> None:
    """The only owned payload is a validated model on both sides of YAML."""
    source = m.Cli.XlsxCellAddress(row=7, column=9)
    target = tmp_path / "address.yaml"

    written = cli.yaml_write_model(target, source)
    loaded = cli.yaml_read_model(target, m.Cli.XlsxCellAddress)

    tm.that(written.success, eq=True)
    tm.that(loaded.success, eq=True)
    tm.that(loaded.value, eq=source)


__all__: tuple[str, ...] = (
    "test_write_yaml_model_round_trips_the_same_model_contract",
)
