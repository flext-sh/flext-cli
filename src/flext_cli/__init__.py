"""FLEXT CLI - CLI-specific functionality extending flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Import all from each module following flext-core patterns
from flext_cli.api import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.auth import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.client import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.cmd import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.config import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.constants import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.context import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.debug import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.decorators import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.mixins import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.models import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.services import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.typings import *  # type: ignore[import-untyped] # noqa: F403
from flext_cli.utilities import *  # type: ignore[import-untyped] # noqa: F403

# Combine all __all__ from all modules following flext-core pattern
import flext_cli.api as _api
import flext_cli.auth as _auth
import flext_cli.client as _client
import flext_cli.cmd as _cmd
import flext_cli.config as _config
import flext_cli.constants as _constants
import flext_cli.context as _context
import flext_cli.debug as _debug
import flext_cli.decorators as _decorators
import flext_cli.mixins as _mixins
import flext_cli.models as _models
import flext_cli.services as _services
import flext_cli.typings as _typings
import flext_cli.utilities as _utilities

# Build __all__ list - PyRight compatible approach
_all_exports: list[str] = []

# Module exports collection
_modules_to_check = [
    _api, _auth, _client, _cmd, _config, _constants,
    _context, _debug, _decorators, _mixins, _models,
    _services, _typings, _utilities
]

for module in _modules_to_check:
    if hasattr(module, "__all__"):
        module_all = module.__all__
        if isinstance(module_all, (list, tuple)):
            _all_exports += list(module_all)

# Remove duplicates and sort
__all__ = tuple(sorted(set(_all_exports)))
