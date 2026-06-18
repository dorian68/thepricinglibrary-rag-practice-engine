---
slug: options-book-greeks-pnl
topic: Options book Greeks and P&L attribution
product: equity options book
level: intermediate
concepts: delta, gamma, vega, theta, hedging
source_count: 10
---

# Module pratique - Options book Greeks and P&L attribution

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Options book Greeks and P&L attribution par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 120 minutes
- Produit: equity options book
- Concepts: delta, gamma, vega, theta, hedging

## Prerequis
- prix d'une option vanilla
- derivees partielles
- notion de hedge

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

## Positionnement bibliotheque
- Track: Derivatives & Volatility
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire le Greek report
- Objectif pratique: Identifier les sensibilites dominantes du book.
- Situation de desk: Un book options arrive avec delta/gamma/vega/theta agrege.
- Notion utile: Delta par %, gamma par %^2, vega par vol point.
- Activite: Verifier unites et signe.
- Livrable apprenant: Risk snapshot.
### Module 2 - P&L attribution
- Objectif pratique: Calculer P&L sous scenario spot/vol/time.
- Situation de desk: Spot baisse, vol monte, un jour passe.
- Notion utile: Taylor P&L delta-gamma-vega-theta.
- Activite: Calculer chaque bloc et le total.
- Livrable apprenant: Attribution table.
### Module 3 - Hedge action
- Objectif pratique: Proposer une couverture avec residual risk visible.
- Situation de desk: Le book est short gamma et long vega.
- Notion utile: Delta hedge, convexity hedge, vega hedge.
- Activite: Choisir action et trigger.
- Livrable apprenant: Hedge memo.
### Module 4 - Communication risk
- Objectif pratique: Ecrire un message utile a trader et risk manager.
- Situation de desk: Le P&L explique doit tenir en 8 lignes.
- Notion utile: Dominant risk, residual risk, monitoring.
- Activite: Rediger la note.
- Livrable apprenant: Desk risk note.

## Cours redige
### Lecon 1 - Lire le Greek report

Lorsqu'un desk de trading reçoit un rapport sur les Greeks d'un book d'options, il est crucial de comprendre comment ces sensibilités influencent la gestion du risque et la stratégie de couverture. Imaginons une situation où le delta agrégé est de 0,6, ce qui signifie que pour chaque mouvement de 1 point dans le prix de l'actif sous-jacent, la valeur du book va varier de 0,6 points. Cette sensibilité au delta est essentielle, car elle nous indique comment le book réagit aux variations de prix, mais elle doit être interprétée en pourcentage pour évaluer son impact relatif sur le portefeuille.

Le gamma, quant à lui, représente la sensibilité du delta par rapport aux mouvements de l'actif sous-jacent. Si le gamma est positif, cela signifie que le delta augmentera à mesure que le prix de l'actif sous-jacent augmente, ce qui peut amplifier les gains ou les pertes. Sur un desk, comprendre le gamma est fondamental pour anticiper les ajustements nécessaires dans la couverture, surtout dans des marchés volatils. Comme le soulignent Mello et Neuhaus (1998), la gestion des risques peut devenir complexe, et une couverture efficace nécessite souvent d'utiliser des options contre d'autres options, ce qui peut être une stratégie délicate à mettre en œuvre.

Il est également important de prêter attention au vega, qui mesure la sensibilité du prix de l'option par rapport à la volatilité implicite. Par exemple, si le vega est de 0,2, cela signifie que pour chaque point de pourcentage d'augmentation de la volatilité, la valeur de l'option augmentera de 0,2 points. Cette mesure est cruciale dans des marchés où la volatilité peut changer rapidement, car elle influence la stratégie de pricing et de couverture. Vérifiez toujours les unités et les signes : un vega positif indique que l'option bénéficie d'une hausse de la volatilité, tandis qu'un vega négatif pourrait indiquer le contraire.

Un piège courant pour un junior est de négliger l'importance des signes dans les Greeks. Par exemple, un delta négatif peut sembler contre-intuitif, mais cela indique que le book est short sur l'actif sous-jacent. Ignorer cette nuance peut mener à des décisions de couverture erronées, augmentant ainsi le risque du portefeuille. La précision dans l'interprétation des Greeks est donc essentielle pour une gestion efficace du book.

### Lecon 2 - P&L attribution

