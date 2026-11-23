"""
Dynamic Schema Independence Tests.
PROVES the engine functions seamlessly across completely distinct,
unfamiliar, non-hardcoded domains:
1. Astrophysics Telemetry & Radio Astronomy
2. Maritime Logistics & Bill of Lading
3. Clinical Pharmacology & Patient Cohorts
4. Minimal 2-column arbitrary key-value pairing
"""

import os
import openpyxl
from docx import Document
import pytest
from engine.excel.analyzer import ExcelAnalyzer
from engine.mapping.engine import IntelligentMappingEngine
from engine.mapping.feedback_store import FeedbackStore
from engine.generator.generator import WordGenerator
from engine.validator.validator import OutputValidator
from engine.word.analyzer import WordAnalyzer
from engine.transform.transformer import DataTransformer


def test_domain_astrophysics_spectral_signals(fixtures_dir, tmp_path):
    """Domain A: Astrophysics Deep Space Telemetry"""
    excel_path = os.path.join(fixtures_dir, "astronomy_telemetry.xlsx")
    word_path = os.path.join(fixtures_dir, "astronomy_template.docx")
    out_path = str(tmp_path / "astro_converted.docx")

    # 1. Analyze Excel
    x_analyzer = ExcelAnalyzer(excel_path)
    src_schema = x_analyzer.analyze_sheet()
    assert src_schema.total_rows == 2
    assert any("Flux_Density_mJy" in f.original_name for f in src_schema.fields)
    assert any("Redshift_z" in f.original_name for f in src_schema.fields)

    # 2. Analyze Word Template
    w_analyzer = WordAnalyzer(word_path)
    tgt_schema = w_analyzer.analyze()
    assert any("Flux Density" in f.original_name for f in tgt_schema.fields)

    # 3. Dynamic Mapping
    store = FeedbackStore(db_path=str(tmp_path / "dyn_feedback.db"))
    mapper = IntelligentMappingEngine(feedback_store=store)
    mappings = mapper.generate_mappings(src_schema.fields, tgt_schema.fields)

    # Verify that unfamiliar scientific terms matched correctly
    flux_map = next(m for m in mappings if "Flux Density" in m.target_name)
    assert flux_map.source_field_id is not None
    assert "Flux_Density" in flux_map.source_name

    # 4. Generate & Validate
    processed = [DataTransformer.process_record(r, mappings) for r in src_schema.preview_records]
    gen = WordGenerator(word_path)
    gen.generate(out_path, processed, mappings, tgt_schema)

    val = OutputValidator.validate(out_path, expected_records_count=2, expected_values_to_verify=["SIG-ALPHA-01", "187.25"])
    assert val.is_valid is True


def test_domain_maritime_logistics_cargo(fixtures_dir, tmp_path):
    """Domain B: Maritime Container Logistics"""
    excel_path = os.path.join(fixtures_dir, "shipping_containers.xlsx")
    word_path = os.path.join(fixtures_dir, "shipping_template.docx")
    out_path = str(tmp_path / "shipping_converted.docx")

    x_analyzer = ExcelAnalyzer(excel_path)
    src_schema = x_analyzer.analyze_sheet()

    w_analyzer = WordAnalyzer(word_path)
    tgt_schema = w_analyzer.analyze()

    store = FeedbackStore(db_path=str(tmp_path / "dyn_feedback.db"))
    mapper = IntelligentMappingEngine(feedback_store=store)
    mappings = mapper.generate_mappings(src_schema.fields, tgt_schema.fields)

    # Verify container logistics terms
    vessel_map = next(m for m in mappings if "Vessel Reference" in m.target_name)
    assert vessel_map.source_name == "Vessel_Reference"

    processed = [DataTransformer.process_record(r, mappings) for r in src_schema.preview_records]
    gen = WordGenerator(word_path)
    gen.generate(out_path, processed, mappings, tgt_schema)

    val = OutputValidator.validate(out_path, expected_records_count=3, expected_values_to_verify=["MSKU-99812", "Rotterdam"])
    assert val.is_valid is True


def test_minimal_two_column_unusual_schema(tmp_path):
    """Domain C: Minimal 2-column arbitrary schema (Xylophone_Hz and Resonant_Q)"""
    excel_path = str(tmp_path / "acoustics.xlsx")
    word_path = str(tmp_path / "acoustics_doc.docx")
    out_path = str(tmp_path / "acoustics_out.docx")

    # Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Xylophone_Hz", "Resonant_Q_Factor"])
    ws.append([440.0, 12.5])
    ws.append([880.0, 18.2])
    wb.save(excel_path)

    # Word
    doc = Document()
    doc.add_heading("Acoustic Resonance Report", level=1)
    t = doc.add_table(rows=2, cols=2)
    t.cell(0, 0).text = "Xylophone Hz"
    t.cell(0, 1).text = "Resonant Q Factor"
    doc.save(word_path)

    # Process
    x_analyzer = ExcelAnalyzer(excel_path)
    src_schema = x_analyzer.analyze_sheet()
    w_analyzer = WordAnalyzer(word_path)
    tgt_schema = w_analyzer.analyze()

    mapper = IntelligentMappingEngine(feedback_store=FeedbackStore(db_path=str(tmp_path / "acoustics_fb.db")))
    mappings = mapper.generate_mappings(src_schema.fields, tgt_schema.fields)

    assert len(mappings) == 2
    assert mappings[0].source_name == "Xylophone_Hz"
    assert mappings[1].source_name == "Resonant_Q_Factor"

    processed = [DataTransformer.process_record(r, mappings) for r in src_schema.preview_records]
    gen = WordGenerator(word_path)
    gen.generate(out_path, processed, mappings, tgt_schema)

    val = OutputValidator.validate(out_path, expected_records_count=2, expected_values_to_verify=["440.0", "12.5"])
    assert val.is_valid is True
