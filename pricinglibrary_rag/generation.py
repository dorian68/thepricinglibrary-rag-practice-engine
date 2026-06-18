from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .calculators import CalculationPack, PracticeCalculator
from .course_blocks import (
    PROVENANCE_LEGEND,
    audience_for,
    corrected_exercise_markdown,
    detect_topic_key,
    prerequisites,
    quiz_markdown,
    seed_for_topic,
    worked_example_markdown,
)
from .llm import LocalLLM
from .pedagogy import (
    PEDAGOGICAL_FLOW,
    classify_chunk,
    detect_pedagogical_gaps,
    stage_covered,
    summarize_pedagogy,
)
from .retrieval import LocalRetriever, RetrievedChunk
from .schemas import (
    CourseRequest,
    ExerciseRequest,
    GenerationResponse,
    MaterialPackRequest,
    SearchRequest,
    SourceRef,
)
from .storage import LocalStore
from .text_utils import (
    clean_snippet,
    concise_snippet,
    keyword_scores,
    split_sentences,
    stable_id,
)


@dataclass(frozen=True)
class GenerationContext:
    query: str
    retrieved: list[RetrievedChunk]
    sources: list[SourceRef]
    facts: list[str]
    keywords: list[str]
    coverage: dict
    gaps: dict
    source_pedagogy: list[dict]


