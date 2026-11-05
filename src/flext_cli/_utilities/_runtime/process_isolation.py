"""Read-only native confinement prepared inside one process lifecycle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import platform
import sys
from collections.abc import Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

if sys.platform == "linux":
    import fcntl

from flext_cli import m, p, t
from flext_cli._utilities import FlextCliUtilitiesAtomicParentDescriptor
from flext_cli._utilities._files.binary_reads import FlextCliUtilitiesFilesPart03
from flext_cli._utilities._files.flextcliutilitiesfiles_part_05 import (
    FlextCliUtilitiesFilesPart05,
)
from flext_cli._utilities._runtime.process_native_tools import (
    FlextCliUtilitiesRuntimeProcessNativeTools,
)


class FlextCliUtilitiesRuntimeProcessIsolation(
    FlextCliUtilitiesRuntimeProcessNativeTools,
):
    """Authenticate isolation inputs and build the confined launcher argv."""

    if TYPE_CHECKING:

        @classmethod
        def run_bytes(
            cls,
            cmd: Sequence[str],
            cwd: t.Cli.TextPath | None = None,
            timeout: int | None = None,
            *,
            options: p.Cli.ProcessOptions | None = None,
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
    def _ensure_isolation_platform_qualified(
        cls,
        isolation: p.Cli.ProcessReadOnlyIsolation,
        request: p.Cli.RuntimeProcessRequest,
    ) -> None:
        """Require a natively qualified host for the read-only isolation.

        Raises:
            ValueError: If the host platform or architecture does not
                qualify the declaration, or caller descriptors would be
                inherited.

        """
        if (
            sys.platform != isolation.platform
            or platform.machine() != isolation.architecture
        ):
            msg = (
                "read-only process isolation has no "
                "qualified native platform capability"
            )
            raise ValueError(msg)
        if request.pass_fds:
            msg = "isolated processes cannot inherit caller file descriptors"
            raise ValueError(msg)

    @classmethod
    def _ensure_isolation_environment_qualified(
        cls, isolation: p.Cli.ProcessReadOnlyIsolation
    ) -> None:
        """Require complete, unique, and valid child environment names.

        Raises:
            ValueError: If environment names are empty, reserved, or
                competing, or a declared value carries a NUL byte.

        """
        environment_names = tuple(name for name, _value in isolation.environment)
        if len(set(environment_names)) != len(environment_names) or any(
            not name or "=" in name or "\0" in name or "\0" in value
            for name, value in isolation.environment
        ):
            msg = "isolated process environment has invalid or competing declarations"
            raise ValueError(msg)

    @classmethod
    def _ensure_isolation_targets_absolute(
        cls, request: p.Cli.RuntimeProcessRequest, command: tuple[str, ...]
    ) -> Path:
        """Require an absolute executable and working directory declaration.

        Returns:
            The declared absolute working directory.

        Raises:
            ValueError: If the declared executable or working directory is
                missing or relative.

        """
        if not command or not Path(command[0]).is_absolute():
            msg = "isolated process requires an absolute declared executable"
            raise ValueError(msg)
        if request.cwd is None or not Path(request.cwd).is_absolute():
            msg = "isolated process requires an absolute declared working directory"
            raise ValueError(msg)
        return Path(request.cwd)

    @classmethod
    def _ensure_isolation_inputs_unique(
        cls, isolation: p.Cli.ProcessReadOnlyIsolation
    ) -> tuple[
        tuple[Path, ...],
        tuple[Path, ...],
        tuple[p.Cli.AtomicFileState, ...],
        p.Cli.AtomicFileState,
    ]:
        """Deduplicate declared isolation inputs and require unique owners.

        Returns:
            The declared runtime roots, the deduplicated input paths, the
            deduplicated captured inputs, and the launcher artifact.

        Raises:
            ValueError: If two declared inputs claim one physical path, or
                two runtime roots claim one physical root.

        """
        roots = tuple(tree.root.path for tree in isolation.runtime_trees)
        launcher_artifact = isolation.launcher.artifact
        files = (
            launcher_artifact,
            isolation.launcher.issuer_receipt,
            isolation.launcher_declaration,
            isolation.policy_compiler.artifact,
            isolation.policy_compiler.issuer_receipt,
            isolation.compiler_declaration,
            *isolation.sources,
            *isolation.runtime_files,
        )
        captured_by_path: MutableMapping[Path, p.Cli.AtomicFileState] = {}
        for captured in files:
            if captured_by_path.setdefault(captured.path, captured) != captured:
                msg = f"isolated input has competing physical states: {captured.path}"
                raise ValueError(msg)
        files = tuple(captured_by_path.values())
        paths = tuple(captured_by_path)
        if len(roots) != len(set(roots)):
            msg = "isolated process inputs have competing physical owners"
            raise ValueError(msg)
        return roots, paths, files, launcher_artifact

    @classmethod
    def _ensure_isolation_roots_qualified(cls, roots: tuple[Path, ...]) -> None:
        """Require disjoint runtime roots inside the host filesystem.

        Raises:
            ValueError: If one runtime root is the host filesystem root or
                two runtime roots overlap.

        """
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

    @classmethod
    def _ensure_isolation_launcher_qualified(
        cls, launcher_artifact: p.Cli.AtomicFileState
    ) -> None:
        """Require an executable, unprivileged isolated launcher.

        Raises:
            ValueError: If the launcher has no captured executable mode or
                carries set-id privilege bits.

        """
        if launcher_artifact.mode is None or not launcher_artifact.mode & 0o111:
            msg = "isolated process launcher is not an authenticated executable"
            raise ValueError(msg)
        if launcher_artifact.mode & 0o6000:
            msg = "isolated process launcher cannot carry set-id privileges"
            raise ValueError(msg)

    @classmethod
    def _ensure_isolation_inputs_unchanged(
        cls, files: tuple[p.Cli.AtomicFileState, ...]
    ) -> None:
        """Require every declared input to match its captured state.

        Raises:
            ValueError: If one declared input changed since its capture.

        """
        for captured in files:
            current = FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
                captured.path, required=captured.content is not None
            ).unwrap()
            if current != captured:
                msg = f"isolated process input changed: {captured.path}"
                raise ValueError(msg)

    @classmethod
    def _retain_isolation_runtime_descriptors(
        cls,
        state: m.Cli.RuntimeProcessState,
        isolation: p.Cli.ProcessReadOnlyIsolation,
        roots: tuple[Path, ...],
        paths: tuple[Path, ...],
    ) -> list[tuple[int, Path]]:
        """Retain directory descriptors for every unchanged runtime tree.

        Returns:
            The open directory descriptor and declared root path retained
            for every authenticated runtime tree.

        Raises:
            ValueError: If one runtime tree changed, one captured link
                escapes its declared closure, or one root identity changed.

        """
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
                cls._ensure_runtime_link_captured(entry, roots, paths)
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
        return runtime_descriptors

    @classmethod
    def _ensure_runtime_link_captured(
        cls,
        entry: p.Cli.AtomicPhysicalTreeEntry,
        roots: tuple[Path, ...],
        paths: tuple[Path, ...],
    ) -> None:
        """Require one captured symlink target to stay in its closure.

        Raises:
            ValueError: If the captured link has no target or resolves
                outside every declared runtime root and input path.

        """
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

    @classmethod
    def _ensure_isolation_closure_qualified(
        cls,
        working: Path,
        isolation: p.Cli.ProcessReadOnlyIsolation,
        roots: tuple[Path, ...],
        command: tuple[str, ...],
    ) -> None:
        """Require the executable and working directory inside their closures.

        Raises:
            ValueError: If the executable is outside the declared runtime
                closure or the working directory is outside the declared
                source closure.

        """
        exposed = tuple(
            item.path
            for item in (*isolation.sources, *isolation.runtime_files)
            if item.content is not None
        )
        executable = Path(command[0])
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
        compiled = cls.run_bytes(
            (f"/proc/self/fd/{compiler}", *cls.native_process_policy_arguments()),
            cwd=request.cwd,
            options=m.Cli.ProcessOptions(
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
