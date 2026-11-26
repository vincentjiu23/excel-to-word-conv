
"""
Unit tests for digital PDF template analyzer and generator.
"""

import fitz
import pytest

from engine.pdf_template import (
    PDFTemplateAnalyzer,
    PDFTemplateGenerator,
)


def create_pdf(path, pages):
    """Create a digital PDF fixture."""

    document = fitz.open()

    for page_content in pages:
        page = document.new_page()

        y_position = 80

        for text in page_content:
            page.insert_text(
                (60, y_position),
                text,
                fontsize=12,
                fontname="helv",
            )
            y_position += 35

    document.save(str(path))
    document.close()

    return path


def test_pdf_analyzer_detects_placeholders(tmp_path):
    """Analyzer detects digital PDF placeholders."""

    pdf_path = create_pdf(
        tmp_path / "template.pdf",
        [
            [
                "Nama: {{nama}}",
                "Alamat: {{alamat}}",
            ]
        ],
    )

    analyzer = PDFTemplateAnalyzer()

    schema = analyzer.analyze(str(pdf_path))

    detected_names = {
        field.original_name
        for field in schema.fields
    }

    assert "nama" in detected_names
    assert "alamat" in detected_names

    assert schema.structure.placeholder_count == 2
    assert schema.structure.sections_count == 1


def test_pdf_generator_replaces_placeholder(tmp_path):
    """Generator replaces PDF placeholders with Excel values."""

    template_path = create_pdf(
        tmp_path / "template.pdf",
        [
            [
                "Nama: {{nama}}",
                "Nilai: {{nilai}}",
            ]
        ],
    )

    output_path = tmp_path / "output.pdf"

    generator = PDFTemplateGenerator()

    result = generator.generate(
        template_path=str(template_path),
        output_path=str(output_path),
        row_data={
            "field_nama": "Siti",
            "field_nilai": 0,
        },
        mappings=[
            {
                "placeholder": "{{nama}}",
                "page_number": 1,
                "font_size": 12,
                "excel_column": "field_nama",
                "matched": True,
            },
            {
                "placeholder": "{{nilai}}",
                "page_number": 1,
                "font_size": 12,
                "excel_column": "field_nilai",
                "matched": True,
            },
        ],
    )

    assert output_path.exists()
    assert result["status"] == "success"
    assert result["replacements_count"] == 2

    with fitz.open(str(output_path)) as document:
        extracted_text = document[0].get_text()

    assert "Siti" in extracted_text
    assert "0" in extracted_text

    assert "{{nama}}" not in extracted_text
    assert "{{nilai}}" not in extracted_text


def test_pdf_generator_preserves_multiple_pages(tmp_path):
    """Generator preserves all original template pages."""

    template_path = create_pdf(
        tmp_path / "multipage.pdf",
        [
            ["Nama: {{nama}}"],
            ["Nomor: {{nomor}}"],
        ],
    )

    output_path = tmp_path / "multipage_output.pdf"

    generator = PDFTemplateGenerator()

    result = generator.generate(
        template_path=str(template_path),
        output_path=str(output_path),
        row_data={
            "nama": "Andi",
            "nomor": "001",
        },
        mappings=[
            {
                "placeholder": "{{nama}}",
                "page_number": 1,
                "font_size": 12,
                "excel_column": "nama",
                "matched": True,
            },
            {
                "placeholder": "{{nomor}}",
                "page_number": 2,
                "font_size": 12,
                "excel_column": "nomor",
                "matched": True,
            },
        ],
    )

    assert result["pages_written"] == 2

    with fitz.open(str(output_path)) as document:
        assert len(document) == 2

        page_one_text = document[0].get_text()
        page_two_text = document[1].get_text()

    assert "Andi" in page_one_text
    assert "001" in page_two_text


def test_pdf_generator_rejects_missing_placeholder(tmp_path):
    """Generator reports placeholders that cannot be found."""

    template_path = create_pdf(
        tmp_path / "missing.pdf",
        [
            ["Nama: {{nama}}"],
        ],
    )

    output_path = tmp_path / "missing_output.pdf"

    generator = PDFTemplateGenerator()

    with pytest.raises(ValueError, match="placeholder"):
        generator.generate(
            template_path=str(template_path),
            output_path=str(output_path),
            row_data={
                "nama": "Budi",
            },
            mappings=[
                {
                    "placeholder": "{{alamat}}",
                    "page_number": 1,
                    "font_size": 12,
                    "excel_column": "nama",
                    "matched": True,
                },
            ],
        )


def test_pdf_analyzer_rejects_scanned_or_empty_pdf(tmp_path):
    """Analyzer rejects PDFs without extractable digital text."""

    pdf_path = tmp_path / "empty.pdf"

    document = fitz.open()
    document.new_page()
    document.save(str(pdf_path))
    document.close()

    analyzer = PDFTemplateAnalyzer()

    with pytest.raises(ValueError, match="OCR belum didukung"):
        analyzer.analyze(str(pdf_path))
