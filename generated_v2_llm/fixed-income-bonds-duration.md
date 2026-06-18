---
slug: fixed-income-bonds-duration
topic: Bond pricing, duration and rate-shock P&L
product: fixed-income bond
level: beginner
concepts: clean price, YTM, duration, convexity, DV01
source_count: 10
---

# Module pratique - Bond pricing, duration and rate-shock P&L

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Bond pricing, duration and rate-shock P&L par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: beginner
- Public vise: etudiant L3/M1, candidat en finance de marche, developpeur front-office debutant
- Duree estimee: 100 minutes
- Produit: fixed-income bond
- Concepts: clean price, YTM, duration, convexity, DV01

## Prerequis
- valeur temps de l'argent
- courbe de taux
- actualisation

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

## Positionnement bibliotheque
- Track: Rates & Fixed Income
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Cash-flow map
- Objectif pratique: Lire coupon, maturite, yield et principal.
- Situation de desk: Un bond book doit expliquer son P&L rates.
- Notion utile: Coupon, clean/dirty price, accrued interest.
- Activite: Construire le tableau de cash-flows.
- Livrable apprenant: Cash-flow schedule.
### Module 2 - Prix et yield
- Objectif pratique: Relier prix et rendement sans perdre les conventions.
- Situation de desk: Le yield mid bouge et le prix doit etre estime.
- Notion utile: YTM, discount factors, accrued interest.
- Activite: Calculer un prix approximatif et verifier le sens prix/yield.
- Livrable apprenant: Pricing table.
### Module 3 - Duration et DV01
- Objectif pratique: Convertir une position en sensibilite EUR/bp.
- Situation de desk: Risk demande l'impact d'un +25bp.
- Notion utile: Modified duration, DV01.
- Activite: Calculer DV01 et shock P&L.
- Livrable apprenant: Duration report.
### Module 4 - Convexity et limites
- Objectif pratique: Savoir quand la duration lineaire ne suffit plus.
- Situation de desk: Un mouvement de taux large rend l'approximation fragile.
- Notion utile: Convexity correction.
- Activite: Comparer approximation lineaire et corrigee.
- Livrable apprenant: Risk caveat.

## Cours redige
### Lecon 1 - Cash-flow map

Dans le monde des marchés financiers, comprendre le cash-flow d'une obligation est essentiel pour évaluer sa valeur et son impact sur le P&L d'un desk de trading. Prenons l'exemple d'une obligation qui verse un coupon semestriel. Chaque paiement de coupon représente un flux de trésorerie que l'investisseur reçoit à des moments précis, et la maturité de l'obligation indique quand le principal sera remboursé. Cette structure de cash-flows permet aux traders de prévoir les revenus futurs et d'évaluer la sensibilité du prix de l'obligation aux variations des taux d'intérêt.

Le prix d'une obligation peut être divisé en deux composantes : le prix "clean" et le prix "dirty". Le prix clean est le montant que l'on paie pour l'obligation sans tenir compte des intérêts courus, tandis que le prix dirty inclut ces intérêts accumulés depuis le dernier paiement de coupon. Cette distinction est cruciale pour les desks de trading, car elle affecte directement la valorisation des positions. En effet, lorsque l'on évalue le P&L, il est impératif de savoir si l'on considère le prix clean ou dirty, car cela peut changer la perception de la performance d'une position.

Pour illustrer cela, construisons un tableau de cash-flows pour une obligation hypothétique. Imaginons une obligation à 10 ans avec un coupon de 5 % payé semestriellement. Chaque six mois, l'investisseur recevra un paiement de coupon, et à la fin de la période, le principal sera remboursé. Ce tableau permettra aux traders de visualiser clairement les flux de trésorerie à venir, facilitant ainsi la gestion des risques et la prise de décision sur le desk.

Un piège courant pour un junior est de confondre le montant du coupon avec le prix de l'obligation. Il est facile de penser que le coupon représente la valeur totale de l'obligation, alors qu'il ne s'agit que d'une partie de la rentabilité. En réalité, le prix de l'obligation fluctue en fonction des taux d'intérêt et d'autres facteurs de marché, ce qui peut entraîner des surprises dans le P&L si l'on ne prend pas en compte ces éléments.

### Lecon 2 - Prix et yield

Dans le monde des marchés financiers, comprendre la relation entre le prix d'une obligation et son rendement est essentiel pour toute opération sur desk. Imaginons qu'une obligation se négocie à 100. Si le rendement à l'échéance (YTM) de cette obligation augmente, le prix de l'obligation doit nécessairement diminuer pour que le rendement reflète le nouveau taux de marché. Cela s'explique par le fait que le rendement est la compensation que les investisseurs exigent pour le risque de détenir l'obligation, et lorsque les taux augmentent, les obligations existantes, avec des coupons fixes, deviennent moins attractives.

