"""
Unit tests for Dynamic Word Template Analyzer.
"""

import os
import pytest
from engine.word.analyzer import WordAnalyzer


def test_word_table_and_header_analysis(fixtures_dir):
    path = os.path.join(fixtures_dir, "medical_template.docx")
    analyzer = WordAnalyzer(path)
    schema = analyzer.analyze()

    assert schema.structure.has_tables is True
    assert schema.structure.table_count == 1
    assert len(schema.tables) == 1

    table0 = schema.tables[0]
    assert table0.col_count == 7
    assert table0.header_row_index == 0
    assert "Subject ID" in table0.sample_headers
    assert "Full Legal Name" in table0.sample_headers

    # Check target fields extracted from table
    field_names = [f.original_name for f in schema.fields]
    assert "Subject ID" in field_names
    assert "Systolic BP" in field_names
    assert "Clinical Notes" in field_names


def test_word_placeholder_detection(fixtures_dir):
    path = os.path.join(fixtures_dir, "placeholder_certificate.docx")
    analyzer = WordAnalyzer(path)
    schema = analyzer.analyze()

    assert schema.structure.placeholder_count >= 5
    field_names = [f.original_name for f in schema.fields]
    assert "Full_Legal_Name" in field_names
    assert "Subject_ID" in field_names
    assert "Visit_Date" in field_names
    assert "replace_placeholders" in schema.candidate_strategies


def test_word_multi_table_detection(fixtures_dir):
    path = os.path.join(fixtures_dir, "multi_table_template.docx")
    analyzer = WordAnalyzer(path)
    schema = analyzer.analyze()

    assert schema.structure.table_count == 2
    assert len(schema.tables) == 2
    assert schema.tables[0].col_count == 3
    assert schema.tables[1].col_count == 4
