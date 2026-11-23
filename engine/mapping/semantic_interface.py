"""
Semantic and ML Matching Interface.
Provides an extensible plugin point for local embeddings or models,
while providing a built-in character n-gram TF-IDF cosine similarity baseline.
"""

from abc import ABC, abstractmethod
import math
import re
from typing import Dict, List, Optional


class BaseSemanticMatcher(ABC):
    @abstractmethod
    def similarity(self, text_a: str, text_b: str) -> float:
        """Compute semantic similarity score between 0.0 and 1.0."""
        pass


class CharacterNGramCosineMatcher(BaseSemanticMatcher):
    """
    Lightweight, deterministic character 3-gram and 4-gram vectorizer
    calculating cosine similarity. Runs locally with zero dependencies or latency.
    """

    def __init__(self, n_range=(3, 4)):
        self.n_range = n_range

    def _get_ngrams(self, text: str) -> Dict[str, int]:
        clean = re.sub(r"\s+", " ", text.lower().strip())
        padded = f"^{clean}$"
        freqs: Dict[str, int] = {}
        for n in self.n_range:
            for i in range(len(padded) - n + 1):
                gram = padded[i : i + n]
                freqs[gram] = freqs.get(gram, 0) + 1
        return freqs

    def similarity(self, text_a: str, text_b: str) -> float:
        if not text_a or not text_b:
            return 0.0
        if text_a.strip().lower() == text_b.strip().lower():
            return 1.0

        vec_a = self._get_ngrams(text_a)
        vec_b = self._get_ngrams(text_b)

        # Dot product
        common_keys = set(vec_a.keys()) & set(vec_b.keys())
        dot_product = sum(vec_a[k] * vec_b[k] for k in common_keys)

        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return round(dot_product / (norm_a * norm_b), 3)


class LocalEmbeddingSemanticMatcher(BaseSemanticMatcher):
    """
    Optional plugin interface for transformer embeddings (e.g. sentence-transformers, onnx, or Ollama).
    Gracefully falls back to NGram matcher if model is not loaded.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name
        self.fallback = CharacterNGramCosineMatcher()
        self.model = None

    def similarity(self, text_a: str, text_b: str) -> float:
        if self.model is None:
            # Documented extensible fallback
            return self.fallback.similarity(text_a, text_b)
        # In a deployment with torch/sentence-transformers installed, inference would happen here
        return self.fallback.similarity(text_a, text_b)
