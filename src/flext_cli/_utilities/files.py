"""Generic filesystem helpers shared through ``u.Cli``."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

from flext_cli import c, r, t


class FlextCliUtilitiesFiles:
    """Generic filesystem operations for utility consumers."""

    @staticmethod
    def ensure_dir(path: t.Cli.TextPath) -> r[Path]:
        """Create a directory tree when missing and return the resolved path."""
        target = Path(path)
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return r[Path].fail(f"ensure_dir: {exc}")
        return r[Path].ok(target)

    @staticmethod
    def atomic_write_text_file(file_path: t.Cli.TextPath, content: str) -> r[bool]:
        """Write a text file atomically via tempfile + replace in the same directory."""
        path = Path(file_path)
        ensure_result = FlextCliUtilitiesFiles.ensure_dir(path.parent)
        if ensure_result.is_failure:
            return r[bool].fail(ensure_result.error or "ensure_dir failed")
        try:
            fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding=c.Cli.Encoding.DEFAULT) as handle:
                    handle.write(content)
                Path(tmp_path).replace(path)
            except BaseException:
                Path(tmp_path).unlink(missing_ok=True)
                raise
        except OSError as exc:
            return r[bool].fail(f"atomic_write_text_file: {exc}")
        return r[bool].ok(True)

    @staticmethod
    def sha256_content(content: str) -> str:
        """Return the SHA-256 hex digest for text content."""
        return hashlib.sha256(content.encode(c.Cli.Encoding.DEFAULT)).hexdigest()

    @staticmethod
    def sha256_file(file_path: t.Cli.TextPath) -> str:
        """Return the SHA-256 hex digest for a file on disk."""
        path = Path(file_path)
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()


__all__ = ["FlextCliUtilitiesFiles"]
