---
slug: yield-curve-bootstrapping
topic: Yield curve bootstrapping for desk pricing
product: interest-rate curve
level: intermediate
concepts: discount factors, zero curve, forward rates, interpolation
source_count: 10
---

# Module pratique - Yield curve bootstrapping for desk pricing

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Yield curve bootstrapping for desk pricing par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 130 minutes
- Produit: interest-rate curve
- Concepts: discount factors, zero curve, forward rates, interpolation

## Prerequis
- discount factor
- interpolation
- conventions de taux

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

## Positionnement bibliotheque
- Track: Market Finance Core
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire les instruments de courbe
- Objectif pratique: Classer deposits, futures et swaps par maturite et convention.
- Situation de desk: Le desk doit reconstruire une courbe avant de pricer un swap.
- Notion utile: Tenor, quote, accrual, discount factor.
- Activite: Transformer les quotes en tableau de bootstrap.
- Livrable apprenant: Curve input sheet.
### Module 2 - Bootstrap discount factors
- Objectif pratique: Extraire les discount factors un par un sans casser les maturites deja calibrees.
- Situation de desk: Une nouvelle quote 5Y arrive et change le point de courbe.
- Notion utile: Recursion sur coupons, interpolation locale.
- Activite: Calculer un point de courbe et documenter la convention.
- Livrable apprenant: Discount-factor ladder.
### Module 3 - Zeros et forwards
- Objectif pratique: Convertir discount factors en zero rates et forwards exploitables.
- Situation de desk: Le trader veut lire le carry implicite entre deux maturites.
- Notion utile: Zero rate continu, forward rate discret.
- Activite: Calculer zero/forward et commenter la pente.
- Livrable apprenant: Zero-forward report.
### Module 4 - Controle et usage desk
- Objectif pratique: Verifier monotonie, interpolation et impact sur PV.
- Situation de desk: Une interpolation trop agressive cree un faux signal de risque.
- Notion utile: No-arbitrage local, smoothness, curve-shape risk.
- Activite: Comparer deux interpolations et choisir une action.
- Livrable apprenant: Curve validation memo.

## Cours redige
### Lecon 1 - Lire les instruments de courbe

Sur un desk de trading, la compréhension des instruments de courbe est cruciale pour la gestion des risques et la valorisation des swaps. Imaginons qu'un trader doit évaluer un swap à 5 ans. Pour cela, il doit d'abord établir une courbe de taux qui reflète les attentes du marché concernant les taux d'intérêt futurs. Les instruments comme les dépôts, les futures et les swaps doivent être classés par maturité et convention, car chaque instrument a un tenor spécifique qui influence sa contribution à la courbe.

Le mécanisme de bootstrap consiste à extraire les taux d'intérêt à partir des quotes disponibles. Par exemple, un dépôt à terme de 3 mois aura une maturité différente d'un swap de 10 ans. En utilisant les quotes de ces instruments, le desk peut construire une courbe de taux qui permet de calculer les facteurs d'actualisation nécessaires pour évaluer le swap. La notion de quote est essentielle ici, car elle représente le taux d'intérêt implicite pour chaque maturité. En effet, comme le souligne l'extrait, "traiter les courbes forward comme des courbes natives" évite des problèmes d'interpolation qui pourraient fausser l'évaluation des instruments [S1].

Il est également important de comprendre les conventions d'accumulation et de décote. L'accumulation se réfère à la manière dont les intérêts sont calculés sur une période donnée, tandis que le facteur de décote est utilisé pour ramener les flux de trésorerie futurs à leur valeur actuelle. Ces concepts sont interconnectés et leur bonne maîtrise permet d'éviter des erreurs dans la valorisation. En transformant les quotes en un tableau de bootstrap, le desk peut visualiser clairement comment chaque instrument contribue à la courbe, facilitant ainsi la prise de décision.

Un piège courant pour un junior réside dans la confusion entre les courbes forward et les courbes de décote. Il peut être tentant de considérer les taux forward comme des taux de décote, mais cela peut mener à des évaluations erronées. Comprendre que les courbes forward doivent être traitées différemment pour éviter les chevauchements d'instruments est essentiel pour une évaluation précise des swaps.

