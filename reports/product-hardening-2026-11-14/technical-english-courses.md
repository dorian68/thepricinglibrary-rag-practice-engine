# Cours anglais — cycle 2

Campagne démarrée le 14 novembre, finalisation le 15 novembre 2026. Rôle : Technical RL. Skills appliqués :
`market-finance-course-extractor` et `market-finance-uiblock-designer`.

## Résultat et statut

Le défaut était réel : `CourseRequest.language=en` changeait le paramètre mais
laissait le cours, ses annexes et ses corrections en français. La branche
anglaise produit maintenant un cursus original anglais, avec calculs déterministes,
sans traduction automatique, LLM payant ni appel Ollama. La branche française
et les douze documents FR existants sont conservés.

**Technical RL : PASS sur la génération, les calculs, le contrôle source et la
recette locale.** Après corrections Business, la série ciblée comporte **74 PASS en 12,31 s**,
notamment les deux vraies routes HTTP de génération avec JWT Student et refus
Anonymous/Starter. Les douze brouillons anglais passent le gate strict au seuil
98 ; chaque cours obtient 99/100, avec scores automatisés student 100 et junior
99. La qualité des widgets vaut 96 car trois types pertinents sont utilisés,
sans ajouter un quatrième graphique sans lien économique pour gonfler ce score.

**Business Client Mystère : PASS sur les douze hashes V2**, suivant
`english-business-approval.json`. Les douze variantes sont copiées dans le
répertoire privé servi avec le manifeste d’acceptation requis. Le contrôle
automatique ne constitue ni une validation par de vrais étudiants, ni une preuve
de volonté de payer, ni une attestation de maîtrise.

## Livrables

- `course_english_content.py` : douze plans originaux, 108 leçons, dérivations,
  questions d’application et 60 questions de quiz propres aux cours.
- `course_english.py` : composition anglaise, corrections calculées, widgets
  cohérents, bibliographie courte et ledger privé de preuves.
- `course_english_feedback.py` : 240 explications distinctes, rédigées pour
  l’option erronée exacte ; aucun classificateur lexical ni fallback générique.
- `generation.py` : branche EN effective, titre et métadonnées de langue,
  absence d’appel au writer externe pour cette branche ; branche FR conservée.
- `scripts/generate_english_courses.py` : corpus strictement RO, historique
  séparé, staging privé et promotion conditionnée au double contrôle.
- `scripts/audit_english_course_quality.py` et extension du gate historique :
  mêmes poids/seuils, rubriques anglaises réelles et contrôles additionnels.
- `scripts/smoke_english_courses.py` : point d’entrée reproductible sans bureau.
- `tests/test_english_courses.py` et `docs/ENGLISH_COURSE_ACCEPTANCE.md` :
  contrats, oracles, attaques du gate et procédure de revue/promotion.

Les brouillons, index et preuves complètes sont privés dans
`Tools/pricinglibrary_rag_backend/generated_english_courses`. Cette arborescence
est ignorée par Git. La destination après acceptation est
`pricinglibrary_rag/course_scripts/en`, elle aussi ignorée. Aucun cours privé
n’a été ajouté au frontend public, au wheel ou aux fichiers destinés au push.

## Périmètre des douze cours

| Variante | Modules | Livrable numérique et limite principale |
| --- | --- | --- |
| Vanilla options | 8 | Call/put, d1/d2, parité, delta/gamma/vega ; modèle européen flat carry/vol. |
| Options book Greeks | 9 | Décomposition delta-gamma-vega-theta ; unités en pourcentage-spot et vol points, approximation locale. |
| Rates swaps | 9 | PV payer, DV01 et choc de taux ; annuité fournie et figée. |
| Yield curve | 9 | Bootstrap, zéros et forwards ; swaps annuels single-curve, pas une calibration OIS/IBOR complète. |
| Bonds | 8 | DV01 et choc de rendement ; valeur de marché et duration modifiée fournies, pas un prix unique sans échéancier. |
| Implied volatility | 9 | Inversion bornée et reprice ; une cotation européenne, pas une surface complète certifiée sans arbitrage. |
| Monte Carlo | 10 | Prix, SE, CI et benchmark analytique ; observations indépendantes définies au niveau des paires antithétiques. |
| Stochastic calculus | 10 | Itô → réplication → PDE/espérance et checkpoint BS ; diffusion idéale, pas une couverture réelle sans risque. |
| Barrier options | 9 | Payoffs FX conditionnels à la survie ; historique de barrière requis, pas un premium générique. |
| Credit derivatives | 8 | CS01, prime annuelle, PV de prime, upfront simplifié, JTD et choc ; annuité/recovery explicites. |
| Autocall | 10 | Machine d’états, mémoire, coupon, autocall et cash receipts ; ni profit net ni fair value. |
| Market risk | 9 | VaR/ES gaussiennes ; horizon, signe et modèle explicites, aucun faux statut de limite. |

