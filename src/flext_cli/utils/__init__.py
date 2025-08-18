"""Utilities package for FLEXT CLI.

This module marks the `utils` namespace for helper utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Auth utilities
from flext_cli.utils.auth import (
    clear_auth_tokens,
    get_auth_token,
    get_refresh_token,
    get_refresh_token_path,
    get_token_path,
    is_authenticated,
    save_auth_token,
    save_refresh_token,
    should_auto_refresh,
)

# Output utilities
from flext_cli.utils.output import (
    format_json,
    format_pipeline,
    format_pipeline_list,
    format_plugin_list,
    format_yaml,
    print_error,
    print_info,
    print_success,
    print_warning,
    setup_console,
    show_flext_cli_paths,
)

__all__ = [
    # Auth utilities
    "clear_auth_tokens",
    "get_auth_token",
    "get_refresh_token",
    "get_refresh_token_path",
    "get_token_path",
    "is_authenticated",
    "save_auth_token",
    "save_refresh_token",
    "should_auto_refresh",
    # Output utilities
    "format_json",
    "format_pipeline",
    "format_pipeline_list",
    "format_plugin_list",
    "format_yaml",
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    "setup_console",
    "show_flext_cli_paths",
]
