from __future__ import annotations

from dataclasses import dataclass

from .llm import LocalLLM
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
from .text_utils import concise_snippet, keyword_scores, split_sentences, stable_id


@dataclass(frozen=True)
class GenerationContext:
    query: str
    retrieved: list[RetrievedChunk]
    sources: list[SourceRef]
    facts: list[str]
    keywords: list[str]


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
            )
        )
        title = f"Module pratique - {request.topic}"
        draft = self._course_template(request, title, context)
        prompt = self._wrap_prompt(
            role="market finance course architect",
            language=request.language,
            task=(
                "Create a practice-first course module for ThePricingLibrary. "
                "Minimize dry theory, anchor every concept in an activity, "
                "and cite the retrieved materials."
            ),
            context=context,
            draft=draft,
        )
        content = self.llm.generate(prompt, max_tokens=3600)
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
            exercises.append(
                self.generate_exercise(
                    ExerciseRequest(
                        topic=request.topic,
                        product=request.product,
                        concept=concept,
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

    def _build_context(self, request: SearchRequest) -> GenerationContext:
        retrieved = self.retriever.retrieve(
            request.query,
            top_k=request.top_k,
            product=request.product,
            concept=request.concept,
            asset_class=request.asset_class,
            tags=request.tags,
        )
        sources = [self.retriever.to_source_ref(item) for item in retrieved]
        text_blocks = [item.chunk.content for item in retrieved]
        facts = self._extract_facts(text_blocks, max_facts=10)
        keywords = [term for term, _ in keyword_scores(text_blocks, top_k=16)]
        return GenerationContext(
            query=request.query,
            retrieved=retrieved,
            sources=sources,
            facts=facts,
            keywords=keywords,
        )

    def _extract_facts(self, blocks: list[str], max_facts: int = 10) -> list[str]:
        facts: list[str] = []
        for block in blocks:
            for sentence in split_sentences(block):
                cleaned = sentence.strip()
                if 70 <= len(cleaned) <= 280:
                    facts.append(cleaned)
                if len(facts) >= max_facts:
                    return facts
        return [concise_snippet(block, max_chars=240) for block in blocks[:max_facts]]

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
        focus = request.free_prompt or request.topic or request.product or request.concept
        return f"Cas pratique - {focus or 'finance de marche'}"

    def _source_lines(self, context: GenerationContext) -> str:
        if not context.sources:
            return "- Aucune source retrouvee localement."
        lines = []
        for idx, src in enumerate(context.sources, start=1):
            label = src.title or src.source or src.document_id
            lines.append(
                f"- [S{idx}] {label}, chunk {src.chunk_index}, score {src.score}: "
                f"{src.snippet}"
            )
        return "\n".join(lines)

    def _facts_lines(self, context: GenerationContext) -> str:
        if not context.facts:
            return "- Aucun fait extrait."
        return "\n".join(f"- {fact}" for fact in context.facts)

    def _exercise_template(
        self,
        request: ExerciseRequest,
        title: str,
        context: GenerationContext,
    ) -> str:
        product = request.product or "instrument a identifier dans le contexte"
        concept = request.concept or request.topic or "concept principal"
        calc_line = (
            "Inclure des calculs progressifs et une interpretation economique."
            if request.require_calculations
            else "Privilegier le raisonnement qualitatif et la decision."
        )
        return f"""
# {title}

## Intention pedagogique
Amener l'apprenant a comprendre {concept} sur {product} par une situation de marche concrete.

## Niveau et format
- Niveau: {request.difficulty}
- Format: {request.exercise_format}
- Public: {request.target_audience}
- Nombre de questions: {request.number_of_questions}
- Consigne: {calc_line}

## Scenario
Un desk doit analyser une situation de marche autour de {product}. L'apprenant recoit
des informations partielles, doit identifier les risques, choisir les donnees utiles,
puis produire une decision argumentee.

## Donnees de depart
- Spot initial: a fixer par l'enseignant ou par un jeu de donnees local.
- Horizon: 1 mois a 1 an selon le produit.
- Volatilite, taux, spread ou carry: fournis dans l'enonce si necessaire.
- Contraintes: expliquer chaque hypothese et distinguer donnees observees et hypotheses.

## Questions
{self._numbered_questions(request)}

## Aide attendue
- Commencer par qualifier le payoff, le risque principal et la sensibilite dominante.
- Relier chaque calcul a une intuition economique.
- Justifier toute approximation.

## Corrige type
Le corrige doit:
- rappeler les hypotheses;
- derouler la methode;
- donner l'interpretation financiere;
- signaler les limites du raisonnement;
- citer les extraits sources pertinents.

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
        for idx in range(1, max(request.module_count, 1) + 1):
            modules.append(
                f"""
### Module {idx}
- Objectif pratique: resoudre une tache concrete liee a {request.topic}.
- Situation: mini-cas de desk, risque, pricing ou structuration.
- Notion utile: introduite seulement au moment ou elle sert l'action.
- Activite: calcul, diagnostic, decision ou critique de modele.
- Livrable apprenant: reponse structuree, tableau, formule commentee ou memo.
""".strip()
            )
        return f"""
# {title}

## Promesse du module
Apprendre {request.topic} par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: {request.target_audience}
- Niveau: {request.level}
- Duree: {request.duration_minutes} minutes
- Produit: {request.product or 'multi-produits'}
- Concepts: {', '.join(request.concepts) if request.concepts else 'a deduire du contexte'}

## Objectifs d'apprentissage
- Comprendre le probleme de marche avant la formule.
- Savoir identifier les inputs, les risques et les hypotheses.
- Produire un raisonnement utilisable en contexte professionnel.
- Transformer une source theorique en decision ou en exercice.

## Deroule pratique
{chr(10).join(modules)}

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

## Faits et angles extraits de la base
{self._facts_lines(context)}

## Sources RAG a citer
{self._source_lines(context)}
""".strip()

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
- Make the output directly usable in a SaaS learning platform.

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

