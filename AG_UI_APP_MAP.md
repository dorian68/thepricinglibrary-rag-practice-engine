# AG-UI App Map — The Pricing Library

Cartographie de l'application et de l'intégration AG-UI (agent pédagogique connecté).

## 1. Stack détectée
- **Frontend**: React 18 + Vite (SPA), `react-router-dom` (BrowserRouter), TanStack Query, i18next, Supabase Auth. App principale dans un seul gros fichier `src/claude/ClaudeFrontend.jsx` + `src/claude/practiceEngine.js`. Design system: `src/claude/claude.css` (tokens `--red #FF2E45`, `--panel`, `--line`, fonts Inter / JetBrains Mono). Markdown+LaTeX déjà dispo (`react-markdown`, `remark-math`, `rehype-katex`, `katex`).
- **Backend**: Python FastAPI — package `pricinglibrary_rag` (RAG local hybride vecteur+BM25 sur SQLite, calculateurs desk vérifiés, génération de cours/exercices). LLM provider configurable (`TPL_LLM_PROVIDER`, défaut `openai` / `gpt-4o-mini`), fallback `template` offline.

## 2. Routes / pages principales (frontend)
Router dans `ClaudeFrontend.jsx` (`App()` switch sur `useHashRoute().path`): `/`, `/courses`, `/courses/:id`, `/tools`, `/tools/:id`, `/lab`, `/exercises`, `/survival`, `/community`, `/blog`, `/dashboard`, `/pricing`, `/auth`, `/leaderboard`, `/notebooks`, `/mentoring`, `/jobs`, `/api`, `/admin`, `/practice`, `/challenge`. Page de campagne statique: `/market-finance-starter-kit`.

## 3. Tools interactifs pilotables par l'agent
Dans `ClaudeFrontend.jsx`, chacun enregistré via `useToolRegister(id, params, setters)`:
| Tool id | Composant | Paramètres pilotables |
|---|---|---|
| `bs-pricer` | BSPricerTool | S, K, r, q, sigma, T, view |
| `payoff` | PayoffVisualizerTool | legs[] (montages / produits structurés) |
| `mc` | MonteCarloTool | S, mu, sigma, T, N |
| `iv-calc` | IVCalcTool | asset, window |
| `calib` | CalibrationTool | model |

## 4. Providers / contextes
`main.tsx` → ErrorBoundary → TooltipProvider → `App.tsx`: I18nextProvider → HelmetProvider → QueryClientProvider → **AuthProvider** → Router → **AgentProvider** → { ClaudeFrontend, AgentDock }. Auth via `useAuth()` (`src/contexts/AuthContext.tsx`, Supabase).

## 5. Services backend connectés à l'agent
- RAG: `services.retriever.search(SearchRequest)` (hybride, pédagogie `usable_only`).
- Calcul vérifié: `black_scholes()` (parité call-put) + `services.generator.calculator.build_pack()`.
- Exercices: `services.generator.generate_exercise(ExerciseRequest)` (avec calculation_pack déterministe).

## 6. Outils AG-UI exposés au LLM (backend `agui.py`)
RAG/contenu : `rag_search`, `get_related_concepts`, `generate_exercise`, `grade_user_answer`.
Quant vérifié : `compute_black_scholes`, `compute_greeks`, `compute_put_call_parity`, `greeks_sensitivity`, `simulate_monte_carlo`, `generate_payoff_scenario`, `build_structured_product_payoff`, `binomial_tree`.
Pilotage UI : `set_tool_params`, `navigate`, `render_block` (le modèle compose lui-même latex/dérivation/quiz/concept map/summary/action/progress). Tous **read-only / UI** → pas de gate de validation pour le périmètre livré ; `confirmation_card` + contrat d'approbation prêts pour des actions sensibles (admin/contenu).

## 7. Actions frontend contrôlées (events Custom → AgentProvider)
- `app.tool.set_params` → `setToolParams(tool, params)` (pilote l'outil ; file d'attente si l'outil n'est pas encore monté, appliqué après `navigate`).
- `app.navigate` → `window.nav(path)`.
- `app.render_component` → push d'un UIBlock (allowlist).

## 8. UIBlocks (allowlist `src/agent/uiblocks.jsx`, synchronisée avec `agui.py`)
Génériques : `summary_card`, `action_card`, `confirmation_card`, `metric_grid`, `data_table`, `chart_block`, `form_block`, `suggestion_chips`, `progress_steps`, `error_card`, `calculation_steps`.
RAG : `source_card`, `rag_source_block`.
Quant finance (graphes SVG + KaTeX) : `latex_formula_block`, `derivation_steps_block`, `payoff_chart_block`, `payoff_block`, `black_scholes_explorer_block`, `bs_pricer_block`, `greeks_sensitivity_block`, `put_call_parity_block`, `monte_carlo_simulation_block`, `binomial_tree_block`, `structured_product_payoff_block`.
Apprentissage : `exercise_block`, `quiz_block` (interactif), `answer_feedback_block`, `concept_map_block`.
Aucun rendu de HTML/JS arbitraire du modèle ; types inconnus ignorés proprement.

## 9. Non connecté (et pourquoi)
- **Persistance des conversations** = `localStorage` (`tpl.agui.threads.v1`). Pas de table backend (le système d'auth est Supabase côté front ; migration backend recommandée ci-dessous dans LOCAL_DOC).
- **Actions sensibles** (paiement, mutation de données) : non exposées à l'agent volontairement ; le `confirmation_card` + l'event `app.approval.required` sont prêts si on en ajoute.
- **volsurface** : pilotable via `set_tool_params` mais pas encore d'enregistrement `useToolRegister` (page tool distincte) — extension point trivial.