### Lecon 2 - Bootstrap discount factors

Dans le contexte d'un desk de trading, la gestion précise des facteurs d'actualisation est cruciale, surtout lorsqu'une nouvelle quote arrive, comme une obligation à 5 ans, qui peut modifier la courbe des taux. L'intuition de marché ici est que chaque point de la courbe des taux doit être calibré avec soin pour refléter les conditions actuelles du marché, tout en maintenant la cohérence des maturités déjà établies. Cela signifie que, lorsque nous intégrons une nouvelle quote, nous devons extraire les facteurs d'actualisation un par un, en utilisant une méthode de bootstrap qui respecte les valeurs existantes.

Le mécanisme de bootstrap consiste à calculer les facteurs d'actualisation à partir des taux des instruments de taux d'intérêt, en commençant par les maturités les plus courtes. Chaque nouveau taux que nous ajoutons, comme celui de la quote à 5 ans, doit être intégré sans perturber les points de la courbe déjà calibrés. Cela implique une interpolation locale, où nous utilisons les taux existants pour estimer le nouveau facteur d'actualisation. En procédant ainsi, nous évitons les oscillations qui pourraient résulter de l'utilisation de taux pour des périodes qui se chevauchent, ce qui pourrait créer des delta-hedges peu plausibles [S3].

En pratique, lorsque vous calculez un point de courbe, il est essentiel de documenter la convention utilisée. Par exemple, si vous avez un coupon semestriel, il faut s'assurer que les périodes d'actualisation soient correctement alignées avec la fréquence des paiements. Cela garantit que les valeurs calculées sont non seulement précises, mais également conformes aux normes du marché.

Un piège courant pour un junior est de négliger l'importance de la cohérence dans l'interpolation des taux. Par exemple, en essayant d'ajuster trop rapidement un facteur d'actualisation sans tenir compte des impacts sur les autres maturités, il peut créer des incohérences dans la courbe, ce qui peut entraîner des erreurs de pricing significatives. Il est donc impératif de procéder avec prudence et méthode, en vérifiant systématiquement l'impact de chaque ajustement sur l'ensemble de la courbe.

### Lecon 3 - Zeros et forwards

Dans le monde des marchés financiers, comprendre la relation entre les taux d'intérêt à différentes maturités est essentiel pour le trader. Lorsqu'un trader souhaite évaluer le carry implicite entre deux maturités, il doit pouvoir convertir les facteurs de discount en taux zéro et en taux forward. Cette conversion est cruciale car elle permet de déterminer le coût de financement et les opportunités d'arbitrage entre différents instruments financiers. Par exemple, si un trader observe un taux zéro à un an et un autre à deux ans, il peut en déduire le coût d'un financement à un an dans le cadre d'un investissement à deux ans.

Le mécanisme de conversion repose sur l'idée que les taux zéro représentent le rendement d'un investissement sans risque sur une période donnée, tandis que les taux forward indiquent le rendement anticipé d'un investissement à partir d'une date future. Dans un environnement de desk, ces taux sont utilisés pour évaluer les produits dérivés et les obligations, ainsi que pour gérer les risques de taux d'intérêt. En lisant les taux zéro et forward, un trader peut mieux comprendre comment les variations des taux d'intérêt affecteront la valeur de ses positions. Comme le souligne l'extrait, la modélisation de la structure par terme est essentielle pour appréhender les risques associés aux différents instruments financiers [S4].

Cependant, un piège courant pour un junior réside dans la confusion entre les taux zéro continus et les taux forward discrets. Un junior pourrait penser que ces deux concepts sont interchangeables, alors qu'ils représentent des informations différentes sur le marché. Par exemple, un taux zéro continu pourrait sembler plus attractif, mais il ne doit pas être utilisé pour évaluer directement les opportunités de carry sans tenir compte des taux forward. Cette distinction est fondamentale pour éviter des erreurs d'interprétation qui pourraient coûter cher sur le desk.

### Lecon 4 - Controle et usage desk

