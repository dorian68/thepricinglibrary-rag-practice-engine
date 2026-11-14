> Copie publique expurgée du rapport local du 14 novembre 2026. Les preuves brutes, captures de cours, bases, corpus et identifiants de test restent locaux. Cette copie ne livre pas un nouveau CLI ni une correction produit.

# Rejouer l'audit backend et CLI

Rapport principal : [technical-audit.md](technical.md).
Les scripts ci-dessous sont des **harness d'audit**, pas une nouvelle CLI SaaS.
Ils consomment le vrai code/serveur et stockent des fixtures séparées ; aucun
résultat métier n'est remplacé par une réponse simulée dans le transport HTTP.

## Prérequis

- Python et dépendances existantes du backend, Node pour la calibration.
- Arborescence du workspace existant et onze fixtures numériques partagées.
- Pour les parties correspondantes seulement : corpus local original, scripts
  privés de cours, ZIP Starter Kit et repo TRADING/dataset natif.
- Aucun navigateur, aucune commande de bureau, aucun Docker/Ollama requis.

Ne lancez pas ces scripts avec des clés de production. `audit_cohort.py`
construit un environnement propre, désactive la lecture du `.env` personnel et
génère des clés de test temporaires. Les droits de plans sont des fixtures
serveur explicites, jamais une preuve d'achat.

Depuis `<workspace>` :

```text
python reports/whole-product-cli-audit-2026-11-14/technical/audit_cli.py
python reports/whole-product-cli-audit-2026-11-14/technical/audit_runtime.py
python reports/whole-product-cli-audit-2026-11-14/technical/audit_numerics.py
python reports/whole-product-cli-audit-2026-11-14/technical/audit_starter_artifact.py
```

Les sorties sont respectivement `cli-evidence.json`, `runtime-evidence.json`,
`numeric-evidence.json` et `starter-artifact-evidence.json`. Les appels moteurs
rejouables et leurs fichiers d'entrée sont dans `numeric-inputs/`. Le rapport
différencie six CLI moteurs natives des trois fonctions appelées par harness.

## Serveur isolé et véritables appels HTTP

Le processus partagé a été lancé sans fenêtre visible avec :

```text
python reports/whole-product-cli-audit-2026-11-14/technical/serve_cohort.py --port 8427 --cohort shared-review --readonly-corpus
```

Il écoute uniquement `127.0.0.1`. Sa connexion au corpus original est en lecture
seule ; toutes les données de test vont dans `cohort/shared-review/`. Ses
connexions sortantes non loopback sont bloquées dans le processus serveur.
Le runner backtest enfant utilise un CSV local et un moteur de fills simulés
inspectés avant le test ; aucun connecteur broker/ordre extérieur n'est appelé.

**Ne démarrez pas un second serveur sur un port déjà occupé.** Le manifeste
cohort-manifest.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/cohort-manifest.json`) expose l'adresse, les rôles et les
chemins, sans secret. `serve_cohort.py` reste attaché au processus d'exécution et
s'arrête par interruption de celui-ci ; aucun service permanent n'est installé.

```text
python reports/whole-product-cli-audit-2026-11-14/technical/audit_http.py
python reports/whole-product-cli-audit-2026-11-14/technical/audit_capabilities.py
```

Ces deux scripts écrivent `http-evidence.json`, `openapi.json` et
`capability-evidence.json`. Les extraits du corpus sont retirés des preuves
destinées au rapport ; les contenus privés des cours sont inspectés par hash,
taille et marqueurs, sans en recopier le texte.

Pendant la recette Business convenue, **ne pas relancer `audit_http.py`** :
`audit-other` lui est réservé pour activation/reprise. Le premier passage
technique a utilisé cet identifiant pour un commentaire/vote de forum et des
refus d'accès, mais aucune tentative/onboarding/session active Interview.
Les autres données de QA préexistantes sont conservées ; aucun reset n'est
autorisé pour obtenir artificiellement un résultat.

Une cohorte neuve utilise un autre nom et un port libre. Elle constitue un autre
store, sans effacer les précédents. Le serveur optionnel 8428 a été arrêté ; le
serveur partagé retenu pour cette recette est 8427.

## Accès de test pour une recette headless

Les identités `free`, `starter`, `student`, `pro`, `other`, `operator` sont dans
`cohort/shared-review/session-credentials.private.json`, ignoré par Git.
Le visiteur n'envoie aucun Bearer. Ne jamais imprimer/copier ces jetons dans un
rapport, un log, une URL ou un dépôt public.

Le helper cohort_client.mjs (preuve locale : `reports/whole-product-cli-audit-2026-11-14/technical/cohort_client.mjs`) fournit :

```javascript
import { auditSession, auditHeaders, cohortFetch } from './cohort_client.mjs';
const sessionFixture = auditSession('pro'); // Ne pas logger cette valeur.
const headers = auditHeaders('pro');
const response = await cohortFetch('/interview/state', {role:'pro'});
```

Il fournit des fixtures cohérentes pour adapter le transport d'authentification
local/headless au vrai serveur d'audit. Il ne remplace ni le calcul métier ni une
vraie connexion Supabase. Le provider local actuel traite `hasPlan` comme
admin/gratuit seulement : une simple réécriture de `__dev/session` en plan Pro
ne suffit pas à prouver une interface membre payant. La recette doit utiliser
un provider cohérent ou nommer précisément cette limite de fixture.

## Portée des résultats

- 22 commandes CLI initiales + 20 commandes runtime, toutes terminées avec code 0.
- Véritable transport MCP JSONL : 2 réponses, processus terminé avec code 0.
- 61 requêtes HTTP de parcours, puis 8 capacités/contraintes supplémentaires.
- 9 moteurs, 10 calculs et 7 exports CSV d'exemple réellement exécutés.
- Starter Kit local : 7 livrables, vérification de bundle code 0, vrai download
  3 642 930 octets conforme au SHA après un grant de test ; 401/403 sans droit.

Ces réussites de transport/exécution ne sont pas un verdict fonctionnel global :
le registre retourne notamment 3.45 pour des prix incompatibles, et des modèles
RFQ annoncés ne correspondent pas à leur implémentation. Le rapport principal
explique ces blocages, les capacités réellement solides et les commandes produit
encore manquantes. Aucun achat réel, visiteur réel, conversion, déploiement public
ou PMF n'est déduit de cette activité de QA.
