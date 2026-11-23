"""
End-to-End Integration Workflow Tests.
Tests the full IPC controller execution path:
Upload/Inspect -> Analyze Excel -> Analyze Word -> Generate Mappings -> Preview -> Execute Conversion -> Validate -> History.
"""

import os
import pytest
from engine.cli import EngineController


def test_full_ipc_workflow(fixtures_dir, tmp_path):
    db_path = str(tmp_path / "integration_history.db")
    controller = EngineController(db_path=db_path)

    excel_path = os.path.join(fixtures_dir, "medical_records.xlsx")
    word_path = os.path.join(fixtures_dir, "medical_template.docx")
    out_path = str(tmp_path / "integration_output.docx")

    # Step 1: Inspect Excel
    resp_inspect = controller.handle_request({
        "command": "inspect_excel",
        "payload": {"file_path": excel_path},
    })
    assert resp_inspect["success"] is True
    assert len(resp_inspect["data"]["sheets"]) == 1

    # Step 2: Analyze Excel
    resp_src = controller.handle_request({
        "command": "analyze_excel",
        "payload": {"file_path": excel_path},
    })
    assert resp_src["success"] is True
    src_schema = resp_src["data"]["source_schema"]
    assert len(src_schema["fields"]) == 7

    # Step 3: Analyze Word
    resp_tgt = controller.handle_request({
        "command": "analyze_word",
        "payload": {"file_path": word_path},
    })
    assert resp_tgt["success"] is True
    tgt_schema = resp_tgt["data"]["target_schema"]
    assert len(tgt_schema["fields"]) == 7

    # Step 4: Generate Mappings
    resp_map = controller.handle_request({
        "command": "generate_mappings",
        "payload": {
            "source_fields": src_schema["fields"],
            "target_fields": tgt_schema["fields"],
        },
    })
    assert resp_map["success"] is True
    mappings = resp_map["data"]["mappings"]
    assert len(mappings) == 7

    # Step 5: Preview Conversion
    resp_prev = controller.handle_request({
        "command": "preview_conversion",
        "payload": {
            "records": src_schema["preview_records"],
            "mappings": mappings,
            "record_indices": [0, 1],
        },
    })
    assert resp_prev["success"] is True
    assert len(resp_prev["data"]["preview_records"]) == 2

    # Step 6: Execute Conversion
    resp_exec = controller.handle_request({
        "command": "execute_conversion",
        "payload": {
            "excel_path": excel_path,
            "word_path": word_path,
            "output_path": out_path,
            "mappings": mappings,
            "record_indices": [0, 1, 2],
        },
    })
    assert resp_exec["success"] is True
    exec_data = resp_exec["data"]
    assert exec_data["generation"]["records_written"] == 3
    assert exec_data["validation"]["is_valid"] is True
    assert os.path.exists(out_path)

    # Step 7: Check History Log
    resp_hist = controller.handle_request({
        "command": "get_history",
        "payload": {"limit": 5},
    })
    assert resp_hist["success"] is True
    assert len(resp_hist["data"]["runs"]) >= 1
    run0 = resp_hist["data"]["runs"][0]
    assert run0["record_count"] == 3
    assert run0["status"] == "success"