Chaque quiz a cinq options A–E distinctes. Les bonnes positions couvrent les
cinq lettres dans chaque cours. Les réponses expliquent les erreurs de contrat,
unités, mesure, signe et risque. Les exercices rédigés distinguent reconstruction
numérique, critique opérationnelle et transfert d’hypothèse ; ils ne sont pas
présentés comme trois évaluations quantitatives inédites ou un autograde.

## Preuves source et confidentialité

Le corpus a été interrogé avec SQLite URI `mode=ro` et `PRAGMA query_only=ON`.
Aucun constructeur LocalStore, migration, ingestion ou backfill ne s’applique à
ce fichier. Seul l’historique de génération utilise une base temporaire séparée.
La taille et le mtime du corpus sont inchangés avant/après chaque génération.
Un test distinct prouve qu’une écriture via la connexion source est rejetée.

État réel du corpus : **123 documents, 46 972 chunks**, tous classifiés ;
40 790 exploitables pour le cours, soit 86,84 %. Il contient notamment 22 613
blocs de théorie, 8 801 worked examples, 3 014 formules, 2 596 exercices et
2 022 solutions. Ces compteurs décrivent la bibliothèque ; ils ne signifient
pas que chaque cours a extrait ou copié un de ces exercices ou corrigés.

Le retriever est interrogé sur les mécanismes de chaque leçon. Les citations
sont des segments contigus effectivement présents dans les chunks, avec rejet
des contrôles OCR, formules aplaties, fragments de bibliographie et résultats
hors sujet. Le premier essai a révélé qu’un snippet historique recomposait une
bibliographie ; ce résultat a été exclu et la sélection a été corrigée avant
le PASS. Aucun extrait reconstruit ou faussement nettoyé n’est présenté comme
une citation intacte.

Les variantes finales retiennent **20 à 68 locators vérifiés** selon le sujet.
Les références publiques réutilisent les ancres déjà revues, vérifiées sur
document/chunk d’origine. Seule la bibliographie des documents FR existants a
été consultée pour ces locators, sans reprise de prose pédagogique française.
Les citations visibles sont limitées à 24 mots par document source. Le ledger
et les réponses complètes restent privés et sont supprimés par la projection
learner. Les droits de redistribution ne sont pas créés par le fait de posséder
un PDF ni par ce PASS local ; les gates de droits et d’entitlement existantes
restent applicables.

La revue indépendante initiale a retrouvé les **569 locators et 28 citations**
des premiers candidats, vérifié les douze tickets par oracles indépendants et
confirmé les douze hashes FR inchangés. Son blocage portait sur les feedbacks de
quiz parfois hors sujet et trois libellés `frequence=annuelle`, pas sur des sources
inventées. La V2 remplace les 240 feedbacks par des explications explicites,
utilise `frequency=annual`, enlève les parenthèses orphelines des titres et préfère
les courtes phrases complètes ; une coupe conserve une ellipse éditoriale sans
inventer de fin ni dépasser le plafond de mots.

## Calculs et garde-fous

Les outputs calculés proviennent de `PracticeCalculator`, projetés en anglais.
Les tests utilisent aussi des oracles élémentaires indépendants : CDF normale
pour BS, arithmétique de P&L/DV01/CS01, récursion de DF, quantile/densité normale
pour VaR/ES et comptabilité des observations d’autocall. Le premium MC est
accompagné de son incertitude et comparé au benchmark, sans exiger qu’un seul
intervalle à 95 % couvre toujours la valeur analytique.

Trois anciens parseurs reconnaissent encore des libellés techniques français.
Un adaptateur explicite de mots-clés pour bond/barrier/autocall conserve tous
les nombres et le contrat anglais. Les deux tickets sont enregistrés en preuve.
Des tests avec notionnels, coupons et chocs non par défaut vérifient qu’aucun
autre scénario n’est substitué. Un pack absent devient une erreur explicite.
Ce pont de parseur n’est pas une traduction du contenu et n’apparaît pas dans
la prose learner.

L’ancienne annotation du producteur FR affirmant une vérification « par un
professionnel » a été remplacée par une description exacte du contrôle moteur,
sans attestation humaine. Les documents FR privés ne sont pas régénérés dans
ce cycle.

## Gate 98 et recette

Les poids et seuils historiques restent : huit modules, 3000 mots de leçons,
moyenne 320 mots/leçon, seize sources, cinq widgets dont équation, table et bloc
pratique, puis qualité et deux scores de persona à au moins 98. Le gate EN ajoute
6500 mots de **prose visible hors JSON widgets et ledger**, vérification des
locators/citations et de l’allowlist, recomputation des résultats, blocage de
fausses affirmations quantitatives connues, cinq options/positions variées et
détection de consignes françaises. Les attaques de tests changent les nombres,
les bonnes positions et les labels de langue : elles sont refusées.

