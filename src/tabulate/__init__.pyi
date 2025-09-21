# Type stubs for tabulate library.
# Copyright (c) 2025 FLEXT Team. All rights reserved.
# SPDX-License-Identifier: MIT

from collections.abc import Iterable, Mapping, Sequence
from typing import Literal

type RowMapping = Mapping[str, object]
type RowSequence = Sequence[object]

def tabulate(
    tabular_data: Iterable[RowMapping | RowSequence],
    headers: Sequence[str] | Literal["firstrow", "keys"] | None = ...,
    tablefmt: str | None = ...,
    floatfmt: str | Sequence[str] = ...,
    numalign: str | None = ...,
    stralign: str | None = ...,
    missingval: str = ...,
    showindex: bool | Literal["always", "never"] | Sequence[str | int] | None = ...,
    disable_numparse: bool | Sequence[bool] = ...,
    colalign: Sequence[str] | None = ...,
    maxcolwidths: Sequence[int | None] | int | None = ...,
) -> str: ...
