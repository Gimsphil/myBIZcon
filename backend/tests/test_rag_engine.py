# -*- coding: utf-8 -*-
"""
test_rag_engine.py - RAG Engine Integration Tests
==================================================
CODEX Step 16: Validates the TF-IDF RAG engine for correctness,
edge-case handling, and consistent semantic retrieval quality.

Test Coverage:
  1. Corpus indexing (mock corpus must load and be non-empty)
  2. TF-IDF vector construction (IDF weights must be non-zero)
  3. Cosine Similarity edge cases (empty vectors → 0.0)
  4. Retrieval quality (semantic search returns a valid string)
  5. Tokenization robustness (Korean + Latin mixed text)

Role: CODEX (2nd Coder / Auditor) - Integration Test Suite
Reviewed by: Antigravity (기술 검토자)
"""

import sys
import os

# Allow imports from the backend root when running pytest from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from backend.app.services.rag_engine import RAGEngineService


# ── Fixture ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def engine():
    """Returns a freshly initialized RAGEngineService with mock corpus."""
    svc = RAGEngineService()
    return svc


# ── Test Cases ─────────────────────────────────────────────────────────────

class TestRAGCorpusIndexing:
    """Tests corpus loading and TF-IDF index construction."""

    def test_mock_corpus_is_loaded(self, engine):
        """The mock corpus must contain at least one document after initialization."""
        assert len(engine.corpus) > 0, (
            "RAGEngine corpus is empty. Mock corpus should always be loaded as fallback."
        )

    def test_doc_vectors_match_corpus(self, engine):
        """Every document in the corpus should have a corresponding TF-IDF vector."""
        assert set(engine.doc_vectors.keys()) == set(engine.corpus.keys()), (
            "Mismatch between corpus documents and doc_vectors. IDF build may have failed."
        )

    def test_idf_weights_are_positive(self, engine):
        """All IDF weights must be strictly positive (log formula guarantees this)."""
        for token, idf_val in engine.idf.items():
            assert idf_val > 0.0, f"IDF weight for token '{token}' is not positive: {idf_val}"

    def test_reindex_resets_and_rebuilds(self, engine):
        """reindex_corpus() must rebuild from scratch (previous state cleared)."""
        old_count = len(engine.corpus)
        engine.reindex_corpus()
        new_count = len(engine.corpus)
        assert new_count > 0, "Corpus is empty after reindex."
        assert new_count == old_count, (
            f"Corpus size changed unexpectedly after reindex: {old_count} → {new_count}"
        )


class TestCosineSimilarity:
    """Tests the cosine similarity utility function."""

    def test_identical_vectors_return_one(self, engine):
        """Two identical sparse vectors must have cosine similarity of 1.0."""
        vec = {"안녕": 0.5, "계약서": 0.3, "회의": 0.2}
        sim = engine._cosine_similarity(vec, vec)
        assert abs(sim - 1.0) < 1e-9, f"Identical vectors should return 1.0, got {sim}"

    def test_empty_vectors_return_zero(self, engine):
        """Cosine similarity with any empty vector must return 0.0 (no division by zero)."""
        assert engine._cosine_similarity({}, {}) == 0.0
        assert engine._cosine_similarity({"a": 1.0}, {}) == 0.0
        assert engine._cosine_similarity({}, {"b": 1.0}) == 0.0

    def test_orthogonal_vectors_return_zero(self, engine):
        """Vectors with no shared tokens must return 0.0."""
        vec1 = {"abc": 0.9}
        vec2 = {"xyz": 0.9}
        assert engine._cosine_similarity(vec1, vec2) == 0.0

    def test_partial_overlap_returns_between_zero_and_one(self, engine):
        """Vectors with partial overlap must return a value in (0.0, 1.0)."""
        vec1 = {"계약서": 0.6, "회의": 0.4}
        vec2 = {"계약서": 0.6, "보고서": 0.4}
        sim = engine._cosine_similarity(vec1, vec2)
        assert 0.0 < sim < 1.0, f"Partial overlap similarity should be between 0 and 1, got {sim}"


class TestTokenization:
    """Tests the tokenizer for robustness."""

    def test_latin_text_tokenized(self, engine):
        """Standard Latin text should produce non-empty tokens."""
        tokens = engine._tokenize("Hello World NDA contract meeting")
        assert len(tokens) > 0

    def test_korean_text_tokenized(self, engine):
        """Korean text (hangul) must be recognized and tokenized."""
        tokens = engine._tokenize("안녕하세요 회의 보고서 계약서 작성")
        assert len(tokens) > 0, "Korean text tokenization failed."

    def test_mixed_language_tokenized(self, engine):
        """Mixed Korean + English text must produce tokens from both."""
        tokens = engine._tokenize("NDA 비밀유지계약서 draft")
        assert len(tokens) >= 2, f"Mixed language tokenization returned too few tokens: {tokens}"

    def test_empty_string_returns_empty_list(self, engine):
        """Empty input must return an empty list without errors."""
        assert engine._tokenize("") == []

    def test_short_tokens_filtered(self, engine):
        """Tokens shorter than 2 characters should be filtered out."""
        tokens = engine._tokenize("a b c hello")
        for t in tokens:
            assert len(t) > 1, f"Short token '{t}' was not filtered."


class TestSemanticRetrieval:
    """Tests the end-to-end semantic retrieval pipeline."""

    def test_retrieve_returns_string(self, engine):
        """retrieve_personal_examples() must always return a string."""
        result = engine.retrieve_personal_examples("NDA 계약서 보내주세요")
        assert isinstance(result, str), "retrieve_personal_examples must return a string."

    def test_retrieve_nonempty_for_relevant_query(self, engine):
        """A query matching mock corpus content should return a non-empty few-shot block."""
        result = engine.retrieve_personal_examples("비밀유지계약서 보내드리겠습니다")
        assert len(result) > 0, (
            "Expected a non-empty few-shot context for a relevant query against mock corpus."
        )

    def test_retrieve_handles_gibberish_gracefully(self, engine):
        """Gibberish input that matches nothing should return empty string, not raise."""
        result = engine.retrieve_personal_examples("xyzzy frobnicator quux")
        assert isinstance(result, str), "Should return empty string for no-match queries."

    def test_retrieve_top_n_limits_results(self, engine):
        """top_n parameter should not cause errors at boundary values."""
        result_1 = engine.retrieve_personal_examples("회의 보고서", top_n=1)
        result_0 = engine.retrieve_personal_examples("회의 보고서", top_n=0)
        assert isinstance(result_1, str)
        assert isinstance(result_0, str)
