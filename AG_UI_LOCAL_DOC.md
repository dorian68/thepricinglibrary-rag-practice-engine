# AG-UI — Documentation locale

**Quant Tutor Agent** AG-UI pour The Pricing Library : page-aware (pageType/level/plan/currentTool), groundé sur le RAG, capable de **piloter les outils**, de **calculer des nombres vérifiés** (Black-Scholes, Greeks complets, parité, arbre binomial, Monte Carlo), d'afficher des **UIBlocks finance interactifs** (payoff, sensibilité d'un Greek, produits structurés autocall/capital-protégé/reverse-convertible, dérivations LaTeX, quiz, correction de réponse, carte conceptuelle) et de générer/corriger des exercices. Markdown + LaTeX (KaTeX). L'allowlist d'UIBlocks frontend (`uiblocks.jsx`) est **synchronisée** avec le backend (`agui.py`).

## 1. Ce qui a été installé / créé
Aucune nouvelle dépendance npm/pip (SSE à la main, `openai>=2.0` déjà présent).

**Backend** (`Tools/pricinglibrary_rag_backend`)
- `pricinglibrary_rag/agui.py` — runtime agent SSE (boucle OpenAI streaming + tool-calling, et fallback offline par intentions), Black-Scholes vérifié, tool executors branchés sur RAG/calc/génération.
- `pricinglibrary_rag/api.py` — route `POST /agent/ag-ui/run` (StreamingResponse `text/event-stream`).
- `scripts/smoke_agui.py` — smoke test offline.

**Frontend** (`WEBSITE/thepricinglab`)
- `src/agent/aguiClient.js` — client SSE fetch-stream.
- `src/agent/toolControl.js` — canal de pilotage des tools (`useToolRegister`, `setToolParams`).
- `src/agent/appContext.js` — contexte de page + suggestions contextuelles.
- `src/agent/AgentProvider.jsx` — état/conversations (localStorage), streaming, dispatch des events Custom.
- `src/agent/uiblocks.jsx` — renderer d'UIBlocks (allowlist).
- `src/agent/AgentDock.jsx` + `src/agent/agent.css` — launcher flottant + panneau (landing, bulles, thinking, streaming md/LaTeX, composer).
- `src/App.tsx` — mount `AgentProvider` + `AgentDock` dans le Router.
- `src/claude/ClaudeFrontend.jsx` — import `useToolRegister`, enregistrement des 5 tools, suppression du `ChatFab` mock (remplacé par l'AgentDock).

## 2. URL de l'endpoint
`POST {VITE_TPL_RAG_API_URL||http://127.0.0.1:8000}/agent/ag-ui/run` (SSE).

## 3. Lancer le projet
```bash
# Backend (offline, sans coût OpenAI)
cd Tools/pricinglibrary_rag_backend
TPL_LLM_PROVIDER=template python -m pricinglibrary_rag.cli serve --host 127.0.0.1 --port 8000

# Backend (LLM réel — gpt-4o-mini, défaut .env)
python -m pricinglibrary_rag.cli serve --host 127.0.0.1 --port 8000

# Frontend
cd WEBSITE/thepricinglab && npm run dev   # http://localhost:5173
```
Le bouton flottant (rouge, bas-droite) ouvre l'assistant. Modèle par défaut : `gpt-4o-mini` (`TPL_OPENAI_MODEL`). Clé : `OPENAI_API_KEY` / `TPL_OPENAI_API_KEY` (gitignorée). Sans clé ou en `template`, le mode offline répond via le RAG local + calculs vérifiés.

## 4. Tester
```bash
# Backend, contrat d'events + grounding + pilotage outil + parité vérifiée
cd Tools/pricinglibrary_rag_backend && TPL_LLM_PROVIDER=template python scripts/smoke_agui.py
# Frontend : npm run build  (passe)
```
**Test manuel** : ouvrir `/tools/bs-pricer`, ouvrir l'assistant → « Montre-moi la parité call-put » : l'agent règle le pricer (S=K), affiche les nombres vérifiés (metric_grid), explique en LaTeX, et cite les sources RAG. Sur `/tools/payoff` → « Construis un bull call spread » reconfigure les legs. Partout → « Donne-moi un exercice » rend un `exercise_block` avec corrigé chiffré.

## 5. Étendre
- **Ajouter un outil backend** : ajouter une fonction `tool_xxx(services, args) -> (result, custom_events)` dans `agui.py`, l'enregistrer dans `TOOL_EXECUTORS`, et ajouter son schéma dans `openai_tool_specs()`.
- **Piloter un nouveau tool frontend** : ajouter `useToolRegister('<id>', {…params}, {key:setter})` dans le composant ; l'agent peut alors `set_tool_params`.
- **Ajouter un UIBlock** : créer le composant dans `uiblocks.jsx`, l'ajouter à `ALLOWED_BLOCKS` + `REGISTRY` ; l'agent l'émet via `render_block`/`app.render_component`.
- **Action sensible (HITL)** : émettre un `confirmation_card` / `app.approval.required` et n'exécuter qu'après validation (contrat prêt, non utilisé par le périmètre read-only actuel).

## 6. Variables d'environnement
`TPL_LLM_PROVIDER` (openai|template|ollama), `TPL_OPENAI_MODEL` (défaut gpt-4o-mini), `OPENAI_API_KEY`/`TPL_OPENAI_API_KEY`, `VITE_TPL_RAG_API_URL` (front, défaut `http://127.0.0.1:8000`).

**Garde-fous de coût** (chemin OpenAI uniquement, valeurs par défaut entre parenthèses) :
- `AG_UI_MAX_OUTPUT_TOKENS` (900) — plafond de tokens de sortie **par appel LLM** (`max_tokens`).
- `AG_UI_MAX_TOTAL_TOKENS` (6000) — **budget total par run** ; au-delà, la boucle s'arrête proprement avant un nouvel appel et affiche une note « limite de coût atteinte ».
- `AG_UI_MAX_STEPS` (5) — nombre max d'itérations think/tool par run.
- `AG_UI_MAX_HISTORY` (12) — nombre de messages d'historique transmis au modèle (borne la taille du prompt).

Ces bornes utilisent `stream_options={"include_usage": true}` pour compter l'usage réel. Le mode offline (`template`) n'a aucun coût et ignore ces garde-fous.

## 7. Limites connues
- Persistance conversations = `localStorage` uniquement. **Migration backend recommandée** : tables `conversations(id,user_id,title,created_at,updated_at)` + `messages(id,conversation_id,role,content,ui_blocks,tool_calls,created_at)` côté `pricinglibrary_rag` (storage.py), reliées à l'auth.
- Le chemin LLM réel (OpenAI streaming + tool-calls) est implémenté selon l'API SDK mais a été validé end-to-end en mode **offline** (sans coût) ; activer une clé pour le valider en réel.
- `volsurface` non encore enregistré (extension triviale).
- Pas d'escalade de modèle activée par défaut (coût maîtrisé, conforme au guide).
