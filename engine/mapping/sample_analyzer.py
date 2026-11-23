"""
Sample value and pattern analysis to enhance field matching confidence.
"""

import re
from typing import Any, List
from ..models.field import DataType


def score_sample_patterns(target_name: str, samples: List[Any]) -> float:
    """
    Examines non-empty sample values from the source field against semantic hints in target name.
    Returns a score modifier between 0.0 and 1.0.
    """
    if not samples:
        return 0.5

    clean_samples = [str(s).strip() for s in samples if s is not None and str(s).strip() != ""]
    if not clean_samples:
        return 0.5

    t_lower = target_name.lower()

    # Email pattern
    if "email" in t_lower or "mail" in t_lower:
        has_email = sum(1 for s in clean_samples if re.search(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", s))
        if has_email > 0:
            return 0.95

    # Phone / Tel pattern
    if any(k in t_lower for k in ["phone", "tel", "mobile", "contact"]):
        has_phone = sum(1 for s in clean_samples if re.search(r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", s))
        if has_phone > 0:
            return 0.90

    # Date pattern
    if any(k in t_lower for k in ["date", "dob", "birth", "day", "created", "timestamp"]):
        has_date = sum(1 for s in clean_samples if re.search(r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}", s))
        if has_date > 0:
            return 0.90

    # Currency / Price pattern
    if any(k in t_lower for k in ["price", "cost", "total", "amount", "fee", "rate", "subtotal", "salary"]):
        has_curr = sum(1 for s in clean_samples if re.search(r"[\$€£¥Rp]|\.\d{2}$", s))
        if has_curr > 0:
            return 0.90

    # Numeric ID / Code pattern
    if any(k in t_lower for k in ["id", "code", "sku", "number", "num", "no"]):
        has_digits = sum(1 for s in clean_samples if any(c.isdigit() for c in s))
        if has_digits > 0:
            return 0.85

    return 0.60
