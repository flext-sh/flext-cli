"""Test final refactored structure."""

from pathlib import Path

# Test structure
structure = {
    "api.py": Path("api.py").exists(),
    "flext_cli.py": Path("flext_cli.py").exists(),
    "backups": all(
        Path(f"{name}.bak").exists()
        for name in ["cli_base.py", "domain.py", "formatters.py"]
    ),
}

for _name, _exists in structure.items():
    pass

# Test file sizes
sizes = {
    "api.py": Path("api.py").stat().st_size if Path("api.py").exists() else 0,
    "flext_cli.py": Path("flext_cli.py").stat().st_size
    if Path("flext_cli.py").exists()
    else 0,
}

for _name, _size in sizes.items():
    pass


# Count functions
try:
    with open("api.py", encoding="utf-8") as f:
        api_functions = f.read().count("def ")
    with open("flext_cli.py", encoding="utf-8") as f:
        cli_functions = f.read().count("def ")


except (RuntimeError, ValueError, TypeError):
    pass