Dans le monde du trading d'options, comprendre l'attribution du P&L est essentiel pour évaluer la performance d'un portefeuille face aux variations du marché. Imaginons une situation où le spot d'un actif sous-jacent, disons une action, baisse de 2% tandis que la volatilité implicite augmente de 1 point. Un jour s'est écoulé, et il est crucial de décomposer l'impact de ces mouvements sur notre P&L en utilisant les Greeks : delta, gamma, vega et theta. Ces mesures nous permettent de quantifier comment les variations des prix, de la volatilité et du temps affectent la valeur de nos options.

Le mécanisme de Taylor pour l'attribution du P&L repose sur l'idée que chaque Greek contribue de manière distincte à la performance globale. Le delta, qui mesure la sensibilité du prix de l'option par rapport au mouvement du spot, va jouer un rôle prépondérant dans notre scénario de baisse. Si notre option est dans la monnaie, une baisse du spot entraînera une perte directe, tandis que le gamma, qui capture la convexité du delta, peut amplifier cette perte si le mouvement est significatif. Parallèlement, une hausse de la volatilité, mesurée par le vega, peut compenser une partie de cette perte, car les options deviennent plus précieuses dans un environnement volatil. Enfin, le theta, représentant la décote temporelle, viendra réduire la valeur de l'option au fil du temps.

Sur un desk de trading, comprendre ces dynamiques est crucial. Les traders doivent être capables d'anticiper comment les mouvements du marché influenceront leur portefeuille et d'ajuster leurs stratégies en conséquence. En utilisant les Greeks pour décomposer le P&L, ils peuvent identifier les sources de gains ou de pertes et prendre des décisions éclairées sur la gestion des risques. Comme l'indique Figlewski (1998), l'information contenue dans la volatilité implicite est essentielle pour la prise de décision sur les marchés, car elle reflète les attentes du marché concernant les mouvements futurs des prix [S4].

Un piège courant pour un junior est de négliger l'importance du gamma dans un scénario de forte volatilité. En se concentrant uniquement sur le delta et en supposant que la perte due à la baisse du spot sera linéaire, il peut sous-estimer l'impact de la convexité sur le P&L. Cela peut conduire à une évaluation erronée de la performance du portefeuille, surtout dans des marchés volatils où les mouvements peuvent être plus extrêmes que prévu.

### Lecon 3 - Hedge action

Dans un environnement de marché où le book est short gamma et long vega, il est crucial de comprendre comment la couverture peut être mise en place pour gérer le risque résiduel. Imaginons un scénario où nous avons des options short gamma, ce qui signifie que notre position perd de la valeur lorsque la volatilité augmente ou que le sous-jacent se déplace rapidement. Dans ce contexte, il devient essentiel d'implémenter une stratégie de couverture qui non seulement compense les mouvements de prix, mais qui prend également en compte la convexité et la sensibilité à la volatilité.

Le delta hedge est la première étape de cette couverture. En ajustant notre position dans le sous-jacent pour neutraliser le delta de notre book, nous réduisons le risque lié aux mouvements de prix immédiats. Cependant, cette approche ne suffit pas lorsque le book est short gamma, car les mouvements rapides du marché peuvent entraîner des pertes importantes. C'est là qu'intervient le convexity hedge. En ajoutant des options supplémentaires, nous pouvons augmenter notre gamma, ce qui nous protège contre les mouvements extrêmes du marché. Cela nous aide à capter la convexité, rendant notre position moins sensible aux variations rapides des prix.

Enfin, avec une position long vega, il est essentiel de gérer le risque de volatilité. Un vega hedge consiste à ajuster notre exposition à la volatilité en utilisant des options dont le vega est opposé à celui de notre book. Cela permet de stabiliser notre P&L face aux fluctuations de la volatilité implicite. En intégrant ces trois types de couverture, nous pouvons créer une stratégie robuste qui minimise le risque résiduel visible.

Un piège courant pour un junior est de se concentrer uniquement sur le delta hedge sans considérer l'impact de la convexité et de la volatilité. Ils pourraient croire qu'une simple neutralisation du delta suffit à protéger le book, alors qu'en réalité, le short gamma peut entraîner des pertes significatives si le marché devient volatile. Comme le souligne l'extrait, la gestion des options à court terme et leur sensibilité au temps, comme le theta, est essentielle pour éviter des erreurs coûteuses dans la couverture [S7].

### Lecon 4 - Communication risk

