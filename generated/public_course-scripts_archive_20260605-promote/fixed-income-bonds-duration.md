---
slug: fixed-income-bonds-duration
topic: Bond pricing, duration and rate-shock P&L
product: fixed-income bond
level: beginner
concepts: clean price, YTM, duration, convexity, DV01
source_count: 10
---

# Module pratique - Bond pricing, duration and rate-shock P&L

## Promesse du module
Apprendre Bond pricing, duration and rate-shock P&L par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: beginner
- Duree: 100 minutes
- Produit: fixed-income bond
- Concepts: clean price, YTM, duration, convexity, DV01

## Objectifs d'apprentissage
- Comprendre le probleme de marche avant la formule.
- Savoir identifier les inputs, les risques et les hypotheses.
- Produire un raisonnement utilisable en contexte professionnel.
- Transformer une source theorique en decision ou en exercice.

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

**Cas de depart.** Un bond book doit expliquer son P&L rates. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** [Page 426]
“close” prices
CML see capital market line CMSs see constant maturity swaps Coleman, T. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Coupon, clean/dirty price, accrued interest..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Construire le tableau de cash-flows. Le livrable attendu est un document court et actionnable: Cash-flow schedule.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - Prix et yield

**Cas de depart.** Le yield mid bouge et le prix doit etre estime. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Because the strategy is designed for in-
terest rate futures, we will illustrate it with reference to a bond and a bond futures contract. [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: YTM, discount factors, accrued interest..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer un prix approximatif et verifier le sens prix/yield. Le livrable attendu est un document court et actionnable: Pricing table.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Duration et DV01

**Cas de depart.** Risk demande l'impact d'un +25bp. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Modified duration, DV01..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer DV01 et shock P&L. Le livrable attendu est un document court et actionnable: Duration report.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Convexity et limites

**Cas de depart.** Un mouvement de taux large rend l'approximation fragile. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Duration has several specific definitions, but generally is used as a
measure of price sensitivity. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Convexity correction..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Comparer approximation lineaire et corrigee. Le livrable attendu est un document court et actionnable: Risk caveat.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. Cash-flow schedule: coupons, principal, accrued interest et maturite.
2. Clean price/YTM: calculer prix approximatif et verifier le sens prix-yield.
3. DV01: convertir duration et prix en EUR/bp sur notionnel impose.
4. Rate shock: appliquer +25bp puis comparer duration seule vs convexity.
5. Risk note: limites de l'approximation et controles de convention.

## Banque d'exercices rattaches
- Exercice 1: calcul court avec correction numerique.
- Exercice 2: cas de risque ou P&L avec interpretation operationnelle.
- Exercice 3: question de jugement professionnel, comme en salle de marches.

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

## Faits et angles extraits de la base
- [Page 426]
“close” prices
CML see capital market line CMSs see constant maturity swaps Coleman, T.
- Because the strategy is designed for in-
terest rate futures, we will illustrate it with reference to a bond and a bond futures contract.
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
(1 þ yB)t ,
where CPt is the cash payment made at time t and will be either the coupon interest or
principal.
- An approxima-
tion to the change in price as it relates to the change in yield is given by the formula,
ΔB  B DURB(ΔyB)
1 þ yB
,
where DURB represents the bond’s duration and Δ represents the change in B or yB.
- For-
mally, the duration is a weighted average of the time to each cash payment date and is
specified in units of time.
- This par-
ticular one, though often just called duration, is more precisely identified as Macaulay’s
duration, named after one of the first economists to derive it.

## Sources RAG a citer
- [S1] Mathematics of the Financial Markets  Financial Instruments and Derivatives Modelling, Valuation and Risk Issues ( PDFDrive ), chunk 265, score 0.52985: n, Toy (BDT) process Black and Karasinski model
Black–Scholes formula
basket options
beyond Black–Scholes
call-put parity
cap pricing
currency options
“exact” pricing
exchange options
exotic options
floor pricing
forward prices
futures/forwards options
gamma processes
hypotheses underlying
jump processes
moneyness
sensitivities example
- [S2] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 515, score 0.474756: small change in interest rates. Because the strategy is designed for in-
terest rate futures, we will illustrate it with reference to a bond and a bond futures contract. In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration. Duration has several specific definitions, but generally is used as a
measure of price sensitivity.
- [S3] Principles of Financial Engineering ( PDFDrive ), chunk 954, score 0.454944: urrency contracts, 8995
Eurocurrency deposit, comparison with onshore
deposit, 27
Eurocurrency futures, 83
comparison with forward rate agreements, 93
hedging FRAs with, 9395
Eurocurrency futures contracts, 33
Eurocurrency markets, 27
Eurodollar (ED) futures, 89, 92
Euro-equity, 28
Euromarkets, 2728
European call options, 431, 558
example, 432b
variance-vega of, 519
European currency, 6061
European Markets Inf...
- [S4] Principles of Financial Engineering ( PDFDrive ), chunk 79, score 0.429242: ...................................................................................................82
3.7.3 FRA Contractual Equation .........................................................................................
- [S5] Principles of Financial Engineering ( PDFDrive ), chunk 947, score 0.423211: ance of LIBOR rate, 441442
BlackScholes assumptions, 431, 564, 704
BlackScholes equation, 286
BlackScholes formula, 289292, 295296, 453454,
512513, 564565, 574575, 668, 710
to bond PDE, 330332
and dividends, 454
option price from, 575
BlackScholes implied volatility, 540541
BlackScholes partial differential equation, 551552,
561562
BlackScholes volatility, 710711
BM&FBovespa, 29
Bond
benchmark, 1...
- [S6] Derivatives Workbook ( PDFDrive ), chunk 13, score 0.422694: acts are priced and valued;
• calculate and interpret the no-arbitrage value of equity, interest rate, fixed-income, and cur-
rency forward and futures contracts;
• describe and compare how interest rate, currency, and equity swaps are priced and valued;
• calculate and interpret the no-arbitrage value of interest rate, currency, and equity swaps.
- [S7] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 78, score 0.394812: ge bid/ask spread of the
combination order book.
- [S8] Derivatives Markets ( PDFDrive ), chunk 525, score 0.378463: rmediated swaps 284–93; non-dealer
intermediated swaps 281–4
plain vanilla put and call options, deﬁnitions
and terminology for 327–32
portfolio price dynamics, replication of 
457
portfolio theory, hedging as 165–8
portfolio variance, calculation of 179–81
position accountability 214, 215, 228, 
229
preference-free risk-neutral valuation 598,
600
present and future spot prices 20–3
present value (PV): valuation o...
- [S9] Derivatives Markets ( PDFDrive ), chunk 509, score 0.355778: ard contracts;
valuation of forward contracts
forward prices 9, 24–5; change in, present
value of 242; no-arbitrage, forward
pricing with 102–3
front stub period 294
fundamental theorem of asset pricing
number one (FTAP1): equivalent
martingale measures (EMMs) 509,
511–12, 517, 528–9, 530, 532, 533;
model-based option pricing (MBOP)
450, 451, 452; option pricing in
continuous time 540; risk-neutral
valuation 596–7...
- [S10] Vault Guide to Advanced Finance and Quantitative Interviews.pdf ( PDFDrive ), chunk 1, score 0.339128: . . . . . .56
Regression Analysis . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .59
Sample Questions and Answers . . . . . . . . . . . . . . . . . . . . . . . . .72
Summary of Formulas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

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

