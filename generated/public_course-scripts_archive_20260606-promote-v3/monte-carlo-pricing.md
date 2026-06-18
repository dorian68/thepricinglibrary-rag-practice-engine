---
slug: monte-carlo-pricing
topic: Monte Carlo pricing and confidence intervals
product: path-dependent option
level: advanced
concepts: GBM, Asian option, standard error, variance reduction
source_count: 10
---

# Module pratique - Pricing des options asiatiques

> Légende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** réécriture pédagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit à partir des concepts; calculs vérifiés par le moteur déterministe, non extraits d'une source.

## Promesse du module
Apprendre le pricing des options asiatiques par la pratique : manipuler, calculer, comparer, décider, puis seulement formaliser la théorie nécessaire.

## Niveau cible et public
- Niveau : avancé
- Public visé : quant confirmé, trader junior, structureur
- Durée estimée : 120 minutes
- Produit : option asiatique
- Concepts : mouvement brownien géométrique (GBM), moyenne arithmétique, simulation de Monte Carlo, méthodes numériques

## Prerequis
- Espérance et variance
- Mouvement brownien géométrique
- Notions de simulation

## Objectifs d'apprentissage
À la fin de ce module, vous saurez :
- Expliquer l'intuition du sujet avant toute formule ;
- Identifier les inputs, les risques et les hypothèses clés ;
- Dérouler un calcul chiffré et l'interpréter en langage de desk ;
- Répondre à un mini-quiz et résoudre un exercice corrigé ;
- Nommer les limites du modèle et la décision opérationnelle associée.

## Positionnement bibliotheque
- Track : Dérivés & Volatilité
- Type d'asset : module réutilisable de cours.
- Sorties attendues : fiche apprenant, cas pratique, corrigé, quiz, notes instructeur.
- Intégration SaaS : ce module doit pouvoir être découpé en leçons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Ticket de simulation
- Objectif pratique : Définir le processus, le payoff, le monitoring et la précision attendue.
- Situation de desk : Un payoff asiatique n'a pas de prix ferme dans l'outil vanilla.
- Notion utile : GBM, pas de temps, seed, payoff path-dependent.
- Activité : Écrire le ticket modèle avant de coder.
- Livrable apprenant : Modèle de ticket.

### Module 2 - Generer les chemins
- Objectif pratique : Simuler les trajectoires avec contrôle de seed et discrétisation.
- Situation de desk : Le quant dev doit produire un prix reproductible.
- Notion utile : GBM exact step, chocs normaux, monitoring dates.
- Activité : Construire les chemins et vérifier les moments simples.
- Livrable apprenant : Notebook de simulation de chemins.

### Module 3 - Prix et intervalle
- Objectif pratique : Reporter prix, erreur standard et intervalle de confiance.
- Situation de desk : Le trader veut savoir si 5bp de différence est significatif.
- Notion utile : Espérance actualisée, erreur standard.
- Activité : Calculer prix et CI à 95%.
- Livrable apprenant : Quote avec incertitude.

### Module 4 - Reduction de variance
- Objectif pratique : Améliorer la précision sans exploser le temps de calcul.
- Situation de desk : Le batch overnight doit tenir son SLA.
- Notion utile : Antithétique, variate de contrôle, convergence.
- Activité : Comparer deux estimateurs.
- Livrable apprenant : Compte rendu de décision sur la méthode.

## Cours redige
### Lecon 1 - Ticket de simulation

**Intuition _[reformule]_.** Un payoff asiatique n'a pas de prix ferme dans l'outil vanilla. L'objectif de cette leçon est précisément : définir le processus, le payoff, le monitoring et la précision attendue.

**Ce que disent les sources** _[extrait]_. « To price the option, one must invert the Laplace transform numerically; see [7]. Shaw [18] demonstrated that the inversion can be done quickly and efficiently for all reasonable parameter choices in Mathematica, making this a fast and effective approach. » [S1]

**Le point clé : GBM, pas de temps, seed, payoff path-dependent.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Écrire le ticket modèle avant de coder. Livrable attendu : Modèle de ticket - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Confondre une sensibilité 'par 1%' avec 'par 0.01' : respecter strictement les unités.

### Lecon 2 - Generer les chemins

**Intuition _[reformule]_.** Le quant dev doit produire un prix reproductible. L'objectif de cette leçon est précisément : simuler les trajectoires avec contrôle de seed et discrétisation.

**Ce que disent les sources** _[extrait]_. « Monte Carlo methods are often the only viable computational strategy. Even more so when one has to deal with more complicated processes than an innocent geometric Brownian motion (GBM). » [S2]

**Le point clé : GBM exact step, chocs normaux, monitoring dates.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Construire les chemins et vérifier les moments simples. Livrable attendu : Notebook de simulation de chemins - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Oublier le signe de la position (long/short, payer/receiver) dans l'interprétation du P&L.

### Lecon 3 - Prix et intervalle

**Intuition _[reformule]_.** Le trader veut savoir si 5bp de différence est significatif. L'objectif de cette leçon est précisément : reporter prix, erreur standard et intervalle de confiance.

**Ce que disent les sources** _[extrait]_. « Option pricing is one of the most important application fields for Monte Carlo methods, since option prices may be expressed as expected values under a suitable probability measure. » [S3]

**Le point clé : Espérance actualisée, erreur standard.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer prix et CI à 95%. Livrable attendu : Quote avec incertitude - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Appliquer une approximation locale (Taylor) à un choc trop large sans vérifier sa validité.

### Lecon 4 - Reduction de variance

**Intuition _[reformule]_.** Le batch overnight doit tenir son SLA. L'objectif de cette leçon est précisément : améliorer la précision sans exploser le temps de calcul.

**Ce que disent les sources** _[extrait]_. « Monte Carlo methods are flexible and can be applied to path-dependent options. » [S4]

**Le point clé : Antithétique, variate de contrôle, convergence.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Comparer deux estimateurs. Livrable attendu : Compte rendu de décision sur la méthode - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Présenter un chiffre sans unité ni ordre de grandeur de contrôle.

## Labs pratiques a inclure
1. Modèle de ticket : processus, payoff, monitoring, seed, path count.
2. Simulation de chemins : générer chemins GBM et vérifier moyenne/variance.
3. Pricing : actualiser payoff moyen et calculer erreur standard.
4. Précision : produire CI à 95% et décider si l'écart est significatif.
5. Réduction de variance : comparer antithétique ou variate de contrôle.

## Script enseignant
1. Ouvrir par un cas concret.
2. Demander aux apprenants de formuler l'intuition.
3. Introduire la notation minimale.
4. Faire résoudre une micro-tâche.
5. Debrief : erreurs courantes, limites, interprétation marché.

## Supports a produire
- Fiche apprenant d'une page.
- Slides courtes orientées cas.
- Notebook ou tableur de calcul si le sujet s'y prête.
- Corrigé détaillé.
- Quiz de vérification rapide.

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

