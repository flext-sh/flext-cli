#!/usr/bin/env python3
"""Script to convert FlextCliFileTools from service to simple class."""

import re
from pathlib import Path


def convert_file_tools() -> None:
    """Convert FlextCliFileTools from FlextService to simple class."""
    file_path = Path("src/flext_cli/file_tools.py")

    # Read the file
    content = file_path.read_text(encoding="utf-8")

    # 1. Remove FlextService import
    content = content.replace(
        r"from flext_core import FlextResult, FlextService, FlextTypes",
        "from flext_core import FlextResult, FlextTypes",
    )

    # 2. Change class declaration
    content = re.sub(
        r"class FlextCliFileTools\(FlextService\[dict\[str, object\]\]\):",
        "class FlextCliFileTools:",
        content,
    )

    # 3. Update docstring
    content = content.replace(
        '"""Unified file operations service following FLEXT namespace pattern.',
        '"""Unified file operations utility following FLEXT namespace pattern.',
    )
    content = content.replace(
        "Single class containing all file operations with nested helper classes",
        "Single class containing all stateless file operations with nested helper classes",
    )

    # 4. Remove __init__ method (lines 45-51)
    init_pattern = r"    def __init__\(self\) -> None:.*?self\._supported_formats = FlextCliConstants\.FILE_FORMATS\n\n    # Attributes initialized in __init__\n"
    content = re.sub(init_pattern, "", content, flags=re.DOTALL)

    # 5. Remove execute() method (lines 53-63)
    execute_pattern = r"    def execute\(self\) -> FlextResult\[dict\[str, object\]\]:.*?(?=\n    # =)"
    content = re.sub(execute_pattern, "", content, flags=re.DOTALL)

    # 6. Add @staticmethod to methods that don't already have it
    # Find all method definitions that don't have @staticmethod
    def add_staticmethod(match: re.Match[str]) -> str:
        """Add @staticmethod decorator if not present."""
        method_def = match.group(0)
        if "@staticmethod" not in method_def:
            indent = "    "
            return f"{indent}@staticmethod\n{method_def}"
        return method_def

    # Pattern for method definitions (4 spaces indent, def keyword)
    method_pattern = r"^    def \w+\(self,"
    content = re.sub(method_pattern, add_staticmethod, content, flags=re.MULTILINE)

    # 7. Remove 'self, ' parameter from all method signatures
    # This pattern catches 'self, ' followed by other parameters
    content = re.sub(r"\(self, ", "(", content)

    # Also catch 'self)' for methods with no other parameters
    content = re.sub(r"\(self\)", "()", content)

    # 8. Replace self._NestedClass with _NestedClass (nested class calls)
    content = content.replace("self._FileLoader", "_FileLoader")
    content = content.replace("self._FileSystemOps", "_FileSystemOps")
    content = content.replace("self._FormatDetector", "_FormatDetector")
    content = content.replace("self._FileSaver", "_FileSaver")

    # 9. Replace self.method_name() with FlextCliFileTools.method_name()
    # Find all self.method calls
    self_call_pattern = r"self\.(\w+)\("
    content = re.sub(self_call_pattern, r"FlextCliFileTools.\1(", content)

    # 10. Clean up any remaining 'self.' references
    # Check if there are any (there shouldn't be)
    if "self." in content:
        print("⚠️  Warning: Found remaining 'self.' references")
        for i, line in enumerate(content.split("\n"), 1):
            if "self." in line and not line.strip().startswith("#"):
                print(f"  Line {i}: {line.strip()}")

    # Write the converted file
    file_path.write_text(content, encoding="utf-8")
    print("✅ FlextCliFileTools converted successfully")
    print(f"   File: {file_path}")
    print(f"   Lines: {len(content.split(chr(10)))}")


if __name__ == "__main__":
    convert_file_tools()
