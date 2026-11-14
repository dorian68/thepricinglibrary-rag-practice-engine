> Copie publique expurgée du rapport local du 14 novembre 2026. Les preuves brutes, captures de cours, bases, corpus et identifiants de test restent locaux. Cette copie ne livre pas un nouveau CLI ni une correction produit.

# Recette indépendante Business — produit entier

14 novembre 2026 · ThePricingLibrary · rôle Business Client Mystère.

**Verdict global : FAIL.** Le produit contient un vrai cœur utile : neuf calculateurs exécutables et exportables, des cours substantiels, une bibliothèque privée et un Interview Lab anglais dont la tentative et la reprise fonctionnent. L'ensemble ne constitue pas encore un parcours autonome cohérent et suffisamment fiable pour être vendu à un étudiant de master anglophone. Des résultats financiers de démonstration sont présentés comme provenant de modèles qui ne sont pas exécutés ; la progression est fragmentée ; des transitions changent de sujet ; l'essentiel de la bibliothèque historique reste français.

**Décision : poursuivre un pilote local encadré sur le Lab anglais et les calculateurs canoniques, avec un périmètre annoncé. Ne pas ouvrir la vente du SaaS entier ni promouvoir le desk/registre comme moteurs de pricing vérifiés.** Le score antérieur de 94,25 concernait le pilote de six cas. Il n'est ni repris ni extrapolé au produit entier.

Ce rapport précède les corrections. Aucun changement de code produit, de navbar, de hero, de configuration commerciale ou de documents stratégiques n'a été effectué par cette recette.

## 1. Ce qui a réellement été examiné

La cible est un candidat M1/M2 anglophone préparant des entretiens bancaires en dérivés, structuration, sales/trading ou market risk, avec un premier angle equity derivatives. Une préparation de probabilités pour prop trading est un autre besoin. Les critères sont : comprendre quoi faire en 30 secondes, défendre un petit cas en 30–60 minutes, retrouver son travail, puis constater un progrès sur une variante après plusieurs séances. L'audit ne mesure pas ces résultats sur de véritables candidats.

Le protocole AGENTS.md, le rôle Business, son skill, PRODUCT_PHILOSOPHY.md, FUNCTIONAL_SPECIFICATION.md, PRODUCTION_READINESS.md et la stratégie du 14 novembre ont servi de contrats. Les anciennes recettes servent uniquement de contexte ; les constats ci-dessous indiquent leur preuve actuelle.

Méthode exclusivement CLI/HTTP/Chromium **headless**. Aucune fenêtre navigateur visible, CUA, souris, clavier natif, application Windows, Docker ou Ollama. Interface locale `http://127.0.0.1:5173`, API de cohorte isolée `http://127.0.0.1:8427`. Les identités sont des fixtures JWT signées et les plans sont des droits de test, pas des clients payants. Le transport d'identité est contrôlé ; le vrai AuthContext, les requêtes applicatives, les contrôles d'accès et les calculs sont utilisés. Un header Bearer manquant n'est jamais ajouté par le harness. Cela ne certifie pas un signup, un reset email ou Supabase réel.

La recette Business a effectué un inventaire anonyme de **63 vues**, exécuté les **neuf outils** avec un téléchargement JSON réel par outil, lu les **12 scripts de cours** par HTTP signé, suivi une activation non-admin et une reprise dans un nouveau contexte, puis testé des transitions de formation et la récupération du dashboard. Les vues et états DOM, captures, entrées et réponses pertinentes sont conservés ici. Les délais mesurés localement ne constituent pas un engagement de performance à froid.

Les preuves techniques complémentaires ont été relues : calculs contrastés, RFQ, registre/MCP, RAG, backtest, données de marché, livraison du Kit et contrôles d'accès. Leur exécution est attribuée à l'agent technique. La matrice frontend racine comporte **175 vues / 77 routes**, aux largeurs 1440 et 390, avec 0 erreur de page et 0 débordement horizontal au repos. Elle ne certifie pas tous les états interactifs, toutes les tailles ou les lecteurs d'écran.

Légende : **R-B** = reproduit par cette recette Business ; **R-T** = reproduit par la recette technique indépendante et preuve relue ; **I** = inspecté dans DOM/source/document ; **NV** = comportement non vérifié ; **IND** = indisponible dans cet environnement. Un refus 401/403 attendu n'est pas une feature absente.

## 2. Trois parcours cibles et leur résultat

