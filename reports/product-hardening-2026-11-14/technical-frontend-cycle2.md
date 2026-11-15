# Technical RL — Frontend, cycle 2

Réalisé les 14–15 novembre 2026. Cible : étudiants de master finance et candidats anglophones aux métiers de marché. Travail exclusivement CLI, navigateur Chromium headless pour les parcours ; aucun contrôle du bureau.

**Technical RL : PASS local pour le périmètre de ce cycle, avec Business PASS indépendant et performance PASS.** Le run complet a été rejoué après les retours Business : 30 contrôles, 6 états Axe sans violation et zéro erreur JavaScript. S'ajoutent 13 contrôles de continuité/refus, 4 états Axe, 14 références réellement exécutées et un contrôle de mathématiques QA. La revue Business indépendante a validé les corrections et les trois équations réelles Stochastic à320px. La suite générale fonctionnelle est passée après actualisation des anciens contrats de tests ; le dernier budget mobile est respecté sans changer ses seuils. La vente publique, les droits et paiements réels conservent leurs gates distincts.

## Résultat livré

| Parcours | Comportement réel et limites | Preuve |
| --- | --- | --- |
| Survival | Questions, temps, vies, score, réponses, feedback et reprise appartiennent au serveur commun avec le CLI. Le reload conserve le délai de 30 s ; le feedback attend Next. Trois vies ; vingt questions ; score `max(50, (30-floor(elapsed))*12)` si correct. Aucun classement ou certificat de maîtrise. | Réponse correcte puis reload ; attente réelle d'expiration ≥30 s ; trois vies perdues ; nouvelle partie avec 20 réponses via les boutons ; reprise de la partie terminée ; lecture privée refusée à un autre compte. |
| Exercices écrits | Tentatives privées pour les exercices générés enregistrés et les 14 canoniques. Réponse et raisonnement sauvegardés avant comparaison ; historique, revue personnelle séparée, reprise et exports JSON/Markdown. Le résultat numérique de référence n'est pas une note automatique de prose. | Trois réponses réelles, une revue enregistrée, reload du même identifiant et des notes, export contenant les réponses originales ; autre compte Pro →404. |
| Dashboard et reprise | Une seule lecture progress fournit aussi le vrai bloc learning. Compteurs distincts pour réponses écrites, auto-revues, parties commencées, réponses chronométrées et parties terminées. Un run ouvert sans réponse n'est pas une soumission ; une partie terminée n'est pas une réussite certifiée. | Cohorte neuve, aucun événement legacy : deux tentatives et revue récente de l'ancienne, lien exact et GET privé direct `?attempt=`, reload ; partie à0 puis1 réponse visible et reprise du même feedback. |
| Références pratiques | Les 14 identifiants restent disponibles. Solution, sortie, ticket, conventions, hypothèses et limites viennent des mêmes assets que les API/CLI. Chargement JSON dynamique à l'ouverture de l'exercice. Exécution serveur strictement enregistrée, export Python/Jupyter réel ; l'action ne prétend pas exécuter le code édité de l'apprenant. | 14 pages ouvertes ; égalité des assets frontend/backend ; 14 fichiers Python exécutés et confrontés aux résultats/contrôles/sorties affichés ; exécution API ; source téléchargée exécutée ; notebook format4 avec cellule de code. |
| Portabilité Lab | Rapport lisible, CSV, Anki TSV et calendrier ICS. Anki concerne uniquement les cas primaires déjà tentés/révélés, jamais la correction d'un transfert encore inconnu. Conversion du temps local en UTC explicite. Aucun compte calendrier/Anki ni synchronisation implicite. | Compte vierge : bouton désactivé et API409 ; exposition explicite d'un primaire puis vrai TSV ; rapport/CSV ; trois événements UTC valides dans ICS. |
| Langues des cours | Choix de versions réellement publiées selon le catalogue ; contenu et `Content-Language` cohérents ; lecture des titres Written course/Lesson et des plans de module EN. Pas de substitution FR silencieuse à une version EN absente. Erreur exploitable, reprise et completion bloquées sans contenu. | Fixture originale EN8 leçons, passage FR réel, EN manquant →404 visible, zéro faux module et completion désactivée, récupération FR. API relancée après ajout du gate index/hash. |
| RFQ | Entête, type, strike, quantité, prix et payoff du même contrat serveur. Valeur propre de l'autocall, PV en devise, moteur exécuté, observations, seed et incertitude ; les autres contrats vanilla restent des illustrations distinctes. Limites non évaluées explicites. | BTC put : K21000, quantité3, prix3278.027771... ; autocall3Y : 99.596727...% du pair, PV995967.2753...EUR, intervalle MC, aucune pastille BEST contradictoire. |
| Paper trade | Action séparée de la simple demande de prix ; aucune exécution de courtier. Même query et clé de requête conservées tant que l'accusé de réception manque. Livre privé affichant `paper_positions`. Limite de persistance au redémarrage explicitée. | Le serveur enregistre réellement le trade, puis le test remplace son accusé par503 ; Retry emploie la même clé et ne crée qu'une position. |
| Payoff mobile | Après Analyze et au focus clavier, le champ Dividend est intégralement hors de la navbar collante. | À390px : navbar bas78, input haut151.14/bas183.64 après analyse ; focus haut176.14. Géométrie naturelle mesurée, sans ignorer Axe. |
| Mathématiques au clavier | Les blocs KaTeX réellement débordants sont focusables et scrollables. ResizeObserver et fin de chargement des fontes recalculent le besoin ; les expressions qui tiennent n'ajoutent aucun arrêt de Tab. | QA synthétique : trois contextes de rendu, flèche droite, resize et Axe. Business indépendant : trois équations réelles Stochastic EN320, défilements40/40/21px, Axe zéro, resize390 sans débordement ni erreur JS. |

