"""Read-only native confinement prepared inside one process lifecycle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING

if sys.platform == "linux":
    import fcntl

from flext_cli import m, p
from flext_cli._utilities._runtime.process_isolation_inputs import (
    FlextCliUtilitiesRuntimeProcessIsolationInputs,
)


class FlextCliUtilitiesRuntimeProcessIsolation(
    FlextCliUtilitiesRuntimeProcessIsolationInputs,
):
    """Authenticate isolation inputs and build the confined launcher argv."""

    if TYPE_CHECKING:

        @classmethod
        def _execute_streamed_process(
            cls,
            request: p.Cli.RuntimeProcessRequest,
        ) -> p.Result[p.Cli.CommandBytesOutput]: ...

    @classmethod
    def _prepare_process_isolation(
        cls,
        request: p.Cli.RuntimeProcessRequest,
        state: m.Cli.RuntimeProcessState,
        command: tuple[str, ...],
        timing: m.Cli.RuntimeProcessTiming,
    ) -> tuple[tuple[str, ...], Mapping[str, str] | None, tuple[int, ...]] | None:
        """Prepare explicit native confinement inside the existing lifecycle.

        Returns:
            The effective command, environment, and inherited descriptor
            numbers: the caller's declaration when isolation is not requested,
            otherwise the confined launcher argv with a cleared environment
            and the sealed input and runtime-root descriptors, or ``None``
            when the bounded native policy compilation failed.

        """
        isolation = request.isolation
        if isolation is None:
            return command, request.env, request.pass_fds
        cls._ensure_isolation_platform_qualified(isolation, request)
        cls._ensure_isolation_environment_qualified(isolation)
        working = cls._ensure_isolation_targets_absolute(request, command)
        roots, paths, files, launcher_artifact = cls._ensure_isolation_inputs_unique(
            isolation
        )
        cls._ensure_isolation_roots_qualified(roots)
        cls._ensure_isolation_launcher_qualified(launcher_artifact)
        cls._ensure_isolation_inputs_unchanged(files)
        runtime_descriptors = cls._retain_isolation_runtime_descriptors(
            state, isolation, roots, paths
        )
        cls._ensure_isolation_closure_qualified(working, isolation, roots, command)
        cls._qualify_isolation_native_tools(isolation)
        sealed = cls._seal_isolation_executors(
            request, state, isolation, timing.grace_seconds
        )
        if sealed is None:
            return None
        arguments, inherited = cls._build_isolation_arguments(
            state,
            isolation,
            m.Cli.ProcessIsolationSeal(
                launcher=sealed[0],
                policy=sealed[1],
                runtime_descriptors=tuple(runtime_descriptors),
            ),
        )
        arguments.extend(("--chdir", str(working), "--remount-ro", "/", "--", *command))
        return tuple(arguments), {}, tuple(inherited)











    @classmethod
    def _qualify_isolation_native_tools(
        cls, isolation: p.Cli.ProcessReadOnlyIsolation
    ) -> None:
        """Qualify the launcher and policy compiler bootstrap evidence rows."""
        cls._qualify_native_tool(isolation, "isolation-launcher")
        cls._qualify_native_tool(isolation, "policy-compiler")

    @classmethod
    def _seal_isolation_executors(
        cls,
        request: p.Cli.RuntimeProcessRequest,
        state: m.Cli.RuntimeProcessState,
        isolation: p.Cli.ProcessReadOnlyIsolation,
        grace_seconds: float,
    ) -> tuple[int, int] | None:
        """Seal the launcher and compile the read-only policy descriptor.

        Returns:
            The sealed launcher and policy descriptor numbers, or ``None``
            when the bounded policy compilation failed.

        """
        launcher = cls._sealed_process_input(state, isolation.launcher.artifact)
        policy = cls._compile_process_policy(request, state, grace_seconds)
        if policy is None:
            return None
        return launcher, policy

    @classmethod
    def _build_isolation_arguments(
        cls,
        state: m.Cli.RuntimeProcessState,
        isolation: p.Cli.ProcessReadOnlyIsolation,
        sealed: m.Cli.ProcessIsolationSeal,
    ) -> tuple[list[str], list[int]]:
        """Bind sealed inputs and runtime roots into the confined argv.

        Returns:
            The confined launcher arguments without the working-directory
            tail, and the inherited descriptor numbers.

        Raises:
            ValueError: If one captured input has no captured mode.

        """
        launcher, policy = sealed.launcher, sealed.policy
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
        for descriptor, root in sealed.runtime_descriptors:
            inherited.append(descriptor)
            arguments.extend(("--ro-bind-fd", str(descriptor), str(root)))
        for captured in (
            isolation.launcher.artifact,
            *isolation.sources,
            *isolation.runtime_files,
        ):
            if captured.content is None:
                continue
            descriptor = (
                launcher
                if captured is isolation.launcher.artifact
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
        return arguments, inherited

    @classmethod
    def _compile_process_policy(
        cls,
        request: p.Cli.RuntimeProcessRequest,
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
        compiled = cls._execute_streamed_process(
            m.Cli.RuntimeProcessRequest(
                cmd=(
                    f"/proc/self/fd/{compiler}",
                    *cls.native_process_policy_arguments(),
                ),
                cwd=request.cwd,
                env={},
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
        captured: p.Cli.AtomicFileState,
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
        return FlextCliUtilitiesRuntimeProcessIsolation._sealed_process_bytes(
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


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessIsolation"]
