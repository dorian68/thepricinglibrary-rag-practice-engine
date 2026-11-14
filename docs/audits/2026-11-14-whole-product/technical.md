> Copie publique expurgée du rapport local du 14 novembre 2026. Les preuves brutes, captures de cours, bases, corpus et identifiants de test restent locaux. Cette copie ne livre pas un nouveau CLI ni une correction produit.

# Audit fonctionnel backend, API et CLI — 14 novembre 2026

**Verdict : couverture CLI intégrale non acquise et blocages de confiance dans
les outils agentiques/RFQ.** Les calculateurs canoniques, le parcours Interview
Lab, la persistance privée et plusieurs parcours de contenu fonctionnent
réellement dans le périmètre testé. Cela ne valide pas les 874 outils annoncés
par le registre, ni tous les modèles affichés dans le desk.

Cet audit précède toute correction produit. Aucun code produit, compte réel,
paiement, ordre de marché, processus Docker/Ollama ou interface Windows n'a été
modifié. Les écritures sont exclusivement des données de test dans des bases
séparées sous `technical/cohort/` ; le corpus original est lu en mode SQLite
`mode=ro` avec `PRAGMA query_only=ON`.

## Preuves et portée

- CLI et MCP (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/cli-evidence.json`) : 22 commandes existantes jouées, sur un
  catalogue de 49 commandes et 874 descripteurs. Les sorties, arguments,
  historiques et artefacts sont conservés. Le parseur et `cli.main(argv)` sont
  réellement exécutés, dans un environnement isolé ; ce n'est pas un nouveau
  client produit. Le chargement du `.env` personnel est désactivé.
- Cycle du runtime (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/runtime-evidence.json`) : 20 commandes supplémentaires,
  session → tour → outil → historique/artefact → résumé → fork → marqueur de
  rollback → approbation refusée → tâche annulée. Une tâche enregistrée n'est
  pas présentée comme un agent worker ayant travaillé. Le véritable processus
  `mcp-serve` répond également à deux requêtes JSONL sur stdin/stdout.
- Parcours HTTP (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/http-evidence.json`) : 61 requêtes réelles vers un processus
  loopback séparé ; 47 réponses 2xx, 14 refus/erreurs 4xx inspectés, aucun échec
  de transport. OpenAPI (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/openapi.json`) inventorie 115 opérations. Le nombre de
  routes n'est pas une preuve de couverture de tous leurs comportements.
- Capacités et contraintes réelles (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/capability-evidence.json`) : 8 requêtes
  supplémentaires, dont backtest natif borné, historique réellement mis en
  cache, stream AG-UI et deux RFQ exotiques contrastés.
- Neuf moteurs (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/numeric-evidence.json`) : dix calculs réels et sept exports CSV
  d'exemple, tous terminés sans erreur. Six familles ont un CLI Python natif ;
  trois nécessitent encore un appel Python/Node écrit par le développeur.