Pour un trader, cette dynamique est cruciale. Lorsqu'un yield mid bouge, il est impératif d'estimer rapidement le nouveau prix de l'obligation. Cela implique d'utiliser des facteurs d'actualisation qui tiennent compte des flux de trésorerie futurs de l'obligation. Par exemple, si l'on considère que le rendement a augmenté, les flux de trésorerie futurs doivent être actualisés à un taux plus élevé, ce qui réduit leur valeur présente, et par conséquent, le prix de l'obligation. En outre, il est essentiel de ne pas oublier l'intérêt couru, qui doit être ajouté au prix de l'obligation pour obtenir le prix de règlement correct.

Un piège courant pour un junior dans ce contexte est de négliger l'impact de l'intérêt couru lors de l'évaluation du prix. Parfois, un trader peut se concentrer uniquement sur le prix théorique calculé à partir du YTM sans prendre en compte l'intérêt couru accumulé depuis le dernier paiement de coupon. Cela peut entraîner une estimation incorrecte du prix à payer ou à recevoir, affectant ainsi la rentabilité de la transaction. En gardant à l'esprit ces conventions, un trader peut naviguer plus efficacement dans le monde complexe des obligations.

### Lecon 3 - Duration et DV01

Dans le monde des marchés financiers, comprendre la sensibilité d'une position de taux d'intérêt est crucial pour gérer le risque. Prenons un exemple concret : imaginez que vous détenez une obligation qui pourrait voir son prix fluctuer en fonction des variations des taux d'intérêt. Ici, la notion de **duration** et de **DV01** (dollar value of 01) devient essentielle. La duration modifiée, en particulier, mesure la sensibilité du prix d'une obligation à un changement de 1 point de base (bp) dans les taux d'intérêt. Cela signifie qu'une obligation avec une duration modifiée de 5 ans verra son prix changer d'environ 5 % si les taux augmentent de 100 points de base.

Sur un desk de trading, le calcul du DV01 permet de quantifier ce risque de manière plus tangible. En effet, le DV01 représente la variation en dollars du prix d'une obligation pour un mouvement de 1 point de base. Cela devient particulièrement pertinent lorsque le risk manager demande l'impact d'une variation de 25 points de base. Par exemple, si votre DV01 est de 50 €, une hausse de 25 bp entraînera une perte théorique de 12,50 € sur votre position. Ce mécanisme est fondamental pour les traders, car il leur permet d'évaluer rapidement l'impact potentiel d'un changement de taux sur leur portefeuille, en respectant les règles d'arbitrage qui stipulent qu'il est préférable d'éviter le risque de prix [S5].

Cependant, un piège courant pour les juniors est de confondre la duration modifiée avec la duration classique. La première ajuste la sensibilité en tenant compte de la variation des taux, tandis que la seconde ne le fait pas. Cela peut mener à des estimations erronées du risque de taux, et donc à des décisions de trading mal informées. Il est donc crucial de bien saisir ces distinctions pour naviguer efficacement dans le monde complexe des obligations et des taux d'intérêt.

### Lecon 4 - Convexity et limites

Dans un environnement de marché, la gestion des obligations exige une compréhension fine des variations de prix en fonction des mouvements des taux d'intérêt. Imaginons qu'un trader observe une forte hausse des taux, ce qui pourrait initialement sembler gérable grâce à la duration. Cependant, lorsque les taux changent de manière significative, la simple approximation par la duration linéaire devient insuffisante. C'est ici qu'intervient la notion de convexité, qui permet de mieux anticiper l'impact des variations de taux sur le prix des obligations.

La convexité mesure la sensibilité du prix d'une obligation à des changements de taux d'intérêt, en tenant compte non seulement de la direction de ces changements, mais aussi de leur ampleur. En pratique, cela signifie que lorsque les taux augmentent ou diminuent de manière significative, le prix d'une obligation ne varie pas simplement selon une relation linéaire. Au lieu de cela, la convexité offre une correction qui ajuste cette approximation, rendant ainsi le modèle de tarification plus précis. Sur un desk de trading, cette précision est cruciale, car une mauvaise évaluation des risques peut mener à des pertes substantielles, surtout dans un contexte de volatilité accrue.

En utilisant l'extrait mentionné, on peut comprendre que la fixation finale des prix sur les marchés, comme celle établie par Eurex, repose sur des mécanismes de volume qui peuvent également être influencés par des mouvements de taux importants. Si un trader ne prend pas en compte la convexité, il pourrait sous-estimer le risque de perte lors de la liquidation de positions, surtout si le prix final est basé sur des trades effectués dans un environnement de taux instable [S7].