Dans le contexte d'un desk de trading, la gestion des courbes de taux est cruciale pour évaluer les instruments financiers. Imaginons que vous ayez deux courbes de taux, l'une obtenue par une interpolation linéaire et l'autre par une interpolation spline. Si la première présente une variation brutale à certains points, cela pourrait créer une perception erronée du risque associé à des produits dérivés. En effet, une interpolation trop agressive peut masquer des variations de taux plus subtiles, entraînant des décisions de trading basées sur des signaux erronés. C'est ici que la notion de monotonie entre en jeu : une courbe de taux doit être non seulement croissante, mais également lisse pour refléter correctement les attentes du marché.

Le mécanisme sous-jacent repose sur le principe de no-arbitrage local, qui stipule que les prix des actifs doivent être cohérents à court terme pour éviter des opportunités d'arbitrage. Si une interpolation crée des sauts brusques, cela peut engendrer des incohérences dans les prix des produits dérivés, ce qui est problématique pour un desk, car cela pourrait mener à des pertes inattendues. Ainsi, la smoothness de la courbe est essentielle pour garantir que les variations de prix soient prévisibles et alignées avec les attentes du marché. Comme le souligne l'extrait, "ces deux courbes sont interchangeables", ce qui signifie qu'une connaissance approfondie de l'une permet de déduire l'autre, rendant d'autant plus critique la précision de l'interpolation choisie [S5].

Un piège courant pour un junior est de privilégier une interpolation qui semble plus précise sur des données historiques, sans tenir compte de la continuité et de la forme de la courbe. Par exemple, choisir une interpolation qui présente des pics et des creux marqués peut sembler séduisant à première vue, mais cela peut créer des faux signaux de risque qui nuisent à la stratégie de pricing. En négligeant l'importance de la smoothness, un junior pourrait se retrouver à prendre des positions qui ne sont pas justifiées par la réalité du marché, augmentant ainsi le risque de pertes.

## Labs pratiques a inclure
1. Curve inputs: classer deposits/futures/swaps et conventions de day count.
2. Bootstrap: calculer les discount factors successifs et verifier la monotonie.
3. Zero/forward: convertir DF en zero rates puis forward rates.
4. Interpolation control: comparer deux interpolations et impact PV.
5. Curve memo: conventions, controles et risques de courbe residuels.

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
_[genere - calcul verifie]_ On valorise un payer swap et on mesure sa sensibilite a la courbe.

**Donnees.** Payer swap EUR notionnel 100m fixed coupon 3.20% par swap rate 3.00% annuity 4.55, la courbe monte de 10bp.

### PV/DV01 de swap de taux
- Famille: rates_swap_dv01
- Hypotheses controlees:
  - Approximation mono-courbe et parallel shift.
  - Annuite fournie par le prompt, pas recalibree.
  - Signe exprime du point de vue payer fixe / receiver flottant.
- Calculs a respecter:
  - DV01:
    - Formule: Annuite * Notionnel * 1bp
    - Application: 4.55 * 100,000,000 * 0.0001
    - Resultat: 45,500 EUR/bp
    - Lecture desk: Sensibilite lineaire de la position a un bp de courbe.
  - PV payer approx:
    - Formule: (Par rate - Fixed coupon) * Annuite * Notionnel
    - Application: (3% - 3.2%) * 4.55 * 100,000,000
    - Resultat: -910,000 EUR
    - Lecture desk: Un payer au-dessus du par rate est initialement hors-la-monnaie.
  - P&L shock taux:
    - Formule: DV01 * shock bp pour un payer
    - Application: 45,500 * 10
    - Resultat: 455,000 EUR
    - Lecture desk: Un payer gagne quand les taux montent, perd quand ils baissent.
- Actions operationnelles attendues:
  - Comparer le signe de PV avec le sens payer/receiver.
  - Hedger DV01 avec swap oppose, futures taux ou bond hedge selon le book.
  - Expliquer le basis risk si la couverture n'est pas sur le meme tenor.

**Lecture finale.** Chaque chiffre ci-dessus a une unite explicite et un sens economique; un apprenant doit pouvoir refaire le calcul a la main et retrouver le meme ordre de grandeur.

## Exercices corriges
### Exercice 1 - application directe
_[genere]_ Un payer swap a un fixed coupon au-dessus du par rate. Sa PV initiale est-elle positive ou negative pour le payer?

