"""
Unit tests for data selection, filtering, and transformations.
"""

from datetime import date
import pytest
from engine.models.mapping import FieldMapping, FieldTransformation
from engine.transform.transformer import DataTransformer


def test_value_transformations():
    # Trim
    t_trim = [FieldTransformation(transform_type="trim")]
    assert DataTransformer.transform_value("  hello world  ", t_trim) == "hello world"

    # Uppercase
    t_upper = [FieldTransformation(transform_type="uppercase")]
    assert DataTransformer.transform_value("john doe", t_upper) == "JOHN DOE"

    # Date formatting
    t_date = [FieldTransformation(transform_type="date_format", parameters={"format": "%d-%m-%Y"})]
    assert DataTransformer.transform_value(date(2025, 12, 31), t_date) == "31-12-2025"

    # Number formatting with decimals and thousands separator
    t_num = [FieldTransformation(transform_type="number_format", parameters={"decimals": 2, "thousands_separator": True})]
    assert DataTransformer.transform_value(1234567.891, t_num) == "1,234,567.89"

    # Default value for empty
    t_def = [FieldTransformation(transform_type="default_value", parameters={"value": "N/A"})]
    assert DataTransformer.transform_value(None, t_def) == "N/A"
    assert DataTransformer.transform_value("", t_def) == "N/A"


def test_process_record_non_mutating():
    raw_record = {
        "src_id": "AST-100",
        "src_val": 45000,
    }
    mapping1 = FieldMapping(
        mapping_id="m1",
        target_field_id="tgt_code",
        target_name="Code",
        source_field_id="src_id",
        transformations=[FieldTransformation(transform_type="uppercase")],
    )
    mapping2 = FieldMapping(
        mapping_id="m2",
        target_field_id="tgt_amt",
        target_name="Amount",
        source_field_id="src_val",
        transformations=[FieldTransformation(transform_type="number_format", parameters={"decimals": 0})],
    )

    processed = DataTransformer.process_record(raw_record, [mapping1, mapping2])

    assert processed["tgt_code"] == "AST-100"
    assert processed["tgt_amt"] == "45,000"

    # Source record must remain completely untouched
    assert raw_record["src_val"] == 45000
