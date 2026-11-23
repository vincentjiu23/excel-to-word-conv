"""
Field name normalization module.
"""

import re
import unicodedata

# Generic common abbreviations across varied domains
ABBREVIATIONS = {
    "qty": "quantity",
    "amt": "amount",
    "num": "number",
    "no": "number",
    "desc": "description",
    "addr": "address",
    "tel": "telephone",
    "ph": "phone",
    "dob": "date of birth",
    "dt": "date",
    "id": "identifier",
    "pct": "percentage",
    "perc": "percentage",
    "val": "value",
    "cat": "category",
    "stat": "status",
    "ref": "reference",
    "tot": "total",
    "subtot": "subtotal",
    "loc": "location",
    "std": "standard",
    "dev": "deviation",
    "avg": "average",
    "min": "minimum",
    "max": "maximum",
    "curr": "currency",
}


def normalize_field_name(text: str) -> str:
    """
    Standardize text:
    - Unicode normalize (NFKD)
    - Lowercase
    - Replace punctuation, underscores, hyphens with spaces
    - Expand common abbreviations
    - Strip and collapse whitespaces
    """
    if not text:
        return ""

    # Normalize unicode accents
    norm = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    norm = norm.lower()

    # Replace symbols and punctuation with space
    norm = re.sub(r"[^\w\s]", " ", norm)
    # Replace underscores
    norm = norm.replace("_", " ")

    tokens = norm.split()
    expanded_tokens = [ABBREVIATIONS.get(t, t) for t in tokens]
    return " ".join(expanded_tokens).strip()


def slugify_field_name(text: str) -> str:
    """Generate clean snake_case slug from field name."""
    norm = normalize_field_name(text)
    return re.sub(r"\s+", "_", norm)
