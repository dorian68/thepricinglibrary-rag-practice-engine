---
slug: monte-carlo-pricing
topic: Monte Carlo pricing and confidence intervals
product: path-dependent option
level: advanced
concepts: GBM, Asian option, standard error, variance reduction
source_count: 10
---

# Module pratique - Monte Carlo pricing and confidence intervals

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Monte Carlo pricing and confidence intervals par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: advanced
- Public vise: quant confirme, trader junior, structureur
- Duree estimee: 140 minutes
- Produit: path-dependent option
- Concepts: GBM, Asian option, standard error, variance reduction

## Prerequis
- esperance et variance
- mouvement brownien geometrique
- intervalle de confiance

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
### Module 1 - Ticket de simulation
- Objectif pratique: Definir process, payoff, monitoring et precision attendue.
- Situation de desk: Un payoff asiatique n'a pas de prix ferme dans l'outil vanilla.
- Notion utile: GBM, pas de temps, seed, payoff path-dependent.
- Activite: Ecrire le ticket modele avant de coder.
- Livrable apprenant: Model ticket.
### Module 2 - Generer les chemins
- Objectif pratique: Simuler les trajectoires avec controle de seed et discretisation.
- Situation de desk: Le quant dev doit produire un prix reproductible.
- Notion utile: GBM exact step, chocs normaux, monitoring dates.
- Activite: Construire les chemins et verifier moments simples.
- Livrable apprenant: Notebook path simulation.
### Module 3 - Prix et intervalle
- Objectif pratique: Reporter prix, standard error et intervalle de confiance.
- Situation de desk: Le trader veut savoir si 5bp de difference est significatif.
- Notion utile: Discounted expectation, standard error.
- Activite: Calculer prix et CI 95%.
- Livrable apprenant: Quote avec incertitude.
### Module 4 - Variance reduction
- Objectif pratique: Ameliorer la precision sans exploser le temps de calcul.
- Situation de desk: Le batch overnight doit tenir son SLA.
- Notion utile: Antithetic, control variate, convergence.
- Activite: Comparer deux estimateurs.
- Livrable apprenant: Decision path count / methode.

## Cours redige
### Lecon 1 - Ticket de simulation

**Intuition _[reformule]_.** Un payoff asiatique n'a pas de prix ferme dans l'outil vanilla. L'objectif de cette lecon est precisement: Definir process, payoff, monitoring et precision attendue.

**Ce que disent les sources** _[extrait]_. « Their methods are based on a relationship between
geometric Brownian motion and time-changed Bessel
processes. To price the option, one must invert the
Laplace transform numerically; see [7]. Shaw [18]
demonstrated that the inversion can be done quickly
and efficiently for all reasonable parameter choices
in Mathematica, making this a fast and effective
approach. » [S1]

**Le point cle: GBM, pas de temps, seed, payoff path-dependent.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Ecrire le ticket modele avant de coder. Livrable attendu: Model ticket - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

### Lecon 2 - Generer les chemins

**Intuition _[reformule]_.** Le quant dev doit produire un prix reproductible. L'objectif de cette lecon est precisement: Simuler les trajectoires avec controle de seed et discretisation.

**Ce que disent les sources** _[extrait]_. « Avellaneda, ed., World Scientific, 336–364, Vol. III,
www.math.nyu.edu/faculty/avellane/Conquering TheGreeks. & Glasserman, P. Estimating security price
derivatives using simulation, Management Science 42(2),
269–285. (ed) (1998). Monte Carlo: Methodologies and Applications for Pricing and Risk Management, Risk Publications. Fournie, E., Lasry, J.M., Lebuchoux, J., Lions, P.L. » [S2]

**Le point cle: GBM exact step, chocs normaux, monitoring dates.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Construire les chemins et verifier moments simples. Livrable attendu: Notebook path simulation - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

### Lecon 3 - Prix et intervalle

**Intuition _[reformule]_.** Le trader veut savoir si 5bp de difference est significatif. L'objectif de cette lecon est precisement: Reporter prix, standard error et intervalle de confiance.

**Ce que disent les sources** _[extrait]_. « Tsallis and D.A. Generalized simulated annealing. Physica A, 
233:395-406, 1996. Watkins and P. Machine Learning, 8:279-292, 
1992. Model Building in Mathematical Programming (4th ed.). Wiley, Chichester, 1999. Integer Programming. Wiley, New York, 1998. Firefly algorithm, Levy flights and global optimization. Ellis, and M. Petridis, editors, Research and Development in 
Intelligent Systems XXVI, pp. Springer, 2010. » [S3]

**Le point cle: Discounted expectation, standard error.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer prix et CI 95%. Livrable attendu: Quote avec incertitude - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

### Lecon 4 - Variance reduction

**Intuition _[reformule]_.** Le batch overnight doit tenir son SLA. L'objectif de cette lecon est precisement: Ameliorer la precision sans exploser le temps de calcul.

**Ce que disent les sources** _[extrait]_. « Journal of Finance, 59 (3), 1405–1440. and White, A. (1998) Value at risk when daily changes in market variables are not normally 
distributed. Journal of Derivatives, 5 (3), 9–19. and White, A. (1987) The pricing of options on assets with stochastic volatility. Journal of 
Finance, 42, 281–300. Ingersoll, J.E. (2000) Digital contracts: Simple tools for pricing complex derivatives. » [S4]

**Le point cle: Antithetic, control variate, convergence.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Comparer deux estimateurs. Livrable attendu: Decision path count / methode - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** presenter un chiffre sans unite ni ordre de grandeur de controle.

