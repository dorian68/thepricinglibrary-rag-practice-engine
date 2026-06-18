from __future__ import annotations

from .generation import MaterialGenerator
from .schemas import CourseRequest, ExerciseRequest, GenerationResponse


class PracticeAgent:
    """Small product-facing agent around the RAG material generator.

    The agent keeps the product promise explicit: start from a desk task,
    generate usable practice material, and end with a worked correction and
    operational action.
    """

    def __init__(self, generator: MaterialGenerator) -> None:
        self.generator = generator

    def create_exercise(self, request: ExerciseRequest) -> GenerationResponse:
        augmented = request.model_copy(
            update={
                "free_prompt": self._augment_exercise_prompt(request),
                "require_calculations": True,
                "target_audience": (
                    "learners training for market finance, pricing, risk, "
                    "structuring or trading desk work"
                ),
            }
        )
        response = self.generator.generate_exercise(augmented)
        response.metadata["agent"] = {
            "name": "ThePricingLibrary Practice Agent",
            "mode": "desk_case_generation",
            "contract": [
                "practice_first",
                "source_grounded",
                "worked_correction",
                "operational_action",
            ],
        }
        return response

    def create_course(self, request: CourseRequest) -> GenerationResponse:
        augmented = request.model_copy(
            update={
                "target_audience": (
                    "learners who want to practice market finance through "
                    "desk cases, calculations and risk decisions"
                ),
            }
        )
        response = self.generator.generate_course(augmented)
        response.metadata["agent"] = {
            "name": "ThePricingLibrary Practice Agent",
            "mode": "practice_course_generation",
            "contract": [
                "desk_workflow",
                "minimum_theory",
                "labs",
                "assessment_grid",
            ],
        }
        return response

    def _augment_exercise_prompt(self, request: ExerciseRequest) -> str:
        user_prompt = request.free_prompt or ""
        product = request.product or "produit de finance de marche"
        concept = request.concept or request.topic or "pricing et risque"
        return f"""
Mission produit ThePricingLibrary:
Construire un exercice pratique comme en salle de marche, pas une fiche de
theorie. L'apprenant doit partir d'une situation concrete, lire les donnees,
calculer, interpreter, puis proposer une action operationnelle.

Produit: {product}
Concept: {concept}
Niveau: {request.difficulty}
Format: {request.exercise_format}

Structure obligatoire:
1. Brief de desk.
2. Donnees de marche.
3. Mission apprenant.
4. Questions/taches.
5. Corrige commente avec formules, substitutions et nombres finaux.
6. Decision operationnelle: hedge, monitor, reduce, quote, reject ou escalate.
7. Limites du modele et erreurs courantes.

Contraintes donnees par l'utilisateur:
{user_prompt or "Aucune contrainte numerique additionnelle."}
""".strip()
