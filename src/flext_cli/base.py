"""Shared service foundation for flext-cli components.

Reads settings through the service runtime so every consumer uses
``settings`` as the single settings access point.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Concrete-module imports: this module resolves during the package root's
# lazy ``s`` export, when the root namespace is still initializing.
from flext_cli.models import m
from flext_cli.protocols import p
from flext_cli.typings import t
from flext_cli.utilities import u
from flext_core import s


class FlextCliServiceBase[TDomainResult: p.Base = m.Cli.RuntimeStatus](
    s[TDomainResult], u.Cli
):
    """Base class for flext-cli services with typed configuration access.

    Note: This is an abstract base class. Subclasses must implement the
    `execute` method from s.
    """


s = FlextCliServiceBase

__all__: t.MutableSequenceOf[str] = ["FlextCliServiceBase", "s"]
