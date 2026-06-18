---
slug: options-book-greeks-pnl
topic: Options book Greeks and P&L attribution
product: equity options book
level: intermediate
concepts: delta, gamma, vega, theta, hedging
source_count: 10
---

# Module pratique - Options book Greeks and P&L attribution

## Promesse du module
Apprendre Options book Greeks and P&L attribution par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: intermediate
- Duree: 120 minutes
- Produit: equity options book
- Concepts: delta, gamma, vega, theta, hedging

## Objectifs d'apprentissage
- Comprendre le probleme de marche avant la formule.
- Savoir identifier les inputs, les risques et les hypotheses.
- Produire un raisonnement utilisable en contexte professionnel.
- Transformer une source theorique en decision ou en exercice.

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

**Cas de depart.** Un book options arrive avec delta/gamma/vega/theta agrege. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** cent times the beneﬁts and robustness of hedging options with
options have created a whole new area of quantitative research often known as static hedging,
semi-static hedging as well as dynamic static hedging. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Delta par %, gamma par %^2, vega par vol point..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Verifier unites et signe. Le livrable attendu est un document court et actionnable: Risk snapshot.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - P&L attribution

**Cas de depart.** Spot baisse, vol monte, un jour passe. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** For example Mello and Neuhaus (1998)
illustrates that discrete delta hedging can cause substantial risk, further they suggest that a large
part of this risk can be hedged away by using options against options. [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Taylor P&L delta-gamma-vega-theta..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer chaque bloc et le total. Le livrable attendu est un document court et actionnable: Attribution table.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Hedge action

**Cas de depart.** Le book est short gamma et long vega. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** They assume a quite
practical situation were a market maker often not can hedge a option with another option with
exactly the same strike and maturity. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Delta hedge, convexity hedge, vega hedge..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Choisir action et trigger. Le livrable attendu est un document court et actionnable: Hedge memo.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Communication risk

**Cas de depart.** Le P&L explique doit tenir en 8 lignes. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** As a market maker you will typically not be able to buy
back exactly the same option you just sold at a proﬁt or even at ﬂat, at least not immediately, but
typically you will be able to hedge an option with some other options with a slightly different
strike and or maturity. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Dominant risk, residual risk, monitoring..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Rediger la note. Le livrable attendu est un document court et actionnable: Desk risk note.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. Mini-diagnostic: identifier produit, payoff ou risque economique.
2. Calcul de desk: appliquer une formule ou approximation sur donnees numeriques.
3. Sensibilites: expliquer ce qui bouge si spot/taux/vol/spread change.
4. Decision: hedge, quote, no-trade, monitoring ou escalation risk.
5. Debrief: erreurs courantes et limites du modele.

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
- cent times the beneﬁts and robustness of hedging options with
options have created a whole new area of quantitative research often known as static hedging,
semi-static hedging as well as dynamic static hedging.
- For example Mello and Neuhaus (1998)
illustrates that discrete delta hedging can cause substantial risk, further they suggest that a large
part of this risk can be hedged away by using options against options.
- They assume a quite
practical situation were a market maker often not can hedge a option with another option with
exactly the same strike and maturity.
- As a market maker you will typically not be able to buy
back exactly the same option you just sold at a proﬁt or even at ﬂat, at least not immediately, but
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
will beneﬁt from this hedging error when the market crash.

## Sources RAG a citer
- [S1] Derivatives Models on Models ( PDFDrive ), chunk 81, score 0.50742: cent times the beneﬁts and robustness of hedging options with
options have created a whole new area of quantitative research often known as static hedging,
semi-static hedging as well as dynamic static hedging. For example Mello and Neuhaus (1998)
illustrates that discrete delta hedging can cause substantial risk, further they suggest that a large
part of this risk can be hedged away by using options against options.
- [S2] Derivatives Models on Models ( PDFDrive ), chunk 95, score 0.441891: two big
steps as we often feel when reading most modern text books on options and derivatives
(including some of my own work).
- [S3] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 411, score 0.43069: lying assets
asset-or-nothing options
asset swaps
at-the-money (ATM) options
best-of calls
best-of puts
cliquets
correlation
- [S4] Derivatives Models on Models ( PDFDrive ), chunk 100, score 0.374561: und Wien: Verlag Franz Deticke. ■Canina, L. and S. Figlewski (1998): ‘‘The Information Content of Implied Volatility’’ The
Review of Financial Studies, 6(3), 659–681. ■Castelli, C. (1877) The Theory of Options in Stocks and Shares. London: F.C. Mathieson. ■Carr, P., and J. Bowie (1994): ‘‘Static Simplicity,’’ Risk Magazine, 7(8). ■Carr, P., and A.
- [S5] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 419, score 0.3737: ts
Sklar’s theorem
smile dynamics
smooth surface calibration
snowball effect, autocallables
- [S6] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 2, score 0.359261: Contracts
45
Option Contracts
50
Summary
53
Appendix A
54
CHAPTER 3
Developing Fuel Hedging Strategies
55
The Rationale for Commodity Hedging
55
Developing a Fuel Hedging Program
57
Risk Identification and Assessment
57
Types of Risk
58
Risk Identification
59
Forecasting Prices and Conducting Simulations
59
Articulating the Firm’s Risk Appetite
60
Setting Objectives for Fuel Hedging and the Scope of Hedging
60
Ide...
- [S7] Problems and Solutions in Mathematical Finance  Equity Derivatives, Volume 2 ( PDFDrive ), chunk 451, score 0.354863: –1
average strike option payoff 441
capped options 532–3
corridor options 533–4
cross-currency options 575–86
definitions of payoff 1–4
down-and-out/in options 400, 401, 405, 407
exotic options 531, 575–86
knock-out equity accumulator 429
Merton model 430–1
path-dependent options 531
path-independent options 531
terminal payoffs 409, 533, 584, 586
up-and-out/in options 398, 399, 403, 404,
434–7
PDEs see partial di...
- [S8] Derivative Pricing   a Problem Based Primer ( PDFDrive ), chunk 4, score 0.346864: n Elasticity . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 212
6.4
Problems
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 220
7
Option Greeks and Risk Management
231
7.1
Delta-hedging
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 231
7.2
Hedging Multiple Greeks
. . . . . . . . . . . . . . . . . . . . . . . . . . . .
- [S9] Derivative Pricing  A Problem Based Primer ( PDFDrive ), chunk 4, score 0.346864: n Elasticity . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 212
6.4
Problems
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 220
7
Option Greeks and Risk Management
231
7.1
Delta-hedging
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 231
7.2
Hedging Multiple Greeks
. . . . . . . . . . . . . . . . . . . . . . . . . . . .
- [S10] Financial Risk Manager Handbook + Test Bank  FRM Part I   Part II ( PDFDrive ), chunk 304, score 0.339488: es, so statement c. is correct. Theta is greater (in absolute value) for short-term ATM options, so statement
d. is incorrect. [Page 371]
Nonlinear (Option) Risk Models
353
Example 14.11: Vega and Gamma
a. Long positions in options have positive gamma and vega. Gamma (or instability
in delta) increases near maturity; vega decreases near maturity.

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

