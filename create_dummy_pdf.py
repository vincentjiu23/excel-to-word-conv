
import fitz
import os

output_dir = os.path.join("tests", "fixtures", "generated")
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "medical_pdf_template.pdf")

doc = fitz.open()
page = doc.new_page(width=595, height=842)

# Header
page.insert_text(
    (50, 55),
    "MEDICAL PATIENT REPORT",
    fontsize=20,
    fontname="helv",
    color=(0.1, 0.25, 0.45),
)

page.insert_text(
    (50, 82),
    "Patient Medical Record - Digital PDF Template",
    fontsize=10,
)

page.draw_line((50, 100), (545, 100), color=(0.4, 0.4, 0.4))

# Patient information
page.insert_text((50, 140), "PATIENT INFORMATION", fontsize=13, fontname="hebo")

fields = [
    ("Subject ID", "{{Subject_ID}}"),
    ("Full Legal Name", "{{Full_Legal_Name}}"),
    ("Visit Date", "{{Visit_Date}}"),
]

y = 180
for label, placeholder in fields:
    page.insert_text((60, y), label + ":", fontsize=10)
    page.insert_text((220, y), placeholder, fontsize=10)
    y += 35

page.draw_line((50, 295), (545, 295), color=(0.6, 0.6, 0.6))

# Clinical information
page.insert_text((50, 330), "CLINICAL ASSESSMENT", fontsize=13, fontname="hebo")

clinical_fields = [
    ("Systolic BP", "{{Systolic_BP}}"),
    ("Diastolic BP", "{{Diastolic_BP}}"),
    ("Condition", "{{Condition_Class}}"),
]

y = 370
for label, placeholder in clinical_fields:
    page.insert_text((60, y), label + ":", fontsize=10)
    page.insert_text((220, y), placeholder, fontsize=10)
    y += 35

page.insert_text((60, 500), "Clinical Notes:", fontsize=10)
page.insert_textbox(
    fitz.Rect(60, 520, 535, 610),
    "{{Clinical_Notes}}",
    fontsize=10,
    fontname="helv",
)

page.draw_line((50, 690), (545, 690), color=(0.6, 0.6, 0.6))

page.insert_text(
    (50, 720),
    "Generated automatically by Smart Document Converter",
    fontsize=9,
    color=(0.4, 0.4, 0.4),
)

doc.save(output_file)
doc.close()

print("PDF template created:", output_file)
