
"""
Structured Versioned JSON IPC Protocol Interface & CLI Entrypoint.
Protocol Version: 1.0.0

Supports:
- Excel analysis
- Word template analysis
- Digital PDF template analysis
- Intelligent field mapping
- Conversion preview
- Excel -> Word DOCX
- Word DOCX -> PDF
- Excel -> Digital PDF template -> PDF
- Conversion history
- Download generated files (PDF/DOCX)
- CLI and FastAPI IPC server
"""

import argparse
import json
import os
import sys
import uuid
import tempfile

from typing import Any, Dict

from .excel import ExcelAnalyzer
from .generator import WordGenerator
from .mapping import FeedbackStore, IntelligentMappingEngine
from .models.field import FieldModel
from .models.mapping import FieldMapping
from .models.protocol import IPCRequest, IPCResponse, PROTOCOL_VERSION
from .models.schema import SourceSchema, TargetSchema
from .transform import DataTransformer
from .validator import OutputValidator
from .word import WordAnalyzer
from .pdf_converter import PDFConverter
from .pdf_template import PDFTemplateAnalyzer
from .pdf_template import PDFTemplateMapper
from .pdf_template import PDFTemplateGenerator


class EngineController:

    def __init__(self, db_path: str = None):

        if db_path is None:
            data_dir = os.environ.get("SMART_CONVERTER_DATA_DIR")

            if data_dir:
                os.makedirs(data_dir, exist_ok=True)
                db_path = os.path.join(
                    data_dir,
                    "conversion_history.db"
                )
            else:
                db_path = "conversion_history.db"

        else:
            db_parent = os.path.dirname(os.path.abspath(db_path))
            os.makedirs(db_parent, exist_ok=True)

        self.feedback_store = FeedbackStore(
            db_path=db_path
        )

        self.mapping_engine = IntelligentMappingEngine(
            feedback_store=self.feedback_store
        )

        self.mapping_engine = IntelligentMappingEngine(
            feedback_store=self.feedback_store
        )

    # =========================================================
    # MAIN IPC HANDLER
    # =========================================================

    def handle_request(
        self,
        request_data: Dict[str, Any],
    ) -> Dict[str, Any]:

        req_id = request_data.get(
            "request_id",
            str(uuid.uuid4()),
        )

        cmd = request_data.get("command", "")

        payload = request_data.get("payload", {})

        try:

            # =================================================
            # INSPECT EXCEL
            # =================================================

            if cmd == "inspect_excel":

                file_path = payload.get("file_path")

                analyzer = ExcelAnalyzer(file_path)

                sheets = analyzer.inspect_sheets()

                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={
                        "sheets": [
                            sheet.model_dump()
                            for sheet in sheets
                        ]
                    },
                ).model_dump()

            # =================================================
            # ANALYZE EXCEL
            # =================================================

            elif cmd == "analyze_excel":

                file_path = payload.get("file_path")

                sheet_name = payload.get("sheet_name")

                header_override = payload.get(
                    "header_row_override"
                )

                analyzer = ExcelAnalyzer(file_path)

                schema = analyzer.analyze_sheet(
                    sheet_name=sheet_name,
                    header_row_override=header_override,
                )

                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={
                        "source_schema": schema.model_dump()
                    },
                ).model_dump()

            # =================================================
            # ANALYZE WORD TEMPLATE
            # =================================================

            elif cmd == "analyze_word":

                file_path = payload.get("file_path")

                analyzer = WordAnalyzer(file_path)

                schema = analyzer.analyze()

                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={
                        "target_schema": schema.model_dump()
                    },
                ).model_dump()

            # =================================================
            # ANALYZE DIGITAL PDF TEMPLATE
            # =================================================

            elif cmd == "analyze_pdf_template":

                file_path = payload.get("file_path")

                analyzer = PDFTemplateAnalyzer()

                schema = analyzer.analyze(file_path)

                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={
                        "target_schema": schema.model_dump(),
                        "template_type": "pdf",
                    },
                ).model_dump()

            # =================================================
            # GENERATE INTELLIGENT MAPPINGS
            # =================================================

            elif cmd == "generate_mappings":

                source_fields = [
                    FieldModel(**field)
                    for field in payload.get(
                        "source_fields",
                        [],
                    )
                ]

                target_fields = [
                    FieldModel(**field)
                    for field in payload.get(
                        "target_fields",
                        [],
                    )
                ]

                mappings = self.mapping_engine.generate_mappings(
                    source_fields,
                    target_fields,
                )

                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={
                        "mappings": [
                            mapping.model_dump()
                            for mapping in mappings
                        ]
                    },
                ).model_dump()

            # =================================================
            # PREVIEW CONVERSION
            # =================================================

            elif cmd == "preview_conversion":

                records = payload.get("records", [])

                mappings = [
                    FieldMapping(**mapping)
                    for mapping in payload.get(
                        "mappings",
                        [],
                    )
                ]

                indices = payload.get("record_indices")

                search_query = payload.get("search_query")

                filtered = DataTransformer.filter_records(
                    records,
                    search_query=search_query,
                    selected_indices=indices,
                )

                processed = [
                    DataTransformer.process_record(
                        record,
                        mappings,
                    )
                    for _, record in filtered[:20]
                ]

                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={
                        "total_filtered": len(filtered),
                        "preview_records": processed,
                    },
                ).model_dump()

            # =================================================
            # EXECUTE CONVERSION
            # =================================================

            elif cmd == "execute_conversion":

                excel_path = payload.get("excel_path")

                word_path = (
                    payload.get("template_path")
                    or payload.get("word_path")
                )

                output_path = payload.get("output_path")

                output_format = str(
                    payload.get(
                        "output_format",
                        "docx",
                    )
                ).lower()

                sheet_name = payload.get("sheet_name")

                header_override = payload.get(
                    "header_row_override"
                )

                table_index = payload.get(
                    "table_index",
                    0,
                )

                strategy_override = payload.get(
                    "strategy_override"
                )

                record_indices = payload.get(
                    "record_indices"
                )

                mappings = [
                    FieldMapping(**mapping)
                    for mapping in payload.get(
                        "mappings",
                        [],
                    )
                ]

                # ---------------------------------------------
                # VALIDATE INPUT
                # ---------------------------------------------

                if output_format not in ("docx", "pdf"):

                    raise ValueError(
                        "Format output harus docx atau pdf."
                    )

                if not excel_path or not word_path:

                    raise ValueError(
                        "File Excel dan template dokumen wajib disediakan."
                    )

                if not os.path.isfile(excel_path):

                    raise FileNotFoundError(
                        f"File Excel tidak ditemukan: {excel_path}"
                    )

                if not os.path.isfile(word_path):

                    raise FileNotFoundError(
                        f"Template tidak ditemukan: {word_path}"
                    )

                template_type = os.path.splitext(
                    word_path
                )[1].lower()

                if template_type not in (".docx", ".pdf"):

                    raise ValueError(
                        "Template hanya mendukung DOCX dan PDF."
                    )

                if (
                    template_type == ".pdf"
                    and output_format != "pdf"
                ):

                    raise ValueError(
                        "Template PDF hanya dapat menghasilkan PDF."
                    )

                # ---------------------------------------------
                # OUTPUT PATH
                # ---------------------------------------------

                if not output_path:

                    base_name = os.path.splitext(
                        os.path.basename(word_path)
                    )[0]

                    extension = (
                        ".pdf"
                        if output_format == "pdf"
                        else ".docx"
                    )

                    output_path = os.path.join(
                        os.path.dirname(word_path),
                        f"{base_name}_output{extension}",
                    )

                output_path = os.path.abspath(output_path)

                expected_extension = (
                    ".pdf"
                    if output_format == "pdf"
                    else ".docx"
                )

                if not output_path.lower().endswith(
                    expected_extension
                ):

                    output_path = (
                        os.path.splitext(output_path)[0]
                        + expected_extension
                    )

                # ---------------------------------------------
                # ANALYZE EXCEL
                # ---------------------------------------------

                excel_analyzer = ExcelAnalyzer(excel_path)

                src_schema = excel_analyzer.analyze_sheet(
                    sheet_name=sheet_name,
                    header_row_override=header_override,
                )

                all_records = src_schema.all_records

                filtered = DataTransformer.filter_records(
                    all_records,
                    selected_indices=record_indices,
                )

                if not filtered:

                    raise ValueError(
                        "Tidak ada record Excel yang dipilih."
                    )

                processed = [
                    DataTransformer.process_record(
                        record,
                        mappings,
                    )
                    for _, record in filtered
                ]

                sample_vals = []

                for record in processed[:5]:

                    sample_vals.extend(
                        [
                            value
                            for value in record.values()
                            if value is not None and value != ""
                        ]
                    )

                validation_data = {}

                validation_valid = False

                # =================================================
                # PDF TEMPLATE DIRECT GENERATION
                # =================================================

                if template_type == ".pdf":

                    import fitz

                    analyzer = PDFTemplateAnalyzer()

                    tgt_schema = analyzer.analyze(word_path)

                    if not tgt_schema.fields:

                        raise ValueError(
                            "Tidak ditemukan placeholder {{nama_field}} "
                            "pada template PDF."
                        )

                    mappings_by_target = {
                        mapping.target_field_id: mapping
                        for mapping in mappings
                    }

                    pdf_mappings = []

                    seen_occurrences = set()

                    for field in tgt_schema.fields:

                        field_mapping = mappings_by_target.get(
                            field.field_id
                        )

                        if not field_mapping:

                            continue

                        if not field_mapping.source_field_id:

                            continue

                        if str(
                            field_mapping.status
                        ).lower().split(".")[-1] in (
                            "unmatched",
                            "ambiguous",
                        ):

                            continue

                        occurrences = field.metadata.get(
                            "occurrences",
                            [],
                        )

                        for occurrence in occurrences:

                            occurrence_key = (
                                occurrence["placeholder"],
                                occurrence["page_number"],
                            )

                            if occurrence_key in seen_occurrences:

                                continue

                            seen_occurrences.add(
                                occurrence_key
                            )

                            pdf_mappings.append({

                                "placeholder": occurrence[
                                    "placeholder"
                                ],

                                "page_number": occurrence[
                                    "page_number"
                                ],

                                "font_size": occurrence.get(
                                    "font_size",
                                    10,
                                ),

                                "excel_column": field.field_id,

                                "matched": True,

                            })

                    if not pdf_mappings:

                        raise ValueError(
                            "Tidak ada mapping PDF yang valid. "
                            "Periksa pemetaan field."
                        )

                    generator = PDFTemplateGenerator()

                    os.makedirs(
                        os.path.dirname(output_path),
                        exist_ok=True,
                    )

                    total_replacements = 0

                    with tempfile.TemporaryDirectory(
                        prefix="pdf_template_batch_"
                    ) as temp_dir:

                        combined_pdf = fitz.open()

                        try:

                            for index, record in enumerate(
                                processed
                            ):

                                temp_pdf_path = os.path.join(
                                    temp_dir,
                                    f"record_{index + 1}.pdf",
                                )

                                gen_result = generator.generate(

                                    template_path=word_path,

                                    output_path=temp_pdf_path,

                                    row_data=record,

                                    mappings=pdf_mappings,

                                )

                                total_replacements += gen_result[
                                    "replacements_count"
                                ]

                                with fitz.open(
                                    temp_pdf_path
                                ) as part:

                                    combined_pdf.insert_pdf(
                                        part
                                    )

                            if len(combined_pdf) == 0:

                                raise RuntimeError(
                                    "PDF hasil tidak memiliki halaman."
                                )

                            combined_pdf.save(
                                output_path,
                                garbage=4,
                                deflate=True,
                            )

                        finally:

                            combined_pdf.close()

                    # -----------------------------------------
                    # VALIDATE GENERATED PDF
                    # -----------------------------------------

                    with fitz.open(output_path) as result_pdf:

                        actual_pages = len(result_pdf)

                    with fitz.open(word_path) as template_pdf:

                        expected_pages = (
                            len(template_pdf) * len(processed)
                        )

                    validation_valid = (
                        actual_pages == expected_pages
                        and actual_pages > 0
                    )

                    validation_data = {

                        "is_valid": validation_valid,

                        "expected_pages": expected_pages,

                        "actual_pages": actual_pages,

                        "records_processed": len(processed),

                        "replacements_count": total_replacements,

                        "warnings": (
                            []
                            if validation_valid
                            else [
                                "Jumlah halaman PDF tidak sesuai "
                                "dengan jumlah halaman yang diharapkan."
                            ]
                        ),

                    }

                    gen_result = {

                        "output_path": output_path,

                        "records_written": len(processed),

                        "pages_written": actual_pages,

                        "replacements_count": total_replacements,

                        "file_size_bytes": os.path.getsize(
                            output_path
                        ),

                        "output_format": "pdf",

                        "template_type": "pdf",

                        "strategy_used": "replace_placeholders",

                    }

                # =================================================
                # ORIGINAL WORD DOCX GENERATION
                # =================================================

                else:

                    word_analyzer = WordAnalyzer(word_path)

                    tgt_schema = word_analyzer.analyze()

                    generator = WordGenerator(word_path)

                    # -----------------------------------------
                    # WORD TO PDF
                    # -----------------------------------------

                    if output_format == "pdf":

                        with tempfile.TemporaryDirectory(
                            prefix="document_converter_"
                        ) as temp_dir:

                            temp_docx_path = os.path.join(
                                temp_dir,
                                "intermediate_document.docx",
                            )

                            generator.generate(

                                output_path=temp_docx_path,

                                processed_records=processed,

                                mappings=mappings,

                                target_schema=tgt_schema,

                                strategy_override=strategy_override,

                                table_index=table_index,

                            )

                            val_result = OutputValidator.validate(

                                output_path=temp_docx_path,

                                expected_records_count=len(
                                    processed
                                ),

                                expected_values_to_verify=sample_vals[:10],

                                table_index=table_index,

                            )

                            if not val_result.is_valid:

                                raise RuntimeError(
                                    "Dokumen Word sementara gagal "
                                    "divalidasi. Konversi PDF dibatalkan."
                                )

                            pdf_converter = PDFConverter()

                            pdf_result = pdf_converter.convert(

                                docx_path=temp_docx_path,

                                pdf_path=output_path,

                            )

                            gen_result = {

                                "output_path": pdf_result[
                                    "output_path"
                                ],

                                "records_written": len(processed),

                                "strategy_used": (
                                    strategy_override
                                    or tgt_schema.recommended_strategy
                                    or "repeat_template_row"
                                ),

                                "table_index": table_index,

                                "file_size_bytes": pdf_result[
                                    "file_size_bytes"
                                ],

                                "output_format": "pdf",

                                "template_type": "docx",

                            }

                            validation_data = (
                                val_result.to_dict()
                            )

                            validation_valid = (
                                val_result.is_valid
                            )

                    # -----------------------------------------
                    # WORD TO DOCX
                    # -----------------------------------------

                    else:

                        gen_result = generator.generate(

                            output_path=output_path,

                            processed_records=processed,

                            mappings=mappings,

                            target_schema=tgt_schema,

                            strategy_override=strategy_override,

                            table_index=table_index,

                        )

                        val_result = OutputValidator.validate(

                            output_path=output_path,

                            expected_records_count=len(processed),

                            expected_values_to_verify=sample_vals[:10],

                            table_index=table_index,

                        )

                        validation_data = (
                            val_result.to_dict()
                        )

                        validation_valid = (
                            val_result.is_valid
                        )

                        gen_result["output_format"] = "docx"

                        gen_result["template_type"] = "docx"

                # =================================================
                # RECORD USER CONFIRMED MAPPINGS
                # =================================================

                for mapping in mappings:

                    if (
                        mapping.source_name
                        and mapping.target_name
                        and mapping.user_override
                    ):

                        self.feedback_store.record_confirmed_mapping(
                            mapping.source_name,
                            mapping.target_name,
                        )

                # =================================================
                # RECORD CONVERSION HISTORY
                # =================================================

                session_id = payload.get(
                    "session_id",
                    str(uuid.uuid4()),
                )

                self.feedback_store.record_conversion_run(

                    session_id=session_id,

                    excel_path=excel_path,

                    word_path=word_path,

                    output_path=output_path,

                    record_count=len(processed),

                    status=(
                        "success"
                        if validation_valid
                        else "validation_warning"
                    ),

                )

                return IPCResponse(

                    success=True,

                    request_id=req_id,

                    data={

                        "generation": gen_result,

                        "validation": validation_data,

                        "session_id": session_id,

                    },

                ).model_dump()

            # =================================================
            # GET CONVERSION HISTORY
            # =================================================

            elif cmd == "get_history":

                limit = payload.get(
                    "limit",
                    20,
                )

                runs = self.feedback_store.get_recent_runs(
                    limit=limit
                )

                return IPCResponse(

                    success=True,

                    request_id=req_id,

                    data={
                        "runs": runs
                    },

                ).model_dump()

            # =================================================
            # UNKNOWN COMMAND
            # =================================================

            else:

                return IPCResponse(

                    success=False,

                    request_id=req_id,

                    error=f"Unknown command: '{cmd}'",

                ).model_dump()

        except Exception as e:

            return IPCResponse(

                success=False,

                request_id=req_id,

                error=str(e),

            ).model_dump()


