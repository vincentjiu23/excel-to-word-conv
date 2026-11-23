"""
Machine Learning & Semantic Matching Benchmark Evaluation.
Evaluates deterministic baseline vs. semantic & hybrid matching across diverse schemas.
Measures Top-1 Accuracy, Top-3 Accuracy, Precision, Recall, and F1.
"""

import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Tuple
from engine.mapping.engine import IntelligentMappingEngine
from engine.mapping.feedback_store import FeedbackStore
from engine.mapping.normalizer import normalize_field_name
from engine.models.field import DataType, FieldModel, SourceType
from engine.models.mapping import MappingStatus

# Diverse synthetic ground-truth test pairs across 5 distinct domains:
BENCHMARK_DATASET: List[Tuple[str, str, bool]] = [
    # Domain 1: Medical / Clinical
    ("Subject_ID", "Patient Identifier", True),
    ("Systolic_BP", "Systolic Blood Pressure (mmHg)", True),
    ("Diastolic_BP", "Diastolic Blood Pressure (mmHg)", True),
    ("Visit_Date", "Date of Examination", True),
    ("Clinical_Notes", "Doctor's Assessment Remarks", True),
    ("Patient_Weight_Kg", "Target Cholesterol Level", False),
    # Domain 2: Maritime Logistics
    ("Container_Code", "Cargo Container Unit ID", True),
    ("Gross_Weight_KG", "Total Gross Mass (kg)", True),
    ("Tare_Weight_KG", "Tare Weight", True),
    ("Departure_Date", "Sailing Date", True),
    ("Origin_Port", "Port of Loading", True),
    ("Vessel_Reference", "Captain Passport Number", False),
    # Domain 3: Astrophysics Telemetry
    ("Signal_ID", "Detection ID", True),
    ("Right_Ascension_Deg", "Right Ascension (J2000)", True),
    ("Flux_Density_mJy", "Observed Radio Flux (mJy)", True),
    ("Observation_Epoch", "UTC Observation Timestamp", True),
    ("Redshift_z", "Radial Velocity Km/s", False),
    # Domain 4: Retail & Commerce
    ("SKU_Code", "Product Identifier Code", True),
    ("Unit_Price_USD", "Item Cost Amount", True),
    ("Qty_Shipped", "Quantity Dispatched", True),
    ("Customer_Address", "Delivery Location Address", True),
    ("Discount_Rate", "Warehouse Bay Number", False),
    # Domain 5: Human Resources & Payroll
    ("Employee_DOB", "Birth Date", True),
    ("Basic_Salary", "Base Remuneration Amount", True),
    ("Job_Title", "Position Designation", True),
    ("Dept_Code", "Division Identifier", True),
    ("Leave_Balance", "Office Parking Spot", False),
]


def run_benchmark():
    print("=" * 70)
    print("  Machine Learning & Intelligent Matching Evaluation Benchmark")
    print("=" * 70)

    engine = IntelligentMappingEngine(feedback_store=FeedbackStore(":memory:"))

    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    top1_correct = 0
    total_pairs = len(BENCHMARK_DATASET)

    start_time = time.perf_counter()

    for s_name, t_name, is_match in BENCHMARK_DATASET:
        src = FieldModel(
            field_id=f"src_{s_name}",
            original_name=s_name,
            normalized_name=normalize_field_name(s_name),
            data_type=DataType.STRING,
            source_type=SourceType.EXCEL,
        )
        tgt = FieldModel(
            field_id=f"tgt_{t_name}",
            original_name=t_name,
            normalized_name=normalize_field_name(t_name),
            data_type=DataType.STRING,
            source_type=SourceType.WORD,
        )

        mappings = engine.generate_mappings([src], [tgt])
        m = mappings[0]

        predicted_match = m.status in (
            MappingStatus.EXACT_MATCH,
            MappingStatus.HIGH_CONFIDENCE,
            MappingStatus.RECOMMENDED,
            MappingStatus.NEEDS_REVIEW,
        ) and m.confidence >= 0.50

        if is_match and predicted_match:
            true_positives += 1
            top1_correct += 1
        elif not is_match and not predicted_match:
            true_negatives += 1
        elif not is_match and predicted_match:
            false_positives += 1
            print(f"  [FP Alert] Pair ('{s_name}' -> '{t_name}') predicted match with conf {m.confidence}")
        elif is_match and not predicted_match:
            false_negatives += 1
            print(f"  [FN Alert] Pair ('{s_name}' -> '{t_name}') failed to match. Conf: {m.confidence}, Reason: {m.reason}")

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    precision = true_positives / max(true_positives + false_positives, 1)
    recall = true_positives / max(true_positives + false_negatives, 1)
    f1 = (2 * precision * recall) / max(precision + recall, 1e-6)
    accuracy = (true_positives + true_negatives) / total_pairs

    print("\n" + "-" * 70)
    print("  EVALUATION RESULTS")
    print("-" * 70)
    print(f"  Total Test Schema Pairs   : {total_pairs}")
    print(f"  True Positives (TP)       : {true_positives}")
    print(f"  True Negatives (TN)       : {true_negatives}")
    print(f"  False Positives (FP)      : {false_positives}")
    print(f"  False Negatives (FN)      : {false_negatives}")
    print(f"  Overall Accuracy          : {accuracy * 100:.2f}%")
    print(f"  Precision                 : {precision * 100:.2f}%")
    print(f"  Recall                    : {recall * 100:.2f}%")
    print(f"  F1 Score                  : {f1 * 100:.2f}%")
    print(f"  Average Matching Latency  : {elapsed_ms / total_pairs:.3f} ms per pair")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
