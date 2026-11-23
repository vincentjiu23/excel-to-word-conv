"""
Unit tests for Word Generation Engine and Output Validator.
"""

import os
import pytest
from docx import Document
from engine.generator.generator import WordGenerator
from engine.validator.validator import OutputValidator
from engine.word.analyzer import WordAnalyzer
from engine.models.mapping import FieldMapping


def test_word_generator_repeat_rows(fixtures_dir, tmp_path):
    template_path = os.path.join(fixtures_dir, "medical_template.docx")
    out_path = str(tmp_path / "generated_medical.docx")

    word_analyzer = WordAnalyzer(template_path)
    tgt_schema = word_analyzer.analyze()

    # Create synthetic mapped records
    processed_records = [
        {
            tgt_schema.fields[0].field_id: "SUB-01",
            tgt_schema.fields[1].field_id: "Alice",
            tgt_schema.fields[2].field_id: "120",
            tgt_schema.fields[3].field_id: "80",
            tgt_schema.fields[4].field_id: "2025-01-01",
            tgt_schema.fields[5].field_id: "Normal",
            tgt_schema.fields[6].field_id: "Ok",
        },
        {
            tgt_schema.fields[0].field_id: "SUB-02",
            tgt_schema.fields[1].field_id: "Bob",
            tgt_schema.fields[2].field_id: "140",
            tgt_schema.fields[3].field_id: "90",
            tgt_schema.fields[4].field_id: "2025-01-02",
            tgt_schema.fields[5].field_id: "Elevated",
            tgt_schema.fields[6].field_id: "Followup",
        },
    ]

    mappings = [
        FieldMapping(
            mapping_id=f"m_{f.field_id}",
            target_field_id=f.field_id,
            target_name=f.original_name,
        )
        for f in tgt_schema.fields
    ]

    generator = WordGenerator(template_path)
    res = generator.generate(
        output_path=out_path,
        processed_records=processed_records,
        mappings=mappings,
        target_schema=tgt_schema,
    )

    assert os.path.exists(out_path)
    assert res["records_written"] == 2

    # Validate output
    val = OutputValidator.validate(
        output_path=out_path,
        expected_records_count=2,
        expected_values_to_verify=["Alice", "Bob", "SUB-01"],
    )
    assert val.is_valid is True
    assert len(val.checks_failed) == 0


def test_word_generator_placeholders(fixtures_dir, tmp_path):
    template_path = os.path.join(fixtures_dir, "placeholder_certificate.docx")
    out_path = str(tmp_path / "generated_cert.docx")

    word_analyzer = WordAnalyzer(template_path)
    tgt_schema = word_analyzer.analyze()

    f_map = {f.original_name: f.field_id for f in tgt_schema.fields}

    processed_records = [
        {
            f_map["Full_Legal_Name"]: "Dr. Elizabeth Shaw",
            f_map["Subject_ID"]: "SUB-999",
            f_map["Visit_Date"]: "2025-07-04",
            f_map["Condition_Class"]: "Exemplary",
            f_map["Clinical_Notes"]: "All biomarkers stable",
        }
    ]

    mappings = [
        FieldMapping(
            mapping_id=f"m_{f.field_id}",
            target_field_id=f.field_id,
            target_name=f.original_name,
        )
        for f in tgt_schema.fields
    ]

    generator = WordGenerator(template_path)
    res = generator.generate(
        output_path=out_path,
        processed_records=processed_records,
        mappings=mappings,
        target_schema=tgt_schema,
        strategy_override="replace_placeholders",
    )

    assert os.path.exists(out_path)
    doc = Document(out_path)
    full_text = " ".join(p.text for p in doc.paragraphs)
    assert "Dr. Elizabeth Shaw" in full_text
    assert "SUB-999" in full_text
    assert "{{Full_Legal_Name}}" not in full_text
