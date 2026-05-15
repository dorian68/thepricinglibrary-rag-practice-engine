# ThePricingLibrary RAG Practice Engine

## Resume Executif

Le projet construit est un backend RAG local-first pour ThePricingLibrary.
Son objectif n'est pas de produire un chatbot finance generique, mais un
Practice Engine pedagogique capable de transformer une base documentaire de
finance de marche et finance quantitative en:

- exercices pratiques;
- cas de desk;
- corriges detailles;
- grilles d'evaluation;
- cours et modules pedagogiques;
- packs de materiels de cours.

La promesse produit est simple:

> Apprendre la finance de marche par la pratique, pas par la theorie indigeste.

## Ce Qu'on A Construit

Le backend se trouve dans:

```text
C:\Users\Labry\Documents\THEPRICINGLIBRARY\Tools\pricinglibrary_rag_backend
```

Il contient:

- une bibliotheque Python interne;
- une API FastAPI;
- un CLI d'administration;
- un stockage local SQLite;
- une ingestion PDF locale;
- un moteur de retrieval hybride vectoriel + lexical;
- un generateur de cours;
- un generateur d'exercices pratiques;
- une GUI de test simpliste.

La GUI est disponible ici quand le serveur tourne:

```text
http://127.0.0.1:8000/ui
```

La documentation API FastAPI est disponible ici:

```text
http://127.0.0.1:8000/docs
```

## Nature Technique Du Produit

Ce n'est pas seulement une bibliotheque.
Ce n'est pas encore un agent IA autonome.

La meilleure definition est:

> un Practice Engine RAG pour ThePricingLibrary.

Il peut etre vu sous trois formes:

- Bibliotheque Python: modules `ingestion`, `retrieval`, `generation`, `storage`.
- Backend API: service FastAPI consommable par le SaaS.
- Outil interne: CLI pour ingester des PDFs et tester la generation.

Le coeur produit doit rester un pipeline controle:

```text
PDFs finance quantitative
        -> extraction texte
        -> chunks
        -> embeddings locaux
        -> SQLite
        -> retrieval RAG
        -> gpt-4o-mini
        -> cours / exercices / corriges
```

## Architecture Recommandee Pour Le SaaS

La forme la plus interessante pour ThePricingLibrary est de garder ce backend
comme microservice pedagogique specialise derriere le SaaS.

Architecture cible:

```text
thepricinglibrary.com
        |
        | HTTP API
        v
ThePricingLibrary Practice Engine
        |
        | SQLite local maintenant
        | Postgres/pgvector plus tard si besoin
        v
Base documentaire finance quantitative
```

Endpoints principaux:

```text
GET  /health
GET  /ui
GET  /documents
POST /documents/ingest
POST /rag/search
POST /generate/exercise
POST /generate/course
POST /generate/material-pack
```

## Etat Actuel Du RAG

Base PDF source:

```text
C:\Users\Labry\Documents\THEPRICINGLIBRARY\QUANTITATIVE_FINANCE
```

Resultat d'ingestion:

- PDFs traites: 137
- Documents ingeres: 123
- Doublons ignores: 10
- Echecs d'extraction texte: 4
- Chunks RAG crees: 46 972
- Base SQLite: environ 808 MB

Les echecs d'extraction viennent probablement de PDFs scannes ou non
extractibles sans OCR.

## LLM Configure

Le backend utilise maintenant OpenAI par API.

Provider par defaut:

```text
openai:gpt-4o-mini
```

Variables supportees:

```powershell
$env:TPL_OPENAI_API_KEY = "sk-..."
$env:TPL_OPENAI_MODEL = "gpt-4o-mini"
```

Ou:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

Important: aucune cle OpenAI n'est stockee dans le projet. La generation reelle
necessite que la cle soit fournie dans l'environnement ou dans un `.env` local.

## Commandes Utiles

Se placer dans le backend:

```powershell
cd C:\Users\Labry\Documents\THEPRICINGLIBRARY\Tools\pricinglibrary_rag_backend
```

Initialiser la base:

```powershell
python -m pricinglibrary_rag.cli init-db
```

