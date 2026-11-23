"""
Data type compatibility matrix for mapping validation.
"""

from typing import Dict, Tuple
from ..models.field import DataType

# Compatibility scoring: (source_type, target_type) -> score 0.0 to 1.0
COMPATIBILITY_SCORES: Dict[Tuple[DataType, DataType], float] = {
    (DataType.STRING, DataType.STRING): 1.0,
    (DataType.INTEGER, DataType.INTEGER): 1.0,
    (DataType.FLOAT, DataType.FLOAT): 1.0,
    (DataType.INTEGER, DataType.FLOAT): 0.95,
    (DataType.FLOAT, DataType.INTEGER): 0.70,
    (DataType.DATE, DataType.DATE): 1.0,
    (DataType.DATETIME, DataType.DATETIME): 1.0,
    (DataType.DATE, DataType.DATETIME): 0.90,
    (DataType.DATETIME, DataType.DATE): 0.90,
    (DataType.CURRENCY, DataType.FLOAT): 0.95,
    (DataType.CURRENCY, DataType.CURRENCY): 1.0,
    (DataType.PERCENTAGE, DataType.FLOAT): 0.90,
    (DataType.BOOLEAN, DataType.BOOLEAN): 1.0,
    (DataType.UNKNOWN, DataType.STRING): 0.80,
}


def check_type_compatibility(source_type: DataType, target_type: DataType) -> float:
    """
    Returns compatibility score between source and target data types.
    Strings can accept almost any type, so source->string gets a reasonable score.
    """
    if source_type == target_type:
        return 1.0

    if (source_type, target_type) in COMPATIBILITY_SCORES:
        return COMPATIBILITY_SCORES[(source_type, target_type)]

    # Target is string: virtually any type can be represented as text
    if target_type == DataType.STRING:
        return 0.85

    return 0.40
