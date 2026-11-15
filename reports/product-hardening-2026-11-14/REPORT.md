# ThePricingLibrary — corrections produit et livraison locale

Campagne démarrée le 14 novembre, validée le 15 novembre 2026.
Travail uniquement en CLI, API et navigateur headless, sans contrôle du bureau.

Le produit dispose maintenant d'un parcours concret pour un étudiant en master
finance anglophone : lire un cours réellement anglais, essayer un ticket,
conserver sa réponse, comparer un calcul reproductible, revoir son raisonnement
et reprendre son travail. La préparation d'entretien reste la priorité ; les
fonctions avancées existantes sont conservées avec leurs limites déclarées.

**Technical RL : PASS local. Business Client Mystère : PASS local,
91,25/100 de jugement expert sur les parcours testés.** Cette note n'est pas une
mesure de satisfaction ou de résultats d'étudiants réels.

## Ce qui a changé

| Besoin | Résultat livré |
| --- | --- |
| Pouvoir utiliser le produit depuis un terminal | Client authentifié `tpl`, 96 commandes, droits serveur, erreurs structurées et exports réels. Connexion/récupération/refresh avec le protocole du fournisseur et développement local explicite. |
| Faire confiance aux résultats | Outils supportés branchés aux vrais moteurs ; capacités indisponibles déclarées ; Black-76, autocall Monte Carlo et positions papier cohérents avec le contrat affiché. |
| Pouvoir travailler puis revenir | Tentatives écrites privées, auto-revue, reprise exacte par identifiant, dashboard alimenté par Interview, exercices et réponses Survival sans inventer de maîtrise. |
| Servir un étudiant anglophone | Douze programmes anglais, 108 leçons, exemples et quiz relus ; publication seulement des hashes acceptés. Les douze originaux français sont conservés. |
| Reproduire une correction | Quatorze références avec ticket, hypothèses, résultats, contrôles et vrais fichiers Python/Jupyter exécutables. Deux notebooks pédagogiques fonctionnent aussi dans un Worker navigateur. |
| S'intégrer aux habitudes d'étude | Rapport lisible, CSV pour tableur, Python/Jupyter, cartes Anki limitées aux cas exposés et planning iCalendar. Les téléchargements restent distincts de l'assiduité. |
| Utiliser Survival de façon cohérente | Timer/score/vies calculés sur le serveur, reprise du même run, feedback conservé, vingt questions et mode non surveillé/non classé. |
| Garder le design choisi | Logo horizontal, navbar et Courbe signature préservés ; corrections de formulaires, contrastes, titres et navigation au clavier. |

## Recette et portée

La validation technique détaillée se trouve dans `technical-integrated.md` et
la couverture par famille dans `CLI_FEATURE_COVERAGE.md`. La recette indépendante
est `business-integrated-review.md` ; elle ne reprend pas les notes antérieures
du seul pilote Interview ou du contenu.

- Suite backend complète : **593 tests PASS** avant le dernier correctif de
  projection ; **75 tests ciblés PASS après** cette modification additive.
  Ces nombres se recoupent et ne doivent pas être additionnés.
- Production check local et paquet installé hors checkout : **PASS**. Le wheel
  final exécute le client, l'API, les ressources, une référence et la calibration
  Node ; il ne contient aucun cours privé.
- Cours : douze variantes réelles servies par une nouvelle API et de vrais
  processus CLI sous compte non administrateur ; gate strict 98 et approbation
  indépendante de chaque hash.
- Frontend : trente contrôles intégrés, puis treize contrôles ciblés de reprise
  et refus RFQ ; six puis quatre états Axe sans violation détectée. Les
  régressions de calculateurs, permissions, hero et livrables sont conservées.
- Dernier test mobile contraint : **PASS**, FCP 2,24s, LCP 3,52s, CLS 0,01675,
  interactions médiane/pire 120/136ms, budgets inchangés. Le shell est découvert
  plus tôt ; aucune fonction ou composante visuelle n'est supprimée. Les premiers
  essais FAIL restent conservés. Les vraies équations débordantes sont maintenant
  défilables au clavier, avec focus/ArrowRight et Axe0 vérifiés indépendamment.