- Livraison Starter Kit (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/starter-artifact-evidence.json`) : contrôle du véritable
  ZIP local et livraison API dans une autre base de test, sans achat réel.

Les identités `audit-*`, les plans actifs et le rôle opérateur sont des fixtures
signées, pas de véritables sessions Supabase ou des clients payants. Les clés
temporaires ne figurent pas dans les preuves publiques. Le serveur partagé
8427 bloque les connexions sortantes non loopback dans son processus ; le
backtest enfant a été inspecté séparément et utilise un CSV local sans connecteur
broker. Aucun appel à un fournisseur LLM externe n'a été effectué.

## Constats critiques

### T01 — P0, registre/MCP : une réponse réussie peut contenir une valeur fictive

`desk.pricing.price_vanilla_option`, invoqué par `tool-run`, `mcp-call` et
`POST /agent/tools/{name}/run`, renvoie **3.45 `desk_units`** pour ces deux tickets :

| Ticket | Résultat réel du moteur BSM canonique | Registre CLI, MCP et HTTP |
| --- | ---: | ---: |
| S=100, K=100, T=1, r=5 %, q=0, σ=20 % | 10.450575 | 3.45 |
| S=200, K=100, T=1, r=5 %, q=0, σ=80 % | 114.877191 | 3.45 |

Le registre répond `status:ok`, nomme une formule générique et n'émet aucun
avertissement. Le calcul canonique contrasté est enregistré séparément dans
`numeric-evidence.json` : les moteurs mathématiques fonctionnent ; l'adaptateur
du registre ne les invoque pas pour ce chemin.

Deux autres invocations illustrent la même limite : `load_ois_curve {}` renvoie
une qualité 0.92 et `stale:false` sans table de courbe ; `book.limit_usage` avec
une perte de 10¹² et une limite de 1 renvoie `PASS_FOR_CONTRACT`, usage 0.55,
`blocks_deployment:false`. Ces valeurs sont littérales dans
`pricinglibrary_rag/tool_registry.py`, méthode `_execute` vers la ligne 749.

`coverage_report().all_ok` compte surtout le nombre d'outils par rôle. Ce
résultat ne démontre ni leur implémentation financière ni leur exécution. Le
registre est exposé aux opérateurs : visiteur 401, membre gratuit ou Pro 403,
opérateur 200. Ce contrôle d'accès fonctionne, mais ne rend pas ses chiffres
vérifiés. Il faut relier chaque outil financier à un vrai moteur, ou le déclarer
indisponible/scaffold sans produire un résultat financier réussi.

### T02 — P0, RFQ Exotics : le modèle annoncé n'est pas exécuté

La page Agent Room utilise un autre chemin :
`AgentRoomReal.jsx:568` → `platformApi.deskRun` → `/agent/desk/run` →
`DeskOrchestrator` → `desk_agents.PricingAgent.kit.price`.
Il ne faut donc pas lui attribuer mécaniquement le 3.45 du registre.

En revanche, deux demandes d'autocall Athena Euro Stoxx 50 à 3 et 5 ans renvoient
le même **102.21 % du pair**, avec vega 800, corrélation 500 et gamma 300. Le
modèle retourné annonce « Local-stochastic vol Monte-Carlo », un smile calibré
et 20 000 trajectoires. `_exotic_price` calcule seulement
`notional * (1 + 0.06 * 1.4 * 0.62 - 0.03)` et des sensibilités proportionnelles
constantes. Aucun Monte Carlo n'est exécuté dans cette fonction.

Les tickets retournés nomment aussi **US Rates (10Y)** comme sous-jacent, malgré
la demande Euro Stoxx 50. La mention générale de simulation pédagogique ne suffit
pas à attribuer au résultat un algorithme absent. Il faut fournir le modèle réel
avec son contrat et ses limites, ou présenter explicitement une illustration
arithmétique sans fausse attribution de modèle/Greeks.

### T03 — P0/P1, RFQ WTI : incohérence entre modèle annoncé et formule

Le desk annonce Black-76 sur futures. Son pricer appelle pourtant `desk_state.bs`,
formule BSM sur spot sans dividende. Pour ses propres données littérales
F/K=80, r=4 %, σ=13.41 %, T=0.5, l'API affiche **3.85**, contre **2.965277** avec
Black-76 sur futures. Le détail et le calcul indépendant figurent dans
commodity-model-comparison.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/commodity-model-comparison.json`).

Les méthodes de risque du desk comportent également des usages de limites et
statuts `GREEN`/`AMBER`/`approved:true` codés par famille. Les prix/sensibilités
calculés et les hypothèses de démonstration doivent être distingués d'un contrôle
réel de limites sur un portefeuille. Cela concerne le desk RFQ, pas le pricer
BSM canonique ni le moteur Monte Carlo natif.

### T04 — P1, assistant hors ligne : le ticket et la langue sont ignorés

L'appel AG-UI demande de conserver S=125/K=110/r=3 %/q=1 %/σ=30 %/T=0.75 an et
de répondre en anglais. Le stream retourne `runtime:offline`, puis ordonne
`set_tool_params` avec S=100/K=100/r=2 %/q=0/σ=20 %/T=180 jours et répond en français.
Le calcul de parité est cohérent pour son nouveau ticket ; il ne répond pas au
ticket demandé. Le stream atteint pourtant `RunFinished/success`.

