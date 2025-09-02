"""FlextCliUtils - Class-based CLI utilities (no module-level helpers)."""

from __future__ import annotations

import asyncio
import csv
import importlib
import json
import shlex
from collections.abc import Callable
from pathlib import Path

from flext_core import FlextResult

from flext_cli.typings import FlextCliOutputFormat

type FlextCliData = dict[str, object] | list[object] | str | int | float | None


class FlextCliUtils:
    """Class-based utilities for CLI workflows."""

    # ------------------------- File IO -------------------------
    @staticmethod
    def load_json_file(path: Path) -> FlextResult[dict[str, object]]:
        if not path.exists():
            return FlextResult[dict[str, object]].fail("File not found")
        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            if not isinstance(data, dict):
                return FlextResult[dict[str, object]].fail(
                    "JSON root must be an object"
                )
            return FlextResult[dict[str, object]].ok(data)
        except json.JSONDecodeError as e:
            return FlextResult[dict[str, object]].fail(f"JSON decode error: {e}")
        except Exception as e:
            return FlextResult[dict[str, object]].fail(str(e))

    @staticmethod
    def save_json_file(data: dict[str, object], path: Path) -> FlextResult[None]:
        try:
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(str(e))

    @staticmethod
    def load_text_file(path: Path) -> FlextResult[str]:
        try:
            content = Path(path).read_text(encoding="utf-8")
            return FlextResult[str].ok(content)
        except Exception as e:
            return FlextResult[str].fail(str(e))

    @staticmethod
    def save_text_file(content: str, path: Path) -> FlextResult[None]:
        try:
            Path(path).write_text(content, encoding="utf-8")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(str(e))

    @staticmethod
    def load_yaml_file(path: Path) -> FlextResult[object]:
        if not path.exists():
            return FlextResult[object].fail("File not found")
        try:
            yaml_mod = importlib.import_module("yaml")
            data = yaml_mod.safe_load(path.read_text(encoding="utf-8"))
            return FlextResult[object].ok(data)
        except Exception as e:
            return FlextResult[object].fail(f"YAML parse error: {e}")

    @staticmethod
    def save_yaml_file(data: object, path: Path) -> FlextResult[None]:
        try:
            yaml_mod = importlib.import_module("yaml")
            text = yaml_mod.safe_dump(data)
            path.write_text(text, encoding="utf-8")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(str(e))

    @staticmethod
    def load_csv_file(path: Path) -> FlextResult[list[dict[str, str]]]:
        try:
            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                return FlextResult[list[dict[str, str]]].ok([dict(r) for r in reader])
        except Exception as e:
            return FlextResult[list[dict[str, str]]].fail(str(e))

    @staticmethod
    def save_csv_file(data: list[dict[str, object]], path: Path) -> FlextResult[None]:
        try:
            if not data:
                path.write_text("", encoding="utf-8")
                return FlextResult[None].ok(None)
            keys = list(data[0].keys())
            with path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for row in data:
                    writer.writerow({k: row.get(k, "") for k in keys})
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(str(e))

    # ---------------------- Serialization ----------------------
    @staticmethod
    def convert_to_serializable(value: object) -> object:
        try:
            if isinstance(value, Path):
                return str(value)
            if (
                hasattr(value, "hex")
                and hasattr(value, "version")
                and hasattr(value, "__str__")
            ):
                return str(value)
            return value
        except Exception:
            return str(value)

    # --------------------------- CLI ---------------------------
    @staticmethod
    def format_output(data: object, fmt: FlextCliOutputFormat) -> FlextResult[str]:
        if fmt == FlextCliOutputFormat.JSON:
            try:
                return FlextResult[str].ok(json.dumps(data, ensure_ascii=False))
            except (TypeError, ValueError) as e:
                return FlextResult[str].fail(str(e))
        return FlextResult[str].ok(str(data))

    @staticmethod
    def load_data_file(path: Path) -> FlextResult[object]:
        suffix = path.suffix.lower()
        if suffix == ".json":
            json_result = FlextCliUtils.load_json_file(path)
            if json_result.is_failure:
                return FlextResult[object].fail(json_result.error or "JSON load failed")
            return FlextResult[object].ok(json_result.unwrap())
        if suffix in {".txt", ".log"}:
            text_result = FlextCliUtils.load_text_file(path)
            if text_result.is_failure:
                return FlextResult[object].fail(text_result.error or "Text load failed")
            return FlextResult[object].ok(text_result.unwrap())
        if suffix in {".yaml", ".yml"}:
            return FlextCliUtils.load_yaml_file(path)
        if suffix == ".csv":
            csv_result = FlextCliUtils.load_csv_file(path)
            if csv_result.is_failure:
                return FlextResult[object].fail(csv_result.error or "CSV load failed")
            return FlextResult[object].ok(csv_result.unwrap())
        return FlextResult[object].fail("Unsupported file format")

    @staticmethod
    def save_data_file(
        data: FlextCliData, path: Path, format_hint: FlextCliOutputFormat
    ) -> FlextResult[None]:
        # Determine format based on hint or file extension
        is_json = (
            format_hint == FlextCliOutputFormat.JSON or path.suffix.lower() == ".json"
        )
        is_csv = (
            format_hint == FlextCliOutputFormat.CSV or path.suffix.lower() == ".csv"
        )
        is_yaml = format_hint == FlextCliOutputFormat.YAML or path.suffix.lower() in {
            ".yaml",
            ".yml",
        }

        if is_json:
            if not isinstance(data, (dict, list)):
                return FlextResult[None].fail("JSON target requires dict or list data")
            serializable = json.loads(json.dumps(data, default=str))
            if not isinstance(serializable, dict):
                return FlextResult[None].fail("JSON target requires a JSON object")
            return FlextCliUtils.save_json_file(serializable, path)

        if is_csv:
            if not (isinstance(data, list) and (not data or isinstance(data[0], dict))):
                return FlextResult[None].fail(
                    "CSV export requires list of dictionaries"
                )
            # Ensure data is list of dicts for CSV
            csv_data: list[dict[str, object]] = []
            if isinstance(data, list):
                csv_data.extend(item for item in data if isinstance(item, dict))
            return FlextCliUtils.save_csv_file(csv_data, path)

        if is_yaml:
            return FlextCliUtils.save_yaml_file(data, path)

        return FlextCliUtils.save_text_file(str(data), path)

    @staticmethod
    def create_table(data: object, title: str | None = None) -> FlextResult[object]:
        try:
            from rich.table import Table

            table = Table(title=title)
            if isinstance(data, list):
                if len(data) == 0:
                    return FlextResult[object].fail(
                        "Empty list has no table representation"
                    )
                first = data[0]
                if isinstance(first, dict):
                    for k in first:
                        table.add_column(str(k))
                    for row in data:
                        table.add_row(*[str(row.get(k, "")) for k in first])
                else:
                    table.add_column("value")
                    for v in data:
                        table.add_row(str(v))
            elif isinstance(data, dict):
                table.add_column("Key")
                table.add_column("Value")
                for k, v in data.items():
                    table.add_row(str(k), str(v))
            else:
                table.add_column("Value")
                table.add_row(str(data))
            return FlextResult[object].ok(table)
        except Exception as e:
            return FlextResult[object].fail(str(e))

    @staticmethod
    def run_command(command_line: str) -> FlextResult[dict[str, object]]:
        try:
            args = shlex.split(command_line)

            async def _run() -> dict[str, object]:
                proc = await asyncio.create_subprocess_exec(
                    *args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout_b, stderr_b = await proc.communicate()
                return {
                    "stdout": stdout_b.decode(),
                    "stderr": stderr_b.decode(),
                    "exit_code": proc.returncode,
                }

            result = asyncio.run(_run())
            result["returncode"] = result.get("exit_code", 1)
            exit_code = result.get("exit_code", 1)
            if isinstance(exit_code, int) and exit_code == 0:
                return FlextResult[dict[str, object]].ok(result)
            return FlextResult[dict[str, object]].fail(
                "Command failed: " + str(result.get("stderr", "") or "Command failed")
            )
        except Exception as e:
            return FlextResult[dict[str, object]].fail(str(e))

    # -------- batch processing --------
    @staticmethod
    def batch_process_files(
        files: list[Path],
        processor: Callable[[Path], FlextResult[object]],
        *,
        show_progress: bool = False,
    ) -> FlextResult[dict[str, object]]:
        try:
            _ = show_progress
            results: dict[str, object] = {
                "processed": 0,
                "failed": 0,
                "successful": [],
                "errors": [],
            }
            for file_path in files:
                res = processor(file_path)
                if res.is_success:
                    processed = results["processed"]
                    results["processed"] = (
                        int(processed) if isinstance(processed, (int, str)) else 0
                    ) + 1
                    successful_obj = results.get("successful", [])
                    successes = (
                        list(successful_obj) if isinstance(successful_obj, list) else []
                    )
                    successes.append(str(file_path))
                    results["successful"] = successes
                else:
                    failed = results["failed"]
                    results["failed"] = (
                        int(failed) if isinstance(failed, (int, str)) else 0
                    ) + 1
                    errors_obj = results.get("errors", [])
                    errors = list(errors_obj) if isinstance(errors_obj, list) else []
                    errors.append(
                        {
                            "file": str(file_path),
                            "error": res.error or "Unknown error",
                        }
                    )
                    results["errors"] = errors
            return FlextResult[dict[str, object]].ok(results)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(str(e))

    # -------- convenience bridges for tests --------
    @staticmethod
    def process_single_file(
        path: Path,
        processor: Callable[[Path], FlextResult[object]],
        results: dict[str, object],
        *,
        fail_fast: bool,
    ) -> tuple[bool, str | None]:
        try:
            res = processor(path)
            if res.is_success:
                processed = results.get("processed", 0)
                results["processed"] = (
                    int(processed) if isinstance(processed, (int, str)) else 0
                ) + 1
                successful_obj = results.get("successful", [])
                successes = (
                    list(successful_obj) if isinstance(successful_obj, list) else []
                )
                successes.append(str(path))
                results["successful"] = successes
                return False, None
            failed = results.get("failed", 0)
            results["failed"] = (
                int(failed) if isinstance(failed, (int, str)) else 0
            ) + 1
            errors_obj = results.get("errors", [])
            errors = list(errors_obj) if isinstance(errors_obj, list) else []
            errors.append({"file": str(path), "error": res.error or "Unknown error"})
            results["errors"] = errors
            return (True, res.error) if fail_fast else (False, None)
        except Exception as e:
            failed = results.get("failed", 0)
            results["failed"] = (
                int(failed) if isinstance(failed, (int, str)) else 0
            ) + 1
            errors_obj = results.get("errors", [])
            errors = list(errors_obj) if isinstance(errors_obj, list) else []
            errors.append({"file": str(path), "error": str(e)})
            results["errors"] = errors
            return (True, str(e)) if fail_fast else (False, None)

    @staticmethod
    def create_directory_structure(
        base_path: Path, dir_names: list[str]
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        for name in dir_names:
            p = base_path / name
            p.mkdir(parents=True, exist_ok=True)
            result[f"dir_{name}"] = str(p)
        return result

    @staticmethod
    def init_git_repo(project_path: Path) -> bool:
        try:
            mod = importlib.import_module("git")
            repo_cls = getattr(mod, "Repo", None)
            if repo_cls is None:
                return False
            repo_cls.init(str(project_path))
            return True
        except Exception:
            return False

    @staticmethod
    def write_basic_pyproject(project_name: str, project_path: Path) -> Path:
        project_path.mkdir(parents=True, exist_ok=True)
        pyproject = project_path / "pyproject.toml"
        content = (
            "[project]\n"
            f'name = "{project_name}"\n'
            'version = "0.1.0"\n'
            'requires-python = "\\>=3.13"\n'
        )
        pyproject.write_text(content, encoding="utf-8")
        return pyproject


__all__ = ["FlextCliData", "FlextCliUtils"]
