# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Documents package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._documents.docx_formatting import (
        FlextCliUtilitiesDocxFormatting,
    )
    from flext_cli._utilities._documents.docx_layout import FlextCliUtilitiesDocxLayout
    from flext_cli._utilities._documents.docx_reader import FlextCliUtilitiesDocxReader
    from flext_cli._utilities._documents.docx_renderer import (
        FlextCliUtilitiesDocxRenderer,
    )
    from flext_cli._utilities._documents.pptx_reader import FlextCliUtilitiesPptxReader
    from flext_cli._utilities._documents.pptx_renderer import (
        FlextCliUtilitiesPptxRenderer,
    )
    from flext_cli._utilities._documents.pptx_serializer import (
        FlextCliUtilitiesPptxSerializer,
    )


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesDocxFormatting",
    "FlextCliUtilitiesDocxLayout",
    "FlextCliUtilitiesDocxReader",
    "FlextCliUtilitiesDocxRenderer",
    "FlextCliUtilitiesPptxReader",
    "FlextCliUtilitiesPptxRenderer",
    "FlextCliUtilitiesPptxSerializer",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliUtilitiesDocxFormatting": ".docx_formatting",
        "FlextCliUtilitiesDocxLayout": ".docx_layout",
        "FlextCliUtilitiesDocxReader": ".docx_reader",
        "FlextCliUtilitiesDocxRenderer": ".docx_renderer",
        "FlextCliUtilitiesPptxReader": ".pptx_reader",
        "FlextCliUtilitiesPptxRenderer": ".pptx_renderer",
        "FlextCliUtilitiesPptxSerializer": ".pptx_serializer",
    },
    public_exports=__all__,
)
