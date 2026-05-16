# ThePricingLibrary Local RAG Backend

Backend Python local pour transformer une base de PDFs finance de marche /
finance quantitative en generateur de cours, exercices pratiques et packs
pedagogiques.

Le backend est volontairement local-first:

- pas de Supabase requis;
- pas d'API externe requise par defaut;
- stockage SQLite local;
- recherche hybride vectorielle + lexicale;
- generation via OpenAI `gpt-4o-mini` par defaut;
- fallback template disponible pour tests offline;
- compatibilite optionnelle avec embeddings locaux `sentence-transformers`;
- compatibilite optionnelle avec LLM local Ollama ou Transformers.

## Structure

```text
pricinglibrary_rag/
  api.py              FastAPI
  cli.py              commandes locales
  config.py           configuration env
  document_loader.py  lecture PDF/TXT/MD
  ingestion.py        ingestion documents -> chunks
  embeddings.py       embeddings locaux
  retrieval.py        RAG local hybride
  generation.py       cours, exercices, packs
  calculators.py      answer keys numeriques controles
  evaluation.py       score qualite produit
  storage.py          SQLite + FTS
```

## Installation

Depuis ce dossier:

```powershell
python -m pip install -r requirements.txt
```

Pour ingester des PDFs, installe au minimum un parseur PDF local:

```powershell
python -m pip install PyMuPDF
```

Sans PyMuPDF, le backend reste testable avec des fichiers `.txt` ou `.md`.

## Initialiser

```powershell
python -m pricinglibrary_rag.cli init-db
```

Par defaut, la base est creee dans:

```text
./data/pricinglibrary_rag.sqlite3
```

Tu peux changer via `.env` ou variables d'environnement:

```powershell
$env:TPL_DATA_DIR = "C:\data\thepricinglibrary_rag"
$env:TPL_DB_PATH = "C:\data\thepricinglibrary_rag\rag.sqlite3"
```

## Ingester une archive

```powershell
python -m pricinglibrary_rag.cli ingest "C:\path\to\pdfs" --recursive --glob "*.pdf" --tag pricing --asset-class rates
```

Ou un fichier:

```powershell
python -m pricinglibrary_rag.cli ingest "C:\path\to\Hull.pdf" --product options --concept derivatives
```

## Rechercher dans la base

```powershell
python -m pricinglibrary_rag.cli search "barrier option payoff and hedging intuition" --top-k 8
```

## Generer un exercice pratique

```powershell
python -m pricinglibrary_rag.cli exercise --product option --concept "barrier option" --difficulty intermediate --format quantitative_problem
```

## Generer un cours

```powershell
python -m pricinglibrary_rag.cli course "Options exotiques" --product option --concept barrier --concept asian --duration 120
```

## Generer un pack complet

```powershell
python -m pricinglibrary_rag.cli material-pack "Introduction au pricing d'options" --product option --exercises 4
```

## Lancer l'API

```powershell
$env:TPL_OPENAI_API_KEY = "sk-..."
python -m pricinglibrary_rag.cli serve --host 127.0.0.1 --port 8000
```

Endpoints principaux:

- `GET /` ou `GET /ui` pour le GUI de test
- `GET /health`
- `GET /documents`
- `POST /documents/ingest`
- `POST /rag/search`
- `POST /calculate/practice`
- `POST /generate/exercise`
- `POST /generate/course`
- `POST /generate/material-pack`
- `GET /library/generations`
- `GET /library/generations/{id}`
- `GET /evaluation/cases`
- `POST /evaluation/response`
- `POST /evaluation/suite`

## Practice Library

Le backend est pense comme une bibliotheque pedagogique, pas comme un simple
chatbot. Chaque generation est sauvegardee dans `generation_runs` et peut etre
retrouvee via l'API ou le CLI.

```powershell
python -m pricinglibrary_rag.cli library --limit 10
```

Les cours sortent comme modules reutilisables:

- objectifs d'apprentissage;
- track pedagogique;
- labs pratiques;
- banque d'exercices rattaches;
- script enseignant;
- supports a produire;
- sources RAG.

Les exercices sortent comme cas pratiques de desk:

- donnees de marche;
- taches operationnelles;
- calculs;
- corriges;
- interpretation;
- decision de hedge/risk/monitoring;
- sources.

## Calculateurs Pedagogiques

Les calculs importants sont controles par le backend avant d'etre donnes au LLM.
Cela evite les erreurs d'unites et donne une answer key plus fiable.

Familles couvertes:

- `options_book_greeks`: P&L delta/gamma/vega/theta;
- `rates_swap_dv01`: PV, DV01 et shock P&L de swap;
- `fx_barrier_option`: payoff de barriere et gap risk;
- `bond_duration_dv01`: duration, DV01 et shock obligataire;
- `vanilla_option_black_scholes`: prix et greeks Black-Scholes;
- `cds_cs01`: CS01, carry et spread shock;
- `parametric_var`: VaR parametrique simple.

Tester un calcul:

```powershell
python -m pricinglibrary_rag.cli calculate "book delta +250k EUR par 1%, gamma -80k EUR par 1%^2, vega +120k EUR par vol point, theta -15k EUR par jour. Scenario spot -2%, vol +3 points"
python -m pricinglibrary_rag.cli calculate --family cds_cs01 "CDS notionnel 50m spread 120bp risky annuity 4.2 shock 25bp"
```

## Evaluation Produit

Le banc d'evaluation verifie que les exercices generes sont utilisables pour
ThePricingLibrary:

- sources RAG presentes;
- marqueurs de source `[S1]`;
- calculs numeriques;
- corrige;
- formule ou sensibilite;
- action operationnelle;
- pas de placeholder generique;
- calculateur specialise reconnu.

Lancer l'evaluation:

```powershell
python -m pricinglibrary_rag.cli evaluate --limit 3
```

## Mode generation OpenAI

Par defaut, `TPL_LLM_PROVIDER=openai` et `TPL_OPENAI_MODEL=gpt-4o-mini`.

Le backend lit la cle depuis `TPL_OPENAI_API_KEY` ou `OPENAI_API_KEY`.
Tu peux aussi creer un `.env` dans ce dossier:

```text
TPL_OPENAI_API_KEY=sk-...
TPL_OPENAI_MODEL=gpt-4o-mini
TPL_OPENAI_TIMEOUT_SECONDS=90
TPL_OPENAI_MAX_RETRIES=1
```

Pour tester sans appel LLM:

```powershell
$env:TPL_LLM_PROVIDER = "template"
```

## LLM local optionnel

Le produit vise maintenant OpenAI par API, mais les providers locaux restent
disponibles pour tests techniques si besoin.

Ollama:

```powershell
$env:TPL_LLM_PROVIDER = "ollama"
$env:TPL_OLLAMA_MODEL = "llama3.1:8b"
python -m pricinglibrary_rag.cli serve
```

Transformers local:

```powershell
$env:TPL_LLM_PROVIDER = "transformers"
$env:TPL_TRANSFORMERS_MODEL_PATH = "C:\models\my-local-instruct-model"
python -m pricinglibrary_rag.cli serve
```

## Embeddings

Par defaut, `TPL_EMBEDDING_BACKEND=local-hashing`: robuste, local, sans
telechargement, mais moins semantique qu'un vrai modele.

Pour utiliser un modele local sentence-transformers:

```powershell
$env:TPL_EMBEDDING_BACKEND = "sentence-transformers"
$env:TPL_SENTENCE_TRANSFORMER_MODEL = "C:\models\bge-small-en-v1.5"
```

Il faut que le modele soit deja present localement.
