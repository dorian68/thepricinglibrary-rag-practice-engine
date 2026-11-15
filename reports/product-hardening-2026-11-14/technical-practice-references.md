# Technical RL — 14 références pratiques exécutables

14 novembre 2026. Cycle demandé après constat de cinq solutions réduites à des
commentaires et de fragments non autonomes dans les autres cas.

**Verdict technique du sous-périmètre : PASS — 39 tests, dont l’exécution réelle
des 14 scripts Python et des 14 notebooks autonomes.** Le branchement API/CLI,
le renderer et la revue Business indépendante sont effectués par root ; ils
ne sont pas déclarés validés par ces seuls tests de références.

## Livrables et contrat

* `pricinglibrary_rag/practice_references.py` : fonctions allowlistées, tickets
  fixes, calculs et génération des exports. Aucun `eval`, `exec`, code apprenant,
  provider, LLM, corpus privé, ordre ou paiement n’est utilisé pour calculer.
* `pricinglibrary_rag/learning_assets/practice_references.json` : enrichissement
  de **14 IDs existants**, solution autonome et véritable output JSON de chaque
  exécution. Le fichier source `practice_exercises.json` est inchangé.
* `tests/test_practice_references.py` : transports d’export en sous-processus
  isolés, intégrité des tickets, oracles numériques et limites des revendications.

```python
from pricinglibrary_rag.practice_references import (
    list_reference_ids, run_reference, get_reference, export_reference,
)

run_reference("iv-newton")
get_reference("mc-asian")
export_reference("autocall", format="python")
export_reference("delta-hedge", format="ipynb")
```

`run_reference(id)` retourne `{schema_version,id,ticket,result,checks,
conventions,limitations,assumptions,execution_mode}`. Le ticket est fixé par la
référence et copié : aucune entrée de code ou de paramètres utilisateur n’est
exécutée. ID absent/inconnu : `ValueError`.

`get_reference(id)` ajoute `solution`, `output`, `dependencies`,
`python_version`, `output_format` et `assessment_notice`. `output` est le JSON
réellement imprimé par le script, avec le même ticket et le même calcul. Le
catalogue a la forme `{schema_version,references:[14 entrées]}`. Root peut le
fusionner par ID sans modifier les 14 routes, compétences ou briefs existants.

`export_reference` accepte `python`/`py` et `ipynb`/`notebook`. Les fichiers
contiennent imports, fonctions, ticket, conventions, hypothèses, limites et
point d’entrée imprimant un JSON. Aucun import du package TPL ni dépendance
SciPy n’est requis. Deux références utilisent NumPy : `mc-asian` et `smile-fit`.
Les douze autres utilisent uniquement la bibliothèque standard Python.

## Résultats calculés

| ID conservé | Référence réellement calculée | Contrôle indépendant ou résultat principal |
|---|---|---|
| `realized-vol-estimators` | Cinq variances journalières sur les mêmes 11 séances des 12 OHLC d’origine ; annualisation 252/365 | Vols annuelles 15,73591361 %, 17,15027235 %, 18,39255738 %, 18,05823305 %, 17,75005135 %. Concordance avec l’implémentation canonique indépendante et contrôle du facteur √(365/252). |
| `bs-eur-call` | BSM européen, CDF `math.erf`, call, put, delta, vega et parité | Call 6,12065411346 ; dividende nul explicitement supposé, taux continu 2 %, T=0,5. |
| `options-book-greeks` | Attribution delta/gamma/vega/theta, unités en points de pourcentage | −500k −160k +360k −15k = **−315k EUR**, gamma avec facteur 1/2. |
| `swap-dv01` | Payer, annuité fournie constante | PV −910k EUR ; +45,5k EUR/bp pour hausse des taux ; choc +10bp : +455k. Hedge de sens opposé : recevoir fixe. |
| `barrier-knock-in` | **Down-and-out** conformément au brief, malgré l’ID historique conservé | 1,05→0 ; 1,00→KO→0 ; 1,20 sans contact→1m USD ; retour à 1,20 après contact antérieur→0. Cashflows, aucun prix de modèle de barrière inventé. |
| `smile-fit` | Moindres carrés IV quadratique en log(K/S), cinq quotes IV d’origine | a=0,1825176894 ; b=−0,2716712652 ; c=1,0036034001 ; résidu RMS 0,0049375744 IV. Orthogonalité des résidus aux trois colonnes de régression vérifiée. |
| `mc-asian` | GBM risque neutre, moyenne arithmétique, 12 observations mensuelles excluant t=0, 100 000 chemins indépendants | Prix **5,356683200676238**, SE **0,025638091260381794**, IC normal 95 % [5,3064325418 ; 5,4069338595]. Reconstruction indépendante des chemins et de la variance ; borne géométrique analytique. |
| `curve-boot` | Bootstrap annuel 1Y/2Y/3Y aux taux 3 %/3,2 %/3,35 % | DFs **0,9708737864 / 0,9388876345 / 0,9056826245**, vérifiés par résolution indépendante d’un système linéaire ; les trois swaps repricent à PV nul. |
| `delta-hedge` | Long 1 000 calls, multiplicateur 100, deltas fournis 0,54 puis 0,61 | Vendre 54 000 actions, nouvelle cible −61 000, rééquilibrage **−7 000** ; neutralité calculée et convention acheter+/vendre−. |
| `iv-newton` | Newton avec vega par volatilité 1,0, encadrement positif et secours bisection | **26,73112393864625 %**, prix reproduit 8,000000000000007 ; 4 évaluations, 3 mises à jour. Comparaison à une bisection indépendante. |
| `autocall` | Flux déterministes trimestriels **sans mémoire**, 2 ans, niveaux d’origine complétés et annoncés | Coupon **8 % p.a. / 4 = 2 % par trimestre**. Up : 102 à Q1 ; flat : 106 au total jusqu’à Q3 ; down : 8 observations, coupons 4 + remboursement 55 = **59 par 100 de principal**, sans actualisation. |
| `cds-cs01` | **Acheteur de protection** explicite ; annuité risquée fournie | Prime annuelle payée **−600k EUR**, CS01 **+21k EUR/bp**, élargissement +25bp **+525k EUR**. Aucun « profit » garanti en additionnant des horizons différents. |
| `parametric-var` | VaR gaussienne à un jour avec le quantile arrondi d’origine 1,645 | 658k EUR, limite pédagogique 600k dépassée ; stress −5 % : −1m EUR. La VaR n’est pas une perte maximale. |
| `bond-duration` | Approximation de duration modifiée d’une position obligataire longue | DV01 magnitude 17k EUR/bp, sensibilité signée −17k ; choc +25bp : **−425k EUR**. Aucun faux calcul de convexité sans entrée. |

