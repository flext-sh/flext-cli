"""Read-only launch options for the public CLI process runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import threading
from collections.abc import Callable, Mapping, MutableSequence, Sequence
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from flext_core import FlextProtocols, c

from flext_cli import t
from flext_cli._protocols._base import (
    FlextCliProtocolsBaseFlextclimodelsbasePart01,
    FlextCliProtocolsBasePart02,
)

if TYPE_CHECKING:
    from collections.abc import Buffer

    from flext_core import p

    from flext_cli._protocols._base import (
        FlextCliProtocolsBaseFlextclimodelsbasePart02,
        FlextCliProtocolsBaseFlextclimodelsbasePart09,
    )


class FlextCliProtocolsProcess:
    """Structural launch and managed-child contracts exposed through ``p.Cli``."""

    @runtime_checkable
    class ParentSignalObserver(Protocol):
        """Observe interruption without taking over the owned child lifecycle."""

        def on_operator_signal(self, signum: int, frame: FrameType | None) -> None:
            """Capture signal evidence without invoking a terminating action."""
            ...

    @runtime_checkable
    class ManagedProcess(Protocol):
        """The existing managed child handle, independent of its utility owner."""

        @property
        def pid(self) -> int:
            """Operating-system child identifier."""
            ...

        @property
        def returncode(self) -> int | None:
            """Observed child exit code, absent while it runs."""
            ...

        @property
        def cwd(self) -> Path | None:
            """Declared child working directory."""
            ...

        @property
        def env(self) -> Mapping[str, str] | None:
            """Read-only child environment overrides."""
            ...

        @property
        def stdout(self) -> str:
            """Decoded standard output collected by the handle."""
            ...

        @property
        def stderr(self) -> str:
            """Decoded standard error collected by the handle."""
            ...

        def poll(self) -> int | None:
            """Observe child completion without waiting."""
            ...

        def terminate(self) -> p.Result[bool]:
            """Signal the owned child or process group to finish."""
            ...

        def kill(self) -> p.Result[bool]:
            """Force the owned child or process group to stop."""
            ...

        def wait(self, timeout: float | None = None) -> p.Result[int]:
            """Reap the child and preserve its output and exit code."""
            ...

        def stdin_write(
            self,
            data: bytes,
            *,
            timeout: float = c.DEFAULT_TIMEOUT_SECONDS,
        ) -> p.Result[int]:
            """Send every byte before the deadline without closing input."""
            ...

        def stdout_read_until(
            self,
            delimiter: bytes,
            *,
            timeout: float,
        ) -> p.Result[bytes]:
            """Read through the delimiter within the supplied deadline."""
            ...

    @runtime_checkable
    class RuntimeClosableStream(Protocol):
        """The cleanup capability shared by owned input and output streams."""

        def close(self) -> None:
            """Release the stream."""
            ...

    @runtime_checkable
    class RuntimeBinaryStream(RuntimeClosableStream, Protocol):
        """Opaque durable sink, retained by identity rather than serialized."""

        def write(self, data: Buffer, /) -> int | None:
            """Write bytes to the sink."""
            ...

        def flush(self) -> None:
            """Flush buffered bytes."""
            ...

        def fileno(self) -> int:
            """Return the underlying descriptor."""
            ...

    @runtime_checkable
    class SignalWave(Protocol):
        """Operator-signal forwarding owned by the main thread for worker lifecycles."""

        def subscribe(
            self,
            received_signals: MutableSequence[int],
            wake: threading.Event,
        ) -> Callable[[], None]:
            """Deliver each received signal to one lifecycle until unsubscribed."""
            ...

    @runtime_checkable
    class ProcessNativeToolEvidence(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def role(self) -> Literal["isolation-launcher", "policy-compiler"]:
            """Declared native capability qualified by this bootstrap row."""
            ...

        @property
        def artifact_receipt(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileReceipt:
            """Immutable receipt for the qualified native executable."""
            ...

        @property
        def declaration_inputs(
            self,
        ) -> tuple[
            FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileReceipt, ...
        ]:
            """Captured qualification declarations."""
            ...

        @property
        def installation_inputs(
            self,
        ) -> tuple[
            FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileReceipt, ...
        ]:
            """Captured native installation inputs."""
            ...

        @property
        def source_inputs(
            self,
        ) -> tuple[
            FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileReceipt, ...
        ]:
            """Captured source inputs for native qualification."""
            ...

        @property
        def native_build_outcome(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart01.ProcessOutcome:
            """Causal outcome of the native compiler build."""
            ...

        @property
        def native_abi_probe_outcome(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart01.ProcessOutcome:
            """Causal outcome of the native ABI qualification probe."""
            ...

        @property
        def native_policy_probe_outcome(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart01.ProcessOutcome:
            """Original native socket and io_uring denial probe outcome."""
            ...

        @property
        def policy_sha256(self) -> str:
            """Exact process-owner policy request proven by native probes."""
            ...

        @property
        def native_policy_probes(
            self,
        ) -> tuple[FlextCliProtocolsProcess.ProcessNativePolicyProbe, ...]:
            """Original attempted syscall observations, never inferred."""
            ...

        @property
        def probe_compiler_receipt(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileReceipt:
            """Exact compiler whose filter supplied the native denial probes."""
            ...

        @property
        def abi_reference(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileReceipt:
            """Captured independently elected native ABI reference."""
            ...

        @property
        def architecture(self) -> str:
            """Qualified native executable architecture."""
            ...

    @runtime_checkable
    class ProcessOptions(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        env: Mapping[str, str] | None
        remove_env_keys: Sequence[str]
        inherit_environment: bool
        input_data: str | bytes | None
        inherit_stdin: bool
        live: bool
        heartbeat_seconds: float | None
        deadline: FlextCliProtocolsBaseFlextclimodelsbasePart01.ProcessDeadline | None
        pass_fds: t.InstanceOfSequence[int]
        stderr_file: t.Cli.TextPath | None

        @property
        def isolation(self) -> FlextCliProtocolsProcess.ProcessReadOnlyIsolation | None:
            """Explicit native read-only confinement request."""
            ...

        signal_wave: FlextCliProtocolsProcess.SignalWave | None

    @runtime_checkable
    class PythonScriptExecution(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def module(self) -> str:
            """Native declaring module of the script entrypoint."""
            ...

        @property
        def role(self) -> Literal["isolated-stdlib"]:
            """Entrypoint cannot import framework or site dependencies."""
            ...

        @property
        def python_flags(self) -> tuple[Literal["-I"], Literal["-S"]]:
            """Derive the interpreter protocol from the isolated stdlib role."""
            ...

    @runtime_checkable
    class ProcessNativePolicyProbe(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def syscall(self) -> str:
            """Declared symbolic syscall actually attempted."""
            ...

        @property
        def observed_errno(self) -> int:
            """Original errno returned by the denied native syscall."""
            ...

    @runtime_checkable
    class ProcessNativeToolQualification(ProcessNativeToolEvidence, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def issuer_receipt(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState:
            """Exact existing bootstrap report containing this evidence row."""
            ...

        @property
        def artifact(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState:
            """Captured exact compiler bytes matching the installed receipt."""
            ...

    @runtime_checkable
    class ProcessNativeQualificationReceipt[ContextT, IssueT, OutcomeT](
        FlextProtocols.BaseModel, Protocol
    ):
        """Structural data contract projected from the owning model."""

        @property
        def runtime_context(self) -> ContextT | None:
            """Authenticated installed association retained across failure."""
            ...

        @property
        def root(self) -> Path:
            """Repository actually attempted."""
            ...

        @property
        def executed(self) -> bool:
            """Original operation was invoked."""
            ...

        @property
        def outcome(self) -> OutcomeT | None:
            """Native outcome independent of report transport."""
            ...

        @property
        def native_exit_code(self) -> int | None:
            """Original native shell exit status."""
            ...

        @property
        def stage(self) -> t.NonEmptyStr | None:
            """Original bootstrap stage reached."""
            ...

        @property
        def completed(self) -> bool | None:
            """Original bootstrap reached its final stage."""
            ...

        @property
        def applicability(self) -> str:
            """Declaration policy preventing execution."""
            ...

        @property
        def files(self) -> tuple[Path, ...]:
            """Paths returned by the original operation owner."""
            ...

        @property
        def issues(self) -> tuple[IssueT, ...]:
            """Native findings retained from the issuing domain."""
            ...

        @property
        def native_tool_qualifications(
            self,
        ) -> tuple[FlextCliProtocolsProcess.ProcessNativeToolEvidence, ...]:
            """Native tool evidence in the original receipt."""
            ...

    @runtime_checkable
    class ProcessNativeQualificationReport[ContextT, IssueT, OutcomeT](
        FlextProtocols.BaseModel, Protocol
    ):
        """Structural data contract projected from the owning model."""

        @property
        def root(self) -> Path:
            """Invoking repository root."""
            ...

        @property
        def operation(self) -> t.NonEmptyStr:
            """Public operation name."""
            ...

        @property
        def scope(self) -> tuple[Path, ...]:
            """Roots discovered once before the original batch."""
            ...

        @property
        def candidate_sha(self) -> str | None:
            """Original Git candidate when available."""
            ...

        @property
        def candidate_read_exit_code(self) -> int | None:
            """Original Git metadata read status."""
            ...

        @property
        def receipts(
            self,
        ) -> tuple[
            FlextCliProtocolsProcess.ProcessNativeQualificationReceipt[
                ContextT, IssueT, OutcomeT
            ],
            ...,
        ]:
            """Original workspace operation receipts."""
            ...

    @runtime_checkable
    class ProcessReadOnlyIsolation(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def platform(self) -> Literal["linux"]:
            """Declared native capability."""
            ...

        @property
        def architecture(self) -> str:
            """Qualified filter ABI."""
            ...

        @property
        def launcher(self) -> FlextCliProtocolsProcess.ProcessNativeToolQualification:
            """Bootstrap-qualified static native Bubblewrap launcher."""
            ...

        @property
        def launcher_declaration(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState:
            """Independently elected canonical launcher declaration."""
            ...

        @property
        def policy_compiler(
            self,
        ) -> FlextCliProtocolsProcess.ProcessNativeToolQualification:
            """Bootstrap-qualified static native libseccomp policy compiler."""
            ...

        @property
        def compiler_declaration(
            self,
        ) -> FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState:
            """Independently elected canonical compiler declaration."""
            ...

        @property
        def sources(
            self,
        ) -> tuple[FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState, ...]:
            """Captured source, metadata and resource bytes."""
            ...

        @property
        def runtime_trees(
            self,
        ) -> tuple[
            FlextCliProtocolsBaseFlextclimodelsbasePart09.AtomicPhysicalTreeManifest,
            ...,
        ]:
            """Authenticated read-only interpreter and system roots."""
            ...

        @property
        def runtime_files(
            self,
        ) -> tuple[FlextCliProtocolsBaseFlextclimodelsbasePart02.AtomicFileState, ...]:
            """Authenticated read-only runtime files outside those roots."""
            ...

        @property
        def environment(self) -> tuple[tuple[str, str], ...]:
            """Complete child environment, without inherited host variables."""
            ...

    @runtime_checkable
    class RuntimeProcessRequest(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        cmd: t.InstanceOfSequence[str]
        output_path: Path | None
        stderr_path: Path | None
        cwd: t.Cli.TextPath | None
        env: Mapping[str, str] | None
        input_data: str | bytes | None
        inherit_stdin: bool
        capture_output: bool
        live: bool
        heartbeat_seconds: float | None
        timeout: int | None
        deadline: FlextCliProtocolsBaseFlextclimodelsbasePart01.ProcessDeadline | None

        @property
        def isolation(self) -> FlextCliProtocolsProcess.ProcessReadOnlyIsolation | None:
            """Immutable native confinement inputs."""
            ...

        pass_fds: tuple[int, ...]
        signal_wave: FlextCliProtocolsProcess.SignalWave | None

    @runtime_checkable
    class RuntimeProcessState(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        process: FlextCliProtocolsBasePart02.ProcessHandle | None
        waiter: threading.Thread | None
        durable_log: FlextCliProtocolsProcess.RuntimeBinaryStream | None
        durable_stderr: FlextCliProtocolsProcess.RuntimeBinaryStream | None
        job_handle: int
        failures: MutableSequence[str]
        cleanup_errors: MutableSequence[str]
        restore_handlers: MutableSequence[Callable[[], None]]
        forwarded_signals: MutableSequence[int]
        received_signals: MutableSequence[int]
        return_codes: MutableSequence[int]
        stdout_output: bytearray
        stderr_output: bytearray
        pump_streams: MutableSequence[
            tuple[threading.Thread, FlextCliProtocolsProcess.RuntimeClosableStream]
        ]
        input_pump: (
            tuple[threading.Thread, FlextCliProtocolsProcess.RuntimeClosableStream]
            | None
        )
        pump_stop: threading.Event
        process_done: threading.Event
        wake: threading.Event
        stack: contextlib.ExitStack
        return_code: int | None
        timed_out: bool
        final_deadline: float | None
        cleanup_complete: bool
        primary_error: Exception | None

    @runtime_checkable
    class RuntimeOutputTarget(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        durable_log: FlextCliProtocolsProcess.RuntimeBinaryStream | None
        captured_output: bytearray | None
        live_fd: int | None

    @runtime_checkable
    class RuntimeSpawnOptions(FlextProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        capture_output: bool
        combine_output: bool
        creation_flags: int
        pass_fds: tuple[int, ...]
        start_new_session: bool | None
        stdin_mode: Literal["devnull", "inherit", "pipe"]


__all__: list[str] = ["FlextCliProtocolsProcess"]
