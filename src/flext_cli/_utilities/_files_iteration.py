"""Git-aware file iteration shared through ``u.Cli``."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli import config, r, t
from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime

if TYPE_CHECKING:
    from flext_cli import p


class FlextCliUtilitiesFileIteration:
    """Select files deterministically from Git state or the filesystem."""

    @classmethod
    def iter_matching_files(
        cls, root: Path, *, includes: t.StrSequence, excludes: t.StrSequence = ()
    ) -> p.Result[t.SequenceOf[Path]]:
        """Return matching files from one resolved, Git-aware scope Result."""
        if not root.is_dir():
            return r[t.SequenceOf[Path]].ok([])
        resolved_root = root.resolve()
        repository_root = cls._git_repository_root(resolved_root)
        if repository_root is None:
            candidates = cls._fallback_scope_paths(resolved_root)
        else:
            git_paths = cls._git_scope_paths(repository_root, resolved_root)
            if git_paths.failure:
                return r[t.SequenceOf[Path]].from_failure(git_paths)
            candidates = git_paths.value
        return r[t.SequenceOf[Path]].ok(
            sorted({
                path
                for path in candidates
                if path.is_file()
                if cls._matches(
                    path.relative_to(resolved_root),
                    includes=includes,
                    excludes=excludes,
                )
            })
        )

    @staticmethod
    def _matches(
        relative_path: Path, *, includes: t.StrSequence, excludes: t.StrSequence
    ) -> bool:
        """Return whether one scope-relative path satisfies configured globs."""
        path_text = relative_path.as_posix()
        included = not includes or any(
            fnmatch.fnmatch(path_text, pattern) for pattern in includes
        )
        excluded = any(fnmatch.fnmatch(path_text, pattern) for pattern in excludes)
        return included and not excluded

    @classmethod
    def _git_scope_paths(
        cls, repository_root: Path, scope_root: Path
    ) -> p.Result[t.SequenceOf[Path]]:
        """Return Git-visible files under ``scope_root`` or a typed failure."""
        policy = config.Cli.file_iteration
        files_result = FlextCliUtilitiesRuntime.run(
            (policy.executable, *policy.scope_files_args),
            cwd=repository_root,
            timeout=policy.timeout_seconds,
        )
        if files_result.failure:
            return r[t.SequenceOf[Path]].from_failure(files_result)
        return r[t.SequenceOf[Path]].ok(
            cls._scope_paths_from_output(
                repository_root,
                scope_root,
                files_result.value.stdout,
                separator=policy.output_separator,
            )
        )

    @staticmethod
    def _fallback_scope_paths(scope_root: Path) -> t.SequenceOf[Path]:
        """Return non-hidden regular files for a non-Git filesystem scope."""
        excluded_prefixes = config.Cli.file_iteration.fallback_excluded_segment_prefixes
        return [
            path
            for path in scope_root.rglob("*")
            if path.is_file()
            if not any(
                part.startswith(prefix)
                for part in path.relative_to(scope_root).parts
                for prefix in excluded_prefixes
            )
        ]

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
        repository_root: Path, scope_root: Path, output: str, *, separator: str
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
