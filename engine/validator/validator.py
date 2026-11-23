"""
Rigorous output validation module.
Verifies file existence, DOCX ZIP structure integrity, reopenability,
table readability, row counts, and data fidelity.
"""

import os
import zipfile
from typing import Any, Dict, List, Optional
from docx import Document


class ValidationResult:
    def __init__(self):
        self.is_valid: bool = True
        self.checks_passed: List[str] = []
        self.checks_failed: List[str] = []
        self.details: Dict[str, Any] = {}

    def add_pass(self, check_name: str, message: str = ""):
        self.checks_passed.append(f"{check_name}: {message}" if message else check_name)

    def add_fail(self, check_name: str, message: str):
        self.is_valid = False
        self.checks_failed.append(f"{check_name}: {message}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "details": self.details,
        }


class OutputValidator:
    @staticmethod
    def validate(
        output_path: str,
        expected_records_count: Optional[int] = None,
        expected_values_to_verify: Optional[List[str]] = None,
        table_index: int = 0,
    ) -> ValidationResult:
        result = ValidationResult()

        # Check 1: File exists
        if not os.path.exists(output_path):
            result.add_fail("file_existence", f"Generated output file not found at: {output_path}")
            return result
        result.add_pass("file_existence", f"File exists at {output_path}")

        # Check 2: Non-empty file
        size = os.path.getsize(output_path)
        if size == 0:
            result.add_fail("non_empty", "File is empty (0 bytes)")
            return result
        result.add_pass("non_empty", f"File size is {size} bytes")
        result.details["file_size_bytes"] = size

        # Check 3: Valid DOCX ZIP structure
        if not zipfile.is_zipfile(output_path):
            result.add_fail("zip_structure", "File is not a valid ZIP / DOCX package")
            return result

        try:
            with zipfile.ZipFile(output_path, "r") as zf:
                file_list = zf.namelist()
                if "[Content_Types].xml" not in file_list or "word/document.xml" not in file_list:
                    result.add_fail("docx_package", "Missing essential DOCX components ([Content_Types].xml or word/document.xml)")
                    return result
            result.add_pass("zip_structure", "Valid OOXML ZIP package with required manifests")
        except Exception as e:
            result.add_fail("zip_structure", f"Corrupt ZIP package: {str(e)}")
            return result

        # Check 4: Can be reopened cleanly by python-docx
        try:
            doc = Document(output_path)
            result.add_pass("document_reopen", "Document opened successfully with python-docx")
        except Exception as e:
            result.add_fail("document_reopen", f"Failed to reopen generated docx: {str(e)}")
            return result

        # Check 5: Tables remain readable and row counts match
        total_tables = len(doc.tables)
        result.details["tables_count"] = total_tables
        result.details["paragraphs_count"] = len(doc.paragraphs)

        if expected_records_count is not None and total_tables > 0:
            if table_index < total_tables:
                table = doc.tables[table_index]
                actual_rows = len(table.rows)
                result.details["table_rows"] = actual_rows
                expected_min = expected_records_count
                if actual_rows >= expected_min:
                    result.add_pass("row_count", f"Table has {actual_rows} rows (expected >= {expected_min})")
                else:
                    result.add_fail("row_count", f"Table has {actual_rows} rows, expected at least {expected_min}")

        # Check 6: Check for expected mapped values presence
        all_text_fragments = [p.text for p in doc.paragraphs]
        for t in doc.tables:
            for row in t.rows:
                for c in row.cells:
                    all_text_fragments.append(c.text)

        document_full_text = " ".join(all_text_fragments)

        if expected_values_to_verify:
            missing_vals = []
            for val in expected_values_to_verify:
                clean_v = str(val).strip()
                if not clean_v:
                    continue

                found = clean_v in document_full_text
                # Also check float-to-integer representation equivalence (e.g. 440.0 in test vs 440 in table)
                if not found:
                    try:
                        f_v = float(clean_v)
                        if f_v.is_integer() and str(int(f_v)) in document_full_text:
                            found = True
                    except (ValueError, TypeError):
                        pass

                if not found:
                    missing_vals.append(clean_v)

            if missing_vals:
                result.add_fail("data_fidelity", f"Missing expected data values in output: {missing_vals[:5]}")
            else:
                result.add_pass("data_fidelity", f"All {len(expected_values_to_verify)} verified sample values present in output")

        return result