class MaterialGenerator:
    def __init__(
        self,
        retriever: LocalRetriever,
        llm: LocalLLM,
        store: LocalStore | None = None,
    ) -> None:
        self.retriever = retriever
        self.llm = llm
        self.store = store
        self.calculator = PracticeCalculator()

    def generate_exercise(self, request: ExerciseRequest) -> GenerationResponse:
        query = self._exercise_query(request)
        context = self._build_context(
            SearchRequest(
                query=query,
                top_k=request.top_k,
                product=request.product,
                concept=request.concept,
            )
        )
        title = self._exercise_title(request)
        draft = self._exercise_template(request, title, context)
        prompt = self._wrap_prompt(
            role="practical exercise designer",
            language=request.language,
            task=(
                "Create a practical market-finance exercise. It must teach by "
                "doing, stay grounded in retrieved context, include a solution, "
                "and avoid unsupported formulas."
            ),
            context=context,
            draft=draft,
        )
        content = self.llm.generate(prompt, max_tokens=2600)
        response = GenerationResponse(
            kind="exercise",
            title=title,
            content=content,
            sources=context.sources,
            metadata={
                "llm": self.llm.name,
                "query": context.query,
                "difficulty": request.difficulty,
                "format": request.exercise_format,
                "calculation_pack": self._calculation_pack(request).model_dump(),
            },
        )
        self._save("exercise", request.model_dump(), response.model_dump())
        return response

    def generate_course(self, request: CourseRequest) -> GenerationResponse:
        query = self._course_query(request)
        context = self._build_context(
            SearchRequest(
                query=query,
                top_k=request.top_k,
                product=request.product,
                concept=" ".join(request.concepts) if request.concepts else None,
            ),
            usable_only=True,
            min_quality=45,
        )
        title = f"Module pratique - {request.topic}"
        # Per-lesson authoring: each lesson body is written on its own (LLM call
        # per lesson, grounded in that lesson's source) inside _course_template,
        # so no two lessons share a skeleton. The verified blocks (worked example
        # with engine-computed numbers, quiz, corrected exercises, noise-filtered
        # sources) are appended verbatim, so an LLM can never paraphrase a number.
        # We deliberately do NOT do a second whole-draft rewrite: that step used
        # to homogenise every lesson into one fill-in-the-blank template.
        prose = self._course_template(request, title, context)
        appendix = self._course_appendix(request, context)
        content = f"{prose.strip()}\n\n{appendix}".strip()
        response = GenerationResponse(
            kind="course",
            title=title,
            content=content,
            sources=context.sources,
            metadata={
                "llm": self.llm.name,
                "query": context.query,
                "level": request.level,
                "duration_minutes": request.duration_minutes,
                "library_track": self._library_track(request.topic, request.product),
                "source_coverage": context.coverage,
                "pedagogical_gaps": context.gaps,
            },
        )
        self._save("course", request.model_dump(), response.model_dump())
        return response

    def generate_material_pack(self, request: MaterialPackRequest) -> GenerationResponse:
        course = self.generate_course(
            CourseRequest(
                topic=request.topic,
                product=request.product,
                concepts=request.concepts,
                level=request.level,
                duration_minutes=request.duration_minutes,
                module_count=4,
                language=request.language,
            )
        )
        exercises = []
        for idx in range(max(request.exercise_count, 1)):
            concept = request.concepts[idx % len(request.concepts)] if request.concepts else None
            exercise_prompt = (
                f"Construis un cas pratique operationnel pour le module {request.topic}. "
                f"Produit: {request.product or 'multi-produits'}. "
                f"Concept cible: {concept or request.topic}. "
                "Le cas doit inclure donnees numeriques, taches de desk, corrige, "
                "interpretation des risques et decision operationnelle."
            )
            exercises.append(
                self.generate_exercise(
                    ExerciseRequest(
                        topic=request.topic,
                        product=request.product,
                        concept=concept,
                        free_prompt=exercise_prompt,
                        difficulty=request.level,
                        exercise_format="mixed",
                        number_of_questions=5,
                        language=request.language,
                    )
                )
            )

        sections = [course.content]
        sections.append("\n\n# Banque d'exercices pratiques\n")
        for idx, exercise in enumerate(exercises, start=1):
            sections.append(f"\n\n## Exercice {idx} - {exercise.title}\n\n{exercise.content}")
        sources = self._dedupe_sources(
            [*course.sources, *[src for ex in exercises for src in ex.sources]]
        )
        title = f"Pack pedagogique - {request.topic}"
        response = GenerationResponse(
            kind="material_pack",
            title=title,
            content="\n".join(sections).strip(),
            sources=sources,
            metadata={
                "llm": self.llm.name,
                "exercise_count": len(exercises),
            },
        )
        self._save("material_pack", request.model_dump(), response.model_dump())
        return response

    def _build_context(
        self,
        request: SearchRequest,
        *,
        usable_only: bool = False,
        min_quality: int | None = None,
    ) -> GenerationContext:
        retrieved = self.retriever.retrieve(
            request.query,
            top_k=request.top_k,
            product=request.product,
            concept=request.concept,
            asset_class=request.asset_class,
            tags=request.tags,
            usable_only=usable_only,
            min_quality=min_quality,
        )
        sources = [self.retriever.to_source_ref(item) for item in retrieved]
        text_blocks = [item.chunk.content for item in retrieved]
        facts = self._extract_facts(text_blocks, max_facts=10)
        keywords = [term for term, _ in keyword_scores(text_blocks, top_k=16)]
        pedagogy_items = [self._chunk_pedagogy(item.chunk) for item in retrieved]
        coverage = summarize_pedagogy(pedagogy_items)
        gaps = detect_pedagogical_gaps(pedagogy_items)
        return GenerationContext(
            query=request.query,
            retrieved=retrieved,
            sources=sources,
            facts=facts,
            keywords=keywords,
            coverage=coverage,
            gaps=gaps,
            source_pedagogy=pedagogy_items,
        )

    def _chunk_pedagogy(self, chunk) -> dict:
        """Return the chunk's persisted pedagogy block, classifying on the fly
        if the chunk predates pedagogical ingestion (no backfill yet)."""
        pedagogy = (chunk.metadata or {}).get("pedagogy")
        if isinstance(pedagogy, dict) and pedagogy.get("content_type"):
            return pedagogy
        return classify_chunk(
            chunk.content, section_title=chunk.section_title
        ).to_metadata()

    def _extract_facts(self, blocks: list[str], max_facts: int = 10) -> list[str]:
        facts: list[str] = []
        for block in blocks:
            for sentence in split_sentences(block):
                # clean_snippet rejects mid-word/noisy fragments (returns "").
                cleaned = clean_snippet(sentence, max_chars=280)
                if cleaned and 60 <= len(cleaned) <= 280:
                    facts.append(cleaned)
                if len(facts) >= max_facts:
                    return facts
        if facts:
            return facts
        # fallback: clean snippet of each block, dropping the noisy ones
        return [s for s in (clean_snippet(block, max_chars=240) for block in blocks[:max_facts]) if s]

    def _exercise_query(self, request: ExerciseRequest) -> str:
        parts = [
            request.free_prompt or "",
            request.topic or "",
            request.product or "",
            request.concept or "",
            request.exercise_format,
            request.difficulty,
            "pricing valuation risk hedging payoff scenario market finance",
        ]
        return " ".join(part for part in parts if part).strip()

    def _course_query(self, request: CourseRequest) -> str:
        parts = [
            request.topic,
            request.product or "",
            " ".join(request.concepts),
            request.level,
            "market finance pricing risk valuation hedging practical course",
        ]
        return " ".join(part for part in parts if part).strip()

    def _exercise_title(self, request: ExerciseRequest) -> str:
        focus = request.topic or request.product or request.concept or "finance de marche"
        if len(focus) > 90:
            focus = focus[:87].rstrip() + "..."
        return f"Cas pratique - {focus}"

    def _source_lines(self, context: GenerationContext) -> str:
        if not context.sources:
            return "- Aucune source retrouvee localement."
        lines = []
        for idx, src in enumerate(context.sources, start=1):
            label = src.title or src.source or src.document_id
            base = f"- [S{idx}] {label}, chunk {src.chunk_index}, score {src.score}"
            # Show a clean excerpt only when one survived noise filtering;
            # otherwise cite the reference without a garbled quote.
            if src.snippet:
                lines.append(f"{base}: {src.snippet}")
            else:
                lines.append(f"{base} (extrait non cite: source bruitee)")
        return "\n".join(lines)

    def _facts_lines(self, context: GenerationContext) -> str:
        if not context.facts:
            return "- Aucun fait extrait."
        return "\n".join(f"- {fact}" for fact in context.facts)

    _CONTENT_TYPE_LABELS_FR = {
        "definition": "definitions",
        "intuition": "intuitions",
        "formula": "formules",
        "example": "exemples",
        "worked_example": "exemples resolus",
        "exercise": "exercices",
        "solution": "corriges",
        "case_study": "cas pratiques",
        "summary": "resumes",
    }

    def _coverage_lines(self, context: GenerationContext) -> str:
        cov = context.coverage or {}
        if not cov.get("total"):
            return "- Aucune source exploitable retrouvee pour ce sujet."
        dist = cov.get("content_type_distribution", {})
        dist_str = ", ".join(f"{ct}: {n}" for ct, n in list(dist.items())[:8]) or "n/a"
        return "\n".join(
            [
                f"- Chunks sources analyses: {cov['total']} (exploitables: {cov['usable']}).",
                f"- Score pedagogique moyen: {cov['average_pedagogical_value']}/100 "
                f"(qualite structurelle: {cov['average_quality_score']}/100).",
                f"- Definitions: {cov['definitions']} | exemples: {cov['examples']} | "
                f"exercices: {cov['exercises']} | formules: {cov['formulas']} | "
                f"cas pratiques: {cov['case_studies']}.",
                f"- Repartition par type: {dist_str}.",
            ]
        )

    def _adaptive_plan_lines(self, context: GenerationContext) -> str:
        """Build the lesson flow from what the sources actually provide.

        Each canonical stage is mapped to the source chunks [Sx] that cover it,
        or explicitly flagged as to-be-generated when no source supports it.
        """
        peds = context.source_pedagogy or []
        if not peds:
            return "- Aucune source exploitable: plan a construire manuellement."
        lines = []
        for position, stage in enumerate(PEDAGOGICAL_FLOW, start=1):
            covering = [
                f"[S{idx + 1}]"
                for idx, ped in enumerate(peds)
                if stage_covered(ped, stage)
            ]
            label = self._CONTENT_TYPE_LABELS_FR.get(stage, stage)
            if covering:
                lines.append(
                    f"{position}. {label.capitalize()} - couvert par "
                    f"{', '.join(covering[:4])}."
                )
            else:
                lines.append(
                    f"{position}. {label.capitalize()} - ABSENT des sources: "
                    f"a generer et marquer 'genere a partir des concepts'."
                )
        return "\n".join(lines)

    def _gaps_lines(self, context: GenerationContext) -> str:
        gaps = context.gaps or {}
        status = gaps.get("status", "not_usable")
        status_label = {
            "usable": "Sources suffisantes pour un cours complet.",
            "partially_usable": "Sources partiellement suffisantes: completer les manques.",
            "not_usable": "Sources insuffisantes: ne pas fabriquer le contenu manquant.",
        }.get(status, status)
        missing = gaps.get("missing", [])
        present = gaps.get("present", [])
        lines = [f"- Statut: {status} - {status_label}"]
        if present:
            present_fr = [self._CONTENT_TYPE_LABELS_FR.get(s, s) for s in present]
            lines.append(f"- Presents dans les sources: {', '.join(present_fr)}.")
        if missing:
            missing_fr = [self._CONTENT_TYPE_LABELS_FR.get(s, s) for s in missing]
            lines.append(
                f"- Absents des sources (a marquer 'genere a partir des concepts', "
                f"pas 'extrait'): {', '.join(missing_fr)}."
            )
        else:
            lines.append("- Aucun trou majeur: tous les blocs pedagogiques cles sont couverts.")
        return "\n".join(lines)

    def _exercise_template(
        self,
        request: ExerciseRequest,
        title: str,
        context: GenerationContext,
    ) -> str:
        product = request.product or "instrument a identifier dans le contexte"
        concept = request.concept or request.topic or "concept principal"
        requested_case = request.free_prompt or "Aucune contrainte numerique imposee."
        numeric_controls = self._numeric_control_block(request)
        calc_line = (
            "Inclure des calculs progressifs et une interpretation economique."
            if request.require_calculations
            else "Privilegier le raisonnement qualitatif et la decision."
        )
        return f"""
# {title}

## Brief de desk
Tu arrives sur un desk et tu dois traiter un cas concret autour de {product}.
Le but est de produire un calcul exploitable, une interpretation risque et une
action operationnelle. La theorie n'apparait que si elle sert directement la
decision.

## Niveau et format
- Niveau: {request.difficulty}
- Format: {request.exercise_format}
- Public: {request.target_audience}
- Nombre de questions: {request.number_of_questions}
- Consigne: {calc_line}

## Contraintes donnees par le demandeur
{requested_case}

## Donnees de marche et garde-fous numeriques
{numeric_controls}

## Donnees a completer
- Reprendre toutes les donnees numeriques imposees ci-dessus.
- Si une donnee manque, poser une hypothese simple et visible.
- Distinguer donnees de marche observees, approximation de pricing et jugement de trader.

## Mission apprenant
{self._numbered_questions(request)}

## Methode attendue
- Commencer par qualifier le payoff, le risque principal et la sensibilite dominante.
- Relier chaque calcul a une intuition economique.
- Justifier toute approximation.
- Montrer les formules utilisees avant l'application numerique.
- Terminer par une decision operationnelle: hedge, monitoring, escalation ou no-trade.

## Corrige commente
Le corrige doit etre directement utilisable:
- rappeler les hypotheses;
- derouler la methode et les calculs numeriques;
- donner l'interpretation financiere;
- expliquer ce que ferait un trader, un sales ou un risk manager;
- signaler les limites du raisonnement;
- citer les extraits sources pertinents.

## Decision operationnelle
Conclure explicitement par une action: hedge, rebalance, monitor, escalate,
quote, reject ou no-trade. Preciser le declencheur de suivi.

## Grille d'evaluation
- Identification du produit et des risques: 25%.
- Methode de valorisation ou de decision: 30%.
- Calculs et coherence numerique: 25%.
- Interpretation marche et communication: 20%.

## Sources RAG a exploiter
{self._source_lines(context)}
""".strip()

    def _numbered_questions(self, request: ExerciseRequest) -> str:
        base = [
            "Identifier le produit, son payoff ou sa logique economique.",
            "Lister les variables de marche qui pilotent sa valeur ou son risque.",
            "Construire une methode de resolution praticable par un analyste junior.",
            "Calculer ou estimer le resultat demande avec les donnees disponibles.",
            "Interpréter le resultat et proposer une decision ou une couverture.",
            "Presenter les limites du modele et les risques de mauvaise utilisation.",
        ]
        selected = base[: max(1, min(request.number_of_questions, len(base)))]
        return "\n".join(f"{idx}. {question}" for idx, question in enumerate(selected, start=1))

    def _course_template(
        self,
        request: CourseRequest,
        title: str,
        context: GenerationContext,
    ) -> str:
        modules = []
        module_plan = self._course_module_plan(request)
        for idx, module in enumerate(module_plan[: max(request.module_count, 1)], start=1):
            modules.append(
                f"""
### Module {idx} - {module["title"]}
- Objectif pratique: {module["objective"]}
- Situation de desk: {module["situation"]}
- Notion utile: {module["notion"]}
- Activite: {module["activity"]}
- Livrable apprenant: {module["deliverable"]}
""".strip()
            )
        written_lessons = self._course_written_lessons(module_plan, context, request)
        labs = self._course_labs(request)
        topic_key = detect_topic_key(request.topic, request.product, request.concepts)
        prereq_lines = "\n".join(f"- {item}" for item in prerequisites(topic_key))
        return f"""
# {title}

{PROVENANCE_LEGEND}

## Promesse du module
Apprendre {request.topic} par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: {request.level}
- Public vise: {audience_for(request.level)}
- Duree estimee: {request.duration_minutes} minutes
- Produit: {request.product or 'multi-produits'}
- Concepts: {', '.join(request.concepts) if request.concepts else 'a deduire du contexte'}

## Prerequis
{prereq_lines}

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

## Positionnement bibliotheque
- Track: {self._library_track(request.topic, request.product)["track"]}
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
{chr(10).join(modules)}

## Cours redige
{written_lessons}

## Labs pratiques a inclure
{chr(10).join(f"{idx}. {lab}" for idx, lab in enumerate(labs, start=1))}

## Script enseignant
1. Ouvrir par un cas concret.
2. Demander aux apprenants de formuler l'intuition.
3. Introduire la notation minimale.
4. Faire resoudre une micro-tache.
5. Debrief: erreurs courantes, limites, interpretation marche.

## Supports a produire
- Fiche apprenant d'une page.
- Slides courtes orientees cas.
- Notebook ou tableur de calcul si le sujet s'y prete.
- Corrige detaille.
- Quiz de verification rapide.
""".strip()

    def _normalize_course_headings(self, text: str) -> str:
        """Canonicalise heading lines so an LLM's accented variants
        (``### Leçon 1``, ``## Cours rédigé``) still match the parser/audit,
        which expect unaccented headings. Only ``#``-lines are touched; body
        prose keeps its natural French accents.
        """
        out = []
        for line in (text or "").splitlines():
            if line.lstrip().startswith("#"):
                line = "".join(
                    c for c in unicodedata.normalize("NFKD", line)
                    if not unicodedata.combining(c)
                )
            out.append(line)
        return "\n".join(out)

    def _guard_course_prose(self, written: str, fallback: str) -> str:
        """Never let an LLM rewrite degrade the course below the deterministic
        baseline: if it dropped the lesson structure or returned too little,
        keep the structured prose draft instead."""
        text = (written or "").strip()
        has_lessons = len(re.findall(r"(?im)^###\s+Lecon\s+\d+", text)) >= 1
        has_modules = len(re.findall(r"(?im)^###\s+Module\s+\d+", text)) >= 1
        long_enough = len(text) >= int(len(fallback) * 0.6)
        if has_lessons and has_modules and long_enough:
            return text
        return fallback

    def _course_appendix(
        self,
        request: CourseRequest,
        context: GenerationContext,
    ) -> str:
        """Deterministic, verified blocks appended VERBATIM after any LLM prose.

        These must not be paraphrased by an LLM: the worked example carries
        engine-computed numbers, the quiz has fixed answers, and the source
        excerpts are noise-filtered. Keeping them out of the rewrite guarantees
        correctness and a stable, parseable structure.
        """
        topic_key = detect_topic_key(request.topic, request.product, request.concepts)
        worked = worked_example_markdown(topic_key, self.calculator)
        exercises = corrected_exercise_markdown(topic_key, self.calculator)
        quiz = quiz_markdown(topic_key)
        return f"""
## Exemple numerique resolu
{worked}

## Exercices corriges
{exercises}

## Mini-quiz
{quiz}

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
{self._coverage_lines(context)}

## Plan pedagogique adaptatif (base sur les sources)
{self._adaptive_plan_lines(context)}

## Trous pedagogiques (signaler, ne pas inventer)
{self._gaps_lines(context)}

## Faits et angles extraits de la base
{self._facts_lines(context)}

## Sources RAG a citer
{self._source_lines(context)}
""".strip()

    def _course_written_lessons(
        self,
        modules: list[dict[str, str]],
        context: GenerationContext,
        request: CourseRequest,
    ) -> str:
        selected_modules = modules[: max(request.module_count, 1)]
        if not selected_modules:
            return ""

        retrieved = context.retrieved or []
        # Distinct, clean source quotes per lesson so no excerpt repeats and no
        # OCR fragment is shown. clean_snippet returns "" for noise.
        clean_quotes: list[tuple[str, str]] = []  # (text, marker)
        for sidx, item in enumerate(retrieved, start=1):
            quote = clean_snippet(item.chunk.content, max_chars=420)
            if quote:
                clean_quotes.append((quote, f"[S{sidx}]"))

        blocks: list[str] = []
        for idx, module in enumerate(selected_modules, start=1):
            # Distinct source excerpt per lesson (rotates through the clean pool).
            if clean_quotes:
                quote, marker = clean_quotes[(idx - 1) % len(clean_quotes)]
            else:
                quote, marker = "", ""
            body = self._lesson_body(request, module, idx, quote, marker)
            blocks.append(f"### Lecon {idx} - {module['title']}\n\n{body}".strip())
        return "\n\n".join(blocks)

    def _lesson_body(
        self,
        request: CourseRequest,
        module: dict[str, str],
        idx: int,
        quote: str,
        marker: str,
    ) -> str:
        """Author ONE lesson body. Each lesson is written on its own — by the LLM
        when one is available, otherwise by a per-index deterministic frame — so
        no two lessons share a skeleton. Numbers stay out of the prose (the
        verified worked example lives in the appendix), so the LLM cannot
        fabricate a price or a greek here."""
        if self.llm.name != "template":
            try:
                body = self.llm.generate(
                    self._lesson_prompt(request, module, idx, quote, marker),
                    max_tokens=650,
                )
                body = self._clean_lesson_body(body)
                if body and len(body) >= 220:
                    return body
            except Exception:
                pass  # fall through to the deterministic frame
        return self._template_lesson_body(module, idx, quote, marker)

    def _lesson_prompt(
        self,
        request: CourseRequest,
        module: dict[str, str],
        idx: int,
        quote: str,
        marker: str,
    ) -> str:
        if quote:
            source_line = (
                f'Extrait source que tu peux exploiter (cite-le comme {marker} '
                f'quand tu t\'en sers, prefixe par [extrait]):\n"{quote}"'
            )
        else:
            source_line = (
                "Aucun extrait source propre n'est disponible pour cette lecon: "
                "appuie-toi sur le concept et marque ton raisonnement [reformule]."
            )
        return f"""
Tu rediges UNE seule lecon d'un cours de finance de marche, en {request.language}.
Cours: {request.topic}. Niveau: {request.level}. Lecon {idx}: {module['title']}.

Objectif pratique de la lecon: {module['objective']}
Situation de desk: {module['situation']}
Notion centrale a enseigner: {module['notion']}
Activite pratique liee (contexte, ne te contente pas de la repeter): {module['activity']}

{source_line}

Ecris 2 a 4 courts paragraphes qui enseignent reellement CETTE lecon precise:
- Pars d'une intuition de marche concrete et propre a cette notion (jamais une phrase passe-partout).
- Explique le mecanisme et pourquoi cela compte sur un desk de trading.
- Quand tu utilises l'extrait, cite quelques mots et tague {marker or '[reformule]'}.
- Termine par UN piege precis qu'un junior commet sur CETTE notion exacte.

Regles strictes:
- N'invente AUCUNE valeur chiffree reelle (prix, greek, taux de marche): l'exemple numerique verifie est fourni a part. Un ordre de grandeur clairement hypothetique ("imaginons un spot a 100") est autorise comme illustration.
- N'ecris PAS de formule mathematique explicite (pas d'equation comme "C - P = ..."): decris-la en mots; les formules exactes figurent telles quelles dans une section dediee. Cela evite toute formule fausse.
- N'utilise aucune phrase de liaison generique reutilisable d'une lecon a l'autre; chaque lecon doit se lire differemment.
- Pas de titre, pas de liste d'objectifs: de la prose pedagogique fluide (gras en amorce autorise).
- {request.language} uniquement. Ne renvoie que le corps de la lecon, sans le titre '### Lecon'.
""".strip()

    def _clean_lesson_body(self, text: str) -> str:
        """Strip a stray heading the model may have echoed and tidy whitespace."""
        lines = [ln.rstrip() for ln in (text or "").strip().splitlines()]
        kept: list[str] = []
        for ln in lines:
            stripped = ln.lstrip()
            # drop an echoed lesson/section heading or a fenced marker
            if stripped.startswith("### Lecon") or stripped.startswith("### Leçon"):
                continue
            if stripped in ("```", "```markdown", "```md"):
                continue
            kept.append(ln)
        return "\n".join(kept).strip()

    def _template_lesson_body(
        self,
        module: dict[str, str],
        idx: int,
        quote: str,
        marker: str,
    ) -> str:
        """Deterministic offline fallback. Four distinct narrative frames rotate
        by lesson index so adjacent lessons never share the same skeleton."""
        notion = module["notion"].rstrip(". ").strip()
        objective = module["objective"].rstrip(". ").strip()
        situation = module["situation"].rstrip(". ").strip()
        activity = module["activity"].rstrip(". ").strip()
        deliverable = module["deliverable"].rstrip(". ").strip()
        pitfall = self._lesson_pitfall(idx, notion)
        if quote:
            src = f"Les sources le confirment _[extrait]_: « {quote} » {marker}."
        else:
            src = (
                "Les extraits disponibles sont trop bruites pour etre cites ici "
                "_[reformule]_; on s'appuie sur les formules et l'exemple resolu du module."
            )

        frames = [
            # Frame A - intuition first
            (
                f"**Le reflexe d'abord.** {situation} Avant toute formule, demandez-vous "
                f"ce que {notion.lower()} change pour le risque que vous portez. "
                f"{src} L'enjeu operationnel est clair: {objective.lower()}.\n\n"
                f"Concretement, vous {activity.lower()} et vous en tirez un {deliverable.lower()}. "
                f"Le piege a eviter: {pitfall}"
            ),
            # Frame B - mechanism first
            (
                f"**Comment ca marche.** {notion} n'est pas un concept abstrait: c'est le "
                f"mecanisme qui relie {situation.lower()} a une decision chiffree. {src}\n\n"
                f"En pratique, la lecon consiste a {objective.lower()}. Vous {activity.lower()} "
                f"pour produire un {deliverable.lower()}, livrable que le desk peut relire en trente secondes. "
                f"Attention: {pitfall}"
            ),
            # Frame C - risk first
            (
                f"**Ou est le risque.** {situation} Mal traiter {notion.lower()} se paie "
                f"immediatement en P&L. {src}\n\n"
                f"L'objectif de cette lecon est donc tres opérationnel: {objective.lower()}. "
                f"On {activity.lower()}, on documente un {deliverable.lower()}, et on relie chaque chiffre "
                f"a une intuition de signe avant de le transmettre. Erreur classique: {pitfall}"
            ),
            # Frame D - decision first
            (
                f"**La decision visee.** A la fin de cette lecon vous saurez {objective.lower()} "
                f"sans hesiter. Le declencheur: {situation.lower()} {src}\n\n"
                f"La notion de {notion.lower()} sert exactement a cela. Vous {activity.lower()}, "
                f"vous produisez un {deliverable.lower()}, puis vous concluez par une action de desk "
                f"explicite (quote, hedge, hold ou reject). Ne tombez pas dans le piege de {pitfall}"
            ),
        ]
        return frames[(idx - 1) % len(frames)].strip()

    _PITFALLS = (
        "confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.",
        "oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.",
        "appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.",
        "presenter un chiffre sans unite ni ordre de grandeur de controle.",
        "traiter un risque discontinu (barriere, defaut) comme un Greek lisse.",
        "melanger donnee de marche observee, approximation de pricing et jugement de trader.",
    )

    def _lesson_pitfall(self, idx: int, notion: str) -> str:
        return self._PITFALLS[(idx - 1) % len(self._PITFALLS)]

    def _course_module_plan(self, request: CourseRequest) -> list[dict[str, str]]:
        focus = f"{request.topic} {request.product or ''} {' '.join(request.concepts)}".lower()

        def has_any(terms: list[str]) -> bool:
            return any(term in focus for term in terms)

        def has_word(term: str) -> bool:
            return re.search(rf"\b{re.escape(term)}\b", focus) is not None

        def rows(items: list[tuple[str, str, str, str, str]]) -> list[dict[str, str]]:
            return [
                {
                    "title": title,
                    "objective": objective,
                    "situation": situation,
                    "notion": notion,
                    "activity": activity,
                    "deliverable": deliverable,
                }
                for title, objective, situation, notion, activity, deliverable in items
            ]

        if has_any(["vanilla option", "vanilla options", "black-scholes", "black scholes", "put-call parity", "put call parity"]):
            return rows(
                [
                    (
                        "Lire le ticket vanilla",
                        "Transformer une demande de quote en inputs propres: spot, strike, maturite, taux, dividendes et vol.",
                        "Sales demande un prix indicatif sur un call europeen avant envoi client.",
                        "Moneyness, forward, discounting, convention de maturite.",
                        "Construire le ticket et identifier les donnees manquantes.",
                        "Quote ticket controle.",
                    ),
                    (
                        "Prix Black-Scholes",
                        "Calculer call et put avec substitutions visibles et unite de premium.",
                        "Le desk veut un prix defendable et reproductible.",
                        "d1/d2, prix call/put, dividend yield.",
                        "Calculer le prix et verifier intrinsic/time value.",
                        "Pricing sheet.",
                    ),
                    (
                        "Controle put-call parity",
                        "Detecter une incoherence de quote avant de la transmettre.",
                        "Le put mid ne colle pas avec le call mid et le forward.",
                        "C - P = forward discounté moins strike discounté.",
                        "Mesurer le parity gap et conclure quote/hold/reject.",
                        "Parity control.",
                    ),
                    (
                        "Greeks utiles au quote",
                        "Convertir delta et vega en risque concret pour le trader.",
                        "Le client augmente la taille et le trader demande le hedge initial.",
                        "Delta hedge, vega per vol point, sign convention.",
                        "Calculer hedge shares et sensibilite vol.",
                        "Risk add-on note.",
                    ),
                    (
                        "Memo desk",
                        "Synthétiser prix, controles et action front-office.",
                        "Le quote doit tenir dans un message trader/sales de quelques lignes.",
                        "Assumptions, caveats, controls, decision.",
                        "Rediger une note quote ou no-quote.",
                        "Trader quote memo.",
                    ),
                ]
            )

        if has_any(["yield curve", "bootstrapping", "discount factor", "discount factors", "zero curve", "forward rate", "forward rates", "interest-rate curve"]):
            return rows(
                [
                    (
                        "Lire les instruments de courbe",
                        "Classer deposits, futures et swaps par maturite et convention.",
                        "Le desk doit reconstruire une courbe avant de pricer un swap.",
                        "Tenor, quote, accrual, discount factor.",
                        "Transformer les quotes en tableau de bootstrap.",
                        "Curve input sheet.",
                    ),
                    (
                        "Bootstrap discount factors",
                        "Extraire les discount factors un par un sans casser les maturites deja calibrees.",
                        "Une nouvelle quote 5Y arrive et change le point de courbe.",
                        "Recursion sur coupons, interpolation locale.",
                        "Calculer un point de courbe et documenter la convention.",
                        "Discount-factor ladder.",
                    ),
                    (
                        "Zeros et forwards",
                        "Convertir discount factors en zero rates et forwards exploitables.",
                        "Le trader veut lire le carry implicite entre deux maturites.",
                        "Zero rate continu, forward rate discret.",
                        "Calculer zero/forward et commenter la pente.",
                        "Zero-forward report.",
                    ),
                    (
                        "Controle et usage desk",
                        "Verifier monotonie, interpolation et impact sur PV.",
                        "Une interpolation trop agressive cree un faux signal de risque.",
                        "No-arbitrage local, smoothness, curve-shape risk.",
                        "Comparer deux interpolations et choisir une action.",
                        "Curve validation memo.",
                    ),
                ]
            )

        if has_any(["bond", "duration", "convexity", "ytm", "fixed-income bond"]):
            return rows(
                [
                    (
                        "Cash-flow map",
                        "Lire coupon, maturite, yield et principal.",
                        "Un bond book doit expliquer son P&L rates.",
                        "Coupon, clean/dirty price, accrued interest.",
                        "Construire le tableau de cash-flows.",
                        "Cash-flow schedule.",
                    ),
                    (
                        "Prix et yield",
                        "Relier prix et rendement sans perdre les conventions.",
                        "Le yield mid bouge et le prix doit etre estime.",
                        "YTM, discount factors, accrued interest.",
                        "Calculer un prix approximatif et verifier le sens prix/yield.",
                        "Pricing table.",
                    ),
                    (
                        "Duration et DV01",
                        "Convertir une position en sensibilite EUR/bp.",
                        "Risk demande l'impact d'un +25bp.",
                        "Modified duration, DV01.",
                        "Calculer DV01 et shock P&L.",
                        "Duration report.",
                    ),
                    (
                        "Convexity et limites",
                        "Savoir quand la duration lineaire ne suffit plus.",
                        "Un mouvement de taux large rend l'approximation fragile.",
                        "Convexity correction.",
                        "Comparer approximation lineaire et corrigee.",
                        "Risk caveat.",
                    ),
                ]
            )

        if has_any(["autocall", "autocallable", "structured product", "structured products", "term sheet"]):
            return rows(
                [
                    (
                        "Extraire le term sheet",
                        "Transformer la fiche produit en conditions calculables.",
                        "Sales envoie un autocall a expliquer avant client call.",
                        "Observation dates, coupon barrier, autocall level.",
                        "Construire la table des conditions.",
                        "Term-sheet map.",
                    ),
                    (
                        "Coupon et autocall",
                        "Calculer les coupons et l'evenement de remboursement anticipe.",
                        "Le sous-jacent finit au-dessus du niveau autocall a une date d'observation.",
                        "Indicator functions, memory coupon, early redemption.",
                        "Remplir la logique date par date.",
                        "Coupon/autocall grid.",
                    ),
                    (
                        "Protection barrier",
                        "Expliquer la perte conditionnelle en fin de vie.",
                        "Le sous-jacent finit sous la barriere.",
                        "Capital protection, downside participation.",
                        "Calculer redemption finale.",
                        "Downside explanation.",
                    ),
                    (
                        "Scenario table client",
                        "Comparer upside, flat, moderate down et crash scenario.",
                        "Le client veut comprendre coupon vs capital at risk.",
                        "Cash-flow path dependency, redemption, loss participation.",
                        "Produire une table de scenarios lisible par sales.",
                        "Client scenario table.",
                    ),
                    (
                        "Desk risk",
                        "Relier attrait client et risques de couverture.",
                        "La structure vend du coupon mais concentre du tail risk.",
                        "Barrier/gamma/vega/liquidity risk.",
                        "Ecrire memo sales + risk.",
                        "Client/risk memo.",
                    ),
                ]
            )

        if has_any(["monte carlo", "gbm", "asian", "variance reduction", "standard error", "confidence interval", "confidence intervals"]):
            return rows(
                [
                    (
                        "Ticket de simulation",
                        "Definir process, payoff, monitoring et precision attendue.",
                        "Un payoff asiatique n'a pas de prix ferme dans l'outil vanilla.",
                        "GBM, pas de temps, seed, payoff path-dependent.",
                        "Ecrire le ticket modele avant de coder.",
                        "Model ticket.",
                    ),
                    (
                        "Generer les chemins",
                        "Simuler les trajectoires avec controle de seed et discretisation.",
                        "Le quant dev doit produire un prix reproductible.",
                        "GBM exact step, chocs normaux, monitoring dates.",
                        "Construire les chemins et verifier moments simples.",
                        "Notebook path simulation.",
                    ),
                    (
                        "Prix et intervalle",
                        "Reporter prix, standard error et intervalle de confiance.",
                        "Le trader veut savoir si 5bp de difference est significatif.",
                        "Discounted expectation, standard error.",
                        "Calculer prix et CI 95%.",
                        "Quote avec incertitude.",
                    ),
                    (
                        "Variance reduction",
                        "Ameliorer la precision sans exploser le temps de calcul.",
                        "Le batch overnight doit tenir son SLA.",
                        "Antithetic, control variate, convergence.",
                        "Comparer deux estimateurs.",
                        "Decision path count / methode.",
                    ),
                ]
            )

        if has_any(["stochastic", "risk-neutral", "risk neutral", "girsanov"]) or has_word("ito") or has_word("itô") or has_word("sde"):
            return rows(
                [
                    (
                        "SDE utile au hedge",
                        "Relier dynamique du sous-jacent et risque de couverture.",
                        "Un trader demande pourquoi delta hedge suppose un modele continu.",
                        "dS, drift, volatility, Brownian shock.",
                        "Lire une SDE et nommer chaque terme en langage desk.",
                        "SDE risk translation.",
                    ),
                    (
                        "Ito lemma pour P&L",
                        "Faire apparaitre delta, gamma et theta depuis une fonction de prix.",
                        "Le P&L explique montre un terme de convexite non intuitif.",
                        "Ito expansion, quadratic variation.",
                        "Deriver les blocs de P&L utiles a la couverture.",
                        "Delta-gamma-theta map.",
                    ),
                    (
                        "Mesure risque-neutre",
                        "Comprendre pourquoi le drift historique n'est pas l'input de pricing.",
                        "Le learner confond forecast spot et prix d'option.",
                        "Risk-neutral drift, discounting, martingale pricing.",
                        "Comparer intuition P et calcul Q.",
                        "Pricing measure note.",
                    ),
                    (
                        "Limites du hedge continu",
                        "Transformer la theorie en controles operationnels.",
                        "Le hedge discret subit gaps, frais et liquidite.",
                        "Discrete hedging error, transaction costs, model risk.",
                        "Lister triggers de monitoring et residual risk.",
                        "Hedging caveat memo.",
                    ),
                ]
            )

        if has_any(["swap", "dv01", "par rate"]):
            return rows(
                [
                    (
                        "Lire le ticket swap",
                        "Identifier payer/receiver, notional, coupon, maturite et index flottant.",
                        "Un trader demande une lecture rapide d'un payer swap EUR 5Y avant un move BCE.",
                        "Cash-flow fixe contre flottant, par rate, annuite.",
                        "Transformer le ticket en tableau d'inputs et verifier le sens du risque.",
                        "Ticket enrichi + risque principal en une phrase.",
                    ),
                    (
                        "PV par coupon gap",
                        "Estimer la valeur du swap avec l'ecart fixed coupon vs par rate.",
                        "Le coupon du book est au-dessus du mid-market; il faut expliquer le PV.",
                        "PV approx = (par - fixed) * annuite * notionnel selon le sens.",
                        "Calculer PV, signe et interpretation front-office.",
                        "PV explique avec signe payer/receiver.",
                    ),
                    (
                        "DV01 et shock P&L",
                        "Convertir l'annuite en EUR/bp puis appliquer un shock de courbe.",
                        "La courbe bouge de 10bp avant le comite risque.",
                        "DV01 = annuite * notionnel * 1bp.",
                        "Calculer DV01, P&L shock et seuil d'alerte.",
                        "Tableau DV01/shock P&L.",
                    ),
                    (
                        "Hedge et basis risk",
                        "Proposer une couverture realiste et nommer ce qu'elle ne couvre pas.",
                        "Le desk hedge avec futures ou swap oppose de tenor proche.",
                        "Parallel hedge, tenor mismatch, curve-shape risk.",
                        "Choisir hedge, sens, taille approximative et risque residuel.",
                        "Memo hedge en 6 lignes.",
                    ),
                    (
                        "Debrief production",
                        "Savoir quand l'approximation devient dangereuse.",
                        "La position est materialisee dans un report de risk management.",
                        "Conventions, multi-curve, collateral, interpolation.",
                        "Lister les controles avant validation.",
                        "Checklist de validation desk.",
                    ),
                ]
            )

        if has_any(["barrier", "barriere", "knock"]):
            return rows(
                [
                    (
                        "Regle de payoff et chemin",
                        "Distinguer terminal payoff et evenement de knock-out/knock-in.",
                        "Un client demande le resultat d'un DOC FX sous trois chemins spot.",
                        "Path-dependence, barrier event, activation/desactivation.",
                        "Dessiner la regle de payoff et la table des etats.",
                        "Schema payoff + condition de barriere.",
                    ),
                    (
                        "Scenario table",
                        "Calculer payoff sous plusieurs spots et etats de barriere.",
                        "Le spot finit au-dessus du strike mais a peut-etre touche la barriere.",
                        "Payoff conditionnel et notionnel FX.",
                        "Remplir une table spot, hit/no-hit, payoff.",
                        "Table de scenarios avec conclusion.",
                    ),
                    (
                        "Gap risk",
                        "Expliquer pourquoi le risque pres de la barriere n'est pas un Greek lisse.",
                        "Le spot approche la barriere en marche illiquide.",
                        "Discontinuite, jump-to-knock-out, slippage.",
                        "Identifier les limites du delta hedge pres de H.",
                        "Note gap risk pour risk manager.",
                    ),
                    (
                        "Monitoring desk",
                        "Definir les triggers de surveillance et d'escalation.",
                        "La position reste ouverte pendant une annonce macro.",
                        "Barrier distance, realized vol, liquidity window.",
                        "Construire une grille monitor / hedge / escalate.",
                        "Plan d'action operationnel.",
                    ),
                    (
                        "Debrief modele",
                        "Relier pricing, couverture et risque de modele.",
                        "Le modele donne un prix mais le trader doit survivre au chemin.",
                        "Vol surface, smile, discrete monitoring.",
                        "Lister controles et erreurs courantes.",
                        "Checklist exotics desk.",
                    ),
                ]
            )

        if has_any(["cds", "credit", "cs01", "spread"]):
            return rows(
                [
                    (
                        "Lire le ticket CDS",
                        "Identifier protection buyer/seller, spread, notionnel et maturite.",
                        "Un single-name widening arrive dans le book credit.",
                        "Spread CDS, risky annuity, default leg/premium leg.",
                        "Transformer le ticket en inputs de risk.",
                        "Ticket credit enrichi.",
                    ),
                    (
                        "Carry",
                        "Distinguer coupon/carry et mark-to-market.",
                        "Le book semble profitable au carry mais le spread bouge.",
                        "Carry = notionnel * spread selon convention simplifiee.",
                        "Calculer carry annuel et commentaire.",
                        "Carry note.",
                    ),
                    (
                        "CS01",
                        "Calculer la sensibilite a 1bp de spread.",
                        "Risk demande l'impact d'un widening de 25bp.",
                        "CS01 = notionnel * risky annuity * 1bp.",
                        "Calculer CS01 et shock P&L avant signe position.",
                        "Table CS01/shock.",
                    ),
                    (
                        "Decision credit",
                        "Proposer hedge/reduction/monitoring en fonction du risque.",
                        "La liquidite CDS baisse pendant le stress.",
                        "Spread risk, jump-to-default, liquidity.",
                        "Ecrire une decision operationnelle.",
                        "Memo risk action.",
                    ),
                ]
            )

        if has_word("var") or has_any(["value at risk", "stress", "risk limit", "expected shortfall"]):
            return rows(
                [
                    (
                        "Definir la question de risque",
                        "Clarifier horizon, confiance, exposition et limite.",
                        "Un portefeuille approche son seuil de VaR intraday.",
                        "VaR one-sided, horizon, volatility.",
                        "Construire la fiche inputs du risk report.",
                        "Risk ticket.",
                    ),
                    (
                        "Calcul VaR",
                        "Calculer une VaR parametrique simple avec les bonnes unites.",
                        "Le CRO demande une estimation rapide avant la cloture.",
                        "VaR = notional * vol * quantile.",
                        "Calculer et comparer a la limite.",
                        "VaR + statut de limite.",
                    ),
                    (
                        "Stress overlay",
                        "Montrer ce que la VaR ne capture pas.",
                        "Un scenario historique depasse le mouvement normal.",
                        "Stress test, tail loss, expected shortfall.",
                        "Ajouter un choc severe et comparer.",
                        "Table VaR/stress.",
                    ),
                    (
                        "Escalation",
                        "Transformer le chiffre en decision de gestion.",
                        "La limite est franchie mais le desk propose d'attendre.",
                        "Reduce, hedge, monitor, escalate.",
                        "Ecrire une note decisionnelle.",
                        "Escalation memo.",
                    ),
                ]
            )

        if has_any(["monte carlo", "gbm", "asian", "variance reduction"]):
            return rows(
                [
                    (
                        "Ticket de simulation",
                        "Definir process, payoff, monitoring et precision attendue.",
                        "Un payoff asiatique n'a pas de prix ferme dans l'outil vanilla.",
                        "GBM, pas de temps, seed, payoff path-dependent.",
                        "Ecrire le ticket modele avant de coder.",
                        "Model ticket.",
                    ),
                    (
                        "Generer les chemins",
                        "Simuler les trajectoires avec controle de seed et discretisation.",
                        "Le quant dev doit produire un prix reproductible.",
                        "Euler/GBM exact step, chocs normaux.",
                        "Construire les chemins et verifier moments simples.",
                        "Notebook path simulation.",
                    ),
                    (
                        "Prix et intervalle",
                        "Reporter prix, standard error et intervalle de confiance.",
                        "Le trader veut savoir si 5bp de difference est significatif.",
                        "Discounted expectation, standard error.",
                        "Calculer prix et CI 95%.",
                        "Quote avec incertitude.",
                    ),
                    (
                        "Variance reduction",
                        "Ameliorer la precision sans exploser le temps de calcul.",
                        "Le batch overnight doit tenir son SLA.",
                        "Antithetic, control variate, convergence.",
                        "Comparer deux estimateurs.",
                        "Decision path count / methode.",
                    ),
                ]
            )

        if has_any(["vol", "smile", "skew", "svi"]):
            return rows(
                [
                    (
                        "Lire la chaine d'options",
                        "Nettoyer les quotes avant tout fit.",
                        "Les bids/asks contiennent des quotes stale et croisees.",
                        "Bounds, moneyness, bid/ask mid.",
                        "Filtrer la chaine et documenter les rejets.",
                        "Clean option chain.",
                    ),
                    (
                        "Inversion en IV",
                        "Transformer les prix en volatilites implicites comparables.",
                        "Le trader raisonne en vol, pas en premium brut.",
                        "Black-Scholes inversion, vega, convergence.",
                        "Calculer IV par strike.",
                        "Slice IV.",
                    ),
                    (
                        "Smile et skew",
                        "Interpreter la forme de smile comme signal de risque.",
                        "Le put wing s'enrichit avant un evenement macro.",
                        "Skew, term structure, convexite.",
                        "Tracer smile et commenter le risque.",
                        "Vol note.",
                    ),
                    (
                        "Fit utilisable",
                        "Produire une courbe lisse sans cacher les controles.",
                        "Le pricer a besoin d'une surface stable.",
                        "SVI ou fit quadratique, no-arbitrage checks.",
                        "Fit, residus, controles.",
                        "Fit report.",
                    ),
                ]
            )

        if has_any(["bond", "duration", "convexity", "ytm"]):
            return rows(
                [
                    (
                        "Cash-flow map",
                        "Lire coupon, maturite, yield et principal.",
                        "Un bond book doit expliquer son P&L rates.",
                        "Coupon, clean/dirty price, discounting.",
                        "Construire le tableau de cash-flows.",
                        "Cash-flow schedule.",
                    ),
                    (
                        "Prix et yield",
                        "Relier prix et rendement sans perdre les conventions.",
                        "Le yield mid bouge et le prix doit etre estime.",
                        "YTM, discount factors, accrued interest.",
                        "Calculer un prix approximatif.",
                        "Pricing table.",
                    ),
                    (
                        "Duration/DV01",
                        "Convertir une position en sensibilite EUR/bp.",
                        "Risk demande l'impact d'un +25bp.",
                        "Modified duration, DV01.",
                        "Calculer DV01 et shock P&L.",
                        "Duration report.",
                    ),
                    (
                        "Convexity",
                        "Savoir quand la duration lineaire ne suffit plus.",
                        "Un mouvement de taux large rend l'approximation fragile.",
                        "Convexity correction.",
                        "Comparer approximation lineaire et corrigee.",
                        "Risk caveat.",
                    ),
                ]
            )

        if has_any(["autocall", "structured", "term sheet"]):
            return rows(
                [
                    (
                        "Extraire le term sheet",
                        "Transformer la fiche produit en conditions calculables.",
                        "Sales envoie un autocall a expliquer avant client call.",
                        "Observation dates, coupon barrier, autocall level.",
                        "Construire la table des conditions.",
                        "Term-sheet map.",
                    ),
                    (
                        "Scenario table",
                        "Calculer coupons et redemption sous plusieurs chemins.",
                        "Le client demande upside/flat/downside.",
                        "Path dependency, memory coupon, early redemption.",
                        "Remplir trois scenarios.",
                        "Cash-flow scenarios.",
                    ),
                    (
                        "Protection barrier",
                        "Expliquer la perte conditionnelle en fin de vie.",
                        "Le sous-jacent finit sous la barriere.",
                        "Capital protection, downside participation.",
                        "Calculer redemption finale.",
                        "Downside explanation.",
                    ),
                    (
                        "Desk risk",
                        "Relier attrait client et risques de couverture.",
                        "La structure vend du coupon mais concentre du tail risk.",
                        "Barrier/gamma/vega/liquidity risk.",
                        "Ecrire memo sales + risk.",
                        "Client/risk memo.",
                    ),
                ]
            )

        if has_any(["greek", "delta", "gamma", "vega", "theta"]):
            return rows(
                [
                    (
                        "Lire le Greek report",
                        "Identifier les sensibilites dominantes du book.",
                        "Un book options arrive avec delta/gamma/vega/theta agrege.",
                        "Delta par %, gamma par %^2, vega par vol point.",
                        "Verifier unites et signe.",
                        "Risk snapshot.",
                    ),
                    (
                        "P&L attribution",
                        "Calculer P&L sous scenario spot/vol/time.",
                        "Spot baisse, vol monte, un jour passe.",
                        "Taylor P&L delta-gamma-vega-theta.",
                        "Calculer chaque bloc et le total.",
                        "Attribution table.",
                    ),
                    (
                        "Hedge action",
                        "Proposer une couverture avec residual risk visible.",
                        "Le book est short gamma et long vega.",
                        "Delta hedge, convexity hedge, vega hedge.",
                        "Choisir action et trigger.",
                        "Hedge memo.",
                    ),
                    (
                        "Communication risk",
                        "Ecrire un message utile a trader et risk manager.",
                        "Le P&L explique doit tenir en 8 lignes.",
                        "Dominant risk, residual risk, monitoring.",
                        "Rediger la note.",
                        "Desk risk note.",
                    ),
                ]
            )

        return rows(
            [
                (
                    "Diagnostic de marche",
                    f"Comprendre le probleme pratique lie a {request.topic}.",
                    "Un desk demande une analyse rapide et exploitable.",
                    "Produit, inputs, payoff, risque dominant.",
                    "Transformer le sujet en ticket de desk.",
                    "Brief operationnel.",
                ),
                (
                    "Calcul central",
                    "Faire le calcul minimal necessaire a la decision.",
                    "Le desk a besoin d'un chiffre defendable.",
                    "Formule utile, unite, approximation.",
                    "Calculer et controler le resultat.",
                    "Table de calcul.",
                ),
                (
                    "Sensibilites",
                    "Expliquer ce qui bouge quand les donnees de marche changent.",
                    "Le marche se deplace avant validation.",
                    "Scenario, hedge, stress.",
                    "Construire une mini matrice de sensibilite.",
                    "Risk matrix.",
                ),
                (
                    "Decision",
                    "Conclure avec une action claire.",
                    "Trader, sales et risk doivent comprendre la meme conclusion.",
                    "Hedge, monitor, reduce, quote, reject.",
                    "Rediger le memo final.",
                    "Decision memo.",
                ),
            ]
        )

    def _course_labs(self, request: CourseRequest) -> list[str]:
        focus = f"{request.topic} {request.product or ''} {' '.join(request.concepts)}".lower()

        def has_any(terms: list[str]) -> bool:
            return any(term in focus for term in terms)

        def has_word(term: str) -> bool:
            return re.search(rf"\b{re.escape(term)}\b", focus) is not None

        if has_any(["vanilla option", "vanilla options", "black-scholes", "black scholes", "put-call parity", "put call parity"]):
            return [
                "Quote ticket: spot, strike, maturite, taux, dividendes, vol et convention de taille.",
                "Black-Scholes price: calculer call/put, intrinsic value et time value.",
                "Parity check: mesurer le gap call-put-forward et conclure quote ou reject.",
                "Greeks add-on: convertir delta et vega en hedge initial et risk comment.",
                "Trader memo: prix, controles, hypotheses, action et limites.",
            ]
        if has_any(["yield curve", "bootstrapping", "discount factor", "discount factors", "zero curve", "forward rate", "forward rates", "interest-rate curve"]):
            return [
                "Curve inputs: classer deposits/futures/swaps et conventions de day count.",
                "Bootstrap: calculer les discount factors successifs et verifier la monotonie.",
                "Zero/forward: convertir DF en zero rates puis forward rates.",
                "Interpolation control: comparer deux interpolations et impact PV.",
                "Curve memo: conventions, controles et risques de courbe residuels.",
            ]
        if has_any(["bond", "duration", "convexity", "ytm", "fixed-income bond"]):
            return [
                "Cash-flow schedule: coupons, principal, accrued interest et maturite.",
                "Clean price/YTM: calculer prix approximatif et verifier le sens prix-yield.",
                "DV01: convertir duration et prix en EUR/bp sur notionnel impose.",
                "Rate shock: appliquer +25bp puis comparer duration seule vs convexity.",
                "Risk note: limites de l'approximation et controles de convention.",
            ]
        if has_any(["autocall", "autocallable", "structured product", "structured products", "term sheet"]):
            return [
                "Term-sheet map: dates, coupon barrier, autocall level, protection barrier.",
                "Coupon/autocall grid: calculer coupon et early redemption date par date.",
                "Downside: calculer redemption finale sous la barriere de protection.",
                "Scenario table: upside, flat, moderate down et crash scenario.",
                "Sales/risk memo: benefice client, risque de couverture et tail risk.",
            ]
        if has_any(["monte carlo", "gbm", "asian", "variance reduction", "standard error", "confidence interval", "confidence intervals"]):
            return [
                "Model ticket: process, payoff, monitoring, seed, path count.",
                "Path simulation: generer chemins GBM et verifier moyenne/variance.",
                "Pricing: actualiser payoff moyen et calculer standard error.",
                "Precision: produire CI 95% et decider si l'ecart est significatif.",
                "Variance reduction: comparer antithetic ou control variate.",
            ]
        if has_any(["stochastic", "risk-neutral", "risk neutral", "girsanov"]) or has_word("ito") or has_word("itô") or has_word("sde"):
            return [
                "SDE translation: relier drift, vol et choc Brownien au hedge desk.",
                "Ito P&L: faire apparaitre delta, gamma et theta depuis dV.",
                "Pricing measure: expliquer pourquoi le drift risque-neutre est utilise.",
                "Discrete hedge: quantifier les limites gaps/frais/liquidite.",
                "Hedging memo: controles operationnels et residual risk.",
            ]
        if has_any(["swap", "dv01"]):
            return [
                "Ticket swap: identifier payer/receiver, coupon, par rate, annuite et risque principal.",
                "PV/DV01: calculer PV approximatif et EUR/bp sur un notionnel impose.",
                "Shock P&L: appliquer +/-10bp et expliquer le signe.",
                "Hedge memo: proposer hedge, taille et basis risk.",
                "Debrief: controles de convention, courbe et collateral.",
            ]
        if has_any(["barrier", "barriere", "knock"]):
            return [
                "Payoff path rule: definir hit/no-hit et payoff terminal.",
                "Scenario table: calculer trois scenarios spot avec et sans knock-out.",
                "Gap risk: expliquer la rupture de delta hedge pres de la barriere.",
                "Monitoring plan: definir distance barrier, triggers et escalation.",
                "Debrief: limites modele, discrete monitoring et smile.",
            ]
        if has_any(["cds", "credit", "cs01"]):
            return [
                "Ticket CDS: protection buyer/seller, spread, notionnel, risky annuity.",
                "Carry/CS01: calculer carry annuel et sensibilite 1bp.",
                "Spread shock: appliquer +25bp et discuter le signe position.",
                "Risk action: hedge, reduce ou monitor selon liquidite et jump risk.",
            ]
        if has_word("var") or has_any(["value at risk", "stress", "risk limit"]):
            return [
                "VaR ticket: horizon, confiance, volatilite et exposition.",
                "Calcul VaR: comparer a une limite imposee.",
                "Stress overlay: ajouter un scenario extreme et commenter l'ecart.",
                "Escalation memo: decision et suivi.",
            ]
        if has_any(["monte carlo", "gbm", "asian"]):
            return [
                "Model ticket: process, payoff, monitoring, seed, path count.",
                "Simulation: generer chemins et prix actualise.",
                "Precision: calculer standard error et CI 95%.",
                "Variance reduction: comparer antithetic ou control variate.",
            ]
        if has_any(["vol", "smile", "skew", "svi"]):
            return [
                "Quote cleaning: filtrer quotes impossibles/stale.",
                "IV inversion: calculer vol implicite par strike.",
                "Smile view: expliquer skew et risque de hedge.",
                "Fit report: ajuster une courbe et controler les residus.",
            ]
        return [
            "Mini-diagnostic: identifier produit, payoff ou risque economique.",
            "Calcul de desk: appliquer une formule ou approximation sur donnees numeriques.",
            "Sensibilites: expliquer ce qui bouge si spot/taux/vol/spread change.",
            "Decision: hedge, quote, no-trade, monitoring ou escalation risk.",
            "Debrief: erreurs courantes et limites du modele.",
        ]

    def _wrap_prompt(
        self,
        *,
        role: str,
        language: str,
        task: str,
        context: GenerationContext,
        draft: str,
    ) -> str:
        source_text = "\n\n".join(
            f"[S{idx + 1}] {item.chunk.content}"
            for idx, item in enumerate(context.retrieved)
        )
        return f"""
You are a {role} for ThePricingLibrary.
Language: {language}.

Mission:
{task}

Non-negotiable rules:
- Practice first: no theory block unless immediately used in a task.
- Ground the material in the retrieved context.
- If the context does not support a specific formula or market fact, say so.
- Keep a professional market-finance tone.
- Include source markers like [S1], [S2] when using retrieved material.
- Distinguish extracted content (grounded in [Sx]) from reformulated content from generated content. Anything not supported by a source must be labelled "genere a partir des concepts", never presented as extracted from the source.
- If a "Trous pedagogiques" section lists missing blocks (e.g. no exercise, no worked example), either omit them or generate them explicitly flagged as generated; do NOT pretend they came from the sources.
- Make the output directly usable in a SaaS learning platform.
- If the user supplied numerical data, use it. Do not replace it with placeholders.
- Include an explicit worked correction with formulas, substitutions and final numbers.
- Respect units exactly. Example: "250k EUR par 1%" times a -2% move means 250k * (-2), not 250k * (-0.02).
- Include a front-office or risk-management action: hedge, rebalance, monitor, escalate, quote or reject.
- Avoid generic textbook questions. Every question must map to a concrete desk task.
- If a "Garde-fous numeriques" section is present, do not contradict those values.

Retrieved context:
{source_text or 'No retrieved context.'}

[TEMPLATE_OUTPUT]
{draft}
""".strip()

    def _dedupe_sources(self, sources: list[SourceRef]) -> list[SourceRef]:
        seen = set()
        out = []
        for source in sources:
            key = source.chunk_id
            if key in seen:
                continue
            seen.add(key)
            out.append(source)
        return out

    def _save(self, kind: str, request: dict, response: dict) -> None:
        if self.store is None:
            return
        run_id = stable_id(kind, str(request), str(response)[:300], size=24)
        self.store.save_generation(run_id, kind, request, response)

    def _numeric_control_block(self, request: ExerciseRequest) -> str:
        return self._calculation_pack(request).as_markdown()

    def _calculation_pack(self, request: ExerciseRequest) -> CalculationPack:
        text = " ".join(
            part
            for part in [
                request.free_prompt or "",
                request.topic or "",
                request.product or "",
                request.concept or "",
            ]
            if part
        )
        pack = self.calculator.build_pack(text)
        if pack.steps or not request.require_calculations:
            return pack
        # The request carried no parseable numbers, so the calculator produced no
        # answer key. Seed a topic-appropriate verified scenario so the exercise
        # still ships a real, computed correction (F-EXO-3), mirroring the course
        # worked-example path. Honest: this is a generated standard case.
        topic_key = detect_topic_key(
            request.topic or "",
            request.product,
            [request.concept] if request.concept else [],
        )
        seed = seed_for_topic(topic_key)
        if seed:
            family, seed_text = seed
            seeded = self.calculator.build_pack(seed_text, family_hint=family)
            if seeded.steps:
                return seeded
        return pack

    def _library_track(self, topic: str, product: str | None) -> dict:
        focus = f"{topic} {product or ''}".lower()
        if any(term in focus for term in ["option", "vol", "barrier", "barriere"]):
            track = "Derivatives & Volatility"
        elif any(term in focus for term in ["swap", "rates", "taux", "bond", "fixed income"]):
            track = "Rates & Fixed Income"
        elif any(term in focus for term in ["credit", "cds", "default"]):
            track = "Credit & XVA"
        elif any(term in focus for term in ["var", "risk", "portfolio"]):
            track = "Risk Management"
        else:
            track = "Market Finance Core"
        return {
            "track": track,
            "library_role": "Reusable pedagogical module",
            "recommended_assets": ["course", "desk_case", "answer_key", "quiz", "instructor_notes"],
        }
