"""
Unit tests for Dynamic Excel Analyzer.
"""

import os
import pytest
from engine.excel.analyzer import ExcelAnalyzer
from engine.models.field import DataType


def test_excel_sheet_inspection(fixtures_dir):
    path = os.path.join(fixtures_dir, "medical_records.xlsx")
    analyzer = ExcelAnalyzer(path)
    sheets = analyzer.inspect_sheets()
    assert len(sheets) == 1
    assert sheets[0].name == "PatientRecords"
    assert sheets[0].is_hidden is False
    assert sheets[0].detected_header_row == 1


def test_excel_analyze_sheet_schema_and_types(fixtures_dir):
    path = os.path.join(fixtures_dir, "medical_records.xlsx")
    analyzer = ExcelAnalyzer(path)
    schema = analyzer.analyze_sheet()

    assert schema.sheet_name == "PatientRecords"
    assert schema.header_row_index == 1
    assert schema.total_rows == 3
    assert len(schema.fields) == 7

    # Check field names and types
    field_names = [f.original_name for f in schema.fields]
    assert "Subject_ID" in field_names
    assert "Systolic_BP" in field_names
    assert "Visit_Date" in field_names

    # Check type inference
    bp_field = next(f for f in schema.fields if f.original_name == "Systolic_BP")
    assert bp_field.data_type in (DataType.INTEGER, DataType.FLOAT)

    date_field = next(f for f in schema.fields if f.original_name == "Visit_Date")
    assert date_field.data_type in (DataType.DATE, DataType.DATETIME)

    # Check samples collected
    assert len(bp_field.sample_values) > 0


def test_excel_header_on_row_4(fixtures_dir):
    path = os.path.join(fixtures_dir, "header_on_row_4.xlsx")
    analyzer = ExcelAnalyzer(path)
    schema = analyzer.analyze_sheet()

    # The header detector should find row 4 as the header row
    assert schema.header_row_index == 4
    field_names = [f.original_name for f in schema.fields]
    assert "Asset_Tag" in field_names
    assert "Location_Zone" in field_names
    assert "Acquisition_Cost" in field_names


def test_excel_duplicate_and_empty_headers(fixtures_dir):
    path = os.path.join(fixtures_dir, "duplicate_and_empty_headers.xlsx")
    analyzer = ExcelAnalyzer(path)
    schema = analyzer.analyze_sheet()

    # Check that duplicate Item_Code was disambiguated to Item_Code_2
    field_names = [f.original_name for f in schema.fields]
    assert "Item_Code" in field_names
    assert any("Item_Code_2" in name for name in field_names)

    # Check that empty header was assigned Column_B
    assert any("Column_B" in name for name in field_names)
    assert len(schema.warnings) > 0


def test_excel_formula_detection_without_execution(fixtures_dir):
    path = os.path.join(fixtures_dir, "formulas_and_mixed.xlsx")
    analyzer = ExcelAnalyzer(path)
    schema = analyzer.analyze_sheet()

    assert schema.has_formulas is True
    assert schema.formula_count > 0
    assert any("Detected" in w and "formula" in w for w in schema.warnings)
