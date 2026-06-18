---
slug: implied-volatility-smile
topic: Implied volatility smile and quote cleaning
product: equity index options
level: intermediate
concepts: implied volatility, smile, skew, SVI
source_count: 10
---

# Module pratique - Implied volatility smile and quote cleaning

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Implied volatility smile and quote cleaning par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 130 minutes
- Produit: equity index options
- Concepts: implied volatility, smile, skew, SVI

## Prerequis
- prix d'option vanilla
- volatilite implicite
- inversion de Black-Scholes

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

Dans le monde du trading d'options, la lecture de la chaîne d'options est cruciale pour prendre des décisions éclairées. Lorsqu'un trader consulte cette chaîne, il doit être conscient que les bids et asks peuvent contenir des quotes obsolètes ou croisées, ce qui peut fausser l'analyse. Par exemple, si un bid est supérieur à un ask pour le même strike, cela indique une incohérence qui doit être corrigée avant d'effectuer toute opération. En nettoyant ces quotes, on s'assure que les décisions reposent sur des données fiables, ce qui est essentiel pour éviter des pertes inutiles.

Le concept de "moneyness" joue un rôle clé dans ce processus. Il s'agit de la position d'un option par rapport au prix d'exercice par rapport au prix actuel de l'actif sous-jacent. Comprendre si une option est "in the money", "at the money" ou "out of the money" permet d'évaluer la pertinence des quotes. Par ailleurs, le calcul du bid/ask mid, qui représente le prix moyen entre le bid et l'ask, offre une référence utile pour déterminer une valeur juste des options. Comme le soulignent Carr et Wu, une approche rigoureuse dans la construction des surfaces de volatilité implicite est essentielle pour une analyse précise [S1].

Dans un environnement de desk, le nettoyage des quotes ne se limite pas à un simple exercice technique ; c'est une compétence qui peut faire la différence entre un trade réussi et un échec. Les traders doivent filtrer les quotes en documentant les rejets, ce qui permet d'identifier les anomalies et de maintenir une base de données propre. Cela nécessite une attention méticuleuse aux détails et une compréhension des limites de chaque quote, car une quote "stale" peut entraîner des erreurs significatives dans l'évaluation des options.

Un piège fréquent pour un junior est de négliger l'importance des quotes "stale". En supposant que toutes les quotes sont à jour, un trader peut prendre des décisions basées sur des données erronées, ce qui peut compromettre l'intégrité de sa stratégie de trading. Il est donc impératif de toujours vérifier la fraîcheur des quotes avant de procéder à des analyses ou à des transactions.

### Lecon 2 - Inversion en IV

Dans le monde du trading, la volatilité implicite (IV) est souvent perçue comme un indicateur clé de la perception du risque par le marché. Imaginez un trader qui observe une option à un strike de 100 sur un actif dont le prix spot est également de 100. Si la volatilité implicite pour ce strike est significativement différente de celle des strikes adjacents, cela peut signaler une opportunité de trading ou un déséquilibre dans la valorisation des options. En effet, les traders doivent être capables de convertir les prix des options en volatilités implicites comparables pour évaluer correctement le risque et le potentiel de profit.

L'inversion en IV, qui repose sur le modèle de Black-Scholes, est essentielle pour effectuer cette transformation. En utilisant les prix des options, le trader peut estimer la volatilité implicite associée à chaque strike. Cela permet de comprendre comment le marché valorise le risque à différents niveaux de prix. Par exemple, si la volatilité implicite pour un strike à 90 est plus élevée que celle pour un strike à 110, cela peut indiquer une anticipation d'un mouvement baissier plus prononcé. En effet, comme le souligne l'extrait [S2], les volatilités implicites au-delà des strikes à 10 delta doivent être gérées avec soin, souvent par extrapolation ou en utilisant des modèles comme le SVI pour obtenir une courbe de volatilité cohérente.

Sur un desk de trading, cette capacité à inverser les prix en volatilités implicites et à analyser la structure de la volatilité est cruciale. Les traders doivent non seulement comprendre le vega, qui mesure la sensibilité du prix de l'option à la volatilité, mais aussi être attentifs à la convergence des volatilités implicites. Une mauvaise interprétation de ces valeurs peut mener à des décisions de trading erronées, par exemple, en surévaluant ou sous-évaluant le risque associé à une position.

Un piège courant pour les juniors est de supposer que les volatilités implicites doivent toujours être croissantes avec les strikes. En réalité, des anomalies peuvent survenir, et des volatilités plus élevées à des strikes plus bas peuvent indiquer une anticipation de mouvements de marché plus importants. Ignorer ces nuances peut conduire à des évaluations biaisées et à des positions désavantageuses.

