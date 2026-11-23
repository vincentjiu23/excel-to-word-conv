"""
Unit tests for Intelligent Mapping Engine.
Validates stages: Exact match, Normalization, Synonym, Fuzzy, Type, Semantic, and Learning.
"""

import os
import pytest
from engine.mapping.engine import IntelligentMappingEngine
from engine.mapping.feedback_store import FeedbackStore
from engine.mapping.normalizer import normalize_field_name
from engine.mapping.synonyms import SynonymRegistry
from engine.models.field import DataType, FieldModel, SourceType
from engine.models.mapping import MappingStatus


def test_normalization_and_abbreviations():
    assert normalize_field_name("Qty_Shipped-Total") == "quantity shipped total"
    assert normalize_field_name("Emp_DOB") == "emp date of birth"
    assert normalize_field_name("ITEM_AMT_USD") == "item amount usd"


def test_synonym_registry():
    registry = SynonymRegistry()
    assert registry.are_synonyms("cost", "price") is True
    assert registry.are_synonyms("quantity", "units") is True
    assert registry.are_synonyms("status", "state") is True
    assert registry.are_synonyms("banana", "spaceship") is False


def test_exact_and_normalized_matching(tmp_path):
    store = FeedbackStore(db_path=str(tmp_path / "test_feedback.db"))
    engine = IntelligentMappingEngine(feedback_store=store)

    src1 = FieldModel(
        field_id="s1",
        original_name="Patient_Name",
        normalized_name="patient name",
        data_type=DataType.STRING,
        source_type=SourceType.EXCEL,
    )
    src2 = FieldModel(
        field_id="s2",
        original_name="Visit_Date",
        normalized_name="visit date",
        data_type=DataType.DATE,
        source_type=SourceType.EXCEL,
    )

    tgt1 = FieldModel(
        field_id="t1",
        original_name="Patient Name",
        normalized_name="patient name",
        data_type=DataType.STRING,
        source_type=SourceType.WORD,
    )
    tgt2 = FieldModel(
        field_id="t2",
        original_name="Visit Date",
        normalized_name="visit date",
        data_type=DataType.DATE,
        source_type=SourceType.WORD,
    )

    mappings = engine.generate_mappings([src1, src2], [tgt1, tgt2])
    assert len(mappings) == 2

    m1 = next(m for m in mappings if m.target_field_id == "t1")
    assert m1.source_field_id == "s1"
    assert m1.status in (MappingStatus.EXACT_MATCH, MappingStatus.HIGH_CONFIDENCE)
    assert m1.confidence >= 0.90

    m2 = next(m for m in mappings if m.target_field_id == "t2")
    assert m2.source_field_id == "s2"
    assert m2.status in (MappingStatus.EXACT_MATCH, MappingStatus.HIGH_CONFIDENCE)


def test_synonym_and_fuzzy_matching(tmp_path):
    store = FeedbackStore(db_path=str(tmp_path / "test_feedback.db"))
    engine = IntelligentMappingEngine(feedback_store=store)

    src = FieldModel(
        field_id="s_qty",
        original_name="Units_Shipped",
        normalized_name="units shipped",
        data_type=DataType.INTEGER,
        source_type=SourceType.EXCEL,
        sample_values=[10, 25, 40],
    )
    tgt = FieldModel(
        field_id="t_qty",
        original_name="Quantity Shipped",
        normalized_name="quantity shipped",
        data_type=DataType.INTEGER,
        source_type=SourceType.WORD,
    )

    mappings = engine.generate_mappings([src], [tgt])
    assert len(mappings) == 1
    m = mappings[0]
    assert m.source_field_id == "s_qty"
    assert m.confidence >= 0.75
    assert m.status in (MappingStatus.RECOMMENDED, MappingStatus.HIGH_CONFIDENCE)


def test_feedback_store_learning_boost(tmp_path):
    store = FeedbackStore(db_path=str(tmp_path / "test_feedback.db"))
    # Pre-record user confirmation for a custom non-obvious mapping
    store.record_confirmed_mapping("col_alpha", "Target Beta")
    store.record_confirmed_mapping("col_alpha", "Target Beta")

    affinity = store.get_historical_affinity("col_alpha", "Target Beta")
    assert affinity > 0.10

    engine = IntelligentMappingEngine(feedback_store=store)
    src = FieldModel(
        field_id="s_alpha",
        original_name="col_alpha",
        normalized_name="col alpha",
        data_type=DataType.STRING,
        source_type=SourceType.EXCEL,
    )
    tgt = FieldModel(
        field_id="t_beta",
        original_name="Target Beta",
        normalized_name="target beta",
        data_type=DataType.STRING,
        source_type=SourceType.WORD,
    )

    mappings = engine.generate_mappings([src], [tgt])
    assert len(mappings) == 1
    m = mappings[0]
    assert "historical" in m.reason.lower()
