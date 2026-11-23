"""
Data selection, filtering, and transformation pipeline.
Never mutates original source records.
"""

from datetime import date, datetime
import re
from typing import Any, Dict, List, Optional
from ..models.mapping import FieldMapping, FieldTransformation


class DataTransformer:
    @staticmethod
    def transform_value(raw_val: Any, transformations: List[FieldTransformation], default_value: Optional[Any] = None) -> Any:
        """Applies configured transformations sequentially to a value."""
        val = raw_val

        # Handle empty / None first
        if val is None or str(val).strip() == "":
            if default_value is not None:
                return default_value
            # Check if default_value is defined in transformations
            for t in transformations:
                if t.transform_type == "default_value":
                    return t.parameters.get("value", "")
            return ""

        for t in transformations:
            ttype = t.transform_type
            params = t.parameters

            if ttype == "trim":
                if isinstance(val, str):
                    val = val.strip()

            elif ttype == "uppercase":
                if isinstance(val, str):
                    val = val.upper()

            elif ttype == "lowercase":
                if isinstance(val, str):
                    val = val.lower()

            elif ttype == "titlecase":
                if isinstance(val, str):
                    val = val.title()

            elif ttype == "date_format":
                target_fmt = params.get("format", "%Y-%m-%d")
                dt = None
                if isinstance(val, (datetime, date)):
                    dt = val
                elif isinstance(val, str):
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"):
                        try:
                            dt = datetime.strptime(val.strip(), fmt)
                            break
                        except ValueError:
                            continue
                if dt:
                    val = dt.strftime(target_fmt)

            elif ttype == "number_format":
                decimals = params.get("decimals", 2)
                thousands_sep = params.get("thousands_separator", True)
                try:
                    num = float(str(val).replace(",", ""))
                    if thousands_sep:
                        val = f"{num:,.{decimals}f}"
                    else:
                        val = f"{num:.{decimals}f}"
                except (ValueError, TypeError):
                    pass

            elif ttype == "prefix":
                prefix = params.get("text", "")
                val = f"{prefix}{val}"

            elif ttype == "suffix":
                suffix = params.get("text", "")
                val = f"{val}{suffix}"

            elif ttype == "replace":
                old_s = params.get("old", "")
                new_s = params.get("new", "")
                if isinstance(val, str) and old_s:
                    val = val.replace(old_s, new_s)

        return str(val) if val is not None else ""

    @staticmethod
    def process_record(
        raw_record: Dict[str, Any],
        mappings: List[FieldMapping],
    ) -> Dict[str, Any]:
        """
        Transforms a raw record into target fields according to mappings.
        Returns a dictionary mapping target_field_id to final formatted string value.
        """
        output_record: Dict[str, Any] = {}

        for mapping in mappings:
            # Check constant value override
            if mapping.constant_value is not None:
                output_record[mapping.target_field_id] = str(mapping.constant_value)
                continue

            # If no source field assigned, use default or blank
            if not mapping.source_field_id:
                output_record[mapping.target_field_id] = str(mapping.default_value) if mapping.default_value is not None else ""
                continue

            raw_val = raw_record.get(mapping.source_field_id)
            formatted = DataTransformer.transform_value(
                raw_val, mapping.transformations, default_value=mapping.default_value
            )
            output_record[mapping.target_field_id] = formatted

        return output_record

    @staticmethod
    def filter_records(
        records: List[Dict[str, Any]],
        search_query: Optional[str] = None,
        selected_indices: Optional[List[int]] = None,
    ) -> List[Tuple[int, Dict[str, Any]]]:
        """
        Filters records by search query and selection indices.
        Returns list of (original_index, record).
        """
        results: List[Tuple[int, Dict[str, Any]]] = []

        for idx, rec in enumerate(records):
            if selected_indices is not None and idx not in selected_indices:
                continue

            if search_query and search_query.strip():
                q = search_query.strip().lower()
                matches_search = any(q in str(v).lower() for v in rec.values() if v is not None)
                if not matches_search:
                    continue

            results.append((idx, rec))

        return results
