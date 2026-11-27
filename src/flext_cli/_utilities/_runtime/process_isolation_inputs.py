"""Authenticated inputs and closures of read-only native process isolation.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import platform
import sys
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import ClassVar

from flext_cli import m, p
from flext_cli._utilities import (
    FlextCliUtilitiesAtomicFilePath,
    FlextCliUtilitiesAtomicParentDescriptor,
    FlextCliUtilitiesAtomicTreePhysical,
)
from flext_cli._utilities._files import (
    FlextCliUtilitiesFilesPart03,
    FlextCliUtilitiesFilesPart05,
)
from flext_cli._utilities._runtime import FlextCliUtilitiesRuntimeProcessNativeTools


class FlextCliUtilitiesRuntimeProcessIsolationInputs(
    FlextCliUtilitiesRuntimeProcessNativeTools,
):
    """Require declared isolation inputs, roots, and closures to stay exact."""

    _fixture_mounts: ClassVar[tuple[tuple[str, Path], ...]] = (
        ("--dev", Path("/dev")),
        ("--proc", Path("/proc")),
    )
    _fixture_private_paths: ClassVar[tuple[Path, ...]] = (
        *(path for _, path in _fixture_mounts),
        Path("/run"),
        Path("/sys"),
    )

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
    ) -> tuple[tuple[Path, ...], tuple[Path, ...], tuple[p.Cli.AtomicFileState, ...]]:
        """Deduplicate declared isolation inputs and require unique owners.

        Returns:
            The declared runtime roots, deduplicated input paths and
            deduplicated captured inputs.

        Raises:
            ValueError: If two declared inputs claim one physical path, or
                runtime roots declare competing owners.

        """
        roots = tuple(tree.root.path for tree in isolation.runtime_trees)
        if (
            isinstance(isolation, m.Cli.ProcessFixtureIsolation)
            and isolation.runtime_tree_roots
        ):
            if roots:
                msg = "isolated runtime roots and captured trees are mutually exclusive"
                raise ValueError(msg)
            roots = isolation.runtime_tree_roots
        files = (
            isolation.launcher.artifact,
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
        return roots, paths, files

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
        for root in roots:
            FlextCliUtilitiesAtomicFilePath.validate_directory_path(root)
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
        state: p.Cli.RuntimeProcessState,
        isolation: p.Cli.ProcessReadOnlyIsolation,
        roots: tuple[Path, ...],
        paths: tuple[Path, ...],
    ) -> list[tuple[int, Path]]:
        """Capture fixture roots and verify captured trees on the mounted descriptors.

        Returns:
            The open directory descriptor and declared root path retained
            for every authenticated runtime tree.

        Raises:
            ValueError: If one runtime tree changed, one captured link
                escapes its declared closure, or one root identity changed.

        """
        runtime_descriptors: list[tuple[int, Path]] = []
        expected = {tree.root.path: tree for tree in isolation.runtime_trees}
        for path in roots:
            current, descriptor = state.stack.enter_context(
                FlextCliUtilitiesAtomicTreePhysical.retained_physical_tree(path)
            )
            if path in expected and current != expected[path]:
                msg = f"isolated process runtime tree changed: {path}"
                raise ValueError(msg)
            for entry in current.entries:
                if entry.kind != "symlink":
                    continue
                cls._ensure_runtime_link_captured(entry, roots, paths)
            runtime_descriptors.append((descriptor, path))
        return runtime_descriptors

    @classmethod
    def _retain_isolation_writable_directories(
        cls,
        state: p.Cli.RuntimeProcessState,
        isolation: p.Cli.ProcessReadOnlyIsolation,
        working: Path,
        roots: tuple[Path, ...],
        paths: tuple[Path, ...],
    ) -> tuple[tuple[int, Path], ...]:
        """Keep the fixture output and durable data disjoint from input mounts.

        Returns:
            Held descriptors and mount paths for the fixture request.

        Raises:
            ValueError: If fixture inputs overlap private paths or persistent
                data is outside the working directory.

        """
        if not isinstance(isolation, m.Cli.ProcessFixtureIsolation):
            return ()
        for private_path in cls._fixture_private_paths:
            if any(
                root.is_relative_to(private_path) or private_path.is_relative_to(root)
                for root in roots
            ) or any(path.is_relative_to(private_path) for path in paths):
                msg = f"isolated process input overlaps a private mount: {private_path}"
                raise ValueError(msg)
        output = cls._retain_isolation_writable_directory(
            state, isolation.output_directory, roots, paths, require_empty=True
        )
        persistent = isolation.persistent_directory
        if persistent is None or isolation.private_checkout is not None:
            return (output,)
        if working not in persistent.root.path.parents:
            msg = "persistent fixture data must be below the working directory"
            raise ValueError(msg)
        return (
            output,
            cls._retain_isolation_writable_directory(
                state, persistent, (*roots, output[1]), paths, require_empty=False
            ),
        )

    @staticmethod
    def _private_checkout_sources(
        isolation: p.Cli.ProcessFixtureIsolation,
        working: Path,
        runtime_roots: tuple[Path, ...],
    ) -> dict[Path, Path]:
        """Map the captured source files into the elected checkout.

        Returns:
            Physical capture paths and their confined destinations.

        Raises:
            ValueError: If the backing, origin or declared names overlap.

        """
        checkout = isolation.private_checkout
        if checkout is None:
            return {}
        source_root = checkout.source_root
        if (
            checkout.backing.root.path != working
            or working == Path(working.anchor)
            or not source_root.is_absolute()
        ):
            msg = "private checkout requires its own physical cwd and source root"
            raise ValueError(msg)
        if (
            working.is_relative_to(source_root)
            or source_root.is_relative_to(working)
            or working.resolve(strict=True) != working
            or source_root.resolve(strict=True) != source_root
        ):
            msg = "private checkout requires disjoint canonical cwd and source paths"
            raise ValueError(msg)
        names = checkout.persistent_filenames
        if len(set(names)) != len(names) or any(
            not name or name in {".", ".."} or Path(name).name != name or "\0" in name
            for name in names
        ):
            msg = "private checkout requires unique durable basenames"
            raise ValueError(msg)
        destinations: dict[Path, Path] = {}
        if any(source_root.is_relative_to(root) for root in runtime_roots):
            msg = "private checkout source root overlaps a runtime mount"
            raise ValueError(msg)
        fixed_paths = {
            isolation.launcher.artifact.path,
            isolation.policy_compiler.artifact.path,
            *(item.path for item in isolation.runtime_files),
        }
        for source in isolation.sources:
            if (
                source.content is None
                or source.path in fixed_paths
                or source_root not in source.path.parents
                or source.path.resolve(strict=True) != source.path
                or any(source.path.is_relative_to(root) for root in runtime_roots)
            ):
                msg = f"private checkout requires a captured source: {source.path}"
                raise ValueError(msg)
            relative = source.path.relative_to(source_root)
            if relative.parts[0] in names:
                msg = f"private checkout source overlaps durable data: {relative}"
                raise ValueError(msg)
            destinations[source.path] = working / relative
        return destinations

    @classmethod
    def _retain_private_checkout(
        cls,
        state: p.Cli.RuntimeProcessState,
        checkout: p.Cli.ProcessFixtureCheckout,
        persistent: p.Cli.AtomicPhysicalTreeManifest | None,
        protected: tuple[tuple[Path, ...], tuple[Path, ...]],
        destinations: tuple[Path, ...],
    ) -> tuple[int, tuple[int, Path] | None]:
        """Hold the private backing and settle its inventory on process exit.

        Returns:
            Held bindings for the working directory and declared child.

        Raises:
            ValueError: If backing identity or allowed contents have changed.

        """
        backing = checkout.backing
        root = backing.root.path
        roots, paths = protected
        if any(
            root.is_relative_to(other) or other.is_relative_to(root)
            for other in (*roots, *cls._fixture_private_paths)
        ) or any(path.is_relative_to(root) for path in paths):
            msg = f"private checkout overlaps an original input or mount: {root}"
            raise ValueError(msg)
        opened = state.stack.enter_context(
            FlextCliUtilitiesAtomicParentDescriptor.physical_directory(root)
        )
        current = FlextCliUtilitiesFilesPart05.atomic_inventory_physical_tree(
            root, backing
        ).unwrap()
        if (opened.state.st_dev, opened.state.st_ino) != (
            backing.root.device,
            backing.root.inode,
        ) or current != backing:
            msg = f"private checkout backing changed since capture: {root}"
            raise ValueError(msg)
        durable_mount = cls._retain_private_checkout_directory(
            state, checkout, persistent, destinations
        )
        cls._validate_private_checkout(current, checkout, persistent, destinations)
        state.stack.callback(
            cls._settle_private_checkout, checkout, persistent, destinations
        )
        return opened.descriptor, durable_mount

    @classmethod
    def _retain_private_checkout_directory(
        cls,
        state: p.Cli.RuntimeProcessState,
        checkout: p.Cli.ProcessFixtureCheckout,
        persistent: p.Cli.AtomicPhysicalTreeManifest | None,
        destinations: tuple[Path, ...],
    ) -> tuple[int, Path] | None:
        """Authenticate the dedicated durable child without covering sources.

        Returns:
            Held descriptor and target path when the caller declared a child.

        Raises:
            ValueError: If the child or its naming constraint is invalid.

        """
        suffix = checkout.persistent_directory_suffix
        if suffix is None and persistent is None:
            return None
        if (
            persistent is None
            or suffix is None
            or suffix in {"", ".", ".."}
            or Path(suffix).name != suffix
            or "\0" in suffix
        ):
            msg = "private checkout durable directory requires a filename suffix"
            raise ValueError(msg)
        path = persistent.root.path
        if (
            path.parent != checkout.backing.root.path
            or path.name in checkout.persistent_filenames
            or any(
                path.is_relative_to(destination) or destination.is_relative_to(path)
                for destination in destinations
            )
        ):
            msg = f"private checkout durable directory overlaps another input: {path}"
            raise ValueError(msg)
        return cls._retain_isolation_writable_directory(
            state, persistent, (), (), require_empty=False
        )

    @classmethod
    def _settle_private_checkout(
        cls,
        checkout: p.Cli.ProcessFixtureCheckout,
        persistent: p.Cli.AtomicPhysicalTreeManifest | None,
        destinations: tuple[Path, ...],
    ) -> None:
        backing = checkout.backing
        inventoried = FlextCliUtilitiesFilesPart05.atomic_inventory_physical_tree(
            backing.root.path, backing
        )
        if inventoried.failure:
            msg = inventoried.error or "private checkout settlement inventory failed"
            raise ValueError(msg)
        current = inventoried.value
        if (current.root.device, current.root.inode, current.root.mount_id) != (
            backing.root.device,
            backing.root.inode,
            backing.root.mount_id,
        ):
            msg = f"private checkout backing changed identities: {backing.root.path}"
            raise ValueError(msg)
        cls._validate_private_checkout(current, checkout, persistent, destinations)

    @classmethod
    def _validate_private_checkout(
        cls,
        manifest: p.Cli.AtomicPhysicalTreeManifest,
        checkout: p.Cli.ProcessFixtureCheckout,
        persistent: p.Cli.AtomicPhysicalTreeManifest | None,
        destinations: tuple[Path, ...],
    ) -> None:
        root = manifest.root.path
        uid = os.getuid()
        if manifest.root.uid != uid or manifest.root.mode & 0o022:
            msg = f"private checkout backing requires caller ownership: {root}"
            raise ValueError(msg)
        allowed = frozenset(root / name for name in checkout.persistent_filenames)
        durable = cls._validate_private_checkout_directory(
            manifest, persistent, checkout.persistent_directory_suffix
        )
        placeholders = set(destinations)
        directories = {
            parent
            for path in destinations
            for parent in path.parents
            if root in parent.parents
        }
        for entry in manifest.entries:
            if durable is not None and entry.path.is_relative_to(durable):
                continue
            owned = entry.uid == uid and not entry.mode & 0o022
            admitted = (entry.kind == "directory" and entry.path in directories) or (
                entry.kind == "file"
                and entry.link_count == 1
                and (
                    entry.path in allowed
                    or (entry.path in placeholders and entry.size == 0)
                )
            )
            if not owned or not admitted:
                msg = (
                    f"private checkout backing contains ineligible entry: {entry.path}"
                )
                raise ValueError(msg)

    @staticmethod
    def _validate_private_checkout_directory(
        manifest: p.Cli.AtomicPhysicalTreeManifest,
        persistent: p.Cli.AtomicPhysicalTreeManifest | None,
        suffix: str | None,
    ) -> Path | None:
        """Require the original durable directory and eligible shallow entries.

        Returns:
            The path already validated beneath the private checkout.

        Raises:
            ValueError: If the durable directory changed or a file is ineligible.

        """
        if persistent is None or suffix is None:
            return None
        root = persistent.root
        uid = os.getuid()
        found_directory = False
        for entry in manifest.entries:
            if not entry.path.is_relative_to(root.path):
                continue
            owned = entry.uid == uid and not entry.mode & 0o022
            if entry.path == root.path:
                found_directory = (
                    owned
                    and entry.kind == "directory"
                    and (entry.device, entry.inode, entry.mount_id)
                    == (root.device, root.inode, root.mount_id)
                )
                continue
            if (
                not owned
                or entry.kind != "file"
                or entry.link_count != 1
                or entry.path.parent != root.path
                or not entry.path.name.endswith(suffix)
            ):
                msg = (
                    "private checkout durable directory has ineligible file: "
                    f"{entry.path}"
                )
                raise ValueError(msg)
        if not found_directory:
            msg = f"private checkout durable directory changed identity: {root.path}"
            raise ValueError(msg)
        return root.path

    @classmethod
    def _retain_isolation_writable_directory(
        cls,
        state: p.Cli.RuntimeProcessState,
        output: p.Cli.AtomicPhysicalTreeManifest,
        roots: tuple[Path, ...],
        paths: tuple[Path, ...],
        *,
        require_empty: bool,
    ) -> tuple[int, Path]:
        """Retain one authenticated directory for a writable fixture mount.

        Returns:
            The held output descriptor and target path for a fixture request.

        Raises:
            ValueError: If the path overlaps a sealed input or no longer names
                the original private directory, or its contents are ineligible.

        """
        path = output.root.path
        if any(
            path.is_relative_to(root) or root.is_relative_to(path)
            for root in (*roots, *cls._fixture_private_paths)
        ) or any(member.is_relative_to(path) for member in paths):
            msg = f"isolated process output overlaps an input or private mount: {path}"
            raise ValueError(msg)
        uid = os.getuid()
        if (
            output.root.uid != uid
            or output.root.mode & 0o022
            or (require_empty and output.entries)
        ):
            requirement = "empty and owned" if require_empty else "owned"
            msg = f"isolated process output must be {requirement} by the caller: {path}"
            raise ValueError(msg)
        if any(
            entry.kind != "file" or entry.uid != uid or entry.mode & 0o022
            for entry in output.entries
        ):
            msg = f"persistent fixture data requires owned regular files: {path}"
            raise ValueError(msg)
        opened = state.stack.enter_context(
            FlextCliUtilitiesAtomicParentDescriptor.physical_directory(path)
        )
        current = FlextCliUtilitiesFilesPart05.atomic_inventory_physical_tree(path)
        if (opened.state.st_dev, opened.state.st_ino) != (
            output.root.device,
            output.root.inode,
        ) or current.unwrap() != output:
            msg = f"isolated process output has changed since its capture: {path}"
            raise ValueError(msg)
        return opened.descriptor, path

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
        destinations: Mapping[Path, Path],
    ) -> None:
        """Require the executable and working directory inside their closures.

        Raises:
            ValueError: If the executable is outside the declared runtime
                closure or the working directory is outside the declared
                source closure.

        """
        exposed = tuple(
            destinations.get(item.path, item.path)
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