Dans un environnement de marché dynamique, la gestion des risques de communication est essentielle pour les traders et les risk managers. Prenons l'exemple d'un desk qui gère des options. Lorsqu'un trader prend une position, il doit non seulement évaluer le risque dominant, c'est-à-dire le risque principal associé à sa position, mais aussi le risque résiduel, qui est le risque restant après les couvertures mises en place. Par exemple, un trader qui utilise des options pour couvrir une position peut se retrouver avec un risque résiduel si la couverture n'est pas parfaite, notamment en raison de la difficulté à trouver des options avec le même strike et la même maturité, comme le soulignent Mello et Neuhaus (1998) [S1].

Le mécanisme de la communication des risques repose sur la transparence des positions et des couvertures. Un trader doit être capable de justifier ses choix de couverture et d'expliquer comment ils atténuent le risque dominant tout en reconnaissant le risque résiduel. Cela est crucial pour la prise de décision au sein du desk. Par exemple, si un trader a couvert une option avec une autre option, il doit communiquer clairement les limites de cette couverture, surtout si les conditions de marché changent rapidement. La capacité à surveiller ces risques et à ajuster les stratégies en conséquence est ce qui distingue un trader expérimenté d'un junior.

Un piège courant pour un junior est de croire que la couverture élimine complètement le risque. En réalité, même avec des stratégies de couverture, un risque résiduel persiste. Ce malentendu peut mener à une surestimation de la sécurité d'une position et à des décisions imprudentes. Il est donc crucial de toujours garder à l'esprit que la gestion des risques est un processus continu, nécessitant une vigilance constante et une communication claire au sein de l'équipe.

## Labs pratiques a inclure
1. Mini-diagnostic: identifier produit, payoff ou risque economique.
2. Calcul de desk: appliquer une formule ou approximation sur donnees numeriques.
3. Sensibilites: expliquer ce qui bouge si spot/taux/vol/spread change.
4. Decision: hedge, quote, no-trade, monitoring ou escalation risk.
5. Debrief: erreurs courantes et limites du modele.

## Script enseignant
1. Ouvrir par un cas concret.
2. Demander aux apprenants de formuler l'intuition.
3. Introduire la notation minimale.
4. Faire resoudre une micro-tache.
5. Debrief: erreurs courantes, limites, interpretation marche.

## Supports a produire
- Fiche apprenant d'une page.
- Slides courtes orientees cas.
- Notebook ou tableur de calcul si le sujet s'y prete.
- Corrige detaille.
- Quiz de verification rapide.

## Exemple numerique resolu
_[genere - calcul verifie]_ On attribue le P&L intraday d'un book d'options par facteur de risque.

**Donnees.** Book delta +250k EUR par 1%, gamma -80k EUR par 1%^2, vega +120k EUR par vol point, theta -15k EUR par jour. Scenario spot -2%, vol +3.

### P&L delta-gamma-vega-theta
- Famille: options_book_greeks
- Hypotheses controlees:
  - Les greeks sont deja exprimes en EUR par unite de risque operationnelle.
  - Delta: EUR par 1% de mouvement spot.
  - Gamma: EUR par (1%)^2 de mouvement spot.
  - Vega: EUR par point de volatilite.
  - Theta: EUR par jour.
- Calculs a respecter:
  - P&L delta:
    - Formule: Delta * move spot en points de 1%
    - Application: 250,000 * (-2)
    - Resultat: -500,000 EUR
    - Lecture desk: Risque directionnel immediat du book.
  - P&L gamma:
    - Formule: 0.5 * Gamma * move^2
    - Application: 0.5 * -80,000 * (-2)^2
    - Resultat: -160,000 EUR
    - Lecture desk: Convexite du book; ici elle amplifie ou amortit le choc spot.
  - P&L vega:
    - Formule: Vega * move vol
    - Application: 120,000 * (3)
    - Resultat: 360,000 EUR
    - Lecture desk: Exposition a la volatilite implicite.
  - P&L theta:
    - Formule: Theta * 1 jour
    - Application: -15,000 * 1
    - Resultat: -15,000 EUR
    - Lecture desk: Carry temps journalier.
  - P&L total:
    - Formule: Delta + Gamma + Vega + Theta
    - Application: -500,000 + -160,000 + 360,000 + -15,000
    - Resultat: -315,000 EUR
    - Lecture desk: Point de depart du debrief intraday.
- Actions operationnelles attendues:
  - Identifier le facteur dominant du P&L avant toute couverture.
  - Proposer une neutralisation delta avec sous-jacent/futures.
  - Proposer une reduction vega avec options ou variance/vol instruments si disponibles.
  - Surveiller le gamma si le spot continue a bouger intraday.
- Points de vigilance:
  - Ne pas multiplier une sensibilite 'par 1%' par -0.02; utiliser -2.
  - Ce calcul est une approximation locale, pas une revalorisation complete du book.

