"""Resource ownership for one portable streamed process lifecycle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import errno
import os
import platform
import signal
import struct
import sys
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

if sys.platform == "linux":
    import fcntl

from flext_cli import c, config, m, p, r, t
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_03 import (
    FlextCliUtilitiesFilesPart03,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_05 import (
    FlextCliUtilitiesFilesPart05,
)
from flext_cli._utilities._runtime_process_cleanup import (
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
)
from flext_cli._utilities._runtime_process_outcome import (
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
)
from flext_cli._utilities._runtime_process_output import (
    FlextCliUtilitiesRuntimeProcessOutputMixin,
)
from flext_cli._utilities._runtime_process_resources import (
    FlextCliUtilitiesRuntimeProcessResourcesMixin,
)
from flext_cli._utilities._runtime_process_start import (
    FlextCliUtilitiesRuntimeProcessStartMixin,
)
from flext_cli._utilities._runtime_process_timing import (
    FlextCliUtilitiesRuntimeProcessTimingMixin,
)
from flext_cli._utilities.atomic_file_snapshot import (
    FlextCliUtilitiesAtomicFileSnapshot,
)
from flext_cli._utilities.atomic_parent_descriptor import (
    FlextCliUtilitiesAtomicParentDescriptor,
)


class FlextCliUtilitiesRuntimeProcessExecutionMixin(
    FlextCliUtilitiesRuntimeProcessCleanupMixin,
    FlextCliUtilitiesRuntimeProcessOutcomeMixin,
    FlextCliUtilitiesRuntimeProcessOutputMixin,
    FlextCliUtilitiesRuntimeProcessResourcesMixin,
    FlextCliUtilitiesRuntimeProcessStartMixin,
    FlextCliUtilitiesRuntimeProcessTimingMixin,
):
    """Own one child process and its streaming resources."""

    if TYPE_CHECKING:

        @classmethod
        def run_bytes(
            cls,
            cmd: t.StrSequence,
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: p.Cli.ProcessOptions | None = None,
        ) -> p.Result[p.Cli.CommandBytesOutput]: ...

    @classmethod
    def _execute_streamed_process(
        cls,
        request: m.Cli.RuntimeProcessRequest,
    ) -> p.Result[p.Cli.CommandBytesOutput]:
        """Own resources and complete one streamed child lifecycle.

        Returns:
            Captured bytes and the exact causal process outcome.

        """
        started = time.monotonic()
        timing_result = cls._resolve_process_timing(
            request,
            started,
            on_main_thread=threading.current_thread() is threading.main_thread(),
        )
        if timing_result.failure:
            return r[p.Cli.CommandBytesOutput].from_failure(timing_result)
        absolute_deadline, grace_seconds = timing_result.unwrap()
        state = m.Cli.RuntimeProcessState(final_deadline=absolute_deadline)
        try:
            cls._execute_lifecycle(request, state, absolute_deadline, grace_seconds)
        except (OSError, TypeError, ValueError) as exc:
            exc.add_note(r[str].fail(str(exc), exception=exc).error or str(exc))
            state.primary_error = exc
            if state.process is not None:
                signal_result = cls._signal_process_tree(
                    state.process,
                    signal.SIGKILL,
                    state.job_handle,
                    force=True,
                )
                if signal_result.failure:
                    exc.add_note(signal_result.error or "process signal failed")
        finally:
            cls._finalize_lifecycle(state)
        if state.primary_error is not None:
            return r[p.Cli.CommandBytesOutput].fail(
                f"{c.Cli.OUTPUT_EXECUTION_ERROR}: {state.primary_error}",
                exception=state.primary_error,
            )
        return cls._captured_process_result(
            state,
            max(0.0, time.monotonic() - started),
        )

    @classmethod
    def _execute_lifecycle(
        cls,
        request: m.Cli.RuntimeProcessRequest,
        state: m.Cli.RuntimeProcessState,
        absolute_deadline: float | None,
        grace_seconds: float,
    ) -> None:
        if threading.current_thread() is threading.main_thread():
            state.restore_handlers.extend(
                cls._install_forwarding_handlers(
                    state.received_signals,
                    state.forwarded_signals,
                    state.wake,
                ),
            )
        prepared_cmd = tuple(request.cmd)
        if state.received_signals:
            state.wake.set()
            return
        isolated = cls._prepare_process_isolation(
            request, state, prepared_cmd, grace_seconds
        )
        if isolated is None:
            return
        prepared_cmd, child_env, inherited = isolated
        destinations = (request.output_path, request.stderr_path)
        for destination in destinations:
            if destination is not None:
                destination.parent.mkdir(parents=True, exist_ok=True)
        state.durable_log, state.durable_stderr = (
            state.stack.enter_context(destination.open("wb", buffering=0))
            if destination is not None
            else None
            for destination in destinations
        )
        stdin_result = cls._prepare_streamed_stdin(state.stack, request.input_data)
        live_result = cls._prepare_live_descriptor(state.stack, live=request.live)
        if stdin_result.failure:
            state.failures.append(stdin_result.error or "stdin preparation failed")
        elif live_result.failure:
            state.failures.append(live_result.error or "live output preparation failed")
        elif state.received_signals:
            state.wake.set()
        elif cls._spawn_deadline_exhausted(absolute_deadline, grace_seconds):
            state.failures.append("process deadline exhausted before child spawn")
        else:
            start_result = cls._start_contained_process(
                prepared_cmd,
                request.cwd,
                child_env,
                stdin_result.value[0],
                options=m.Cli.RuntimeSpawnOptions(
                    capture_output=(
                        request.output_path is not None or request.capture_output
                    ),
                    combine_output=(
                        request.output_path is not None and request.stderr_path is None
                    ),
                    pass_fds=inherited,
                ),
            )
            if start_result.failure:
                state.failures.append(start_result.error or "process start failed")
            else:
                owned_process, state.job_handle = start_result.unwrap()
                state.process = owned_process
                waiter = cls._attach_process_streams(
                    owned_process,
                    request,
                    state,
                    stdin_result.unwrap(),
                    live_result.value,
                )
                state.timed_out, state.final_deadline = cls._monitor_process(
                    owned_process,
                    state,
                    absolute_deadline,
                    grace_seconds,
                    progress=(live_result.value[1], request.heartbeat_seconds),
                )
                state.return_code = cls._reap_and_drain(owned_process, waiter, state)
                state.cleanup_complete = True

    @classmethod
    def _prepare_process_isolation(
        cls,
        request: m.Cli.RuntimeProcessRequest,
        state: m.Cli.RuntimeProcessState,
        command: tuple[str, ...],
        grace_seconds: float,
    ) -> tuple[tuple[str, ...], t.StrMapping | None, tuple[int, ...]] | None:
        """Prepare explicit native confinement inside the existing lifecycle.

        Returns:
            The effective command, environment, and inherited descriptor
            numbers: the caller's declaration when isolation is not requested,
            otherwise the confined launcher argv with a cleared environment
            and the sealed input and runtime-root descriptors.

        Raises:
            ValueError: If the isolation declaration cannot be confined
                natively, for example a platform mismatch, inherited caller
                descriptors, invalid environment names, non-absolute
                executable or working directory, competing or overlapping
                runtime roots, an unexecutable or set-id launcher, an
                incomplete seccomp filter, an input changed since capture,
                or an escaping link, executable, or working directory.

        """
        isolation = request.isolation
        if isolation is None:
            return command, request.env, request.pass_fds
        if (
            sys.platform != isolation.platform
            or platform.machine() != isolation.architecture
        ):
            msg = "read-only process isolation has no qualified native platform capability"
            raise ValueError(msg)
        if request.pass_fds:
            msg = "isolated processes cannot inherit caller file descriptors"
            raise ValueError(msg)
        environment_names = tuple(name for name, _value in isolation.environment)
        if len(set(environment_names)) != len(environment_names) or any(
            not name or "=" in name or "\0" in name or "\0" in value
            for name, value in isolation.environment
        ):
            msg = "isolated process environment has invalid or competing declarations"
            raise ValueError(msg)
        if not command or not Path(command[0]).is_absolute():
            msg = "isolated process requires an absolute declared executable"
            raise ValueError(msg)
        if request.cwd is None or not Path(request.cwd).is_absolute():
            msg = "isolated process requires an absolute declared working directory"
            raise ValueError(msg)
        roots = tuple(tree.root.path for tree in isolation.runtime_trees)
        files = (
            isolation.launcher,
            isolation.policy_compiler.artifact,
            isolation.policy_compiler.issuer_receipt,
            isolation.compiler_declaration,
            *isolation.sources,
            *isolation.runtime_files,
        )
        captured_by_path: dict[Path, m.Cli.AtomicFileState] = {}
        for captured in files:
            if captured_by_path.setdefault(captured.path, captured) != captured:
                msg = f"isolated input has competing physical states: {captured.path}"
                raise ValueError(msg)
        files = tuple(captured_by_path.values())
        paths = tuple(captured_by_path)
        if len(roots) != len(set(roots)):
            msg = "isolated process inputs have competing physical owners"
            raise ValueError(msg)
        if any(root == Path(root.anchor) for root in roots):
            msg = "isolated process cannot expose the host filesystem root"
            raise ValueError(msg)
        if any(
            root.is_relative_to(other)
            for root in roots
            for other in roots
            if root != other
        ):
            msg = "isolated process runtime roots overlap"
            raise ValueError(msg)
        if isolation.launcher.mode is None or not isolation.launcher.mode & 0o111:
            msg = "isolated process launcher is not an authenticated executable"
            raise ValueError(msg)
        if isolation.launcher.mode & 0o6000:
            msg = "isolated process launcher cannot carry set-id privileges"
            raise ValueError(msg)
        for captured in files:
            current = FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
                captured.path, required=captured.content is not None
            ).unwrap()
            if current != captured:
                msg = f"isolated process input changed: {captured.path}"
                raise ValueError(msg)
        runtime_descriptors: list[tuple[int, Path]] = []
        for tree in isolation.runtime_trees:
            current = FlextCliUtilitiesFilesPart05.atomic_inventory_physical_tree(
                tree.root.path
            ).unwrap()
            if current != tree:
                msg = f"isolated process runtime tree changed: {tree.root.path}"
                raise ValueError(msg)
            for entry in tree.entries:
                if entry.kind != "symlink":
                    continue
                if entry.link_target is None:
                    msg = f"isolated runtime link has no captured target: {entry.path}"
                    raise ValueError(msg)
                target = Path(entry.link_target)
                target = Path(
                    os.path.normpath(
                        target if target.is_absolute() else entry.path.parent / target
                    )
                )
                if not any(target.is_relative_to(root) for root in roots) and (
                    target not in paths
                ):
                    msg = f"isolated runtime link escapes its declared closure: {entry.path}"
                    raise ValueError(msg)
            opened = state.stack.enter_context(
                FlextCliUtilitiesAtomicParentDescriptor.physical_directory(
                    tree.root.path
                )
            )
            if (opened.state.st_dev, opened.state.st_ino) != (
                tree.root.device,
                tree.root.inode,
            ):
                msg = f"isolated runtime root identity changed: {tree.root.path}"
                raise ValueError(msg)
            runtime_descriptors.append((opened.descriptor, tree.root.path))
        exposed = tuple(
            item.path
            for item in (*isolation.sources, *isolation.runtime_files)
            if item.content is not None
        )
        executable = Path(command[0])
        working = Path(request.cwd)
        if not any(executable.is_relative_to(root) for root in roots) and (
            executable not in exposed
        ):
            msg = "isolated executable is outside its declared runtime closure"
            raise ValueError(msg)
        if not any(working.is_relative_to(root) for root in roots) and not any(
            working == path.parent or working in path.parents for path in exposed
        ):
            msg = "isolated working directory is outside its declared source closure"
            raise ValueError(msg)
        launcher = cls._sealed_process_input(state, isolation.launcher)
        cls._qualify_policy_compiler(isolation)
        policy = cls._compile_process_policy(request, state, grace_seconds)
        if policy is None:
            return None
        inherited = [launcher, policy]
        arguments = [
            f"/proc/self/fd/{launcher}",
            "--unshare-user",
            "--unshare-ipc",
            "--unshare-pid",
            "--unshare-net",
            "--unshare-uts",
            "--unshare-cgroup",
            "--disable-userns",
            "--assert-userns-disabled",
            "--new-session",
            "--die-with-parent",
            "--cap-drop",
            "ALL",
            "--clearenv",
            "--seccomp",
            str(policy),
        ]
        for descriptor, root in runtime_descriptors:
            inherited.append(descriptor)
            arguments.extend(("--ro-bind-fd", str(descriptor), str(root)))
        for captured in (
            isolation.launcher,
            *isolation.sources,
            *isolation.runtime_files,
        ):
            if captured.content is None:
                continue
            descriptor = (
                launcher
                if captured is isolation.launcher
                else (cls._sealed_process_input(state, captured))
            )
            if descriptor != launcher:
                inherited.append(descriptor)
            if captured.mode is None:
                msg = f"isolated process input has no captured mode: {captured.path}"
                raise ValueError(msg)
            arguments.extend((
                "--perms",
                format(captured.mode, "o"),
                "--ro-bind-data",
                str(descriptor),
                str(captured.path),
            ))
        for name, value in isolation.environment:
            arguments.extend(("--setenv", name, value))
        arguments.extend(("--chdir", str(working), "--remount-ro", "/", "--", *command))
        return tuple(arguments), {}, tuple(inherited)

    @classmethod
    def _qualify_policy_compiler(
        cls, isolation: m.Cli.ProcessReadOnlyIsolation
    ) -> None:
        """Bind the compiler to an actual current bootstrap evidence row.

        Raises:
            ValueError: If the qualification evidence is missing, changed,
                unqualified, or inconsistent with the declared isolation.

        """
        qualification = isolation.policy_compiler
        if qualification.issuer_receipt.content is None:
            msg = "native policy compiler has no original bootstrap issuer bytes"
            raise ValueError(msg)
        report = m.Cli.ProcessNativeQualificationReport.model_validate_json(
            qualification.issuer_receipt.content
        )
        evidence = m.Cli.ProcessNativeToolEvidence.model_validate(
            qualification.model_dump(exclude={"issuer_receipt", "artifact"})
        )
        matches = tuple(
            item
            for receipt in report.receipts
            for item in receipt.native_tool_qualifications
            if item == evidence
        )
        if len(matches) != 1:
            msg = (
                "native policy compiler lacks one original bootstrap qualification row"
            )
            raise ValueError(msg)
        if not all(cls.process_succeeded(outcome) for outcome in (
            qualification.native_build_outcome,
            qualification.native_abi_probe_outcome,
            qualification.native_policy_probe_outcome,
        )):
            msg = "native policy compiler build, ABI or denial qualification failed"
            raise ValueError(msg)
        policy = m.Cli.ProcessNativePolicyRequest(
            denied_syscalls=config.ProcessIsolation.denied_syscalls
        ).model_dump_json().encode("utf-8")
        if hashlib.sha256(policy).hexdigest() != qualification.policy_sha256:
            msg = "native denial qualification differs from the canonical process policy"
            raise ValueError(msg)
        observed = tuple(probe.syscall for probe in qualification.native_policy_probes)
        if len(observed) != len(set(observed)) or set(observed) != set(
            config.ProcessIsolation.denied_syscalls
        ) or any(
            probe.observed_errno != errno.EACCES
            for probe in qualification.native_policy_probes
        ):
            msg = "native policy qualification lacks complete original denial observations"
            raise ValueError(msg)
        if qualification.architecture != isolation.architecture:
            msg = "native policy compiler qualification has a different ABI"
            raise ValueError(msg)
        declared = FlextCliUtilitiesAtomicFileSnapshot.read_receipt(
            isolation.compiler_declaration.path, required=True
        )
        if declared not in qualification.declaration_inputs:
            msg = "native policy compiler differs from the independently elected declaration"
            raise ValueError(msg)
        for receipt in (
            qualification.artifact_receipt,
            qualification.abi_reference,
            *qualification.declaration_inputs,
            *qualification.installation_inputs,
            *qualification.source_inputs,
        ):
            current = FlextCliUtilitiesAtomicFileSnapshot.read_receipt(
                receipt.path, required=True
            )
            if current != receipt:
                msg = f"native policy compiler qualification input changed: {receipt.path}"
                raise ValueError(msg)
        artifact = qualification.artifact
        if (
            artifact.path != qualification.artifact_receipt.path
            or artifact.content is None
            or hashlib.sha256(artifact.content).hexdigest()
            != qualification.artifact_receipt.sha256
        ):
            msg = "native policy compiler bytes differ from the installed artifact receipt"
            raise ValueError(msg)
        reference = qualification.abi_reference
        if reference.size is None:
            msg = "native policy compiler has no captured interpreter ABI"
            raise ValueError(msg)
        with FlextCliUtilitiesAtomicFileSnapshot.receipt_reader(reference) as reader:
            reference_bytes = reader.read_range(0, reference.size)
        if cls._elf_identity(
            artifact.content, require_static=True
        ) != cls._elf_identity(reference_bytes, require_static=False):
            msg = "native policy compiler ELF ABI differs from the declared interpreter"
            raise ValueError(msg)

    @staticmethod
    def _elf_identity(content: bytes, *, require_static: bool) -> tuple[int, int, int]:
        """Read the immutable ELF ABI and reject dynamic native compiler loading.

        Returns:
            The ELF class, data encoding, and machine identifiers read from
            the immutable header bytes.

        Raises:
            ValueError: If the ELF header is absent or unsupported, the
                static program table is incomplete, or a required static
                binary carries an interpreter or shared-library dependency.

        """
        if len(content) < 64 or content[:4] != b"\x7fELF":
            msg = "native policy compiler/reference has no complete ELF header"
            raise ValueError(msg)
        elf_class, encoding = content[4], content[5]
        if elf_class not in {1, 2} or encoding not in {1, 2} or content[6] != 1:
            msg = "native policy compiler/reference ELF ABI is unsupported"
            raise ValueError(msg)
        order = "<" if encoding == 1 else ">"
        machine = int(struct.unpack_from(f"{order}H", content, 18)[0])
        if not require_static:
            return elf_class, encoding, machine
        wide = elf_class == 2
        table = int(
            struct.unpack_from(
                f"{order}{'Q' if wide else 'I'}", content, 32 if wide else 28
            )[0]
        )
        stride, count = (
            int(value)
            for value in struct.unpack_from(f"{order}HH", content, 54 if wide else 42)
        )
        minimum = 56 if wide else 32
        if not count or stride < minimum or table + stride * count > len(content):
            msg = "native policy compiler ELF program table is incomplete"
            raise ValueError(msg)
        for index in range(count):
            offset = table + index * stride
            kind = int(struct.unpack_from(f"{order}I", content, offset)[0])
            if kind == 3:  # PT_INTERP, immutable System V ELF protocol.
                msg = "native policy compiler has an ambient ELF interpreter"
                raise ValueError(msg)
            if kind != 2:  # PT_DYNAMIC.
                continue
            payload = int(
                struct.unpack_from(
                    f"{order}{'Q' if wide else 'I'}",
                    content,
                    offset + (8 if wide else 4),
                )[0]
            )
            size = int(
                struct.unpack_from(
                    f"{order}{'Q' if wide else 'I'}",
                    content,
                    offset + (32 if wide else 16),
                )[0]
            )
            entry_size = 16 if wide else 8
            if payload + size > len(content) or size % entry_size:
                msg = "native policy compiler ELF dynamic table is incomplete"
                raise ValueError(msg)
            for position in range(payload, payload + size, entry_size):
                tag = int(
                    struct.unpack_from(
                        f"{order}{'q' if wide else 'i'}", content, position
                    )[0]
                )
                if tag == 1:  # DT_NEEDED.
                    msg = (
                        "native policy compiler has ambient shared-library dependencies"
                    )
                    raise ValueError(msg)
                if tag == 0:  # DT_NULL.
                    break
        return elf_class, encoding, machine

    @classmethod
    def _compile_process_policy(
        cls,
        request: m.Cli.RuntimeProcessRequest,
        state: m.Cli.RuntimeProcessState,
        grace_seconds: float,
    ) -> int | None:
        """Run the qualified static SDK compiler through the same public process port.

        Returns:
            The sealed descriptor number of the compiled policy bytes, or
            ``None`` when the compiler outcome failed and was recorded in
            the lifecycle state.

        Raises:
            ValueError: If the bounded isolation lifecycle is missing or
                the compiler emitted incomplete BPF bytes.

        """
        isolation = request.isolation
        if isolation is None or state.final_deadline is None:
            msg = "native policy compilation requires its bounded isolation lifecycle"
            raise ValueError(msg)
        compiler = cls._sealed_process_input(state, isolation.policy_compiler.artifact)
        policy = m.Cli.ProcessNativePolicyRequest(
            denied_syscalls=config.ProcessIsolation.denied_syscalls
        )
        compiled = cls.run_bytes(
            (f"/proc/self/fd/{compiler}",),
            cwd=request.cwd,
            options=m.Cli.ProcessOptions(
                input_data=policy.model_dump_json(),
                env={},
                inherit_environment=False,
                pass_fds=(compiler,),
                deadline=m.Cli.ProcessDeadline(
                    expires_at_monotonic=state.final_deadline,
                    termination_grace_seconds=grace_seconds,
                ),
            ),
        ).unwrap()
        if not cls.process_succeeded(compiled.outcome):
            state.return_code = compiled.outcome.raw_return_code
            state.timed_out = compiled.outcome.timed_out
            if compiled.outcome.forwarded_signal is not None:
                state.received_signals.append(compiled.outcome.forwarded_signal)
            state.stdout_output.extend(compiled.stdout)
            state.stderr_output.extend(compiled.stderr)
            return None
        if not compiled.stdout or len(compiled.stdout) % 8:
            msg = "qualified native SDK compiler emitted incomplete BPF"
            raise ValueError(msg)
        return cls._sealed_process_bytes(
            state, "native-readonly-policy", compiled.stdout, 0o400
        )

    @staticmethod
    def _sealed_process_input(
        state: m.Cli.RuntimeProcessState,
        captured: m.Cli.AtomicFileState,
    ) -> int:
        """Retain exact captured bytes in an immutable anonymous native file.

        Returns:
            The descriptor number of the sealed anonymous file carrying the
            exact captured bytes and mode.

        Raises:
            ValueError: If the captured input lacks bytes or a captured
                mode. The sealed-byte write underneath can still fail with
                ``OSError``.

        """
        if captured.content is None or captured.mode is None:
            msg = f"isolated process input has no captured bytes: {captured.path}"
            raise ValueError(msg)
        return FlextCliUtilitiesRuntimeProcessExecutionMixin._sealed_process_bytes(
            state, captured.path.name, captured.content, captured.mode
        )

    @staticmethod
    def _sealed_process_bytes(
        state: m.Cli.RuntimeProcessState, name: str, content: bytes, mode: int
    ) -> int:
        """Seal exact process-owner bytes in an anonymous descriptor.

        Returns:
            The descriptor number of the sealed anonymous file carrying the
            exact bytes and mode.

        Raises:
            OSError: If the anonymous file cannot be created, a write makes
                no progress, or sealing fails.

        """
        descriptor = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
        state.stack.callback(os.close, descriptor)
        remaining = memoryview(content)
        while remaining:
            count = os.write(descriptor, remaining)
            if count <= 0:
                msg = f"isolated process input write made no progress: {name}"
                raise OSError(msg)
            remaining = remaining[count:]
        os.fchmod(descriptor, mode & 0o777)
        os.lseek(descriptor, 0, os.SEEK_SET)
        fcntl.fcntl(
            descriptor,
            fcntl.F_ADD_SEALS,
            fcntl.F_SEAL_WRITE
            | fcntl.F_SEAL_GROW
            | fcntl.F_SEAL_SHRINK
            | fcntl.F_SEAL_SEAL,
        )
        return descriptor

    @classmethod
    def _attach_process_streams(
        cls,
        process: p.Cli.ProcessHandle,
        request: m.Cli.RuntimeProcessRequest,
        state: m.Cli.RuntimeProcessState,
        stdin: t.Triple[BinaryIO | None, BinaryIO | None, bytes],
        live_fds: t.Pair[int | None, int | None],
    ) -> threading.Thread:
        """Attach child I/O without losing ownership on a partial failure.

        Returns:
            The root waiter already retained by the lifecycle state.

        """
        stdin_reader, stdin_writer, stdin_payload = stdin
        if stdin_reader is not None:
            try:
                stdin_reader.close()
            except (OSError, ValueError) as exc:
                state.failures.append(
                    r[str]
                    .fail(
                        f"parent stdin reader close error: {exc}",
                        exception=exc,
                    )
                    .error
                    or str(exc),
                )
        waiter = cls._start_root_waiter(
            process,
            state.return_codes,
            state.failures,
            state.process_done,
            state.wake,
        )
        state.waiter = waiter
        state.pump_streams.extend(
            cls._start_process_output(
                process,
                state,
                live_fds,
                capture_output=request.capture_output,
            ),
        )
        if stdin_writer is not None:
            input_thread = cls._start_input_pump(
                stdin_writer,
                stdin_payload,
                state.failures,
                state.wake,
            )
            state.input_pump = (input_thread, stdin_writer)
        return waiter

    @classmethod
    def _finalize_lifecycle(cls, state: m.Cli.RuntimeProcessState) -> None:
        if (
            state.process is not None
            and state.waiter is not None
            and not state.cleanup_complete
        ):
            state.return_code = cls._reap_and_drain(
                state.process,
                state.waiter,
                state,
            )
        for stream in (state.durable_log, state.durable_stderr):
            if stream is not None:
                state.cleanup_errors.extend(cls._flush_durable_log(stream))
        close_error = cls._windows_job_close(state.job_handle)
        if close_error is not None:
            state.cleanup_errors.append(close_error)
        state.cleanup_errors.extend(cls._close_process_resources(state.stack))
        state.cleanup_errors.extend(
            cls._restore_forwarding_handlers(state.restore_handlers),
        )
        if state.primary_error is not None:
            for cleanup_error in state.cleanup_errors:
                state.primary_error.add_note(cleanup_error)


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessExecutionMixin"]
