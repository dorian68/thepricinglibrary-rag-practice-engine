"""Questions, answer key and rubric derived from the same verified pack."""
from __future__ import annotations

import re

from .calculators import CalculationPack
from .schemas import ExerciseRequest


def build_assessment(request: ExerciseRequest, pack: CalculationPack) -> dict:
    if request.language == "en":
        from .exercise_english import build_english_assessment
        return build_english_assessment(request, pack)
    count = request.number_of_questions
    context = request.product or request.topic or pack.title
    explanations = "\n".join(f"- {item}" for item in pack.assumptions if not item.startswith("Moteur canonique"))
    actions = "\n".join(f"- {item}" for item in pack.desk_actions)
    warnings = "\n".join(f"- {item}" for item in pack.warnings) or explanations
    mode = request.exercise_format
    focus = {
        "quantitative_problem": "justifier le calcul et contrôler les unités",
        "risk_management": "identifier les expositions et justifier la couverture",
        "trading_decision": "justifier une décision de cotation ou de couverture",
        "case_study": "rédiger un diagnostic de desk fondé sur les données",
        "mixed": "relier calcul, contrôle et décision",
    }[mode]
    questions = []

    def add(prompt, answer, criterion):
        questions.append({"number": len(questions) + 1, "prompt": prompt,
                          "answer": answer, "criterion": criterion})

    if count >= 3:
        add(f"Pour {context}, {focus}. Identifier le produit, les données et les conventions utiles.",
            f"Produit / calcul : **{pack.title}**.\n\n{explanations}",
            f"Produit, sens de la position et conventions de {pack.title} correctement identifiés.")
    slots = max(1, min(len(pack.steps), count - (2 if count >= 3 else 1 if count == 2 else 0)))
    groups = [pack.steps[i * len(pack.steps) // slots:(i + 1) * len(pack.steps) // slots] for i in range(slots)]
    for steps in groups:
        names = ", ".join(step.label for step in steps)
        scaffold = ""
        if request.difficulty == "beginner":
            scaffold = " Aide : " + "; ".join(f"{step.label} = {step.formula}" for step in steps) + "."
        elif request.difficulty == "advanced":
            scaffold = " Justifier les conventions, puis distinguer résultat du modèle et approximation utilisée."
        elif request.difficulty == "expert":
            scaffold = " Auditer les hypothèses et les signes ; expliquer dans quelles conditions ces résultats cessent d'être une valorisation fiable."
        answer = "\n\n".join(
            f"**{step.label}**\n\n- Formule : `{step.formula}`\n- Substitution : `{step.substitution}`\n"
            f"- Résultat : **{step.result}**\n- Lecture : {step.desk_comment}" for step in steps)
        if request.difficulty in {"advanced", "expert"}:
            answer += "\n\n**Hypothèses et limites à contrôler**\n" + warnings
        if count == 1:
            answer += "\n\n**Décision de desk**\n" + actions
        add(f"Calculer {names}, puis {focus}.{scaffold}", answer,
            f"Formules, substitutions, signes et unités de {names} ; interprétation cohérente avec les hypothèses.")
    reviews = [
        ("Contrôler les unités et l'horizon des résultats obtenus.", explanations),
        ("Expliquer le sens économique des résultats avant de proposer un hedge.", "\n".join(f"- {s.label} : {s.result}. {s.desk_comment}" for s in pack.steps)),
        ("Identifier les hypothèses à revalider avant de réutiliser ce calcul sur un ticket réel.", warnings),
        ("Distinguer les données du cas pédagogique d'une cotation de marché exécutable.", "Les données sont celles de cet énoncé pédagogique. Aucune cotation live ni liquidité exécutable n'est prouvée.\n" + explanations),
        ("Décrire le contrôle à effectuer avant de choisir l'instrument de couverture.", actions),
        ("Rédiger une note de risque à partir du calcul, sans inventer de sensibilité supplémentaire.", warnings + "\n" + actions),
        ("Expliquer les limites d'une réutilisation du résultat sous une autre convention.", explanations + "\n" + warnings),
        ("Séparer ce qui est calculé de ce qui doit être confirmé avec le desk.", "Résultats calculés : " + "; ".join(s.label for s in pack.steps) + ".\n" + warnings),
    ]
    while len(questions) < count - 1:
        prompt, answer = reviews[(len(questions) - slots - (1 if count >= 3 else 0)) % len(reviews)]
        add(prompt, answer, f"Contrôle argumenté et relié aux hypothèses de {pack.title}, sans nombre inventé.")
    if len(questions) < count:
        add(f"Conclure : {focus}. Préciser l'action, les conditions de suivi et les limites du modèle.",
            actions + "\n\n**Limites**\n" + warnings,
            f"Décision reliée aux résultats de {pack.title}, sens du hedge et limites explicités.")
    for i, question in enumerate(questions):
        question["points"] = 100 // count + (1 if i < 100 % count else 0)
    return {"question_count": count, "total_points": 100, "questions": questions,
            "grading_mode": "self_review", "difficulty": request.difficulty, "format": mode}


def assessment_markdown(assessment: dict) -> tuple[str, str, str]:
    english = assessment.get("language") == "en"
    questions = "\n".join(f'{q["number"]}. {q["prompt"]}' for q in assessment["questions"])
    answer_label = "Answer" if english else "Réponse"
    answers = "\n\n".join(f'### {answer_label} {q["number"]}\n\n{q["answer"]}' for q in assessment["questions"])
    rubric = ("| Question | Success criteria | Points |\n" if english else "| Question | Critères de réussite | Points |\n") + "| --- | --- | ---: |\n" + "\n".join(
        f'| {q["number"]} | {q["criterion"].replace("|", "/")} | {q["points"]} |' for q in assessment["questions"])
    rubric += ("\n\n**Total: 100 points.** Self-review against the worked correction; no automatic grade is claimed."
               if english else "\n\n**Total : 100 points.** Auto-évaluation avec corrigé ; aucune note automatique n'est revendiquée.")
    return questions, answers, rubric


def assessment_matches_document(content: str, assessment: dict) -> bool:
    if assessment.get("language") == "en" and not all(
        heading in content for heading in ("## Desk brief", "## Problem", "## Verified solution", "## Assessment rubric")
    ):
        return False
    section = re.search(r"## Questions\n([\s\S]*?)\n---", content)
    if not section:
        return False
    prompts = re.findall(r"^\d+\. (.+)$", section.group(1), re.M)
    expected = assessment["questions"]
    label = "Answer" if assessment.get("language") == "en" else "Réponse"
    answers = re.findall(r"^### " + label + r" (\d+)", content, re.M)
    rows = re.findall(r"^\| (\d+) \| [^\n]+ \| (\d+) \|$", content, re.M)
    return (prompts == [q["prompt"] for q in expected]
            and answers == [str(q["number"]) for q in expected]
            and rows == [(str(q["number"]), str(q["points"])) for q in expected]
            and "Mission produit" not in content and "Structure obligatoire" not in content)
