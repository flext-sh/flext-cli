#!/usr/bin/env python3
"""Extract all hard-coded strings from flext-cli source code.

This script scans all Python files in src/flext_cli (except constants.py and typings.py)
and extracts hard-coded string literals for migration to constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import json
import re
from collections import defaultdict
from pathlib import Path

# Configuration
SRC_DIR = Path("src/flext_cli")
EXCLUDE_FILES = {"constants.py", "typings.py", "__pycache__"}
MIN_STRING_LENGTH = 2
OUTPUT_FILE = "hardcoded_strings_analysis.json"

# String patterns to exclude (commonly acceptable)
EXCLUDE_PATTERNS = [
    r"^[a-z_]+$",  # Simple variable names
    r"^__[a-z_]+__$",  # Dunder names
    r"^\d+$",  # Pure numbers
    r"^[,\.\-\s]+$",  # Punctuation only
]

# Categories for classification
CATEGORIES = {
    "error_messages": r"(error|fail|invalid|cannot|must|required|missing)",
    "validation_messages": r"(validat|check|verif|ensur)",
    "service_messages": r"(operational|available|status|service)",
    "dict_keys": r"^[a-z][a-z0-9_]*$",  # Simple snake_case keys
    "paths": r"(\.py|\.json|\.yaml|\.yml|\.toml|/|\\\\)",
    "formats": r"(json|yaml|table|csv|grid|format)",
    "http": r"(http://|https://|api|url)",
    "file_operations": r"(read|write|open|close|encoding|utf)",
}


def should_exclude(string: str) -> bool:
    """Check if string should be excluded from analysis."""
    if len(string) < MIN_STRING_LENGTH:
        return True

    return any(re.match(pattern, string, re.IGNORECASE) for pattern in EXCLUDE_PATTERNS)


def categorize_string(string: str, _context: str) -> str:
    """Categorize a string based on its content and context.

    Args:
        string: The string to categorize.
        _context: The line context (currently unused, reserved for future enhancement).

    Returns:
        The category name.

    """
    string_lower = string.lower()

    # Check each category
    for category, pattern in CATEGORIES.items():
        if re.search(pattern, string_lower, re.IGNORECASE):
            return category

    # Default category
    if len(string) > 50:
        return "messages"
    if "/" in string or "\\" in string:
        return "paths"
    if string.isupper() or string.upper() == string:
        return "constants"

    return "misc"


def extract_strings_from_file(file_path: Path) -> list[dict]:
    """Extract all hard-coded strings from a Python file."""
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return []

    # Pattern to match string literals (handles both ' and " and escapes)
    string_pattern = re.compile(
        r"""(?P<type>[frbFRB]?)(?P<quote>["'])(?P<content>(?:(?!(?<!\\)\2).)*)\2""",
        re.DOTALL,
    )

    strings_found = []
    lines = content.split("\n")

    for match in string_pattern.finditer(content):
        string_type = match.group("type")
        string_content = match.group("content")

        # Skip if should be excluded
        if should_exclude(string_content):
            continue

        # Skip docstrings (naive check - could be improved)
        if len(string_content) > 100 and "\n" in string_content:
            continue

        # Get line number and context
        line_num = content[: match.start()].count("\n") + 1
        line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""

        # Categorize
        category = categorize_string(string_content, line_content)

        strings_found.append({
            "line": line_num,
            "string": string_content,
            "type": string_type or "normal",
            "context": line_content[:100],
            "category": category,
        })

    return strings_found


def main() -> None:
    """Main extraction process."""
    # Get all Python files
    py_files = sorted(SRC_DIR.glob("*.py"))
    py_files = [f for f in py_files if f.name not in EXCLUDE_FILES]

    # Extract strings from all files
    all_strings = {}
    category_counts: defaultdict[str, int] = defaultdict(int)
    total_strings = 0

    for py_file in py_files:
        strings = extract_strings_from_file(py_file)

        if strings:
            all_strings[py_file.name] = strings
            total_strings += len(strings)

            # Count categories
            for s in strings:
                category_counts[s["category"]] += 1

    # Generate analysis report
    report = {
        "summary": {
            "total_files_scanned": len(py_files),
            "files_with_strings": len(all_strings),
            "total_strings": total_strings,
            "category_breakdown": dict[str, object](category_counts),
        },
        "strings_by_file": all_strings,
    }

    # Save to JSON
    output_path = Path(OUTPUT_FILE)
    with Path(output_path).open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Print summary
    for _category, _count in sorted(category_counts.items(), key=lambda x: -x[1]):
        pass


if __name__ == "__main__":
    main()
