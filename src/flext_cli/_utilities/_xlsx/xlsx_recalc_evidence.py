"""Raw cached-value evidence for recalculated XLSX workbooks.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from io import BytesIO
from typing import Literal
from zipfile import BadZipFile, LargeZipFile, ZipFile

from flext_core import r

from flext_cli import c, p
from flext_cli._utilities._xlsx import FlextCliUtilitiesXlsxArchiveChecks


class FlextCliUtilitiesXlsxRecalcEvidence(FlextCliUtilitiesXlsxArchiveChecks):
    """Read formula cache facts straight from safely parsed worksheet XML."""

    # NOTE (multi-agent, mro-j2yt.1): openpyxl cannot distinguish a missing
    # cached value from an empty-string result; the OOXML value element is the
    # only faithful evidence and stays behind this private adapter.
    @classmethod
    def _require_xml(
        cls,
        archive: p.Cli.XlsxArchiveReader,
        member: str,
    ) -> p.Cli.XlsxXmlElement:
        result = cls._xml_root(archive, member)
        if result.failure:
            msg = result.error or f"Invalid OOXML member: {member}"
            raise ValueError(msg)
        return result.value

    @classmethod
    def _worksheet_targets(
        cls,
        workbook_root: p.Cli.XlsxXmlElement,
        rels_root: p.Cli.XlsxXmlElement,
    ) -> tuple[tuple[str, str], ...]:
        """Resolve every declared sheet to its worksheet package member.

        Returns:
            The sheet names paired with their package members, in order.

        """
        relationships = cls._relationship_targets(rels_root)
        targets: list[tuple[str, str]] = []
        for sheet in workbook_root.iter():
            if cls._local_name(sheet.tag) != "sheet":
                continue
            name = sheet.get("name")
            rel_id = sheet.get(c.Cli.XLSX_RELATIONSHIPS_ID_ATTRIBUTE)
            target = relationships.get(rel_id) if rel_id is not None else None
            if name is not None and target is not None:
                targets.append((name, cls._package_member(target)))
        return tuple(targets)

    @classmethod
    def _relationship_targets(
        cls,
        rels_root: p.Cli.XlsxXmlElement,
    ) -> dict[str, str]:
        """Index relationship targets by identifier, keeping the first one.

        Returns:
            The first declared target of every relationship identifier.

        """
        relationships: dict[str, str] = {}
        for relationship in rels_root.iter():
            if cls._local_name(relationship.tag) != "Relationship":
                continue
            rel_id = relationship.get("Id")
            target = relationship.get("Target")
            if rel_id is not None and target is not None:
                relationships.setdefault(rel_id, target)
        return relationships

    @staticmethod
    def _package_member(target: str) -> str:
        """Return the package member name of one relationship target.

        Returns:
            The target rooted under the workbook package prefix.

        """
        member = target.lstrip("/")
        if member.startswith(c.Cli.XLSX_PACKAGE_PREFIX):
            return member
        return f"{c.Cli.XLSX_PACKAGE_PREFIX}{member}"

    @classmethod
    def _formula_cache_evidence(
        cls,
        source: bytes,
    ) -> p.Result[tuple[tuple[str, ...], tuple[str, ...]]]:
        """Classify formula cells as uncached or empty-string cached.

        Returns:
            The resulting ``p.Result[tuple[tuple[str, ...],
                tuple[str, ...]]]``.

        """
        try:
            evidence = cls._formula_cache_evidence_unchecked(source)
        except (BadZipFile, LargeZipFile, OSError, ValueError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[tuple[tuple[str, ...], tuple[str, ...]]].fail(
                f"{c.Cli.XlsxError.PARITY_FAILED}: {detail}",
            )
        return r[tuple[tuple[str, ...], tuple[str, ...]]].ok(evidence)

    @classmethod
    def _formula_cache_parts(
        cls,
        element: p.Cli.XlsxXmlElement,
    ) -> tuple[bool, p.Cli.XlsxXmlElement | None]:
        has_formula = False
        value_element: p.Cli.XlsxXmlElement | None = None
        for child in element.iter():
            local = cls._local_name(child.tag)
            if local == "f":
                has_formula = True
            elif local == "v" and value_element is None:
                value_element = child
        return has_formula, value_element

    @classmethod
    def _formula_cache_evidence_unchecked(
        cls,
        source: bytes,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        uncached: list[str] = []
        empty: list[str] = []
        with ZipFile(BytesIO(source)) as archive:
            workbook_root = cls._require_xml(archive, c.Cli.XLSX_WORKBOOK_MEMBER)
            rels_root = cls._require_xml(archive, c.Cli.XLSX_WORKBOOK_RELS_MEMBER)
            for sheet_name, member in cls._worksheet_targets(workbook_root, rels_root):
                root = cls._require_xml(archive, member)
                for element in root.iter():
                    state = cls._formula_cache_state(element, member)
                    if state is None:
                        continue
                    (uncached if state == "uncached" else empty).append(
                        f"{sheet_name}!{element.get('r')}"
                    )
        return tuple(uncached), tuple(empty)

    @classmethod
    def _formula_cache_state(
        cls,
        element: p.Cli.XlsxXmlElement,
        member: str,
    ) -> Literal["uncached", "empty"] | None:
        """Classify one worksheet element as an uncached or empty formula cell.

        Returns:
            ``uncached`` or ``empty`` for such a formula cell, otherwise ``None``.

        Raises:
            ValueError: If a formula cell has no coordinate.

        """
        if cls._local_name(element.tag) != "c":
            return None
        has_formula, value_element = cls._formula_cache_parts(element)
        if not has_formula:
            return None
        if element.get("r") is None:
            msg = f"Formula cell without coordinate in {member}"
            raise ValueError(msg)
        if value_element is None:
            return "uncached"
        return None if (value_element.text or "").strip() else "empty"


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxRecalcEvidence",)
