"""Generic model-driven DOCX renderer.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from docx import Document
from docx.document import Document as DocumentType
from flext_core import r

from flext_cli import c, m, p, t
from flext_cli._utilities import FlextCliUtilitiesFiles
from flext_cli._utilities._docx.formatting import FlextCliUtilitiesDocxFormatting
from flext_cli._utilities._files.native_results import (
    FlextCliUtilitiesFilesNativeResults,
)


class FlextCliUtilitiesDocxRenderer(FlextCliUtilitiesDocxFormatting):
    """Render one immutable document plan into DOCX bytes."""

    _ZIP_EPOCH_FLOOR_YEAR = 1980

    # NOTE (multi-agent, mro-j2yt.1): python-docx objects stay inside this
    # module; consumers exchange only validated plans and bytes.

    @classmethod
    def docx_render(
        cls,
        request: p.Cli.DocxRenderRequest,
    ) -> p.Result[p.Cli.DocxRenderResult]:
        """Render typed paragraphs, tables, and sections into document bytes.

        Returns:
            The resulting ``p.Result[p.Cli.DocxRenderResult]``.

        """
        document_result = cls._document_for_request(request)
        if document_result.failure:
            return r[p.Cli.DocxRenderResult].from_failure(document_result)
        document = document_result.value
        try:
            cls._apply_document(document, request.plan)
            cls._apply_source_date(document, request.source_date_epoch)
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            detail = str(exc).strip() or exc.__class__.__name__
            return r[p.Cli.DocxRenderResult].fail(
                f"{c.Cli.DocxError.RENDER_FAILED}: {detail}",
            )
        content = cls._serialize_document(
            document,
            source_date_epoch=request.source_date_epoch,
        )
        if content.failure:
            return r[p.Cli.DocxRenderResult].from_failure(content)
        return r[p.Cli.DocxRenderResult].ok(
            m.Cli.DocxRenderResult(
                content=content.value,
                plan=m.Cli.DocxDocumentPlan.model_validate(
                    request.plan, from_attributes=True
                ),
            ),
        )

    @classmethod
    def _document_for_request(
        cls,
        request: p.Cli.DocxRenderRequest,
    ) -> p.Result[DocumentType]:
        if request.template is None:
            return r[DocumentType].ok(Document())
        return FlextCliUtilitiesFilesNativeResults.coded_result(
            Document,
            c.Cli.DocxError.DOCUMENT_LOAD_FAILED,
            (OSError, ValueError, KeyError),
        )(BytesIO(request.template))

    @classmethod
    def _apply_source_date(
        cls,
        document: DocumentType,
        source_date_epoch: int | None,
    ) -> None:
        if source_date_epoch is None:
            return
        moment = datetime.fromtimestamp(source_date_epoch, tz=UTC)
        core_props = document.core_properties
        core_props.created = moment
        core_props.modified = moment

    @classmethod
    def _serialize_document(
        cls,
        document: DocumentType,
        *,
        source_date_epoch: int | None = None,
    ) -> p.Result[bytes]:
        serialized = FlextCliUtilitiesFiles.files_save_bytes(
            document.save, str(c.Cli.DocxError.SERIALIZE_FAILED)
        )
        if serialized.failure or source_date_epoch is None:
            return serialized
        return cls._normalize_archive(serialized.value, source_date_epoch)

    @classmethod
    def _normalize_archive(
        cls,
        content: bytes,
        source_date_epoch: int,
    ) -> p.Result[bytes]:
        member_date = cls._stable_member_date(source_date_epoch)
        return FlextCliUtilitiesFiles.files_save_bytes(
            lambda target: cls._rewrite_members(content, target, member_date),
            str(c.Cli.DocxError.SERIALIZE_FAILED),
            catch=(OSError, ValueError),
        )

    @staticmethod
    def _stable_member_date(
        source_date_epoch: int,
    ) -> tuple[int, int, int, int, int, int]:
        moment = datetime.fromtimestamp(source_date_epoch, tz=UTC)
        zip_floor = datetime(
            FlextCliUtilitiesDocxRenderer._ZIP_EPOCH_FLOOR_YEAR, 1, 1, tzinfo=UTC
        )
        stamped = max(moment, zip_floor)
        return (
            stamped.year,
            stamped.month,
            stamped.day,
            stamped.hour,
            stamped.minute,
            stamped.second,
        )

    @staticmethod
    def _rewrite_members(
        content: bytes,
        target: BytesIO,
        member_date: tuple[int, int, int, int, int, int],
    ) -> None:
        with (
            ZipFile(BytesIO(content)) as source,
            ZipFile(target, "w", ZIP_DEFLATED) as normalized,
        ):
            for info in source.infolist():
                stable = ZipInfo(filename=info.filename, date_time=member_date)
                stable.compress_type = info.compress_type
                stable.external_attr = info.external_attr
                stable.internal_attr = info.internal_attr
                stable.create_system = info.create_system
                normalized.writestr(stable, source.read(info.filename))

    @classmethod
    def _apply_document(
        cls,
        document: DocumentType,
        plan: p.Cli.DocxDocumentPlan,
    ) -> None:
        cls._apply_core_properties(document, plan.core_properties)
        for paragraph in plan.paragraphs:
            cls._apply_paragraph(document, paragraph)
        for table in plan.tables:
            cls._apply_table(document, table)
        cls._apply_sections(document, plan.sections)

    @classmethod
    def _apply_core_properties(
        cls,
        document: DocumentType,
        properties: t.JsonMapping,
    ) -> None:
        core_props = document.core_properties
        for key, value in properties.items():
            if hasattr(core_props, key):
                setattr(core_props, key, value)


__all__: tuple[str, ...] = ("FlextCliUtilitiesDocxRenderer",)
