---
slug: stochastic-calculus-for-hedging
topic: Stochastic calculus only where it helps hedging
product: option pricing model
level: expert
concepts: Ito lemma, SDE, risk-neutral measure, hedging
source_count: 10
---

# Module pratique - Stochastic calculus only where it helps hedging

## Promesse du module
Apprendre Stochastic calculus only where it helps hedging par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: expert
- Duree: 150 minutes
- Produit: option pricing model
- Concepts: Ito lemma, SDE, risk-neutral measure, hedging

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
### Module 1 - SDE utile au hedge
- Objectif pratique: Relier dynamique du sous-jacent et risque de couverture.
- Situation de desk: Un trader demande pourquoi delta hedge suppose un modele continu.
- Notion utile: dS, drift, volatility, Brownian shock.
- Activite: Lire une SDE et nommer chaque terme en langage desk.
- Livrable apprenant: SDE risk translation.
### Module 2 - Ito lemma pour P&L
- Objectif pratique: Faire apparaitre delta, gamma et theta depuis une fonction de prix.
- Situation de desk: Le P&L explique montre un terme de convexite non intuitif.
- Notion utile: Ito expansion, quadratic variation.
- Activite: Deriver les blocs de P&L utiles a la couverture.
- Livrable apprenant: Delta-gamma-theta map.
### Module 3 - Mesure risque-neutre
- Objectif pratique: Comprendre pourquoi le drift historique n'est pas l'input de pricing.
- Situation de desk: Le learner confond forecast spot et prix d'option.
- Notion utile: Risk-neutral drift, discounting, martingale pricing.
- Activite: Comparer intuition P et calcul Q.
- Livrable apprenant: Pricing measure note.
### Module 4 - Limites du hedge continu
- Objectif pratique: Transformer la theorie en controles operationnels.
- Situation de desk: Le hedge discret subit gaps, frais et liquidite.
- Notion utile: Discrete hedging error, transaction costs, model risk.
- Activite: Lister triggers de monitoring et residual risk.
- Livrable apprenant: Hedging caveat memo.

## Cours redige
### Lecon 1 - SDE utile au hedge

**Cas de depart.** Un trader demande pourquoi delta hedge suppose un modele continu. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** currency futures positions 220; currency
futures 213–17; contract speciﬁcations
213–15; pricing vs. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: dS, drift, volatility, Brownian shock..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Lire une SDE et nommer chaque terme en langage desk. Le livrable attendu est un document court et actionnable: SDE risk translation.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - Ito lemma pour P&L

