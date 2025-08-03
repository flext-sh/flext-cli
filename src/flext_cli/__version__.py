"""FLEXT CLI Version Information - Package Metadata and Version Management.

This module provides centralized version information and metadata for FLEXT CLI,
including version numbers, release information, and package details. Used for
version management, compatibility checking, and release tracking.

Version Management:
    - Semantic versioning (MAJOR.MINOR.PATCH)
    - Version tuple for programmatic comparison
    - Development status and release metadata
    - Copyright and licensing information

Current Release Status:
    ✅ Version 0.9.0 - Development release with core functionality
    ✅ 30% implementation complete (auth, config, debug commands)
    📋 70% planned for Sprints 1-10 (docs/TODO.md roadmap)

Version Information:
    - __version__: String version for display and packaging
    - __version_info__: Tuple for programmatic version comparison
    - Release metadata: Author, email, license, description

Usage Examples:
    Version checking:
    >>> from flext_cli import __version__
    >>> print(f"FLEXT CLI v{__version__}")

    Programmatic comparison:
    >>> from flext_cli.__version__ import __version_info__
    >>> if __version_info__ >= (0, 9, 0):
    ...     # Use new features

Integration:
    - Used by setup.py/pyproject.toml for package metadata
    - Imported by main package for version display
    - Used by CLI commands for version reporting
    - Referenced in documentation and release notes

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Library version - FLEXT CLI Development Toolkit
# Semantic versioning: MAJOR.MINOR.PATCH
__version__ = "0.9.0"
__version_info__ = (0, 9, 0)  # Corrected to match string version

# Release status and development information
__status__ = "Development"  # Development, Beta, Production
__release_date__ = "2025-01-01"
__build__ = "dev"

# Library metadata for packaging and distribution
__author__ = "FLEXT Team"
__author_email__ = "team@flext.sh"
__maintainer__ = "FLEXT Team"
__maintainer_email__ = "team@flext.sh"
__license__ = "MIT"
__description__ = (
    "Unified Command Line Interface for FLEXT Ecosystem - 32+ Data Integration Projects"
)
__long_description__ = """
FLEXT CLI provides a comprehensive command-line interface for the entire FLEXT
distributed data integration ecosystem (32+ projects). Built with Clean Architecture,
Domain-Driven Design, and CQRS patterns for enterprise-grade CLI operations.
"""

# URLs and project information
__url__ = "https://github.com/flext/flext-cli"
__download_url__ = "https://pypi.org/project/flext-cli/"
__documentation_url__ = "https://docs.flext.sh/cli"
__repository_url__ = "https://github.com/flext/flext-cli"
__issues_url__ = "https://github.com/flext/flext-cli/issues"

# Development and compatibility information
__python_requires__ = ">=3.13"
__platforms__ = ["any"]
__keywords__ = ["cli", "data-integration", "flext", "enterprise", "clean-architecture"]

# Classification for package indexing
__classifiers__ = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Systems Administration",
    "Topic :: Utilities",
]
