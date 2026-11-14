# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Protocols. Base package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._protocols._base.flextclimodelsbase_part_01 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart01,
    )
    from flext_cli._protocols._base.flextclimodelsbase_part_02 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart02,
    )
    from flext_cli._protocols._base.flextclimodelsbase_part_03 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart03,
    )
    from flext_cli._protocols._base.flextclimodelsbase_part_04 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart04,
    )
    from flext_cli._protocols._base.flextclimodelsbase_part_05 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart05,
    )
    from flext_cli._protocols._base.flextclimodelsbase_part_06 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart06,
    )
    from flext_cli._protocols._base.flextclimodelsbase_part_07 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart07,
    )
    from flext_cli._protocols._base.flextclimodelsbase_part_08 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart08,
    )
    from flext_cli._protocols._base.flextclimodelsbase_part_09 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart09,
    )
    from flext_cli._protocols._base.flextclimodelsbase_part_10 import (
        FlextCliProtocolsBaseFlextclimodelsbasePart10,
    )
    from flext_cli._protocols._base.flextcliprotocolsbase_part_01 import (
        FlextCliProtocolsBasePart01,
    )
    from flext_cli._protocols._base.flextcliprotocolsbase_part_02 import (
        FlextCliProtocolsBasePart02,
    )
    from flext_cli._protocols._base.flextcliprotocolsbase_part_03 import (
        FlextCliProtocolsBasePart03,
    )
    from flext_cli._protocols._base.flextcliprotocolsbase_part_04 import (
        FlextCliProtocolsBasePart04,
    )
    from flext_cli._protocols._base.flextcliprotocolsbase_part_05 import (
        FlextCliProtocolsBasePart05,
    )


