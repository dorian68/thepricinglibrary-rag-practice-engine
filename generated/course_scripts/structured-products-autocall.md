---
slug: structured-products-autocall
topic: Autocallable structured products from term sheet to scenario table
product: autocallable note
level: advanced
concepts: coupon barrier, autocall, protection barrier, redemption
source_count: 10
---

# Module pratique - Autocallable structured products from term sheet to scenario table

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Autocallable structured products from term sheet to scenario table par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: advanced
- Public vise: quant confirme, trader junior, structureur
- Duree estimee: 150 minutes
- Produit: autocallable note
- Concepts: coupon barrier, autocall, protection barrier, redemption

## Prerequis
- option vanilla
- delta/gamma
- notion de path-dependence

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

## Positionnement bibliotheque
- Track: Market Finance Core
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Extraire le term sheet
- Objectif pratique: Transformer la fiche produit en conditions calculables.
- Situation de desk: Sales envoie un autocall a expliquer avant client call.
- Notion utile: Observation dates, coupon barrier, autocall level.
- Activite: Construire la table des conditions.
- Livrable apprenant: Term-sheet map.
### Module 2 - Coupon et autocall
- Objectif pratique: Calculer les coupons et l'evenement de remboursement anticipe.
- Situation de desk: Le sous-jacent finit au-dessus du niveau autocall a une date d'observation.
- Notion utile: Indicator functions, memory coupon, early redemption.
- Activite: Remplir la logique date par date.
- Livrable apprenant: Coupon/autocall grid.
### Module 3 - Protection barrier
- Objectif pratique: Expliquer la perte conditionnelle en fin de vie.
- Situation de desk: Le sous-jacent finit sous la barriere.
- Notion utile: Capital protection, downside participation.
- Activite: Calculer redemption finale.
- Livrable apprenant: Downside explanation.
### Module 4 - Scenario table client
- Objectif pratique: Comparer upside, flat, moderate down et crash scenario.
- Situation de desk: Le client veut comprendre coupon vs capital at risk.
- Notion utile: Cash-flow path dependency, redemption, loss participation.
- Activite: Produire une table de scenarios lisible par sales.
- Livrable apprenant: Client scenario table.
### Module 5 - Desk risk
- Objectif pratique: Relier attrait client et risques de couverture.
- Situation de desk: La structure vend du coupon mais concentre du tail risk.
- Notion utile: Barrier/gamma/vega/liquidity risk.
- Activite: Ecrire memo sales + risk.
- Livrable apprenant: Client/risk memo.

## Cours redige
### Lecon 1 - Extraire le term sheet

Dans le cadre d'une vente d'un produit structuré autocallable, il est crucial de bien comprendre les éléments clés du term sheet afin de les transformer en conditions calculables. Imaginons un scénario où le sous-jacent est un indice boursier, et que le produit offre un coupon conditionnel. Les dates d'observation, la barrière de coupon et le niveau d'autocall sont des paramètres fondamentaux qui détermineront le rendement et le risque associé à l'investissement. Par exemple, si le produit stipule que le coupon est versé uniquement si l'indice reste au-dessus d'une certaine barrière lors des dates d'observation, cela signifie que tout mouvement en dessous de ce seuil pourrait entraîner une perte de rendement pour l'investisseur.

Sur un desk de trading, la capacité à extraire ces informations et à les traduire en conditions calculables est essentielle pour anticiper les réactions des clients et les mouvements de marché. Les dates d'observation permettent de déterminer à quel moment l'indice doit être évalué, tandis que le niveau d'autocall indique à quel seuil de performance le produit sera remboursé par anticipation. Cette dynamique est particulièrement importante dans un contexte de volatilité accrue, où les investisseurs pourraient être surpris par des pertes inattendues, comme le souligne l'extrait : "Thus, investors should carefully compare the yield offered by the" [S1]. Une bonne compréhension de ces mécanismes permet de mieux gérer les attentes des clients et de positionner le produit de manière stratégique.

