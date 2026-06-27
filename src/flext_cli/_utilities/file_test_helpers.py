"""Test-oriented file helpers generalized for reuse through ``u.Cli``.

These operations are generic enough to be used by tests, examples, and
maintenance scripts, but were originally duplicated in ``flext-tests``.
They live here so ``flext-tests`` can delegate to ``u.Cli`` instead of
reimplementing them.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Generator, Mapping, MutableMapping
from contextlib import contextmanager
from pathlib import Path
from typing import cast

from flext_cli import c, p, r, t
from flext_cli._utilities.files import FlextCliUtilitiesFiles
from flext_cli._utilities.json import FlextCliUtilitiesJson as uj
from flext_cli._utilities.yaml import FlextCliUtilitiesYaml as uy


class FlextCliUtilitiesFileTestHelpersMixin:
    """Generic file helpers for tests and examples.

    Covers temporary file bundles, existence assertions, content comparison,
    and metadata extraction. All operations return ``r[T]`` and use canonical
    aliases ``c``, ``p``, ``r``, ``t``.
    """

    @classmethod
    @contextmanager
    def files_context(
        cls,
        content: Mapping[str, str | bytes | t.JsonValue | t.SequenceOf[t.StrSequence]],
        *,
        directory: Path | None = None,
        ext: str | None = None,
        cleanup: bool = True,
    ) -> Generator[Mapping[str, Path]]:
        """Create a temporary bundle of files and yield the path mapping.

        Args:
            content: Mapping from file name to raw content.
            directory: Optional base directory; uses a temp directory if omitted.
            ext: Optional extension appended to every file name.
            cleanup: Remove created files/directories on exit when True.

        Yields:
            Mapping[str, Path] with resolved file paths.

        """
        base_dir = directory or Path(tempfile.mkdtemp())
        created: dict[str, Path] = {}
        try:
            for name, raw in content.items():
                file_name = f"{name}{ext or ''}"
                file_path = base_dir / file_name
                FlextCliUtilitiesFiles.ensure_dir(file_path.parent)
                if isinstance(raw, bytes):
                    file_path.write_bytes(raw)
                elif isinstance(raw, str):
                    file_path.write_text(raw, encoding=c.Cli.ENCODING_DEFAULT)
                elif isinstance(raw, Mapping):
                    fmt = (
                        c.Cli.FILE_FORMAT_YAML
                        if file_path.suffix in {".yaml", ".yml"}
                        else c.Cli.FILE_FORMAT_JSON
                    )
                    cls._files_write_structured(file_path, raw, fmt)
                elif isinstance(raw, list):
                    FlextCliUtilitiesFiles.files_write_csv(
                        file_path,
                        cast("t.SequenceOf[t.StrSequence]", raw),
                    )
                else:
                    file_path.write_text(str(raw), encoding=c.Cli.ENCODING_DEFAULT)
                created[name] = file_path
            yield created
        finally:
            if cleanup:
                for path in created.values():
                    if path.exists() or path.is_symlink():
                        if path.is_dir():
                            shutil.rmtree(path)
                        else:
                            path.unlink()
                if directory is None and base_dir.exists():
                    shutil.rmtree(base_dir)

    @staticmethod
    def _files_write_structured(
        path: Path,
        data: t.JsonValue,
        fmt: str,
    ) -> p.Result[bool]:
        """Write a structured payload as JSON or YAML."""
        validated = t.Cli.JSON_VALUE_ADAPTER.validate_python(data)
        if fmt == c.Cli.FILE_FORMAT_YAML:
            dumped = uy.yaml_dump_str(validated)
            return FlextCliUtilitiesFiles.files_write_text(path, dumped)
        dumped_result = uj.json_dumps(validated)
        if dumped_result.failure:
            return r[bool].fail(dumped_result.error or "json_dumps failed")
        return FlextCliUtilitiesFiles.files_write_text(path, dumped_result.unwrap())

    @staticmethod
    def files_assert_exists(
        path: Path,
        *,
        is_file: bool | None = None,
        is_dir: bool | None = None,
        not_empty: bool | None = None,
        readable: bool | None = None,
        writable: bool | None = None,
    ) -> Path:
        """Assert file-system properties on ``path``.

        Args:
            path: Path to validate.
            is_file: Assert (or deny) that ``path`` is a regular file.
            is_dir: Assert (or deny) that ``path`` is a directory.
            not_empty: Assert that a file has content or a directory has entries.
            readable: Assert that ``path`` is readable.
            writable: Assert that ``path`` is writable.

        Returns:
            The validated ``path``.

        Raises:
            AssertionError: when any predicate fails.

        """
        if is_file is True and not path.is_file():
            msg = f"Expected file: {path}"
            raise AssertionError(msg)
        if is_file is False and path.is_file():
            msg = f"Expected non-file: {path}"
            raise AssertionError(msg)
        if is_dir is True and not path.is_dir():
            msg = f"Expected directory: {path}"
            raise AssertionError(msg)
        if is_dir is False and path.is_dir():
            msg = f"Expected non-directory: {path}"
            raise AssertionError(msg)
        if not_empty is True:
            if path.is_file() and path.stat().st_size == 0:
                msg = f"Expected non-empty file: {path}"
                raise AssertionError(msg)
            if path.is_dir() and not any(path.iterdir()):
                msg = f"Expected non-empty directory: {path}"
                raise AssertionError(msg)
        if readable is True and not os.access(path, os.R_OK):
            msg = f"Expected readable path: {path}"
            raise AssertionError(msg)
        if writable is True and not os.access(path, os.W_OK):
            msg = f"Expected writable path: {path}"
            raise AssertionError(msg)
        return path

    @staticmethod
    def files_compare(
        file1: Path,
        file2: Path,
        *,
        mode: str = "content",
        ignore_ws: bool = False,
        ignore_case: bool = False,
    ) -> p.Result[bool]:
        """Compare two files by content, size, hash, or lines.

        Args:
            file1: First file.
            file2: Second file.
            mode: ``content``, ``size``, ``hash``, or ``lines``.
            ignore_ws: Ignore whitespace for content/lines comparison.
            ignore_case: Case-insensitive comparison.

        Returns:
            ``r.ok(True)`` when equal, ``r.ok(False)`` when different, or
            ``r.fail(msg)`` on error.

        """
        if mode == "size":
            return r[bool].ok(file1.stat().st_size == file2.stat().st_size)
        if mode == "hash":
            return r[bool].ok(
                FlextCliUtilitiesFiles.sha256_file(file1)
                == FlextCliUtilitiesFiles.sha256_file(file2),
            )
        if mode == "lines":
            try:
                lines1 = file1.read_text(encoding=c.Cli.ENCODING_DEFAULT).splitlines()
                lines2 = file2.read_text(encoding=c.Cli.ENCODING_DEFAULT).splitlines()
            except OSError as exc:
                msg = f"Compare lines failed: {exc}"
                return r[bool].fail(msg)
            if ignore_ws:
                lines1 = ["".join(line.split()) for line in lines1]
                lines2 = ["".join(line.split()) for line in lines2]
            if ignore_case:
                lines1 = [line.lower() for line in lines1]
                lines2 = [line.lower() for line in lines2]
            return r[bool].ok(lines1 == lines2)
        try:
            text1 = file1.read_text(encoding=c.Cli.ENCODING_DEFAULT)
            text2 = file2.read_text(encoding=c.Cli.ENCODING_DEFAULT)
        except OSError as exc:
            msg = f"Compare content failed: {exc}"
            return r[bool].fail(msg)
        if ignore_ws:
            text1 = "".join(text1.split())
            text2 = "".join(text2.split())
        if ignore_case:
            text1 = text1.lower()
            text2 = text2.lower()
        return r[bool].ok(text1 == text2)

    @staticmethod
    def files_info(
        path: Path,
        *,
        compute_hash: bool = False,
        parse_content: bool = False,
    ) -> p.Result[Mapping[str, object]]:
        """Return generic file metadata.

        Args:
            path: File path.
            compute_hash: Include SHA-256 hex digest.
            parse_content: Parse JSON/YAML content and include as ``parsed``.

        Returns:
            ``r.ok(mapping)`` with keys such as ``exists``, ``size``,
            ``is_file``, ``is_dir``, ``format``, ``hash``, ``parsed``.

        """
        try:
            stat = path.stat()
        except OSError as exc:
            msg = f"files_info failed: {exc}"
            return r[Mapping[str, object]].fail(msg)

        info: MutableMapping[str, object] = {
            "exists": path.exists(),
            "path": str(path),
            "size": stat.st_size,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "format": FlextCliUtilitiesFiles.files_detect_format_from_path(path),
        }
        if compute_hash:
            info["hash"] = FlextCliUtilitiesFiles.sha256_file(path)
        if parse_content and path.is_file():
            parsed_result = FlextCliUtilitiesFileTestHelpersMixin._files_parse_content(
                path,
                str(info["format"]),
            )
            info["parsed"] = parsed_result
        return r[Mapping[str, object]].ok(info)

    @staticmethod
    def _files_parse_content(
        path: Path,
        fmt: str,
    ) -> p.Result[object]:
        """Parse JSON/YAML file content for ``files_info``."""
        if fmt == c.Cli.FILE_FORMAT_JSON:
            result = uj.json_read(path)
            if result.failure:
                return r[object].fail(result.error or "json_read failed")
            return r[object].ok(result.value)
        if fmt == c.Cli.FILE_FORMAT_YAML:
            result = uy.yaml_safe_load(path)
            if result.failure:
                return r[object].fail(result.error or "yaml_safe_load failed")
            return r[object].ok(result.value)
        msg = f"Cannot parse format: {fmt}"
        return r[object].fail(msg)