## Limites et hypothèses rendues explicites

Le smile source ne fournit que cinq **IV**, sans prix, bid/ask ou timestamp.
La référence vérifie leur validité numérique puis calcule une régression
quadratique ; elle n’annonce ni nettoyage de prix impossibles, inversion IV,
validation de quotes stale/crossed, calibration SVI ni preuve d’absence
d’arbitrage. Ces capacités restent `false` dans le résultat. Le signe de skew
peut nourrir une discussion ; il ne prouve pas une demande de protection observée.

L’Asian utilise `numpy.random.default_rng(seed=7)`, une matrice de chocs
`(100000,12)` par ligne/chemin et une volatilité constante de 20 %. L’erreur
standard est le SD échantillonnal des **payoffs actualisés indépendants**, avec
ddof=1, divisé par √100000. L’intervalle couvre l’erreur d’échantillonnage du
modèle, pas l’erreur de modèle ou de données. Budget borné à 100000 chemins et
12 observations ; aucun GPU, provider ou calibrateur n’est appelé.

Les anciens paths autocall avaient seulement 2/3/3 niveaux pour un produit
de huit trimestres. Les préfixes sont conservés exactement ; les extensions
à huit niveaux sont des hypothèses **synthétiques déclarées**. Pour down,
`[.82,.68,.55]` est complété par `[.62,.74,.69,.63,.55]`. Le coupon de Q5 est 2,
sans rattrapage des coupons manqués. Après un autocall, les futurs niveaux
fournis ne sont plus utilisés. Aucun PV, processus stochastique ou probabilité
n’est ajouté à cet exercice de lecture de term sheet.

Les signes, unités, informations manquantes et périmètres des approximations
sont disponibles dans les exports, le résultat et le JSON du renderer. Les
contrôles booléens sont des vérifications numériques locales. Ils ne sont
pas une notation experte du raisonnement, une certification de maîtrise ou
une approbation de risque réelle.

## Reproduction et preuve

Depuis `Tools/pricinglibrary_rag_backend` :

```powershell
python -m pytest tests/test_practice_references.py -q --basetemp .tmp/practice-references-review
python -m pricinglibrary_rag.practice_references mc-asian
python -m pricinglibrary_rag.practice_references iv-newton --format python
python -m pricinglibrary_rag.practice_references autocall --format ipynb
python -m pricinglibrary_rag.practice_references --write-catalog
```

Résultat observé : **39 PASS en 7,52 s**, Python 3.11.9 / NumPy 2.4.6. Les 28 exports s’exécutent par
`python -I exercise.py`, depuis des répertoires temporaires sans package TPL ni
`PYTHONPATH`. Pour chaque référence, la sortie réellement parsée est comparée
au résultat service et à l’`output` affiché. Les différences de dernier bit
des routines NumPy sont comparées avec une tolérance explicite 1e-12 relative
/ 1e-10 absolue ; les contrôles de signes/unités sont exacts.

Les IDs non allowlistés, tentatives d’injection de code par ID et formats
inconnus sont rejetés. Les sorties sont copiées afin qu’un appel ne modifie
pas le ticket d’un appel ultérieur. Le JSON du catalogue est regénéré et
comparé aux résultats calculés ; le CSV OHLC, les cinq quotes smile et les
préfixes autocall d’origine sont comparés aux littéraux du starter par AST,
**sans exécuter le starter incomplet**.

Aucun fichier de book, API, learner CLI, workflow, frontend, brief source ou
générateur existant n’a été modifié pendant ce sous-cycle. Aucun commit/push.

SHA-256 du brief source conservé :
`553071094a0b86ed2d5a741cb69025bd0f6a492ffaea1f9d52c074cc7945dd03`.