**Lecture finale.** Chaque chiffre ci-dessus a une unite explicite et un sens economique; un apprenant doit pouvoir refaire le calcul a la main et retrouver le meme ordre de grandeur.

## Exercices corriges
### Exercice 1 - application directe
_[genere]_ Un book est long gamma. Le spot fait un aller-retour (-2% puis +2%). Le P&L gamma est-il positif ou negatif?

**Correction.** Positif. Long gamma => convexite favorable: la position gagne sur les mouvements realises dans les deux sens (re-hedge bas, re-hedge haut). C'est l'inverse pour un short gamma.

### Exercice 2 - niveau desk
_[genere]_ Book delta +250k/1%, gamma -80k/1%^2, vega +120k/pt, theta -15k/jour. Scenario spot -2%, vol +3pts, 1 jour. Estimez le P&L total et le risque dominant.

**Correction detaillee (calcul verifie).**
### P&L delta-gamma-vega-theta
- Famille: options_book_greeks
- Hypotheses controlees:
  - Les greeks sont deja exprimes en EUR par unite de risque operationnelle.
  - Delta: EUR par 1% de mouvement spot.
  - Gamma: EUR par (1%)^2 de mouvement spot.
  - Vega: EUR par point de volatilite.
  - Theta: EUR par jour.
- Calculs a respecter:
  - P&L delta:
    - Formule: Delta * move spot en points de 1%
    - Application: 250,000 * (-2)
    - Resultat: -500,000 EUR
    - Lecture desk: Risque directionnel immediat du book.
  - P&L gamma:
    - Formule: 0.5 * Gamma * move^2
    - Application: 0.5 * -80,000 * (-2)^2
    - Resultat: -160,000 EUR
    - Lecture desk: Convexite du book; ici elle amplifie ou amortit le choc spot.
  - P&L vega:
    - Formule: Vega * move vol
    - Application: 120,000 * (3)
    - Resultat: 360,000 EUR
    - Lecture desk: Exposition a la volatilite implicite.
  - P&L theta:
    - Formule: Theta * 1 jour
    - Application: -15,000 * 1
    - Resultat: -15,000 EUR
    - Lecture desk: Carry temps journalier.
  - P&L total:
    - Formule: Delta + Gamma + Vega + Theta
    - Application: -500,000 + -160,000 + 360,000 + -15,000
    - Resultat: -315,000 EUR
    - Lecture desk: Point de depart du debrief intraday.
- Actions operationnelles attendues:
  - Identifier le facteur dominant du P&L avant toute couverture.
  - Proposer une neutralisation delta avec sous-jacent/futures.
  - Proposer une reduction vega avec options ou variance/vol instruments si disponibles.
  - Surveiller le gamma si le spot continue a bouger intraday.
- Points de vigilance:
  - Ne pas multiplier une sensibilite 'par 1%' par -0.02; utiliser -2.
  - Ce calcul est une approximation locale, pas une revalorisation complete du book.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Etre long gamma signifie:**
- A) perdre sur les grands mouvements
- B) gagner sur la volatilite realisee
- C) etre insensible au spot
- D) etre short vega
  - Reponse: **B**. Long gamma = convexite favorable: on profite des mouvements realises dans les deux sens.

**Q2. Le theta d'une position long options est en general:**
- A) positif
- B) negatif
- C) nul
- D) egal au delta
  - Reponse: **B**. Detenir de la valeur temps coute du theta: elle se degrade chaque jour.

**Q3. Un book short gamma et long vega est surtout vulnerable a:**
- A) une vol implicite qui monte sans bouger le spot
- B) un spot qui bouge beaucoup en realise
- C) rien
- D) une baisse des taux
  - Reponse: **B**. Short gamma fait mal quand le realise est eleve, meme si la vega aide si l'implicite monte.

**Q4. Delta-neutre veut dire:**
- A) gamma nul
- B) sensibilite de premier ordre au spot ~ 0
- C) vega nul
- D) theta nul
  - Reponse: **B**. On annule la sensibilite directionnelle de premier ordre; gamma/vega/theta restent.