**Cas de depart.** Le P&L explique montre un terme de convexite non intuitif. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** two big
steps as we often feel when reading most modern text books on options and derivatives
(including some of my own work). [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Ito expansion, quadratic variation..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Deriver les blocs de P&L utiles a la couverture. Le livrable attendu est un document court et actionnable: Delta-gamma-theta map.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Mesure risque-neutre

**Cas de depart.** Le learner confond forecast spot et prix d'option. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** •
Dynamic delta hedging removes a lot of risk compared to not hedging or to static delta
hedging, but there is plenty of risk left, and far too much to argue for risk-neutral
valuation in practice. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Risk-neutral drift, discounting, martingale pricing..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Comparer intuition P et calcul Q. Le livrable attendu est un document court et actionnable: Pricing measure note.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Limites du hedge continu

**Cas de depart.** Le hedge discret subit gaps, frais et liquidite. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** The idea of continuous dynamic delta hedging to get risk-neutrality
is simply not a robust idea. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Discrete hedging error, transaction costs, model risk..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Lister triggers de monitoring et residual risk. Le livrable attendu est un document court et actionnable: Hedging caveat memo.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. SDE translation: relier drift, vol et choc Brownien au hedge desk.
2. Ito P&L: faire apparaitre delta, gamma et theta depuis dV.
3. Pricing measure: expliquer pourquoi le drift risque-neutre est utilise.
4. Discrete hedge: quantifier les limites gaps/frais/liquidite.
5. Hedging memo: controles operationnels et residual risk.

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
- currency futures positions 220; currency
futures 213–17; contract speciﬁcations
213–15; pricing vs.
- two big
steps as we often feel when reading most modern text books on options and derivatives
(including some of my own work).
- •
Dynamic delta hedging removes a lot of risk compared to not hedging or to static delta
hedging, but there is plenty of risk left, and far too much to argue for risk-neutral
valuation in practice.
- The idea of continuous dynamic delta hedging to get risk-neutrality
is simply not a robust idea.
- We have unsystematic jumps that seem to matter for some players, and we also
have systematic jumps.
- •
Option traders do not like to rely on option models built on equilibrium models alone, and
in particular not on the CAPM and the Gaussian.
- Further,
jump risk is often systematic; in particular the largest jumps that basically can only be
hedged with other options.
- •
Option traders rely mainly on hedging away unwanted risk by hedging options with
options, a concept that was more or less understood at least 100 years ago.
- •
Option traders also use delta hedging, but they construct their portfolios in such a way
that they are not vulnerable to how poorly delta hedging works in many situations, that
means using options against options at least to protect yourself for large jumps.
- The risk
in delta hedging is not symmetric for long and short option positions.

## Sources RAG a citer
- [S1] Derivatives Markets ( PDFDrive ), chunk 509, score 0.785403: ard contracts;
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
- [S2] Derivatives Markets ( PDFDrive ), chunk 505, score 0.769444: exchange-traded funds (ETFs) 191–2, 226
exercise of options 328
exercise price 328, 336
exercises for learning development:
binomial option pricing model (BOPM)
501–5; equivalent martingale measures
(EMMs) 537; ﬁnancial futures contracts
266–8; hedging with forward contracts
56–61; hedging with futures contracts
205–7; interest-rate swaps 315–16;
market organization for futures contracts
158–9; model-based option...
- [S3] Derivatives Markets ( PDFDrive ), chunk 504, score 0.699086: Debreu (AD) securities, option pricing
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
- [S4] Derivatives Models on Models ( PDFDrive ), chunk 95, score 0.613957: two big
steps as we often feel when reading most modern text books on options and derivatives
(including some of my own work).
- [S5] Derivatives Markets ( PDFDrive ), chunk 528, score 0.607086: of
hedge ratio 482; down state, replication
in 481; hedge ratio, interpretation of
482–3; replication over period 2 (under
scenario 1) 479–82; replication under
scenario 2 (over period 2) 484; scenarios
478–9; solving equations for ?
- [S6] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 496, score 0.600061: ike swaps and forwards on behalf of their clients. They offer these ser-
vices to help their clients manage their risks. These financial institutions then turn
around and hedge the risk they have assumed on behalf of their clients. How do they
1The material in this section draws heavily from C. W. Smith and R. M.
- [S7] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2295, score 0.587446: nimal martingale mea-
sure and the F¨ollmer-Schweizer decomposition, Stochas-
tic Analysis and Applications 13, 573–599. [Page 1494]
Mean–Variance Hedging
5
[53]
Schweizer, M. (1996). Approximation pricing and the
variance-optimal martingale measure, Annals of Proba-
bility 24, 206–236. [54]
Schweizer, M. (2001). From actuarial to ﬁnancial valua-
tion principles, Insurance: Mathematics and Economics
28, 31–47.
- [S8] Derivatives Markets ( PDFDrive ), chunk 356, score 0.582047: l (arbitrage-
free) option pricing model. This model is called the Binomial Option Pricing
Model (BOPM) and it is a discrete time model. The Binomial option pricing
model uses a decision tree framework but goes beyond it. In fact, the Binomial
option pricing model shows how to correctly discount option payoffs in a
discrete, decision tree context.
- [S9] Derivatives Models on Models ( PDFDrive ), chunk 94, score 0.546574: initially were many people relying too much on the Black-Scholes-
Merton way of deriving the formula. For example Leland O’Brien Rubinstein Associates and
their way of constructing synthetic options (portfolio insurance) based on dynamic delta hedging
basically failed in the crash of 1987.
- [S10] Financial Derivatives  Pricing, Applications, and Mathematics ( PDFDrive ), chunk 212, score 0.526992: gPaper,FinancialStrategiesGroup,MerrillLynch
Capital Markets, New York. Jamshidian, F. (1991a): “Bond and Option Evaluation in the Gaussian Interest
Rate Model,” Research in Finance 9: 131–170. Jamshidian, F. (1991b): “Commodity Option Evaluation in the Gaussian Fu-
tures Term Structure Model,” Review of Futures Markets 10: 324–346. Jamshidian, F.

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Ito process
$$
dS_t=\mu S_t\,dt+\sigma S_t\,dW_t
$$
- Usage desk: state the modeling assumption behind the hedge derivation.
### F2 - Ito lemma
$$
dV=\left(\frac{\partial V}{\partial t}+\mu S\frac{\partial V}{\partial S}+\frac{1}{2}\sigma^2S^2\frac{\partial^2V}{\partial S^2}\right)dt+\sigma S\frac{\partial V}{\partial S}dW_t
$$
- Usage desk: connect model dynamics to delta and gamma risk.
### F3 - Risk-neutral drift
$$
dS_t=(r-q)S_t\,dt+\sigma S_t\,dW_t^{\mathbb{Q}}
$$
- Usage desk: separate pricing measure logic from real-world forecasting.