Il s'agit d'un scénario de démonstration déterministe, pas d'une compréhension
générale des demandes. Un mode pédagogique de démonstration peut être utile ; il
doit annoncer ses capacités et demander explicitement un changement de ticket.

### T05 — P1/P2, contrats de contenu CLI/API incomplets

`cli course ... --language en` génère un document français, titré « Module
pratique », avec ses sections pédagogiques françaises. L'option existe mais
n'est pas respectée dans le template de cours. L'exercice anglais, lui,
fonctionne dans le chemin effectivement joué.

Les scripts Black-Scholes et Yield Curves servis par API contiennent encore le
commentaire HTML historique « Bloc de quiz générique … ». Le rendu du site peut
le masquer ; un consommateur API/CLI reçoit toujours ce bloc. C'est un problème
de projection du contenu autorisé, pas une exposition publique sans droit : les
contrôles 401/403 des cours payants fonctionnent.

### T06 — P1, dashboard : deux contrats de progression non réunis

La recette Business a constaté une tentative et un contrôle numérique dans le
Lab, une reprise correcte, puis « No activity recorded yet » sur le dashboard.
La source explique ce décalage : `DashboardPage` lit uniquement
`/platform/progress/{id}` ; `PlatformStore.progress_summary` interroge
`platform_progress`, tandis que le Lab écrit dans `interview_events` et
`interview_profiles`. `DashOverview`, vers la ligne 5388 de
`ClaudeFrontend.jsx`, considère `prog.events == 0` comme une absence d'activité.
Les données Lab ne sont pas perdues ; leur projection dans l'accueil personnel
est absente. Il faut réunir les vues de progression en conservant des catégories
distinctes, sans transformer un contrôle numérique ou une auto-revue en score
de maîtrise global.

La première requête du dashboard a aussi reçu 401 sans Bearer, alors que les
requêtes entitlement/Interview étaient signées ; « Try again » réussit dans la
même session. Le code présente une cause compatible : `platformGet` utilise la
variable globale mutable `platformAccessToken`, publiée par `RealAuthProvider`
dans un effet React ; le chargement du dashboard dépend de `userId/reload`, sans
dépendance au jeton. Le Lab passe directement `auth.session.access_token` à sa
requête. Une initialisation décalée peut donc laisser partir le premier appel
du dashboard sans jeton. L'absence du header et la reprise réussie sont des faits
de recette ; l'ordre exact des effets reste à confirmer par une trace dédiée,
notamment pour exclure une particularité du transport de la fixture headless.

## Matrice des fonctions et de leur accès en console

« HTTP rejoué » signifie un véritable parcours signé du serveur dans la cohorte,
pas une simulation de réponse. « Harness » indique un outil d'audit écrit ici ;
il ne devient pas pour autant un CLI utilisateur livré.

