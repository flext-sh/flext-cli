"""Policy checks for safely parsed OOXML members."""

from __future__ import annotations

from defusedxml import ElementTree as DefusedET
from defusedxml.common import DefusedXmlException

from flext_cli._constants.xlsx import FlextCliConstantsXlsx
from flext_cli._models.xlsx_archive import FlextCliModelsXlsxArchive
from flext_cli._protocols.xlsx_archive import FlextCliProtocolsXlsxArchive
from flext_cli._typings.xlsx import FlextCliTypesXlsx
from flext_core import p, r


class FlextCliUtilitiesXlsxArchiveChecks:
    """Pure checks over archive metadata and safely parsed XML nodes."""

    # NOTE (multi-agent, mro-j2yt.1): checks consume only policy models and
    # narrow protocols; proposal-specific member or tag rules stay in config.
    @staticmethod
    def _violation(
        kind: FlextCliTypesXlsx.XlsxArchiveViolationKind, location: str, detail: str
    ) -> FlextCliModelsXlsxArchive.XlsxArchiveViolation:
        return FlextCliModelsXlsxArchive.XlsxArchiveViolation(
            kind=kind, location=location, detail=detail
        )

    @staticmethod
    def _local_name(tag: str) -> str:
        """Return one namespace-independent XML tag name."""
        return tag.rpartition("}")[2]

    @classmethod
    def _xml_root(
        cls, archive: FlextCliProtocolsXlsxArchive.XlsxArchiveReader, member: str
    ) -> p.Result[FlextCliProtocolsXlsxArchive.XlsxXmlElement]:
        """Read and safely parse one XML archive member."""
        try:
            raw_root = DefusedET.fromstring(
                archive.read(member),
                forbid_dtd=True,
                forbid_entities=True,
                forbid_external=True,
            )
        except (DefusedET.ParseError, DefusedXmlException, KeyError, OSError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[FlextCliProtocolsXlsxArchive.XlsxXmlElement].fail(
                f"Invalid OOXML member {member}: {detail}"
            )
        # mro-j47u (codex): defusedxml's parsed Element implements the exact port.
        return r[FlextCliProtocolsXlsxArchive.XlsxXmlElement].ok(raw_root)

    @classmethod
    def _worksheet_violations(
        cls,
        root: FlextCliProtocolsXlsxArchive.XlsxXmlElement,
        member: str,
        policy: FlextCliModelsXlsxArchive.XlsxArchivePolicy,
    ) -> tuple[FlextCliModelsXlsxArchive.XlsxArchiveViolation, ...]:
        violations: tuple[FlextCliModelsXlsxArchive.XlsxArchiveViolation, ...] = ()
        for element in root.iter():
            tag = cls._local_name(element.tag)
            if tag in policy.forbidden_worksheet_tags:
                violations = (*violations, cls._violation("worksheet_tag", member, tag))
        return violations

    @classmethod
    def _workbook_violations(
        cls,
        root: FlextCliProtocolsXlsxArchive.XlsxXmlElement,
        member: str,
        policy: FlextCliModelsXlsxArchive.XlsxArchivePolicy,
    ) -> tuple[FlextCliModelsXlsxArchive.XlsxArchiveViolation, ...]:
        if not policy.reject_defined_names:
            return ()
        return tuple(
            cls._violation("defined_name", member, cls._local_name(element.tag))
            for element in root.iter()
            if cls._local_name(element.tag) == "definedName"
        )

    @classmethod
    def _style_violations(
        cls,
        root: FlextCliProtocolsXlsxArchive.XlsxXmlElement,
        member: str,
        policy: FlextCliModelsXlsxArchive.XlsxArchivePolicy,
    ) -> tuple[FlextCliModelsXlsxArchive.XlsxArchiveViolation, ...]:
        if not policy.reject_style_protection:
            return ()
        violations: tuple[FlextCliModelsXlsxArchive.XlsxArchiveViolation, ...] = ()
        for group in root.iter():
            if (
                cls._local_name(group.tag)
                not in FlextCliConstantsXlsx.XLSX_STYLE_GROUPS_WITH_PROTECTION
            ):
                continue
            for element in group.iter():
                if cls._local_name(element.tag) != "protection":
                    continue
                locked = element.get("locked")
                hidden = element.get("hidden")
                if (
                    locked not in policy.allowed_locked_tokens
                    or hidden not in policy.allowed_hidden_tokens
                ):
                    detail = f"locked={locked!r}, hidden={hidden!r}"
                    violations = (
                        *violations,
                        cls._violation("style_protection", member, detail),
                    )
        return violations


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxArchiveChecks",)
