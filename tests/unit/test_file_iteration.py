"""Behavioral contract for config-owned Git-aware file iteration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import config, p, u
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliFileIteration:
    """Exercise the public ``u.Cli.iter_matching_files`` owner."""

    def test_git_scope_preserves_visible_state_and_path_semantics(
        self, tmp_path: Path
    ) -> None:
        """Select tracked, dirty, and untracked files with Git ignore semantics."""
        repository = tmp_path / "arbitrary repository"
        nested = repository / "nested"
        nested.mkdir(parents=True)
        policy = config.Cli.file_iteration
        tm.that(policy, is_=p.Cli.FileIteration)
        tm.ok(
            u.Cli.run(
                (policy.executable, "init", "--quiet"),
                cwd=repository,
                timeout=policy.timeout_seconds,
            )
        )

        tracked = repository / "tracked.py"
        dirty = nested / "dirty.py"
        untracked = nested / "untracked.py"
        excluded = nested / "excluded.py"
        ignored = repository / "ignored.py"
        removed = repository / "removed.py"
        rename_source = repository / "rename-source.py"
        renamed = repository / "renamed.py"
        note = repository / "note.md"
        ignore_file = repository / ".gitignore"
        for path in (
            tracked,
            dirty,
            untracked,
            excluded,
            ignored,
            removed,
            rename_source,
            note,
        ):
            path.write_text(path.name, encoding="utf-8")
        ignore_file.write_text(f"{ignored.name}\n", encoding="utf-8")
        tm.ok(
            u.Cli.run(
                (
                    policy.executable,
                    "add",
                    "--",
                    ignore_file.name,
                    tracked.name,
                    dirty.relative_to(repository).as_posix(),
                    removed.name,
                    rename_source.name,
                    note.name,
                ),
                cwd=repository,
                timeout=policy.timeout_seconds,
            )
        )
        tracked.write_text("dirty tracked state", encoding="utf-8")
        dirty.write_text("dirty nested state", encoding="utf-8")
        removed.unlink()
        tm.ok(
            u.Cli.run(
                (policy.executable, "mv", "--", rename_source.name, renamed.name),
                cwd=repository,
                timeout=policy.timeout_seconds,
            )
        )

        selected_result = u.Cli.iter_matching_files(
            repository,
            includes=("*.py",),
            excludes=(excluded.relative_to(repository).as_posix(),),
        )
        tm.ok(selected_result)
        selected = selected_result.value
        expected = sorted((tracked, dirty, untracked, renamed))
        tm.that(selected, eq=expected)
        tm.that(selected, is_=list)
        tm.that(selected, eq=sorted(set(selected)))
        tm.that(all(path.is_absolute() for path in selected), eq=True)
        tm.that(ignored in selected, eq=False)
        tm.that(removed in selected, eq=False)

        nested_result = u.Cli.iter_matching_files(
            nested, includes=("*.py",), excludes=()
        )
        tm.ok(nested_result)
        nested_selected = nested_result.value
        tm.that(nested_selected, eq=sorted((dirty, excluded, untracked)))

    def test_non_git_scope_falls_back_to_recursive_globs(self, tmp_path: Path) -> None:
        """Use the same include/exclude contract when no repository is active."""
        root = tmp_path / "arbitrary-files"
        nested = root / "nested"
        nested.mkdir(parents=True)
        top_level = root / "top.py"
        nested_match = nested / "match.py"
        nested_excluded = nested / "excluded.py"
        unrelated = root / "note.md"
        excluded_prefix = config.Cli.file_iteration.fallback_excluded_segment_prefixes[
            0
        ]
        hidden_file = root / f"{excluded_prefix}hidden.py"
        hidden_nested = root / f"{excluded_prefix}hidden-directory" / "nested.py"
        hidden_nested.parent.mkdir()
        for path in (
            top_level,
            nested_match,
            nested_excluded,
            unrelated,
            hidden_file,
            hidden_nested,
        ):
            path.write_text(path.name, encoding="utf-8")

        selected_result = u.Cli.iter_matching_files(
            root,
            includes=("*.py",),
            excludes=(nested_excluded.relative_to(root).as_posix(),),
        )
        tm.ok(selected_result)
        selected = selected_result.value
        tm.that(selected, eq=sorted((top_level, nested_match)))
        missing_result = u.Cli.iter_matching_files(
            root / "missing", includes=("*.py",), excludes=()
        )
        tm.ok(missing_result)
        tm.that(missing_result.value, eq=[])

    def test_git_failure_is_not_reinterpreted_as_filesystem_scope(
        self, tmp_path: Path
    ) -> None:
        """Fail closed when a discovered Git worktree cannot execute its query."""
        broken_repository = tmp_path / "broken-repository"
        (broken_repository / ".git").mkdir(parents=True)
        visible = broken_repository / "visible.py"
        visible.write_text(visible.name, encoding="utf-8")

        result = u.Cli.iter_matching_files(
            broken_repository, includes=("*.py",), excludes=()
        )

        tm.fail(result)


__all__: list[str] = ["TestsFlextCliFileIteration"]