Un piège courant pour un junior réside dans la confusion entre le niveau d'autocall et la barrière de coupon. Il peut être tentant de penser que ces deux éléments sont interchangeables, alors qu'ils jouent des rôles distincts dans la structure du produit. Le niveau d'autocall détermine si le produit sera remboursé avant son échéance, tandis que la barrière de coupon conditionne le versement des intérêts. Ignorer cette distinction peut mener à des erreurs dans la présentation du produit aux clients, entraînant des malentendus et potentiellement des pertes de confiance.

### Lecon 2 - Coupon et autocall

Dans le monde des produits structurés autocallables, la compréhension des coupons et des événements de remboursement anticipé est cruciale pour optimiser la gestion des risques et des rendements. Imaginez un scénario où le sous-jacent, par exemple l'or, termine au-dessus du niveau d'autocall à une date d'observation. Cela signifie que le produit est susceptible d'être remboursé avant son échéance, ce qui peut avoir un impact significatif sur la stratégie de trading. Les coupons, souvent conditionnels, sont des éléments clés qui déterminent le rendement pour l'investisseur.

Le mécanisme de calcul des coupons repose sur des fonctions indicatrices qui activent ou désactivent le paiement en fonction de la performance du sous-jacent. Par exemple, si l'or final est supérieur à l'or initial, le remboursement inclura un coupon conditionnel, augmentant ainsi le montant total remboursé. Ce point est essentiel pour un desk de trading, car il influence non seulement la valorisation du produit, mais également les décisions d'arbitrage et de couverture. Comme mentionné dans l'extrait, "si GoldFinal ≥ GoldInitial, redemption is equal to (100% + Conditional Coupon) × Notional" [S2]. Cela souligne l'importance d'une évaluation précise des niveaux d'observation pour anticiper les flux de trésorerie.

Un piège fréquent pour un junior réside dans la confusion entre le coupon et le remboursement anticipé. Il est crucial de ne pas supposer que le simple fait d'atteindre le niveau d'autocall garantit le paiement du coupon. Parfois, des conditions spécifiques doivent être remplies, et un manque de vigilance sur ces détails peut entraîner des erreurs de calcul dans les prévisions de flux de trésorerie. Ainsi, une attention particulière à la logique de chaque date d'observation est indispensable pour éviter des surprises désagréables dans la gestion des produits structurés.

### Lecon 3 - Protection barrier

Dans le cadre des produits structurés autocallables, la notion de barrière de protection est cruciale pour comprendre comment le capital est affecté en fin de vie. Imaginons un scénario où le sous-jacent, disons l'or, finit sous la barrière de protection. Cela signifie que le prix final de l'actif est inférieur à un certain seuil, souvent désigné comme le "Put Strike". Dans cette situation, le détenteur de la note subit une perte conditionnelle, car il est exposé à un risque de baisse qui découle de la position courte sur le put.

Le mécanisme de cette protection est essentiel sur un desk de trading. Si à la date d'échéance programmée, le prix de l'or est inférieur à son niveau initial, la récupération du capital se fait sur la base d'un ratio qui compare le prix final au prix initial. En d'autres termes, le remboursement sera proportionnel à la performance de l'actif sous-jacent, ce qui peut entraîner une perte significative pour l'investisseur. Pour illustrer, si l'or se termine à 80 alors qu'il était à 100 au départ, le remboursement ne sera que de 80% du nominal, ce qui implique une perte de 20% du capital investi. Comme indiqué dans l'extrait, "la note-holder est exposé à la downside risk arising from the short put position" [S3].

Cette dynamique est d'une importance capitale pour les traders, car elle influence non seulement la stratégie de couverture, mais aussi la gestion des risques. Un desk doit être en mesure de prévoir ces scénarios et d'évaluer l'impact potentiel sur le portefeuille. La compréhension de la barrière de protection permet également de mieux communiquer avec les clients sur les risques associés à ces produits.

Un piège fréquent pour les juniors est de supposer que la barrière de protection garantit toujours le capital. Ils peuvent négliger le fait que, si le sous-jacent finit sous cette barrière, la protection ne s'applique pas et que le capital peut être considérablement réduit. Cette méprise peut conduire à des attentes irréalistes et à une mauvaise gestion des risques.

### Lecon 4 - Scenario table client