| Scénario candidat | Résultat actuel | Ce que cela prouve / ne prouve pas |
| --- | --- | --- |
| « Je dois refaire et expliquer une quote vanilla aujourd'hui. » Accueil → Black-Scholes → résultat → Interview call quote → réponse → correction → nouvelle session | Le calcul gratuit est réellement exploitable ; une tentative non-admin est sauvegardée et la reprise ouvre son feedback. L'exploration clavier ouvre le menu et Escape rend le focus. | R-B. Première valeur réelle et mémoire du cas. L'étudiant doit encore trouver lui-même le chemin vers le Lab ; aucune étude utilisateur ne valide son temps d'activation. |
| « Je révise pour un entretien anglophone dans deux semaines. » Cours → exercice → outil → retour quotidien | Les cours sont substantiels, mais historiques français ; certains liens changent de concept. Le Lab a son propre historique tandis que Dashboard affiche une erreur, puis “No activity recorded yet”. | R-B. La reprise du Lab n'est pas perdue. En revanche le bureau personnel ne donne pas un état global fidèle de la préparation. Un contrôle numérique ne mesure pas à lui seul la qualité de l'explication. |
| « Je veux défendre un hedge ou un produit plus complexe avec les agents. » RFQ → modèle → prix/risques → preuve | Le desk est présent et le backend s'exécute. Des RFQ annoncent Black-76 ou Local-stochastic vol Monte-Carlo sans exécuter le modèle annoncé ; le registre générique donne des valeurs constantes réussies. | R-T + I du discours visible. Blocage de confiance pédagogique. Aucun ordre réel ni transaction financière n'a été exécuté ; les neuf calculateurs canoniques suivent d'autres chemins. |

## 3. Matrice de couverture fonctionnelle

| Surface / routes principales | État et preuve actuelle | Limite de conclusion |
| --- | --- | --- |
| Découverte, navbar, hero, `/about`, `/courses`, `/tools` | R-B DOM ; calculateur BS accessible sans compte ; navigation Explore au clavier fonctionnelle | Le hero et le logo acceptés ne nécessitent pas de refonte pour résoudre les problèmes recensés. Pas de test de compréhension auprès de candidats. |
| 12 cours, `/courses/{id}` | R-B : 12 réponses 200 sous droit Pro ; textes d'environ 6 472 à 8 090 mots selon le comptage du harness, prérequis et sections présents ; bibliothèque historique française | Échantillonnage éditorial et structurel, pas certification mathématique exhaustive de chaque phrase. Les plans inférieurs ont des droits différents, effectivement contrôlés. |
| Exercices génériques, `/exercises`, `/practice`, `/exercises/{id}` | R-B navigation et lecture ; R-T génération anglaise privée, réouverture, RAG sur corpus réel et isolation inter-comptes | Corrigé et barème documentaires ne sont pas un contrat de tentative notée. Aucun appel LLM externe ni correction humaine certifiés. |
| Interview Lab, `/interview`, `/interview/call-quote` | R-B réponse non-admin, retour calculé, état conservé, reprise en nouveau contexte ; R-T variante et export privé | Six cas anglais, domaine borné. L'indépendance enregistrée n'est pas une surveillance d'examen ; reasoning self-review ≠ note d'expert. |
| Neuf outils : `bs-pricer`, `payoff`, `mc`, `iv-calc`, `calib`, `binomial`, `volsurface`, `bond`, `curve` | R-B neuf exécutions et neuf JSON téléchargés ; R-T entrées contrastées/calculs et CSV | Moteurs réels, pas données live ni validation de tous les inputs possibles. Pas de certification globale des nombres du desk/registre. |
| Survival, `/survival`, `/survival/core` | R-B/I état de lancement honnête : une vague de 20 questions, 30 s/question, 3 vies ; R-T score signé enregistré mais non classé | Pas de nouvelle partie complète chronométrée par cette recette globale ; ancienne preuve de pilote distincte. Le leaderboard vide n'est pas une preuve de panne. |
| Trading Lab, scénarios, stratégies, comparaisons | I/R-B DOM : entrées vers exercices canoniques et scénarios explicités | Tous les parcours ne sont pas des travaux conservés ou évalués. Plusieurs textes et consignes sont encore français. |
| Backtest, `/lab/backtest` | I configuration DOM ; R-T exécution native bornée sur 2 000 barres locales, 2 trades, P&L −94,9084 USD | Pas de nouveau lancement UI Business, ni validation de toutes les stratégies, tous les actifs ou du walk-forward long. Un moteur disponible n'est pas une stratégie rentable. |
| Agent Room / RFQ | I DOM ; R-T vrais appels `/agent/desk/run` et comparaison de modèles | Exécution réelle mais attribution de modèle non fiable sur les cas détaillés. Pas de trade/book exécuté par cet audit. |
| Assistant AG-UI, registre, MCP | R-T stream, contrats et transport ; droits opérateurs vérifiés | Démo hors ligne et registre de contrats ne sont pas un assistant généraliste ni 874 moteurs financiers implémentés. LLM externe NV. |
| Communauté/forum | R-B DOM d'une discussion **fixture d'audit** ; R-T post/commentaire/réouverture/vote idempotent dans base isolée | Fonction de forum réelle. Pas preuve de communauté active, de modération opérée ou de demande. Aucun message Business publié. |
| Jobs et blog | R-B/I DOM de contenus explicitement fixtures ; R-T création/lecture et candidature locale | Aucun poste réel ni catalogue éditorial validé ; candidature ne vaut pas envoi employeur. Pas de subscription/newsletter externe testée. |
| Notebooks, `/challenge` → `/notebooks` | R-B ouverture de l'éditeur BS, clic Run, erreur de chargement CDN affichée | IND au cours de cet essai : Pyodide n'a pas chargé malgré GET CDN autorisés. Pas de preuve d'exécution Python réussie ici, ni conclusion de panne universelle. Sauvegarde/partage absents et honnêtement annoncés. |
| Mentoring | R-B/I page “PILOT · NOT ON SALE”, aucun mentor publié, pas de réservation payable | Indisponibilité assumée ; ni humain, ni délai, ni feedback professionnel effectivement délivrés. |
| Starter Kit | R-B/I présentation française et fermeture vente ; R-T ZIP réel, SHA conforme et téléchargement avec grant fixture | L'artefact existe ; un cache de cohorte vide ne permet pas de le déclarer absent. Achat, réexécution Excel et disponibilité humaine NV. |
| Plans, billing, auth, account/support | R-B verrouillages et plans, checkout désactivé, contact non configuré ; R-T refus d'accès et entitlements | Fermeture volontaire, pas panne de paiement. Login/reset/email réel, achat, remboursement, suppression/export global du compte NV. Pas d'espace compte complet trouvé dans le routeur actif inspecté. |
| API, exports, métriques | R-B neuf JSON ; R-T JSON privé Interview, ZIP, CSV, agrégats opérateur et API réelle | `/api` annonce correctement une preview non vendue. Pas de neuf API publiques de pricing ou CLI client uniforme. Activité QA ≠ adoption, revenu ou rétention commerciale. |

