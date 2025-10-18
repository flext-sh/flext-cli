#!/usr/bin/env python3
"""Migrate hard-coded strings to constants.py automatically.

This script processes the hardcoded_strings_analysis.json file and migrates
critical strings (error messages, validation messages, service messages, formats, paths, dict_keys)
to constants.py, then updates the source files.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

import json
import re
from collections import defaultdict
from pathlib import Path

# Configuration
ANALYSIS_FILE = "hardcoded_strings_analysis.json"
CONSTANTS_FILE = "src/flext_cli/constants.py"
SRC_DIR = Path("src/flext_cli")

# Categories to auto-migrate to constants.py
CRITICAL_CATEGORIES = {
    "error_messages",
    "validation_messages",
    "service_messages",
    "formats",
    "paths",
    "dict_keys",
}


# Constant name generators
def generate_constant_name(string: str, category: str) -> str:
    """Generate a constant name from a string."""
    # Remove format placeholders for naming
    cleaned = re.sub(r"\{[^}]+\}", "", string)
    # Take first 50 chars, convert to uppercase snake case
    words = re.findall(r"[a-zA-Z0-9]+", cleaned[:50])
    name = "_".join(words).upper()

    # Add category prefix
    if category == "error_messages":
        prefix = "ERR_"
    elif category == "validation_messages":
        prefix = "VAL_"
    elif category == "service_messages":
        prefix = "SVC_"
    elif category == "formats":
        prefix = "FMT_"
    elif category == "paths":
        prefix = "PATH_"
    elif category == "dict_keys":
        prefix = "KEY_"
    else:
        prefix = ""

    return f"{prefix}{name}"


def collect_strings_to_migrate() -> dict[str, list[dict[str, str | int]]]:
    """Collect all strings that should be migrated to constants."""
    with Path(ANALYSIS_FILE).open(encoding="utf-8") as f:
        data = json.load(f)

    # Group strings by category
    strings_by_category: defaultdict[str, list[dict[str, str | int]]] = defaultdict(
        list
    )

    for module, strings in data["strings_by_file"].items():
        for s in strings:
            category = s["category"]
            if category in CRITICAL_CATEGORIES:
                strings_by_category[category].append({
                    "string": s["string"],
                    "module": module,
                    "line": s["line"],
                    "context": s["context"],
                })

    return strings_by_category


def generate_constants_additions(
    strings_by_category: dict[str, list[dict[str, str | int]]],
) -> tuple[dict[str, list[str]], dict[str, str]]:
    """Generate constant definitions to add to constants.py."""
    additions: dict[str, list[str]] = {}
    constant_names: dict[str, str] = {}

    for category, strings in strings_by_category.items():
        category_constants = []
        seen_names = set()

        # Deduplicate strings
        unique_strings = {}
        for s in strings:
            string_val = s["string"]
            if string_val not in unique_strings:
                unique_strings[string_val] = s

        for string_val in unique_strings:
            # Generate constant name
            const_name = generate_constant_name(string_val, category)

            # Handle duplicates
            original_name = const_name
            counter = 2
            while const_name in seen_names:
                const_name = f"{original_name}_{counter}"
                counter += 1

            seen_names.add(const_name)

            # Store mapping for replacement
            if string_val not in constant_names:
                constant_names[string_val] = const_name

            # Format constant definition
            category_constants.append(f'    {const_name}: str = "{string_val}"')

        additions[category] = category_constants

    return additions, constant_names


def main() -> None:
    """Main migration process."""
    # Collect strings
    strings_by_category = collect_strings_to_migrate()

    sum(len(strings) for strings in strings_by_category.values())
    for _category, _strings in sorted(
        strings_by_category.items(), key=lambda x: -len(x[1])
    ):
        pass

    # Generate constants
    additions, constant_names = generate_constants_additions(strings_by_category)

    # Count unique constants
    sum(len(consts) for consts in additions.values())

    # Save to file for manual review
    output_file = "constants_to_add.txt"
    with Path(output_file).open("w", encoding="utf-8") as f:
        f.write("# Constants to add to constants.py\n")
        f.write("# Review and add to appropriate sections\n\n")

        for category in CRITICAL_CATEGORIES:
            if category in additions:
                f.write(f"\n# {category.upper().replace('_', ' ')}\n")
                f.writelines(f"{const_def}\n" for const_def in additions[category])

    # Save mapping for replacement
    mapping_file = "string_to_constant_mapping.json"
    with Path(mapping_file).open("w", encoding="utf-8") as f:
        json.dump(constant_names, f, indent=2)


if __name__ == "__main__":
    main()
