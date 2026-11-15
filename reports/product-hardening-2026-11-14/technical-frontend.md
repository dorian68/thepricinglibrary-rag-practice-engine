# Cycle 1 — corrections frontend et parcours cohérents

14 novembre 2026. Rôle Technical RL ; mise en œuvre et tests uniquement par CLI, API et Chromium `headless:true`. Aucun contrôle du bureau. Le smoke a également été rejoué avec les anciennes tentatives conservées, sans reset de store. Ce rapport ne remplace pas la validation indépendante Business et ne donne pas un PASS global au SaaS.

## Contrats d’acceptation et changements

| Audit / contrat | Implémentation | Preuve actuelle |
| --- | --- | --- |
| B04 : accès direct au dashboard authentifié | Le token est publié avant `setSession` dans AuthContext ; `getProgress` reçoit aussi explicitement le token de la session et attend son état prêt. | Premier GET progress non-admin Pro, Bearer présent, HTTP200 sans retry. |
| B05 : activité Lab visible sans altérer le registre des cours | Le DTO backend `interview` apparaît dans une section dédiée, avec tentatives, tâches numériques distinctes, checks indépendants et auto-revues. `events` legacy n’est pas renommé en maîtrise. Reprise bornée à `/interview/{case}?variant=primary|transfer`. | Vraie réponse enregistrée, dashboard actualisé, lien de reprise ouvrant le même feedback. Pas de faux « No activity recorded yet ». |
| B14 : nom du compte n’entraîne plus une déconnexion surprise | Le nom ouvre des actions de compte ; route `/account` avec identité, accès courant, réactualisation, liens travail/mot de passe/support/vie privée et bouton Sign out explicite. | Menu ouvert sans logout puis navigation réelle vers le compte. Hero, logo et composition de la navbar conservés. |
| F01 : contraste des boutons d’action | Fond rose de marque conservé, premier plan sombre lisible ; hover du variant finance ne réduit plus le fond à 85% d’opacité. | Axe ne relève aucune violation dans les onze états ciblés contrôlés. Ce n’est pas une certification de tous les états. |
| F02–F04 : champs et régions défilantes nommés | Labels par jambe/paramètre dans Payoff, association Label/combobox Radix en Calibration, champs Backtest/Credit nommés ; exemples API et ticker du desk atteignables au focus. | Payoff, Calibration, Backtest, Credit et API inspectés par Axe ; Payoff/Calibration aussi à 390 px. |
| F05 : métadonnées transitoires | L’observateur de la route reste actif jusqu’à navigation au lieu de se déconnecter au premier H1. | Cas réel ouvert et titre d’onglet égal au titre de la tâche après chargement. |
| F06 : langue annoncée | La livraison de cours conserve `Content-Language` dans son état ; la prose est marquée selon la langue effectivement reçue. Preview anglais, historique français et Starter Kit français restent distingués. | Chemin de contenu réel exercé. Le sélecteur de variantes anglaises attend les artefacts/capacités backend du cycle suivant. |
| B07 : volatilité réalisée vers la bonne pratique | Nouveau cas original `realized-vol-estimators`, mêmes douze lignes OHLC synthétiques que l’outil, onze sessions et cinq estimateurs. L’ancien exercice IV reste disponible. | Le lien ouvre ce cas ; sa solution Python concorde avec les cinq estimateurs du moteur JS à `1e-12`. |
| B08 : barrière vers le vrai notebook | `/challenge` ouvre `/notebooks?lab=barrier-down-out`. Deux labs originaux, sources éditables, brouillons locaux par compte, vrais exports `.ipynb`/`.py`, retour au même problème. | Le fichier téléchargé est réellement exécuté en Python et conserve ticket, modèle, Monte Carlo et intervalle. Aucune sauvegarde cloud ou correction humaine revendiquée. |
| Notebook : erreur CDN et calcul bloquant | Python s’exécute dans un Worker dédié, avec Stop, timeout de 60 s, récupération après échec et source conservée. | Échec CDN contrôlé deux fois avec nouvelle tentative ; exécution réelle de Pyodide vanilla en navigateur également réussie séparément. |
| B11 : prolonger une action malgré une vente fermée | Le verrou garde ses droits, explique la disponibilité et propose le pilote anglais utilisable. | Compte gratuit refusé dans Exercises puis lien vers le vrai Lab ; aucune levée de droits payants. |
| Affichage RFQ de données manquantes | `null`, chaîne vide et booléen ne deviennent plus le nombre zéro ; risque sans limites affiché « not assessed », sans approbation verte. | Contrat numérique/null et message de risque testés ; les calculs/backend RFQ restent la responsabilité du cycle technique dédié. |

## Exécution mathématique du nouveau notebook barrière

Ticket original hypothétique : S100, K100, H85, taux continu2%, volatilité20%, T0,5 an, zéro dividende/rebate, observation continue. Domaine du code : H≤K, H<S ; aucun autre modèle exotique n’est revendiqué.

Le modèle est un GBM. La formule fermée utilise la décomposition vanilla − down-and-in. Le MC conditionne la survie continue au terminal par Brownian bridge et emploie des normales antithétiques : 100000 tirages terminaux, 50000 moyennes de paires indépendantes pour l’erreur standard. Aucun pas de temps discret n’est confondu avec une barrière continue.

- Formule fermée : **6,066750199334226**.
- Vanilla : **6,120654113455842** ; down-and-in : **0,05390391412161555**.
- MC avec seed7 : **6,070291031648397** ; erreur standard **0,022178750608832423**.
- IC95% : **[6,026820680455085 ; 6,113761382841709]**.