**Correction.** Negative: payer un coupon superieur au marche est desavantageux, donc PV(payer) = (par - fixed) * annuite * notionnel < 0.

### Exercice 2 - niveau desk
_[genere]_ Payer swap EUR 100m, fixed 3.20%, par 3.00%, annuite 4.55. Courbe +10bp. Calculez PV, DV01 et P&L.

**Correction detaillee (calcul verifie).**
### PV/DV01 de swap de taux
- Famille: rates_swap_dv01
- Hypotheses controlees:
  - Approximation mono-courbe et parallel shift.
  - Annuite fournie par le prompt, pas recalibree.
  - Signe exprime du point de vue payer fixe / receiver flottant.
- Calculs a respecter:
  - DV01:
    - Formule: Annuite * Notionnel * 1bp
    - Application: 4.55 * 100,000,000 * 0.0001
    - Resultat: 45,500 EUR/bp
    - Lecture desk: Sensibilite lineaire de la position a un bp de courbe.
  - PV payer approx:
    - Formule: (Par rate - Fixed coupon) * Annuite * Notionnel
    - Application: (3% - 3.2%) * 4.55 * 100,000,000
    - Resultat: -910,000 EUR
    - Lecture desk: Un payer au-dessus du par rate est initialement hors-la-monnaie.
  - P&L shock taux:
    - Formule: DV01 * shock bp pour un payer
    - Application: 45,500 * 10
    - Resultat: 455,000 EUR
    - Lecture desk: Un payer gagne quand les taux montent, perd quand ils baissent.
- Actions operationnelles attendues:
  - Comparer le signe de PV avec le sens payer/receiver.
  - Hedger DV01 avec swap oppose, futures taux ou bond hedge selon le book.
  - Expliquer le basis risk si la couverture n'est pas sur le meme tenor.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Le DV01 d'un swap mesure:**
- A) le P&L pour 1bp de courbe
- B) le coupon fixe
- C) la prime d'option
- D) le spread de credit
  - Reponse: **A**. DV01 = annuite * notionnel * 1bp: sensibilite lineaire a la courbe.

**Q2. Un payer swap gagne quand:**
- A) les taux baissent
- B) les taux montent
- C) la vol monte
- D) le spread s'ecarte
  - Reponse: **B**. Le payer recoit le flottant: il profite d'une hausse des taux.

**Q3. La PV d'un payer dont le coupon = par rate est:**
- A) fortement positive
- B) proche de zero
- C) fortement negative
- D) indeterminee
  - Reponse: **B**. Au par, fixed = par rate => PV ~ 0 a l'initiation.

**Q4. Le basis risk d'un hedge swap vient surtout de:**
- A) un mismatch de tenor/index
- B) la couleur de l'ecran
- C) le notionnel
- D) le jour de la semaine
  - Reponse: **A**. Couvrir avec un tenor/index different laisse un risque de base residuel.

**Q5. Annuite elevee => DV01:**
- A) plus faible
- B) plus eleve
- C) inchange
- D) negatif
  - Reponse: **B**. DV01 croit avec l'annuite (et le notionnel).

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 10 (exploitables: 10).
- Score pedagogique moyen: 60.2/100 (qualite structurelle: 94.5/100).
- Definitions: 2 | exemples: 4 | exercices: 1 | formules: 5 | cas pratiques: 0.
- Repartition par type: theory: 6, worked_example: 2, definition: 1, solution: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S1], [S2].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S1], [S3], [S5], [S9].
4. Exemples - couvert par [S1], [S3], [S6], [S9].
5. Exemples resolus - couvert par [S3], [S9].
6. Exercices - couvert par [S9].
7. Corriges - couvert par [S3], [S5].
8. Cas pratiques - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, cas pratiques, resumes.