## 4. Constats prioritaires et décisions proposées

P0 désigne ici un **blocage de confiance avant exposition commerciale de la surface concernée**, sans prétendre avoir découvert une exécution financière réelle ou une faille de sécurité critique. P1 bloque une tâche ou la cohérence du parcours cible ; P2 dégrade la compréhension, l'accessibilité ou la répétition. Chaque proposition reste une décision à prendre : aucune correction n'est appliquée par cet audit.

### B01 — P0 · Le desk exotique attribue ses nombres à un modèle absent

**Surface :** `/agent-room` → `POST /agent/desk/run`. **Preuve R-T :** deux autocalls Athena Euro Stoxx 50, maturités 3 et 5 ans, retournent 102,21 % du pair et les mêmes sensibilités proportionnelles, avec le modèle annoncé “Local-stochastic vol Monte-Carlo”, smile calibré et 20 000 trajectoires. `_exotic_price` ne lance pas ce Monte Carlo : il calcule une expression arithmétique fixe. Le ticket retourné nomme aussi US Rates (10Y). Le DOM promet que chaque chiffre provient d'un pricer déterministe, “jamais inventé”.

**Conséquence :** un candidat peut apprendre à justifier un prix avec un modèle et un sous-jacent qui ne correspondent pas au calcul. La mention générale “simulation” ne corrige pas cette attribution. **Décision :** rendre ce cas indisponible ou explicitement illustratif, sans faux nom de modèle/Greeks, jusqu'à un vrai moteur et des inputs fidèles. Preuves : [audit technique T02](technical.md), capability-evidence.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/capability-evidence.json`), DOM RFQ de la matrice (preuve locale : `reports/whole-product-cli-audit-2026-11-14/frontend/evidence/route-matrix.json`).

### B02 — P0 · Le WTI est étiqueté Black-76 mais calculé avec un BSM spot