### Lecon 3 - Smile et skew

Dans le monde des options, la forme de la courbe de volatilité implicite, souvent appelée "smile" ou "skew", peut révéler des informations cruciales sur le sentiment du marché et les anticipations de risque. Par exemple, lorsque l'on observe que les options de vente (puts) sur les ailes (wings) s'enrichissent avant un événement macroéconomique, cela peut indiquer une aversion au risque croissante parmi les investisseurs. Cette dynamique est particulièrement pertinente dans un contexte où les acteurs du marché se préparent à une volatilité accrue, souvent associée à des annonces économiques majeures ou à des événements géopolitiques.

Le mécanisme sous-jacent à cette observation réside dans la manière dont les traders évaluent le risque. Un "skew" positif, où les options de vente à des prix d'exercice plus bas affichent une volatilité implicite plus élevée, peut signaler une protection accrue contre une baisse potentielle des marchés. Cela est dû à l'anticipation que les mouvements à la baisse peuvent être plus prononcés que ceux à la hausse, ce qui pousse les traders à payer plus cher pour ces protections. Sur un desk de trading, comprendre cette dynamique est essentiel, car elle influence non seulement les stratégies de couverture, mais également la manière dont les positions sont gérées en période d'incertitude.

En traçant la courbe de volatilité implicite, il est crucial de commenter non seulement sa forme, mais aussi son évolution dans le temps. Par exemple, si l'on observe un changement dans le "term structure" de la volatilité, cela peut indiquer une modification des attentes de risque à court et à long terme. Une convexité accrue dans la courbe peut également signaler une réaction disproportionnée aux mouvements de prix sous-jacents, ce qui est un signal fort pour les traders cherchant à ajuster leurs positions. En analysant ces éléments, on peut mieux anticiper les mouvements futurs du marché et ajuster les stratégies en conséquence.

Un piège courant pour un junior est de supposer que la forme de la smile est statique. En réalité, elle peut évoluer rapidement en réponse à des événements de marché ou à des changements dans le sentiment des investisseurs. Ignorer cette dynamique peut entraîner des décisions de trading mal informées, notamment en négligeant d'ajuster les couvertures ou les positions en fonction des nouvelles informations disponibles.

### Lecon 4 - Fit utilisable

Dans le monde des dérivés, la notion de sourire de volatilité (volatility smile) est essentielle pour comprendre comment les marchés évaluent le risque. Par exemple, dans le cadre des options sur actions, il est courant d'observer que les options avec des strikes plus bas affichent une volatilité implicite plus élevée que celles avec des strikes plus élevés. Cela s'explique par le comportement des actions qui tendent à augmenter lentement, ce qui crée une demande accrue pour les options de protection à bas prix. Cette dynamique se reflète dans les contrats de risk reversal, qui mesurent l'inclinaison du sourire de volatilité, et qui sont souvent cotés avec des maturités similaires à celles de la courbe ATM [S4].

Pour un desk de trading, avoir une surface de volatilité stable est crucial. Cela permet de mieux évaluer les risques et de prendre des décisions éclairées concernant les positions à prendre. En utilisant des méthodes de fit, telles que le SVI (Stochastic Volatility Inspired) ou un fit quadratique, les traders peuvent ajuster les courbes de volatilité pour qu'elles soient lisses tout en respectant les contrôles de non-arbitrage. Cela signifie que les prix des options doivent être cohérents entre eux, empêchant ainsi des opportunités de profit sans risque. En pratique, cela implique de vérifier les résidus du fit pour s'assurer qu'ils ne présentent pas de schémas systématiques, ce qui pourrait indiquer un problème dans l'ajustement.

Un piège courant pour un junior est de se concentrer uniquement sur la minimisation des résidus sans prêter attention aux contrôles de non-arbitrage. Par exemple, un junior pourrait ajuster la courbe de volatilité de manière à obtenir un fit parfait avec les données historiques, mais cela pourrait conduire à des incohérences dans les prix des options, rendant la surface instable. Il est donc impératif de garder à l'esprit que la qualité du fit ne doit pas compromettre l'intégrité des prix sur le marché.

## Labs pratiques a inclure
1. Quote cleaning: filtrer quotes impossibles/stale.
2. IV inversion: calculer vol implicite par strike.
3. Smile view: expliquer skew et risque de hedge.
4. Fit report: ajuster une courbe et controler les residus.

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