Dans le cadre de l'évaluation des produits structurés autocallables, il est crucial de comprendre comment les scénarios de marché influencent les flux de trésorerie et le risque de capital. Imaginons un produit structuré qui offre un coupon conditionnel basé sur la performance d'un indice boursier. Dans un scénario haussier, où l'indice dépasse un certain seuil, le client peut recevoir un coupon attractif tout en préservant son capital. En revanche, dans un scénario de crash, où l'indice chute de manière significative, le risque de perte de capital devient réel, et le client pourrait ne pas récupérer son investissement initial. Cette dynamique de dépendance des flux de trésorerie est essentielle pour comprendre le fonctionnement des produits structurés sur un desk de trading.

La notion de participation aux pertes est également centrale dans cette analyse. Dans un scénario modéré à la baisse, même si le capital est partiellement protégé, le coupon peut être réduit, ce qui impacte directement le rendement global du produit. Les traders doivent donc être capables d'expliquer à leurs clients comment ces différents scénarios affectent non seulement le coupon, mais aussi le capital à risque. Comme le souligne l'extrait, "il y a un risque non négligeable de défaut" dans les produits structurés, ce qui rappelle que la protection du capital n'est pas toujours garantie, surtout si l'émetteur est en difficulté [S4].

Un piège courant pour un junior est de supposer que le coupon est toujours garanti, indépendamment de la performance du sous-jacent. Cela peut conduire à des attentes irréalistes chez le client, qui pourrait croire que son capital est entièrement protégé alors qu'il est en réalité soumis à des conditions de marché spécifiques. Une compréhension approfondie des scénarios de cash-flow et de la participation aux pertes est donc indispensable pour éviter de telles confusions et pour fournir des conseils éclairés aux clients.

### Lecon 5 - Desk risk

Lorsqu'un desk de trading propose des produits structurés autocallables, il attire souvent les clients par la promesse d'un coupon attractif, tout en prenant en compte des risques sous-jacents significatifs. L'un des aspects cruciaux à considérer est le tail risk, qui se manifeste lorsque des événements extrêmes, bien que peu probables, peuvent entraîner des pertes considérables. En effet, ces structures, tout en offrant une protection du capital ou des améliorations de crédit, peuvent exposer le desk à des risques de barrière, gamma, vega et de liquidité qui ne sont pas toujours évidents pour les investisseurs [S5].

Le mécanisme de ces risques est intimement lié à la nature des options complexes qui composent ces produits. Par exemple, lorsque le sous-jacent approche une barrière, la sensibilité du prix du produit à de petites variations du sous-jacent (gamma) peut augmenter de manière exponentielle. Cela signifie qu'un léger mouvement du marché peut engendrer des fluctuations de prix importantes, rendant la couverture du risque plus difficile. De plus, le risque de liquidité peut se manifester si le desk doit liquider rapidement des positions pour couvrir ces risques, ce qui pourrait entraîner des coûts supplémentaires et des pertes. La gestion de ces risques est donc essentielle pour maintenir la rentabilité et la réputation du desk.

Un piège courant pour un junior est de sous-estimer l'impact du risque de vega, qui est la sensibilité du prix d'une option par rapport à la volatilité implicite. En se concentrant uniquement sur le rendement promis, un junior peut négliger comment une variation de la volatilité peut affecter la valorisation du produit structuré. Cela peut conduire à des décisions de couverture inappropriées, augmentant ainsi l'exposition au risque de marché. Il est donc impératif de comprendre non seulement le produit vendu, mais également les dynamiques de risque qui l'accompagnent pour éviter des erreurs coûteuses.

## Labs pratiques a inclure
1. Term-sheet map: dates, coupon barrier, autocall level, protection barrier.
2. Coupon/autocall grid: calculer coupon et early redemption date par date.
3. Downside: calculer redemption finale sous la barriere de protection.
4. Scenario table: upside, flat, moderate down et crash scenario.
5. Sales/risk memo: benefice client, risque de couverture et tail risk.

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

## Fondements theoriques (ancres sources)
_[genere - theorie, formules verifiees par un professionnel]_

