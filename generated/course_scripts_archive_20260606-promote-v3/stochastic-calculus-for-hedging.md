---
slug: stochastic-calculus-for-hedging
topic: Stochastic calculus only where it helps hedging
product: option pricing model
level: expert
concepts: Ito lemma, SDE, risk-neutral measure, hedging
source_count: 10
---

# Module pratique - Stochastic calculus only where it helps hedging

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Stochastic calculus only where it helps hedging par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: expert
- Public vise: quant senior, desk strat
- Duree estimee: 150 minutes
- Produit: option pricing model
- Concepts: Ito lemma, SDE, risk-neutral measure, hedging

## Prerequis
- calcul differentiel
- mouvement brownien
- esperance conditionnelle

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

**Intuition _[reformule]_.** Un trader demande pourquoi delta hedge suppose un modele continu. L'objectif de cette lecon est precisement: Relier dynamique du sous-jacent et risque de couverture.

**Ce que disent les sources** _[extrait]_. « They offer these services to help their clients manage their risks. These financial institutions then turn
around and hedge the risk they have assumed on behalf of their clients. How do they
1The material in this section draws heavily from C. Smith and R. Stulz, “The Determinants of Firms’
Hedging Policies,” Journal of Financial and Quantitative Analysis 20 (1985): 391–405; D. » [S7]

**Le point cle: dS, drift, volatility, Brownian shock.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Lire une SDE et nommer chaque terme en langage desk. Livrable attendu: SDE risk translation - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

### Lecon 2 - Ito lemma pour P&L

**Intuition _[reformule]_.** Le P&L explique montre un terme de convexite non intuitif. L'objectif de cette lecon est precisement: Faire apparaitre delta, gamma et theta depuis une fonction de prix.

**Ce que disent les sources** _[extrait]_. « This model is called the Binomial Option Pricing
Model (BOPM) and it is a discrete time model. The Binomial option pricing
model uses a decision tree framework but goes beyond it. In fact, the Binomial
option pricing model shows how to correctly discount option payoffs in a
discrete, decision tree context. » [S8]

**Le point cle: Ito expansion, quadratic variation.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Deriver les blocs de P&L utiles a la couverture. Livrable attendu: Delta-gamma-theta map - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

### Lecon 3 - Mesure risque-neutre

**Intuition _[reformule]_.** Le learner confond forecast spot et prix d'option. L'objectif de cette lecon est precisement: Comprendre pourquoi le drift historique n'est pas l'input de pricing.

**Ce que disent les sources** _[extrait]_. « Jamshidian, F. (1991a): “Bond and Option Evaluation in the Gaussian Interest
Rate Model,” Research in Finance 9: 131–170. Jamshidian, F. (1991b): “Commodity Option Evaluation in the Gaussian Futures Term Structure Model,” Review of Futures Markets 10: 324–346. Jamshidian, F. (1991c): “Forward Induction and Construction of Yield Curve
Diffusion Models,” Journal of Fixed Income, June: 62–74. Jamshidian, F. » [S10]

**Le point cle: Risk-neutral drift, discounting, martingale pricing.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Comparer intuition P et calcul Q. Livrable attendu: Pricing measure note - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

### Lecon 4 - Limites du hedge continu

**Intuition _[reformule]_.** Le hedge discret subit gaps, frais et liquidite. L'objectif de cette lecon est precisement: Transformer la theorie en controles operationnels.

**Ce que disent les sources** _[extrait]_. « They offer these services to help their clients manage their risks. These financial institutions then turn
around and hedge the risk they have assumed on behalf of their clients. How do they
1The material in this section draws heavily from C. Smith and R. Stulz, “The Determinants of Firms’
Hedging Policies,” Journal of Financial and Quantitative Analysis 20 (1985): 391–405; D. » [S7]

**Le point cle: Discrete hedging error, transaction costs, model risk.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Lister triggers de monitoring et residual risk. Livrable attendu: Hedging caveat memo - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** presenter un chiffre sans unite ni ordre de grandeur de controle.

