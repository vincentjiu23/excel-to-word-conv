
import re
from typing import Any


class PDFTemplateMapper:
    """
    Mendeteksi placeholder pada PDF dan menghubungkannya
    dengan nama kolom Excel.
    """

    PLACEHOLDER_PATTERN = re.compile(
        r"\{\{\s*([^{}]+?)\s*\}\}"
    )

    def detect_placeholders(self, analysis: dict) -> list[dict]:
        placeholders = []

        for page in analysis.get("pages", []):
            for block in page.get("text_blocks", []):
                text = block.get("text", "")

                for match in self.PLACEHOLDER_PATTERN.finditer(text):
                    placeholders.append({
                        "placeholder": match.group(0),
                        "field": match.group(1).strip(),
                        "page_number": page["page_number"],
                        "bbox": block["bbox"],
                        "font": block.get("font", ""),
                        "font_size": block.get("font_size", 0),
                    })

        return placeholders

    def create_mapping(
        self,
        placeholders: list[dict],
        excel_columns: list[str],
    ) -> dict:
        normalized_columns = {
            self._normalize(column): column
            for column in excel_columns
        }

        mappings = []

        for item in placeholders:
            field = item["field"]
            normalized_field = self._normalize(field)

            matched_column = normalized_columns.get(normalized_field)

            mappings.append({
                **item,
                "excel_column": matched_column,
                "matched": matched_column is not None,
            })

        return {
            "mappings": mappings,
            "total_placeholders": len(mappings),
            "matched_count": sum(
                item["matched"] for item in mappings
            ),
            "unmatched_count": sum(
                not item["matched"] for item in mappings
            ),
        }

    @staticmethod
    def _normalize(value: Any) -> str:
        value = str(value).strip().lower()
        return re.sub(r"[\s_\-]+", "", value)
