from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .factory import Services, build_services
from .schemas import (
    CourseRequest,
    ExerciseRequest,
    GenerationResponse,
    IngestRequest,
    IngestResult,
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

    @app.post("/generate/exercise", response_model=GenerationResponse)
    def generate_exercise(request: ExerciseRequest) -> GenerationResponse:
        try:
            return services.generator.generate_exercise(request)
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
    <button class="secondary" onclick="searchOnly()">Tester le retrieval</button>
  </header>

  <main>
    <section>
      <h2>Parametres</h2>
      <label>Mode</label>
      <select id="mode">
        <option value="exercise">Exercice pratique</option>
        <option value="course">Cours / module</option>
      </select>

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
      <h2 id="resultTitle">Resultat</h2>
      <div id="output">Choisis un mode, remplis un sujet ou un produit, puis genere.</div>
      <div class="sources" id="sources"></div>
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
        document.getElementById('resultTitle').textContent = data.title;
        document.getElementById('output').textContent = data.content;
        renderSources(data.sources);
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

    health();
  </script>
</body>
</html>
"""