## Labs pratiques a inclure
1. SDE translation: relier drift, vol et choc Brownien au hedge desk.
2. Ito P&L: faire apparaitre delta, gamma et theta depuis dV.
3. Pricing measure: expliquer pourquoi le drift risque-neutre est utilise.
4. Discrete hedge: quantifier les limites gaps/frais/liquidite.
5. Hedging memo: controles operationnels et residual risk.

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
_[genere - calcul verifie]_ On price un call europeen a la monnaie et on lit prix, d1, d2 et greeks.

**Donnees.** Call vanilla spot 100 strike 100 vol 20% maturite 1 taux 5%.

### Option vanilla Black-Scholes
- Famille: vanilla_option_black_scholes
- Hypotheses controlees:
  - Pas de dividende/carry si non precise.
  - Volatilite et taux constants.
- Calculs a respecter:
  - d1/d2:
    - Formule: BS d1, d2
    - Application: d1=0.3500; d2=0.1500
    - Resultat: d1=0.3500, d2=0.1500
    - Lecture desk: Variables pivots du pricing et des greeks.
  - Prix call:
    - Formule: S*N(d1)-K*exp(-rT)*N(d2)
    - Application: 100*N(0.3500)-100*exp(-0.0500*1)*N(0.1500)
    - Resultat: 10.4506
    - Lecture desk: Valeur theorique du call.
  - Greeks:
    - Formule: Delta=N(d1); Gamma=phi(d1)/(S sigma sqrt(T)); Vega=S phi(d1) sqrt(T)/100
    - Application: inputs S=100, sigma=20.00%, T=1
    - Resultat: Delta=0.6368; Gamma=0.018762; Vega/vol pt=0.3752
    - Lecture desk: Base du hedge delta/vega.
- Actions operationnelles attendues:
  - Comparer prix modele et prix marche.
  - Hedger delta puis surveiller vega/gamma.

**Lecture finale.** Chaque chiffre ci-dessus a une unite explicite et un sens economique; un apprenant doit pouvoir refaire le calcul a la main et retrouver le meme ordre de grandeur.

## Exercices corriges
### Exercice 1 - application directe
_[genere]_ Un call ATM a S=K=100, vol 20%, T=1, r=5%. Sans calculer finement, dites si son delta est plutot proche de 0, 0.5 ou 1, et pourquoi.

**Correction.** Pour un call a la monnaie, N(d1) est legerement au-dessus de 0.5 (le drift r decale d1 vers le positif). Le delta est donc proche de 0.5-0.6: une hausse de 1 du spot fait gagner ~0.5-0.6 au call.

### Exercice 2 - niveau desk
_[genere]_ Spot 100, strike 100, vol 20%, T=1, r=5%. Calculez d1, d2, le prix du call et son delta, puis dites comment hedger 1000 calls.

**Correction detaillee (calcul verifie).**
### Option vanilla Black-Scholes
- Famille: vanilla_option_black_scholes
- Hypotheses controlees:
  - Pas de dividende/carry si non precise.
  - Volatilite et taux constants.
- Calculs a respecter:
  - d1/d2:
    - Formule: BS d1, d2
    - Application: d1=0.3500; d2=0.1500
    - Resultat: d1=0.3500, d2=0.1500
    - Lecture desk: Variables pivots du pricing et des greeks.
  - Prix call:
    - Formule: S*N(d1)-K*exp(-rT)*N(d2)
    - Application: 100*N(0.3500)-100*exp(-0.0500*1)*N(0.1500)
    - Resultat: 10.4506
    - Lecture desk: Valeur theorique du call.
  - Greeks:
    - Formule: Delta=N(d1); Gamma=phi(d1)/(S sigma sqrt(T)); Vega=S phi(d1) sqrt(T)/100
    - Application: inputs S=100, sigma=20.00%, T=1
    - Resultat: Delta=0.6368; Gamma=0.018762; Vega/vol pt=0.3752
    - Lecture desk: Base du hedge delta/vega.
- Actions operationnelles attendues:
  - Comparer prix modele et prix marche.
  - Hedger delta puis surveiller vega/gamma.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Dans Black-Scholes, que represente N(d2)?**
- A) La probabilite risque-neutre d'exercice
- B) Le delta du call
- C) La vega
- D) Le prix du put
  - Reponse: **A**. N(d2) est la probabilite risque-neutre que le call finisse dans la monnaie.

