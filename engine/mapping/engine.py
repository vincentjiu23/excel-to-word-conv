"""
Comprehensive 9-Stage Intelligent Hybrid Mapping Engine.
Produces explainable reasons and strict confidence scoring.
Zero hardcoded assumptions about business schemas.
"""

from typing import Dict, List, Optional, Tuple
from ..models.field import FieldModel
from ..models.mapping import FieldMapping, MappingStatus
from .feedback_store import FeedbackStore
from .fuzzy import calculate_string_similarity
from .normalizer import normalize_field_name
from .sample_analyzer import score_sample_patterns
from .semantic_interface import BaseSemanticMatcher, CharacterNGramCosineMatcher
from .synonyms import SynonymRegistry
from .type_checker import check_type_compatibility


class IntelligentMappingEngine:
    def __init__(
        self,
        synonym_registry: Optional[SynonymRegistry] = None,
        semantic_matcher: Optional[BaseSemanticMatcher] = None,
        feedback_store: Optional[FeedbackStore] = None,
    ):
        self.synonyms = synonym_registry or SynonymRegistry()
        self.semantic = semantic_matcher or CharacterNGramCosineMatcher()
        self.feedback = feedback_store or FeedbackStore()

    def generate_mappings(
        self, source_fields: List[FieldModel], target_fields: List[FieldModel]
    ) -> List[FieldMapping]:
        """
        Takes dynamic source fields and dynamic target fields,
        evaluates candidate pairs across 9 stages, and returns recommended mappings.
        """
        mappings: List[FieldMapping] = []

        for t_idx, target in enumerate(target_fields):
            t_orig = target.original_name
            t_norm = target.normalized_name or normalize_field_name(t_orig)

            all_candidate_scores: List[Tuple[FieldModel, float, str, str]] = []

            for source in source_fields:
                s_orig = source.original_name
                s_norm = source.normalized_name or normalize_field_name(s_orig)

                score = 0.0
                reason = ""
                stage = ""

                # Stage 1: Exact match on original name
                if s_orig.strip().lower() == t_orig.strip().lower():
                    score = 1.0
                    reason = f"Exact match on original name ('{s_orig}')"
                    stage = "exact_match"

                # Stage 2: Exact match on normalized name (case, symbols, abbreviations)
                elif s_norm and t_norm and s_norm == t_norm:
                    score = 0.95
                    reason = f"Normalized match: '{s_orig}' -> '{t_orig}'"
                    stage = "normalization"

                # Stage 3: Synonym matching (single terms or multi-token phrases)
                elif self.synonyms.are_synonyms(s_norm, t_norm) or self.synonyms.are_phrases_synonymous(s_norm, t_norm):
                    score = 0.90
                    reason = f"Synonym match: '{s_orig}' is synonymous with '{t_orig}'"
                    stage = "synonym"

                else:
                    # Stage 4: Fuzzy similarity
                    fuzzy_score = calculate_string_similarity(s_norm, t_norm)

                    # Stage 7: Semantic n-gram / embedding similarity
                    semantic_score = self.semantic.similarity(s_norm, t_norm)

                    # Stage 5: Type compatibility factor
                    type_factor = check_type_compatibility(source.data_type, target.data_type)

                    # Stage 6: Sample pattern factor
                    sample_factor = score_sample_patterns(t_orig, source.sample_values)

                    # Combine fuzzy, semantic, type, and sample
                    composite = (fuzzy_score * 0.50) + (semantic_score * 0.25) + (type_factor * 0.15) + (sample_factor * 0.10)

                    # Stage 8: Document position bonus (if column index aligns in a table)
                    s_col = source.location.get("column_index")
                    t_col = target.location.get("col_index")
                    if s_col is not None and t_col is not None and s_col == (t_col + 1):
                        composite += 0.05

                    if composite > 0.10:
                        score = min(composite, 0.94)
                        reason = f"Fuzzy similarity ({round(fuzzy_score, 2)}) with {source.data_type.value} compatibility"
                        stage = "fuzzy_semantic"

                # Stage 9: Historical user feedback affinity boost
                affinity = self.feedback.get_historical_affinity(s_orig, t_orig)
                if affinity > 0:
                    score = min(score + affinity, 1.0)
                    if reason:
                        reason += f" (Boosted by historical confirmation +{round(affinity, 2)})"
                    else:
                        reason = f"Historical confirmation match (+{round(affinity, 2)})"
                        stage = "historical_learning"

                if score > 0:
                    all_candidate_scores.append((source, score, reason, stage))

            # Sort candidate scores descending
            all_candidate_scores.sort(key=lambda x: x[1], reverse=True)

            if all_candidate_scores:
                top_candidate, top_score, top_reason, top_stage = all_candidate_scores[0]

                # Check for ambiguity: if runner-up score is within 0.04 of top score
                is_ambiguous = False
                if len(all_candidate_scores) > 1:
                    runner_up = all_candidate_scores[1]
                    if (top_score - runner_up[1]) < 0.04 and top_score < 0.95:
                        is_ambiguous = True

                if is_ambiguous:
                    status = MappingStatus.AMBIGUOUS
                    reason = f"Ambiguous candidates: '{top_candidate.original_name}' ({round(top_score, 2)}) vs '{runner_up[0].original_name}' ({round(runner_up[1], 2)})"
                elif top_score >= 0.98:
                    status = MappingStatus.EXACT_MATCH
                    reason = top_reason
                elif top_score >= 0.85:
                    status = MappingStatus.HIGH_CONFIDENCE
                    reason = top_reason
                elif top_score >= 0.70:
                    status = MappingStatus.RECOMMENDED
                    reason = top_reason
                elif top_score >= 0.45:
                    status = MappingStatus.NEEDS_REVIEW
                    reason = top_reason
                else:
                    status = MappingStatus.UNMATCHED
                    reason = f"{top_reason} (below threshold: {round(top_score, 2)})"

                mapping_id = f"map_{t_idx}_{target.field_id}"
                mapping = FieldMapping(
                    mapping_id=mapping_id,
                    target_field_id=target.field_id,
                    target_name=target.original_name,
                    source_field_id=top_candidate.field_id if status != MappingStatus.UNMATCHED else None,
                    source_name=top_candidate.original_name if status != MappingStatus.UNMATCHED else None,
                    confidence=round(top_score, 3),
                    status=status,
                    reason=reason,
                    stage=top_stage,
                )
                mappings.append(mapping)
            else:
                mapping_id = f"map_{t_idx}_{target.field_id}"
                mappings.append(
                    FieldMapping(
                        mapping_id=mapping_id,
                        target_field_id=target.field_id,
                        target_name=target.original_name,
                        source_field_id=None,
                        source_name=None,
                        confidence=0.0,
                        status=MappingStatus.UNMATCHED,
                        reason="No compatible source field found",
                        stage="unmatched",
                    )
                )

        return mappings