| Fonction | Accès existant | Preuve et résultat | Limite pour un CLI produit complet |
| --- | --- | --- | --- |
| Catalogue/aperçu public des cours | Manifest frontend, fichier de preview | Revue frontend séparée ; API privée refuse le visiteur | Pas de commande native ni catalogue serveur uniforme joué |
| Lecture des cours payants | `GET /courses/{id}/script` | BS/Greeks/Yield 200 selon plan ; Exotics Starter 403/Pro 200 | HTTP rejoué ; `tpl courses read` absent, projection HTML à nettoyer |
| Position/complétion des cours | PUT position, POST progress, GET progress | Index 3 et complétion conservés ; autre compte 403 ; score navigateur ignoré | HTTP seulement ; lecture ≠ maîtrise ; pas de CLI signé dédié |
| Ingestion/recherche corpus | `cli ingest/search/pedagogy-stats` et API | Ingestion originale synthétique + recherche CLI ; corpus réel RO 123 docs/46 972 chunks pour génération HTTP | CLI opérateur, pas une bibliothèque personnelle client |
| Génération d'exercices | `cli exercise/agent-exercise`, `POST /agent/exercise` | Anglais CLI ; vrai RAG HTTP 8 sources/template ; membre gratuit 403 | Aucun appel LLM externe certifié ; corrigé déjà fourni |
| Bibliothèque privée d'exercices | `GET /platform/exercises[/{id}]` | Réouverture du vrai cas ; autre compte 404 | `cli library` liste les générations opérateur, pas cette bibliothèque signée |
| Répondre/évaluer un exercice générique | Corrigé/barème documentaire | Lecture et correction existent | Pas de contrat de tentative/évaluation générique joué ; ne pas confondre avec Interview Lab |
| Génération de cours | `cli course/agent-course/material-pack` | Un vrai cours persiste et apparaît dans `library` | `--language en` non respecté sur le template joué ; pas une preuve de relecture des 12 cours |
| Interview Lab | `/interview/catalog/cases/onboarding/attempts/review/session/state/export` | Ticket → tentative → auto-revue → put de transfert → reprise/export réels | API complet joué ; CLI natif de candidat absent ; auto-revue ≠ évaluation experte |
| Mesure du pilote | `/interview/pilot/metrics` opérateur | Agrégats consultés ; tentatives/revues séparées | Activité de QA, pas clients, revenus ou PMF |
| Dashboard personnel | `GET /platform/progress/{id}` | Parcours des cours persistant ; Business constate un 401 initial récupérable puis une activité Lab absente de l'overview | Agrège seulement l'ancien `platform_progress`, pas le Lab ; transport Bearer initial à fiabiliser |
| Black-Scholes | `python -m pricinglibrary_rag.black_scholes --input ...` | Deux tickets contrastés, prix distincts et CSV réels | CLI moteur, pas commande SaaS avec identité |
| Arbre binomial | `python -m pricinglibrary_rag.binomial --input ...` | Analyse et convergence CSV réelles | Même réserve d'identité/version produit |
| Obligations | `python -m pricinglibrary_rag.bond --input ...` | Analyse et cashflows CSV réels | Même réserve |
| Monte Carlo | `python -m pricinglibrary_rag.monte_carlo --input ... --format json` | 1 000 trajectoires et terminal CSV calculés | Aucun lien avec le faux MC annoncé par le RFQ Exotics |
| Payoff/stratégies | `python -m pricinglibrary_rag.payoff_strategy --input ...` | Iron condor à quatre jambes, analyse et CSV réels | Commande moteur indépendante de la sélection UI |
| Volatilité réalisée | `python -m pricinglibrary_rag.realized_volatility fichier.csv ...` | Vrai CSV original de test, indicateurs et rolling CSV | Source explicitement synthétique ; pas un flux live |
| Surface de volatilité | `analyze_vol_surface(...)` | Interpolation déterministe effectivement exécutée | Callable Python, pas de parseur CLI natif dans le module |
| Courbe de taux | `build_yield_curve(...)` | Bootstrap de swaps sparse effectivement exécuté | Callable Python, pas de parseur CLI natif |
| Calibration de modèle | Import Node `calibrateVolatilityModel` | SABR réellement calibré sur surface explicitement synthétique | Harness Node ; pas de commande CLI de produit |
| Survival | Interface de jeu, POST score et GET leaderboard | Soumission signée Student acceptée mais `ranked:false`, non publiée | La banque de questions, le timer et la partie ne sont pas un moteur de partie CLI/API |
| Forum | API threads/comments/votes | Création → commentaire → réouverture ; vote répété reste à 1 | CRUD HTTP réel dans la base isolée ; pas preuve de communauté active ni CLI natif |
| Jobs | API publication/liste/candidature | Poste fictif d'audit puis candidature persistée | Pas d'envoi à un employeur prouvé ; sourcing externe non lancé ; pas CLI natif |
| Blog | API écriture opérateur/lecture publique | Article original de fixture écrit et relu | Pas preuve de catalogue éditorial ; pas CLI natif |
| Mentoring | Surface frontend | Pas de route de réservation/service dans l'inventaire backend | Pas CLI/API de booking ; disponibilité humaine non prouvée |
| Notebooks | Surface frontend/Pyodide | Exécution browser non rejouée par cet agent | Pas backend de notebook/save/share ni CLI de parcours ; l'absence d'API ne signifie pas absence de calcul browser |
| Assistant AG-UI | `POST /agent/ag-ui/run`, SSE | Stream et outils effectifs ; Pro 200/gratuit 403 | Démonstration template change le ticket/langue ; pas commande `ask` ni preuve de LLM externe |
| RFQ Desk | `POST /agent/desk/run` | WTI et deux autocalls réellement exécutés | Contrats modèles/inputs non fiables sur les chemins détaillés ci-dessus |
| Salle/book simulés | GET `/agent/desk/state`, endpoints tick/trade | Snapshot de salle joué ; code de book en mémoire inspecté | Pas de transaction de book exécutée ; pas de broker/live order ; persistance de compte non certifiée |
| Registre d'outils | `tool-list/describe/run/coverage`, API opérateur | Métadonnées découvrables ; réponses financières génériques 3.45 prouvées | Échec de confiance ; 874 descripteurs ≠ 874 implémentations |
| MCP | `mcp-tools/describe/call/handle/serve` | Appel outil et vrai transport JSONL joués | Hérite des faux résultats du registre ; conformité protocolaire complète non certifiée ici |
| Sessions/tours/approbations/tasks | Commandes `session-*`, `turn-*`, `approval-*`, `task-*`, `gateway-inbound` | Historiques, artefacts, fork, résumés, refus et annulation persistés | Opérateur ; une ligne `task`/`approval` ne prouve pas orchestration autonome ni décision financière |
| Backtest | POST `/strategy/backtest` → runner du repo TRADING | 2 000 barres locales 15 min, 2 trades, 570 refus, P&L −94.9084 USD | Dépendance au repo/dataset voisin ; ni scan global, ni walk-forward long, ni validation de stratégie complète |
| Données de marché | `/market/catalog/history/universe/providers` | Vrai cache FRED DGS10 copié à l'identique ; 12 points servis ; as-of 25 juin 2026, unité % yield, statut cached_snapshot | Historique ancien explicitement signalé ; pas actualisation live, pas aspiration lancée ; le membre gratuit signé peut lire cet historique |
| Authentification/permissions | Middleware JWT/plans, identité API | 401/403/404 attendus inspectés ; isolation et accès effectifs | Fixtures JWT internes, pas signup/email/reset Supabase réels ; pas CLI login/whoami |
| Abonnements/paiements | `billing-config/checkout/entitlement`, API/webhook | Mode mock/non configuré ; checkout anonyme 401, signé 400 droits non validés | Blocage externe volontaire ; aucun achat/webhook Stripe réel certifié |
| Starter Kit | API availability/manifest/download, vérificateur local | ZIP réel 3 642 930 octets, SHA conforme, 7 livrables, vérificateur exit 0 ; download 200 après grant fixture, sinon 401/403 | Livraison locale avec données de test ; ni paiement réel ni disponibilité de Q&A humain certifiée |
| Exports | CSV moteurs, JSON Interview, ZIP Kit | Vrais octets produits, headers/sha/identité inspectés | Pas de commande SaaS d'export uniforme ; export de notebook/génération frontend non rejoué ici |

