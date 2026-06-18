---
slug: vanilla-options-quote
topic: Vanilla options desk quote
product: equity vanilla option
level: beginner
concepts: Black-Scholes, put-call parity, delta, vega
source_count: 10
---

# Module pratique - Vanilla options desk quote

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Vanilla options desk quote par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: beginner
- Public vise: etudiant L3/M1, candidat en finance de marche, developpeur front-office debutant
- Duree estimee: 90 minutes
- Produit: equity vanilla option
- Concepts: Black-Scholes, put-call parity, delta, vega

## Prerequis
- payoff d'une option
- actualisation
- loi normale
- notion de volatilite

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

Dans le monde des options, comprendre la notion de **moneyness** est essentiel pour évaluer correctement un call européen. Imaginons que vous ayez un sous-jacent dont le prix spot est à 100. Si le strike de l'option est fixé à 90, l'option est considérée comme "in the money", ce qui signifie qu'elle a une valeur intrinsèque. À l'inverse, si le strike est à 110, l'option est "out of the money" et n'a pas de valeur intrinsèque. Cette distinction est cruciale car elle influence directement la prime de l'option et, par conséquent, le prix que vous allez communiquer à votre client.

Dans un contexte de desk de trading, la demande d'un prix indicatif sur un call européen implique plusieurs inputs clés : le spot, le strike, la maturité, le taux d'intérêt, les dividendes et la volatilité implicite. Le **forward** est également un concept central ici, car il permet d'anticiper le prix futur du sous-jacent à la maturité de l'option. En effet, pour évaluer correctement la prime d'une option, il est nécessaire de prendre en compte le taux d'actualisation, qui permet de ramener les flux futurs à leur valeur actuelle. Cela fait appel à des conventions de maturité spécifiques, car les options peuvent avoir des dates d'échéance variées qui influencent leur valorisation.

En se basant sur l'extrait [S1], il est important de noter que la **vega** d'une option, qui mesure la sensibilité de la prime par rapport à la volatilité, atteint son pic à la maturité où la valeur temporelle est maximisée. Cela signifie que plus l'option a de temps avant son expiration, plus elle est sensible aux variations de la volatilité implicite. Cette compréhension est fondamentale pour un junior sur le desk, car elle impacte la gestion des risques et la stratégie de pricing.

Un piège courant pour un junior est de négliger l'importance de la **maturité** dans l'évaluation des options. Par exemple, ils pourraient penser qu'un call avec un strike plus faible est toujours plus attractif, sans considérer que si la maturité est très courte, la prime pourrait être faible, même si l'option est "in the money". Cela peut conduire à des décisions de pricing erronées et à des opportunités manquées sur le marché.

### Lecon 2 - Prix Black-Scholes

Dans le monde des options, comprendre le prix Black-Scholes est essentiel pour établir des cotations défendables sur un desk. Imaginons un actif sous-jacent dont le prix spot est de 100. Les traders doivent évaluer à quel point une option d'achat (call) ou de vente (put) est précieuse, en tenant compte de divers facteurs comme la volatilité, le temps jusqu'à l'échéance et le rendement des dividendes. En effet, la formule de Black-Scholes repose sur des concepts clés tels que d1 et d2, qui représentent des probabilités ajustées par la volatilité et le temps, influençant directement le prix des options.

Le mécanisme de Black-Scholes permet de décomposer la valeur d'une option en deux composantes principales : la valeur intrinsèque et la valeur temps. La valeur intrinsèque correspond à la différence entre le prix du sous-jacent et le prix d'exercice, tandis que la valeur temps reflète le potentiel de gain futur de l'option. Sur un desk de trading, cette distinction est cruciale, car elle aide à déterminer si une option est sous-évaluée ou surévaluée par rapport à son prix de marché. Les traders doivent donc être capables de calculer ces valeurs rapidement et avec précision pour prendre des décisions éclairées.

L'extrait de Bachelier [S4] souligne l'importance historique de la modélisation des prix d'options, en se basant sur l'hypothèse d'une distribution normale des prix d'actifs. Cette approche a été fondatrice pour le développement de modèles modernes, comme celui de Black-Scholes, qui utilisent des distributions log-normales pour mieux refléter les comportements du marché. Ainsi, la capacité à évaluer correctement les options à l'aide de ces modèles est essentielle pour maintenir un avantage concurrentiel sur le marché.

