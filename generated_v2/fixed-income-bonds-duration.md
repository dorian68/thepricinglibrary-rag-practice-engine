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

**Intuition _[reformule]_.** Un bond book doit expliquer son P&L rates. L'objectif de cette lecon est precisement: Lire coupon, maturite, yield et principal.

**Ce que disent les sources** _[extrait]_. « Because the strategy is designed for interest rate futures, we will illustrate it with reference to a bond and a bond futures contract. In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration. Duration has several specific definitions, but generally is used as a
measure of price sensitivity. » [S2]

**Le point cle: Coupon, clean/dirty price, accrued interest.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Construire le tableau de cash-flows. Livrable attendu: Cash-flow schedule - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

### Lecon 2 - Prix et yield

**Intuition _[reformule]_.** Le yield mid bouge et le prix doit etre estime. L'objectif de cette lecon est precisement: Relier prix et rendement sans perdre les conventions.

**Ce que disent les sources** _[extrait]_. « .82
3.7.3 FRA Contractual Equation. 82
3.7.3.1 Application: FRA strips.82
3.8 Fixed Income Risk Measures: Duration, Convexity and Value-at-Risk. 83
3.8.1 DV01 and PV01. 84
3.8.1.1 Dollar duration DV01.84
3.8.1.2 PV01.85
3.8.2 Duration. 85
3.8.3 Convexity. 87
3.8.4 Immunization. 87
3.8.5 Value-at-Risk, Expected Shortfall, Basel Capital Requirements and Funding Costs. 88
3.9 Futures: Eurocurrency Contracts. » [S4]

**Le point cle: YTM, discount factors, accrued interest.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer un prix approximatif et verifier le sens prix/yield. Livrable attendu: Pricing table - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

### Lecon 3 - Duration et DV01

**Intuition _[reformule]_.** Risk demande l'impact d'un +25bp. L'objectif de cette lecon est precisement: Convertir une position en sensibilite EUR/bp.

**Ce que disent les sources** _[extrait]_. « Summary OVERVIEW
This reading on forward commitment pricing and valuation provides a foundation for understanding how forwards, futures, and swaps are both priced and valued. Key points include the following:
• The arbitrageur would rather have more money than less and abides by two fundamental 
rules: Do not use your own money, and do not take any price risk. » [S5]

**Le point cle: Modified duration, DV01.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer DV01 et shock P&L. Livrable attendu: Duration report - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

### Lecon 4 - Convexity et limites

**Intuition _[reformule]_.** Un mouvement de taux large rend l'approximation fragile. L'objectif de cette lecon est precisement: Savoir quand la duration lineaire ne suffit plus.

**Ce que disent les sources** _[extrait]_. « Final Settlement Price
The Final Settlement Price is established by Eurex on the Final Settlement Day at 12:30 CET based on the volume-weighted average price
of all trades during the final minute of trading provided that more than
10 trades occurred during this minute; otherwise the volume-weighted
average price of the last 10 trades of the day, provided that these are » [S7]

**Le point cle: Convexity correction.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Comparer approximation lineaire et corrigee. Livrable attendu: Risk caveat - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** presenter un chiffre sans unite ni ordre de grandeur de controle.

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

