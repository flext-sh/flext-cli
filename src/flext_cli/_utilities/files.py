"""Generic filesystem helpers shared through ``u.Cli``."""

from __future__ import annotations

import csv
import hashlib
import os
import shutil
import tempfile
from collections.abc import (
    Mapping,
    Sequence,
)
from pathlib import Path

from flext_cli import (
    FlextCliUtilitiesJson as uj,
    FlextCliUtilitiesYaml as uy,
    c,
    p,
    r,
    t,
)
from flext_core import m


class FlextCliUtilitiesFiles:
    """Generic filesystem operations for utility consumers."""

    @staticmethod
    def files_delete(file_path: t.Cli.TextPath) -> p.Result[bool]:
        """Delete one file path using canonical error handling."""
        path = Path(file_path)
        return FlextCliUtilitiesFiles.files_execute_bool(
            path.unlink,
            c.Cli.ERR_FILE_DELETION_FAILED,
        )

    @staticmethod
    def files_read_text(file_path: t.Cli.TextPath) -> p.Result[str]:
        """Read one UTF-8 text file."""
        return FlextCliUtilitiesFiles.files_execute(
            lambda: Path(file_path).read_text(encoding=c.Cli.ENCODING_DEFAULT),
            "Text read failed: {error}",
        )

    @staticmethod
    def files_write_text(file_path: t.Cli.TextPath, content: str) -> p.Result[bool]:
        """Write one UTF-8 text file."""

        def _write() -> bool:
            Path(file_path).write_text(content, encoding=c.Cli.ENCODING_DEFAULT)
            return True

        return FlextCliUtilitiesFiles.files_execute(
            _write,
            "Text write failed: {error}",
        )

    @staticmethod
    def files_read_json(file_path: t.Cli.TextPath) -> p.Result[t.JsonValue]:
        """Read one JSON file and validate to canonical JSON value."""

        def _load() -> t.JsonValue:
            raw = Path(file_path).read_text(encoding=c.Cli.ENCODING_DEFAULT)
            return t.Cli.JSON_VALUE_ADAPTER.validate_json(raw)

        return FlextCliUtilitiesFiles.files_execute(
            _load,
            c.Cli.ERR_JSON_LOAD_FAILED,
        )

    @staticmethod
    def files_read_json_model[M: m.BaseModel](
        file_path: t.Cli.TextPath,
        model_type: type[M],
    ) -> p.Result[M]:
        """Read one JSON file directly into one Pydantic model."""

        def _load() -> M:
            raw = Path(file_path).read_bytes()
            return model_type.model_validate_json(raw, strict=False)

        return FlextCliUtilitiesFiles.files_execute(
            _load,
            c.Cli.ERR_JSON_LOAD_FAILED,
        )

    @staticmethod
    def files_write_json_model(
        file_path: t.Cli.TextPath,
        model: m.BaseModel,
        *,
        indent: int,
        by_alias: bool,
        exclude_none: bool,
    ) -> p.Result[bool]:
        """Write one Pydantic model to JSON text."""

        def _write() -> bool:
            json_str = model.model_dump_json(
                indent=indent,
                by_alias=by_alias,
                exclude_none=exclude_none,
            )
            Path(file_path).write_text(json_str, encoding=c.Cli.ENCODING_DEFAULT)
            return True

        return FlextCliUtilitiesFiles.files_execute(
            _write,
            c.Cli.ERR_JSON_WRITE_FAILED,
        )

    @staticmethod
    def files_read_yaml(file_path: t.Cli.TextPath) -> p.Result[t.JsonValue]:
        """Read one YAML file and validate to canonical JSON value."""
        result = uy.yaml_safe_load(Path(file_path))
        if result.failure:
            return r[t.JsonValue].fail(result.error or "YAML load failed")
        validated: t.JsonValue = t.Cli.JSON_VALUE_ADAPTER.validate_python(
            result.value,
        )
        return r[t.JsonValue].ok(validated)

    @staticmethod
    def files_write_csv(
        file_path: t.Cli.TextPath,
        rows: Sequence[t.StrSequence],
    ) -> p.Result[bool]:
        """Write one CSV file from row sequence."""

        def _write() -> bool:
            with Path(file_path).open(
                mode="w",
                encoding=c.Cli.ENCODING_DEFAULT,
                newline="",
            ) as handle:
                writer = csv.writer(handle)
                for row in rows:
                    writer.writerow(list(row))
            return True

        return FlextCliUtilitiesFiles.files_execute(
            _write,
            "CSV write failed: {error}",
        )

    @staticmethod
    def files_read_csv_with_headers(
        file_path: t.Cli.TextPath,
    ) -> p.Result[Sequence[t.StrMapping]]:
        """Read one CSV file into mapping rows using header row."""

        def _load() -> Sequence[t.StrMapping]:
            with Path(file_path).open(
                encoding=c.Cli.ENCODING_DEFAULT,
                newline="",
            ) as handle:
                return [dict(row) for row in csv.DictReader(handle)]

        return FlextCliUtilitiesFiles.files_execute(
            _load,
            "CSV read failed: {error}",
        )

    @staticmethod
    def files_read_binary(file_path: t.Cli.TextPath) -> p.Result[bytes]:
        """Read one binary file."""
        return FlextCliUtilitiesFiles.files_execute(
            lambda: Path(file_path).read_bytes(),
            "Binary read failed: {error}",
        )

    @staticmethod
    def files_write_binary(file_path: t.Cli.TextPath, data: bytes) -> p.Result[bool]:
        """Write one binary file."""

        def _write() -> bool:
            Path(file_path).write_bytes(data)
            return True

        return FlextCliUtilitiesFiles.files_execute(
            _write,
            "Binary write failed: {error}",
        )

    @staticmethod
    def files_copy(
        source_path: t.Cli.TextPath,
        destination_path: t.Cli.TextPath,
    ) -> p.Result[bool]:
        """Copy one file preserving metadata."""

        def _copy() -> bool:
            shutil.copy2(source_path, destination_path)
            return True

        return FlextCliUtilitiesFiles.files_execute(
            _copy,
            "File copy failed: {error}",
        )

    @staticmethod
    def files_execute[T](
        operation_func: t.Cli.NullaryOperation[T],
        error_template: str,
        **format_kwargs: t.Scalar,
    ) -> p.Result[T]:
        """Execute one operation and map common runtime errors to ``r``."""
        try:
            return r[T].ok(operation_func())
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as exc:
            return r[T].fail(error_template.format(error=exc, **format_kwargs))

    @staticmethod
    def files_execute_bool[T](
        operation_func: t.Cli.NullaryOperation[T],
        error_template: str,
        **format_kwargs: t.Scalar,
    ) -> p.Result[bool]:
        """Execute one operation that should return a success boolean."""

        def _run() -> bool:
            _ = operation_func()
            return True

        return FlextCliUtilitiesFiles.files_execute(
            _run,
            error_template,
            **format_kwargs,
        )

    @staticmethod
    def ensure_dir(path: t.Cli.TextPath) -> p.Result[Path]:
        """Create a directory tree when missing and return the resolved path."""
        target = Path(path)
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return r[Path].fail(
                c.Cli.ERR_ENSURE_DIR_FAILED.format(error=exc),
            )
        return r[Path].ok(target)

    @staticmethod
    def ensure_symlink(
        target: t.Cli.TextPath, source: t.Cli.TextPath
    ) -> p.Result[bool]:
        """Ensure target points to source via directory symlink."""
        target_path = Path(target)
        source_path = Path(source).resolve()
        ensure_result = FlextCliUtilitiesFiles.ensure_dir(target_path.parent)
        if ensure_result.failure:
            return r[bool].fail(
                ensure_result.error or f"failed to create parent dir for {target_path}",
            )
        try:
            if target_path.is_symlink() and target_path.resolve() == source_path:
                return r[bool].ok(True)
            if target_path.exists() or target_path.is_symlink():
                if target_path.is_dir() and (not target_path.is_symlink()):
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            target_path.symlink_to(source_path, target_is_directory=True)
        except OSError as exc:
            return r[bool].fail(f"failed to ensure symlink for {target_path}: {exc}")
        return r[bool].ok(True)

    @staticmethod
    def atomic_write_text_file(
        file_path: t.Cli.TextPath, content: str
    ) -> p.Result[bool]:
        """Write a text file atomically via tempfile + replace in the same directory."""
        path = Path(file_path)
        ensure_result = FlextCliUtilitiesFiles.ensure_dir(path.parent)
        if ensure_result.failure:
            return r[bool].fail(
                ensure_result.error or c.Cli.ERR_ENSURE_DIR_GENERIC_FAILED,
            )
        try:
            fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding=c.Cli.ENCODING_DEFAULT) as handle:
                    handle.write(content)
                Path(tmp_path).replace(path)
            except BaseException:
                Path(tmp_path).unlink(missing_ok=True)
                raise
        except OSError as exc:
            return r[bool].fail(
                c.Cli.ERR_ATOMIC_WRITE_TEXT_FILE_FAILED.format(
                    error=exc,
                ),
            )
        return r[bool].ok(True)

    @staticmethod
    def sha256_content(content: str) -> str:
        """Return the SHA-256 hex digest for text content."""
        return hashlib.sha256(content.encode(c.Cli.ENCODING_DEFAULT)).hexdigest()

    @staticmethod
    def sha256_file(file_path: t.Cli.TextPath) -> str:
        """Return the SHA-256 hex digest for a file on disk."""
        path = Path(file_path)
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def files_detect_format(file_path: t.Cli.TextPath) -> p.Result[str]:
        """Detect one file format from extension using canonical output enums."""
        match Path(file_path).suffix.lower():
            case ".json":
                return r[str].ok(c.Cli.OutputFormats.JSON)
            case ".yaml" | ".yml":
                return r[str].ok(c.Cli.OutputFormats.YAML)
            case ".csv":
                return r[str].ok(c.Cli.OutputFormats.CSV)
            case ".txt" | ".log":
                return r[str].ok(c.Cli.OutputFormats.TEXT)
            case "":
                return r[str].fail("Unable to detect file format without an extension")
            case unknown:
                return r[str].fail(f"Unsupported format: {unknown}")

    @staticmethod
    def files_load_auto_mapping(
        file_path: t.Cli.TextPath,
    ) -> p.Result[t.JsonMapping]:
        """Load JSON/YAML file and normalize to one mapping payload."""
        path = Path(file_path)
        if path.suffix.lower() == ".json":
            read_result = uj.json_read(path)
        elif path.suffix.lower() in {".yaml", ".yml"}:
            read_result = uy.yaml_safe_load(path)
        else:
            return r[t.JsonMapping].fail(
                f"Unsupported format: {path.suffix or '<none>'}",
            )
        if read_result.failure:
            return r[t.JsonMapping].fail(read_result.error or "Auto load failed")
        payload = read_result.value
        if not isinstance(payload, Mapping):
            return r[t.JsonMapping].fail(
                "Auto-detected file must contain a mapping",
            )
        normalized_payload: t.JsonMapping = {
            str(key): uj.normalize_json_value(value) for key, value in payload.items()
        }
        return r[t.JsonMapping].ok(normalized_payload)


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesFiles"]