Un piège courant pour un junior est de confondre la valeur intrinsèque et la valeur temps, en négligeant l'impact des dividendes. Par exemple, si un actif verse des dividendes, cela peut réduire la valeur d'un call, car le prix de l'actif pourrait baisser à cause des paiements de dividendes. Ignorer ce facteur peut mener à des évaluations erronées et à des décisions de trading désavantageuses.

### Lecon 3 - Controle put-call parity

Dans le monde des options, la relation entre les options d'achat (calls) et les options de vente (puts) est fondamentale pour assurer une cohérence dans les prix. Imaginons un scénario où vous observez un call mid à 10 et un put mid à 5, alors que le forward est à 95. À première vue, cela semble acceptable, mais en creusant un peu, vous devez vérifier si cette quote respecte la parité put-call. En effet, la différence entre le prix du call et celui du put doit correspondre à la différence entre le forward et le strike, tous deux actualisés. Si cette relation est rompue, cela indique une incohérence dans le marché qui pourrait vous coûter cher si elle n'est pas corrigée avant d'envoyer la quote.

Le mécanisme qui sous-tend cette parité est crucial pour un desk de trading. En tant que trader, vous devez comprendre que si le call est trop cher par rapport au put, cela peut signaler une opportunité d'arbitrage. Par exemple, si le call est surévalué, vous pourriez vendre ce call tout en achetant le put pour capturer la différence de prix. Cela vous permet de sécuriser un profit sans risque, car vous exploitez une inefficacité du marché. Comme mentionné dans l'extrait, la nature des options américaines, qui peuvent être exercées à tout moment, peut influencer leur prix par rapport aux options européennes, mais cela ne doit pas altérer la parité fondamentale que vous devez surveiller [S5].

Un piège courant pour un junior est de négliger l'importance de l'actualisation des valeurs. Parfois, un trader peut se concentrer uniquement sur les prix nominaux des options sans tenir compte des taux d'intérêt ou de la durée jusqu'à l'échéance, ce qui peut fausser son évaluation de la parité. En omettant de calculer correctement ces valeurs actualisées, vous risquez de transmettre une quote erronée, ce qui pourrait entraîner des pertes significatives pour votre desk.

### Lecon 4 - Greeks utiles au quote

Dans un environnement de trading, comprendre comment les options réagissent aux mouvements du marché est essentiel pour gérer le risque. Prenons l'exemple d'un trader qui reçoit une demande d'un client souhaitant augmenter la taille de sa position sur une option. Dans cette situation, le trader doit évaluer l'impact de cette augmentation sur le portefeuille, notamment en utilisant le delta et le vega. Le delta indique combien le prix de l'option devrait changer pour un mouvement d'un point dans le prix de l'actif sous-jacent, tandis que le vega mesure la sensibilité du prix de l'option aux variations de volatilité. Ces deux grecs sont cruciaux pour établir un hedge efficace.

Le mécanisme du delta hedge consiste à compenser les variations de prix de l'option en prenant une position opposée sur l'actif sous-jacent. Par exemple, si le delta de l'option est de 0,5, cela signifie que pour chaque mouvement de 1 point de l'actif sous-jacent, le prix de l'option variera de 0,5 point. Si le client augmente sa position, le trader doit ajuster le nombre d'actions à acheter ou à vendre pour maintenir une couverture neutre. En parallèle, le vega per vol point permet d'évaluer comment le prix de l'option changera si la volatilité augmente. Cela est particulièrement pertinent dans des marchés volatils, où une mauvaise évaluation peut entraîner des pertes significatives.

Dans la pratique, un trader doit donc non seulement surveiller le delta et le vega, mais aussi comprendre leur convention de signe. Par exemple, un delta positif indique que l'option est un call, tandis qu'un delta négatif indique un put. Cela influence directement la stratégie de couverture. Si le trader néglige de prendre en compte la convention de signe, il pourrait se retrouver à prendre une position qui aggrave le risque au lieu de le réduire.

Un piège courant pour un junior est de se concentrer uniquement sur le delta sans tenir compte du vega, surtout dans des marchés où la volatilité est en hausse. Ignorer la sensibilité à la volatilité peut mener à des couvertures incomplètes, exposant ainsi le portefeuille à des fluctuations imprévues. En somme, une compréhension intégrée des grecs est indispensable pour naviguer efficacement dans le monde des options.