__all__: tuple[str, ...] = (
    "FlextCliProtocolsBaseFlextclimodelsbasePart01",
    "FlextCliProtocolsBaseFlextclimodelsbasePart02",
    "FlextCliProtocolsBaseFlextclimodelsbasePart03",
    "FlextCliProtocolsBaseFlextclimodelsbasePart04",
    "FlextCliProtocolsBaseFlextclimodelsbasePart05",
    "FlextCliProtocolsBaseFlextclimodelsbasePart06",
    "FlextCliProtocolsBaseFlextclimodelsbasePart07",
    "FlextCliProtocolsBaseFlextclimodelsbasePart08",
    "FlextCliProtocolsBaseFlextclimodelsbasePart09",
    "FlextCliProtocolsBaseFlextclimodelsbasePart10",
    "FlextCliProtocolsBasePart01",
    "FlextCliProtocolsBasePart02",
    "FlextCliProtocolsBasePart03",
    "FlextCliProtocolsBasePart04",
    "FlextCliProtocolsBasePart05",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliProtocolsBaseFlextclimodelsbasePart01": ".flextclimodelsbase_part_01",
        "FlextCliProtocolsBaseFlextclimodelsbasePart02": ".flextclimodelsbase_part_02",
        "FlextCliProtocolsBaseFlextclimodelsbasePart03": ".flextclimodelsbase_part_03",
        "FlextCliProtocolsBaseFlextclimodelsbasePart04": ".flextclimodelsbase_part_04",
        "FlextCliProtocolsBaseFlextclimodelsbasePart05": ".flextclimodelsbase_part_05",
        "FlextCliProtocolsBaseFlextclimodelsbasePart06": ".flextclimodelsbase_part_06",
        "FlextCliProtocolsBaseFlextclimodelsbasePart07": ".flextclimodelsbase_part_07",
        "FlextCliProtocolsBaseFlextclimodelsbasePart08": ".flextclimodelsbase_part_08",
        "FlextCliProtocolsBaseFlextclimodelsbasePart09": ".flextclimodelsbase_part_09",
        "FlextCliProtocolsBaseFlextclimodelsbasePart10": ".flextclimodelsbase_part_10",
        "FlextCliProtocolsBasePart01": ".flextcliprotocolsbase_part_01",
        "FlextCliProtocolsBasePart02": ".flextcliprotocolsbase_part_02",
        "FlextCliProtocolsBasePart03": ".flextcliprotocolsbase_part_03",
        "FlextCliProtocolsBasePart04": ".flextcliprotocolsbase_part_04",
        "FlextCliProtocolsBasePart05": ".flextcliprotocolsbase_part_05",
    },
    public_exports=__all__,
    deferred_members={
        "FlextCliProtocolsBaseFlextclimodelsbasePart01": (
            "ProcessOutcome",
            "CommandOutputEnvelope",
            "CommandOutput",
            "CommandBytesOutput",
            "ProcessDeadline",
            "RuntimeComponents",
            "RuntimeStatus",
            "DisplayData",
            "LoadedConfig",
            "CliNormalizedJson",
            "NormalizedJsonList",
            "SuccessSummaryDetails",
        ),
        "FlextCliProtocolsBaseFlextclimodelsbasePart02": (
            "AtomicPhysicalIdentity",
            "AtomicFileIdentity",
            "AtomicFileState",
            "AtomicFileReceipt",
            "PromptRuntimeState",
            "AuthCredentialsPayload",
            "ProcessEnvironmentSpec",
        ),
        "FlextCliProtocolsBaseFlextclimodelsbasePart03": (
            "AtomicDirectoryState",
            "CommandEntryModel",
            "EmptyRequest",
            "CommandMetadata",
            "ResultCommandRoute",
        ),
        "FlextCliProtocolsBaseFlextclimodelsbasePart04": ("TableConfig",),
        "FlextCliProtocolsBaseFlextclimodelsbasePart05": (
            "SettingsSnapshot",
            "OfficeRenderRequest",
            "OfficeRenderResult",
        ),
        "FlextCliProtocolsBaseFlextclimodelsbasePart06": (
            "CliParamsConfig",
            "OptionMetadata",
            "OptionSpec",
            "InvocationResult",
        ),
        "FlextCliProtocolsBaseFlextclimodelsbasePart07": (
            "ServiceOptions",
            "TypedExtract",
            "JsonWriteOptions",
            "TableRenderRequest",
            "DataReportRequest",
        ),
        "FlextCliProtocolsBaseFlextclimodelsbasePart08": (
            "AtomicNativeSelections",
            "AtomicDirectoryChainPlan",
        ),
        "FlextCliProtocolsBaseFlextclimodelsbasePart09": (
            "AtomicPhysicalTreeEntry",
            "AtomicDirectoryName",
            "AtomicDirectoryInventory",
            "AtomicPhysicalTreeManifest",
        ),
        "FlextCliProtocolsBaseFlextclimodelsbasePart10": (
            "AtomicDirectoryObservations",
            "AtomicDirectoryQueryEffects",
            "AtomicFilePublication",
        ),
        "FlextCliProtocolsBasePart01": ("CliSettings",),
        "FlextCliProtocolsBasePart02": (
            "Settings",
            "ProcessHandle",
            "CliSettings",
        ),
        "FlextCliProtocolsBasePart03": (
            "CommandRunner",
            "Settings",
            "ProcessHandle",
            "CliSettings",
        ),
        "FlextCliProtocolsBasePart04": (
            "CliOptionSpec",
            "CliCommandWrapper",
            "ResultCommandHandler",
            "ErasedCommandResult",
            "CommandRunner",
            "Settings",
            "ProcessHandle",
            "CliSettings",
        ),
        "FlextCliProtocolsBasePart05": (
            "YamlModule",
            "CliOptionSpec",
            "CliCommandWrapper",
            "ResultCommandHandler",
            "ErasedCommandResult",
            "CommandRunner",
            "Settings",
            "ProcessHandle",
            "CliSettings",
        ),
    },
)