Le README de confidentialité a été exclu de l’énumération des cours : il est une
documentation, pas un treizième cours. Aucun vrai cours ni critère n’a été retiré
pour atteindre un PASS. Les **12/12 FR** passent toujours leur contrôle strict.

```powershell
python scripts/generate_english_courses.py --output-dir generated_english_courses
python scripts/audit_course_quality.py --dir generated_english_courses --threshold 98 --json
python -m pytest -q tests/test_english_courses.py tests/test_english_generation.py tests/test_course_blocks.py tests/test_generation_controls.py tests/test_generation_llm_guardrails.py
```

Résultat ciblé après correction : **74 PASS en 12,31 s**, plus **3 PASS** ciblés
sur promotion, mapping de feedback et connexion source RO/hash de revue. Rapports :
`english-course-quality.json`, `french-course-quality-cycle2.json` et
`english-course-candidates-v2.json` et `english-course-quality-v2.json`. Les candidats V2 fournissent les douze chemins privés
et SHA-256 à examiner ; aucun contenu de cours privé n’est dans ce rapport.

Le point d’entrée `python scripts/smoke_english_courses.py --existing` a
également été exécuté : gate **12/12 PASS**, puis **26 tests PASS en 7,27 s**.
Ces ensembles se recouvrent ; ils ne constituent pas un total de tests distincts.

## Validation indépendante et promotion

La commande de promotion exige le gate strict et une revue Business PASS sur
les hashes exacts. Un changement de texte invalide la correspondance de hash.
Un rôle de revue incorrect, un verdict FAIL ou des entrées dupliquées sont
rejetés par les tests. La présence seule d’un fichier de brouillon ne le rend
pas disponible au catalogue learner.

Le manifeste final suit `schema_version: tpl.course.language-index.v1`, puis
`courses[{slug,sha256,status:accepted_98_and_independent_review}]`. Les bytes
revus sont copiés sans réécriture et revérifiés ; le manifeste est remplacé
atomiquement après toutes les copies. Le lecteur API/catalogue parent vérifie
le statut et le hash brut, ce qui ferme l’accès à un fichier seul ou modifié.

**Promotion effective :** la commande `generate_english_courses.py --promote`
avec l’approval Business a passé le gate puis copié les douze documents et leurs
preuves privées. Les bytes correspondent exactement aux douze hashes acceptés.
`accepted_english_course` les accepte tous, le corpus source est resté inchangé
et les douze hashes FR restent identiques au baseline.

**Livraison consommée :** `python scripts/smoke_published_english_courses.py`
a démarré une application/Uvicorn neuve et de vrais sous-processus `tpl`.
Le catalogue expose EN pour les douze cours. Un compte signé **Member avec plan
Pro**, sans rôle admin, lit les douze vrais contenus ; Anonymous et Free sont
refusés, et Student est refusé sur les cours Pro. Les headers `Content-Language:
en` et `no-store`, les leçons/quiz et l’absence de ledger privé sont vérifiés.
Le script finit avec code 0 et écrit `english-published-http-cli.json`.
Les sessions et plans sont des fixtures techniques vérifiées par le vrai serveur,
sans login Supabase ou achat réel. Un premier essai avait validé les lectures
mais échoué à nettoyer un verrou SQLite Windows ; la fermeture/collecte du
harness a été corrigée et la recette entière rejouée avec succès.

Un **P2 non bloquant** reste documenté par le reviewer : une courte citation de
la courbe commence par le fragment `gorithms.` avant l’ancre Best-fit. Son origine
est vérifiée ; ce n’est pas une source inventée. Aucun changement silencieux
n’a été fait sous le hash accepté. Un nettoyage ultérieur exigera un nouveau
candidat et une nouvelle empreinte revue.

La projection, le parser frontend et les parcours de compte sont intégrés par
le parent dans des lots distincts. Le smoke valide ici les véritables lectures
API/CLI des cours publiés ; il ne certifie pas un déploiement Supabase/Stripe ni
la demande commerciale. Aucun commit/push n’a été réalisé par cet agent.

Nettoyage de test : la suppression de l’ancien dossier temporaire
`.tmp/english-publish-ybhm4bo9` a été refusée par le contrôle automatique de
commande (« blocked by policy », sans motif plus détaillé). Le dossier reste
ignoré par Git et contient uniquement le store de fixtures techniques du premier
smoke. Le smoke corrigé a fini avec code 0 ; ce résidu ne modifie ni les cours,
ni le manifeste, ni la preuve de lecture.
