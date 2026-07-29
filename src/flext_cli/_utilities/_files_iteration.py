"""Git-aware file iteration shared through ``u.Cli``."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli import config
from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliUtilitiesFileIteration:
    """Select files deterministically from Git state or the filesystem."""

    @classmethod
    def iter_matching_files(
        cls, root: Path, *, includes: t.StrSequence, excludes: t.StrSequence = ()
    ) -> t.SequenceOf[Path]:
        """Return matching files from one resolved, Git-aware scope."""
        if not root.is_dir():
            return []
        resolved_root = root.resolve()
        git_paths = cls._git_scope_paths(resolved_root)
        candidates = (
            git_paths
            if git_paths is not None
            else [path for path in resolved_root.rglob("*") if path.is_file()]
        )
        return sorted(
            {
                path
                for path in candidates
                if path.is_file()
                if cls._matches(
                    path.relative_to(resolved_root), includes=includes, excludes=excludes
                )
            }
        )

    @staticmethod
    def _matches(
        relative_path: Path,
        *,
        includes: t.StrSequence,
        excludes: t.StrSequence,
    ) -> bool:
        """Return whether one scope-relative path satisfies configured globs."""
        path_text = relative_path.as_posix()
        included = not includes or any(
            fnmatch.fnmatch(path_text, pattern) for pattern in includes
        )
        excluded = any(fnmatch.fnmatch(path_text, pattern) for pattern in excludes)
        return included and not excluded

    @classmethod
    def _git_scope_paths(cls, scope_root: Path) -> t.SequenceOf[Path] | None:
        """Return Git-visible files under ``scope_root`` or ``None`` outside Git."""
        policy = config.Cli.file_iteration
        repository_root = cls._git_repository_root(scope_root)
        if repository_root is None:
            return None
        files_result = FlextCliUtilitiesRuntime.run(
            (policy.executable, *policy.scope_files_args),
            cwd=repository_root,
            timeout=policy.timeout_seconds,
        )
        if files_result.failure:
            return None
        return cls._scope_paths_from_output(
            repository_root,
            scope_root,
            files_result.value.stdout,
            separator=policy.output_separator,
        )

    @staticmethod
    def _git_repository_root(scope_root: Path) -> Path | None:
        """Return the nearest enclosing Git worktree root."""
        current = scope_root
        while True:
            if (current / ".git").exists():
                return current
            parent = current.parent
            if parent == current:
                return None
            current = parent

    @staticmethod
    def _scope_paths_from_output(
        repository_root: Path,
        scope_root: Path,
        output: str,
        *,
        separator: str,
    ) -> t.SequenceOf[Path]:
        """Parse repository-relative Git paths into one safe scope sequence."""
        paths: set[Path] = set()
        for raw_path in output.split(separator):
            if not raw_path:
                continue
            relative_path = Path(raw_path)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                continue
            candidate = repository_root / relative_path
            try:
                candidate.relative_to(scope_root)
            except ValueError:
                continue
            if candidate.is_file():
                paths.add(candidate)
        return sorted(paths)


__all__: list[str] = ["FlextCliUtilitiesFileIteration"]
