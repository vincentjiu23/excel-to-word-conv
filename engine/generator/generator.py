"""
Word Document Generator.
Uses the original template as base, preserving styling, margins, fonts, and headers.
Never overwrites the original template file.
"""

import os
from typing import Any, Dict, List, Optional
from docx import Document

from ..models.mapping import FieldMapping
from ..models.schema import TargetSchema
from .strategies import (
    apply_fill_blank_rows,
    apply_label_value_form,
    apply_placeholder_replacement,
    apply_repeat_template_row,
)


class WordGenerator:
    def __init__(self, template_path: str):
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template path not found: {template_path}")
        self.template_path = template_path

    def generate(
        self,
        output_path: str,
        processed_records: List[Dict[str, Any]],
        mappings: List[FieldMapping],
        target_schema: TargetSchema,
        strategy_override: Optional[str] = None,
        table_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Executes document conversion and saves output to a new file.
        """
        # Ensure output directory exists
        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # Ensure we do not overwrite template directly unless explicitly identical
        if os.path.abspath(output_path) == os.path.abspath(self.template_path):
            base, ext = os.path.splitext(output_path)
            output_path = f"{base}_converted{ext}"

        doc = Document(self.template_path)
        strategy = strategy_override or target_schema.recommended_strategy or "repeat_template_row"

        # Apply strategy
        if strategy == "replace_placeholders":
            apply_placeholder_replacement(doc, processed_records, mappings)

        elif strategy == "repeat_template_row":
            if doc.tables and table_index < len(doc.tables):
                apply_repeat_template_row(
                    doc.tables[table_index],
                    processed_records,
                    mappings,
                    target_schema,
                    table_index=table_index,
                )
            # Also apply placeholder replacement in case header/footer/paragraphs contain tokens
            apply_placeholder_replacement(doc, processed_records, mappings)

        elif strategy == "fill_existing_blank_rows":
            if doc.tables and table_index < len(doc.tables):
                apply_fill_blank_rows(
                    doc.tables[table_index],
                    processed_records,
                    mappings,
                    target_schema,
                    table_index=table_index,
                )
            apply_placeholder_replacement(doc, processed_records, mappings)

        elif strategy == "fill_label_value_form":
            if doc.tables and table_index < len(doc.tables):
                apply_label_value_form(doc.tables[table_index], processed_records, mappings)
            apply_placeholder_replacement(doc, processed_records, mappings)

        else:
            # Fallback to repeating template row or placeholder replacement
            if doc.tables:
                apply_repeat_template_row(
                    doc.tables[table_index],
                    processed_records,
                    mappings,
                    target_schema,
                    table_index=table_index,
                )
            apply_placeholder_replacement(doc, processed_records, mappings)

        # Save generated file
        doc.save(output_path)
        file_size = os.path.getsize(output_path)

        return {
            "output_path": output_path,
            "records_written": len(processed_records),
            "strategy_used": strategy,
            "table_index": table_index,
            "file_size_bytes": file_size,
        }