## Labs pratiques a inclure
1. Model ticket: process, payoff, monitoring, seed, path count.
2. Path simulation: generer chemins GBM et verifier moyenne/variance.
3. Pricing: actualiser payoff moyen et calculer standard error.
4. Precision: produire CI 95% et decider si l'ecart est significatif.
5. Variance reduction: comparer antithetic ou control variate.

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
- Score pedagogique moyen: 50.5/100 (qualite structurelle: 81.0/100).
- Definitions: 1 | exemples: 4 | exercices: 1 | formules: 1 | cas pratiques: 2.
- Repartition par type: theory: 7, worked_example: 2, solution: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S6].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S5].
4. Exemples - couvert par [S1], [S2], [S5], [S8].
5. Exemples resolus - couvert par [S2], [S5].
6. Exercices - couvert par [S3], [S5], [S7].
7. Corriges - couvert par [S2], [S3], [S10].
8. Cas pratiques - couvert par [S2], [S3].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, resumes.

## Faits et angles extraits de la base
- Their methods are based on a relationship between
geometric Brownian motion and time-changed Bessel
processes.
- To price the option, one must invert the
Laplace transform numerically; see [7].
- Shaw [18]
demonstrated that the inversion can be done quickly
and efficiently for all reasonable parameter choices
in Mathematica, making this a fast and effective
approach.
- Linetsky [14] produced a quasi-analytic
pricing formula using eigenfunction methods, with
highly accurate results, also employing a package
such as Mathematica.
- Direct numerical methods such as Monte Carlo
or quasi-Monte Carlo simulation and finite-difference
partial differential equation (PDE) methods can be
used to price the Asian option (see Lattice Methods for Path-dependent Options).
- In fact, given
the popularity of such techniques, these methods
were probably amongst the first used by practitioners
(and remain popular today).
- Monte Carlo simulation was used to price Asian options by Broadie
and Glasserman [4] and Kemna and Vorst [11],
among many other more recent researchers.
- Simulation methods have the advantage of being widely
used by practitioners to price derivatives, so no
“new” method is required.
- Additional practical features such as stochastic volatility or interest rates
can be incorporated without a significant increase
in complexity.
- Control variates can often be used
(e.g., using a geometric Asian option when pricing an arithmetic option).

## Sources RAG a citer
- [S1] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 838, score 0.715954: Their methods are based on a relationship between
geometric Brownian motion and time-changed Bessel
processes. To price the option, one must invert the
Laplace transform numerically; see [7].
- [S2] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2038, score 0.525842: Avellaneda, ed., World Scientific, 336–364, Vol. III,
www.math.nyu.edu/faculty/avellane/Conquering TheGreeks. & Glasserman, P. Estimating security price
derivatives using simulation, Management Science 42(2),
269–285. (ed) (1998).
- [S3] Handbook in Monte Carlo Simulation  Applications in Financial Engineering, Risk Management, and Economics ( PDFDrive ), chunk 450, score 0.510039: Tsallis and D.A. Generalized simulated annealing. Physica A, 
233:395-406, 1996. Watkins and P. Machine Learning, 8:279-292, 
1992. Model Building in Mathematical Programming (4th ed.). Wiley, Chichester, 1999. Integer Programming. Wiley, New York, 1998. Firefly algorithm, Levy flights and global optimization.
- [S4] Fourier Transform Methods in Finance (The Wiley Finance Series) ( PDFDrive ), chunk 196, score 0.498004: Journal of Finance, 59 (3), 1405–1440. and White, A. (1998) Value at risk when daily changes in market variables are not normally 
distributed. Journal of Derivatives, 5 (3), 9–19. and White, A. (1987) The pricing of options on assets with stochastic volatility. Journal of 
Finance, 42, 281–300. Ingersoll, J.E.
- [S5] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 752, score 0.45399: Exotic options often involve several
underlying assets and complicated payment streams,
but even a simple call option can be exotic if it
poses significant hedging difficulties, as for example do long-dated equity options.
- [S6] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 723, score 0.451672: Firms with
significant exposures to oil price risk are major users
of derivatives. Indeed derivatives are applicable to risk
management problems throughout an organization. In
fact, the widespread use of derivatives has spawned a
new profession, risk management.
- [S7] The Concepts and Practice of Mathematical Finance, Second Edition (Mathematics, Finance and Risk) ( PDFDrive ), chunk 482, score 0.449321: Lamberton, B. Lapeyre, Introduction to Stochastic Calculus Applied to Finance,
CRC Press, 1996. Reimer, Binomial models for option valuation-examining and
improving convergence, Applied Mathematical Finance 3, 1996, 319-46.
- [S8] Derivatives Models on Models ( PDFDrive ), chunk 94, score 0.447828: For example Leland O’Brien Rubinstein Associates and
their way of constructing synthetic options (portfolio insurance) based on dynamic delta hedging
basically failed in the crash of 1987.
- [S9] The Concepts and Practice of Mathematical Finance, Second Edition (Mathematics, Finance and Risk) ( PDFDrive ), chunk 479, score 0.413035 (extrait non cite: source bruitee)
- [S10] Derivatives Markets ( PDFDrive ), chunk 509, score 0.388893 (extrait non cite: source bruitee)

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - GBM step
$$
S_{t+\Delta t}=S_t\exp\left((r-q-\frac{1}{2}\sigma^2)\Delta t+\sigma\sqrt{\Delta t}Z\right)
$$
- Usage desk: simulate risk-neutral paths for a path-dependent payoff.
### F2 - Discounted estimator
$$
\hat{V}_0=e^{-rT}\frac{1}{M}\sum_{m=1}^{M}\Phi(S^{(m)})
$$
- Usage desk: price by averaging simulated payoffs and discounting them.
### F3 - Confidence interval
$$
\hat{V}_0 \pm 1.96\frac{s_{\Phi}}{\sqrt{M}}
$$
- Usage desk: decide whether the Monte Carlo error is small enough for the desk use case.

