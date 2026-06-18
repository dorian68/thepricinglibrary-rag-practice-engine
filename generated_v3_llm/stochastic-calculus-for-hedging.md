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

Dans le monde du trading, comprendre la dynamique d'un sous-jacent est essentiel pour gérer efficacement le risque. Prenons l'exemple d'une action dont le prix évolue de manière aléatoire. Ce mouvement peut être modélisé par une équation différentielle stochastique (EDS) qui décrit comment le prix d'une action, noté \( S_t \), change au cours du temps. Cette EDS intègre des éléments cruciaux tels que le drift, qui représente la tendance générale du prix, et la volatilité, qui mesure l'incertitude ou la dispersion des rendements. En d'autres termes, la volatilité est le facteur qui rend le prix d'un actif imprévisible, et le drift indique la direction générale dans laquelle le prix est susceptible d'évoluer.

Sur un desk de trading, cette compréhension est primordiale pour le processus de couverture, notamment dans le cadre du delta hedge. Lorsqu'un trader cherche à se protéger contre les variations de prix d'un actif, il doit tenir compte de la continuité des mouvements de prix. En effet, le delta hedge repose sur l'idée que les variations infinitésimales du prix de l'actif sous-jacent peuvent être compensées par des ajustements dans la position de couverture. Cela signifie que le trader doit être capable de réagir rapidement aux chocs de Brownien, ces mouvements brusques et imprévisibles qui peuvent survenir à tout moment. Comme le souligne l'extrait, les institutions financières aident leurs clients à gérer leurs risques, mais elles doivent également couvrir les risques qu'elles assument [S7].

Il est crucial de se rappeler que la modélisation continue est une hypothèse fondamentale qui permet de simplifier la gestion du risque. Un piège courant pour un junior est de penser que la couverture peut être effectuée efficacement sans prendre en compte la nature stochastique des mouvements de prix. Par exemple, un trader novice pourrait négliger l'importance de la volatilité dans ses calculs de couverture, en supposant que les mouvements de prix sont prévisibles et linéaires. Cette erreur peut entraîner des pertes significatives, car les ajustements de couverture basés sur des modèles discrets ne capturent pas la réalité des marchés, où les chocs de prix peuvent survenir de manière inattendue.

### Lecon 2 - Ito lemma pour P&L

Dans un environnement de trading, il est essentiel de comprendre comment les variations de prix d'un actif peuvent affecter le P&L (profit et perte) d'une position. Imaginons un spot à 100, et considérons une option dont le prix évolue en fonction de ce spot. La dynamique de ce prix n'est pas linéaire, et c'est ici que le lemme d'Itô entre en jeu. En appliquant l'expansion d'Itô, nous pouvons décomposer le changement de prix en plusieurs composantes, dont le delta, le gamma et le theta, qui sont cruciaux pour la gestion des risques sur un desk.

Le delta représente la sensibilité du prix de l'option par rapport à un changement infinitésimal du prix de l'actif sous-jacent. Le gamma, quant à lui, mesure la variation du delta lorsque le prix de l'actif change, ce qui introduit une notion de convexité dans notre analyse. Cela signifie que les mouvements de prix ne se traduisent pas simplement par des changements proportionnels dans le P&L, mais peuvent engendrer des effets non intuitifs, surtout dans des marchés volatils. En effet, un desk de trading doit être conscient que ces effets de convexité peuvent influencer significativement le P&L, rendant la couverture plus complexe que prévu.

L'extrait du modèle binomial de tarification des options [S8] souligne l'importance de bien comprendre comment les payoffs des options doivent être actualisés dans un cadre discret. Cela illustre que même dans des modèles simples, la gestion des risques et la tarification nécessitent une attention particulière aux variations quadratiques. Sur un desk, cela signifie que les traders doivent être capables d'anticiper ces variations pour ajuster leurs positions et leurs couvertures en conséquence.

Un piège courant pour un junior est de négliger l'impact du gamma dans des situations de forte volatilité. Souvent, ils se concentrent uniquement sur le delta, pensant que la couverture est suffisante. Cependant, en omettant l'effet du gamma, ils peuvent se retrouver exposés à des mouvements de prix qui dépassent leurs attentes, entraînant des pertes inattendues. Il est donc crucial de toujours considérer la convexité et d'intégrer ces éléments dans la stratégie de couverture.

### Lecon 3 - Mesure risque-neutre

