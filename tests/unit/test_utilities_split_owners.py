"""Observable contracts of the process, tree, markdown, and DOCX owner split.

Each case drives the public ``u.Cli`` facade with real children, real
directories, and real rendered bytes, so the assertions hold whichever
internal owner carries the behavior.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT

from tests import c, m, t, tm, u


class TestsFlextCliUtilitiesSplitOwners:
    """Public behavior preserved across the decomposed utility owners."""

    @staticmethod
    def test_run_raw_feeds_stdin_and_keeps_streams_and_exit_apart() -> None:
        """A non-zero child keeps its exit code, stdout, and stderr distinct."""
        result = u.Cli.run_raw(
            [
                sys.executable,
                "-c",
                (
                    "import sys; sys.stdout.write(sys.stdin.read().upper()); "
                    "sys.stderr.write('warn'); sys.exit(3)"
                ),
            ],
            options=m.Cli.ProcessOptions(input_data="payload"),
        )
        output = tm.ok(result)
        tm.that(output.stdout, eq="PAYLOAD")
        tm.that(output.stderr, eq="warn")
        tm.that(output.outcome.raw_return_code, eq=3)
        tm.that(output.outcome.timed_out, eq=False)

    @staticmethod
    def test_run_fails_with_the_typed_exit_outcome() -> None:
        """The checked runner carries the child exit in its error data."""
        result = u.Cli.run([sys.executable, "-c", "raise SystemExit(4)"])
        tm.fail(result)
        error_data = tm.not_none(result.error_data)
        tm.that(error_data[c.Cli.PROCESS_EXIT_CODE_KEY], eq=4)
        tm.that(error_data[c.Cli.PROCESS_TIMED_OUT_KEY], eq=False)

    @staticmethod
    def test_timeout_terminates_the_child_and_reports_it() -> None:
        """A child past its deadline is reaped and reported as timed out."""
        sleeper = [sys.executable, "-c", "import time; time.sleep(30)"]
        raw = tm.ok(u.Cli.run_raw(sleeper, timeout=1))
        tm.that(raw.outcome.timed_out, eq=True)
        tm.that(raw.outcome.raw_return_code, ne=0)
        checked = u.Cli.run(sleeper, timeout=1)
        tm.fail(checked)
        tm.that(
            tm.not_none(checked.error_data)[c.Cli.PROCESS_TIMED_OUT_KEY],
            eq=True,
        )

    @staticmethod
    def test_run_bytes_preserves_undecodable_output() -> None:
        """Byte-exact capture keeps bytes that are not valid UTF-8."""
        result = u.Cli.run_bytes([
            sys.executable,
            "-c",
            "import sys; sys.stdout.buffer.write(bytes([0, 255]))",
        ])
        tm.that(tm.ok(result).stdout, eq=bytes([0, 255]))

    @staticmethod
    def test_run_to_file_combines_or_separates_stderr(tmp_path: Path) -> None:
        """Without a stderr sink both streams share the output file."""
        script = [
            sys.executable,
            "-c",
            "import sys; print('out', flush=True); print('err', file=sys.stderr)",
        ]
        combined = tmp_path / "combined.txt"
        tm.that(tm.ok(u.Cli.run_to_file(script, combined)).raw_return_code, eq=0)
        tm.that(combined.read_text(encoding=c.DEFAULT_ENCODING), has="out")
        tm.that(combined.read_text(encoding=c.DEFAULT_ENCODING), has="err")

        stdout_file = tmp_path / "stdout.txt"
        stderr_file = tmp_path / "stderr.txt"
        tm.ok(
            u.Cli.run_to_file(
                script,
                stdout_file,
                options=m.Cli.ProcessOptions(stderr_file=stderr_file),
            ),
        )
        tm.that(stdout_file.read_text(encoding=c.DEFAULT_ENCODING), eq="out\n")
        tm.that(stderr_file.read_text(encoding=c.DEFAULT_ENCODING), eq="err\n")

    @staticmethod
    def test_directory_inventory_backs_query_verification(tmp_path: Path) -> None:
        """Queries hold against the inventory and fail once the tree changes."""
        root = tmp_path / "root"
        root.mkdir()
        (root / "leaf").write_text("data", encoding=c.DEFAULT_ENCODING)
        (root / "nested").mkdir()
        inventory = tm.ok(u.Cli.atomic_inventory_physical_directory(root))
        tm.that(
            tuple((entry.name, entry.kind) for entry in inventory.entries),
            eq=(("leaf", "file"), ("nested", "directory")),
        )
        queried = m.Cli.AtomicDirectoryInventory.model_validate({
            "root": inventory.root,
            "entries": inventory.entries,
            "queries": (("absent", "exists"), ("leaf", "isfile"), ("nested", "isdir")),
        })
        tm.that(
            tm.ok(u.Cli.atomic_verify_directory_queries((queried,), ())),
            eq=True,
        )
        (root / "absent").mkdir()
        with u.Tests.raises(ValueError, match="source directory query changed"):
            u.Cli.atomic_verify_directory_queries((queried,), ())

    @staticmethod
    def test_markdown_link_owner_rewrites_and_unlinks_one_line() -> None:
        """Link discovery, target rewrite, and unlink agree on one line."""
        text = "See [guide](a.md) and ![logo](b.png).\n"
        links = u.Cli.markdown_links(text)
        tm.that(
            tuple((link.target, link.image) for link in links),
            eq=(("a.md", False), ("b.png", True)),
        )
        rewritten, count = u.Cli.markdown_rewrite_link_targets(
            text,
            lambda link: "c.md" if link.target == "a.md" else None,
        )
        tm.that(count, eq=1)
        tm.that(rewritten, eq="See [guide](c.md) and ![logo](b.png).\n")
        tm.that(
            u.Cli.markdown_unlink(rewritten, lambda link: not link.image),
            eq="See guide and ![logo](b.png).\n",
        )

    @staticmethod
    def test_docx_render_applies_font_table_and_section_layout() -> None:
        """Formatting and layout owners both reach the rendered document."""
        cell = m.Cli.DocxTableCellPlan(
            paragraphs=(m.Cli.DocxParagraphPlan(runs=(m.Cli.DocxRunPlan(text="A1"),)),),
        )
        plan = m.Cli.DocxDocumentPlan(
            paragraphs=(
                m.Cli.DocxParagraphPlan(
                    runs=(
                        m.Cli.DocxRunPlan(
                            text="Heading",
                            style=m.Cli.DocxRunStyleSpec(
                                font=m.Cli.DocxFontSpec(bold=True, size=14),
                            ),
                        ),
                    ),
                ),
            ),
            tables=(
                m.Cli.DocxTablePlan(
                    rows=(
                        m.Cli.DocxTableRowPlan(
                            cells=(cell, m.Cli.DocxTableCellPlan()),
                        ),
                    ),
                ),
            ),
            sections=(
                m.Cli.DocxSectionPlan(
                    orientation="landscape",
                    width=10058400,
                    height=7772400,
                    left_margin=457200,
                ),
            ),
        )
        rendered = tm.ok(
            u.Cli.docx_render(m.Cli.DocxRenderRequest(plan=plan, source_date_epoch=0)),
        )
        document = Document(BytesIO(rendered.content))
        run = document.paragraphs[0].runs[0]
        tm.that(run.text, eq="Heading")
        tm.that(run.font.bold, eq=True)
        tm.that(tm.not_none(run.font.size).pt, eq=14.0)
        table = document.tables[0]
        tm.that(len(table.columns), eq=2)
        tm.that(table.cell(0, 0).text, eq="A1")
        section = document.sections[-1]
        tm.that(section.orientation, eq=WD_ORIENT.LANDSCAPE)
        tm.that(section.page_width, eq=10058400)
        tm.that(section.left_margin, eq=457200)

    @staticmethod
    def test_supplied_options_reject_a_structural_look_alike_context() -> None:
        """Only the context Typer injects passes, not a look-alike value."""

        class LookAlikeContext(tuple[str, ...]):
            """Option value that also exposes ``get_parameter_source``."""

            __slots__ = ()

            @staticmethod
            def get_parameter_source(name: str) -> None:
                """Answer like a context without being one."""
                del name

        options: dict[str, t.Cli.CliValue] = {
            "ctx": LookAlikeContext(("ctx",)),
            "flag": True,
        }
        with u.Tests.raises(TypeError, match="Typer did not inject"):
            u.Cli.framework_supplied_options(options, "ctx")
