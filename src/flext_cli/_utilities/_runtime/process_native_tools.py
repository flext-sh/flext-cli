"""Native tool qualification and static ELF checks for process isolation.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import hashlib
import struct
from typing import ClassVar, Literal

from flext_core import u

from flext_cli import m, p, t
from flext_cli._config import config
from flext_cli._utilities import FlextCliUtilitiesAtomicFileSnapshot
from flext_cli._utilities._runtime import FlextCliUtilitiesRuntimeProcessOutcome


class FlextCliUtilitiesRuntimeProcessNativeTools(
    FlextCliUtilitiesRuntimeProcessOutcome,
):
    """Bind declared native tools to their original bootstrap evidence."""

    _ELF_HEADER_BYTES: ClassVar[int] = 64
    _ELFCLASS64: ClassVar[int] = 2
    _PT_INTERP: ClassVar[int] = 3
    _PT_DYNAMIC: ClassVar[int] = 2

    @classmethod
    def _qualify_native_tool(
        cls,
        isolation: p.Cli.ProcessReadOnlyIsolation,
        role: Literal["isolation-launcher", "policy-compiler"],
    ) -> None:
        """Bind one declared native tool to an actual current bootstrap evidence row."""
        qualification, declaration = (
            (isolation.launcher, isolation.launcher_declaration)
            if role == "isolation-launcher"
            else (isolation.policy_compiler, isolation.compiler_declaration)
        )
        cls._ensure_native_tool_evidence(
            qualification, role, isolation.policy_compiler.artifact_receipt
        )
        cls._ensure_native_tool_denials(qualification, isolation.architecture)
        cls._ensure_native_tool_declaration(qualification, declaration)
        cls._ensure_native_tool_artifact(qualification)

    @classmethod
    def _ensure_native_tool_evidence(
        cls,
        qualification: p.Cli.ProcessNativeToolQualification,
        role: Literal["isolation-launcher", "policy-compiler"],
        compiler_receipt: p.Cli.AtomicFileReceipt,
    ) -> None:
        """Require one original bootstrap qualification row for the tool.

        Raises:
            ValueError: If the issuer receipt has no bytes, the bootstrap
                report cannot be parsed, or the tool lacks exactly one
                matching qualification row, role, or policy compiler.

        """
        if qualification.issuer_receipt.content is None:
            msg = "native policy compiler has no original bootstrap issuer bytes"
            raise ValueError(msg)
        report = m.Cli.ProcessNativeQualificationReport[
            t.JsonValue, t.JsonValue, t.JsonValue
        ].model_validate_json(qualification.issuer_receipt.content)
        evidence = u.dump(
            qualification,
            options=m.ModelDumpOptions(exclude={"issuer_receipt", "artifact"}),
        )
        matches = tuple(
            item
            for receipt in report.receipts
            for item in receipt.native_tool_qualifications
            if u.dump(item) == evidence
        )
        if len(matches) != 1:
            msg = (
                "native policy compiler lacks one original bootstrap qualification row"
            )
            raise ValueError(msg)
        if qualification.role != role:
            msg = "native tool qualification names a different execution capability"
            raise ValueError(msg)
        if qualification.probe_compiler_receipt != compiler_receipt:
            msg = "native tool denial probes used a different policy compiler"
            raise ValueError(msg)

    @classmethod
    def _ensure_native_tool_denials(
        cls, qualification: p.Cli.ProcessNativeToolQualification, architecture: str
    ) -> None:
        """Require complete denial qualification for the declared ABI.

        Raises:
            ValueError: If the build, ABI, or denial probes failed, the
                canonical policy digest differs, the observed denials are
                incomplete, or the qualification ABI differs.

        """
        if not all(
            cls.process_succeeded(outcome)
            for outcome in (
                qualification.native_build_outcome,
                qualification.native_abi_probe_outcome,
                qualification.native_policy_probe_outcome,
            )
        ):
            msg = "native policy compiler build, ABI or denial qualification failed"
            raise ValueError(msg)
        if cls.native_process_policy_identity() != qualification.policy_sha256:
            msg = (
                "native denial qualification differs from the canonical process policy"
            )
            raise ValueError(msg)
        observed = tuple(probe.syscall for probe in qualification.native_policy_probes)
        if (
            len(observed) != len(set(observed))
            or set(observed) != set(config.ProcessIsolation.denied_syscalls)
            or any(
                probe.observed_errno != errno.EACCES
                for probe in qualification.native_policy_probes
            )
        ):
            msg = (
                "native policy qualification lacks "
                "complete original denial observations"
            )
            raise ValueError(msg)
        if qualification.architecture != architecture:
            msg = "native policy compiler qualification has a different ABI"
            raise ValueError(msg)

    @classmethod
    def _ensure_native_tool_declaration(
        cls,
        qualification: p.Cli.ProcessNativeToolQualification,
        declaration: p.Cli.AtomicFileState,
    ) -> None:
        """Require the elected declaration and unchanged qualification inputs.

        Raises:
            ValueError: If the declaration differs from the independently
                elected declaration or one qualification input changed.

        """
        declared = FlextCliUtilitiesAtomicFileSnapshot.read_receipt(
            declaration.path, required=True
        )
        if declared not in qualification.declaration_inputs:
            msg = (
                "native policy compiler differs from the "
                "independently elected declaration"
            )
            raise ValueError(msg)
        for receipt in (
            qualification.artifact_receipt,
            qualification.abi_reference,
            qualification.probe_compiler_receipt,
            *qualification.declaration_inputs,
            *qualification.installation_inputs,
            *qualification.source_inputs,
        ):
            current = FlextCliUtilitiesAtomicFileSnapshot.read_receipt(
                receipt.path, required=True
            )
            if current != receipt:
                msg = (
                    "native policy compiler qualification "
                    f"input changed: {receipt.path}"
                )
                raise ValueError(msg)

    @classmethod
    def _ensure_native_tool_artifact(
        cls, qualification: p.Cli.ProcessNativeToolQualification
    ) -> None:
        """Require artifact bytes matching the receipt and declared ABI.

        Raises:
            ValueError: If the artifact bytes differ from the installed
                receipt, the interpreter ABI is missing, or the artifact
                ELF ABI differs from the declared interpreter.

        """
        artifact = qualification.artifact
        if (
            artifact.path != qualification.artifact_receipt.path
            or artifact.content is None
            or hashlib.sha256(artifact.content).hexdigest()
            != qualification.artifact_receipt.sha256
        ):
            msg = (
                "native policy compiler bytes differ "
                "from the installed artifact receipt"
            )
            raise ValueError(msg)
        reference = qualification.abi_reference
        if reference.size is None:
            msg = "native policy compiler has no captured interpreter ABI"
            raise ValueError(msg)
        with FlextCliUtilitiesAtomicFileSnapshot.receipt_reader(reference) as reader:
            reference_bytes = reader.read_range(0, reference.size)
        if cls.native_binary_identity(
            artifact.content, require_static=True
        ) != cls.native_binary_identity(reference_bytes, require_static=False):
            msg = "native policy compiler ELF ABI differs from the declared interpreter"
            raise ValueError(msg)

    @staticmethod
    def native_process_policy_arguments() -> tuple[str, ...]:
        """Return the source-owned symbolic native denial obligations."""
        return config.ProcessIsolation.denied_syscalls

    @staticmethod
    def native_process_policy_identity() -> str:
        """Fingerprint the exact NUL-terminated native policy argument vector.

        Returns:
            The SHA-256 digest of the NUL-terminated policy argument
            vector.

        """
        mixin = FlextCliUtilitiesRuntimeProcessNativeTools
        arguments = mixin.native_process_policy_arguments()
        content = b"\0".join(name.encode("ascii") for name in arguments) + b"\0"
        return hashlib.sha256(content).hexdigest()

    @classmethod
    def native_binary_identity(
        cls, content: bytes, *, require_static: bool
    ) -> tuple[int, int, int]:
        """Read the immutable ELF ABI and reject dynamic native compiler loading.

        Returns:
            The ELF class, data encoding, and machine identifiers read from
            the immutable header bytes.

        """
        elf_class, encoding, machine = cls._native_elf_header_identity(content)
        if not require_static:
            return elf_class, encoding, machine
        cls._reject_native_elf_interpreters(
            m.Cli.NativeElfLayout(
                order="<" if encoding == 1 else ">",
                wide=elf_class == cls._ELFCLASS64,
            ),
            content,
        )
        return elf_class, encoding, machine

    @classmethod
    def _native_elf_header_identity(cls, content: bytes) -> tuple[int, int, int]:
        """Read and validate the immutable ELF header identity bytes.

        Returns:
            The ELF class, data encoding, and machine identifiers read from
            the immutable header bytes.

        Raises:
            ValueError: If the ELF header is absent or unsupported.

        """
        if len(content) < cls._ELF_HEADER_BYTES or content[:4] != b"\x7fELF":
            msg = "native policy compiler/reference has no complete ELF header"
            raise ValueError(msg)
        elf_class, encoding = content[4], content[5]
        if elf_class not in {1, 2} or encoding not in {1, 2} or content[6] != 1:
            msg = "native policy compiler/reference ELF ABI is unsupported"
            raise ValueError(msg)
        order = "<" if encoding == 1 else ">"
        machine = int(struct.unpack_from(f"{order}H", content, 18)[0])
        return elf_class, encoding, machine

    @classmethod
    def _reject_native_elf_interpreters(
        cls, layout: m.Cli.NativeElfLayout, content: bytes
    ) -> None:
        """Reject a required-static binary with ambient native interpreters.

        Raises:
            ValueError: If the ELF program table is incomplete or the
                binary carries an ambient interpreter.

        """
        order, wide = layout.order, layout.wide
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
            if kind == cls._PT_INTERP:  # Immutable System V ELF protocol.
                msg = "native policy compiler has an ambient ELF interpreter"
                raise ValueError(msg)
            if kind != cls._PT_DYNAMIC:  # Only dynamic tables carry dependencies.
                continue
            cls._reject_native_elf_needed(layout, content, offset)

    @classmethod
    def _reject_native_elf_needed(
        cls, layout: m.Cli.NativeElfLayout, content: bytes, offset: int
    ) -> None:
        """Reject one dynamic table with ambient shared-library dependencies.

        Raises:
            ValueError: If the dynamic table is incomplete or carries an
                ambient shared-library dependency.

        """
        order, wide = layout.order, layout.wide
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
                struct.unpack_from(f"{order}{'q' if wide else 'i'}", content, position)[
                    0
                ]
            )
            if tag == 1:  # DT_NEEDED.
                msg = "native policy compiler has ambient shared-library dependencies"
                raise ValueError(msg)
            if tag == 0:  # DT_NULL.
                break


__all__: list[str] = ["FlextCliUtilitiesRuntimeProcessNativeTools"]
