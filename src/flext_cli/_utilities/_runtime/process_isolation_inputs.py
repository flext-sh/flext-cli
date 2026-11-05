"""Authenticated inputs and closures of read-only native process isolation.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import platform
import sys
from collections.abc import MutableMapping
from pathlib import Path

from flext_cli import m, p
from flext_cli._utilities import FlextCliUtilitiesAtomicParentDescriptor
from flext_cli._utilities._files.binary_reads import FlextCliUtilitiesFilesPart03
from flext_cli._utilities._files.flextcliutilitiesfiles_part_05 import (
    FlextCliUtilitiesFilesPart05,
)
from flext_cli._utilities._runtime.process_native_tools import (
    FlextCliUtilitiesRuntimeProcessNativeTools,
)


class FlextCliUtilitiesRuntimeProcessIsolationInputs(
    FlextCliUtilitiesRuntimeProcessNativeTools,
):
    """Require declared isolation inputs, roots, and closures to stay exact."""

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
            not name or "=" in name or "\0" in f"{name}{value}"
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


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessIsolationInputs"]
