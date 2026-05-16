from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .generation import MaterialGenerator
from .schemas import EvaluationReport, ExerciseRequest, GenerationResponse


@dataclass(frozen=True)
class QualityCheck:
    name: str
    passed: bool
    weight: float
    detail: str


class ProductEvaluator:
    """Quality gates for practice-first course/exercise generation."""

    def default_cases(self) -> list[tuple[str, ExerciseRequest]]:
        return [
            (
                "options_book_greeks",
                ExerciseRequest(
                    topic="Options book risk management",
                    product="equity options book",
                    concept="delta gamma vega theta hedging",
                    difficulty="intermediate",
                    exercise_format="risk_management",
                    number_of_questions=6,
                    free_prompt=(
                        "Genere un exercice pratique de risk management sur un book d'options actions. "
                        "Donnees imposees: book delta +250k EUR par 1%, gamma -80k EUR par 1%^2, "
                        "vega +120k EUR par vol point, theta -15k EUR par jour. Scenario: spot -2%, "
                        "vol +3 points, un jour passe. L'etudiant doit estimer P&L delta-gamma-vega-theta, "
                        "identifier le risque dominant, proposer une couverture delta et vega."
                    ),
                ),
            ),
            (
                "rates_swap_dv01",
                ExerciseRequest(
                    topic="Interest rate swap valuation and DV01",
                    product="EUR interest rate swap",
                    concept="PV, par rate, DV01, hedge PnL",
                    difficulty="intermediate",
                    exercise_format="quantitative_problem",
                    number_of_questions=6,
                    free_prompt=(
                        "Genere un exercice operationnel de desk rates. Donnees imposees: payer swap EUR 5Y, "
                        "notionnel 100m, fixed coupon 3.20%, par swap rate actuel 3.00%, annuity approx 4.55, "
                        "la courbe monte de 10bp. Calculer PV, DV01, P&L et couverture."
                    ),
                ),
            ),
            (
                "fx_barrier_option",
                ExerciseRequest(
                    topic="FX barrier option desk case",
                    product="FX barrier option",
                    concept="down-and-out call, gap risk",
                    difficulty="advanced",
                    exercise_format="quantitative_problem",
                    number_of_questions=6,
                    free_prompt=(
                        "Option barriere FX. EUR/USD spot 1.0800, strike 1.1000, "
                        "barriere down-and-out 1.0000, notionnel EUR 10m. Scenarios spot a 1.0500, "
                        "spot a 1.0000, spot a 1.2000 sans knock-out. Evaluer payoff et gap risk."
                    ),
                ),
            ),
            (
                "vanilla_option_black_scholes",
                ExerciseRequest(
                    topic="Black-Scholes call desk approximation",
                    product="equity call option",
                    concept="price delta gamma vega",
                    difficulty="intermediate",
                    exercise_format="quantitative_problem",
                    number_of_questions=5,
                    free_prompt="Call vanilla spot 100 strike 100 vol 20% maturite 1 taux 5%. Calculer prix et greeks.",
                ),
            ),
            (
                "cds_cs01",
                ExerciseRequest(
                    topic="CDS CS01 and spread shock",
                    product="single-name CDS",
                    concept="CS01 carry spread shock",
                    difficulty="advanced",
                    exercise_format="risk_management",
                    number_of_questions=5,
                    free_prompt="CDS notionnel 50m spread 120bp risky annuity 4.2 shock 25bp. Calculer CS01, carry et P&L spread.",
                ),
            ),
            (
                "parametric_var",
                ExerciseRequest(
                    topic="Parametric VaR desk limit",
                    product="portfolio",
                    concept="VaR stress risk limit",
                    difficulty="beginner",
                    exercise_format="risk_management",
                    number_of_questions=5,
                    free_prompt="VaR portefeuille 20m volatilite 2% confiance 95% horizon 1 jour. Calculer VaR et discuter limite.",
                ),
            ),
        ]

    def evaluate_response(self, response: GenerationResponse | dict[str, Any]) -> dict[str, Any]:
        if isinstance(response, GenerationResponse):
            payload = response.model_dump()
        else:
            payload = response
        content = str(payload.get("content") or "")
        sources = payload.get("sources") or []
        metadata = payload.get("metadata") or {}
        pack = metadata.get("calculation_pack") or {}
        checks = [
            self._check("sources", bool(sources), 1.0, f"{len(sources)} sources"),
            self._check("source_markers", bool(re.search(r"\[S\d+\]", content)), 0.8, "markers [Sx] in content"),
            self._check("worked_numbers", bool(re.search(r"\d", content)), 1.0, "numeric content"),
            self._check("correction", bool(re.search(r"(?i)corrig|solution|answer key", content)), 1.0, "correction section"),
            self._check("formula", bool(re.search(r"(?i)formule|formula|P&L|DV01|delta|gamma|vega|VaR|CS01|payoff|PV", content)), 1.0, "formula/risk terms"),
            self._check("desk_action", bool(re.search(r"(?i)hedg|couver|monitor|surveill|rebalance|quote|no-trade|risk manager|trader", content)), 1.0, "operational decision"),
            self._check("not_generic", "a fixer par l'enseignant" not in content.lower(), 0.8, "no generic placeholders"),
            self._check("calculator", (pack.get("family") or "generic") != "generic", 1.2, f"calculator={pack.get('family')}"),
        ]
        score = self._score(checks)
        return {
            "score": score,
            "passed": score >= 0.78,
            "checks": [check.__dict__ for check in checks],
            "title": payload.get("title"),
            "kind": payload.get("kind"),
        }

    def run_generation_suite(
        self,
        generator: MaterialGenerator,
        *,
        limit: int | None = None,
    ) -> EvaluationReport:
        results = []
        cases = self.default_cases()[:limit] if limit else self.default_cases()
        for name, request in cases:
            response = generator.generate_exercise(request)
            evaluation = self.evaluate_response(response)
            evaluation["case"] = name
            evaluation["request"] = request.model_dump()
            results.append(evaluation)
        passed = sum(1 for item in results if item["passed"])
        failed = len(results) - passed
        avg = sum(float(item["score"]) for item in results) / max(len(results), 1)
        return EvaluationReport(
            total=len(results),
            passed=passed,
            failed=failed,
            average_score=round(avg, 4),
            results=results,
        )

    def _check(self, name: str, passed: bool, weight: float, detail: str) -> QualityCheck:
        return QualityCheck(name=name, passed=passed, weight=weight, detail=detail)

    def _score(self, checks: list[QualityCheck]) -> float:
        total = sum(check.weight for check in checks)
        hit = sum(check.weight for check in checks if check.passed)
        return round(hit / max(total, 1e-9), 4)

