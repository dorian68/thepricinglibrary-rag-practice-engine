# Couverture du client utilisateur — 15 novembre 2026

Le client livré expose 96 commandes nommées. Elles appellent les API réelles et
leurs contrôles serveur. L'opérateur conserve une CLI de maintenance distincte.
Ce tableau décrit la capacité et sa preuve ; il ne promet pas 100 % des états
possibles ni la disponibilité de fournisseurs non configurés.

| Famille `tpl` | Droit et capacité | Preuve normale / erreur / reprise | Frontière extérieure |
| --- | --- | --- | --- |
| `auth` | Signup, login, verify, recover, password, refresh, logout, whoami ; dev-session loopback explicite. | Tests de protocole HTTP, session privée/ACL, secrets hors arguments et receipts, ancien fichier conservé si refresh échoue, redirects refusées. | Pas de login Supabase déployé ou email livré certifié. |
| `doctor`, `coverage` | Santé, disponibilité, identité vérifiée ; inventaire des commandes. | Vrais processus CLI, anonyme/sessions valides/expirées. | Un inventaire n'est pas une preuve de vente. |
| `courses` | Liste/aperçu, EN ou FR privé sous plan, position, completion, reprise et progrès. | Variantes acceptées par hash, modification non approuvée →404/catalogue EN retiré, restauration →lecture ; droits/owner ; module hors limites refusé ; 12 cours EN réels relus par HTTP/CLI. | Scripts et corpus sont privés et ne sont pas livrés dans le wheel. |
| `interview` | Six cas, six variantes, onboarding, réponse/reveal/review, état/reprise, export/rapport/CSV/Anki/ICS ; métriques opérateur. | Tentative réelle, clé répétée et conflit, autre propriétaire, exposition distinguée, reprise, agrégats ; exports Anki vierges refusés. | Auto-revue et numérique ne certifient pas l'embauche ou la maîtrise. |
| `exercises` | Génération, bibliothèque privée, énoncé, tentative, revue et exports ; 14 références calculées. | Génération réellement enregistrée, bibliothèque/owner, réponses écrites numérotées, idempotence, relecture, 14 scripts et 14 notebooks exécutés. | Génération template/RAG vérifiée localement ; fournisseur LLM externe non attesté. |
| `tools` | Liste, ticket d'exemple et exécution des 9 moteurs, sorties JSON/CSV natives. | Tickets modifiés, résultats réels, exports contrôlés, plans refusés et entrées invalides ; calibration Node empaquetée. | Les modèles et leurs hypothèses ne sont pas des conseils ou prix live. |
| `survival` | Plan Student ; start/list/state/answer/next. | Banque/timer serveur, reload, feedback conservé, owner, doublons, trois vies et vingt réponses jusqu'à fin ; API et UI concordent. | Non surveillé et non classé comme compétence vérifiée. |
| `notebooks` | Plan Student ; list/open/export/run des deux exemples autorisés. | Résultats comparés à formules/quadrature, exécution Python autonome, exports valides ; code arbitraire rejeté côté serveur. | Un brouillon personnel exporté s'exécute localement ; pas de serveur d'exécution arbitraire. |
| `forum` | Lecture/écriture sous plan, threads, réponse et vote. | Contributions réellement persistées, vote répété idempotent, refus du compte Free. | Limite de récupération : cent discussions dans le listing actuel. |
| `jobs`, `blog` | Listings/lecture, candidature authentifiée ; publication et sources réservées opérateur. | Publication et lecture réelle en base QA, refus membre, candidature enregistrée. | Aucun contact externe ou email au recruteur envoyé. |
| `newsletter`, `leaderboard` | Inscription publique stockée, lecture des classements selon droits. | Même email QA inscrit deux fois →une ligne ; listes lues sous compte autorisé. | Enregistrement n'est pas livraison d'email ; Survival non surveillé ne devient pas un classement vérifié. |
| `market` | Catalogue, univers, historique sous droits. | Routes réelles, paramètres bornés et erreurs de source conservées ; audit initial sur données locales. | Données/fournisseurs réels et licences à configurer ; aucune série inventée. |
| `backtest` | Instruments, run, scan, walkforward sous droits. | Audit de base sur CSV local/moteur réel ; mêmes routes nommées exposées par le client. | Pas de validation de performance financière ou de toutes les stratégies/données externes. |
| `rfq` | Plan Pro ; prix, état privé, paper trade et tick simulé. | Oracles, six produits fidèles, autre compte vide, même clé après tick/réponse perdue →une seule position ; ticket changé refusé. | Mémoire de processus, maturité contractuelle constante ; aucun ordre broker ou modèle de marché calibré. |
| `services`, `support` | Disponibilité et incident stocké. | État non réservable explicite, incident réel retrouvé dans la vue opérateur. | Aucun rendez-vous humain ou email livré déduit. |
| `plans`, `kit` | État public/entitlement, checkout sous gates et manifeste/ZIP sous droit. | Fail-closed actuel ; tests locaux de cycle signé, duplicata webhook, révocation et artefact. | Stripe réel, mentions, support, source rights et paiement effectif non validés. |
| `admin` | Compteurs, incidents et fournisseurs réservés à l'opérateur. | Refus membres, compteurs exacts et lectures réelles sur la cohorte isolée. | Des compteurs QA ne sont pas des ventes ni une mesure d'adoption. |

Rejouer : `python scripts/smoke_learner_cli.py`, puis
`python scripts/check_learner_package.py`. La suite complète finale comporte
593 tests PASS ; les tests de protocole, API et processus sont complémentaires.
Le launcher `scripts/serve_learner_fixture.py` permet une cohorte headless
reproductible sans interaction avec le bureau.
