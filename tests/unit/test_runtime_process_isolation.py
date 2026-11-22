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
from tests import c, m, p, tm, u

pytestmark = [c.Tests.MARK.slow]


class TestsFlextCliRuntimeProcessIsolation:
    """Isolation prerequisites fail before any command can execute."""

    @staticmethod
    def _request(
        tmp_path: Path,
        *,
        fixture_output: Path | None = None,
        persistent_directory: Path | None = None,
    ) -> p.Cli.ProcessReadOnlyIsolation:
        """Capture real local files for negative pre-execution contracts.

        Returns:
            Requested file states with no matching native bootstrap evidence.

        """
        source = tmp_path / "source.py"
        source.write_text('"""Captured source."""\n', encoding="utf-8")
        issuer = tmp_path / "unqualified-bootstrap.json"
        issuer.write_text(
            m.Cli.ProcessNativeQualificationReport(
                root=tmp_path,
                operation="bootstrap",
                scope=(tmp_path,),
                receipts=(),
            ).model_dump_json(),
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
        compiler = m.Cli.ProcessNativeToolQualification.model_validate({
            "role": "policy-compiler",
            "issuer_receipt": tm.ok(
                u.Cli.atomic_read_binary_file_state(issuer, required=True)
            ),
            "artifact": artifact,
            "artifact_receipt": artifact_receipt,
            "declaration_inputs": (source_receipt,),
            "installation_inputs": (source_receipt,),
            "source_inputs": (source_receipt,),
            "native_build_outcome": outcome,
            "native_abi_probe_outcome": outcome,
            "native_policy_probe_outcome": outcome,
            "native_policy_probes": (),
            "probe_compiler_receipt": artifact_receipt,
            "policy_sha256": u.Cli.native_process_policy_identity(),
            "abi_reference": artifact_receipt,
            "architecture": platform.machine(),
        })
        declaration: dict[str, object] = {
            "platform": "linux",
            "architecture": platform.machine(),
            "launcher": compiler,
            "launcher_declaration": source_state,
            "policy_compiler": compiler,
            "compiler_declaration": source_state,
            "sources": (source_state,),
            "runtime_trees": (),
            "runtime_files": (artifact,),
            "environment": (),
        }
        if fixture_output is None:
            return m.Cli.ProcessReadOnlyIsolation.model_validate(declaration)
        return m.Cli.ProcessFixtureIsolation.model_validate({
            **declaration,
            "output_directory": tm.ok(
                u.Cli.atomic_inventory_physical_tree(fixture_output)
            ),
            "persistent_directory": (
                tm.ok(u.Cli.atomic_inventory_physical_tree(persistent_directory))
                if persistent_directory is not None
                else None
            ),
        })

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
        tm.ok(isinstance(result.exception, ValueError))

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
    def test_native_evidence_round_trips_original_process_outcomes(
        tmp_path: Path,
    ) -> None:
        """Persist real native outcomes through the canonical bootstrap wire model."""
        qualification = TestsFlextCliRuntimeProcessIsolation._request(
            tmp_path
        ).policy_compiler
        restored = m.Cli.ProcessNativeToolEvidence.model_validate_json(
            qualification.model_dump_json(exclude={"issuer_receipt", "artifact"})
        )

        tm.that(
            restored.model_dump(),
            eq=qualification.model_dump(exclude={"issuer_receipt", "artifact"}),
        )
        for before, after in (
            (qualification.native_build_outcome, restored.native_build_outcome),
            (qualification.native_abi_probe_outcome, restored.native_abi_probe_outcome),
            (
                qualification.native_policy_probe_outcome,
                restored.native_policy_probe_outcome,
            ),
        ):
            tm.that(after.raw_return_code, eq=before.raw_return_code)
            tm.that(after.timed_out, eq=before.timed_out)
            tm.that(after.forwarded_signal, eq=before.forwarded_signal)

    @staticmethod
    def test_unqualified_compiler_does_not_create_durable_output(
        tmp_path: Path,
    ) -> None:
        """File identity cannot replace the original bootstrap qualification."""
        isolation = TestsFlextCliRuntimeProcessIsolation._request(tmp_path)
        output = tmp_path / "output" / "raw.log"
        result = u.Cli.run_to_file(
            [
                str(isolation.policy_compiler.abi_reference.path),
                "-c",
                "raise SystemExit(71)",
            ],
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
        tm.fail(output.parent.exists())

    @staticmethod
    @pytest.mark.parametrize("overlaps_source", [False, True])
    def test_fixture_output_rejects_host_inputs(
        tmp_path: Path, *, overlaps_source: bool
    ) -> None:
        """A write capability excludes source paths and preexisting files."""
        output = tmp_path if overlaps_source else tmp_path / "output"
        output.mkdir(exist_ok=True)
        existing = output / "original.txt"
        existing.write_text("original", encoding="utf-8")
        isolation = TestsFlextCliRuntimeProcessIsolation._request(
            tmp_path, fixture_output=output
        )
        result = u.Cli.run_raw(
            (
                str(isolation.policy_compiler.abi_reference.path),
                "-c",
                "raise SystemExit(71)",
            ),
            cwd=tmp_path,
            options=m.Cli.ProcessOptions(isolation=isolation),
        )

        tm.fail(result)
        expected = "no qualified native platform capability"
        if sys.platform == "linux":
            expected = (
                "output overlaps an input or private mount"
                if overlaps_source
                else "output must be empty and owned by the caller"
            )
        tm.that(result.error or "", has=expected)
        tm.that(existing.read_text(encoding="utf-8"), eq="original")

    @staticmethod
    @pytest.mark.parametrize(
        ("layout", "expected"),
        [
            ("regular", "one original bootstrap qualification row"),
            ("overlap", "output overlaps an input or private mount"),
            ("symlink", "persistent fixture data requires owned regular files"),
            ("outside", "persistent fixture data must be below the working directory"),
        ],
    )
    def test_fixture_accepts_only_separate_owned_persistent_data(
        tmp_path: Path, layout: str, expected: str
    ) -> None:
        """Admit preexisting data from a dedicated directory inside the checkout."""
        working = tmp_path / "workspace"
        working.mkdir()
        output = working / "output"
        output.mkdir(mode=0o700)
        database = (tmp_path if layout == "outside" else working) / "test-data"
        database.mkdir(mode=0o700)
        data = database / "state.sqlite"
        data.write_bytes(b"owned data")
        data.chmod(0o600)
        if layout == "symlink":
            (database / "alias").symlink_to(data)
        persistent = output if layout == "overlap" else database
        isolation = TestsFlextCliRuntimeProcessIsolation._request(
            working, fixture_output=output, persistent_directory=persistent
        )
        result = u.Cli.run_raw(
            (str(isolation.policy_compiler.abi_reference.path), "--version"),
            cwd=working,
            options=m.Cli.ProcessOptions(isolation=isolation),
        )

        tm.fail(result)
        tm.that(
            result.error or "",
            has=(
                expected
                if sys.platform == "linux"
                else "no qualified native platform capability"
            ),
        )
        tm.that(data.read_bytes(), eq=b"owned data")

    @staticmethod
    @pytest.mark.parametrize(
        "layout", ["clean", "extra", "symlink", "traversal", "runtime-overlap"]
    )
    def test_private_checkout_admits_only_declared_physical_state(
        tmp_path: Path, layout: str
    ) -> None:
        """Preserve source and backing identity before qualifying the child."""
        original = tmp_path / "original"
        working = tmp_path / "private"
        output = tmp_path / "output"
        for directory in (original, working, output):
            directory.mkdir(mode=0o700)
        isolation = TestsFlextCliRuntimeProcessIsolation._request(
            original, fixture_output=output
        )
        database = working / ".testmondata"
        source = original / "source.py"
        if layout == "symlink":
            database.symlink_to(source)
        else:
            database.write_bytes(b"durable")
        if layout == "extra":
            (working / "unowned").touch()
        checkout = m.Cli.ProcessFixtureCheckout.model_validate({
            "backing": tm.ok(u.Cli.atomic_inventory_physical_tree(working)),
            "source_root": original / ".." / original.name
            if layout == "traversal"
            else original,
            "persistent_filenames": (database.name,),
        })
        if layout == "runtime-overlap":
            runtime = tm.ok(u.Cli.atomic_inventory_physical_tree(original))
            isolation = isolation.model_copy(update={"runtime_trees": (runtime,)})
        result = u.Cli.run_raw(
            (str(isolation.policy_compiler.abi_reference.path), "--version"),
            cwd=working,
            options=m.Cli.ProcessOptions(
                isolation=isolation.model_copy(update={"private_checkout": checkout})
            ),
        )

        tm.fail(result)
        expected = {
            "clean": "one original bootstrap qualification row",
            "extra": "private checkout backing contains ineligible entry",
            "symlink": "private checkout backing contains ineligible entry",
            "traversal": "private checkout requires disjoint canonical cwd",
            "runtime-overlap": "private checkout source root overlaps a runtime mount",
        }
        tm.that(
            result.error or "",
            has=(
                expected[layout]
                if sys.platform == "linux"
                else "no qualified native platform capability"
            ),
        )
        tm.that(source.read_text(encoding="utf-8"), eq='"""Captured source."""\n')

    @staticmethod
    def test_network_policy_cannot_remove_a_required_syscall() -> None:
        """Native reference imports cannot weaken the external syscall contract."""
        policy = config.ProcessIsolation.denied_syscalls

        with u.Tests.raises(ValueError, match="denied_syscalls"):
            m.Cli.ProcessIsolation.model_validate({
                "compiler_resource_parts": (
                    config.ProcessIsolation.compiler_resource_parts
                ),
                "denied_syscalls": policy[1:],
            })

    @staticmethod
    @pytest.mark.parametrize("field", ["compiler_resource_parts", "denied_syscalls"])
    @pytest.mark.parametrize("missing", [False, True])
    def test_native_policy_requires_nonempty_declared_yaml_fields(
        field: str,
        *,
        missing: bool,
    ) -> None:
        """Missing YAML policy cannot construct an empty successful namespace."""
        payload = config.ProcessIsolation.model_dump()
        if missing:
            del payload[field]
        else:
            payload[field] = ()

        with u.Tests.raises(ValueError, match=field):
            m.Cli.ProcessIsolation.model_validate(payload)

    @staticmethod
    def test_native_policy_reads_the_config_singleton_in_any_import_order(
        tmp_path: Path,
    ) -> None:
        """The denial policy reads the singleton even when the submodule loads first.

        Importing ``flext_cli.config`` as a module rebinds the package attribute
        of the same name, so a later ``from flext_cli import config`` would bind
        the module and ``config.ProcessIsolation`` would not exist.
        """
        script = (
            "import importlib\n"
            "importlib.import_module('flext_cli.config')\n"
            "from flext_cli import u\n"
            "policy = u.Cli.native_process_policy_arguments()\n"
            "raise SystemExit(0 if policy else 1)\n"
        )

        result = u.Cli.run_raw((sys.executable, "-c", script), cwd=tmp_path)

        tm.ok(result)
        tm.that(
            u.Cli.process_succeeded(result.value.outcome),
            eq=True,
            msg=result.value.stderr,
        )

    @staticmethod
    def test_resource_declaration_refuses_parent_escape() -> None:
        """The source locator must remain inside the selected installed package."""
        with u.Tests.raises(ValueError, match="compiler_resource_parts"):
            m.Cli.ProcessIsolation.model_validate({
                "compiler_resource_parts": ("..",),
                "denied_syscalls": config.ProcessIsolation.denied_syscalls,
            })

    @staticmethod
    def test_raw_filter_is_not_a_qualification_input(tmp_path: Path) -> None:
        """An arbitrary allow-all BPF field has no admission route."""
        isolation = TestsFlextCliRuntimeProcessIsolation._request(tmp_path)
        payload: dict[str, object] = dict(isolation.model_dump())
        payload["seccomp_filter"] = isolation.sources[0]

        with u.Tests.raises(ValueError, match="seccomp_filter"):
            m.Cli.ProcessReadOnlyIsolation.model_validate(payload)