Navbar, logo original et Courbe signature approuvés préservés. Le dashboard conserve les catégories distinctes introduites par le parent. Aucun outil, route, générateur, éditeur ou carnet existant supprimé. Le lecteur de cours accepte également les leçons écrites sans plan séparé, et les champs `Objective:`/`Deliverable:` sans puce du générateur anglais.

## Vérification

- `npm run smoke:product-cycle2` : **14 références PASS**. Le code est réellement exécuté en Python, pas simplement compilé ni comparé à un stub.
- `npm run smoke:product-cycle2:browser` : **30 contrôles PASS**, quatre identités signées, API locale fraîche, réponses métier réelles. L'identité Supabase est un transport QA déclaré. Les prix et écritures sont fournis par la vraie API. L'unique erreur HTTP observée dans le transport normal est le404 EN attendu.
- Axe4.14.0 : **6 états ciblés, zéro violation détectée** : tentative écrite/revue, source canonique et calcul réel, Payoff390 après Analyze, RFQ autocall, feedback timeout Survival390, partie Survival terminée390. Aucune certification WCAG globale déduite.
- `npm run build`, `typecheck`, `smoke:product-contract`, `smoke:auth-freshness`, `smoke:visual-shell`, `smoke:bundle`, `smoke:product-hardening` : PASS. Le plus gros chunk de production reste Markdown437077 octets, sous500000. Le JSON des références ne charge pas dans l'accueil.
- `npm run smoke:ux:browser` : **12 étapes PASS** sur build de production, dont identité visuelle et Courbe signature à320–1440px ; aucun asset cassé ou erreur JavaScript observé.
- `npm audit --omit=dev` : **zéro vulnérabilité signalée** dans le périmètre runtime.
- Suite `audit:technical` : lint, types, calculs/cross-runtime/Workers, RUM, navigation, configuration de production, audit Business statique, matrice des cinq profils et douze cours, neuf ateliers headless, parcours général, teaching scenarios et delivery **PASS**. Reprise au point d'arrêt après actualisation d'anciens gardes de tests, sans recalculer les moteurs déjà validés. `technical-audit.log`, `entitlements-browser.log`, `technical-audit-continuation.log` et `technical-audit-remainder.log` conservent cette traçabilité.
- `smoke:continuity-recovery:browser` : **13 contrôles PASS**, quatre états Axe sans violation ; ancienne tentative revue reprise exactement, dashboard et run privé, refus RFQ422/horizon hors domaine puis récupération valide.
- `TPL_CYCLE2_SECTION=math` : **5 contrôles PASS**, dont clavier, resize et Axe sur des équations QA originales. La vraie leçon Stochastic a aussi son retest Business indépendant.
- `smoke:performance` : **dernier run standard PASS**, budgets inchangés : FCP2244ms≤2500 ; LCP3516ms≤4000 ; CLS0,0167507≤0,1 ; trois interactions, médiane120ms≤300 et pire136ms≤400 ; aucune erreur JS. Le parent a supprimé l'attente de chargement du shell par un vrai hint modulepreload de faible priorité, avec fichier hashé trouvé dans le bundle. Les anciens échecs restent des diagnostics historiques, pas le verdict final. Preuve : `frontend/cycle2/performance-final-prefetch.log`.
- Dernière livraison, après ce hint : build17,79s et budget437077octets PASS (parent) ; typecheck/lint, `smoke_public_checkout --check-build` (119 fichiers publics) et entitlements PASS ; `smoke:ux:browser` **12 étapes PASS**, dont logo/Courbe signature,320–1440px, navigation/focus/mobile et zéro erreur/asset cassé. Tous ces contextes sont fermés. Les règles financières et états métier inchangés n'ont pas été recalculés sans motif.

Preuves locales : **`frontend/cycle2/full/{browser.log,evidence.json,payoff-geometry.json}` est le run global final rejoué**, avec `section:all`, 30 contrôles et 6 scans. Les sous-batches écrivent dans leur propre dossier ; `math/{browser.log,evidence.json}` contient le contrôle synthétique final. `continuity-recovery-evidence.json` et `continuity-recovery.log` contiennent les13 contrôles sur une cohorte neuve. `references.log`, `runtime-audit.json`, `ux-final.log`, `public-artifact-final.log`, `lint-final.log`, `typecheck-final.log` et les journaux audit dans le dossier parent complètent ces preuves. Build dans `frontend/cycle2-build.log`. L'ancien `frontend/cycle2/evidence.json` a été écrasé par un premier sous-batch math vide ; il n'est plus la preuve globale, n'a pas été reconstruit, et son `browser.log` initial reste historique. Les preuves brutes et captures restent locales et passent le contrôle de secrets avant toute sélection pour Git.