**Surface :** RFQ WTI. **Preuve R-T :** F=K=80, r=4 %, σ=13,41 %, T=0,5 an ; prix API 3,85 ; référence Black-76 calculée indépendamment sur les paramètres littéraux 2,965277. Le chemin `_comm_price` appelle `desk_state.bs`, sans la convention futures annoncée.

**Conséquence :** l'erreur concerne précisément le choix de modèle que l'étudiant doit défendre. **Décision :** aligner formule, données du ticket, actualisation, unités et intitulé, puis faire rejouer ce même exemple et un exemple contrasté. Preuve : commodity-model-comparison.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/commodity-model-comparison.json`). Cela n'invalide pas le Black-Scholes canonique du catalogue.

### B03 — P0 · Le registre/MCP réussit avec des valeurs constantes non signalées

**Surface :** CLI `tool-run`, `mcp-call`, API opérateur `/agent/tools/{name}/run`. **Preuve R-T :** deux tickets dont les prix BSM canoniques sont 10,450575 et 114,877191 retournent tous deux 3,45 `desk_units`, `status:ok`, sans avertissement. Une courbe retourne qualité 0,92 sans courbe ; une perte 10¹² contre limite 1 retourne `PASS_FOR_CONTRACT` et usage 0,55.

**Conséquence :** les descripteurs et succès techniques fabriquent une assurance financière. L'accès opérateur est correctement limité : ce n'est pas un résultat directement accessible à tous les étudiants Pro. **Décision :** séparer outils réels, scaffolds et indisponibles ; ne pas commercialiser ce catalogue/MCP comme pricing intégré avant raccordement aux moteurs. Preuves : CLI (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/cli-evidence.json`), HTTP (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/http-evidence.json`), [T01](technical.md). Les neuf calculateurs ont été exécutés séparément et sont réels.

### B04 — P1 · Le premier dashboard signé part sans identité puis récupère au retry

**Surface :** ouverture directe `/dashboard`, compte non-admin. **Preuve R-B :** `/platform/progress/audit-other` part sans Bearer et reçoit 401, tandis qu'entitlement et Interview envoient leur Bearer et reçoivent 200. “Your progress could not be loaded” s'affiche ; “Try again” réussit dans la même session.

**Conséquence :** le premier retour sur son espace donne l'impression que le compte ou les données sont cassés. **Décision :** attendre la disponibilité de l'authentification pour la requête et la relancer quand l'identité change. La variable globale de token publiée par effet dans `AuthContext.tsx:54` et le chargement de `DashboardPage` (`ClaudeFrontend.jsx:5332`) sont compatibles avec la course observée ; la cause exacte reste à confirmer sans fixture. Preuves : dashboard-reproduction-api.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/dashboard-reproduction-api.json`), état initial (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/dashboard-direct-auth-state.json`), après retry (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/dashboard-retry-with-same-session.json`). Le harness conserve l'absence du header ; il ne la répare pas.

### B05 — P1 · Le dashboard affirme qu'aucune activité n'existe après une tentative sauvegardée

**Surface :** `/interview` puis `/dashboard`. **Preuve R-B :** une tentative `call-quote` conservée, 1 contrôle numérique réussi, puis “No activity recorded yet” après le retry réussi et après navigation SPA. Une nouvelle session reprend pourtant le bon feedback du Lab. **I/R-T :** Dashboard lit l'ancien `platform_progress`, le Lab écrit un autre ledger.

**Conséquence :** le candidat ne peut pas utiliser son accueil pour savoir où il en est. Ce n'est pas une perte de tentative. **Décision :** projeter les activités du Lab dans l'accueil, avec des catégories distinctes : tenté, numérique correct, transfert, auto-revue ; ne pas les appeler maîtrise certifiée. Preuves : activation (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/activation-continuity.json`), comparaison (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/dashboard-and-free-boundaries.json`), reprise (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/activation-fresh-account-resume.json`).

### B06 — P1 · La bibliothèque payante est française pour une cible de lancement anglophone

**Surface :** les 12 scripts `/courses/{id}/script`, Trading Lab, backtest, RFQ, Kit. **Preuve R-B :** les 12 scripts lus sont substantiels et français ; les cartes de cours et une partie de la navigation sont anglaises. Le Lab et les nouveaux exercices anglais existent réellement. Les labels “historical French” préviennent la limite, mais ne rendent pas le programme utilisable par un candidat ne parlant pas français. R-T : `cli course --language en` produit encore un template français.

**Conséquence :** six cas anglais ne constituent pas une bibliothèque entière d'entretiens en anglais ; le plan promet un prolongement que ce candidat ne peut pas suivre. **Décision :** définir explicitement le premier programme anglais vendu et traduire/éditer ses cours et transitions, ou proposer le français comme catalogue distinct. Preuves : course-editorial-inventory.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/course-editorial-inventory.json`), Trading Lab/backtest/RFQ DOM (preuve locale : `reports/whole-product-cli-audit-2026-11-14/frontend/evidence/route-matrix.json`), [T05](technical.md). Aucune absence générale de contenu n'est alléguée.

