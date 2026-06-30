# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package."""

from __future__ import annotations

from flext_cli.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)
from flext_cli._exports import (
    FLEXT_CLI_LAZY_IMPORTS,
    FLEXT_CLI_PUBLIC_EXPORTS,
)
from flext_core import d, e, h, r, x
from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    name: target
    for name, target in FLEXT_CLI_LAZY_IMPORTS.items()
    if name in FLEXT_CLI_PUBLIC_EXPORTS
}


_EAGER_EXPORTS = (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
    d,
    e,
    h,
    r,
    x,
)


_PUBLIC_EXPORTS: tuple[str, ...] = FLEXT_CLI_PUBLIC_EXPORTS


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=_PUBLIC_EXPORTS,
)
