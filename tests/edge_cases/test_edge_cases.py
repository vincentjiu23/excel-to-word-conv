"""
Edge Case Tests.
Tests:
- Header on row 1 vs later rows
- Blank and corrupted inputs
- Missing values in records
- Special characters, symbols, emojis in cell text
- Single record conversions
- Mappings with empty or null inputs
"""

import os
import openpyxl
from docx import Document
import pytest
from engine.excel.analyzer import ExcelAnalyzer
from engine.generator.generator import WordGenerator
from engine.mapping.engine import IntelligentMappingEngine
from engine.models.mapping import FieldMapping, MappingStatus
from engine.transform.transformer import DataTransformer
from engine.validator.validator import OutputValidator
from engine.word.analyzer import WordAnalyzer


def test_special_characters_and_emojis(tmp_path):
    excel_path = str(tmp_path / "emojis.xlsx")
    word_path = str(tmp_path / "emojis.docx")
    out_path = str(tmp_path / "emojis_out.docx")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Status_Icon", "Description_Text"])
    ws.append(["✅ Passed", "All tests ok: ∑ π α β"])
    ws.append(["⚠️ Warning", "Check threshold: 100% & <200>"])
    wb.save(excel_path)

    doc = Document()
    t = doc.add_table(rows=2, cols=2)
    t.cell(0, 0).text = "Status Icon"
    t.cell(0, 1).text = "Description Text"
    doc.save(word_path)

    x_analyzer = ExcelAnalyzer(excel_path)
    src_schema = x_analyzer.analyze_sheet()
    w_analyzer = WordAnalyzer(word_path)
    tgt_schema = w_analyzer.analyze()

    mapper = IntelligentMappingEngine()
    mappings = mapper.generate_mappings(src_schema.fields, tgt_schema.fields)
    processed = [DataTransformer.process_record(r, mappings) for r in src_schema.preview_records]

    gen = WordGenerator(word_path)
    gen.generate(out_path, processed, mappings, tgt_schema)

    val = OutputValidator.validate(out_path, expected_records_count=2, expected_values_to_verify=["Passed", "Warning"])
    assert val.is_valid is True


def test_missing_values_and_null_cells(tmp_path):
    excel_path = str(tmp_path / "sparse.xlsx")
    word_path = str(tmp_path / "sparse.docx")
    out_path = str(tmp_path / "sparse_out.docx")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ColA", "ColB", "ColC"])
    ws.append(["A1", None, "C1"])
    ws.append([None, "B2", None])
    ws.append(["", "", ""])  # Entirely blank row
    wb.save(excel_path)

    doc = Document()
    t = doc.add_table(rows=2, cols=3)
    t.cell(0, 0).text = "ColA"
    t.cell(0, 1).text = "ColB"
    t.cell(0, 2).text = "ColC"
    doc.save(word_path)

    x_analyzer = ExcelAnalyzer(excel_path)
    src_schema = x_analyzer.analyze_sheet()

    # The 3rd empty row should be skipped, so total_rows == 2
    assert src_schema.total_rows == 2

    w_analyzer = WordAnalyzer(word_path)
    tgt_schema = w_analyzer.analyze()

    mapper = IntelligentMappingEngine()
    mappings = mapper.generate_mappings(src_schema.fields, tgt_schema.fields)
    processed = [DataTransformer.process_record(r, mappings) for r in src_schema.preview_records]

    gen = WordGenerator(word_path)
    gen.generate(out_path, processed, mappings, tgt_schema)

    val = OutputValidator.validate(out_path, expected_records_count=2, expected_values_to_verify=["A1", "B2"])
    assert val.is_valid is True