**Q2. Le delta d'un call ATM est environ:**
- A) 0
- B) 0.5
- C) 1
- D) -0.5
  - Reponse: **B**. N(d1) ~ 0.5 a la monnaie (legerement au-dessus avec un taux positif).

**Q3. La put-call parity relie call et put via:**
- A) la vol implicite
- B) C - P = S - K e^{-rT}
- C) le gamma
- D) la duration
  - Reponse: **B**. C - P = forward actualise - strike actualise; une violation signale une incoherence de quote.

**Q4. Augmenter la volatilite implicite fait:**
- A) baisser call et put
- B) monter call et put
- C) monter le call, baisser le put
- D) rien
  - Reponse: **B**. La vega est positive pour call et put: plus de vol = plus de valeur temps.

**Q5. La vega est maximale:**
- A) tres ITM
- B) tres OTM
- C) proche de la monnaie
- D) a maturite nulle
  - Reponse: **C**. La sensibilite a la vol est la plus forte autour de l'ATM, surtout a maturite moyenne.

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 10 (exploitables: 9).
- Score pedagogique moyen: 52.8/100 (qualite structurelle: 95.5/100).
- Definitions: 1 | exemples: 0 | exercices: 2 | formules: 4 | cas pratiques: 2.
- Repartition par type: theory: 7, solution: 2, methodology: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S8].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S3], [S4], [S8], [S9].
4. Exemples - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
5. Exemples resolus - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
6. Exercices - couvert par [S2], [S3], [S7], [S9].
7. Corriges - couvert par [S1], [S2], [S5], [S6].
8. Cas pratiques - couvert par [S4], [S5].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: partially_usable - Sources partiellement suffisantes: completer les manques.
- Presents dans les sources: definitions, formules, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, exemples, exemples resolus, resumes.

## Faits et angles extraits de la base
- •
Dynamic delta hedging removes a lot of risk compared to not hedging or to static delta
hedging, but there is plenty of risk left, and far too much to argue for risk-neutral
valuation in practice.
- The idea of continuous dynamic delta hedging to get risk-neutrality
is simply not a robust idea.
- •
Dynamic delta hedging works extremely poorly when we have jumps.
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
- Nelson’s (1904)
argument that most experienced option traders/dealers had a tendency to be long options
rather than short seems to be consistent with what experienced option traders are saying
today.

## Sources RAG a citer
- [S1] Derivatives Markets ( PDFDrive ), chunk 509, score 0.788129 (extrait non cite: source bruitee)
- [S2] Derivatives Markets ( PDFDrive ), chunk 505, score 0.770809 (extrait non cite: source bruitee)
- [S3] Derivatives Markets ( PDFDrive ), chunk 504, score 0.700684 (extrait non cite: source bruitee)
- [S4] Derivatives Markets ( PDFDrive ), chunk 528, score 0.609628 (extrait non cite: source bruitee)
- [S5] Derivatives Models on Models ( PDFDrive ), chunk 95, score 0.598581 (extrait non cite: source bruitee)
- [S6] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2295, score 0.590367 (extrait non cite: source bruitee)
- [S7] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 496, score 0.585707: They offer these services to help their clients manage their risks. These financial institutions then turn
around and hedge the risk they have assumed on behalf of their clients. How do they
1The material in this section draws heavily from C. Smith and R.
- [S8] Derivatives Markets ( PDFDrive ), chunk 356, score 0.556594: This model is called the Binomial Option Pricing
Model (BOPM) and it is a discrete time model. The Binomial option pricing
model uses a decision tree framework but goes beyond it. In fact, the Binomial
option pricing model shows how to correctly discount option payoffs in a
discrete, decision tree context.
- [S9] Derivatives Markets ( PDFDrive ), chunk 525, score 0.529995 (extrait non cite: source bruitee)
- [S10] Financial Derivatives  Pricing, Applications, and Mathematics ( PDFDrive ), chunk 212, score 0.529955: Jamshidian, F. (1991a): “Bond and Option Evaluation in the Gaussian Interest
Rate Model,” Research in Finance 9: 131–170. Jamshidian, F. (1991b): “Commodity Option Evaluation in the Gaussian Futures Term Structure Model,” Review of Futures Markets 10: 324–346. Jamshidian, F.

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