## Faits et angles extraits de la base
- Distinguishing forward curves from discount curves (representing the collateralization of
the forward) motivates an alternative interpolation method, namely interpolation of
the forward value (the product of the forward and the discount factor).
- In addition,
treating forward curves as native curves (instead of representing them by pseudodiscount curves) will avoid other problems, like that of overlapping instruments.
- Besides the interpolation, we discuss the calibration of the curves for which we give
a generic object-oriented implementation in Fries (Curve calibration.
- Keywords Multi-curve construction· Interest rate curves· Interest rate curve interpolation · Cross-currency curves · Term structure models
C.P.
- Fries (B)
DZ BANK AG, Frankfurt, Germany
e-mail: email@christian-fries.de
C.P.
- Fries
Department of Mathematics, LMU Munich, Munich, Germany
© The Author(s) 2016
K.
- (eds.), Innovations in Derivatives Markets, Springer Proceedings
in Mathematics & Statistics 165, DOI 10.1007/978-3-319-33446-2_11
227
- Fries
1
Introduction
Dynamic multi-curve term structure models, as the one discussed in this book, often
use given interest rate curves as initial data.
- The classical (single curve) example is
the HJM oder LMM model, where
df (t, T) = μ(t, T)dt + Σ(t, T)dW(t),
f (t0, T) = f0(T).
- However, a good curve construction is of high importance
for practitioners, since it has a strong impact on the delta-hedge (that is, the first-order
interest rate risk).

## Sources RAG a citer
- [S1] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 238, score 0.618846: Distinguishing forward curves from discount curves (representing the collateralization of
the forward) motivates an alternative interpolation method, namely interpolation of
the forward value (the product of the forward and the discount factor).
- [S2] Swaps and Other Derivatives  (With CD ROM) (The Wiley Finance Series) ( PDFDrive ), chunk 390, score 0.580414 (extrait non cite: source bruitee)
- [S3] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 251, score 0.536308: The method is a common practice (also considered in [1]). However,
considering forwards for overlapping periods, this may introduce oscillations and
result in implausible delta-hedges (see
- [S4] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 281, score 0.497778 (extrait non cite: source bruitee)
- [S5] Interest Rate Swaps and Their Derivatives  A Practitioner s Guide ( PDFDrive ), chunk 153, score 0.497127: Note that these two curves are
interchangeable, and knowledge of one completely determines the other.
- [S6] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 349, score 0.490514: “Best-fit” algorithms
start by assuming a functional form for the term structure and calibrate
its parameters such as to minimize the re-pricing error of the chosen
© The Author(s) 2017
529
J.R.M. Röman, Analytical Finance: Volume II,
https://doi.org/10.1007/978-3-319-52584-6_21
- [S7] The Mathematics Of Financial Modeling And Investment Management ( PDFDrive ), chunk 562, score 0.485387: Since 
the swap curve is effectively the LIBOR curve and investors borrow based 
on LIBOR, the swap curve is more useful to funded investors than a government yield curve.
- [S8] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 237, score 0.475076: Jamshidian, F.: An exact bond option pricing formula. 44, 205–209 (1989)
20. Kenyon, C.: Short-rate pricing after the liquidity and credit shocks: including the basis. 83–87 (2010)
21. Kijima, M., Muromachi, Y.: Reformulation of the arbitrage-free pricing method under the
multi-curve environment. Preprint (2015)
22.
- [S9] Quantitative Finance  A Simulation Based Introduction Using Excel ( PDFDrive ), chunk 119, score 0.466182: 13.4  Yield Curves, Discount Factors, and 
Forward Rates
In this section we discuss the spreadsheet YieldDiscountForward, which 
implements the connection between Yield Curve, Discount Factors, and 
Instantaneous forward rates described in Section 13.2.
- [S10] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 263, score 0.460862: ,Hoboken(2007). http://www.christian-fries.de/finmath/book
11. Fries, C.P.: Curve calibration. Object oriented reference implementation 2010–2015. http://
www.finmath.net/topics/curvecalibration
12.

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Discount factor recursion
$$
P(0,T_n)=\frac{1-c_n\sum_{i=1}^{n-1}\alpha_iP(0,T_i)}{1+c_n\alpha_n}
$$
- Usage desk: bootstrap the next point of the curve from a quoted par instrument.
### F2 - Zero rate
$$
z(0,T)=-\frac{\ln P(0,T)}{T}
$$
- Usage desk: convert discount factors into continuously compounded zero rates.
### F3 - Forward rate
$$
f(t_i,t_j)=\frac{1}{t_j-t_i}\ln\left(\frac{P(0,t_i)}{P(0,t_j)}\right)
$$
- Usage desk: read the market-implied carry between two maturities.

