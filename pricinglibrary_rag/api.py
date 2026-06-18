from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from .agui import run_agui_stream
from .billing import BillingError
from .factory import Services, build_services


class CheckoutBody(BaseModel):
    plan: str
    email: str | None = None
    success_url: str | None = None
    cancel_url: str | None = None
from .practice_agent import PracticeAgent
from .schemas import (
    CalculationRequest,
    CalculationResponse,
    CourseRequest,
    ExerciseRequest,
    EvaluationReport,
    GenerationResponse,
    IngestRequest,
    IngestResult,
    LibraryItem,
    MaterialPackRequest,
    SearchRequest,
    SearchResponse,
)


def create_app(services: Services | None = None) -> FastAPI:
    services = services or build_services()
    app = FastAPI(
        title="ThePricingLibrary Local RAG Backend",
        version="0.1.0",
        description=(
            "Local backend for ingesting finance PDFs and generating "
            "practice-first courses and exercises."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    agent = PracticeAgent(services.generator)

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "db_path": str(services.settings.db_path),
            "embedding_backend": services.embeddings.name,
            "embedding_dim": services.embeddings.dim,
            "llm": services.llm.name,
            "openai_configured": bool(services.settings.openai_api_key),
        }

    @app.get("/", response_class=HTMLResponse)
    @app.get("/ui", response_class=HTMLResponse)
    def ui() -> str:
        return _ui_html()

    @app.get("/documents")
    def list_documents(limit: int = 100, offset: int = 0) -> list[dict]:
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "source": doc.source,
                "path": doc.path,
                "metadata": doc.metadata,
                "status": doc.status,
                "created_at": doc.created_at,
            }
            for doc in services.store.list_documents(limit=limit, offset=offset)
        ]

    @app.get("/sources/pedagogy-stats")
    def pedagogy_stats() -> dict:
        """Pedagogical coverage of the ingested corpus.

        Lets a UI surface: usable chunks, average pedagogical score, content-type
        distribution and overall usability — without scanning the corpus itself.
        """
        from .pedagogy import detect_pedagogical_gaps

        stats = services.store.pedagogy_stats()
        usable = services.store.iter_chunks(usable_only=True, limit=4000)
        items = [
            (c.metadata or {}).get("pedagogy")
            for c in usable
            if (c.metadata or {}).get("pedagogy")
        ]
        stats["gaps"] = detect_pedagogical_gaps(items)
        return stats

    @app.post("/documents/ingest", response_model=list[IngestResult])
    def ingest(request: IngestRequest) -> list[IngestResult]:
        if request.recursive:
            results = services.ingestion.ingest_directory(
                request.path,
                metadata=request.metadata,
                glob=request.glob,
                recursive=True,
                force=request.force,
            )
            services.retriever.refresh()
            return results
        results = [
            services.ingestion.ingest_file(
                request.path,
                metadata=request.metadata,
                force=request.force,
            )
        ]
        services.retriever.refresh()
        return results

    @app.post("/rag/search", response_model=SearchResponse)
    def search(request: SearchRequest) -> SearchResponse:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="query is required")
        return services.retriever.search(request)

    @app.post("/calculate/practice", response_model=CalculationResponse)
    def calculate_practice(request: CalculationRequest) -> CalculationResponse:
        pack = services.generator.calculator.build_pack(
            request.prompt,
            family_hint=request.family_hint,
        )
        return CalculationResponse(
            family=pack.family,
            title=pack.title,
            markdown=pack.as_markdown(),
            pack=pack.model_dump(),
        )

    @app.get("/library/generations", response_model=list[LibraryItem])
    def list_generations(
        kind: str | None = None,
        limit: int = 30,
        offset: int = 0,
    ) -> list[LibraryItem]:
        return [
            LibraryItem(
                id=item.id,
                kind=item.kind,
                title=item.title,
                created_at=item.created_at,
                request=item.request,
                response=item.response,
            )
            for item in services.store.list_generation_runs(
                kind=kind,
                limit=limit,
                offset=offset,
            )
        ]

    @app.get("/library/generations/{run_id}", response_model=LibraryItem)
    def get_generation(run_id: str) -> LibraryItem:
        item = services.store.get_generation_run(run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="generation not found")
        return LibraryItem(
            id=item.id,
            kind=item.kind,
            title=item.title,
            created_at=item.created_at,
            request=item.request,
            response=item.response,
        )

    @app.get("/evaluation/cases")
    def evaluation_cases() -> list[dict]:
        return [
            {"name": name, "request": request.model_dump()}
            for name, request in services.evaluator.default_cases()
        ]

    @app.post("/evaluation/response")
    def evaluate_response(response: GenerationResponse) -> dict:
        return services.evaluator.evaluate_response(response)

    @app.post("/evaluation/suite", response_model=EvaluationReport)
    def run_evaluation_suite(limit: int | None = None) -> EvaluationReport:
        try:
            return services.evaluator.run_generation_suite(
                services.generator,
                limit=limit,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/generate/exercise", response_model=GenerationResponse)
    def generate_exercise(request: ExerciseRequest) -> GenerationResponse:
        try:
            return services.generator.generate_exercise(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/agent/exercise", response_model=GenerationResponse)
    def agent_exercise(request: ExerciseRequest) -> GenerationResponse:
        try:
            return agent.create_exercise(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/agent/course", response_model=GenerationResponse)
    def agent_course(request: CourseRequest) -> GenerationResponse:
        try:
            return agent.create_course(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/generate/course", response_model=GenerationResponse)
    def generate_course(request: CourseRequest) -> GenerationResponse:
        try:
            return services.generator.generate_course(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/generate/material-pack", response_model=GenerationResponse)
    def generate_material_pack(request: MaterialPackRequest) -> GenerationResponse:
        try:
            return services.generator.generate_material_pack(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # --- AG-UI agentic assistant (SSE streaming) --------------------------
    @app.post("/agent/ag-ui/run")
    async def agent_ag_ui_run(request: Request) -> StreamingResponse:
        payload = await request.json()

        def _gen():
            yield from run_agui_stream(services, payload)

        return StreamingResponse(
            _gen(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
        )

    # --- billing (Stripe) -------------------------------------------------
    @app.get("/billing/config")
    def billing_config() -> dict:
        return services.billing.config_summary()

    @app.post("/billing/checkout")
    def billing_checkout(body: CheckoutBody) -> dict:
        try:
            session = services.billing.create_checkout_session(
                body.plan,
                email=body.email,
                success_url=body.success_url,
                cancel_url=body.cancel_url,
            )
        except BillingError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"id": session.id, "url": session.url, "plan": session.plan, "mode": session.mode}

    @app.post("/billing/webhook")
    async def billing_webhook(request: Request) -> dict:
        payload = await request.body()
        sig = request.headers.get("stripe-signature", "")
        try:
            return services.billing.handle_webhook(payload, sig)
        except BillingError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/billing/entitlement")
    def billing_entitlement(email: str) -> dict:
        return services.billing.entitlement(email)

    return app


app = create_app()


def _ui_html() -> str:
    return """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ThePricingLibrary Practice Engine</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: #f7f8fb;
      color: #172033;
    }
    * { box-sizing: border-box; }
    body { margin: 0; }
    header {
      padding: 22px 28px;
      background: #ffffff;
      border-bottom: 1px solid #e3e7ee;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }
    h1 { font-size: 22px; margin: 0; letter-spacing: 0; }
    .status { font-size: 13px; color: #536176; }
    main {
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 22px;
    }
    section {
      background: #ffffff;
      border: 1px solid #e3e7ee;
      border-radius: 8px;
      padding: 18px;
    }
    h2 { font-size: 16px; margin: 0 0 14px; }
    label {
      display: block;
      font-size: 12px;
      font-weight: 650;
      color: #4b5870;
      margin: 12px 0 6px;
    }
    input, select, textarea {
      width: 100%;
      border: 1px solid #cfd6e2;
      border-radius: 6px;
      padding: 10px 11px;
      font: inherit;
      background: #fff;
      color: #172033;
    }
    textarea { min-height: 78px; resize: vertical; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    button {
      border: 0;
      background: #145c9e;
      color: #fff;
      border-radius: 6px;
      padding: 10px 14px;
      font-weight: 700;
      cursor: pointer;
      margin-top: 14px;
    }
    button.secondary { background: #2f3b52; }
    button:disabled { opacity: .55; cursor: wait; }
    #output {
      white-space: pre-wrap;
      line-height: 1.48;
      font-size: 14px;
      min-height: 520px;
    }
    .sources {
      margin-top: 18px;
      border-top: 1px solid #e3e7ee;
      padding-top: 12px;
      font-size: 13px;
      color: #3c485c;
    }
    .source {
      padding: 10px 0;
      border-bottom: 1px solid #edf0f5;
    }
    .error {
      background: #fff2f0;
      border: 1px solid #ffccc7;
      color: #8c1d18;
      padding: 10px;
      border-radius: 6px;
      margin-top: 12px;
      display: none;
    }
    .toolbar { display: flex; gap: 8px; flex-wrap: wrap; }
    .preset-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }
    .preset-grid button { margin-top: 0; background: #eef3f8; color: #1b304b; }
    .meta {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }
    .metric {
      border: 1px solid #e3e7ee;
      border-radius: 6px;
      padding: 10px;
      background: #fafbfc;
      font-size: 12px;
    }
    .metric b { display: block; font-size: 18px; color: #172033; }
    .library-list { margin-top: 12px; display: grid; gap: 8px; }
    .library-item {
      border: 1px solid #e3e7ee;
      border-radius: 6px;
      padding: 10px;
      cursor: pointer;
      background: #fff;
    }
    .library-item:hover { background: #f4f7fb; }
    @media (max-width: 920px) {
      main { grid-template-columns: 1fr; padding: 14px; }
      header { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>ThePricingLibrary Practice Engine</h1>
      <div class="status" id="status">Chargement...</div>
    </div>
    <div class="toolbar">
      <button class="secondary" onclick="searchOnly()">Tester le retrieval</button>
      <button class="secondary" onclick="calculateOnly()">Tester les calculs</button>
      <button class="secondary" onclick="loadLibrary()">Bibliotheque</button>
      <button class="secondary" onclick="runEvaluation()">Evaluation</button>
    </div>
  </header>

  <main>
    <section>
      <h2>Parametres</h2>
      <label>Mode</label>
      <select id="mode">
        <option value="exercise">Exercice pratique</option>
        <option value="course">Cours / module</option>
        <option value="pack">Pack pedagogique</option>
      </select>

      <label>Exemples desk</label>
      <div class="preset-grid">
        <button onclick="loadPreset('greeks')">Book greeks</button>
        <button onclick="loadPreset('swap')">Swap DV01</button>
        <button onclick="loadPreset('barrier')">Barriere FX</button>
        <button onclick="loadPreset('cds')">CDS CS01</button>
        <button onclick="loadPreset('var')">VaR</button>
        <button onclick="loadPreset('vanilla')">Call BS</button>
      </div>

      <label>Sujet</label>
      <input id="topic" placeholder="Ex: Options exotiques, VaR, credit derivatives" />

      <div class="row">
        <div>
          <label>Produit</label>
          <input id="product" placeholder="Ex: option, swap, CDS" />
        </div>
        <div>
          <label>Concept</label>
          <input id="concept" placeholder="Ex: barrier option" />
        </div>
      </div>

      <div class="row">
        <div>
          <label>Niveau</label>
          <select id="level">
            <option value="beginner">Beginner</option>
            <option value="intermediate" selected>Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="expert">Expert</option>
          </select>
        </div>
        <div>
          <label>Top K sources</label>
          <input id="topk" type="number" value="8" min="3" max="20" />
        </div>
      </div>

      <label>Prompt libre</label>
      <textarea id="freePrompt" placeholder="Ex: Genere un cas pratique de desk sur la couverture gamma proche d'une barriere."></textarea>

      <button id="generateBtn" onclick="generate()">Generer</button>
      <div class="error" id="error"></div>
    </section>

    <section>
      <div class="meta">
        <div class="metric"><span>Sources</span><b id="metricSources">-</b></div>
        <div class="metric"><span>Calculateur</span><b id="metricCalc">-</b></div>
        <div class="metric"><span>Type</span><b id="metricKind">-</b></div>
        <div class="metric"><span>Score</span><b id="metricScore">-</b></div>
      </div>
      <h2 id="resultTitle">Resultat</h2>
      <div id="output">Choisis un mode, remplis un sujet ou un produit, puis genere.</div>
      <div class="sources" id="sources"></div>
      <div class="sources">
        <strong>Bibliotheque locale</strong>
        <div class="library-list" id="library"></div>
      </div>
    </section>
  </main>

  <script>
    async function health() {
      const res = await fetch('/health');
      const data = await res.json();
      document.getElementById('status').textContent =
        `LLM: ${data.llm} | OpenAI key: ${data.openai_configured ? 'configuree' : 'manquante'} | Embeddings: ${data.embedding_backend}`;
    }

    function payloadBase() {
      return {
        topic: value('topic') || null,
        product: value('product') || null,
        concept: value('concept') || null,
        difficulty: value('level'),
        level: value('level'),
        top_k: Number(value('topk') || 8),
        language: 'fr'
      };
    }

    function value(id) {
      return document.getElementById(id).value.trim();
    }

    function setBusy(flag) {
      document.getElementById('generateBtn').disabled = flag;
      document.getElementById('generateBtn').textContent = flag ? 'Generation...' : 'Generer';
    }

    function showError(text) {
      const box = document.getElementById('error');
      box.style.display = text ? 'block' : 'none';
      box.textContent = text || '';
    }

    function renderSources(items) {
      document.getElementById('metricSources').textContent = items ? items.length : 0;
      const box = document.getElementById('sources');
      if (!items || !items.length) {
        box.innerHTML = '<strong>Sources</strong><div>Aucune source retournee.</div>';
        return;
      }
      box.innerHTML = '<strong>Sources</strong>' + items.map((s, i) => `
        <div class="source">
          <b>[S${i + 1}] ${s.title || s.source || s.document_id}</b><br>
          score ${s.score} | chunk ${s.chunk_index}<br>
          ${s.snippet}
        </div>
      `).join('');
    }

    function updateMetrics(data, evaluation) {
      const pack = data && data.metadata && data.metadata.calculation_pack;
      document.getElementById('metricKind').textContent = data ? data.kind : '-';
      document.getElementById('metricCalc').textContent = pack ? pack.family : '-';
      document.getElementById('metricScore').textContent = evaluation ? Math.round(evaluation.score * 100) + '%' : '-';
    }

    async function generate() {
      showError('');
      setBusy(true);
      try {
        const mode = value('mode');
        const base = payloadBase();
        let endpoint;
        let payload;
        if (mode === 'course') {
          endpoint = '/generate/course';
          payload = {
            topic: base.topic || base.product || base.concept || 'Finance de marche',
            product: base.product,
            concepts: base.concept ? [base.concept] : [],
            level: base.level,
            top_k: base.top_k,
            duration_minutes: 90,
            module_count: 4,
            language: 'fr'
          };
        } else if (mode === 'pack') {
          endpoint = '/generate/material-pack';
          payload = {
            topic: base.topic || base.product || base.concept || 'Finance de marche',
            product: base.product,
            concepts: base.concept ? [base.concept] : [],
            level: base.level,
            duration_minutes: 120,
            exercise_count: 3,
            language: 'fr'
          };
        } else {
          endpoint = '/generate/exercise';
          payload = {
            topic: base.topic,
            product: base.product,
            concept: base.concept,
            free_prompt: value('freePrompt') || null,
            difficulty: base.difficulty,
            top_k: base.top_k,
            exercise_format: 'mixed',
            number_of_questions: 5,
            language: 'fr'
          };
        }
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
        let evaluation = null;
        if (data.kind === 'exercise') {
          const ev = await fetch('/evaluation/response', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
          });
          evaluation = await ev.json();
        }
        document.getElementById('resultTitle').textContent = data.title;
        document.getElementById('output').textContent = data.content;
        updateMetrics(data, evaluation);
        renderSources(data.sources);
        loadLibrary();
      } catch (err) {
        showError(err.message);
      } finally {
        setBusy(false);
      }
    }

    async function searchOnly() {
      showError('');
      const q = [value('freePrompt'), value('topic'), value('product'), value('concept')].filter(Boolean).join(' ');
      if (!q) {
        showError('Ajoute au moins un sujet, produit, concept ou prompt.');
        return;
      }
      const res = await fetch('/rag/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: q, top_k: Number(value('topk') || 8)})
      });
      const data = await res.json();
      document.getElementById('resultTitle').textContent = 'Retrieval';
      document.getElementById('output').textContent = JSON.stringify(data.results, null, 2);
      renderSources(data.results);
    }

    async function calculateOnly() {
      showError('');
      const prompt = [value('freePrompt'), value('topic'), value('product'), value('concept')].filter(Boolean).join(' ');
      if (!prompt) {
        showError('Ajoute un prompt ou un sujet avec des donnees numeriques.');
        return;
      }
      const res = await fetch('/calculate/practice', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt})
      });
      const data = await res.json();
      document.getElementById('resultTitle').textContent = data.title;
      document.getElementById('output').textContent = data.markdown;
      document.getElementById('metricCalc').textContent = data.family;
      document.getElementById('metricKind').textContent = 'calculation';
      document.getElementById('metricScore').textContent = '-';
      renderSources([]);
    }

    async function loadLibrary() {
      const res = await fetch('/library/generations?limit=12');
      const items = await res.json();
      const box = document.getElementById('library');
      if (!items.length) {
        box.innerHTML = '<div>Aucun contenu sauvegarde pour l instant.</div>';
        return;
      }
      box.innerHTML = items.map(item => `
        <div class="library-item" onclick="openLibraryItem('${item.id}')">
          <b>${item.title}</b><br>
          ${item.kind} | ${item.created_at}
        </div>
      `).join('');
    }

    async function openLibraryItem(id) {
      const res = await fetch('/library/generations/' + id);
      const item = await res.json();
      const data = item.response;
      document.getElementById('resultTitle').textContent = item.title;
      document.getElementById('output').textContent = data.content || JSON.stringify(data, null, 2);
      updateMetrics(data, null);
      renderSources(data.sources || []);
    }

    async function runEvaluation() {
      showError('');
      document.getElementById('resultTitle').textContent = 'Evaluation produit';
      document.getElementById('output').textContent = 'Execution des cas de controle...';
      const res = await fetch('/evaluation/suite?limit=3', {method: 'POST'});
      const data = await res.json();
      if (!res.ok) {
        showError(data.detail || JSON.stringify(data));
        return;
      }
      document.getElementById('output').textContent = JSON.stringify(data, null, 2);
      document.getElementById('metricScore').textContent = Math.round(data.average_score * 100) + '%';
      document.getElementById('metricKind').textContent = 'evaluation';
    }

    function loadPreset(name) {
      const presets = {
        greeks: {
          topic: 'Options book risk management',
          product: 'equity options book',
          concept: 'delta gamma vega theta hedging',
          prompt: "Genere un exercice pratique de risk management sur un book d'options actions. Donnees imposees: book delta +250k EUR par 1%, gamma -80k EUR par 1%^2, vega +120k EUR par vol point, theta -15k EUR par jour. Scenario: spot -2%, vol +3 points, un jour passe. L'etudiant doit estimer P&L delta-gamma-vega-theta, identifier le risque dominant, proposer une couverture delta et vega."
        },
        swap: {
          topic: 'Interest rate swap valuation and DV01',
          product: 'EUR interest rate swap',
          concept: 'PV par rate DV01 hedge PnL',
          prompt: 'Genere un exercice operationnel de desk rates. Donnees imposees: payer swap EUR 5Y, notionnel 100m, fixed coupon 3.20%, par swap rate actuel 3.00%, annuity approx 4.55, la courbe monte de 10bp. Calculer PV, DV01, P&L et couverture.'
        },
        barrier: {
          topic: 'FX barrier option desk case',
          product: 'FX barrier option',
          concept: 'down-and-out call gap risk',
          prompt: 'Option barriere FX. EUR/USD spot 1.0800, strike 1.1000, barriere down-and-out 1.0000, notionnel EUR 10m. Scenarios spot a 1.0500, spot a 1.0000, spot a 1.2000 sans knock-out. Evaluer payoff et gap risk.'
        },
        cds: {
          topic: 'CDS CS01 and spread shock',
          product: 'single-name CDS',
          concept: 'CS01 carry spread shock',
          prompt: 'CDS notionnel 50m spread 120bp risky annuity 4.2 shock 25bp. Calculer CS01, carry et P&L spread.'
        },
        var: {
          topic: 'Parametric VaR desk limit',
          product: 'portfolio',
          concept: 'VaR stress risk limit',
          prompt: 'VaR portefeuille 20m volatilite 2% confiance 95% horizon 1 jour. Calculer VaR et discuter limite.'
        },
        vanilla: {
          topic: 'Black-Scholes call desk approximation',
          product: 'equity call option',
          concept: 'price delta gamma vega',
          prompt: 'Call vanilla spot 100 strike 100 vol 20% maturite 1 taux 5%. Calculer prix et greeks.'
        }
      };
      const p = presets[name];
      document.getElementById('topic').value = p.topic;
      document.getElementById('product').value = p.product;
      document.getElementById('concept').value = p.concept;
      document.getElementById('freePrompt').value = p.prompt;
    }

    health();
    loadLibrary();
  </script>
</body>
</html>
"""