**Q5. Vega s'exprime usuellement en:**
- A) EUR par 1% de spot
- B) EUR par point de vol
- C) EUR par jour
- D) EUR par bp de taux
  - Reponse: **B**. Vega = variation de valeur par point de volatilite implicite.

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 10 (exploitables: 5).
- Score pedagogique moyen: 38.7/100 (qualite structurelle: 62.4/100).
- Definitions: 1 | exemples: 1 | exercices: 0 | formules: 1 | cas pratiques: 2.
- Repartition par type: theory: 7, worked_example: 1, market_context: 1, definition: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S8].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S7].
4. Exemples - couvert par [S1].
5. Exemples resolus - couvert par [S1].
6. Exercices - couvert par [S7], [S8].
7. Corriges - couvert par [S1], [S2], [S4].
8. Cas pratiques - couvert par [S1], [S2].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, resumes.

## Faits et angles extraits de la base
- For example Mello and Neuhaus (1998)
illustrates that discrete delta hedging can cause substantial risk, further they suggest that a large
part of this risk can be hedged away by using options against options.
- They assume a quite
practical situation were a market maker often not can hedge a option with another option with
exactly the same strike and maturity.
- As a market maker you will typically not be able to buy
back exactly the same option you just sold at a profit or even at flat, at least not immediately, but
typically you will be able to hedge an option with some other options with a slightly different
strike and or maturity.
- When we have jumps in the asset price Carr and Wu (2002) shows how
hedging options with options is superior to delta hedging.
- According to Carr and Wu simulations
indicate that the inferior performance of the delta hedge in the presence of jumps cannot be
improved upon by increasing the rebalancing frequency, see also Hyungsok and Wilmott (2007).
- Bates (1991) is basing his risk-neutral valuation for a jump-diffusion model partly on the idea
that traders can hedge jump risk with other options.
- Hua and Wilmott (1995) describes a great
example of the asymmetry in delta hedging replication error for long and short options.
- If you are
delta hedging a long option position the worst case scenario for you is that there is no crash.
- This
is actually because the delta hedging works poorly for any jumps, but if you are long options you
will benefit from this hedging error when the market crash.
- Among the many papers looking into
hedging options with options are for example Choie and Novomestky (1989), Carr and Madan
(2001), Andreasen and Carr (2002) and Haug (1993).

## Sources RAG a citer
- [S1] Derivatives Models on Models ( PDFDrive ), chunk 81, score 0.52142: For example Mello and Neuhaus (1998)
illustrates that discrete delta hedging can cause substantial risk, further they suggest that a large
part of this risk can be hedged away by using options against options.
- [S2] Derivatives Models on Models ( PDFDrive ), chunk 95, score 0.449788 (extrait non cite: source bruitee)
- [S3] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 411, score 0.432138 (extrait non cite: source bruitee)
- [S4] Derivatives Models on Models ( PDFDrive ), chunk 100, score 0.387186: Figlewski (1998): ‘‘The Information Content of Implied Volatility’’ The
Review of Financial Studies, 6(3), 659–681. ■Castelli, C. (1877) The Theory of Options in Stocks and Shares. London: F.C. ■Carr, P., and J. Bowie (1994): ‘‘Static Simplicity,’’ Risk Magazine, 7(8). ■Carr, P., and A.
- [S5] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 419, score 0.375034 (extrait non cite: source bruitee)
- [S6] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 2, score 0.364293 (extrait non cite: source bruitee)
- [S7] Financial Risk Manager Handbook + Test Bank  FRM Part I   Part II ( PDFDrive ), chunk 304, score 0.355696: Theta is greater (in absolute value) for short-term ATM options, so statement
d. is incorrect.
- [S8] Problems and Solutions in Mathematical Finance  Equity Derivatives, Volume 2 ( PDFDrive ), chunk 451, score 0.354145 (extrait non cite: source bruitee)
- [S9] Derivative Pricing   a Problem Based Primer ( PDFDrive ), chunk 4, score 0.347352 (extrait non cite: source bruitee)
- [S10] Derivative Pricing  A Problem Based Primer ( PDFDrive ), chunk 4, score 0.347352 (extrait non cite: source bruitee)

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Delta-gamma-vega-theta attribution
$$
\Delta V \approx \Delta\,\Delta S+\frac{1}{2}\Gamma(\Delta S)^2+\nu\,\Delta\sigma+\Theta\,\Delta t
$$
- Usage desk: break a daily P&L move into explainable risk buckets.
### F2 - Delta hedge notional
$$
\text{Shares to trade}=-N_{\text{contracts}}\times m\times \Delta_{\text{option}}
$$
- Usage desk: translate model delta into a concrete hedge ticket.
### F3 - Residual gamma P&L
$$
\text{Gamma P\&L}\approx \frac{1}{2}\Gamma(\Delta S)^2
$$
- Usage desk: show why a delta-neutral book can still win or lose on realized moves.