Les deux derniers chemins Kit utilisent une base de test distincte avec les
chemins réels de l'artefact local. L'API partagée 8427 avait volontairement un
cache/artefact vide avant configuration : son `artifact_ready:false` initial ne
prouve pas que le véritable ZIP du projet est absent.

## Rendre l'ensemble accessible sans dépendre d'un écran

Ajouter une CLI unifiée n'exige pas de recréer tous les moteurs. Il faut
d'abord définir un **contrat d'action utilisateur** par domaine, puis relier
cette action au serveur ou au calculateur effectif. Une commande qui cache un
appel HTTP arbitraire ou retourne un hash de payload ne prouve pas le résultat.

Proposition de client `tpl`, distinct de l'ancien CLI opérateur :

```text
tpl doctor --json
tpl auth whoami
tpl courses list|read|resume|complete
tpl exercises generate|list|open|export
tpl interview start|task|answer|review|resume|export
tpl tools black-scholes|binomial|bond|monte-carlo|payoff|realized-vol|vol-surface|curve|calibrate
tpl community threads|reply|vote
tpl jobs list|apply
tpl blog list|read
tpl desk quote --ticket ticket.json
tpl backtest run --instrument EURUSD --max-bars 2000
tpl market history --symbol DGS10
tpl admin pilot-metrics
```