### B07 — P1 · L'exercice recommandé après volatilité réalisée change de problème

**Surface :** `/tools/iv-calc` → “Exercise ↗”. **Preuve R-B :** après cinq estimateurs OHLC réels, le lien ouvre `/exercises/iv-newton`, “Implied Vol via Newton-Raphson”, inversion d'un prix d'option. Le mapping est explicite dans `ClaudeFrontend.jsx:520`.

**Conséquence :** confusion entre volatilité historique estimée et volatilité implicite ; l'outil explique lui-même cette distinction avant de la brouiller dans le parcours. **Décision :** un exercice sur calendrier, ajustement, overnight et comparaison des estimateurs ; proposer l'IV comme comparaison nommée, pas comme continuation directe. Preuves : résultat réel (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/realized-vol-actual-result.json`), destination (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/realized-vol-learning-link-destination.json`).

### B08 — P1 · Le défi barrière n'ouvre pas un notebook permettant de faire ce défi

**Surface :** `/challenge` → Open Notebook → `/notebooks`. **Preuve R-B :** le défi demande down-and-out, formule et Monte Carlo avec 100 000 trajectoires/antithétiques/intervalle ; le bouton ouvre le seul `black-scholes-intro.ipynb`, sans code barrière et sans reprise du ticket. Le lancement Python a ensuite échoué au chargement du CDN Pyodide : aucune exécution Python réussie n'est revendiquée.

**Conséquence :** l'utilisateur arrive dans un autre exercice et doit construire lui-même la plupart du contexte annoncé. **Décision :** ouvrir un starter dédié avec les mêmes paramètres et une voie de correction, ou renommer le bouton vers le laboratoire BS générique. Offrir une sortie locale quand le runtime ne charge pas. Preuves : défi (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/barrier-challenge.json`), destination (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/challenge-opened-notebook.json`), erreur Run (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/notebook-python-run.json`). L'erreur CDN est une indisponibilité observée, pas une preuve que Pyodide ou tous les notebooks seraient fictifs.

### B09 — P1 · Le mode assistant hors ligne termine avec succès en changeant le ticket et la langue

**Surface :** assistant AG-UI. **Preuve R-T :** demande anglaise S=125/K=110/r=3 %/q=1 %/σ=30 %/T=0,75 an ; stream `runtime:offline`, remplacement par S=100/K=100/r=2 %/q=0/σ=20 %/T=180 jours, réponse française, puis succès.

**Conséquence :** un candidat peut croire que sa question a été traitée. Le calcul sur le nouveau ticket peut être cohérent tout en ne répondant pas au besoin. **Décision :** annoncer une démo fixe avant interaction, conserver le ticket ou demander confirmation de son changement ; ne pas annoncer un assistant généraliste avant preuve. Preuve : capability-evidence.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/capability-evidence.json`), [T04](technical.md). LLM live NV, pas présumé absent.

### B10 — P1 · La vente et le cycle de support ne sont pas prêts ; la fermeture est correcte

**Surface :** `/pricing`, `/contact`, billing, kit, mentoring. **Preuve R-B :** “PREVIEW · SALES DISABLED”, boutons non achetables, contact non configuré. R-T : mock/configuration fermée, checkout signé refusé pour exigences non validées. Les droits/source, identité légale, support, paiements et emails réels ne sont pas certifiés.

**Conséquence :** aucun parcours de vente autonome livrable aujourd'hui. Cette fermeture évite une fausse promesse ; ce n'est pas un bug à contourner pour vendre. **Décision :** maintenir la fermeture jusqu'aux validations externes et au parcours achat→accès→support→annulation/remboursement. Ne pas vendre une disponibilité de mentor non établie. Preuves : destination plans (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/free-upgrade-destination.json`), matrice contact/pricing (preuve locale : `reports/whole-product-cli-audit-2026-11-14/frontend/evidence/route-matrix.json`), HTTP (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/http-evidence.json`), PRODUCTION_READINESS.md.

### B11 — P2 · L'offre libre/les paliers cassent certaines continuités pédagogiques

**Surface :** cours BS → Exercises pour un membre gratuit ; outil MC Starter → Course. **Preuve R-B :** la zone d'exercice demande Starter et propose “See plans”, alors que la vente est fermée ; le Lab disponible n'est pas proposé dans le verrou lui-même. Starter exécute le vrai MC, mais son lien Course conduit à un cours réservé Pro.

**Conséquence :** l'étudiant arrive à une impasse précisément lorsqu'il veut prolonger une première réussite. **Décision :** donner le prochain exercice utilisable dans son droit et annoncer avant le clic les extensions de plan. L'accès payant est attendu et ne doit pas être supprimé pour masquer la friction. Preuves : verrou free (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/free-course-exercise-boundary.json`), verrou cours MC (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/starter-tool-course-access-boundary.json`), parcours associé (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/adjacent-learning-journeys.json`).

