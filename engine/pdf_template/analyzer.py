
from pathlib import Path
import re
import fitz

from ..models.field import DataType, FieldModel, SourceType
from ..models.schema import TargetDocumentStructure, TargetSchema


class PDFTemplateAnalyzer:
    """Menganalisis template PDF digital dan mendeteksi placeholder."""

    PLACEHOLDER_PATTERN = re.compile(
        r"\{\{\s*([a-zA-Z0-9_\s.-]+?)\s*\}\}"
    )

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"[\s_-]+", "_", value.strip().lower())

    def analyze_document(self, pdf_path: str) -> dict:
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF tidak ditemukan: {pdf_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError("File template harus berformat PDF.")

        try:
            document = fitz.open(path)
        except Exception as exc:
            raise ValueError(f"Gagal membaca PDF: {exc}") from exc

        if document.is_encrypted:
            document.close()
            raise ValueError("PDF terenkripsi atau membutuhkan password.")

        pages = []

        try:
            for page_number, page in enumerate(document, start=1):
                text_blocks = []

                # Gabungkan span dalam satu baris agar placeholder
                # yang terpecah antar-span tetap dapat dideteksi.
                page_dict = page.get_text("dict")

                for block in page_dict.get("blocks", []):
                    if block.get("type") != 0:
                        continue

                    for line in block.get("lines", []):
                        spans = line.get("spans", [])
                        text = "".join(
                            span.get("text", "") for span in spans
                        )

                        if not text.strip():
                            continue

                        valid_spans = [
                            span for span in spans
                            if span.get("text", "").strip()
                        ]

                        if not valid_spans:
                            continue

                        x0 = min(s["bbox"][0] for s in valid_spans)
                        y0 = min(s["bbox"][1] for s in valid_spans)
                        x1 = max(s["bbox"][2] for s in valid_spans)
                        y1 = max(s["bbox"][3] for s in valid_spans)

                        text_blocks.append({
                            "text": text,
                            "bbox": [x0, y0, x1, y1],
                            "font": valid_spans[0].get("font", ""),
                            "font_size": max(
                                float(s.get("size", 0))
                                for s in valid_spans
                            ),
                        })

                pages.append({
                    "page_number": page_number,
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "text_blocks": text_blocks,
                })

        finally:
            document.close()

        all_text = [
            block["text"]
            for page in pages
            for block in page["text_blocks"]
        ]

        return {
            "file_name": path.name,
            "file_path": str(path.resolve()),
            "page_count": len(pages),
            "is_digital": any(all_text),
            "pages": pages,
            "detected_text": all_text,
        }

    def analyze(self, pdf_path: str) -> TargetSchema:
        analysis = self.analyze_document(pdf_path)

        if not analysis["is_digital"]:
            raise ValueError(
                "PDF tidak memiliki teks digital yang dapat dibaca. "
                "Kemungkinan PDF berupa hasil scan. OCR belum didukung."
            )

        discovered = {}

        for page in analysis["pages"]:
            for block in page["text_blocks"]:
                for match in self.PLACEHOLDER_PATTERN.finditer(
                    block["text"]
                ):
                    name = match.group(1).strip()

                    if not name:
                        continue

                    occurrence = {
                        "page_number": page["page_number"],
                        "bbox": block["bbox"],
                        "placeholder": match.group(0),
                        "font": block["font"],
                        "font_size": block["font_size"],
                    }

                    discovered.setdefault(name, []).append(occurrence)

        fields = []

        for index, (name, occurrences) in enumerate(
            discovered.items()
        ):
            safe_name = re.sub(
                r"[^a-zA-Z0-9_]", "_", name.lower()
            )

            fields.append(
                FieldModel(
                    field_id=f"pdf_ph_{index}_{safe_name}",
                    original_name=name,
                    normalized_name=self._normalize(name),
                    data_type=DataType.STRING,
                    source_type=SourceType.PDF,
                    location={
                        "type": "pdf_placeholder",
                        "page_number": occurrences[0]["page_number"],
                        "bbox": occurrences[0]["bbox"],
                    },
                    sample_values=[name],
                    confidence=0.95,
                    metadata={
                        "occurrences": occurrences,
                        "placeholder_count": len(occurrences),
                    },
                )
            )

        warnings = []

        if not fields:
            warnings.append(
                "Tidak ditemukan placeholder {{nama_field}} "
                "pada template PDF."
            )

        structure = TargetDocumentStructure(
            has_tables=False,
            table_count=0,
            paragraph_count=len(analysis["detected_text"]),
            placeholder_count=sum(
                len(items) for items in discovered.values()
            ),
            has_headers_footers=False,
            sections_count=1,
            unsupported_features_detected=[
                "PDF template saat ini mendukung placeholder digital "
                "berformat {{nama_field}}."
            ],
        )

        return TargetSchema(
            file_path=analysis["file_path"],
            structure=structure,
            tables=[],
            fields=fields,
            candidate_strategies=["replace_placeholders"],
            recommended_strategy="replace_placeholders",
            warnings=warnings,
        )
