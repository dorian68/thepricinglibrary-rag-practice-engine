---
slug: implied-volatility-smile
topic: Implied volatility smile and quote cleaning
product: equity index options
level: intermediate
concepts: implied volatility, smile, skew, SVI
source_count: 10
---

# Module pratique - Implied volatility smile and quote cleaning

## Promesse du module
Apprendre Implied volatility smile and quote cleaning par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: intermediate
- Duree: 130 minutes
- Produit: equity index options
- Concepts: implied volatility, smile, skew, SVI

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
### Module 1 - Lire la chaine d'options
- Objectif pratique: Nettoyer les quotes avant tout fit.
- Situation de desk: Les bids/asks contiennent des quotes stale et croisees.
- Notion utile: Bounds, moneyness, bid/ask mid.
- Activite: Filtrer la chaine et documenter les rejets.
- Livrable apprenant: Clean option chain.
### Module 2 - Inversion en IV
- Objectif pratique: Transformer les prix en volatilites implicites comparables.
- Situation de desk: Le trader raisonne en vol, pas en premium brut.
- Notion utile: Black-Scholes inversion, vega, convergence.
- Activite: Calculer IV par strike.
- Livrable apprenant: Slice IV.
### Module 3 - Smile et skew
- Objectif pratique: Interpreter la forme de smile comme signal de risque.
- Situation de desk: Le put wing s'enrichit avant un evenement macro.
- Notion utile: Skew, term structure, convexite.
- Activite: Tracer smile et commenter le risque.
- Livrable apprenant: Vol note.
### Module 4 - Fit utilisable
- Objectif pratique: Produire une courbe lisse sans cacher les controles.
- Situation de desk: Le pricer a besoin d'une surface stable.
- Notion utile: SVI ou fit quadratique, no-arbitrage checks.
- Activite: Fit, residus, controles.
- Livrable apprenant: Fit report.

## Cours redige
### Lecon 1 - Lire la chaine d'options

**Cas de depart.** Les bids/asks contiennent des quotes stale et croisees. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** e implied volatility, and known dynamics for the evo-
lution of the underlying spot price as well as the implied volatility surface
itself. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Bounds, moneyness, bid/ask mid..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Filtrer la chaine et documenter les rejets. Le livrable attendu est un document court et actionnable: Clean option chain.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - Inversion en IV