### B12 — P2 · Lecture, quiz et calculs ne forment pas encore une mesure commune de préparation

**Surface :** cours historiques, outils, dashboard, Interview. **Preuve R-B/I :** six quiz sur douze ont les cinq bonnes réponses à la même position (trois AAAAA, trois BBBBB), avec les réponses immédiatement lisibles dans le script. Les outils ont calculs, preuves et historiques locaux ; la mesure conservée du Lab concerne son propre périmètre. R-T : les exercices génériques livrent corrigé/barème sans contrat de tentative générique.

**Conséquence :** la richesse des contenus ne permet pas de conclure “je sais expliquer ce hedge maintenant”. Un motif pour revenir reste à construire à travers les modules. **Décision :** priorité à un petit diagnostic et à deux variantes comparables d'une même compétence ; séparer complétion, réussite numérique et argumentation. Ne pas convertir artificiellement les anciennes lectures en score de maîtrise. Preuve : 12 quiz inspectés (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/course-editorial-inventory.json`), état réel du Lab (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/activation-continuity.json`), [matrice technique](technical.md).

### B13 — P1 · Accessibilité : des champs sans nom et un contraste insuffisant sur des actions importantes

**Surface :** Payoff, Calibration, Backtest, Credit et plusieurs boutons. **Preuve R-T frontend :** 118/175 vues ont au moins une violation Axe, avec répétitions de routes/acteurs ; 117 contiennent le problème de contraste. Blanc sur rose : 3,55:1 contre 4,5:1 attendu pour le texte courant. La configuration backtest contient notamment un capital sans label et trois selects sans nom accessible. Des noms de boutons manquent aussi sur deux vues.

**Conséquence :** une partie du produit ne se commande pas avec la même clarté via lecteur d'écran ; le texte d'action est moins lisible. Les documents déclarés anglais contenant de longs blocs français ajoutent une difficulté de prononciation potentielle. **Décision :** corriger les tokens d'action, associations nom/champ et langues déclarées dans les surfaces concernées, puis rejouer les formulaires au clavier et avec lecteur d'écran. Les menus, skiplinks et retour de focus déjà testés fonctionnent : il ne faut pas refaire toute la navbar. Preuves : route-matrix.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/frontend/evidence/route-matrix.json`), [rapport frontend](frontend.md). Axe ne constitue pas une certification d'accessibilité générale ; 118 vues ne veut pas dire 118 défauts uniques.

### B14 — P2 · Le bouton au nom de l'utilisateur déconnecte au lieu d'ouvrir son compte

**Surface :** navbar desktop authentifiée. **Preuve R-B/I :** nom accessible “Audit” dans la cohorte ; `ClaudeFrontend.jsx` vers 692–699 lie ce bouton à `handleSignOut`, sans texte “Sign out” à cet endroit. Le menu mobile, lui, possède un texte de déconnexion. Aucun logout n'a été déclenché par cette recette.

**Conséquence :** action difficile à anticiper et pas d'entrée claire vers préférences/compte pour un utilisateur payant. **Décision :** nommer explicitement l'action de sortie et rendre le chemin compte/support compréhensible. Préserver le dessin et le logo acceptés. Preuve : capture DOM après tentative (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/activation-interview-record-after-attempt.json`), source active précitée. Un espace compte complet n'a pas été trouvé dans le routeur inspecté ; son fonctionnement extérieur reste NV.

### B15 — P2 · L'onglet d'un cas ouvert peut conserver un titre d'échec

