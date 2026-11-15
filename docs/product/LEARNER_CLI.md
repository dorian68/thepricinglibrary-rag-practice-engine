# CLI utilisateur ThePricingLibrary : `tpl`

`tpl` utilise les API réelles du produit, avec la session et les droits du compte.
La CLI de maintenance reste `python -m pricinglibrary_rag.cli` : ingestion,
configuration opérateur et outils d’orchestration ne sont pas des actions étudiant.

## Installation et première vérification

Depuis le dossier backend, dans un environnement Python 3.11 ou supérieur :

```powershell
python -m pip install -e .
tpl --help
tpl coverage
```

La calibration utilise Node.js et le même moteur JavaScript versionné que le
site, livré dans le paquet backend. Les huit autres moteurs sont Python. Aucun
chemin vers le checkout frontend n’est nécessaire à l’exécution.

Configurez l’API et une session **valide délivrée par le service d’identité** :

```powershell
$env:TPL_API_URL = 'https://api.example.com'
$env:TPL_TOKEN_FILE = 'C:\chemin\prive\session.private.json'
tpl doctor
tpl auth whoami
```

Le fichier contient soit le token seul, soit `{"access_token":"…"}`. Une autre
option est la variable `TPL_ACCESS_TOKEN`. L’option globale `--token-file` prime
sur ces variables. Ne passez pas de token dans les arguments ou les URL. Le client
ne fabrique pas de session et n’obtient pas de droits depuis un profil local.
Une connexion Supabase réelle et les fixtures signées d’un test technique sont
deux situations différentes ; le smoke ci-dessous n’atteste pas une connexion
Supabase de production.

## Connexion, récupération et test local sans navigateur

Le client peut aussi obtenir sa session auprès du même fournisseur Supabase que
le site. Configurez `TPL_SUPABASE_URL` et sa clé publique dans
`TPL_SUPABASE_ANON_KEY` (jamais une clé `service_role` ou `sb_secret`). Le mot de
passe et le code sont lus au prompt masqué ; les options `--password-stdin` et
`--code-stdin` permettent un appel automatisé sans secret dans les arguments.

