"""
Synthetic test fixtures generator for multi-domain dynamic schema testing.
Generates realistic, completely distinct Excel workbooks and Word templates.
Zero dependence on fixed business models.
"""

import os
from datetime import date, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


def create_all_fixtures(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Clinical Medical Dataset (Domain A)
    wb_med = openpyxl.Workbook()
    ws_med = wb_med.active
    ws_med.title = "PatientRecords"
    med_headers = ["Subject_ID", "Full_Legal_Name", "Systolic_BP", "Diastolic_BP", "Visit_Date", "Condition_Class", "Clinical_Notes"]
    ws_med.append(med_headers)
    ws_med.append(["SUB-1001", "Dr. Alice Morgan", 120, 80, date(2025, 3, 15), "Normotensive", "Routine checkup; normal findings"])
    ws_med.append(["SUB-1002", "Bob Vance", 145, 92, date(2025, 4, 10), "Stage 1 Hypertension", "Advised sodium reduction"])
    ws_med.append(["SUB-1003", "Clara Oswald", 118, 76, date(2025, 5, 22), "Optimal", "Clear clearance"])
    wb_med.save(os.path.join(output_dir, "medical_records.xlsx"))

    # Word Template for Clinical Medical (Table + repeating row)
    doc_med = Document()
    doc_med.add_heading("Clinical Examination Summary", level=1)
    doc_med.add_paragraph("This clinical assessment summarizes the cohort outcomes.")
    table_med = doc_med.add_table(rows=2, cols=7)
    table_med.style = "Table Grid"
    for idx, h in enumerate(["Subject ID", "Full Legal Name", "Systolic BP", "Diastolic BP", "Visit Date", "Condition Class", "Clinical Notes"]):
        table_med.cell(0, idx).text = h
    # Template row with sample formatting
    for idx in range(7):
        table_med.cell(1, idx).text = ""
    doc_med.save(os.path.join(output_dir, "medical_template.docx"))

    # 2. Logistics Shipping Containers (Domain B)
    wb_ship = openpyxl.Workbook()
    ws_ship = wb_ship.active
    ws_ship.title = "CargoManifest"
    ship_headers = ["Container_Code", "Vessel_Reference", "Tare_Weight_KG", "Gross_Weight_KG", "Origin_Port", "Destination_Port", "Departure_Date"]
    ws_ship.append(ship_headers)
    ws_ship.append(["MSKU-99812", "Ever Given IV", 2400.5, 28500.0, "Rotterdam", "Singapore", date(2025, 1, 12)])
    ws_ship.append(["TGHU-44102", "CMA CGM Marco Polo", 2150.0, 31200.75, "Shanghai", "Los Angeles", date(2025, 2, 18)])
    ws_ship.append(["HLXU-88391", "Hapag-Lloyd Express", 2300.0, 19450.2, "Hamburg", "Dubai", date(2025, 3, 5)])
    wb_ship.save(os.path.join(output_dir, "shipping_containers.xlsx"))

    doc_ship = Document()
    doc_ship.add_heading("International Cargo Manifest", level=1)
    table_ship = doc_ship.add_table(rows=2, cols=7)
    table_ship.style = "Table Grid"
    for idx, h in enumerate(["Container Code", "Vessel Reference", "Tare Weight (KG)", "Gross Weight (KG)", "Origin Port", "Destination Port", "Departure Date"]):
        table_ship.cell(0, idx).text = h
    doc_ship.save(os.path.join(output_dir, "shipping_template.docx"))

    # 3. Astrophysics Telemetry (Domain C)
    wb_astro = openpyxl.Workbook()
    ws_astro = wb_astro.active
    ws_astro.title = "SpectralSignals"
    astro_headers = ["Signal_ID", "Right_Ascension_Deg", "Declination_Deg", "Flux_Density_mJy", "Observation_Epoch", "Redshift_z"]
    ws_astro.append(astro_headers)
    ws_astro.append(["SIG-ALPHA-01", 187.25, 12.33, 45.8, "2025-06-01", 0.052])
    ws_astro.append(["SIG-BETA-09", 42.11, -8.45, 120.4, "2025-06-02", 1.284])
    wb_astro.save(os.path.join(output_dir, "astronomy_telemetry.xlsx"))

    doc_astro = Document()
    doc_astro.add_heading("Deep Space Radio Astronomy Observation", level=1)
    table_astro = doc_astro.add_table(rows=2, cols=6)
    table_astro.style = "Table Grid"
    for idx, h in enumerate(["Signal ID", "Right Ascension (Deg)", "Declination (Deg)", "Flux Density (mJy)", "Observation Epoch", "Redshift (z)"]):
        table_astro.cell(0, idx).text = h
    doc_astro.save(os.path.join(output_dir, "astronomy_template.docx"))

    # 4. Header on Row 4 (Leading banner & blanks)
    wb_banner = openpyxl.Workbook()
    ws_banner = wb_banner.active
    ws_banner.title = "OffsetSheet"
    ws_banner.cell(row=1, column=1, value="ACME CORP INTERNAL CONSOLIDATED REPORT")
    ws_banner.merge_cells("A1:E1")
    # Rows 2 and 3 are blank
    ws_banner.cell(row=4, column=1, value="Asset_Tag")
    ws_banner.cell(row=4, column=2, value="Location_Zone")
    ws_banner.cell(row=4, column=3, value="Acquisition_Cost")
    ws_banner.cell(row=4, column=4, value="In_Service")
    ws_banner.append(["AST-001", "Zone North", 12500, True])
    ws_banner.append(["AST-002", "Zone East", 8400, False])
    wb_banner.save(os.path.join(output_dir, "header_on_row_4.xlsx"))

    # 5. Duplicate and empty headers
    wb_dups = openpyxl.Workbook()
    ws_dups = wb_dups.active
    # Column 1: Code, Column 2: empty, Column 3: Code, Column 4: Notes
    ws_dups.cell(row=1, column=1, value="Item_Code")
    ws_dups.cell(row=1, column=2, value="")  # Empty header
    ws_dups.cell(row=1, column=3, value="Item_Code")  # Duplicate
    ws_dups.cell(row=1, column=4, value="Notes")
    ws_dups.append(["ITM-1", "Auxiliary", "ITM-1-ALT", "Verified"])
    ws_dups.append(["ITM-2", "Primary", "ITM-2-ALT", "Pending"])
    wb_dups.save(os.path.join(output_dir, "duplicate_and_empty_headers.xlsx"))

    # 6. Formulas and mixed formats
    wb_forms = openpyxl.Workbook()
    ws_forms = wb_forms.active
    ws_forms.append(["Product_Name", "Unit_Price", "Units_Sold", "Revenue_Total"])
    ws_forms.append(["Widget Alpha", 15.5, 100, "=B2*C2"])
    ws_forms.append(["Widget Beta", 25.0, 50, "=B3*C3"])
    wb_forms.save(os.path.join(output_dir, "formulas_and_mixed.xlsx"))

    # 7. Placeholder-based Word Document Template
    doc_ph = Document()
    doc_ph.add_heading("Certificate of Achievement", level=1)
    doc_ph.add_paragraph("This certifies that {{Full_Legal_Name}} (ID: {{Subject_ID}})")
    doc_ph.add_paragraph("has fulfilled all criteria on visit date {{Visit_Date}} with classification {{Condition_Class}}.")
    doc_ph.add_paragraph("Official clinical note recorded: {{Clinical_Notes}}.")
    doc_ph.save(os.path.join(output_dir, "placeholder_certificate.docx"))

    # 8. Multiple Tables Document Template
    doc_multi = Document()
    doc_multi.add_heading("Multi-Section Document", level=1)
    t1 = doc_multi.add_table(rows=2, cols=3)
    t1.style = "Table Grid"
    t1.cell(0, 0).text = "Department"
    t1.cell(0, 1).text = "Manager"
    t1.cell(0, 2).text = "Budget"

    doc_multi.add_paragraph("Details table follows below:")
    t2 = doc_multi.add_table(rows=2, cols=4)
    t2.style = "Table Grid"
    t2.cell(0, 0).text = "Item Code"
    t2.cell(0, 1).text = "Description"
    t2.cell(0, 2).text = "Unit Cost"
    t2.cell(0, 3).text = "Quantity"
    doc_multi.save(os.path.join(output_dir, "multi_table_template.docx"))


if __name__ == "__main__":
    fixtures_dir = os.path.join(os.path.dirname(__file__), "generated")
    create_all_fixtures(fixtures_dir)
    print(f"Fixtures successfully generated at: {fixtures_dir}")