**Surface :** `/interview/call-quote`, desktop et mobile. **Preuve R-T frontend :** le cas et la tâche sont visibles mais le titre du document reste “This case could not be opened.” après trois secondes, reproduit deux fois. L'observateur RouteMetadata cesse de suivre après un premier h1 transitoire.

**Conséquence :** contradiction entre l'écran, l'onglet et l'historique ; difficulté à retrouver son travail parmi des onglets. **Décision :** publier les métadonnées à partir de l'état de route résolu. Ce n'est pas une preuve que le cas ou sa reprise ne fonctionne pas. Preuves : [rapport frontend F05](frontend.md), contrôles de navigation (preuve locale : `reports/whole-product-cli-audit-2026-11-14/frontend/evidence/navigation.json`) ; cause source inspectée par cet agent, non retracée indépendamment par Business.

### B16 — P2 · La largeur du SaaS ne donne pas encore un motif de paiement supplémentaire démontré

**Surface :** forum, jobs, blog, mentor, API, backtest autour du cœur interview/pricing. **Preuve R-B/I et R-T :** forum/CRUD et backtest existent réellement, mais les contenus visibles de la cohorte sont des fixtures ; mentor non disponible ; API privée non vendue ; dataset de marché en cache daté, explicitement signalé. Aucun client, communauté active ou catalogue de postes réel n'est établi par ces preuves.

**Conséquence :** un candidat doit distinguer seul pratique d'entretien, recherche/backtest, service humain et produit téléchargeable. Le nombre de rubriques ne prouve pas la valeur de l'abonnement. **Décision :** organiser l'activation autour du cas d'entretien et de son prochain entraînement ; garder les extensions accessibles avec leur statut, mais ne pas les additionner comme raisons de payer non validées. Évaluer l'intérêt avec des candidats avant de développer davantage de modules. Preuves : matrice DOM (preuve locale : `reports/whole-product-cli-audit-2026-11-14/frontend/evidence/route-matrix.json`), [capacités techniques](technical.md). C'est un jugement de cohérence et une hypothèse de marché à tester, pas la preuve qu'aucun étudiant n'utiliserait ces fonctions.

## 5. Score et décision, strictement périmétrés

Les nombres ci-dessous sont des **jugements de cette revue experte**, pas des données de clients, taux de satisfaction ou mesures de PMF. Ils portent sur l'offre entière présentée au candidat anglophone, avec ses surfaces visibles et sa capacité actuelle à soutenir une bêta payante. Une moyenne ne peut pas lever un blocage de confiance.

| Critère du skill Business | Note /100 | Motif principal |
| --- | ---: | --- |
| Clarté | 68 | Première action libre concrète ; Lab lisible ; mais changements de langue, sujets et paliers et plusieurs états concurrents de progression. |
| Confiance | 45 | Exports et limites des outils convaincants ; fausses attributions de modèles RFQ et valeurs constantes du registre empêchent de se fier à l'offre entière. |
| Utilité | 80 | Neuf moteurs, contenus substantiels, réponse/correction/reprise anglaises ; continuité et preuve de maîtrise encore trop locales. |
| Préparation commerciale | 35 | Droits et vente volontairement fermés ; support, cycle de paiement, service humain et exploitation publique non validés ; cible linguistique partiellement servie. |
| **Moyenne simple globale** | **57** | **FAIL**, sous le seuil 90 et avec blocages de confiance. |

Le calcul 57 est exact pour ces quatre jugements ; il n'a pas une précision statistique de ±1 point. Les fonctions NV ne reçoivent pas de score inventé. Les constats s'appuient sur les parcours et preuves détaillés, pas sur cette moyenne seule.

| Décision de lancement | Verdict | Conditions |
| --- | --- | --- |
| Pilote local encadré, Lab anglais + calculateurs canoniques | **GO conditionnel, périmètre restreint** | Dire six cas, pas programme universel ; conserver réponses/variantes/limites ; utiliser le hub Lab pour reprendre ; ne pas inclure desk/registre comme référence de pricing. Les défauts de dashboard/titre sont documentés. Ce n'est pas un nouveau PASS global à 94. |
| Produit entier en libre-service autonome, même local | **NO-GO** | Fermer B01–B05 ; rendre le programme cible et ses transitions fidèles ; statuts indisponibles/illustratifs explicites. |
| Vente publique de l'abonnement SaaS entier | **NO-GO** | En plus du parcours, preuves légales/droits/support/paiements/emails, accès et gestion du compte en déploiement ; aucun contournement des verrous commerciaux. |
| Promesse de communauté, mentorat humain, MCP quant complet ou maîtrise certifiée | **NON VALIDÉE** | Demande des preuves distinctes de disponibilité réelle, service et résultat ; les fixtures et un catalogue de contrats ne les apportent pas. |