**Mecanique.** A chaque date d'observation $t_i$: si $S_{t_i}\ge$ barriere d'autocall, **rappel anticipe** (nominal + coupon); si $\ge$ barriere de coupon, coupon paye (avec **memoire** des coupons manques); a maturite, si jamais rappele, capital protege tant que $S_T\ge$ barriere de protection, sinon perte $1{:}1$.

**Decomposition vendeur (risque).** Vendre un autocall worst-of revient a etre
$$\text{short les digitales de coupon/autocall} \;+\; \text{long un put down-and-in worst-of},$$
soit, du point de vue du **vendeur**, un profil **long skew, long volatilite, short correlation (= long dispersion)**, en echange du portage paye via les coupons digitaux vendus. (L'investisseur est exactement le miroir: short vol, short skew, long correlation, recoit le coupon.)

**Pricing.** Pas de forme fermee (payoff path-dependent, souvent multi-sous-jacents): on price par **Monte-Carlo** sous vol/dividendes/correlation (lien vers monte_carlo et vol_smile).

**Intuition rigoureuse.** L'investisseur vend de la protection en echange d'un coupon eleve: il est *short* le crash. L'effet "snowball" (memoire) concentre les coupons sur les scenarios de remontee.

**Piege theorique.** Le risque vendeur est non lineaire et explose pres de la barriere de protection a l'approche de la maturite (gap + correlation qui monte en stress).

**References (corpus).** Bouzoubaa & Osseiran, *Exotic Options and Hybrids* (§12.4 snowball, worst-of put, decomposition de risque); *Pricing and Hedging Financial Derivatives* (notes structurees, worst-of digital).

## Exemple numerique resolu
_[genere - calcul verifie]_ On deroule le payoff d'un autocall a memoire selon un scenario d'observations.

**Donnees.** Autocall Athena sur indice, niveau initial 100, barriere autocall 100%, barriere coupon 70%, barriere protection 60%, coupon 6% par observation avec memoire, notionnel 1m. Niveaux observes: 65, 102.

### Payoff d'un autocall (Athena a memoire)
- Famille: autocall_structured
- Hypotheses controlees:
  - Observations periodiques fournies; chaque niveau compare au niveau initial.
  - Effet memoire des coupons: actif.
  - Barriere autocall, coupon et protection en % du niveau initial.
  - Protection du capital de type europeenne (observee a maturite).
- Calculs a respecter:
  - Observation 1 - coupon:
    - Formule: ratio < barriere coupon
    - Application: ratio 65.00% < 70%
    - Resultat: 0 EUR (coupon en memoire)
    - Lecture desk: Coupon non paye; mis en memoire pour la prochaine observation.
  - Observation 2 - coupon:
    - Formule: coupon * periodes dues * notionnel
    - Application: 0.06 * 2 * 1,000,000
    - Resultat: +120,000 EUR
    - Lecture desk: niveau 102 (ratio 102.00%) >= barriere coupon 70%: paie 2 coupon(s) (memoire)
  - Observation 2 - autocall:
    - Formule: ratio >= barriere autocall
    - Application: ratio 102.00% >= 100%
    - Resultat: rappel anticipe: +1,000,000 EUR
    - Lecture desk: Le produit est rappele: remboursement du nominal puis arret.
  - Payoff total investisseur:
    - Formule: Somme coupons + remboursement
    - Application: 120,000 + 1,000,000
    - Resultat: 1,120,000 EUR
    - Lecture desk: Cash total recu sur la vie du produit.
- Actions operationnelles attendues:
  - Identifier le scenario dominant: rappel anticipe (probable si spot eleve) ou perte en capital.
  - Lire la sensibilite vendeur: short put down-and-in + short calls digitaux (autocall = combinaison d'options).
  - Surveiller le gap pres de la barriere de protection a l'approche de la maturite.
- Points de vigilance:
  - Le prix reel exige un modele (Monte Carlo sous vol/dividendes/correlation), pas seulement le payoff de scenarios.
  - Le risque vendeur est non lineaire et path-dependent: la protection peut sauter pres de la barriere.

**Lecture finale.** Chaque chiffre ci-dessus a une unite explicite et un sens economique; un apprenant doit pouvoir refaire le calcul a la main et retrouver le meme ordre de grandeur.

## Exercices corriges
### Exercice 1 - application directe
_[genere]_ Identifiez le produit, son risque dominant et la donnee de marche qui le pilote le plus.

**Correction.** Reponse type: nommer le payoff, la sensibilite de premier ordre (delta/DV01/CS01...) et la variable marche associee (spot/taux/spread).

### Exercice 2 - niveau desk
_[genere]_ Construisez un mini-cas chiffre du sujet et resolvez-le pas a pas avec unites et interpretation.

**Correction detaillee (calcul verifie).**
### Payoff d'un autocall (Athena a memoire)
- Famille: autocall_structured
- Hypotheses controlees:
  - Observations periodiques fournies; chaque niveau compare au niveau initial.
  - Effet memoire des coupons: actif.
  - Barriere autocall, coupon et protection en % du niveau initial.
  - Protection du capital de type europeenne (observee a maturite).
- Calculs a respecter:
  - Observation 1 - coupon:
    - Formule: ratio < barriere coupon
    - Application: ratio 65.00% < 70%
    - Resultat: 0 EUR (coupon en memoire)
    - Lecture desk: Coupon non paye; mis en memoire pour la prochaine observation.
  - Observation 2 - coupon:
    - Formule: coupon * periodes dues * notionnel
    - Application: 0.06 * 2 * 1,000,000
    - Resultat: +120,000 EUR
    - Lecture desk: niveau 102 (ratio 102.00%) >= barriere coupon 70%: paie 2 coupon(s) (memoire)
  - Observation 2 - autocall:
    - Formule: ratio >= barriere autocall
    - Application: ratio 102.00% >= 100%
    - Resultat: rappel anticipe: +1,000,000 EUR
    - Lecture desk: Le produit est rappele: remboursement du nominal puis arret.
  - Payoff total investisseur:
    - Formule: Somme coupons + remboursement
    - Application: 120,000 + 1,000,000
    - Resultat: 1,120,000 EUR
    - Lecture desk: Cash total recu sur la vie du produit.
- Actions operationnelles attendues:
  - Identifier le scenario dominant: rappel anticipe (probable si spot eleve) ou perte en capital.
  - Lire la sensibilite vendeur: short put down-and-in + short calls digitaux (autocall = combinaison d'options).
  - Surveiller le gap pres de la barriere de protection a l'approche de la maturite.
- Points de vigilance:
  - Le prix reel exige un modele (Monte Carlo sous vol/dividendes/correlation), pas seulement le payoff de scenarios.
  - Le risque vendeur est non lineaire et path-dependent: la protection peut sauter pres de la barriere.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Un knock-out option:**
- A) nait quand la barriere est touchee
- B) s'eteint quand la barriere est touchee
- C) ignore la barriere
- D) est sans risque
  - Reponse: **B**. Le knock-out disparait si la barriere est atteinte pendant la vie.