## Rejouer depuis un checkout propre

Terminal backend, depuis `Tools/pricinglibrary_rag_backend` :

```powershell
python scripts/serve_learner_fixture.py --port 8434 --data-dir .learner-fixtures/frontend-cycle2
```

Terminal frontend, depuis `WEBSITE/thepricinglab` :

```powershell
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173 --strictPort
```

Autre terminal frontend :

```powershell
npm run smoke:product-cycle2
npm run smoke:product-cycle2:browser
npm run smoke:continuity-recovery:browser
npm run audit:technical
```

Le smoke prépare uniquement de petits textes QA originaux dans le store marqué de cette cohorte, avec un index EN et SHA correspondant. Il refuse un répertoire non marqué ou des credentials non QA. **Ces textes ne sont ni le curriculum commercial ni une preuve de sa note98.** Le contenu anglais réel fait l'objet de sa validation Business distincte. Aucun corpus ou cours utilisateur n'est copié dans cette fixture. Les fichiers privés de credentials ne doivent jamais être imprimés, capturés ou publiés.

Pour isoler une investigation, `TPL_CYCLE2_SECTION` accepte `learning`, `exports`, `payoff`, `rfq`, `survival` ou `math`. Le défaut exécute l'ensemble principal ; un sous-batch ne vaut pas un PASS global. La fixture conserve les tentatives entre les runs et ne réinitialise aucun store personnel. Le smoke continuité crée sa propre cohorte publique vide puis arrête ce processus. Après les preuves finales, les anciennes cohortes8429/8434 ont été fermées sans effacer leurs stores ; Vite5173 et le preview utilisateur4195 sont conservés.

Fichiers fonctionnels ajoutés : `ServerSurvival.jsx`, `ExerciseAttempt.jsx`, `PracticeReference.jsx`, `InterviewPortability.jsx`, `LearningActivity.jsx`, `learningApi.js`, `DeskContract.jsx`, `practiceReferences.json`, `practiceReferenceCatalog.mjs`, `deskRequest.mjs`, `scrollVisibility.mjs`. Intégration dans les pages existantes, extension sûre de `learnerProgress.mjs`, focus KaTeX dans `CourseMarkdown.jsx`, correction des attentes devenues anciennes dans les smokes et helper headless signé protégeant les erreurs de nettoyage contre l'impression des headers. La CI frontend inclut les contrats offline hardening et les14 références originales, sans cours privé ni fournisseur externe requis.

Changements complémentaires du parent à inclure à l'inventaire final : `src/App.tsx` précharge le module StarterKit uniquement sur sa route en conservant React.lazy ; `src/main.tsx` ne prétend plus qu'une équipe est notifiée quand seul console.error est appelé ; `vite.config.ts` précharge le vrai chunk shell avec son hash généré, trouvé via moduleIds et vérifié présent. Aucun de ces changements ne redessine la navbar ou le hero. Le runtime utilisateur a été confirmé par le parent avec une vraie session CLI adminPro : bloc learning v1 présent, interview et historique conservés.

Aucun commit ou push exécuté par cet agent ; le parent consolide la version GitHub après les gates indépendants.

## Retour Business — corrections validées

La revue indépendante a trouvé une absence de reprise des exercices écrits dans le dashboard, un faux état vide après des réponses Survival, et un crash sur « Euro Stoxx 50 and Nikkei225,3years ». Ce dernier venait du parseur local qui assimilait «50 and» à50ans, puis laissait le domaine du modèle lever pendant le rendu.

Corrections implémentées : projection `learning` lue dans la même réponse progress, compteurs distincts sans note de maîtrise, reprise directe `?attempt=exa_…` owner-bound y compris une ancienne tentative revue récemment, reprise du run exact ; une partie démarrée sans réponse ne devient pas une activité soumise. Le parseur exige désormais un mot d'unité complet ; horizon hors domaine et refus API gardent la requête éditable, avec leur raison et aucun ancien contrat/alternative. Le texte du leaderboard ne promet plus de publier un score Survival non classé.

Le smoke dédié public `scripts/smoke_continuity_recovery_browser.mjs` démarre sa propre cohorte vide via le launcher versionné et utilise un seul contexte headless à la fois : **13 contrôles et4 états Axe PASS**. Les retests Business ont confirmé les reprises et refus. Le résidu KaTeX trouvé ensuite est corrigé et validé sur les trois vraies équations. Un premier essai synthétique avait une fixture incorrecte : le remplacement JS avait réduit ses délimiteurs `$$` à `$`, et son bloc UIBLOCK n'utilisait pas le format attendu. La fixture a été corrigée ; son contrôle est désormais PASS. Aucun échec n'a été converti artificiellement en preuve d'exécution.
