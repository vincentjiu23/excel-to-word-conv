"""
Structured Versioned JSON IPC Protocol Interface & CLI Entrypoint.
Protocol Version: 1.0.0
Can be executed as CLI (stdin -> stdout) or launched as local IPC server.
"""

import argparse
import json
import os
import sys
import uuid
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


class EngineController:
    def __init__(self, db_path: str = "conversion_history.db"):
        self.feedback_store = FeedbackStore(db_path=db_path)
        self.mapping_engine = IntelligentMappingEngine(feedback_store=self.feedback_store)

    def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        req_id = request_data.get("request_id", str(uuid.uuid4()))
        cmd = request_data.get("command", "")
        payload = request_data.get("payload", {})

        try:
            if cmd == "inspect_excel":
                file_path = payload.get("file_path")
                analyzer = ExcelAnalyzer(file_path)
                sheets = analyzer.inspect_sheets()
                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={"sheets": [s.model_dump() for s in sheets]},
                ).model_dump()

            elif cmd == "analyze_excel":
                file_path = payload.get("file_path")
                sheet_name = payload.get("sheet_name")
                header_override = payload.get("header_row_override")
                analyzer = ExcelAnalyzer(file_path)
                schema = analyzer.analyze_sheet(
                    sheet_name=sheet_name,
                    header_row_override=header_override,
                )
                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={"source_schema": schema.model_dump()},
                ).model_dump()

            elif cmd == "analyze_word":
                file_path = payload.get("file_path")
                analyzer = WordAnalyzer(file_path)
                schema = analyzer.analyze()
                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={"target_schema": schema.model_dump()},
                ).model_dump()

            elif cmd == "generate_mappings":
                source_fields = [FieldModel(**f) for f in payload.get("source_fields", [])]
                target_fields = [FieldModel(**f) for f in payload.get("target_fields", [])]
                mappings = self.mapping_engine.generate_mappings(source_fields, target_fields)
                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={"mappings": [m.model_dump() for m in mappings]},
                ).model_dump()

            elif cmd == "preview_conversion":
                records = payload.get("records", [])
                mappings = [FieldMapping(**m) for m in payload.get("mappings", [])]
                indices = payload.get("record_indices")
                search_query = payload.get("search_query")

                filtered = DataTransformer.filter_records(records, search_query=search_query, selected_indices=indices)
                processed = [DataTransformer.process_record(r, mappings) for _, r in filtered[:20]]

                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={
                        "total_filtered": len(filtered),
                        "preview_records": processed,
                    },
                ).model_dump()

            elif cmd == "execute_conversion":
                excel_path = payload.get("excel_path")
                word_path = payload.get("word_path")
                output_path = payload.get("output_path")
                sheet_name = payload.get("sheet_name")
                header_override = payload.get("header_row_override")
                table_index = payload.get("table_index", 0)
                strategy_override = payload.get("strategy_override")
                record_indices = payload.get("record_indices")
                mappings = [FieldMapping(**m) for m in payload.get("mappings", [])]

                if not output_path:
                    base_name = os.path.splitext(os.path.basename(word_path))[0]
                    output_path = os.path.join(os.path.dirname(word_path), f"{base_name}_output.docx")

                # Analyze excel to load full records
                excel_analyzer = ExcelAnalyzer(excel_path)
                src_schema = excel_analyzer.analyze_sheet(sheet_name=sheet_name, header_row_override=header_override)

                # Analyze word target
                word_analyzer = WordAnalyzer(word_path)
                tgt_schema = word_analyzer.analyze()

                # Process records
                all_records = src_schema.preview_records  # or full records from analyzer
                filtered = DataTransformer.filter_records(all_records, selected_indices=record_indices)
                processed = [DataTransformer.process_record(r, mappings) for _, r in filtered]

                # Generate word doc
                generator = WordGenerator(word_path)
                gen_result = generator.generate(
                    output_path=output_path,
                    processed_records=processed,
                    mappings=mappings,
                    target_schema=tgt_schema,
                    strategy_override=strategy_override,
                    table_index=table_index,
                )

                # Validate output
                sample_vals = []
                for p_rec in processed[:5]:
                    sample_vals.extend([v for v in p_rec.values() if v])

                val_result = OutputValidator.validate(
                    output_path=output_path,
                    expected_records_count=len(processed),
                    expected_values_to_verify=sample_vals[:10],
                    table_index=table_index,
                )

                # Record user confirmations in feedback store
                for m in mappings:
                    if m.source_name and m.target_name and m.user_override:
                        self.feedback_store.record_confirmed_mapping(m.source_name, m.target_name)

                # Record run history
                session_id = payload.get("session_id", str(uuid.uuid4()))
                self.feedback_store.record_conversion_run(
                    session_id=session_id,
                    excel_path=excel_path,
                    word_path=word_path,
                    output_path=output_path,
                    record_count=len(processed),
                    status="success" if val_result.is_valid else "validation_warning",
                )

                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={
                        "generation": gen_result,
                        "validation": val_result.to_dict(),
                        "session_id": session_id,
                    },
                ).model_dump()

            elif cmd == "get_history":
                limit = payload.get("limit", 20)
                runs = self.feedback_store.get_recent_runs(limit=limit)
                return IPCResponse(
                    success=True,
                    request_id=req_id,
                    data={"runs": runs},
                ).model_dump()

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


def run_cli_mode():
    controller = EngineController()
    input_text = sys.stdin.read().strip()
    if not input_text:
        res = IPCResponse(
            success=False,
            request_id="init",
            error="No input JSON provided on stdin",
        )
        sys.stdout.write(json.dumps(res.model_dump()))
        sys.stdout.write("\n")
        return

    try:
        req_data = json.loads(input_text)
        res_data = controller.handle_request(req_data)
        sys.stdout.write(json.dumps(res_data))
        sys.stdout.write("\n")
    except Exception as e:
        res = IPCResponse(
            success=False,
            request_id="parse_error",
            error=f"Invalid JSON input: {str(e)}",
        )
        sys.stdout.write(json.dumps(res.model_dump()))
        sys.stdout.write("\n")


def create_fastapi_app():
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    app = FastAPI(title="Smart Document Converter Engine API", version=PROTOCOL_VERSION)
    controller = EngineController()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/api/ipc")
    async def ipc_endpoint(request: IPCRequest):
        res = controller.handle_request(request.model_dump())
        if not res.get("success"):
            raise HTTPException(status_code=400, detail=res.get("error", "Engine error"))
        return res

    @app.get("/api/health")
    async def health():
        return {"status": "healthy", "protocol_version": PROTOCOL_VERSION}

    return app


def main():
    parser = argparse.ArgumentParser(description="Smart Document Converter Python Engine")
    parser.add_argument("--serve", action="store_true", help="Start local FastAPI IPC server")
    parser.add_argument("--port", type=int, default=8000, help="Port for IPC server")
    parser.add_argument("--command", type=str, help="Single JSON string to execute")

    args = parser.parse_args()

    if args.serve:
        import uvicorn

        app = create_fastapi_app()
        uvicorn.run(app, host="127.0.0.1", port=args.port)
    elif args.command:
        controller = EngineController()
        req_data = json.loads(args.command)
        res_data = controller.handle_request(req_data)
        print(json.dumps(res_data))
    else:
        run_cli_mode()


if __name__ == "__main__":
    main()