Parité in/out, barrière éloignée, borne de nombre de tirages et cohérence des paires sont rejouées en Python. Cet intervalle traite l’erreur d’échantillonnage, pas le risque de modèle. Le fichier public est une création pédagogique originale, sans extrait de cours privé.

Le Worker suit l’API de la version épinglée du runtime ; l’absence de blocage du thread d’interface est le but de cette séparation. [Documentation Pyodide 0.26.2 — web worker](https://pyodide.org/en/0.26.2/usage/webworker.html).

## Vérification effectuée

- `npm run smoke:product-hardening` : **8 contrats PASS**, dont deux sources réellement exécutées en Python, notebook structure4.5, cinq estimateurs Python/JS, catégories de progression, reprise locale sûre, null RFQ, annulation/retry/timeout du transport Worker. Les tests de transport ne prétendent pas charger le CDN.
- `npm run smoke:product-hardening:browser` : **18 contrôles PASS** sur le vrai frontend et l’API isolée signée. Identité transport fixture explicite ; les calculs et écritures métier ne sont pas remplacés par des réponses simulées. Zéro `pageerror`.
- Axe4.14.0 : **zéro violation détectée dans onze états ciblés** : accueil, dashboard, compte, Payoff, Calibration, Backtest, Credit, API à1440px ; Payoff/Calibration/Account à390px. Pas de conclusion WCAG globale, lecteur d’écran natif ou zoom400%.
- `npm run smoke:notebook:browser-runtime` : **PASS**, vrai chargement des assets Pyodide épinglés et exécution Python en Worker headless ; résultat vanilla6,120654113455842. Seuls les GET du CDN épinglé sont autorisés en sortie dans ce test, en plus de l’API locale et du transport d’identité contrôlé.
- Build de production, typecheck, auth-freshness, product-contract, visual-shell, budget du bundle : **PASS**. `npm audit --omit=dev` : zéro vulnérabilité runtime signalée. Le nouveau scanner Axe est une dépendance de développement épinglée.
- `npm run smoke:ux:browser` : **12 étapes PASS**, dont logo original/SHA, Courbe signature et ancrage de prix à huit largeurs320–1440px, activation gratuite réelle, navigation clavier, menu mobile, zéro erreur/asset cassé. Aucun changement de hero approuvé.

Le garde product-contract référençait déjà un ancien index Survival absent de HEAD avant ce cycle ; il accepte désormais l’index canonique actuel. La logique du jeu n’a pas été modifiée ici.

## Rejouer sans bureau

Depuis `WEBSITE/thepricinglab`, frontend local5173 et cohorte signée en fonctionnement :

```powershell
$env:TPL_USER_TEST_CREDENTIALS='<workspace>/reports/whole-product-cli-audit-2026-11-14/technical/cohort/frontend-hardening/session-credentials.private.json'
npm run smoke:product-hardening
npm run smoke:product-hardening:browser
npm run smoke:notebook:browser-runtime
npm run typecheck
npm run build
npm run smoke:product-contract
npm run smoke:visual-shell
npm run smoke:bundle
npm run smoke:ux:browser
```

La cohorte utilisée ici écoute uniquement127.0.0.1:8429, sous le nom `frontend-hardening`. Elle a été lancée par `python reports/whole-product-cli-audit-2026-11-14/technical/serve_cohort.py --port 8429 --cohort frontend-hardening`. Aucun corpus original attaché. Les écritures sont des tentatives QA dans son store ; aucune base utilisateur n’a été réinitialisée. Le smoke est prévu pour être rejoué sur ce store sans supprimer les anciennes tentatives.

Fichiers privés de credentials à ne jamais imprimer/publier. Preuves locales : `frontend/browser-evidence.json`, `frontend/notebook-browser-runtime.json`, `frontend/ux-regression/`. Les captures peuvent montrer du contenu privé et restent locales.

## Limites et suite

**Technical RL PASS pour ce cycle borné ; revue Business indépendante requise.** Le catalogue entier, la vente publique et les calculs agentiques ne reçoivent aucun nouveau PASS par extrapolation.

Cycle2 planifié : consommer le vrai protocole de partie Survival serveur, la tentative d’exercice générique et les nouveaux exports portables Lab ; ajouter le choix de langue de cours seulement lorsque les variantes backend sont effectivement disponibles. Les données publiques/privées et les contrats de paiement/support restent sous leurs vrais droits et exigences externes. Aucun commit/push exécuté par cet agent ; consolidation Git par le parent.

## Cycle 2 — mise à jour du 15 novembre

Le cycle2 est maintenant implémenté et validé localement : Survival serveur persistant, tentatives écrites, 14 références exécutables, exports portables, choix réel EN/FR, correction des contrats/refus RFQ et reprise idempotente paper trade. **Run complet rejoué30 contrôles PASS**,13 contrôles de continuité supplémentaires,14 exécutions Python, maths au clavier, grande suite fonctionnelle, dernier budget performance inchangé et revue Business indépendante PASS. La preuve globale finale est isolée dans `frontend/cycle2/full/`. Détail, inventaire et limites dans [technical-frontend-cycle2.md](technical-frontend-cycle2.md). Les anciennes cohortes QA sont fermées ; Vite5173 et le preview utilisateur4195 restent disponibles. La vente publique et les droits/facturations réels gardent leurs gates propres.
