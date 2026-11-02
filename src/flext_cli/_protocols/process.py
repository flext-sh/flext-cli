"""Read-only launch options for the public CLI process runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_cli import p


from collections.abc import Mapping, MutableSequence, Sequence
from types import FrameType
from typing import Literal, Protocol, runtime_checkable

from flext_core import c

if TYPE_CHECKING:
    import threading
    from collections.abc import Buffer, Callable
    from pathlib import Path

    from flext_core import p

    from flext_cli import t
    from flext_cli._models.process import FlextCliModelsProcess
    from flext_cli._protocols._base import (
        FlextCliProtocolsBasePart01,
        FlextCliProtocolsBasePart02,
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
    class ProcessNativeToolEvidence(Protocol):
        """Read-only native tool evidence serialized in a bootstrap receipt."""

        @property
        def role(self) -> Literal["isolation-launcher", "policy-compiler"]:
            """Declared native capability qualified by this bootstrap row."""
            ...

        @property
        def artifact_receipt(self) -> FlextCliProtocolsBasePart01.AtomicFileReceipt:
            """Immutable receipt for the qualified native executable."""
            ...

        @property
        def declaration_inputs(
            self,
        ) -> tuple[FlextCliProtocolsBasePart01.AtomicFileReceipt, ...]:
            """Captured qualification declarations."""
            ...

        @property
        def installation_inputs(
            self,
        ) -> tuple[FlextCliProtocolsBasePart01.AtomicFileReceipt, ...]:
            """Captured native installation inputs."""
            ...

        @property
        def source_inputs(
            self,
        ) -> tuple[FlextCliProtocolsBasePart01.AtomicFileReceipt, ...]:
            """Captured source inputs for native qualification."""
            ...

        @property
        def native_build_outcome(self) -> FlextCliProtocolsBasePart02.ProcessOutcome:
            """Causal outcome of the native compiler build."""
            ...

        @property
        def native_abi_probe_outcome(
            self,
        ) -> FlextCliProtocolsBasePart02.ProcessOutcome:
            """Causal outcome of the native ABI qualification probe."""
            ...

        @property
        def native_policy_probe_outcome(
            self,
        ) -> FlextCliProtocolsBasePart02.ProcessOutcome:
            """Original native socket and io_uring denial probe outcome."""
            ...

        @property
        def policy_sha256(self) -> str:
            """Exact process-owner policy request proven by native probes."""
            ...

        @property
        def native_policy_probes(
            self,
        ) -> tuple[FlextCliModelsProcess.ProcessNativePolicyProbe, ...]:
            """Original attempted syscall observations, never inferred."""
            ...

        @property
        def probe_compiler_receipt(
            self,
        ) -> FlextCliProtocolsBasePart01.AtomicFileReceipt:
            """Exact compiler whose filter supplied the native denial probes."""
            ...

        @property
        def abi_reference(self) -> FlextCliProtocolsBasePart01.AtomicFileReceipt:
            """Captured independently elected native ABI reference."""
            ...

        @property
        def architecture(self) -> str:
            """Qualified native executable architecture."""
            ...

    @runtime_checkable
    class ProcessOptions(Protocol):
        """Read-only child input, environment, and durable-output options."""

        @property
        def env(self) -> Mapping[str, str] | None:
            """Environment overrides for the child process."""
            ...

        @property
        def remove_env_keys(self) -> Sequence[str]:
            """Environment keys to remove before child execution."""
            ...

        @property
        def inherit_environment(self) -> bool:
            """Whether execution overlays the inherited host environment."""
            ...

        @property
        def input_data(self) -> str | bytes | None:
            """Text or byte payload supplied to child stdin."""
            ...

        @property
        def inherit_stdin(self) -> bool:
            """Whether the child reads the caller's stdin instead of the null device."""
            ...

        @property
        def live(self) -> bool:
            """Whether child output is mirrored to live sinks."""
            ...

        @property
        def heartbeat_seconds(self) -> float | None:
            """Interval between live progress heartbeats."""
            ...

        @property
        def deadline(self) -> FlextCliProtocolsBasePart02.ProcessDeadline | None:
            """Absolute deadline and termination grace policy."""
            ...

        @property
        def pass_fds(self) -> Sequence[int]:
            """File descriptors inherited by the child process."""
            ...

        @property
        def stderr_file(self) -> t.Cli.TextPath | None:
            """Separate durable stderr destination for durable output."""
            ...

        @property
        def isolation(self) -> FlextCliModelsProcess.ProcessReadOnlyIsolation | None:
            """Qualified immutable native confinement inputs."""
            ...

        @property
        def signal_wave(self) -> FlextCliProtocolsProcess.SignalWave | None:
            """Signal wave a worker-thread lifecycle subscribes to."""
            ...

    @runtime_checkable
    class PythonScriptExecution(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def module(self) -> str: ...
        @property
        def role(self) -> Literal["isolated-stdlib"]: ...
        @property
        def python_flags(self) -> tuple[Literal["-I"], Literal["-S"]]: ...

    @runtime_checkable
    class ProcessNativePolicyProbe(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def syscall(self) -> str: ...
        @property
        def observed_errno(self) -> int: ...

    @runtime_checkable
    class ProcessNativeToolQualification(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def role(self) -> Literal["isolation-launcher", "policy-compiler"]: ...
        @property
        def artifact_receipt(self) -> p.Cli.AtomicFileReceipt: ...
        @property
        def declaration_inputs(self) -> tuple[p.Cli.AtomicFileReceipt, ...]: ...
        @property
        def installation_inputs(self) -> tuple[p.Cli.AtomicFileReceipt, ...]: ...
        @property
        def source_inputs(self) -> tuple[p.Cli.AtomicFileReceipt, ...]: ...
        @property
        def native_build_outcome(self) -> p.Cli.ProcessOutcome: ...
        @property
        def native_abi_probe_outcome(self) -> p.Cli.ProcessOutcome: ...
        @property
        def native_policy_probe_outcome(self) -> p.Cli.ProcessOutcome: ...
        @property
        def policy_sha256(self) -> str: ...
        @property
        def native_policy_probes(
            self,
        ) -> tuple[p.Cli.ProcessNativePolicyProbe, ...]: ...
        @property
        def probe_compiler_receipt(self) -> p.Cli.AtomicFileReceipt: ...
        @property
        def abi_reference(self) -> p.Cli.AtomicFileReceipt: ...
        @property
        def architecture(self) -> str: ...
        @property
        def issuer_receipt(self) -> p.Cli.AtomicFileState: ...
        @property
        def artifact(self) -> p.Cli.AtomicFileState: ...

    @runtime_checkable
    class ProcessNativeQualificationReceipt[ContextT, IssueT, OutcomeT](Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def runtime_context(self) -> ContextT | None: ...
        @property
        def root(self) -> Path: ...
        @property
        def executed(self) -> bool: ...
        @property
        def outcome(self) -> OutcomeT | None: ...
        @property
        def native_exit_code(self) -> int | None: ...
        @property
        def stage(self) -> t.NonEmptyStr | None: ...
        @property
        def completed(self) -> bool | None: ...
        @property
        def applicability(self) -> str: ...
        @property
        def files(self) -> tuple[Path, ...]: ...
        @property
        def issues(self) -> tuple[IssueT, ...]: ...
        @property
        def native_tool_qualifications(
            self,
        ) -> tuple[p.Cli.ProcessNativeToolEvidence, ...]: ...

    @runtime_checkable
    class ProcessNativeQualificationReport[ContextT, IssueT, OutcomeT](Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def root(self) -> Path: ...
        @property
        def operation(self) -> t.NonEmptyStr: ...
        @property
        def scope(self) -> tuple[Path, ...]: ...
        @property
        def candidate_sha(self) -> str | None: ...
        @property
        def candidate_read_exit_code(self) -> int | None: ...
        @property
        def receipts(
            self,
        ) -> tuple[
            p.Cli.ProcessNativeQualificationReceipt[ContextT, IssueT, OutcomeT], ...
        ]: ...

    @runtime_checkable
    class ProcessReadOnlyIsolation(Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def platform(self) -> Literal["linux"]: ...
        @property
        def architecture(self) -> str: ...
        @property
        def launcher(self) -> p.Cli.ProcessNativeToolQualification: ...
        @property
        def launcher_declaration(self) -> p.Cli.AtomicFileState: ...
        @property
        def policy_compiler(self) -> p.Cli.ProcessNativeToolQualification: ...
        @property
        def compiler_declaration(self) -> p.Cli.AtomicFileState: ...
        @property
        def sources(self) -> tuple[p.Cli.AtomicFileState, ...]: ...
        @property
        def runtime_trees(self) -> tuple[p.Cli.AtomicPhysicalTreeManifest, ...]: ...
        @property
        def runtime_files(self) -> tuple[p.Cli.AtomicFileState, ...]: ...
        @property
        def environment(self) -> tuple[tuple[str, str], ...]: ...

    @runtime_checkable
    class RuntimeProcessRequest(Protocol):
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
        deadline: p.Cli.ProcessDeadline | None
        isolation: p.Cli.ProcessReadOnlyIsolation | None
        pass_fds: tuple[int, ...]
        signal_wave: p.Cli.SignalWave | None

    @runtime_checkable
    class RuntimeProcessState(Protocol):
        """Structural data contract projected from the owning model."""

        process: p.Cli.ProcessHandle | None
        waiter: threading.Thread | None
        durable_log: p.Cli.RuntimeBinaryStream | None
        durable_stderr: p.Cli.RuntimeBinaryStream | None
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
            tuple[threading.Thread, p.Cli.RuntimeClosableStream]
        ]
        input_pump: tuple[threading.Thread, p.Cli.RuntimeClosableStream] | None
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
    class RuntimeOutputTarget(Protocol):
        """Structural data contract projected from the owning model."""

        durable_log: p.Cli.RuntimeBinaryStream | None
        captured_output: bytearray | None
        live_fd: int | None

    @runtime_checkable
    class RuntimeSpawnOptions(Protocol):
        """Structural data contract projected from the owning model."""

        capture_output: bool
        combine_output: bool
        creation_flags: int
        pass_fds: tuple[int, ...]
        start_new_session: bool | None
        stdin_mode: Literal["devnull", "inherit", "pipe"]


__all__: list[str] = ["FlextCliProtocolsProcess"]
