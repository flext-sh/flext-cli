"""FLEXT CLI Utilities - Clean Architecture v0.7.0.

Utility modules using flext-core patterns exclusively.
No legacy configuration or fallback code.
"""

# Only export what's needed - clean architecture
from flext_cli.utils.config import CLIConfig
from flext_cli.utils.config import CLISettings
from flext_cli.utils.config import get_config

__all__ = [
    "CLIConfig",
    "CLISettings",
    "get_config",
]