## Labs pratiques a inclure
1. Quote ticket: spot, strike, maturite, taux, dividendes, vol et convention de taille.
2. Black-Scholes price: calculer call/put, intrinsic value et time value.
3. Parity check: mesurer le gap call-put-forward et conclure quote ou reject.
4. Greeks add-on: convertir delta et vega en hedge initial et risk comment.
5. Trader memo: prix, controles, hypotheses, action et limites.

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
- Chunks sources analyses: 10 (exploitables: 6).
- Score pedagogique moyen: 46.4/100 (qualite structurelle: 78.0/100).
- Definitions: 0 | exemples: 1 | exercices: 0 | formules: 2 | cas pratiques: 2.
- Repartition par type: theory: 8, methodology: 1, worked_example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
2. Intuitions - couvert par [S1], [S4], [S10].
3. Formules - couvert par [S4], [S7].
4. Exemples - couvert par [S10].
5. Exemples resolus - couvert par [S10].
6. Exercices - couvert par [S3], [S5], [S7].
7. Corriges - couvert par [S1], [S3], [S10].
8. Cas pratiques - couvert par [S1], [S3].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: partially_usable - Sources partiellement suffisantes: completer les manques.
- Presents dans les sources: intuitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): definitions, resumes.

## Faits et angles extraits de la base
- Intuitively,
vega increases at longer maturities because there is more time for a change in implied
volatility to impact the payoff.
- For a given vanilla option, peak vega (like gamma) occurs at the strike where
optionality and time value is maximized.
- Far away from the optionality the option
is either like a forward (if deep in-the-money) or like no position (if deep outof-the-money).
- In either of these cases, changing volatility has minimal impact on
option value.
- Intuitively this is because
higher volatility widens the distribution and therefore brings larger positive payoffs
into play, hence increasing the option value.
- Likewise, short vanilla options always
have short vega exposure.
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
- [S1] FX Derivatives Trader School ( PDFDrive ), chunk 58, score 0.661419: The peak vega on a vanilla option reduces over time. Intuitively,
vega increases at longer maturities because there is more time for a change in implied
volatility to impact the payoff. For a given vanilla option, peak vega (like gamma) occurs at the strike where
optionality and time value is maximized.
- [S2] FX Derivatives Trader School ( PDFDrive ), chunk 352, score 0.560978 (extrait non cite: source bruitee)
- [S3] Derivatives Markets ( PDFDrive ), chunk 523, score 0.53176 (extrait non cite: source bruitee)
- [S4] Derivatives Models on Models ( PDFDrive ), chunk 47, score 0.458098: Mathematical description of option valuation goes at least back more than
100 years to the now so famous Bachelier (1900) paper, that was based on his doctoral thesis
defended on March 19, 1900. Bachelier assumed a normal distribution for the asset price.
- [S5] FX Derivatives Trader School ( PDFDrive ), chunk 308, score 0.442157: American Vanilla Pricing and Greeks
Comparing American and European vanillas in the CCY1 call and higher CCY1
interest rates case demonstrates how early exercise impacts trading risk. Price
profiles are shown in Exhibit 27.9.
- [S6] FX Derivatives Trader School ( PDFDrive ), chunk 353, score 0.435645: CCY2 premium,
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
Currency blocks, 42
- [S7] Derivatives Markets ( PDFDrive ), chunk 504, score 0.387832 (extrait non cite: source bruitee)
- [S8] Advanced derivatives pricing and risk management  theory, tools and hands on programming application ( PDFDrive ), chunk 431, score 0.38685 (extrait non cite: source bruitee)
- [S9] Advanced Derivatives Pricing and Risk Management  Theory, Tools, and Hands On Programming Applications ( PDFDrive ), chunk 431, score 0.38685 (extrait non cite: source bruitee)
- [S10] FX Derivatives Trader School ( PDFDrive ), chunk 57, score 0.379498: Due to put–call parity, call and put options with the
same strike and maturity have the same gamma profile, shown in Exhibit 6.15. This
gamma can be calculated by taking the gradient of either the call option delta profile
from Exhibit 6.9 or the put option delta profile from Exhibit 6.11.

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

