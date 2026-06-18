# Promouvoir les cours enrichis -> cours actifs

Deux versions enrichies disponibles (toutes deux 90/100, gate PASS, 12/12):
- **`generated_v2/`** — version deterministe (provider `template`), offline, gratuite,
  nombres verifies. Reproductible a l'identique.
- **`generated_v2_llm/`** — version premium (OpenAI gpt-4o-mini): meme structure et
  memes blocs verifies (verbatim), mais prose des lecons reecrite par le LLM en
  francais naturel (10/12 enrichies, 2 repli securise). **Recommandee pour la demo.**

Choisir le dossier source (`generated_v2_llm` recommande) dans les commandes ci-dessous.
Les anciens cours actifs sont:
- backend: `generated/course_scripts/*.md`
- frontend servi: `WEBSITE/thepricinglab/public/course-scripts/*.md`

**Rien n'a été remplacé automatiquement** (action jugée non sûre: elle change ce
que voient les utilisateurs). Promotion manuelle, non destructive, en 3 étapes.

## 1. Archiver l'existant

```powershell
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item -Recurse "generated/course_scripts" "generated/course_scripts_archive_$ts"
Copy-Item -Recurse "../../WEBSITE/thepricinglab/public/course-scripts" "../../WEBSITE/thepricinglab/public/course-scripts_archive_$ts"
```

## 2. Vérifier la qualité avant de promouvoir (gate >= 70)

```powershell
python scripts/audit_course_quality.py --dir generated_v2
# Section Quality Gate doit afficher PASS
```

## 3. Promouvoir

```powershell
Copy-Item "generated_v2/*.md" "generated/course_scripts/" -Force
Copy-Item "generated_v2/*.md" "../../WEBSITE/thepricinglab/public/course-scripts/" -Force
```

Puis re-générer le `_index.json` / `_quality_report.json` côté public si le front
en dépend (l'ancien `scripts/audit_course_scripts.py` écrit `_quality_report.json`).

## Régénérer avec un vrai LLM (qualité encore supérieure)

La clé OpenAI du `.env` renvoie actuellement **401 (invalide/expirée)**. Avec une
clé valide:

```powershell
$env:TPL_OPENAI_API_KEY = "sk-...valide..."
python scripts/generate_course_scripts.py --output-dir generated_v2 --llm-provider openai
python scripts/audit_course_quality.py --dir generated_v2
```

Le pipeline est prêt: le LLM réécrit par-dessus le draft riche déjà sourcé et
chiffré (il ne part pas d'une page blanche).