Chaque commande doit avoir des entrées bornées et versionnées, les mêmes unités
que l'UI, un résultat JSON stable, des erreurs exploitables, un code de sortie
normalisé et un export écrit à la demande. L'identité vient d'un jeton vérifié,
jamais d'un `--user-id` autoritaire. Les secrets ne doivent pas être des arguments
visibles dans l'historique shell. Les écritures réessayables utilisent une clé
d'idempotence ; les actions externes sensibles gardent leur autorisation réelle.

Ordre de travail proposé, après revue de ce rapport :

1. **Bloquer les faux succès** du registre et corriger/renommer les modèles RFQ
   avant de les exposer via davantage d'intégrations. Publier des capacités
   vérifiées, indisponibles ou illustratives, avec une raison exploitable.
2. **Livrer le client signé sur le cœur déjà réel** : Interview Lab, catalogue et
   lecture de cours, bibliothèque d'exercices, vrais neuf outils et exports.
   Un catalogue serveur explicite manque encore pour les cours ; les exercices
   génériques nécessitent un contrat de tentative si l'on veut évaluer la maîtrise.
3. **Extraire les règles de jeu hors du DOM** pour Survival. Garder les notebooks
   browser honnêtes ; ajouter un vrai export/exécution reproductible si ce parcours
   fait partie de l'offre. Un service de mentoring absent ne devient pas disponible
   parce qu'une commande de booking est créée.
4. **Ajouter les domaines adjacents selon leur utilité** : forum, contenu, jobs,
   services de marché et backtest. Leur CLI doit refléter les capacités et les
   limites réellement disponibles, y compris l'absence d'envoi externe ou de
   données récentes.

La recette suivante devra repartir d'un compte membre sans privilèges, conserver
le même ticket du début à l'export, redémarrer uniquement la session cliente pour
vérifier la reprise et confronter le résultat à un oracle indépendant. Le rapport
Business et la revue headless du site complètent cette preuve ; ils ne doivent
pas être remplacés par le nombre de routes ou de tests réussis.

## Rejouer cet audit

Depuis la racine du projet :

```text
python reports/whole-product-cli-audit-2026-11-14/technical/audit_cli.py
python reports/whole-product-cli-audit-2026-11-14/technical/audit_runtime.py
python reports/whole-product-cli-audit-2026-11-14/technical/audit_numerics.py
python reports/whole-product-cli-audit-2026-11-14/technical/audit_starter_artifact.py
```

Le serveur partagé est lancé, en console cachée par l'outil d'exécution, avec
`serve_cohort.py --port 8427 --cohort shared-review --readonly-corpus`.
`audit_http.py` et `audit_capabilities.py` le consomment. Le premier crée des
fixtures et ne doit pas être relancé pendant la recette Business réservant
`audit-other`. Les activités de QA restent dans le store isolé ; aucun reset n'a
été pratiqué. Une cohorte indépendante peut être créée avec un autre nom. Le
processus 8428 lancé pour cette possibilité a été arrêté à la demande du pilote
d'audit ; la recette convenue reste sur 8427.

Le manifeste lisible sans secret est cohort-manifest.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/cohort-manifest.json`).
`cohort_client.mjs` lit les identités temporaires depuis le fichier local privé ;
il ne faut ni les imprimer ni les publier. La cohorte partagée comprend des
tentatives/commentaires de QA antérieurs : ses statistiques ne sont pas des
preuves de demande commerciale.
