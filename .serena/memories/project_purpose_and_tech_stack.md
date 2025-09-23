# FLEXT-CLI Project Purpose and Tech Stack

## Project Purpose
FLEXT-CLI is the CLI FOUNDATION library for the entire FLEXT ecosystem. It serves as:
- Universal CLI interface for all 32+ FLEXT projects
- Click/Rich abstraction layer with ZERO TOLERANCE for direct imports
- CLI output standardization (tables, progress bars, formatting)
- Configuration management for CLI tools across ecosystem

## Tech Stack
- **Python**: 3.13+ (strict requirement)
- **Core Framework**: Built on flext-core 0.9.9 RC (1.0.0 preparation)
- **CLI Framework**: Click 8.2+ (abstracted through flext-cli)
- **Rich Output**: Rich 14.0+ (abstracted through flext-cli)
- **Validation**: Pydantic 2.11+ 
- **HTTP**: httpx 0.28.1+
- **Data Processing**: pandas 2.2.0+
- **Package Management**: Poetry
- **Quality Tools**: Ruff, MyPy, PyRight, Pytest, Bandit

## Architecture Principles
- Single unified class per module (MANDATORY)
- FlextResult railway pattern for all operations
- No helper functions outside classes (use nested classes)
- Zero tolerance for `try/except` fallbacks
- Direct flext-core imports only (no wrappers/aliases)
- 75% minimum test coverage target

## Current Status
- Version: 0.9.0 (targeting 1.0.0 stable release)
- Functionality: 30% → targeting 75%+
- Quality: ZERO TOLERANCE standards enforced