# =============================================================
# CLI MODE
# =============================================================

def run_cli_mode():

    controller = EngineController()

    input_text = sys.stdin.read().strip()

    if not input_text:

        res = IPCResponse(

            success=False,

            request_id="init",

            error="No input JSON provided on stdin",

        )

        sys.stdout.write(
            json.dumps(res.model_dump())
        )

        sys.stdout.write("\n")

        return

    try:

        req_data = json.loads(input_text)

        res_data = controller.handle_request(
            req_data
        )

        sys.stdout.write(
            json.dumps(res_data)
        )

        sys.stdout.write("\n")

    except Exception as e:

        res = IPCResponse(

            success=False,

            request_id="parse_error",

            error=f"Invalid JSON input: {str(e)}",

        )

        sys.stdout.write(
            json.dumps(res.model_dump())
        )

        sys.stdout.write("\n")


# =============================================================
# FASTAPI SERVER
# =============================================================

def create_fastapi_app():

    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse
    from pathlib import Path

    app = FastAPI(
        title="Smart Document Converter Engine API",
        version=PROTOCOL_VERSION,
    )

    controller = EngineController()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # =========================================================
    # IPC ENDPOINT
    # =========================================================

    @app.post("/api/ipc")
    async def ipc_endpoint(request: IPCRequest):

        res = controller.handle_request(
            request.model_dump()
        )

        if not res.get("success"):

            raise HTTPException(
                status_code=400,
                detail=res.get(
                    "error",
                    "Engine error",
                ),
            )

        return res

    # =========================================================
    # DOWNLOAD GENERATED FILE
    # =========================================================

    @app.get("/api/download")
    async def download_endpoint(file_path: str):

        try:

            path = Path(file_path).expanduser().resolve()

        except (ValueError, OSError):

            raise HTTPException(
                status_code=400,
                detail="Invalid file path",
            )

        if not path.exists() or not path.is_file():

            raise HTTPException(
                status_code=404,
                detail="Output file not found",
            )

        allowed_extensions = {
            ".pdf",
            ".docx",
        }

        extension = path.suffix.lower()

        if extension not in allowed_extensions:

            raise HTTPException(
                status_code=400,
                detail="Unsupported download file type",
            )

        media_types = {

            ".pdf": "application/pdf",

            ".docx": (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),

        }

        return FileResponse(

            path=str(path),

            filename=path.name,

            media_type=media_types[extension],

            headers={
                "Content-Disposition": (
                    f'attachment; filename="{path.name}"'
                )
            },

        )

    # =========================================================
    # HEALTH CHECK
    # =========================================================

    @app.get("/api/health")
    async def health():

        return {

            "status": "healthy",

            "protocol_version": PROTOCOL_VERSION,

        }

    return app


# =============================================================
# MAIN ENTRYPOINT
# =============================================================

def main():

    parser = argparse.ArgumentParser(

        description="Smart Document Converter Python Engine"

    )

    parser.add_argument(

        "--serve",

        action="store_true",

        help="Start local FastAPI IPC server",

    )

    parser.add_argument(

        "--port",

        type=int,

        default=8000,

        help="Port for IPC server",

    )

    parser.add_argument(

        "--command",

        type=str,

        help="Single JSON string to execute",

    )

    args = parser.parse_args()

    if args.serve:

        import uvicorn

        app = create_fastapi_app()

        uvicorn.run(

            app,

            host="127.0.0.1",

            port=args.port,

        )

    elif args.command:

        controller = EngineController()

        req_data = json.loads(args.command)

        res_data = controller.handle_request(
            req_data
        )

        print(
            json.dumps(res_data)
        )

    else:

        run_cli_mode()


if __name__ == "__main__":

    main()
