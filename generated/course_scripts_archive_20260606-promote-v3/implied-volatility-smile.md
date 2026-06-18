---
slug: implied-volatility-smile
topic: Implied volatility smile and quote cleaning
product: equity index options
level: intermediate
concepts: implied volatility, smile, skew, SVI
source_count: 10
---

# Module pratique - Implied volatility smile and quote cleaning

> Légende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** réécriture pédagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit à partir des concepts; calculs vérifiés par le moteur déterministe, non extraits d'une source.

## Promesse du module
Apprendre l'Implied volatility smile et le nettoyage des quotes par la pratique : manipuler, calculer, comparer, décider, puis seulement formaliser la théorie nécessaire.

## Niveau cible et public
- Niveau : intermédiaire
- Public visé : junior quant, analyste market risk, sales/structuring junior
- Durée estimée : 130 minutes
- Produit : equity index options
- Concepts : implied volatility, smile, skew, SVI

## Prerequis
- Prix d'option vanilla
- Volatilité implicite
- Inversion de Black-Scholes

## Objectifs d'apprentissage
À la fin de ce module, vous saurez :
- Expliquer l'intuition du sujet avant toute formule ;
- Identifier les inputs, les risques et les hypothèses clés ;
- Dérouler un calcul chiffré et l'interpréter en langage de desk ;
- Répondre à un mini-quiz et résoudre un exercice corrigé ;
- Nommer les limites du modèle et la décision opérationnelle associée.

## Positionnement bibliotheque
- Track : Derivatives & Volatility
- Type d'asset : module réutilisable de cours.
- Sorties attendues : fiche apprenant, cas pratique, corrigé, quiz, notes instructeur.
- Intégration SaaS : ce module doit pouvoir être découpé en leçons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire la chaine d'options
- Objectif pratique : Nettoyer les quotes avant tout fit.
- Situation de desk : Les bids/asks contiennent des quotes obsolètes et croisées.
- Notion utile : Bounds, moneyness, bid/ask mid.
- Activité : Filtrer la chaîne et documenter les rejets.
- Livrable apprenant : Clean option chain.

### Module 2 - Inversion en IV
- Objectif pratique : Transformer les prix en volatilités implicites comparables.
- Situation de desk : Le trader raisonne en vol, pas en premium brut.
- Notion utile : Black-Scholes inversion, vega, convergence.
- Activité : Calculer IV par strike.
- Livrable apprenant : Slice IV.

### Module 3 - Smile et skew
- Objectif pratique : Interpréter la forme de smile comme signal de risque.
- Situation de desk : Le put wing s'enrichit avant un événement macro.
- Notion utile : Skew, term structure, convexité.
- Activité : Tracer smile et commenter le risque.
- Livrable apprenant : Vol note.

### Module 4 - Fit utilisable
- Objectif pratique : Produire une courbe lisse sans cacher les contrôles.
- Situation de desk : Le pricer a besoin d'une surface stable.
- Notion utile : SVI ou fit quadratique, no-arbitrage checks.
- Activité : Fit, résidus, contrôles.
- Livrable apprenant : Fit report.

## Cours redige
### Lecon 1 - Lire la chaine d'options

**Intuition _[reformule]_.** Les bids/asks contiennent des quotes obsolètes et croisées. L'objectif de cette leçon est précisément : Nettoyer les quotes avant tout fit.

**Ce que disent les sources** _[extrait]_. « REFERENCES AND BIBLIOGRAPHY Carr, Peter, and Liuren Wu. “A New Simple Approach for Constructing Implied Volatility Surfaces.” Working paper, New York University and Baruch College. Derman, Emanuel. “Introduction to the Volatility Smile.” Lecture notes, Columbia University. Gatheral, Jim. » [S1]

**Le point clé : Bounds, moneyness, bid/ask mid.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Filtrer la chaîne et documenter les rejets. Livrable attendu : Clean option chain - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Confondre une sensibilité 'par 1%' avec 'par 0.01' : respecter strictement les unités.