## 6. Ordre de décision recommandé, avant d'écrire des correctifs

1. **Sanctuariser la confiance.** Décider quelles surfaces RFQ/registre sont réellement supportées, puis bloquer les faux succès. Conserver les neuf moteurs canoniques, leurs unités et exports comme référence indépendante.
2. **Finir un seul parcours candidat.** Mêmes données du brief au calcul, réponse personnelle avant correction, variante et reprise dans un accueil fidèle ; récupérer proprement une première requête en erreur. Corriger les transitions qui changent de problème avant d'ajouter d'autres exercices.
3. **Décider le périmètre anglais vendu.** Ce choix ne peut pas être remplacé par des labels sur le français. Un petit programme maîtrisé est testable ; une promesse de tout le cursus en anglais ne l'est pas dans l'état actuel.
4. **Préparer un test réel de valeur, puis la vente.** Sur un cas de 30–60 min, observer sans aider si un candidat conserve les conventions et explique son hedge. Deux semaines plus tard, proposer une variante et comparer les réponses conservées, avec consentement. Relever frictions, retours et raisons déclarées de payer ; ne pas transformer le temps, la complétion ou l'auto-revue en preuve de compétence. Les prix de stratégie sont des hypothèses, aucune vente ni offre externe n'a été faite par cet audit.

## 7. Traçabilité, données d'audit et limites

Sources reproductibles Business : harness signé (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/cohort-browser.mjs`), inventaire visiteur (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/visitor-inventory.json`), neuf outils (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/nine-tools-first-use.json`), activité/reprise (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/activation-continuity.json`), dashboard et plans (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/dashboard-and-free-boundaries.json`), continuités (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/adjacent-learning-journeys.json`), cours (preuve locale : `reports/whole-product-cli-audit-2026-11-14/business/course-editorial-inventory.json`). Les `.png` associés conservent l'état d'écran, les `.json` conservent son texte et ses contrôles.

Les réponses financières de neuf outils ont été réellement calculées ; exemples de cette séance : BS call 10,4506/put 5,5735 avec parité PASS, Iron Condor crédit 331,51, MC 10 000 trajectoires avec moyenne terminale 105,126, put américain binomial 300 pas à 6,0877, cinq estimateurs OHLC sur le même échantillon. Les exports existent en octets et se lisent en JSON. Ceci établit leur réalité d'usage, pas une certification indépendante de chaque cas limite. Le détail est dans `nine-tools-first-use.json` et les fichiers `tool-*.json`.

L'unique écriture de réponse Business est la tentative privée `iat_3d1c266caae546b480b0138ea9e26f4d`, `call-quote`, compte fixture non-admin `audit-other`, texte de justification marqué audit. Le parcours a aussi effectué deux appels `POST /interview/session` lors de l'ouverture initiale et de la reprise dans le nouveau contexte, avec réponses 200. Ces activités locales sont de la QA, pas de l'adoption. Elles sont conservées pour la preuve ; aucune donnée existante n'a été supprimée. Les autres écritures des agents techniques sont décrites dans leurs rapports et appartiennent à la cohorte isolée. Aucun contenu Business publié au forum, candidature, email, achat ou ordre n'a été envoyé. Les jetons privés ne sont ni imprimés ni inclus dans ce rapport.

La recette globale n'a pas rejoué tous les variantes/cas limites de chaque module, une partie complète Survival, le run backtest depuis l'UI, un vrai cycle Supabase/SMTP/Stripe, la lecture avec un lecteur d'écran, l'import Excel/Jupyter réel, la fraîcheur de flux live, les LLM externes, la conformité légale ou les droits de redistribution. L'erreur de chargement Pyodide observée reste une indisponibilité de cette séance ; les transports externes et les conditions réseau doivent être examinés avant une conclusion de panne publique. Les dates françaises visibles et les textes mixtes sont pertinents pour la cible anglophone, sans valoir un audit complet de localisation/fuseaux.

Les premières erreurs du harness (hypothèse de plan du compte `other`, sélecteur Course ambigu, mauvais délai d'attente et accès localStorage sur about:blank) ont été corrigées dans les scripts de recette. Elles ne sont pas comptées comme défauts produit. Aucun défaut produit n'a été corrigé au cours de cette mission.
