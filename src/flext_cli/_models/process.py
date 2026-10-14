"""Canonical launch options for the public CLI process runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import threading
from collections.abc import Callable
from pathlib import Path
from typing import ClassVar, Literal

from flext_cli import p, t
from flext_cli._models._base.flextclimodelsbase_part_01 import FlextCliModelsBasePart01
from flext_cli._models._base.flextclimodelsbase_part_02 import FlextCliModelsBasePart02
from flext_cli._models._base.flextclimodelsbase_part_09 import FlextCliModelsBasePart09
from flext_core import m


class FlextCliModelsProcess:
    """Process input declarations exposed through ``m.Cli``."""

    class ProcessNativePolicyProbe(m.BaseModel):
        """One original native denial observation in the bootstrap receipt."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True, extra="forbid")
        syscall: str = m.Field(
            min_length=1, description="Declared symbolic syscall actually attempted"
        )
        observed_errno: int = m.Field(
            ge=0, description="Original errno returned by the denied native syscall"
        )

    class ProcessNativeToolEvidence(m.ArbitraryTypesModel):
        """Native tool row serialized by the existing bootstrap receipt owner."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True, frozen=True, extra="forbid"
        )
        role: Literal["isolation-launcher", "policy-compiler"] = m.Field(
            description="Declared native capability qualified by this bootstrap row"
        )
        artifact_receipt: FlextCliModelsBasePart02.AtomicFileReceipt = m.Field(
            description="Immutable receipt for the qualified native executable",
        )
        declaration_inputs: tuple[FlextCliModelsBasePart02.AtomicFileReceipt, ...] = (
            m.Field(min_length=1, description="Captured qualification declarations")
        )
        installation_inputs: tuple[FlextCliModelsBasePart02.AtomicFileReceipt, ...] = (
            m.Field(min_length=1, description="Captured native installation inputs")
        )
        source_inputs: tuple[FlextCliModelsBasePart02.AtomicFileReceipt, ...] = m.Field(
            min_length=1,
            description="Captured source inputs for native qualification",
        )
        native_build_outcome: FlextCliModelsBasePart01.ProcessOutcome = m.Field(
            description="Causal outcome of the native compiler build",
        )
        native_abi_probe_outcome: FlextCliModelsBasePart01.ProcessOutcome = m.Field(
            description="Causal outcome of the native ABI qualification probe",
        )
        native_policy_probe_outcome: FlextCliModelsBasePart01.ProcessOutcome = m.Field(
            description="Original native socket and io_uring denial probe outcome",
        )
        policy_sha256: str = m.Field(
            pattern=r"^[0-9a-f]{64}$",
            description="Exact process-owner policy request proven by native probes",
        )
        native_policy_probes: tuple[
            FlextCliModelsProcess.ProcessNativePolicyProbe, ...
        ] = m.Field(
            description="Original attempted syscall observations, never inferred"
        )
        probe_compiler_receipt: FlextCliModelsBasePart02.AtomicFileReceipt = m.Field(
            description="Exact compiler whose filter supplied the native denial probes"
        )
        abi_reference: FlextCliModelsBasePart02.AtomicFileReceipt = m.Field(
            description="Captured independently elected native ABI reference",
        )
        architecture: str = m.Field(
            min_length=1,
            description="Qualified native executable architecture",
        )

    class ProcessNativeToolQualification(ProcessNativeToolEvidence):
        """Caller-bound projection over one current native bootstrap report row."""

        issuer_receipt: FlextCliModelsBasePart02.AtomicFileState = m.Field(
            description="Exact existing bootstrap report containing this evidence row"
        )
        artifact: FlextCliModelsBasePart02.AtomicFileState = m.Field(
            description="Captured exact compiler bytes matching the installed receipt"
        )

    class ProcessNativeQualificationReceipt(m.BaseModel):
        """Minimal typed projection of one existing workspace operation receipt."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True, extra="ignore")
        native_tool_qualifications: tuple[
            FlextCliModelsProcess.ProcessNativeToolEvidence, ...
        ] = m.Field(
            default=(), description="Native tool evidence in the original receipt"
        )

    class ProcessNativeQualificationReport(m.BaseModel):
        """Minimal typed projection of the existing bootstrap report."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True, extra="ignore")
        receipts: tuple[
            FlextCliModelsProcess.ProcessNativeQualificationReceipt, ...
        ] = m.Field(description="Original workspace operation receipts")

    class ProcessNativePolicyRequest(m.BaseModel):
        """Canonical stdin protocol for the qualified static policy compiler."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(frozen=True, extra="forbid")
        denied_syscalls: tuple[str, ...] = m.Field(
            min_length=1, description="Symbolic syscall obligations from process config"
        )

    class ProcessReadOnlyIsolation(m.ArbitraryTypesModel):
        """Qualified Linux confinement inputs consumed by the process owner."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True, frozen=True, extra="forbid"
        )
        platform: Literal["linux"] = m.Field(description="Declared native capability")
        architecture: str = m.Field(min_length=1, description="Qualified filter ABI")
        launcher: FlextCliModelsProcess.ProcessNativeToolQualification = m.Field(
            description="Bootstrap-qualified static native Bubblewrap launcher"
        )
        launcher_declaration: FlextCliModelsBasePart02.AtomicFileState = m.Field(
            description="Independently elected canonical launcher declaration"
        )
        policy_compiler: FlextCliModelsProcess.ProcessNativeToolQualification = m.Field(
            description="Bootstrap-qualified static native libseccomp policy compiler"
        )
        compiler_declaration: FlextCliModelsBasePart02.AtomicFileState = m.Field(
            description="Independently elected canonical compiler declaration"
        )
        sources: tuple[FlextCliModelsBasePart02.AtomicFileState, ...] = m.Field(
            min_length=1, description="Captured source, metadata and resource bytes"
        )
        runtime_trees: tuple[
            FlextCliModelsBasePart09.AtomicPhysicalTreeManifest, ...
        ] = m.Field(description="Authenticated read-only interpreter and system roots")
        runtime_files: tuple[FlextCliModelsBasePart02.AtomicFileState, ...] = m.Field(
            description="Authenticated read-only runtime files outside those roots"
        )
        environment: tuple[tuple[str, str], ...] = m.Field(
            description="Complete child environment, without inherited host variables"
        )

    class ProcessOptions(m.ArbitraryTypesModel):
        """Child input, environment, and durable-output execution options."""

        env: t.StrMapping | None = m.Field(
            default=None,
            description="Environment overrides for the child process.",
        )
        remove_env_keys: t.StrSequence = m.Field(
            default=(),
            description="Environment keys to remove before child execution.",
        )
        inherit_environment: bool = m.Field(
            default=True, description="Overlay the caller environment or replace it"
        )
        input_data: str | bytes | None = m.Field(
            default=None,
            description="Text or byte payload supplied to child stdin.",
        )
        live: bool = m.Field(
            default=False,
            description="Mirror child output to live sinks.",
        )
        heartbeat_seconds: float | None = m.Field(
            default=None,
            description="Interval between live progress heartbeats.",
        )
        deadline: p.Cli.ProcessDeadline | None = m.Field(
            default=None,
            description="Absolute deadline and termination grace policy.",
        )
        pass_fds: t.InstanceOfSequence[int] = m.Field(
            default=(),
            description="File descriptors inherited by the child process.",
        )
        stderr_file: t.Cli.TextPath | None = m.Field(
            default=None,
            description="Separate durable stderr destination for durable output.",
        )
        isolation: FlextCliModelsProcess.ProcessReadOnlyIsolation | None = m.Field(
            default=None, description="Explicit native read-only confinement request"
        )

    class RuntimeProcessRequest(m.ArbitraryTypesModel):
        """Resolved launch inputs shared by preparation and process creation."""

        # Borrow the sequence: iteration belongs after signal handlers are installed.
        cmd: t.InstanceOfSequence[str] = m.Field(
            description="Executable and ordered child arguments.",
        )
        output_path: Path | None = m.Field(
            default=None,
            description="Durable stdout destination, combined when stderr has no sink.",
        )
        stderr_path: Path | None = m.Field(
            default=None,
            description="Separate durable stderr destination.",
        )
        cwd: t.Cli.TextPath | None = m.Field(
            default=None,
            description="Working directory for child execution.",
        )
        env: t.StrMapping | None = m.Field(
            default=None,
            description="Resolved environment for child execution.",
        )
        input_data: str | bytes | None = m.Field(
            default=None,
            description="Text or byte payload supplied to child stdin.",
        )
        capture_output: bool = m.Field(
            default=True,
            description="Retain child stdout and stderr in memory.",
        )
        live: bool = m.Field(
            default=False,
            description="Mirror child output to live sinks.",
        )
        heartbeat_seconds: float | None = m.Field(
            default=None,
            description="Interval between live progress heartbeats.",
        )
        timeout: int | None = m.Field(
            default=None,
            description="Relative child execution timeout in seconds.",
        )
        deadline: p.Cli.ProcessDeadline | None = m.Field(
            default=None,
            description="Absolute deadline and termination grace policy.",
        )
        isolation: FlextCliModelsProcess.ProcessReadOnlyIsolation | None = m.Field(
            default=None, description="Immutable native confinement inputs"
        )
        pass_fds: tuple[int, ...] = m.Field(
            default=(),
            description="Explicit descriptors inherited by an ordinary child",
        )

    class RuntimeProcessState(m.ArbitraryTypesModel):
        """Mutable ownership and causal evidence for exactly one lifecycle."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
            validate_assignment=False,
        )
        process: p.Cli.ProcessHandle | None = m.Field(
            default=None,
            description="Owned root child process handle.",
        )
        waiter: threading.Thread | None = m.Field(
            default=None,
            description="Thread responsible for reaping the root child.",
        )
        durable_log: p.Cli.RuntimeBinaryStream | None = m.Field(
            default=None,
            description="Owned stream for durable stdout or combined child output.",
        )
        durable_stderr: p.Cli.RuntimeBinaryStream | None = m.Field(
            default=None,
            description="Owned stream for separate durable child stderr.",
        )
        job_handle: int = m.Field(
            default=0,
            description="Windows job handle owning the child boundary.",
        )
        failures: t.MutableSequenceOf[str] = m.Field(
            default_factory=list[str],
            description="Causal failures collected during execution.",
        )
        cleanup_errors: t.MutableSequenceOf[str] = m.Field(
            default_factory=list[str],
            description="Failures collected while releasing resources.",
        )
        restore_handlers: t.MutableSequenceOf[Callable[[], None]] = m.Field(
            default_factory=list[Callable[[], None]],
            description="Callbacks restoring the parent signal handlers.",
        )
        forwarded_signals: t.MutableSequenceOf[int] = m.Field(
            default_factory=list[int],
            description="Signal numbers registered for forwarding.",
        )
        received_signals: t.MutableSequenceOf[int] = m.Field(
            default_factory=list[int],
            description="Parent signals received during this lifecycle.",
        )
        return_codes: t.MutableSequenceOf[int] = m.Field(
            default_factory=list[int],
            description="Root child return codes recorded by the waiter.",
        )
        stdout_output: bytearray = m.Field(
            default_factory=bytearray,
            description="Mutable byte-exact captured stdout buffer.",
        )
        stderr_output: bytearray = m.Field(
            default_factory=bytearray,
            description="Mutable byte-exact captured stderr buffer.",
        )
        pump_streams: t.MutableSequenceOf[
            t.Pair[threading.Thread, p.Cli.RuntimeClosableStream]
        ] = m.Field(
            default_factory=list[t.Pair[threading.Thread, p.Cli.RuntimeClosableStream]],
            description="Owned output pump threads paired with their source streams.",
        )
        input_pump: tuple[threading.Thread, p.Cli.RuntimeClosableStream] | None = (
            m.Field(
                default=None,
                description="Owned stdin pump thread paired with its sink stream.",
            )
        )
        pump_stop: threading.Event = m.Field(
            default_factory=threading.Event,
            description="Request for output pumps to stop.",
        )
        process_done: threading.Event = m.Field(
            default_factory=threading.Event,
            description="Notification that the root was reaped.",
        )
        wake: threading.Event = m.Field(
            default_factory=threading.Event,
            description="Notification of new lifecycle evidence.",
        )
        stack: contextlib.ExitStack = m.Field(
            default_factory=contextlib.ExitStack,
            description="Owner of lifecycle resource cleanup.",
        )
        return_code: int | None = m.Field(
            default=None,
            description="Final observed root child return code.",
        )
        timed_out: bool = m.Field(
            default=False,
            description="Whether child execution exhausted its deadline.",
        )
        final_deadline: float | None = m.Field(
            default=None,
            description="Monotonic deadline bounding final lifecycle cleanup.",
        )
        cleanup_complete: bool = m.Field(
            default=False,
            description="Whether child reaping and output draining completed.",
        )
        primary_error: Exception | None = m.Field(
            default=None,
            description="Primary exception retaining causal cleanup notes.",
        )

    class RuntimeOutputTarget(m.ArbitraryTypesModel):
        """Destinations for one byte-exact output pump."""

        durable_log: p.Cli.RuntimeBinaryStream | None = m.Field(
            default=None,
            description="Durable sink receiving byte-exact child output.",
        )
        captured_output: bytearray | None = m.Field(
            default=None,
            description="Mutable buffer retaining captured child output.",
        )
        live_fd: int | None = m.Field(
            default=None,
            description="Descriptor receiving mirrored live child output.",
        )

    class RuntimeSpawnOptions(m.ArbitraryTypesModel):
        """Pipe and platform creation policy for one child."""

        capture_output: bool = m.Field(
            description="Create pipes for capturing child output.",
        )
        combine_output: bool = m.Field(
            description="Combine child stderr into its stdout pipe.",
        )
        creation_flags: int = m.Field(
            default=0,
            description="Platform flags used when creating the child process.",
        )
        pass_fds: tuple[int, ...] = m.Field(
            default=(), description="Process-owner descriptors consumed by confinement"
        )


__all__: list[str] = ["FlextCliModelsProcess"]
