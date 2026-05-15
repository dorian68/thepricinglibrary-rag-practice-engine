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
- `POST /generate/exercise`
- `POST /generate/course`
- `POST /generate/material-pack`

## Mode generation OpenAI

Par defaut, `TPL_LLM_PROVIDER=openai` et `TPL_OPENAI_MODEL=gpt-4o-mini`.

Le backend lit la cle depuis `TPL_OPENAI_API_KEY` ou `OPENAI_API_KEY`.
Tu peux aussi creer un `.env` dans ce dossier:

```text
TPL_OPENAI_API_KEY=sk-...
TPL_OPENAI_MODEL=gpt-4o-mini
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