`--token-hash-stdin` accepte aussi le hash d’un lien de confirmation ou de
récupération, sans ouvrir de navigateur. Le type d’inscription est `email`,
selon le [contrat OTP actuel](https://supabase.com/docs/reference/python/auth-verifyotp).

```powershell
tpl auth signup --email me@example.com
tpl auth verify --email me@example.com --kind email
tpl auth login --email me@example.com
tpl auth whoami
tpl auth recover --email me@example.com
tpl auth verify --email me@example.com --kind recovery --replace
tpl auth password
tpl auth refresh
tpl auth logout
```

La session est enregistrée par défaut dans le dossier personnel
`.thepricinglibrary/session.private.json`, avec mode 0600 ou ACL Windows limitée
au compte courant. `--session-file` choisit un autre emplacement ; remplacer une
session lors d’un login exige `--replace`. Les reçus JSON ne contiennent jamais
les tokens, codes ou mots de passe. Une acceptation de signup/recovery ne prouve
pas la livraison de l’email. [Contrat Supabase Auth](https://github.com/supabase/auth),
[confirmation après inscription](https://supabase.com/docs/reference/python/auth-signup).

Pour le **développement local explicitement autorisé**, le Vite déjà lancé offre
son compte de test signé. Aucune session admin n’est créée automatiquement par la
CLI ; la commande suivante sélectionne volontairement ce rôle de test :

```powershell
tpl auth dev-session --preview-url http://127.0.0.1:5173 --role admin
tpl auth whoami
tpl auth logout --local-only
```

Le rôle par défaut de `dev-session` est `learner`. Cette voie ne fonctionne que
sur loopback avec le gateway de développement existant ; elle est absente du
build public. Le proxy API local est mémorisé dans le fichier de session.
L’environnement ou `--api` garde priorité sur cette adresse.

Les contrats signup, login, vérification, récupération, mot de passe, refresh et
logout sont couverts par des tests HTTP isolés. Une connexion Supabase déployée
et la livraison effective de ses emails restent à valider avec le fournisseur.

L’API distante doit être en HTTPS. HTTP est accepté uniquement sur loopback.
Le client ne suit pas les redirections HTTP avec ses credentials. Pour une API
locale déjà configurée : `tpl --api http://127.0.0.1:8000 doctor`.

## Un premier calcul, sans état caché

```powershell
tpl tools example bs-pricer --output ticket.json
tpl tools run bs-pricer --input ticket.json --output pricing.json
tpl tools run bs-pricer --input ticket.json --format scenario-csv --output scenarios.csv
```

Le fichier d’exemple contient les véritables entrées synthétiques attendues,
directement réutilisables par `run`. Modifiez un spot ou une volatilité et
recalculez. Le prix change par le moteur canonique ; aucune valeur de substitution
n’est renvoyée si le service échoue.

| ID | Droit minimal | Exports en plus du JSON |
| --- | --- | --- |
| `bs-pricer` | Gratuit | `scenario-csv`, `sensitivity-csv` |
| `payoff` | Starter | `curve-csv`, `scenario-csv` |
| `mc` | Starter | `terminal-csv`, `paths-csv` |
| `iv-calc` | Starter | `rolling-csv`, `observations-csv` |
| `bond` | Starter | `cashflows-csv`, `scenario-csv` |
| `curve` | Starter | `curve-csv`, `repricing-csv` |
| `binomial` | Student | `convergence-csv`, `frontier-csv` |
| `calib` | Student | `points-csv` |
| `volsurface` | Student | `points-csv`, `diagnostics-csv` |

Les opérateurs signés peuvent tester les services sous leur rôle explicite.
Les comptes apprenants sont vérifiés par le serveur ; une donnée client ne peut
pas attribuer un plan.

## Cours, tentative, correction et reprise

```powershell
tpl courses list
tpl courses preview black-scholes
tpl courses read black-scholes --language en --output lesson.md
tpl courses open black-scholes --module 1
tpl courses complete black-scholes --module 1
tpl courses resume black-scholes
tpl courses progress

tpl interview catalog
tpl interview task call-quote --output task.json
tpl interview onboard --input onboarding.json
tpl interview answer call-quote --input answer.json --request-id my-attempt-0001
tpl interview review ATTEMPT_ID --input review.json --request-id my-review-0001
tpl interview resume
tpl interview export --output my-private-record.json
tpl interview export --format report --output practice.md
tpl interview export --format csv --output practice.csv
tpl interview export --format anki --output reviewed-cards.tsv
tpl interview calendar --input study-plan.json --output study.ics
```

Les index de module sont **à partir de zéro**. La CLI choisit l’anglais par
défaut pour un cours ; l’API historique conserve le français par défaut. Les
langues réellement disponibles sont indiquées dans le catalogue. Une variante
anglaise absente retourne 404, sans servir silencieusement du français.
La complétion d’un module reste une activité déclarée, pas une note de maîtrise.

Exemple `onboarding.json` :

```json
{"role":"structuring","minutes_per_session":30,"deadline":null}
```

Exemple `answer.json` pour le premier cas :

```json
{"answers":{"price":10.4506,"delta":0.63683},"reasoning":"I used European exercise and continuous rates with no dividend yield. A long call has positive delta and its hedge sells underlying shares."}
```

Exemple `review.json` :

```json
{"criteria":{"assumptions":true,"decision":true,"limitations":false},"notes":"I still need to explain transaction costs and model limitations."}
```

Exemple `study-plan.json` :

```json
{"starts_at":"2026-12-01T18:00:00+01:00","minutes":30,"sessions":6}
```

`--preview` sur `interview answer` utilise le contrôle anonyme du premier cas,
explicitement non sauvegardé. `interview reveal` révèle une correction et marque
l’exposition ; ce n’est pas une tentative indépendante. Les exports du compte
et les tentatives ne sont accessibles qu’au propriétaire. Les cartes Anki sont
des supports de révision ; elles ne transfèrent pas une maîtrise à TPL. Le
calendrier est un plan volontaire, pas un relevé de présence.

## Exercices de bibliothèque et notebooks

```powershell
tpl exercises catalog
tpl exercises open bs-eur-call
tpl exercises task realized-vol-estimators
tpl exercises generate --input request.json --request-id generation-0001
tpl exercises library --limit 20 --offset 0
tpl exercises open EXERCISE_ID
tpl exercises export EXERCISE_ID --format markdown --output exercise.md
tpl exercises answer EXERCISE_ID --input written-answers.json --request-id written-0001
tpl exercises attempts EXERCISE_ID
tpl exercises review ATTEMPT_ID --input written-review.json --request-id review-0001
tpl exercises export-attempt ATTEMPT_ID --format md --output written-record.md

tpl exercises reference mc-asian
tpl exercises run-reference mc-asian
tpl exercises export-reference mc-asian --format python --output asian-reference.py

tpl notebooks list
tpl notebooks open black-scholes-intro
tpl notebooks export black-scholes-intro --output black-scholes.ipynb
tpl notebooks export barrier-down-out --format py --output barrier.py
tpl notebooks run barrier-down-out
```

Les exercices canoniques et les exercices générés privés ont des identifiants
différents. Leurs tentatives écrites utilisent une auto-évaluation documentée,
sans note d’expert ni note automatique inventée. Les réponses du fichier sont
indexées par numéro, par exemple `{"answers":{"1":"...","2":"..."}}`.
Le fichier de revue utilise `criteria` avec les mêmes numéros et des booléens.

Les notebooks fournis sont des exemples originaux autorisés et bornés. `run`
exécute seulement ces exemples prédéfinis ; il n’envoie pas un brouillon Python
arbitraire au serveur. Les exports `.ipynb` et `.py` sont de vrais fichiers.

## Survival et autres surfaces du produit

```powershell
tpl survival start --request-id survival-start-0001
tpl survival list
tpl survival state RUN_ID
tpl survival answer RUN_ID --input survival-answer.json --request-id survival-answer-0001
tpl survival next RUN_ID --request-id survival-next-0001
```

La réponse contient `question_id` et `answer` (`A`, `B`, `C`, `D` ou `timeout`).
Le feedback reste attaché à la question avant `next`. Le serveur calcule le
temps, les points et les vies ; le client n’envoie pas de score. Le mode actuel
est une vague Core de 20 questions, 30 secondes chacune, non surveillée et non
classée comme preuve de recrutement.

| Domaine | Commandes et nature réelle |
| --- | --- |
| Forum | `forum list`, `thread ID`, `create --input`, `reply ID --input`, `vote ID` : lectures/réponses/votes serveur ; les écritures non idempotentes ne sont pas automatiquement rejouées. |
| Jobs / blog | `jobs list`, `jobs apply ID --input`, `blog list`, `blog open SLUG` ; `jobs sources`, `jobs publish --input` et `blog publish --input` sont réservés à l’opérateur. Une liste vide reste vide. |
| Newsletter / classements | `newsletter subscribe --input` enregistre l’inscription sans envoyer d’email. `leaderboard activity` et `leaderboard survival` lisent les classements existants ; les nouvelles sessions Survival non surveillées n’alimentent pas un classement vérifié. |
| Marché | `market catalog`, `universe`, `history SYMBOL --points 260 --provider ...` : provenance conservée ; erreur réelle si fournisseur ou série indisponible. |
| Backtest | `backtest instruments`, `run`, `scan`, `walkforward` ; arguments `--instrument`, `--max-bars`, `--capital`, `--strategy` selon la commande. Les moteurs/données doivent être disponibles sur l’API ; aucun résultat de repli n’est fabriqué. |
| RFQ / paper book | `rfq run --input`, `state`, `trade --input --request-id INTENTION`, `tick --seconds 1` : cotation et simulation, jamais ordre externe. Réutiliser la même clé et le même ticket récupère la transaction unique après une réponse perdue. Les droits Pro, l’isolation et la fidélité du carnet sont contrôlés côté API. Les positions en mémoire ne survivent pas à un redémarrage. |
| Services | `services availability`, `support status`, `support report --input` : états et enregistrement d’incident. Aucun email livré ni disponibilité humaine déduits d’un simple enregistrement. |
| Plans | `plans list`, `entitlement`, `status`, `checkout --plan ...` : configuration, droits et lien de checkout. La CLI n’ouvre pas le navigateur et ne traite pas un checkout simulé comme une transaction. |
| Starter Kit | `kit availability`, `manifest`, `download --output kit.zip`, `checkout`. Le ZIP reçu doit correspondre au SHA-256 du manifeste du compte. Les gates de vente et d’accès restent serveur. |
| Opérateur | `admin counts`, `admin support`, `admin market-providers`, `interview metrics` : droits opérateur requis. Les compteurs d’activité ne sont pas des ventes ni une mesure de product-market fit. |

Le forum `thread` retrouve les discussions parmi les 100 entrées renvoyées par
la route de listing actuelle ; cette limite est explicite. Une pagination de
forum indépendante reste à améliorer avant de promettre un accès illimité à
l’historique.

## Contrat de sortie et erreurs

Sans `--output`, stdout contient un objet JSON `tpl.cli.result.v1` : `ok`,
`command`, `data` ou `error`, puis `meta`. Les receipts de mutation idempotente
contiennent la clé utilisée. Avec `--output`, le fichier reçoit le contenu natif
(JSON, Markdown, CSV, ICS, notebook ou ZIP) et stdout reçoit chemin, taille et
SHA-256. Un fichier existant exige `--overwrite`.

| Code processus | Signification |
| --- | --- |
| 0 | Commande accomplie selon le contrat retourné |
| 2 | Arguments, fichier d’entrée/sortie ou configuration client invalides |
| 3 | Session absente, invalide ou expirée (HTTP 401) |
| 4 | Droits insuffisants (403) |
| 5 | Ressource inexistante ou appartenant à un autre compte (404) |
| 6 | Conflit de version/clé idempotente (409) |
| 7 | Rejet de validation (400/422 et autres rejets client) |
| 8 | Connexion, délai, limitation ou service indisponible |
| 9 | Capacité explicitement non implémentée (501) |

Les entrées JSON sont limitées à 2 MB, les réponses à 32 MB. Les doublons de clés
et nombres non finis sont refusés. `--timeout` vaut 30 secondes, de 1 à 120 ;
`--retries` vaut 1, de 0 à 2. Seules les lectures et actions explicitement
idempotentes ou calculs purs sont automatiquement rejoués. Réutilisez votre
`--request-id` après une rupture de connexion : changer le contenu avec la même
clé doit produire un conflit, pas écraser la première tentative.

## Recette sans bureau

```powershell
python scripts/smoke_learner_cli.py
```

Ce smoke lance un vrai serveur HTTP sur un port isolé et de vrais processus de
la CLI. JWT, plans et publications sont des **fixtures techniques explicites**
dans une base temporaire : il ne s’agit ni d’achats, ni de clients, ni d’une
authentification Supabase de production. Il vérifie calculs/CSV des neuf moteurs,
langues, droits, propriétaires distincts, reprise et exports, puis les nouveaux
parcours pédagogiques. Les services externes, emails et paiements réels demandent
leur propre preuve. `tpl coverage` décrit les commandes livrées ; il ne certifie
pas à lui seul tous les états d’un déploiement.

Pour vérifier le paquet installé hors du checkout, avec ses ressources et les
imports de l’application, lancez `python scripts/check_learner_package.py`.
Ce contrôle utilise un préfixe d’installation isolé et les dépendances de
l’interpréteur courant ; il ne modifie pas son installation globale. Aucun cours
privé n’est embarqué dans le wheel public.

Un checkout neuf peut également lancer une cohorte de test pour les parcours
headless, sans corpus ni fournisseur extérieur :

```powershell
python scripts/serve_learner_fixture.py --port 8432
```

Le programme affiche uniquement l’adresse et le chemin du fichier privé de
credentials, sous `.learner-fixtures/`. Il écoute `127.0.0.1`, préserve les données
des cohortes marquées et refuse un dossier non vide non prévu pour les fixtures.
`TPL_USER_TEST_CREDENTIALS` peut pointer vers ce fichier pour les smokes frontend.
Arrêtez le processus par Ctrl+C après la recette. Ces comptes ne sont jamais des
clients, achats ou preuves d’authentification publique.
