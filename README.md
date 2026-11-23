# excel-to-word-conv



\# Smart Document Converter



Aplikasi desktop untuk membantu mengonversi data dari spreadsheet Excel menjadi dokumen Microsoft Word menggunakan template dokumen dan proses pemetaan data.



Smart Document Converter dirancang untuk menyederhanakan pekerjaan pembuatan dokumen berulang, seperti dokumen administrasi, laporan, formulir, surat, dan dokumen berbasis data.



\## Overview



Smart Document Converter menggabungkan backend Python untuk analisis dan pemrosesan dokumen, frontend React untuk antarmuka pengguna, serta Tauri untuk integrasi aplikasi desktop.



\*\*Tujuan utama:\*\*

\- Mengurangi proses copy-paste data secara manual.

\- Mempermudah penggunaan data Excel untuk mengisi dokumen Word.

\- Membantu proses analisis, pemetaan field, transformasi, dan validasi data.

\- Menyediakan workflow konversi dokumen yang lebih terstruktur.



\## Features



\### Excel Processing

\- Analisis struktur workbook Excel.

\- Identifikasi header dan field data.

\- Deteksi variasi struktur spreadsheet.

\- Mendukung penanganan struktur data dan kasus edge tertentu.



\### Word Template Processing

\- Analisis struktur template Word.

\- Identifikasi field atau placeholder dokumen.

\- Pemrosesan template DOCX.

\- Dukungan manipulasi struktur dokumen melalui OOXML utilities.



\### Data Mapping

\- Pemetaan field Excel dengan field Word.

\- Normalisasi nama field.

\- Fuzzy matching untuk membantu pencocokan field.

\- Dukungan synonym dan pemeriksaan kompatibilitas tipe data.

\- Komponen analisis sample data untuk membantu proses mapping.



\### Conversion Workflow

\- Upload dan analisis file.

\- Pemilihan data/record.

\- Mapping field.

\- Preview hasil.

\- Proses transformasi dan validasi.

\- Penyelesaian serta pengelolaan riwayat konversi.



\### Desktop Application

\- Frontend berbasis React dan TypeScript.

\- Backend Python.

\- Desktop integration menggunakan Tauri.

\- Pengembangan frontend menggunakan Vite.



\## Technology Stack



| Component | Technology |

|---|---|

| Backend | Python |

| API | FastAPI |

| Frontend | React |

| Language | TypeScript |

| Frontend build tool | Vite |

| Styling | Tailwind CSS |

| Desktop framework | Tauri |

| Desktop backend | Rust |

| Excel processing | Python libraries |

| Word processing | DOCX / OOXML tools |

| Testing | pytest |



\## Architecture



```text

┌──────────────────────────────────────┐

│          Desktop Application        │

│                Tauri                │

├──────────────────────────────────────┤

│           React + TypeScript        │

│         Frontend / User UI          │

├──────────────────────────────────────┤

│            Python Backend           │

│               FastAPI               │

├──────────────────────────────────────┤

│ Excel Analyzer │ Mapping Engine     │

│ Word Analyzer  │ Transformer         │

│ Generator      │ Validator           │

└──────────────────────────────────────┘

```



\## Project Structure



```text

smart-document-converter/

│

├── engine/

│   ├── excel/          # Excel analysis \& detection

│   ├── mapping/        # Field mapping engine

│   ├── models/         # Data models

│   ├── generator/      # Document generation

│   ├── transform/      # Data transformation

│   ├── validator/      # Validation

│   └── word/           # Word document analysis

│

├── frontend/

│   ├── src/

│   │   ├── components/

│   │   ├── screens/

│   │   ├── services/

│   │   └── types/

│   └── package.json

│

├── src-tauri/

│   └── src/            # Desktop integration

│

├── tests/

│   ├── unit/

│   ├── integration/

│   ├── edge\_cases/

│   ├── dynamic\_schemas/

│   ├── golden/

│   └── fixtures/

│

├── scripts/

├── requirements.txt

├── README.md

└── .github/

&#x20;   └── workflows/

```



\## Requirements



Untuk menjalankan aplikasi dalam mode development:



\- Windows 10/11

\- Python 3.10+ (sesuaikan dengan versi yang kompatibel dengan dependencies)

\- Node.js dan npm

\- Git



Untuk membangun desktop application menggunakan Tauri, dibutuhkan toolchain Rust serta dependencies build Tauri yang sesuai dengan sistem operasi.



\## Installation



\### 1. Clone Repository



```bash

git clone <YOUR\_REPOSITORY\_URL>

cd <REPOSITORY\_FOLDER>

```



\### 2. Setup Python Backend



Windows:



```cmd

py -m venv .venv

.venv\\Scripts\\activate

py -m pip install --upgrade pip

py -m pip install -r requirements.txt

```



\### 3. Setup Frontend



```cmd

cd frontend

npm install

```



\## Running in Development



\### Start Backend



Dari root project:



```cmd

py -m engine.cli --serve --port 8000

```



Backend akan dijalankan pada port `8000` (sesuai konfigurasi CLI).



\### Start Frontend



Buka terminal kedua:



```cmd

cd frontend

npm run dev

```



Vite akan menampilkan alamat lokal untuk membuka frontend melalui browser.



> Backend harus berjalan agar frontend dapat berkomunikasi dengan API.



\## Running Tests



Dari root project:



```cmd

py -m pytest

```



Untuk menjalankan test dengan output yang lebih detail:



```cmd

py -m pytest -v

```



Test suite mencakup unit tests, integration tests, edge cases, dynamic schemas, dan golden output tests.



\## Build \& Packaging



Project menyediakan scripts untuk menjalankan aplikasi dan membantu proses packaging.



Folder `scripts/` berisi tools terkait:



\- `run\_app.py` — menjalankan aplikasi.

\- `package\_app.py` — proses packaging aplikasi.

\- `benchmark\_ml.py` — benchmark komponen terkait machine learning.

\- `create\_all\_docs.py` — utilitas pembuatan dokumen.



Proses packaging desktop memerlukan environment build yang sesuai dengan konfigurasi Tauri dan Python.



\## Development



Kontribusi dan pengembangan dilakukan pada komponen terpisah:



\- `engine/` untuk backend logic dan document processing.

\- `frontend/` untuk user interface.

\- `src-tauri/` untuk desktop integration.

\- `tests/` untuk quality assurance.



Sebelum melakukan perubahan, disarankan menjalankan test suite dan memastikan aplikasi dapat berjalan pada environment lokal.



\## Roadmap



\- \[ ] Meningkatkan akurasi automatic field mapping.

\- \[ ] Memperluas dukungan struktur Excel yang bervariasi.

\- \[ ] Meningkatkan preview hasil dokumen.

\- \[ ] Memperkuat validasi sebelum proses konversi.

\- \[ ] Meningkatkan pengalaman instalasi dan packaging desktop.

\- \[ ] Memperluas test coverage.

\- \[ ] Dokumentasi penggunaan end-user.



\## Project Status



\*\*Status: Active Development\*\*



Project ini sedang dikembangkan. Beberapa fitur, workflow, dan konfigurasi dapat berubah seiring proses pengembangan dan pengujian.



\## License



Project ini menggunakan lisensi yang tercantum pada file \[`LICENSE`](LICENSE).



\---



Made to simplify repetitive document workflows.



