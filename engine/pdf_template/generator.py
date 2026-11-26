
"""
Digital PDF Template Generator.

Features:
- Replace {{placeholder}} using mapped Excel data.
- Preserve original PDF pages.
- Support multiple placeholders and repeated occurrences.
- Automatically fit replacement text into the original text area.
- Preserve numeric zero and other valid values.
- Report missing placeholders.
- Generate an individual PDF for each Excel record.
- Designed to be used with a batch PDF merger.
"""

from pathlib import Path
from typing import Any
import fitz


class PDFTemplateGenerator:
    """Mengisi placeholder PDF digital berdasarkan data Excel."""

    MIN_FONT_SIZE = 4.0
    MAX_FONT_SIZE = 12.0

    @staticmethod
    def _format_value(value: Any) -> str:
        """
        Mengubah nilai menjadi teks tanpa menghilangkan angka nol.
        """

        if value is None:
            return ""

        if isinstance(value, bool):
            return "Ya" if value else "Tidak"

        if isinstance(value, (dict, list, tuple)):
            return str(value)

        return str(value)

    def _fit_text(
        self,
        page,
        rect,
        value: str,
        font_size: float,
    ) -> float:
        """
        Mencari ukuran font yang memungkinkan teks masuk
        ke dalam area placeholder.
        """

        if not value:
            return font_size

        # Beri sedikit ruang agar teks tidak menempel pada tepi.
        text_rect = fitz.Rect(rect)

        text_rect.x0 += 1
        text_rect.x1 -= 1
        text_rect.y0 += 1
        text_rect.y1 -= 1

        if text_rect.width <= 0 or text_rect.height <= 0:
            raise ValueError(
                "Area placeholder terlalu kecil untuk diisi."
            )

        initial_size = min(
            max(float(font_size), self.MIN_FONT_SIZE),
            self.MAX_FONT_SIZE,
        )

        current_size = initial_size

        while current_size >= self.MIN_FONT_SIZE:

            result = page.insert_textbox(
                text_rect,
                value,
                fontsize=current_size,
                fontname="helv",
                color=(0, 0, 0),
                align=0,
                overlay=True,
            )

            if result >= 0:
                return current_size

            current_size -= 0.5

        raise ValueError(
            "Teks terlalu panjang untuk area placeholder. "
            "Perbesar area pada template PDF atau persingkat nilai "
            f"yang dimasukkan: {value[:80]}"
        )

    def generate(
        self,
        template_path: str,
        output_path: str,
        row_data: dict[str, Any],
        mappings: list[dict],
    ) -> dict:

        template = Path(template_path)
        output = Path(output_path)

        # -----------------------------------------------------
        # VALIDATE FILES
        # -----------------------------------------------------

        if not template.exists():
            raise FileNotFoundError(
                f"Template PDF tidak ditemukan: {template}"
            )

        if template.suffix.lower() != ".pdf":
            raise ValueError(
                "Template harus berupa PDF."
            )

        if output.suffix.lower() != ".pdf":
            raise ValueError(
                "Output harus berformat PDF."
            )

        if not isinstance(row_data, dict):
            raise ValueError(
                "Data record harus berupa dictionary."
            )

        if not isinstance(mappings, list):
            raise ValueError(
                "Mappings harus berupa list."
            )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -----------------------------------------------------
        # OPEN TEMPLATE
        # -----------------------------------------------------

        try:
            document = fitz.open(str(template))

        except Exception as exc:
            raise ValueError(
                f"Gagal membuka template PDF: {exc}"
            ) from exc

        if document.is_encrypted:

            document.close()

            raise ValueError(
                "PDF terenkripsi tidak didukung."
            )

        if len(document) == 0:

            document.close()

            raise ValueError(
                "Template PDF tidak memiliki halaman."
            )

        replacements = []
        missing_placeholders = []
        page_redactions = {}

        try:

            # ================================================
            # FIND PLACEHOLDERS
            # ================================================

            for mapping in mappings:

                if not mapping.get("matched"):
                    continue

                placeholder = mapping.get("placeholder")

                column = mapping.get("excel_column")

                if not placeholder or not column:
                    continue

                if column not in row_data:
                    missing_placeholders.append({
                        "placeholder": placeholder,
                        "reason": "Field tidak ditemukan dalam data record.",
                    })
                    continue

                value = self._format_value(
                    row_data[column]
                )

                try:
                    page_index = (
                        int(mapping.get("page_number", 0)) - 1
                    )
                except (TypeError, ValueError):
                    continue

                if (
                    page_index < 0
                    or page_index >= len(document)
                ):
                    missing_placeholders.append({
                        "placeholder": placeholder,
                        "reason": "Nomor halaman tidak valid.",
                    })
                    continue

                page = document[page_index]

                # Cari posisi placeholder di halaman.
                matches = page.search_for(placeholder)

                if not matches:

                    missing_placeholders.append({
                        "placeholder": placeholder,
                        "page": page_index + 1,
                        "reason": (
                            "Placeholder tidak ditemukan oleh "
                            "pencarian teks PDF."
                        ),
                    })

                    continue

                for rect in matches:

                    # Hindari memproses area yang sama dua kali.
                    rect_key = (
                        page_index,
                        round(rect.x0, 2),
                        round(rect.y0, 2),
                        round(rect.x1, 2),
                        round(rect.y1, 2),
                    )

                    if any(
                        item["rect_key"] == rect_key
                        for item in replacements
                    ):
                        continue

                    replacement = {
                        "page": page_index,
                        "rect": fitz.Rect(rect),
                        "rect_key": rect_key,
                        "value": value,
                        "font_size": mapping.get(
                            "font_size",
                            10,
                        ),
                        "placeholder": placeholder,
                    }

                    replacements.append(replacement)

                    page_redactions.setdefault(
                        page_index,
                        [],
                    ).append(fitz.Rect(rect))

            # ================================================
            # CHECK MISSING PLACEHOLDERS
            # ================================================

            if missing_placeholders:

                missing_names = ", ".join(
                    item["placeholder"]
                    for item in missing_placeholders
                )

                raise ValueError(
                    "Sebagian placeholder tidak dapat ditemukan "
                    "atau tidak memiliki data mapping: "
                    f"{missing_names}"
                )

            if not replacements:

                raise ValueError(
                    "Tidak ada placeholder PDF yang berhasil ditemukan. "
                    "Pastikan template menggunakan placeholder "
                    "{{nama_field}} dan mapping sudah benar."
                )

            # ================================================
            # APPLY REDACTIONS
            # ================================================

            for page_index, rects in page_redactions.items():

                page = document[page_index]

                for rect in rects:

                    page.add_redact_annot(
                        rect,
                        fill=(1, 1, 1),
                    )

                page.apply_redactions()

            # ================================================
            # INSERT REPLACEMENT VALUES
            # ================================================

            inserted_count = 0

            for item in replacements:

                page = document[item["page"]]

                self._fit_text(
                    page=page,
                    rect=item["rect"],
                    value=item["value"],
                    font_size=item["font_size"],
                )

                inserted_count += 1

            # ================================================
            # SAVE OUTPUT
            # ================================================

            document.save(
                str(output),
                garbage=4,
                deflate=True,
            )

        finally:

            document.close()

        # -----------------------------------------------------
        # VERIFY OUTPUT
        # -----------------------------------------------------

        if not output.exists():

            raise RuntimeError(
                "PDF hasil tidak berhasil dibuat."
            )

        file_size = output.stat().st_size

        if file_size <= 0:

            raise RuntimeError(
                "PDF hasil kosong."
            )

        # Periksa apakah file benar-benar dapat dibuka.
        try:

            with fitz.open(str(output)) as result:

                output_pages = len(result)

        except Exception as exc:

            raise RuntimeError(
                f"PDF hasil tidak dapat dibuka: {exc}"
            ) from exc

        return {

            "output_path": str(output.resolve()),

            "file_size_bytes": file_size,

            "output_format": "pdf",

            "pages_written": output_pages,

            "replacements_count": inserted_count,

            "missing_placeholders": missing_placeholders,

            "status": "success",

        }
