"""Public pre-execution failures for explicitly selected native isolation.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

import pytest

from flext_cli import config
from tests import m, tm, u


class TestsFlextCliRuntimeProcessIsolation:
    """Isolation prerequisites fail before any command can execute."""

    @staticmethod
    def _request(tmp_path: Path) -> m.Cli.ProcessReadOnlyIsolation:
        """Capture real local files for negative pre-execution contracts.

        Returns:
            Requested file states with no matching native bootstrap evidence.

        """
        source = tmp_path / "source.py"
        source.write_text('"""Captured source."""\n', encoding="utf-8")
        issuer = tmp_path / "unqualified-bootstrap.json"
        issuer.write_text(
            m.Cli.ProcessNativeQualificationReport(receipts=()).model_dump_json(),
            encoding="utf-8",
        )
        interpreter = Path(sys.executable).resolve()
        artifact = tm.ok(
            u.Cli.atomic_read_binary_file_state(interpreter, required=True)
        )
        artifact_receipt = tm.ok(
            u.Cli.atomic_read_binary_file_receipt(interpreter, required=True)
        )
        source_state = tm.ok(u.Cli.atomic_read_binary_file_state(source, required=True))
        source_receipt = tm.ok(
            u.Cli.atomic_read_binary_file_receipt(source, required=True)
        )
        # A real interpreter outcome cannot attest a policy compiler: the
        # original bootstrap report has no corresponding native tool row.
        outcome = tm.ok(u.Cli.run_bytes((sys.executable, "--version"))).outcome
        compiler = m.Cli.ProcessNativeToolQualification(
            role="policy-compiler",
            issuer_receipt=tm.ok(
                u.Cli.atomic_read_binary_file_state(issuer, required=True)
            ),
            artifact=artifact,
            artifact_receipt=artifact_receipt,
            declaration_inputs=(source_receipt,),
            installation_inputs=(source_receipt,),
            source_inputs=(source_receipt,),
            native_build_outcome=outcome,
            native_abi_probe_outcome=outcome,
            native_policy_probe_outcome=outcome,
            native_policy_probes=(),
            probe_compiler_receipt=artifact_receipt,
            policy_sha256=u.Cli.native_process_policy_identity(),
            abi_reference=artifact_receipt,
            architecture=platform.machine(),
        )
        return m.Cli.ProcessReadOnlyIsolation(
            platform="linux",
            architecture=platform.machine(),
            launcher=compiler,
            launcher_declaration=source_state,
            policy_compiler=compiler,
            compiler_declaration=source_state,
            sources=(source_state,),
            runtime_trees=(),
            runtime_files=(),
            environment=(),
        )

    @staticmethod
    def test_unsupported_native_identity_fails_before_command(
        tmp_path: Path,
    ) -> None:
        """A different filter ABI never starts the supplied command."""
        isolation = TestsFlextCliRuntimeProcessIsolation._request(tmp_path)
        isolation = isolation.model_copy(
            update={
                "architecture": f"{isolation.architecture}-different",
            }
        )
        result = u.Cli.run_raw(
            [sys.executable, "-c", "raise SystemExit(71)"],
            cwd=tmp_path,
            options=m.Cli.ProcessOptions(isolation=isolation),
        )

        tm.fail(result)
        tm.that(result.error or "", has="no qualified native platform capability")
        tm.that(isinstance(result.exception, ValueError), eq=True)

    @staticmethod
    def test_isolation_refuses_inherited_caller_descriptors(
        tmp_path: Path,
    ) -> None:
        """A caller capability cannot be carried into the isolated import."""
        isolation = TestsFlextCliRuntimeProcessIsolation._request(tmp_path)
        result = u.Cli.run_bytes(
            [sys.executable, "-c", "raise SystemExit(71)"],
            cwd=tmp_path,
            options=m.Cli.ProcessOptions(isolation=isolation, pass_fds=(1,)),
        )

        tm.fail(result)
        expected = (
            "cannot inherit caller file descriptors"
            if sys.platform == "linux"
            else "no qualified native platform capability"
        )
        tm.that(result.error or "", has=expected)

    @staticmethod
    def test_unqualified_compiler_does_not_create_durable_output(
        tmp_path: Path,
    ) -> None:
        """File identity cannot replace the original bootstrap qualification."""
        isolation = TestsFlextCliRuntimeProcessIsolation._request(tmp_path)
        output = tmp_path / "output" / "raw.log"
        result = u.Cli.run_to_file(
            [sys.executable, "-c", "raise SystemExit(71)"],
            output,
            cwd=tmp_path,
            options=m.Cli.ProcessOptions(isolation=isolation),
        )

        tm.fail(result)
        expected = (
            "one original bootstrap qualification row"
            if sys.platform == "linux"
            else "no qualified native platform capability"
        )
        tm.that(result.error or "", has=expected)
        tm.that(output.parent.exists(), eq=False)

    @staticmethod
    def test_network_policy_cannot_remove_a_required_syscall() -> None:
        """Native reference imports cannot weaken the external syscall contract."""
        policy = config.ProcessIsolation.denied_syscalls

        with pytest.raises(ValueError, match="denied_syscalls"):
            m.Cli.ProcessIsolation.model_validate({
                "compiler_resource_parts": config.ProcessIsolation.compiler_resource_parts,
                "denied_syscalls": policy[1:],
            })

    @staticmethod
    def test_resource_declaration_refuses_parent_escape() -> None:
        """The source locator must remain inside the selected installed package."""
        with pytest.raises(ValueError, match="compiler_resource_parts"):
            m.Cli.ProcessIsolation.model_validate({
                "compiler_resource_parts": ("..",),
                "denied_syscalls": config.ProcessIsolation.denied_syscalls,
            })

    @staticmethod
    def test_raw_filter_is_not_a_qualification_input(tmp_path: Path) -> None:
        """An arbitrary allow-all BPF field has no admission route."""
        isolation = TestsFlextCliRuntimeProcessIsolation._request(tmp_path)
        payload = isolation.model_dump()
        payload["seccomp_filter"] = isolation.sources[0]

        with pytest.raises(ValueError, match="seccomp_filter"):
            m.Cli.ProcessReadOnlyIsolation.model_validate(payload)
