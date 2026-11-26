
"""Tests for complete Excel record retention."""

import openpyxl

from engine.excel.analyzer import ExcelAnalyzer


def test_analyzer_keeps_all_records_beyond_preview_limit(tmp_path):
    """Preview stays limited while all records remain available."""

    excel_path = tmp_path / "large_dataset.xlsx"

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Data"

    worksheet.append(["Nama", "Nilai"])

    for index in range(1, 76):
        worksheet.append([f"Nama {index}", index * 10])

    workbook.save(excel_path)
    workbook.close()

    analyzer = ExcelAnalyzer(str(excel_path))

    schema = analyzer.analyze_sheet(
        max_preview_records=50
    )

    # Total records detected
    assert schema.total_rows == 75

    # Preview remains limited to 50
    assert len(schema.preview_records) == 50

    # Internal records contain all 75 rows
    assert len(schema.all_records) == 75

    # First and last records are retained
    assert schema.all_records[0]["excel_1_nama"] == "Nama 1"
    assert schema.all_records[-1]["excel_1_nama"] == "Nama 75"

    # Internal records must not leak into serialized schema
    serialized = schema.model_dump()
    assert "all_records" not in serialized
