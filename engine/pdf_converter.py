
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class PDFConverter:
    """Convert DOCX documents to PDF using LibreOffice."""

    DEFAULT_WINDOWS_PATH = (
        r"C:\Program Files\LibreOffice\program\soffice.exe"
    )

    def __init__(
        self,
        soffice_path: Optional[str] = None,
        timeout: int = 120,
    ):
        self.soffice_path = self._resolve_soffice_path(soffice_path)
        self.timeout = timeout

    @classmethod
    def _resolve_soffice_path(
        cls,
        soffice_path: Optional[str] = None,
    ) -> str:
        candidates = [
            soffice_path,
            os.environ.get("LIBREOFFICE_PATH"),
            cls.DEFAULT_WINDOWS_PATH,
            shutil.which("soffice"),
            shutil.which("soffice.exe"),
        ]

        for candidate in candidates:
            if candidate and os.path.isfile(candidate):
                return candidate

        raise FileNotFoundError(
            "LibreOffice tidak ditemukan. Pastikan LibreOffice sudah "
            "terinstal atau atur environment variable LIBREOFFICE_PATH."
        )

    def convert(
        self,
        docx_path: str,
        pdf_path: str,
    ) -> dict:
        source = Path(docx_path).resolve()
        destination = Path(pdf_path).resolve()

        if not source.is_file():
            raise FileNotFoundError(
                f"File DOCX tidak ditemukan: {source}"
            )

        if source.suffix.lower() != ".docx":
            raise ValueError("File input harus berformat .docx")

        if destination.suffix.lower() != ".pdf":
            raise ValueError("File output harus berformat .pdf")

        destination.parent.mkdir(parents=True, exist_ok=True)

        if source == destination:
            raise ValueError("Lokasi file input dan output tidak boleh sama.")

        with tempfile.TemporaryDirectory(
            prefix="document_converter_"
        ) as temp_dir:
            temp_profile = Path(temp_dir) / "lo_profile"
            temp_profile.mkdir(parents=True, exist_ok=True)

            profile_uri = temp_profile.as_uri()

            command = [
                self.soffice_path,
                f"-env:UserInstallation={profile_uri}",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(destination.parent),
                str(source),
            ]

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError(
                    f"Konversi PDF melebihi batas waktu "
                    f"{self.timeout} detik."
                ) from exc
            except OSError as exc:
                raise RuntimeError(
                    f"Gagal menjalankan LibreOffice: {exc}"
                ) from exc

            generated_pdf = destination.parent / (
                source.stem + ".pdf"
            )

            if result.returncode != 0:
                details = (result.stderr or result.stdout or "").strip()
                raise RuntimeError(
                    "LibreOffice gagal mengonversi DOCX ke PDF. "
                    f"Detail: {details or 'Tidak ada detail tambahan.'}"
                )

            if not generated_pdf.is_file():
                raise RuntimeError(
                    "LibreOffice selesai tetapi file PDF tidak ditemukan."
                )

            if generated_pdf.resolve() != destination:
                if destination.exists():
                    destination.unlink()
                shutil.move(str(generated_pdf), str(destination))

        if not destination.is_file() or destination.stat().st_size == 0:
            raise RuntimeError("File PDF hasil konversi kosong atau tidak valid.")

        with destination.open("rb") as pdf_file:
            if pdf_file.read(5) != b"%PDF-":
                raise RuntimeError(
                    "File hasil konversi bukan dokumen PDF yang valid."
                )

        return {
            "output_path": str(destination),
            "file_size_bytes": destination.stat().st_size,
            "output_format": "pdf",
        }
