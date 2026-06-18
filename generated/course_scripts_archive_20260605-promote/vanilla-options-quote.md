---
slug: vanilla-options-quote
topic: Vanilla options desk quote
product: equity vanilla option
level: beginner
concepts: Black-Scholes, put-call parity, delta, vega
source_count: 10
---

# Module pratique - Vanilla options desk quote

## Promesse du module
Apprendre Vanilla options desk quote par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: beginner
- Duree: 90 minutes
- Produit: equity vanilla option
- Concepts: Black-Scholes, put-call parity, delta, vega

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
### Module 1 - Lire le ticket vanilla
- Objectif pratique: Transformer une demande de quote en inputs propres: spot, strike, maturite, taux, dividendes et vol.
- Situation de desk: Sales demande un prix indicatif sur un call europeen avant envoi client.
- Notion utile: Moneyness, forward, discounting, convention de maturite.
- Activite: Construire le ticket et identifier les donnees manquantes.
- Livrable apprenant: Quote ticket controle.
### Module 2 - Prix Black-Scholes
- Objectif pratique: Calculer call et put avec substitutions visibles et unite de premium.
- Situation de desk: Le desk veut un prix defendable et reproductible.
- Notion utile: d1/d2, prix call/put, dividend yield.
- Activite: Calculer le prix et verifier intrinsic/time value.
- Livrable apprenant: Pricing sheet.
### Module 3 - Controle put-call parity
- Objectif pratique: Detecter une incoherence de quote avant de la transmettre.
- Situation de desk: Le put mid ne colle pas avec le call mid et le forward.
- Notion utile: C - P = forward discounté moins strike discounté.
- Activite: Mesurer le parity gap et conclure quote/hold/reject.
- Livrable apprenant: Parity control.
### Module 4 - Greeks utiles au quote
- Objectif pratique: Convertir delta et vega en risque concret pour le trader.
- Situation de desk: Le client augmente la taille et le trader demande le hedge initial.
- Notion utile: Delta hedge, vega per vol point, sign convention.
- Activite: Calculer hedge shares et sensibilite vol.
- Livrable apprenant: Risk add-on note.

## Cours redige
### Lecon 1 - Lire le ticket vanilla

**Cas de depart.** Sales demande un prix indicatif sur un call europeen avant envoi client. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** ty, call and put options with the same strike and maturity have the
same vega proﬁle. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Moneyness, forward, discounting, convention de maturite..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Construire le ticket et identifier les donnees manquantes. Le livrable attendu est un document court et actionnable: Quote ticket controle.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - Prix Black-Scholes

