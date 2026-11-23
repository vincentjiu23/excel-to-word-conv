"""
Generic extensible synonym registry.
Not constrained to any single vertical or industry.
"""

from typing import Dict, List, Optional, Set

GENERIC_SYNONYM_CLUSTERS = [
    {"amount", "total", "sum", "subtotal", "cost", "price", "charge", "fee", "val", "value"},
    {"name", "title", "label", "designation", "heading", "identifier", "caption"},
    {"date", "day", "timestamp", "time", "period", "datetime"},
    {"id", "identifier", "code", "key", "ref", "reference", "serial", "number", "sku", "tag"},
    {"quantity", "count", "units", "volume", "amount", "qty", "items"},
    {"category", "type", "group", "class", "classification", "kind", "genre", "family"},
    {"status", "state", "condition", "stage", "phase", "mode"},
    {"description", "detail", "details", "notes", "note", "remarks", "summary", "comment", "explanation"},
    {"person", "user", "client", "customer", "contact", "agent", "member", "individual", "entity", "party"},
    {"location", "place", "address", "site", "venue", "destination", "position", "city", "region"},
    {"balance", "remaining", "due", "outstanding"},
    {"discount", "rebate", "deduction", "concession"},
    {"tax", "vat", "gst", "duty", "tariff"},
    {"rate", "ratio", "percentage", "proportion"},
    {"result", "outcome", "finding", "score", "grade", "metric"},
    {"start", "begin", "commence", "initiation", "from"},
    {"end", "finish", "conclusion", "termination", "to", "expiry", "deadline"},
]


class SynonymRegistry:
    def __init__(self, custom_clusters: Optional[List[Set[str]]] = None):
        self.clusters: List[Set[str]] = [set(c) for c in GENERIC_SYNONYM_CLUSTERS]
        if custom_clusters:
            for cluster in custom_clusters:
                self.clusters.append(set(cluster))

    def are_synonyms(self, term_a: str, term_b: str) -> bool:
        """Check if two single normalized terms belong to the same synonym cluster."""
        a = term_a.strip().lower()
        b = term_b.strip().lower()
        if not a or not b:
            return False
        if a == b:
            return True

        for cluster in self.clusters:
            if a in cluster and b in cluster:
                return True
        return False

    def are_phrases_synonymous(self, phrase_a: str, phrase_b: str) -> bool:
        """Check if two multi-token phrases are synonymous across their tokens."""
        tokens_a = phrase_a.strip().lower().split()
        tokens_b = phrase_b.strip().lower().split()
        if not tokens_a or not tokens_b:
            return False

        if tokens_a == tokens_b:
            return True

        if len(tokens_a) == len(tokens_b):
            return all(ta == tb or self.are_synonyms(ta, tb) for ta, tb in zip(tokens_a, tokens_b))

        return False

    def add_synonym_pair(self, term_a: str, term_b: str) -> None:
        """Dynamically add or merge a pair into synonym clusters."""
        a = term_a.strip().lower()
        b = term_b.strip().lower()
        for cluster in self.clusters:
            if a in cluster or b in cluster:
                cluster.add(a)
                cluster.add(b)
                return
        self.clusters.append({a, b})