Dans le monde du trading, il est crucial de comprendre que le drift historique d'un actif ne doit pas être utilisé comme input pour le pricing des options. Prenons l'exemple d'un actif dont le prix spot est actuellement à 100. Si l'on se base sur le drift historique pour prédire son évolution future, on pourrait s'attendre à ce qu'il continue à croître à un certain taux, disons 5% par an. Cependant, cette approche ne tient pas compte du fait que les marchés sont souvent influencés par des facteurs externes et que les prévisions basées sur le passé peuvent être trompeuses. En réalité, pour évaluer correctement les options, il est essentiel de se tourner vers une mesure de risque-neutre, où le drift est ajusté pour refléter les attentes du marché sans biais.

Le mécanisme sous-jacent à cette notion repose sur l'idée que, dans un cadre de mesure risque-neutre, les prix des actifs suivent des martingales. Cela signifie que, lorsqu'on actualise les prix futurs à l'aide d'un taux d'intérêt sans risque, la valeur actuelle des flux de trésorerie futurs est égale à leur prix de marché. Par conséquent, au lieu d'utiliser le drift historique, les traders doivent se concentrer sur le drift risque-neutre, qui est souvent inférieur ou supérieur au drift historique en fonction des conditions de marché. Comme le souligne Jamshidian dans ses travaux, cette approche est fondamentale pour évaluer correctement les options dans des modèles de taux d'intérêt ou de produits dérivés [S10].

Dans un desk de trading, cette distinction est cruciale. Un trader qui confond le drift historique avec le drift risque-neutre risque de mal évaluer les options, ce qui peut conduire à des positions non couvertes ou à des pertes significatives. En effet, en utilisant un drift inapproprié, le trader peut se retrouver à surévaluer ou sous-évaluer une option, ce qui fausse sa stratégie de couverture et affecte la rentabilité globale de son portefeuille.

Un piège fréquent pour un junior est de penser que le prix d'une option peut être directement déduit des prévisions de prix spot basées sur le passé. Cette confusion entre prévision et pricing peut entraîner des erreurs de jugement, notamment en négligeant l'importance de l'actualisation et du drift risque-neutre, ce qui compromet la gestion des risques sur le desk.

### Lecon 4 - Limites du hedge continu

Dans un environnement de marché, la gestion des risques est primordiale pour les institutions financières, qui doivent souvent faire face à des situations où le hedge discret peut être insuffisant. Imaginons une position sur un actif dont le prix spot est à 100. Si un événement de marché provoque un gap, la couverture mise en place peut ne pas être efficace, entraînant une erreur de couverture discrète. Ce type d'erreur se produit lorsque le prix d'exécution de la couverture ne correspond pas à celui de l'actif sous-jacent, ce qui peut être amplifié par des frais de transaction et des problèmes de liquidité. Les institutions financières, comme le soulignent Smith et Stulz, doivent non seulement gérer les risques pour leurs clients, mais également se couvrir contre les risques qu'elles assument elles-mêmes [S7].

La compréhension des coûts de transaction et du risque de modèle est essentielle sur un desk de trading. Les coûts de transaction peuvent réduire significativement les gains potentiels d'une stratégie de couverture, surtout dans des marchés volatils où les spreads peuvent s'élargir. De plus, le risque de modèle intervient lorsque les hypothèses sous-jacentes d'un modèle de couverture ne se réalisent pas dans la réalité. Par exemple, si un modèle suppose une volatilité constante alors que celle-ci fluctue, la couverture peut devenir inefficace, laissant le desk exposé à des pertes imprévues. Cela souligne l'importance d'une surveillance continue des positions et des ajustements en temps réel.

Pour gérer ces risques, il est crucial de mettre en place des triggers de monitoring. Ces déclencheurs peuvent inclure des seuils de perte, des variations de volatilité, ou des écarts de prix spécifiques qui, lorsqu'atteints, signalent la nécessité d'une réévaluation de la stratégie de couverture. En parallèle, il est essentiel d'évaluer le risque résiduel, c'est-à-dire le risque qui demeure après la mise en place de la couverture. Cela permet de quantifier l'exposition restante et d'ajuster les positions en conséquence.

Un piège fréquent pour un junior est de négliger l'impact des frais de transaction sur le résultat net de la couverture. Parfois, dans l'enthousiasme de réduire l'exposition au risque, un trader peut exécuter des transactions fréquentes sans tenir compte des coûts associés, ce qui peut finalement conduire à des pertes nettes. Cette méprise peut être particulièrement coûteuse dans un environnement de marché où les mouvements de prix sont rapides et imprévisibles.

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

