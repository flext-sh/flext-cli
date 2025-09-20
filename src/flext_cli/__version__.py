"""FLEXT CLI Version Information.

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

# Development and deployment information
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

# Foundation Layer exports
__all__ = [
    "__author__",
    "__author_email__",
    "__build__",
    "__classifiers__",
    "__description__",
    "__documentation_url__",
    "__download_url__",
    "__issues_url__",
    "__keywords__",
    "__license__",
    "__long_description__",
    "__maintainer__",
    "__maintainer_email__",
    "__platforms__",
    "__python_requires__",
    "__release_date__",
    "__repository_url__",
    "__status__",
    "__url__",
    "__version__",
    "__version_info__",
]