Un piège courant pour un junior est de croire que la convexité n'est pertinente que pour des mouvements de taux extrêmes. En réalité, même des variations modérées peuvent rendre la duration linéaire inexacte. Ignorer cette nuance peut entraîner des erreurs dans la gestion des positions, car la convexité doit être intégrée dans toute analyse de sensibilité, quel que soit le contexte de taux.

## Labs pratiques a inclure
1. Cash-flow schedule: coupons, principal, accrued interest et maturite.
2. Clean price/YTM: calculer prix approximatif et verifier le sens prix-yield.
3. DV01: convertir duration et prix en EUR/bp sur notionnel impose.
4. Rate shock: appliquer +25bp puis comparer duration seule vs convexity.
5. Risk note: limites de l'approximation et controles de convention.

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
- Chunks sources analyses: 10 (exploitables: 7).
- Score pedagogique moyen: 47.6/100 (qualite structurelle: 73.0/100).
- Definitions: 2 | exemples: 2 | exercices: 0 | formules: 3 | cas pratiques: 1.
- Repartition par type: theory: 4, market_context: 2, solution: 2, definition: 1, worked_example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S2], [S3].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S2], [S7], [S8].
4. Exemples - couvert par [S2], [S10].
5. Exemples resolus - couvert par [S2], [S10].
6. Exercices - couvert par [S8].
7. Corriges - couvert par [S2], [S7], [S8], [S9].
8. Cas pratiques - couvert par [S4].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, resumes.

## Faits et angles extraits de la base
- Because the strategy is designed for interest rate futures, we will illustrate it with reference to a bond and a bond futures contract.
- In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration.
- Duration has several specific definitions, but generally is used as a
measure of price sensitivity.
- The bond price, B, is the sum of the present values of each
of its cash payments—coupon interest and principal.
- These present values can be found
by discounting each cash payment at a single interest rate, which is known as the yield
or sometimes yield to maturity (yB).
- Formally, we have
B ¼
X
T
t¼1
CPt
(1 þ yB)t,
where CPt is the cash payment made at time t and will be either the coupon interest or
principal.
- If the yield changes, we know that the price changes inversely.
- An approximation to the change in price as it relates to the change in yield is given by the formula,
ΔB  B DURB(ΔyB)
1 þ yB,
where DURB represents the bond’s duration and Δ represents the change in B or yB.
- Formally, the duration is a weighted average of the time to each cash payment date and is
specified in units of time.
- This particular one, though often just called duration, is more precisely identified as Macaulay’s
duration, named after one of the first economists to derive it.

## Sources RAG a citer
- [S1] Mathematics of the Financial Markets  Financial Instruments and Derivatives Modelling, Valuation and Risk Issues ( PDFDrive ), chunk 265, score 0.52985 (extrait non cite: source bruitee)
- [S2] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 515, score 0.482436: Because the strategy is designed for interest rate futures, we will illustrate it with reference to a bond and a bond futures contract. In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration.
- [S3] Principles of Financial Engineering ( PDFDrive ), chunk 954, score 0.453999 (extrait non cite: source bruitee)
- [S4] Principles of Financial Engineering ( PDFDrive ), chunk 79, score 0.432478 (extrait non cite: source bruitee)
- [S5] Derivatives Workbook ( PDFDrive ), chunk 13, score 0.43012: Summary OVERVIEW
This reading on forward commitment pricing and valuation provides a foundation for understanding how forwards, futures, and swaps are both priced and valued.
- [S6] Principles of Financial Engineering ( PDFDrive ), chunk 947, score 0.423172 (extrait non cite: source bruitee)
- [S7] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 78, score 0.405714 (extrait non cite: source bruitee)
- [S8] Derivatives Markets ( PDFDrive ), chunk 525, score 0.381375 (extrait non cite: source bruitee)
- [S9] Derivatives Markets ( PDFDrive ), chunk 509, score 0.358454 (extrait non cite: source bruitee)
- [S10] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 53, score 0.33733: Valuing Fixed Income Investments and Derivative Securities. New York Institute of Finance, 1991. Business Finance. London: Butterworth, 1995. Martellini L., D. Priaulet, and S. Fixed Income Securities. Chichester, UK: John Wiley 
& Sons, 2004. Fixed Income Analysis for the Global Financial Market.

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Bond price
$$
P=\sum_{i=1}^{n}\frac{CF_i}{(1+y)^{t_i}}
$$
- Usage desk: turn cash flows and yield into clean price controls.
### F2 - Modified duration
$$
D_{\text{mod}}=\frac{D_{\text{Mac}}}{1+y/m}
$$
- Usage desk: estimate price sensitivity to a parallel yield move.
### F3 - Duration-convexity P&L
$$
\frac{\Delta P}{P}\approx -D_{\text{mod}}\Delta y+\frac{1}{2}C(\Delta y)^2
$$
- Usage desk: explain why convexity matters for larger rate shocks.

