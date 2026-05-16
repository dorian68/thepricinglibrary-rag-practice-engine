from pricinglibrary_rag.evaluation import ProductEvaluator
from pricinglibrary_rag.schemas import GenerationResponse, SourceRef


def test_evaluator_scores_operational_exercise() -> None:
    response = GenerationResponse(
        kind="exercise",
        title="Desk case",
        content=(
            "# Cas pratique\n"
            "## Corrige\n"
            "P&L delta = -500,000 EUR [S1]. "
            "Le trader couvre delta et monitor le gamma."
        ),
        sources=[
            SourceRef(
                document_id="doc",
                chunk_id="chunk",
                title="source",
                source="source.pdf",
                chunk_index=1,
                score=0.9,
                vector_score=0.5,
                lexical_score=1.0,
                snippet="delta gamma hedge",
            )
        ],
        metadata={
            "calculation_pack": {
                "family": "options_book_greeks",
            }
        },
    )
    result = ProductEvaluator().evaluate_response(response)
    assert result["passed"]
    assert result["score"] >= 0.78


def test_default_evaluation_cases_cover_core_library() -> None:
    names = {name for name, _ in ProductEvaluator().default_cases()}
    assert "options_book_greeks" in names
    assert "rates_swap_dv01" in names
    assert "fx_barrier_option" in names
    assert "cds_cs01" in names
    assert "parametric_var" in names