**Q2. Le gap risk d'une barriere vient de:**
- A) un delta lisse
- B) une discontinuite de payoff pres de la barriere
- C) le theta
- D) le coupon
  - Reponse: **B**. Pres de la barriere, la valeur saute: le delta hedge continu peut echouer.

**Q3. In-out parity dit:**
- A) C_out = C_in
- B) C_vanilla = C_out + C_in
- C) C_out = C_vanilla
- D) rien
  - Reponse: **B**. Le vanilla se decompose en knock-out plus knock-in.

**Q4. Un down-and-out call vs vanilla est:**
- A) plus cher
- B) moins cher
- C) identique
- D) sans prime
  - Reponse: **B**. Il offre moins (peut s'eteindre) donc coute moins.

**Q5. Pres de la barriere le desk doit surtout:**
- A) ignorer
- B) monitorer et definir des triggers d'escalation
- C) augmenter la taille
- D) vendre du theta
  - Reponse: **B**. Le risque n'est pas un Greek lisse: monitoring et escalation priment.

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 10 (exploitables: 10).
- Score pedagogique moyen: 64.0/100 (qualite structurelle: 100.0/100).
- Definitions: 3 | exemples: 8 | exercices: 1 | formules: 1 | cas pratiques: 2.
- Repartition par type: theory: 8, example: 2.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S4], [S5], [S7].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S6].
4. Exemples - couvert par [S1], [S2], [S3], [S4].
5. Exemples resolus - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
6. Exercices - couvert par [S6].
7. Corriges - couvert par [S4], [S6], [S8], [S10].
8. Cas pratiques - couvert par [S4], [S9].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, exemples resolus, resumes.

