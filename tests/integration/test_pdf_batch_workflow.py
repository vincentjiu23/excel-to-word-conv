
"""
Integration test for Excel -> Digital PDF Template -> Combined PDF.

Verifies that all Excel records are processed, including records
beyond the 50-record preview limit.
"""

import fitz
import openpyxl

from engine.cli import EngineController
from engine.excel.analyzer import ExcelAnalyzer
from engine.pdf_template import PDFTemplateAnalyzer


def create_excel(path, record_count=75):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Data"

    worksheet.append(["Nama"])

    for index in range(1, record_count + 1):
        worksheet.append([f"Nama {index}"])

    workbook.save(path)
    workbook.close()


def create_pdf_template(path):
    document = fitz.open()
    page = document.new_page()

    page.insert_text(
        (60, 100),
        "Nama: {{nama}}",
        fontsize=12,
        fontname="helv",
    )

    document.save(path)
    document.close()


def test_pdf_batch_workflow_processes_all_75_records(tmp_path):
    excel_path = tmp_path / "records.xlsx"
    template_path = tmp_path / "template.pdf"
    output_path = tmp_path / "combined_output.pdf"
    db_path = tmp_path / "history.db"

    # -------------------------------------------------
    # 1. Create test files
    # -------------------------------------------------

    create_excel(excel_path, record_count=75)
    create_pdf_template(str(template_path))

    # -------------------------------------------------
    # 2. Analyze Excel and PDF template
    # -------------------------------------------------

    excel_analyzer = ExcelAnalyzer(str(excel_path))
    source_schema = excel_analyzer.analyze_sheet()

    pdf_analyzer = PDFTemplateAnalyzer()
    target_schema = pdf_analyzer.analyze(str(template_path))

    assert source_schema.total_rows == 75
    assert len(source_schema.preview_records) == 50
    assert len(source_schema.all_records) == 75

    assert len(target_schema.fields) == 1

    source_field = source_schema.fields[0]
    target_field = target_schema.fields[0]

    assert source_field.original_name == "Nama"
    assert target_field.original_name == "nama"

    # -------------------------------------------------
    # 3. Create explicit field mapping
    # -------------------------------------------------

    mappings = [
        {
            "mapping_id": "mapping_nama",
            "target_field_id": target_field.field_id,
            "target_name": target_field.original_name,
            "source_field_id": source_field.field_id,
            "source_name": source_field.original_name,
            "confidence": 1.0,
            "status": "exact_match",
            "reason": "Integration test mapping",
            "stage": "initial",
            "transformations": [],
            "constant_value": None,
            "default_value": None,
            "user_override": True,
            "metadata": {},
        }
    ]

    # -------------------------------------------------
    # 4. Execute conversion through IPC controller
    # -------------------------------------------------

    controller = EngineController(
        db_path=str(db_path)
    )

    response = controller.handle_request({
        "command": "execute_conversion",
        "payload": {
            "excel_path": str(excel_path),
            "template_path": str(template_path),
            "output_path": str(output_path),
            "output_format": "pdf",
            "mappings": mappings,
        },
    })

    assert response["success"] is True, response

    result = response["data"]

    # -------------------------------------------------
    # 5. Verify generation result
    # -------------------------------------------------

    generation = result["generation"]
    validation = result["validation"]

    assert generation["records_written"] == 75
    assert generation["pages_written"] == 75
    assert generation["output_format"] == "pdf"
    assert generation["template_type"] == "pdf"

    assert validation["is_valid"] is True
    assert validation["expected_pages"] == 75
    assert validation["actual_pages"] == 75
    assert validation["records_processed"] == 75

    assert output_path.exists()
    assert output_path.stat().st_size > 0

    # -------------------------------------------------
    # 6. Verify first and last records in final PDF
    # -------------------------------------------------

    with fitz.open(str(output_path)) as document:
        assert len(document) == 75

        first_page_text = document[0].get_text()
        last_page_text = document[74].get_text()

    assert "Nama 1" in first_page_text
    assert "Nama 75" in last_page_text

    # -------------------------------------------------
    # 7. Verify conversion history
    # -------------------------------------------------

    history_response = controller.handle_request({
        "command": "get_history",
        "payload": {"limit": 5},
    })

    assert history_response["success"] is True

    runs = history_response["data"]["runs"]

    assert len(runs) >= 1
    assert runs[0]["record_count"] == 75
    assert runs[0]["status"] == "success"