**Cas de depart.** Le trader raisonne en vol, pas en premium brut. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** “A New Simple Approach for Constructing
Implied Volatility Surfaces.” Working paper, New York University and Baruch
College. [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Black-Scholes inversion, vega, convergence..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer IV par strike. Le livrable attendu est un document court et actionnable: Slice IV.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Smile et skew

**Cas de depart.** Le put wing s'enrichit avant un evenement macro. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** “Introduction to the Volatility Smile.” Lecture notes,
Columbia University. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Skew, term structure, convexite..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Tracer smile et commenter le risque. Le livrable attendu est un document court et actionnable: Vol note.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Fit utilisable

**Cas de depart.** Le pricer a besoin d'une surface stable. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** “A Parsimonious Arbitrage-Free Implied Volatility Parameteri-
zation with Application to the Valuation of Volatility Derivatives.” Proceedings
of the Global Derivatives and Risk Management 2004 Madrid conference. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: SVI ou fit quadratique, no-arbitrage checks..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Fit, residus, controles. Le livrable attendu est un document court et actionnable: Fit report.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. Quote cleaning: filtrer quotes impossibles/stale.
2. IV inversion: calculer vol implicite par strike.
3. Smile view: expliquer skew et risque de hedge.
4. Fit report: ajuster une courbe et controler les residus.

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
- e implied volatility, and known dynamics for the evo-
lution of the underlying spot price as well as the implied volatility surface
itself.
- “A New Simple Approach for Constructing
Implied Volatility Surfaces.” Working paper, New York University and Baruch
College.
- “Introduction to the Volatility Smile.” Lecture notes,
Columbia University.
- “A Parsimonious Arbitrage-Free Implied Volatility Parameteri-
zation with Application to the Valuation of Volatility Derivatives.” Proceedings
of the Global Derivatives and Risk Management 2004 Madrid conference.
- “Convergence of Heston to SVI.” Quan-
titative Finance 11 (8): 1129–1132.
- “A Class of Term Structures for SVI Implied Volatility.”
Working paper.
- Available at http://ssrn.com/abstract=1779463 or http://dx
.doi.org/10.2139/ssrn.1779463.
- [Page 50]
30
ADVANCED EQUITY DERIVATIVES
Hagan, Patrick S., Deep Kumar, Andrew L.
- “A Closed-Form Solution for Options with Stochastic
Volatility with Applications to Bond and Currency Options.” Review of Finan-
cial Studies 6 (2): 327–343.
- “Arbitrage Bounds on the Implied Volatility Strike and
Term Structures of European-Style Options.” Journal of Derivatives (Summer):
23–35.

## Sources RAG a citer
- [S1] Advanced Equity Derivatives  Volatility and Correlation ( PDFDrive ), chunk 26, score 0.96475: e implied volatility, and known dynamics for the evo-
lution of the underlying spot price as well as the implied volatility surface
itself. REFERENCES AND BIBLIOGRAPHY
Carr, Peter, and Liuren Wu. 2011. “A New Simple Approach for Constructing
Implied Volatility Surfaces.” Working paper, New York University and Baruch
College. Derman, Emanuel. 2010.
- [S2] Emerging Financial Derivatives  Understanding exotic options and structured products ( PDFDrive ), chunk 40, score 0.779555: i, I. (1994). “Riding on a Smile.” Risk, 7(2): 32–39. Figlewski, S. & Gao, B. (1999). “The Adaptive Mesh Model: A New Approach to 
Efficient Option Pricing.” Journal of Financial Economics, 53: 313–51. Figlewski, S., Gao, B., & Ahn, D. H. (1999). “Pricing Discrete Barrier Options with an 
Adaptive Mesh Model,” Working Paper, 1999. Haug, E. (1998). Complete Guide to Option Pricing Formulas. McGraw-Hill. Hull, J.
- [S3] FX Derivatives Trader School ( PDFDrive ), chunk 142, score 0.778168: olatility surface, volatilities
are deﬁned only between 10 delta puts on the downside and 10 delta calls on the
topside. Implied volatilities beyond the 10 delta strikes must either be controlled
usingextrapolationorgeneratedautomaticallyusingamodellikeStochasticVolatility
Inspired (SVI)-see Gatheral’s book in Further Reading for more information.
- [S4] FX Derivatives Trader School ( PDFDrive ), chunk 66, score 0.769737: volatility smile (i.e., how steep
the sides of the volatility smile are). ■The risk reversal contract describes the skew of the volatility smile (i.e., how
tilted the volatility smile is). Butterﬂy and risk reversal contracts are quoted at market tenors like the ATM
curve.
- [S5] Emerging Financial Derivatives  Understanding exotic options and structured products ( PDFDrive ), chunk 42, score 0.755231: the BS formula. When the implied volatility is plotted against the strike price, the resulting graph is 
typically downward sloping for equity markets, or valley-shaped for currency 
markets. For markets where the graph is downward sloping, such as for equity 
options, the term volatility skew is often used.
- [S6] Principles of Financial Engineering ( PDFDrive ), chunk 616, score 0.746717: h costs, the market maker may
want to sell the out-of-the-money option at a higher price than warranted by the ATM volatility. 16.14 THE RELEVANCE OF THE SMILE
The volatility smile is important in financial engineering for at least three reasons.
- [S7] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 110, score 0.739791: of Volatility
In addition to the volatility smile, options of different maturities also display 
characteristic differences in implied volatility. This is referred to as the term 
structure of volatility. A few things affect the term structure of volatility. The main 
effect relates to the implied impact of upcoming market events.
- [S8] FX Derivatives Trader School ( PDFDrive ), chunk 65, score 0.73879: n practice. As the horizon date changes, the expiry date for each market tenor
changes accordingly (the methodology for calculating tenor expiry dates is given
in Chapter 10 and implemented in Practical D). Therefore, the contracts liquidly
quoted in the market today have different expiry dates from those quoted yesterday
or those quoted tomorrow.
- [S9] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 107, score 0.73101: s that the market 
for options is driven largely by investors aiming to “insure” their equity hold-
ings, particularly since the 1987 crash, and that those buyers are natural buyers 
of out-of-the-money put options. It is also reasonable to believe that as a compa-
ny’s equity value declines, its leverage increases.
- [S10] FX Derivatives Trader School ( PDFDrive ), chunk 208, score 0.73046: ither the start of the calendar year or at the start or end of their accounting year. The majority of corporate hedge structures net sell vega and this ﬂow into the mar-
ketcancauseimpliedvolatilitytoconsistentlymoveloweratcertaintimesoftheyear.

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Implied volatility root
$$
\sigma_{\text{imp}}:\quad BS(S,K,r,q,T,\sigma_{\text{imp}})=P_{\text{mkt}}
$$
- Usage desk: convert option prices into comparable volatility quotes.
### F2 - Newton update
$$
\sigma_{k+1}=\sigma_k-\frac{BS(\sigma_k)-P_{\text{mkt}}}{\text{Vega}(\sigma_k)}
$$
- Usage desk: iterate quickly while monitoring low-vega strikes.
### F3 - SVI total variance
$$
w(k)=a+b\left(\rho(k-m)+\sqrt{(k-m)^2+\eta^2}\right)
$$
- Usage desk: fit a clean smile while keeping skew and curvature visible.

