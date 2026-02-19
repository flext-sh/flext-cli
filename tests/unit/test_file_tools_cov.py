from __future__ import annotations

from pathlib import Path

from flext_cli.file_tools import FlextCliFileTools


def test_load_structured_file_returns_none_for_unsupported_loader_result(
    tmp_path: Path,
) -> None:
    source = tmp_path / "data.json"
    source.write_text("{}", encoding="utf-8")

    loaded = FlextCliFileTools._load_structured_file(str(source), lambda _f: {1, 2, 3})

    assert loaded is None


def test_load_file_auto_detect_fails_for_detected_csv_format(tmp_path: Path) -> None:
    csv_file = tmp_path / "records.csv"
    csv_file.write_text("id,name\n1,Alice\n", encoding="utf-8")

    result = FlextCliFileTools.load_file_auto_detect(csv_file)

    assert result.is_failure
    assert "Unsupported format" in (result.error or "")


def test_find_files_by_content_skips_directories(tmp_path: Path) -> None:
    target_file = tmp_path / "match.txt"
    target_file.write_text("needle", encoding="utf-8")
    (tmp_path / "nested").mkdir()

    result = FlextCliFileTools.find_files_by_content(tmp_path, "needle")

    assert result.is_success
    matches = result.value
    assert any(path.endswith("match.txt") for path in matches)