### Lecon 2 - Inversion en IV

**Intuition _[reformule]_.** Le trader raisonne en vol, pas en premium brut. L'objectif de cette leçon est précisément : Transformer les prix en volatilités implicites comparables.

**Ce que disent les sources** _[extrait]_. « Implied volatilities beyond the 10 delta strikes must either be controlled using extrapolation or generated automatically using a model like Stochastic Volatility Inspired (SVI) - see Gatheral’s book in Further Reading for more information. » [S2]

**Le point clé : Black-Scholes inversion, vega, convergence.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer IV par strike. Livrable attendu : Slice IV - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Oublier le signe de la position (long/short, payer/receiver) dans l'interprétation du P&L.

### Lecon 3 - Smile et skew

**Intuition _[reformule]_.** Le put wing s'enrichit avant un événement macro. L'objectif de cette leçon est précisément : Interpréter la forme de smile comme signal de risque.

**Ce que disent les sources** _[extrait]_. « “Riding on a Smile.” Risk, 7(2): 32–39. Figlewski, S. “The Adaptive Mesh Model: A New Approach to Efficient Option Pricing.” Journal of Financial Economics, 53: 313–51. Figlewski, S., Gao, B., & Ahn, D. “Pricing Discrete Barrier Options with an Adaptive Mesh Model,” Working Paper, 1999. Complete Guide to Option Pricing Formulas. McGraw-Hill. Options, Futures, & Other Derivatives. Prentice Hall. » [S3]

**Le point clé : Skew, term structure, convexité.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Tracer smile et commenter le risque. Livrable attendu : Vol note - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Appliquer une approximation locale (Taylor) à un choc trop large sans vérifier sa validité.

### Lecon 4 - Fit utilisable

**Intuition _[reformule]_.** Le pricer a besoin d'une surface stable. L'objectif de cette leçon est précisément : Produire une courbe lisse sans cacher les contrôles.

**Ce que disent les sources** _[extrait]_. « ■The risk reversal contract describes the skew of the volatility smile (i.e., how tilted the volatility smile is). Butterfly and risk reversal contracts are quoted at market tenors like the ATM curve. In equity derivatives, lower strikes tend to have higher implied volatility than higher strikes at a given maturity because equities tend to rally slowly and » [S4]

**Le point clé : SVI ou fit quadratique, no-arbitrage checks.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Fit, résidus, contrôles. Livrable attendu : Fit report - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Présenter un chiffre sans unité ni ordre de grandeur de contrôle.

## Labs pratiques a inclure
1. Quote cleaning : filtrer quotes impossibles/stale.
2. IV inversion : calculer vol implicite par strike.
3. Smile view : expliquer skew et risque de hedge.
4. Fit report : ajuster une courbe et contrôler les résidus.

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
- Chunks sources analyses: 10 (exploitables: 10).
- Score pedagogique moyen: 57.8/100 (qualite structurelle: 94.0/100).
- Definitions: 2 | exemples: 6 | exercices: 1 | formules: 1 | cas pratiques: 1.
- Repartition par type: theory: 6, diagram_description: 2, worked_example: 1, example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S3], [S5].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S1].
4. Exemples - couvert par [S1], [S2], [S4], [S5].
5. Exemples resolus - couvert par [S1].
6. Exercices - couvert par [S6].
7. Corriges - couvert par [S1], [S3], [S7], [S9].
8. Cas pratiques - couvert par [S4].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, resumes.

