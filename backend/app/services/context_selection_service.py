import logging
import re
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ContextCandidate:
    source: str  # "retrieval", "graph", "repository"
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    char_count: int = 0
    token_estimate: int = 0

    def __post_init__(self):
        if not self.char_count:
            self.char_count = len(self.content)
        if not self.token_estimate:
            # Fallback estimate (~2.8 chars/token for code/JSON)
            self.token_estimate = max(1, int(self.char_count / 2.8))


class ContextSelectionService:
    """
    Selects and formats context candidates dynamically based on active tools and token limits.
    """

    def __init__(
        self,
        chars_per_token: float = 2.8,
        token_counter_fn: Optional[Any] = None,
        formatting_overhead_reserve: int = 150,
        **kwargs: Any,
    ):
        self.chars_per_token = chars_per_token
        self.token_counter_fn = token_counter_fn
        self.formatting_overhead_reserve = formatting_overhead_reserve

    def _estimate_tokens(self, text: str) -> int:
        if self.token_counter_fn:
            try:
                return max(1, int(self.token_counter_fn(text)))
            except Exception as e:
                logger.warning(f"token_counter_fn failed, falling back to estimation: {e}")
        return max(1, int(len(text) / self.chars_per_token))

    def _count_formatted_tokens(self, candidate_list: List[ContextCandidate]) -> int:
        """Counts exact tokens on the fully formatted context string to account for headers/formatting overhead."""
        formatted_text = self._format_final_context(candidate_list)
        return self._estimate_tokens(formatted_text)

    def _normalize_candidates(
        self, candidates: List[Any], default_source: str
    ) -> List[ContextCandidate]:
        """Normalizes dicts, objects, or raw strings into standard ContextCandidate objects."""
        normalized = []
        for cand in candidates or []:
            if isinstance(cand, ContextCandidate):
                if not cand.token_estimate:
                    cand.token_estimate = self._estimate_tokens(cand.content)
                normalized.append(cand)
            elif isinstance(cand, dict):
                content = (
                    cand.get("content")
                    or cand.get("code")
                    or cand.get("formatted_text")
                    or str(cand)
                )
                score = float(cand.get("score") or cand.get("rerank_score") or 0.0)

                normalized.append(
                    ContextCandidate(
                        source=cand.get("source", default_source),
                        content=content,
                        score=score,
                        metadata=cand,
                        token_estimate=self._estimate_tokens(content),
                    )
                )
            elif isinstance(cand, str):
                normalized.append(
                    ContextCandidate(
                        source=default_source,
                        content=cand,
                        score=1.0,
                        token_estimate=self._estimate_tokens(cand),
                    )
                )
            else:
                content = getattr(cand, "content", getattr(cand, "code", str(cand)))
                score = float(getattr(cand, "score", 1.0))
                normalized.append(
                    ContextCandidate(
                        source=default_source,
                        content=content,
                        score=score,
                        token_estimate=self._estimate_tokens(content),
                    )
                )
        return normalized

    def _calculate_redundancy(self, text: str, selected_contents: List[str]) -> float:
        """Token overlap check to penalize duplicate context."""
        if not selected_contents:
            return 0.0

        words = set(re.findall(r"\w+", text.lower()))
        if not words:
            return 0.0

        max_overlap = 0.0
        for existing in selected_contents:
            existing_words = set(re.findall(r"\w+", existing.lower()))
            if not existing_words:
                continue
            overlap = len(words.intersection(existing_words)) / float(len(words))
            if overlap > max_overlap:
                max_overlap = overlap

        return max_overlap

    def _trim_candidate(
        self, candidate: ContextCandidate, question: str, max_allowed_tokens: int
    ) -> Optional[ContextCandidate]:
        """Strict line-by-line budget-bounded trimming to prevent overflow."""
        lines = candidate.content.splitlines()
        if not lines:
            return None

        keywords = [w.lower() for w in re.findall(r"\w+", question) if len(w) > 3]
        
        matching_indices = [
            idx for idx, line in enumerate(lines)
            if any(kw in line.lower() for kw in keywords)
        ]

        if matching_indices:
            selected_line_indices = set()
            for idx in matching_indices:
                for window in range(max(0, idx - 2), min(len(lines), idx + 3)):
                    selected_line_indices.add(window)
            candidate_lines = [lines[i] for i in sorted(selected_line_indices)]
        else:
            candidate_lines = lines

        trimmed_lines = []
        accumulated_tokens = 0
        header_tokens = self._estimate_tokens("[TRIMMED EXCERPT]\n")

        for line in candidate_lines:
            line_tokens = self._estimate_tokens(line + "\n")
            if accumulated_tokens + line_tokens + header_tokens > max_allowed_tokens:
                break
            trimmed_lines.append(line)
            accumulated_tokens += line_tokens

        if not trimmed_lines:
            return None

        trimmed_content = "[TRIMMED EXCERPT]\n" + "\n".join(trimmed_lines)
        actual_tokens = self._estimate_tokens(trimmed_content)

        return ContextCandidate(
            source=candidate.source,
            content=trimmed_content,
            score=candidate.score * 0.9,
            metadata=candidate.metadata,
            char_count=len(trimmed_content),
            token_estimate=actual_tokens,
        )

    def select_context(
        self,
        question: str,
        retrieval_candidates: List[Any],
        graph_candidates: List[Any],
        repository_candidates: List[Any],
        available_context_budget: int,
        requested_tools: Optional[List[str]] = None,
        deep_analysis: bool = False,
    ) -> str:
        tools = requested_tools or ["retrieval", "graph", "repository"]
        effective_budget = max(0, available_context_budget - self.formatting_overhead_reserve)

        retrieval_norm = self._normalize_candidates(retrieval_candidates, "retrieval")
        graph_norm = self._normalize_candidates(graph_candidates, "graph")
        repo_norm = self._normalize_candidates(repository_candidates, "repository")

        # =========================================================================
        # SINGLE TOOL BRANCH
        # =========================================================================
        if len(tools) == 1 and tools[0] == "retrieval":
            retrieval_norm.sort(key=lambda c: c.score, reverse=True)
            selected_candidates: List[ContextCandidate] = []

            for cand in retrieval_norm:
                test_selection = selected_candidates + [cand]
                if self._count_formatted_tokens(test_selection) <= effective_budget:
                    selected_candidates.append(cand)
                else:
                    baseline_tokens = self._count_formatted_tokens(selected_candidates)
                    remaining_budget = effective_budget - baseline_tokens
                    if remaining_budget > 50:
                        trimmed = self._trim_candidate(cand, question, remaining_budget)
                        if trimmed:
                            if self._count_formatted_tokens(selected_candidates + [trimmed]) <= effective_budget:
                                selected_candidates.append(trimmed)
                    break

            return self._format_final_context(selected_candidates)

        # =========================================================================
        # MULTI-TOOL BRANCH
        # =========================================================================
        all_candidates_by_source: Dict[str, List[ContextCandidate]] = {
            "retrieval": retrieval_norm,
            "graph": graph_norm,
            "repository": repo_norm,
        }
        for source in all_candidates_by_source:
            if source == "graph":
                all_candidates_by_source[source].sort(
                    key=lambda c: (
                        c.metadata.get("category") != "dependent",
                        -c.score,
                    )
                )
            else:
                all_candidates_by_source[source].sort(
                    key=lambda c: c.score,
                    reverse=True
                )

        selected_candidates: List[ContextCandidate] = []
        selected_ids: Set[int] = set()
        selected_contents: List[str] = []

        # --- PHASE 1: Best useful candidate per selected tool ---
        for tool in tools:
            candidates = all_candidates_by_source.get(tool, [])
            for cand in candidates:
                cand_id = id(cand)
                if cand_id in selected_ids:
                    continue

                test_selection = selected_candidates + [cand]
                if self._count_formatted_tokens(test_selection) <= effective_budget:
                    selected_candidates.append(cand)
                    selected_ids.add(cand_id)
                    selected_contents.append(cand.content)
                    break

        # --- PHASE 2: Dynamic Reranking ---
        remaining_candidates: List[ContextCandidate] = []
        for source, candidates in all_candidates_by_source.items():
            for cand in candidates:
                if id(cand) not in selected_ids:
                    remaining_candidates.append(cand)

        source_counts = {t: sum(1 for c in selected_candidates if c.source == t) for t in tools}

        exact_weight = 20.0 if deep_analysis else 10.0
        diversity_weight = 5.0 if len(tools) > 1 else 0.0

        def phase2_score(cand: ContextCandidate) -> float:
            base = cand.score
            redundancy = self._calculate_redundancy(cand.content, selected_contents)
            penalty = redundancy * 15.0

            diversity_boost = diversity_weight if source_counts.get(cand.source, 0) == 0 else 0.0
            exact_match_boost = exact_weight if cand.metadata.get("is_exact_identifier_match") else 0.0
            efficiency = (base / max(1, cand.token_estimate)) * 10.0

            return base + exact_match_boost + diversity_boost - penalty + efficiency

        remaining_candidates.sort(key=phase2_score, reverse=True)

        # Packing loop evaluating exact formatted context bounds
        for cand in remaining_candidates:
            test_selection = selected_candidates + [cand]
            if self._count_formatted_tokens(test_selection) <= effective_budget:
                selected_candidates.append(cand)
                selected_ids.add(id(cand))
                selected_contents.append(cand.content)
                source_counts[cand.source] = source_counts.get(cand.source, 0) + 1
            else:
                baseline_tokens = self._count_formatted_tokens(selected_candidates)
                remaining_budget = effective_budget - baseline_tokens
                if remaining_budget > 50:
                    trimmed = self._trim_candidate(cand, question, remaining_budget)
                    if trimmed:
                        if self._count_formatted_tokens(selected_candidates + [trimmed]) <= effective_budget:
                            selected_candidates.append(trimmed)
                            selected_ids.add(id(cand))
                            selected_contents.append(trimmed.content)
                            source_counts[cand.source] = source_counts.get(cand.source, 0) + 1

        return self._format_final_context(selected_candidates)

    def _format_final_context(self, candidates: List[ContextCandidate]) -> str:
        if not candidates:
            return "No relevant context found."

        retrieval_blocks, graph_blocks, repo_blocks = [], [], []

        for cand in candidates:
            if cand.source == "retrieval":
                retrieval_blocks.append(cand.content)
            elif cand.source == "graph":
                graph_blocks.append(cand.content)
            elif cand.source == "repository":
                repo_blocks.append(cand.content)

        formatted_sections = []
        if retrieval_blocks:
            formatted_sections.append("==== RETRIEVAL CONTEXT ====\n" + "\n\n".join(retrieval_blocks))
        if graph_blocks:
            formatted_sections.append("==== GRAPH CONTEXT ====\n" + "\n\n".join(graph_blocks))
        if repo_blocks:
            formatted_sections.append("==== REPOSITORY CONTEXT ====\n" + "\n\n".join(repo_blocks))

        return "\n\n".join(formatted_sections)
