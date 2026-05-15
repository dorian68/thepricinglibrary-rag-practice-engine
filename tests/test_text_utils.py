from pricinglibrary_rag.text_utils import chunk_text, keyword_scores, tokenize


def test_chunk_text_with_overlap() -> None:
    text = ("Options pricing links payoff, volatility and discounting. " * 220).strip()
    chunks = chunk_text(text, target_chars=900, overlap_chars=120)
    assert len(chunks) > 1
    assert all(chunk.content for chunk in chunks)
    assert chunks[1].start_char < chunks[0].end_char


def test_keyword_scores_returns_terms() -> None:
    scores = keyword_scores(
        [
            "delta hedging option volatility option",
            "credit spread default intensity credit",
        ],
        top_k=5,
    )
    terms = [term for term, _ in scores]
    assert "option" in terms or "credit" in terms


def test_tokenize_filters_stopwords() -> None:
    assert "the" not in tokenize("the option volatility surface")
    assert "option" in tokenize("the option volatility surface")

