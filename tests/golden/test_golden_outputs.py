"""
Golden Output Tests.
Compares generated output against expected golden structure baselines:
- Table grid structure
- Header preservation
- Record counts
- Exact cell data preservation
"""

import os
import pytest
from docx import Document
from engine.excel.analyzer import ExcelAnalyzer
from engine.word.analyzer import WordAnalyzer
from engine.mapping.engine import IntelligentMappingEngine
from engine.generator.generator import WordGenerator
from engine.transform.transformer import DataTransformer
from engine.validator.validator import OutputValidator


def test_golden_medical_conversion(fixtures_dir, tmp_path):
    excel_path = os.path.join(fixtures_dir, "medical_records.xlsx")
    word_path = os.path.join(fixtures_dir, "medical_template.docx")
    golden_out_path = str(tmp_path / "golden_medical_output.docx")

    # Perform conversion
    x_analyzer = ExcelAnalyzer(excel_path)
    src_schema = x_analyzer.analyze_sheet()

    w_analyzer = WordAnalyzer(word_path)
    tgt_schema = w_analyzer.analyze()

    mapper = IntelligentMappingEngine()
    mappings = mapper.generate_mappings(src_schema.fields, tgt_schema.fields)

    processed = [DataTransformer.process_record(r, mappings) for r in src_schema.preview_records]
    gen = WordGenerator(word_path)
    gen.generate(golden_out_path, processed, mappings, tgt_schema)

    # Inspect golden output
    golden_doc = Document(golden_out_path)
    assert len(golden_doc.tables) == 1
    table = golden_doc.tables[0]

    # Expected: 1 header row + 3 data rows = 4 rows
    assert len(table.rows) == 4

    # Header values
    headers = [c.text for c in table.rows[0].cells]
    assert headers[0] == "Subject ID"
    assert headers[1] == "Full Legal Name"

    # Row 1 data
    row1 = [c.text for c in table.rows[1].cells]
    assert row1[0] == "SUB-1001"
    assert "Alice Morgan" in row1[1]

    # Row 2 data
    row2 = [c.text for c in table.rows[2].cells]
    assert row2[0] == "SUB-1002"
    assert "Bob Vance" in row2[1]

    # Row 3 data
    row3 = [c.text for c in table.rows[3].cells]
    assert row3[0] == "SUB-1003"
    assert "Clara Oswald" in row3[1]