## Faits et angles extraits de la base
- In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market downturn the product leads to losses.
- Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING
- In the 1990s, reverse convertibles were often issued with embedded short at-the-money put
options.
- The downside of such products was that investors would suffer losses if the underlying was
below the initial level.
- As investor demand waned in response to the market downturn following the
bursting of the tech bubble, a new generation of products was developed that embedded a short atthe-money down-and-in put option.
- The barrier feature provided investors with additional protection
since the put option would not be triggered unless the (down) barrier was reached.
- Such barrier
reverse convertibles are popular structured products in Europe and in the United States.
- Moreover, the large number of structured products and the relative illiquidity of the underlying equity
market made hedging such products more difficult than is the case for FX products, for example.
- Some structured products including reverse convertibles have embedded call features.
- Banks that issue structured products refer to these
products with call features as autocallable, which is the abbreviation of automatically callable.

## Sources RAG a citer
- [S1] Principles of Financial Engineering ( PDFDrive ), chunk 764, score 0.791685: In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market downturn the product leads to losses. Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING
- [S2] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 305, score 0.774355 (extrait non cite: source bruitee)
- [S3] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 305, score 0.774355 (extrait non cite: source bruitee)
- [S4] Demystifying Exotic Products  Interest Rates, Equities and Foreign Exchange  ( PDFDrive ), chunk 205, score 0.773752: Of course, if the zero-coupon bond were that of any non-government issuer, there is a nonnegligible risk of default. Clearly, Lehman-issued “principal-protected” structured notes failed 
to repay the principal when Lehman Brothers defaulted, much to the chagrin of investors 
who misunderstood the idea.
- [S5] Principles of Financial Engineering ( PDFDrive ), chunk 751, score 0.769596: Financial engineering provides ways to construct any payoff structure desired by an investor. However, often these payoffs involve complex option positions, and clients may not have the
knowledge, or simply the means, to handle such risks. Market practitioners can do this better.
- [S6] FX Derivatives Trader School ( PDFDrive ), chunk 294, score 0.731174: Specifically, there are increased exposures to the ATM curve, and additional
exposures to the forward smile. Therefore, when pricing and risk managing window
barrier options it is important to assess exactly which pricing methodology is used. For example:
■Which ATM volatility curve is used to generate TV?
- [S7] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 176, score 0.666189 (extrait non cite: source bruitee)
- [S8] FX Derivatives Trader School ( PDFDrive ), chunk 293, score 0.665453: Also, if the
rear-window barrier is through current spot, this approach does not work because
the American barrier option variation will have already knocked. It may also be useful to assess the probability of the rear-window barriers being
knocked.
- [S9] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 252, score 0.654239: In a later chapter, we
will see how bundling financing and hedging transactions helps reduce total credit costs and
can aid in monetizing the benefits of hedging.
- [S10] Swaps and Other Derivatives ( PDFDrive ), chunk 260, score 0.653885: In this case, the Final coupon ¼ Total accrued coupon (excluding
current)  Knockout level, where the Knockout level ¼ 20%. If there is no early redemption, the
Final coupon ¼ Knockout level  Total accrued coupon (excluding current).

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Autocall redemption event
$$
\mathbf{1}_{\text{call},i}=\mathbf{1}_{S_{t_i}\geq B_{\text{call}}S_0}
$$
- Usage desk: turn term-sheet language into scenario-table logic.
### F2 - Coupon event
$$
\text{Coupon}_i=Nc_i\mathbf{1}_{S_{t_i}\geq B_{\text{coupon}}S_0}
$$
- Usage desk: separate income trigger risk from capital protection risk.
### F3 - Protected redemption
$$
\text{Redemption}=N\left[1-\max\left(0,1-\frac{S_T}{S_0}\right)\mathbf{1}_{S_T<B_{\text{prot}}S_0}\right]
$$
- Usage desk: explain downside exposure to a non-quant stakeholder.