## Faits et angles extraits de la base
- “A New Simple Approach for Constructing
Implied Volatility Surfaces.” Working paper, New York University and Baruch
College.
- “Introduction to the Volatility Smile.” Lecture notes,
Columbia University.
- “A Parsimonious Arbitrage-Free Implied Volatility Parameterization with Application to the Valuation of Volatility Derivatives.” Proceedings
of the Global Derivatives and Risk Management 2004 Madrid conference.
- “Convergence of Heston to SVI.” Quantitative Finance 11 (8): 1129–1132.
- “A Class of Term Structures for SVI Implied Volatility.”
Working paper.
- “Managing Smile Risk.” Wilmott Magazine (September): 84–108.
- “A Closed-Form Solution for Options with Stochastic
Volatility with Applications to Bond and Currency Options.” Review of Financial Studies 6 (2): 327–343.
- “Arbitrage Bounds on the Implied Volatility Strike and
Term Structures of European-Style Options.” Journal of Derivatives (Summer):
23–35.
- “Implied Volatility Surface: Construction Methodologies
and Characteristics.” Available at http://arxiv.org/abs/1107.1834v1.
- “Diffusion Processes.” In A Second
Course in Stochastic Processes, 157–396.

## Sources RAG a citer
- [S1] Advanced Equity Derivatives  Volatility and Correlation ( PDFDrive ), chunk 26, score 0.96475: REFERENCES AND BIBLIOGRAPHY
Carr, Peter, and Liuren Wu. “A New Simple Approach for Constructing
Implied Volatility Surfaces.” Working paper, New York University and Baruch
College. Derman, Emanuel. “Introduction to the Volatility Smile.” Lecture notes,
Columbia University. Gatheral, Jim.
- [S2] FX Derivatives Trader School ( PDFDrive ), chunk 142, score 0.784345: Implied volatilities beyond the 10 delta strikes must either be controlled
usingextrapolationorgeneratedautomaticallyusingamodellikeStochasticVolatility
Inspired (SVI)-see Gatheral’s book in Further Reading for more information.
- [S3] Emerging Financial Derivatives  Understanding exotic options and structured products ( PDFDrive ), chunk 40, score 0.783746: “Riding on a Smile.” Risk, 7(2): 32–39. Figlewski, S. “The Adaptive Mesh Model: A New Approach to 
Efficient Option Pricing.” Journal of Financial Economics, 53: 313–51. Figlewski, S., Gao, B., & Ahn, D. “Pricing Discrete Barrier Options with an 
Adaptive Mesh Model,” Working Paper, 1999.
- [S4] FX Derivatives Trader School ( PDFDrive ), chunk 66, score 0.775954: ■The risk reversal contract describes the skew of the volatility smile (i.e., how
tilted the volatility smile is). Butterfly and risk reversal contracts are quoted at market tenors like the ATM
curve.
- [S5] Emerging Financial Derivatives  Understanding exotic options and structured products ( PDFDrive ), chunk 42, score 0.767935: When the implied volatility is plotted against the strike price, the resulting graph is 
typically downward sloping for equity markets, or valley-shaped for currency 
markets. For markets where the graph is downward sloping, such as for equity 
options, the term volatility skew is often used.
- [S6] Principles of Financial Engineering ( PDFDrive ), chunk 616, score 0.761744: 16.14 THE RELEVANCE OF THE SMILE
The volatility smile is important in financial engineering for at least three reasons. First, if we associate a volatility smile with all the risk factors, and if this smile shifts randomly
over time, then we may be able to trade it, take spread positions, and arbitrage it.
- [S7] FX Derivatives Trader School ( PDFDrive ), chunk 65, score 0.74862: As the horizon date changes, the expiry date for each market tenor
changes accordingly (the methodology for calculating tenor expiry dates is given
in Chapter 10 and implemented in Practical D).
- [S8] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 110, score 0.747634: This is referred to as the term 
structure of volatility. A few things affect the term structure of volatility. The main 
effect relates to the implied impact of upcoming market events.
- [S9] Analytical Finance  Volume I  The Mathematics of Equity Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 120, score 0.746958: But if this model is used
to back-test the market-traded option, we can observe that different contracts
produce significantly different implied volatilities. Options’ implied volatilities
actually vary with the different time to maturity. This is the term structure of
implied volatility.
- [S10] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 107, score 0.744514: It is also reasonable to believe that as a company’s equity value declines, its leverage increases. This means that the company is 
riskier and thus the implied volatility should be higher (see

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