La revue indépendante a trouvé des défauts après les premiers tests : absence
de reprise des exercices/Survival au dashboard, mauvaise lecture de «50 and»
comme une durée, et équations longues non focusables à320px. Ils ont alimenté
un nouveau correctif et un retest indépendant ; aucune note ou attente n'a été
abaissée pour masquer ces résultats.

## Rejouer et examiner

Le produit local reste accessible à `http://127.0.0.1:5173` avec son compte
administrateur de développement. Le backend y a été rafraîchi, sans effacer
l'activité ni contrôler le navigateur. Les cohortes de QA sont séparées.

Depuis `Tools/pricinglibrary_rag_backend` :

```powershell
python -m pip install -e .
tpl coverage
tpl auth dev-session --preview-url http://127.0.0.1:5173 --role admin
tpl auth whoami
python scripts/smoke_learner_cli.py
python scripts/check_learner_package.py
```

La commande de session est une action locale explicite. Elle n'existe pas dans
le build public et ne contourne aucun droit de production. Pour une cohorte
isolée reproductible, utiliser `scripts/serve_learner_fixture.py`, puis les
smokes frontend documentés. Ne jamais publier les fichiers de session.

## Versionnement et retour en arrière

Les deux dépôts utilisent la branche `codex/2026-11-14-interview-lab`.
Le tag commun `tpl-pre-hardening-2026-11-14` conserve l'état précédent de chacun.
Les commits backend `27ce8df` et `16e00d5` sont poussés ; le second contient
la projection de progression issue de la revue indépendante. Le frontend testé
est poussé au commit `724c2b5fc440b14c75c12028812146c06457e86f`.
Le manifeste `delivery-manifest.json` identifie cette paire et le tag commun
`tpl-product-hardening-2026-11-15`, qui inclut également les contrats et rapports.

Code, tests, contrats et synthèse sont versionnés. Corpus, cours privés, bases,
credentials et captures restent hors Git. Les artefacts de cours acceptés sont
conservés localement avec leurs hashes et leur procédure de génération/promotion.
Un checkout public ne fournit pas le corpus ou ses droits de redistribution.

L'audit npm final de cette branche donne zéro vulnérabilité runtime et onze
avis modérés de développement, aucun élevé ou critique. Au push, GitHub signale
séparément 98 alertes sur la **branche par défaut** (31 élevées, 56 modérées,
11 faibles). La livraison est poussée sur la branche de travail ; elle n'a pas
été fusionnée dans la branche par défaut ni déployée sur le domaine public.

## Ce qui conditionne encore la vente réelle

Le checkout public reste fermé. Les éléments restants demandent une preuve sur
les vrais services : configuration légale/support d'Optiquant IA, droits
commerciaux des sources, identité et emails Supabase, prix/webhooks/paiement
Stripe, déploiement supervisé et rollback. Aucun email de support d'un autre
produit n'a été repris et aucun renseignement manquant inventé.

Le carnet papier garde une limite importante : mémoire du processus, maturité
constante et scénarios simulés, sans exécution broker. Les modèles annoncés
ne prétendent pas à une calibration live ou une approbation de limites de risque.
La couverture de tests et les scans Axe ne sont pas une certification WCAG ou
de toutes les combinaisons d'entrées.

La prochaine preuve commerciale est un pilote réel avec des étudiants cibles :
mesurer la première tentative, le retour à une variante, la reprise après
quelques jours et les raisons de payer ou d'arrêter. Les métriques du compte
permettent cette observation ; les exercices QA et scores d'agents ne prouvent
ni l'adoption ni la demande du marché. Aucun prospect n'a été contacté dans
cette implémentation.

Le contrôle automatique a refusé le nettoyage d'un ancien dossier temporaire
(« blocked by policy »). Ce dossier reste local, ignoré par Git, sans incidence
sur l'application ou les sauvegardes publiées.
