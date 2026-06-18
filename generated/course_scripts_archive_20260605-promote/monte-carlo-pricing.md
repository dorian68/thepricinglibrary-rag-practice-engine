---
slug: monte-carlo-pricing
topic: Monte Carlo pricing and confidence intervals
product: path-dependent option
level: advanced
concepts: GBM, Asian option, standard error, variance reduction
source_count: 10
---

# Module pratique - Monte Carlo pricing and confidence intervals

## Promesse du module
Apprendre Monte Carlo pricing and confidence intervals par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: advanced
- Duree: 140 minutes
- Produit: path-dependent option
- Concepts: GBM, Asian option, standard error, variance reduction

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

**Cas de depart.** Un payoff asiatique n'a pas de prix ferme dans l'outil vanilla. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** the-money” Asian call and a Laplace transform
for “at-the-money” and “out-of-the-money” cases. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: GBM, pas de temps, seed, payoff path-dependent..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Ecrire le ticket modele avant de coder. Le livrable attendu est un document court et actionnable: Model ticket.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - Generer les chemins

**Cas de depart.** Le quant dev doit produire un prix reproductible. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Their methods are based on a relationship between
geometric Brownian motion and time-changed Bessel
processes. [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: GBM exact step, chocs normaux, monitoring dates..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Construire les chemins et verifier moments simples. Le livrable attendu est un document court et actionnable: Notebook path simulation.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Prix et intervalle

**Cas de depart.** Le trader veut savoir si 5bp de difference est significatif. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** To price the option, one must invert the
Laplace transform numerically; see [7]. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Discounted expectation, standard error..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer prix et CI 95%. Le livrable attendu est un document court et actionnable: Quote avec incertitude.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Variance reduction

**Cas de depart.** Le batch overnight doit tenir son SLA. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Shaw [18]
demonstrated that the inversion can be done quickly
and efﬁciently for all reasonable parameter choices
in Mathematica, making this a fast and effective
approach. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Antithetic, control variate, convergence..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Comparer deux estimateurs. Le livrable attendu est un document court et actionnable: Decision path count / methode.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. Model ticket: process, payoff, monitoring, seed, path count.
2. Path simulation: generer chemins GBM et verifier moyenne/variance.
3. Pricing: actualiser payoff moyen et calculer standard error.
4. Precision: produire CI 95% et decider si l'ecart est significatif.
5. Variance reduction: comparer antithetic ou control variate.

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
- the-money” Asian call and a Laplace transform
for “at-the-money” and “out-of-the-money” cases.
- Their methods are based on a relationship between
geometric Brownian motion and time-changed Bessel
processes.
- To price the option, one must invert the
Laplace transform numerically; see [7].
- Shaw [18]
demonstrated that the inversion can be done quickly
and efﬁciently for all reasonable parameter choices
in Mathematica, making this a fast and effective
approach.
- Linetsky [14] produced a quasi-analytic
pricing formula using eigenfunction methods, with
highly accurate results, also employing a package
such as Mathematica.
- Direct numerical methods such as Monte Carlo
or quasi-Monte Carlo simulation and ﬁnite-difference
partial differential equation (PDE) methods can be
used to price the Asian option (see Lattice Meth-
ods for Path-dependent Options).
- In fact, given
the popularity of such techniques, these methods
were probably amongst the ﬁrst used by practitioners
(and remain popular today).
- Monte Carlo simula-
tion was used to price Asian options by Broadie
and Glasserman [4] and Kemna and Vorst [11],
among many other more recent researchers.
- Simu-
lation methods have the advantage of being widely
used by practitioners to price derivatives, so no
“new” method is required.
- Additional practical fea-
tures such as stochastic volatility or interest rates
can be incorporated without a signiﬁcant increase
in complexity.

## Sources RAG a citer
- [S1] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 838, score 0.715954: the-money” Asian call and a Laplace transform
for “at-the-money” and “out-of-the-money” cases. Their methods are based on a relationship between
geometric Brownian motion and time-changed Bessel
processes. To price the option, one must invert the
Laplace transform numerically; see [7].
- [S2] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2038, score 0.528928: uantitative Analysis in Financial Markets,
M. Avellaneda, ed., World Scientiﬁc, 336–364, Vol. III,
www.math.nyu.edu/faculty/avellane/Conquering TheGreeks. pdf. Broadie, M. & Glasserman, P. (1996). Estimating security price
derivatives using simulation, Management Science 42(2),
269–285. Dupire, B. (ed) (1998). Monte Carlo: Methodologies and Appli-
cations for Pricing and Risk Management, Risk Publications.
- [S3] Handbook in Monte Carlo Simulation  Applications in Financial Engineering, Risk Management, and Economics ( PDFDrive ), chunk 450, score 0.511192: er Wheatsheaf, 
New York, 1994. 44 C. Tsallis and D.A. Stariolo. Generalized simulated annealing. Physica A, 
233:395-406, 1996. 45 C.J.C.H. Watkins and P. Dayan. Q-learning. Machine Learning, 8:279-292, 
1992. 46 H.P. Williams. Model Building in Mathematical Programming (4th ed.). Wiley, Chichester, 1999. 47 L.A. Wolsey. Integer Programming. Wiley, New York, 1998. 48 X.-S. Yang.
- [S4] Fourier Transform Methods in Finance (The Wiley Finance Series) ( PDFDrive ), chunk 196, score 0.508285: n time changed 
L´evy processes. Journal of Finance, 59 (3), 1405–1440. Hull, J. and White, A. (1998) Value at risk when daily changes in market variables are not normally 
distributed. Journal of Derivatives, 5 (3), 9–19. Hull, J. and White, A. (1987) The pricing of options on assets with stochastic volatility. Journal of 
Finance, 42, 281–300. Ingersoll, J.E.
- [S5] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 723, score 0.45501: derivative instruments can
be used with slight modifications in equity, currency,
commodity, and interest rate markets. Firms with
significant exposures to oil price risk are major users
of derivatives. Indeed derivatives are applicable to risk
management problems throughout an organization. In
fact, the widespread use of derivatives has spawned a
new profession, risk management.
- [S6] The Concepts and Practice of Mathematical Finance, Second Edition (Mathematics, Finance and Risk) ( PDFDrive ), chunk 482, score 0.454646: ytical tractability, contributed paper to the
Econometric Society World Congress 2000. [97] D. Lamberton, B. Lapeyre, Introduction to Stochastic Calculus Applied to Finance,
CRC Press, 1996. [98] D.P. Leisen, M. Reimer, Binomial models for option valuation-examining and
improving convergence, Applied Mathematical Finance 3, 1996, 319-46. [99] H.E.
- [S7] Derivatives Models on Models ( PDFDrive ), chunk 94, score 0.449722: initially were many people relying too much on the Black-Scholes-
Merton way of deriving the formula. For example Leland O’Brien Rubinstein Associates and
their way of constructing synthetic options (portfolio insurance) based on dynamic delta hedging
basically failed in the crash of 1987.
- [S8] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 752, score 0.447542: es of some kind, which requires
signiﬁcant modeling effort to value, and where differ-
ent analysts could well come up with signiﬁcantly dif-
ferent valuations. Exotic options often involve several
underlying assets and complicated payment streams,
but even a simple call option can be exotic if it
poses signiﬁcant hedging difﬁculties, as for exam-
ple do long-dated equity options.
- [S9] The Concepts and Practice of Mathematical Finance, Second Edition (Mathematics, Finance and Risk) ( PDFDrive ), chunk 479, score 0.420225: average intelligence, Risk 5, 1992, 60. [Page 546]
528
References
[44] M. Curran, Valuing Asian and portfolio options by conditioning on the geometric
mean price, Management Science 40, 1994, 1705-11. [45] F. Delbaen, W. Schachermayer, A general version of the fundamental theorem of
asset pricing, Mathematische Annalen 300, 1997, 463-520. [46] E.
- [S10] Derivatives Markets ( PDFDrive ), chunk 509, score 0.395332: ard contracts;
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

