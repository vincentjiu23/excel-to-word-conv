"""
Fuzzy string similarity algorithms with rapidfuzz and difflib fallback.
"""

from difflib import SequenceMatcher
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False


def calculate_string_similarity(str_a: str, str_b: str) -> float:
    """
    Computes a hybrid similarity score between 0.0 and 1.0.
    Considers token order, token subset, and raw edit distance.
    """
    if not str_a or not str_b:
        return 0.0
    if str_a == str_b:
        return 1.0

    if HAS_RAPIDFUZZ:
        token_sort = fuzz.token_sort_ratio(str_a, str_b) / 100.0
        token_set = fuzz.token_set_ratio(str_a, str_b) / 100.0
        partial = fuzz.partial_ratio(str_a, str_b) / 100.0
        # Weighted combination
        return round((token_sort * 0.45) + (token_set * 0.40) + (partial * 0.15), 3)
    else:
        # Fallback using difflib
        sm = SequenceMatcher(None, str_a, str_b)
        base_ratio = sm.ratio()

        tokens_a = set(str_a.split())
        tokens_b = set(str_b.split())
        jaccard = len(tokens_a & tokens_b) / max(len(tokens_a | tokens_b), 1)

        return round((base_ratio * 0.6) + (jaccard * 0.4), 3)
