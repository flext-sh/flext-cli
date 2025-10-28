"""FLEXT CLI Type Utilities - Union type normalization for Typer compatibility.

Provides type annotation normalization to convert modern Python union syntax
(Python 3.10+) to typing.Union/typing.Optional for Typer compatibility.

Typer does not support modern union syntax (Path | None). This module normalizes
such annotations to Typer-compatible forms transparently.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
import types
from typing import Any, get_args, get_origin


def normalize_annotation(annotation: Any) -> Any:
    """Normalize type annotations for Typer compatibility.

    Converts modern Python 3.10+ union syntax (Path | None) to typing-compatible
    forms (Optional[Path] or Union[...]) that Typer can process.

    Handles:
    - Modern union syntax: Path | None → Optional[Path]
    - Complex unions: str | int | None → Union[str, int, None]
    - Nested generics: list[str] | None → Optional[list[str]]
    - Already-normalized types: Optional[Path] → unchanged
    - Non-union types: str → unchanged

    Args:
        annotation: Type annotation to normalize

    Returns:
        Normalized annotation compatible with Typer

    """
    if annotation is None:
        return annotation

    # Check if this is a modern union type (Python 3.10+: X | Y syntax)
    origin = get_origin(annotation)

    # Python 3.10+ union type using | operator
    if sys.version_info >= (3, 10) and origin is types.UnionType:
        return _normalize_union_type(annotation)

    # typing.Union type (traditional typing.Union[X, Y])
    try:
        from typing import Union

        if origin is Union:
            return _normalize_union_type(annotation)
    except (ImportError, AttributeError):
        pass

    # For generic types, recursively normalize inner types
    if origin is not None and hasattr(annotation, "__args__"):
        args = get_args(annotation)
        if args:
            normalized_args = tuple(normalize_annotation(arg) for arg in args)
            # Reconstruct the generic type with normalized args
            if hasattr(annotation, "__class_getitem__"):
                try:
                    return origin[normalized_args]
                except (TypeError, AttributeError):
                    pass
            # Fall back to original if we can't reconstruct
            return annotation

    return annotation


def _normalize_union_type(annotation: Any) -> Any:
    """Normalize a union type to Optional or Union form.

    Converts modern union syntax and typing.Union to a form Typer understands.

    Args:
        annotation: Union type annotation

    Returns:
        Normalized annotation

    """
    # Import here to avoid circular imports
    from typing import Optional

    # Extract union members
    args = get_args(annotation)
    if not args:
        return annotation

    # Check if None is in the union
    has_none = types.NoneType in args
    non_none_args = tuple(arg for arg in args if arg is not types.NoneType)

    # If only one non-None type with None, use Optional[T]
    if has_none and len(non_none_args) == 1:
        inner_type = non_none_args[0]
        # Recursively normalize the inner type
        normalized_inner = normalize_annotation(inner_type)
        return Optional[normalized_inner]

    # If only one non-None type without None, use that type directly
    if not has_none and len(non_none_args) == 1:
        return normalize_annotation(non_none_args[0])

    # If multiple types, use Union[T1, T2, ...]
    if len(non_none_args) > 1:
        # Recursively normalize all inner types
        normalized_non_none = tuple(normalize_annotation(arg) for arg in non_none_args)
        # Create union from normalized types using the | operator
        union_type = normalized_non_none[0]
        for arg_type in normalized_non_none[1:]:
            union_type |= arg_type

        if has_none:
            # Union with None becomes Optional[Union[...]]
            return union_type | None
        # Union without None stays as Union[...]
        return union_type

    # Edge case: only None (shouldn't happen normally)
    return annotation


__all__ = [
    "normalize_annotation",
]