Lancer le serveur:

```powershell
python -m pricinglibrary_rag.cli serve --host 127.0.0.1 --port 8000
```

Ingester la base quantitative:

```powershell
python -m pricinglibrary_rag.cli ingest "C:\Users\Labry\Documents\THEPRICINGLIBRARY\QUANTITATIVE_FINANCE" --recursive --glob "*.pdf" --tag quantitative_finance --tag market_finance --asset-class multi_asset
```

Tester le retrieval:

```powershell
python -m pricinglibrary_rag.cli search "knock out knock in barrier option payoff American barrier risk profile over hedging" --top-k 5
```

Generer un exercice:

```powershell
python -m pricinglibrary_rag.cli exercise --product option --concept "barrier option" --topic "barrier option payoff"
```

Generer un cours:

```powershell
python -m pricinglibrary_rag.cli course "Options exotiques" --product option --concept barrier --concept asian --duration 120
```

## Produit Client

Le client ne doit pas percevoir le produit comme un chatbot.

Positionnement recommande:

> ThePricingLibrary transforme les concepts de finance de marche en cas
> pratiques realistes, corriges et sources.

Narratif court:

> Donnez un produit, un concept ou une difficulte. Le moteur genere un cas
> pratique de desk: scenario, donnees, questions, correction, grille
> d'evaluation et intuition marche, a partir d'une bibliotheque quantitative
> specialisee.

Angle pedagogique:

> On ne commence pas par la formule. On commence par le probleme de marche.

## Pourquoi C'est Innovant

La valeur ne vient pas seulement du LLM.
Elle vient de la combinaison:

- base documentaire quantitative specialisee;
- retrieval sur corpus proprietaire;
- generation d'exercices pratiques;
- correction structuree;
- orientation desk / analyste / risk / pricing;
- adaptation par niveau;
- reutilisation pour cours, quiz, cas pratiques et supports.

Le produit peut devenir:

- un generateur d'exercices;
- un assistant pedagogique pour formateurs;
- un moteur de creation de curriculum;
- une base de cas pratiques pour apprenants;
- un outil d'entrainement aux entretiens quant/market finance.

## Narratif Bankable

Proposition forte:

> ThePricingLibrary Practice Engine: apprendre la finance de marche comme un
> analyste, pas comme un lecteur de manuel.

Autre version:

> From theory to trading desk cases.

Version SaaS:

> A practice-first learning engine for market finance.

Promesse client:

> Chaque notion devient un exercice. Chaque exercice vient avec son contexte,
> ses questions, sa correction et ses sources.

## Priorites Suivantes

1. Ajouter une cle OpenAI via `TPL_OPENAI_API_KEY` et tester la generation reelle.
2. Ameliorer la qualite du retrieval avec un modele d'embedding OpenAI ou BGE.
3. Ajouter OCR pour les PDFs scannes.
4. Ajouter des templates d'exercices par famille de produits:
   - vanilla options;
   - exotic options;
   - swaps;
   - credit derivatives;
   - fixed income;
   - portfolio/risk;
   - volatility trading;
   - XVA.
5. Ajouter une UI plus proche du SaaS:
   - choix produit;
   - choix niveau;
   - objectif pedagogique;
   - export Markdown/PDF;
   - sauvegarde dans une bibliotheque de cours.
6. Ajouter un systeme de validation pedagogique:
   - pertinence des sources;
   - coherence du corrige;
   - niveau de difficulte;
   - presence d'intuition marche;
   - absence de theorie inutile.

## Decision Technique Recommandee

Pour l'instant:

- garder SQLite pour aller vite;
- garder FastAPI comme service backend;
- utiliser OpenAI `gpt-4o-mini` pour la generation;
- utiliser la base PDF locale comme corpus;
- tester et ameliorer les prompts sur quelques produits cibles.

Ensuite, quand le produit SaaS sera stable:

- passer a Postgres/pgvector si plusieurs utilisateurs ou gros volume;
- ajouter auth et quotas;
- historiser les generations;
- brancher le frontend de ThePricingLibrary;
- produire des exports pedagogiques propres.