**Cas de depart.** Le desk veut un prix defendable et reproductible. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Intuitively,
vega increases at longer maturities because there is more time for a change in implied
volatility to impact the payoff. [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: d1/d2, prix call/put, dividend yield..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer le prix et verifier intrinsic/time value. Le livrable attendu est un document court et actionnable: Pricing sheet.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Controle put-call parity

**Cas de depart.** Le put mid ne colle pas avec le call mid et le forward. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** For a given vanilla option, peak vega (like gamma) occurs at the strike where
optionality and time value is maximized. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: C - P = forward discounté moins strike discounté..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Mesurer le parity gap et conclure quote/hold/reject. Le livrable attendu est un document court et actionnable: Parity control.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Greeks utiles au quote

**Cas de depart.** Le client augmente la taille et le trader demande le hedge initial. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Far away from the optionality the option
is either like a forward (if deep in-the-money) or like no position (if deep out-
of-the-money). [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Delta hedge, vega per vol point, sign convention..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer hedge shares et sensibilite vol. Le livrable attendu est un document court et actionnable: Risk add-on note.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. Quote ticket: spot, strike, maturite, taux, dividendes, vol et convention de taille.
2. Black-Scholes price: calculer call/put, intrinsic value et time value.
3. Parity check: mesurer le gap call-put-forward et conclure quote ou reject.
4. Greeks add-on: convertir delta et vega en hedge initial et risk comment.
5. Trader memo: prix, controles, hypotheses, action et limites.

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
- ty, call and put options with the same strike and maturity have the
same vega proﬁle.
- Intuitively,
vega increases at longer maturities because there is more time for a change in implied
volatility to impact the payoff.
- For a given vanilla option, peak vega (like gamma) occurs at the strike where
optionality and time value is maximized.
- Far away from the optionality the option
is either like a forward (if deep in-the-money) or like no position (if deep out-
of-the-money).
- In either of these cases, changing volatility has minimal impact on
option value.
- Intuitively this is because
higher volatility widens the distribution and therefore brings larger positive payoffs
into play, hence increasing the option value.
- ■Summary
When trading FX derivatives, the majority of trading P&L is generated from the
three Greek exposures introduced in this chapter: delta, gamma, and vega.
- Selling delta hedged vanilla options
results in shorter vega and gamma exposures.
- Gamma and vega both come from the optionality within the derivative contract
and both are therefore maximized at the strike for vanilla options.
- A trading position
with a long vega exposure will make money if implied volatility rises and lose money
if implied volatility falls while gamma impacts how delta moves with spot.

## Sources RAG a citer
- [S1] FX Derivatives Trader School ( PDFDrive ), chunk 58, score 0.652362: ty, call and put options with the same strike and maturity have the
same vega proﬁle. The peak vega on a vanilla option reduces over time. Intuitively,
vega increases at longer maturities because there is more time for a change in implied
volatility to impact the payoff. For a given vanilla option, peak vega (like gamma) occurs at the strike where
optionality and time value is maximized.
- [S2] FX Derivatives Trader School ( PDFDrive ), chunk 352, score 0.560029: holes delta, 276
Black-Scholes formula, 18, 66–67
Black-Scholes framework, 57–68
Black-Scholes formula, 66–67
solving Black-Scholes SDE, 62–65
stochastic differential equation,
57–62
terminal spot distributions in
calculating option values, 65–66
Black-Scholes option pricer (Excel),
91–101
generate ﬁrst-order Greeks, 98–100
plot exposures, 100–101
set up simple option pricer, 91–96
set up VBA pricing function, 96–...
- [S3] Derivatives Markets ( PDFDrive ), chunk 523, score 0.527436: acteristic 363;
short the underlying 348, 349–51;
economic characteristics 351; synthetic
equivalents on basic (naked) strategies
416–18; synthetic strategies, natural
strategies and 416
option valuation: binomial option pricing
model (BOPM) 445–8; risk-neutral
valuation 624–33; direct valuation by
risk-averse investor 626–31;
manipulations 624–6; for risk-neutral
investors 631–3
options and options scenarios 323–...
- [S4] FX Derivatives Trader School ( PDFDrive ), chunk 308, score 0.435384: rs with limited
spot market liquidity, the ability to avoid crossing two option spreads (original deal
plus unwind) plus the spot market spread may save money. American Vanilla Pricing and Greeks
Comparing American and European vanillas in the CCY1 call and higher CCY1
interest rates case demonstrates how early exercise impacts trading risk. Price
proﬁles are shown in Exhibit 27.9.
- [S5] FX Derivatives Trader School ( PDFDrive ), chunk 353, score 0.435211: 1 vs. CCY2 premium,
265–267
European digital option replication:
CCY1, 402–403
CCY2, 402
G10, 4
one-touch options variations CCY1
vs. CCY2 payout, 434–435
relative strength of, 219
self-quanto:
CCY1 call options, 510
CCY1 put options, 510–513
Currency blocks, 42 [Page 599]
INDEX
581
Currency pairs, 3, 8
ATM volatility triangles, 313–319
cross, 7.
- [S6] Derivatives Models on Models ( PDFDrive ), chunk 47, score 0.432038: where all information was reﬂected in the prices of the market, see
also Girlich (2002). Mathematical description of option valuation goes at least back more than
100 years to the now so famous Bachelier (1900) paper, that was based on his doctoral thesis
defended on March 19, 1900. Bachelier assumed a normal distribution for the asset price.
- [S7] Advanced Derivatives Pricing and Risk Management  Theory, Tools, and Hands On Programming Applications ( PDFDrive ), chunk 431, score 0.38705: .
- [S8] Advanced derivatives pricing and risk management  theory, tools and hands on programming application ( PDFDrive ), chunk 431, score 0.38705: .
- [S9] Derivatives Markets ( PDFDrive ), chunk 504, score 0.383398: Debreu (AD) securities, option pricing
and 508–14; concept check: pricing
ADu() and ADd() 514; exercise 1,
pricing B(0,1) 510; exercise 2, pricing
ADu() and ADd() 511–14; random
variables 536; random walk model of
prices 530–1; risk-averse investment 522;
risk-neutral investment 521–2, 523; risk-
neutral valuation 596–7; construction of
601–3; risk premiums in stock prices and
532–3; riskless bonds 509; Sharpe...
- [S10] FX Derivatives Trader School ( PDFDrive ), chunk 355, score 0.378663: lz smile model,
233–234
use Black-Scholes to get strike
from
delta, 235
Exchange rate, 3
Exercise:
vanilla call options, 12
vanilla put options, 13
Exotic FX derivatives, 355–356
deﬁned, 11, 355
pricing, 357–373
example of, 359–360
path dependence, 373
stopping time, 370–371
volatility smile pricing, 360–367
VVV (vega/volga/vanna) pricing,
368–372
pricing models, 375–385
interest rate models, 375
jump diffusion mo...

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Black-Scholes call with dividend yield
$$
C = S_0 e^{-qT}N(d_1)-K e^{-rT}N(d_2)
$$
- Usage desk: quote the option premium from observable inputs and document the carry assumptions.
### F2 - d1/d2 controls
$$
d_1=\frac{\ln(S_0/K)+(r-q+\frac{1}{2}\sigma^2)T}{\sigma\sqrt{T}},\qquad d_2=d_1-\sigma\sqrt{T}
$$
- Usage desk: check moneyness, time and volatility before trusting the model output.
### F3 - Put-call parity
$$
C-P=S_0e^{-qT}-Ke^{-rT}
$$
- Usage desk: detect stale quotes or inconsistent funding/dividend assumptions.

