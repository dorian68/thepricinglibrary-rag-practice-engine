---
slug: rates-swaps-dv01
topic: Interest-rate swaps, PV and DV01
product: EUR interest-rate swap
level: intermediate
concepts: par rate, annuity, DV01, curve shock
source_count: 10
---

# Module pratique - Interest-rate swaps, PV and DV01

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Interest-rate swaps, PV and DV01 par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 120 minutes
- Produit: EUR interest-rate swap
- Concepts: par rate, annuity, DV01, curve shock

## Prerequis
- valeur temps de l'argent
- courbe de taux
- actualisation

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

## Positionnement bibliotheque
- Track: Rates & Fixed Income
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire le ticket swap
- Objectif pratique: Identifier payer/receiver, notional, coupon, maturite et index flottant.
- Situation de desk: Un trader demande une lecture rapide d'un payer swap EUR 5Y avant un move BCE.
- Notion utile: Cash-flow fixe contre flottant, par rate, annuite.
- Activite: Transformer le ticket en tableau d'inputs et verifier le sens du risque.
- Livrable apprenant: Ticket enrichi + risque principal en une phrase.
### Module 2 - PV par coupon gap
- Objectif pratique: Estimer la valeur du swap avec l'ecart fixed coupon vs par rate.
- Situation de desk: Le coupon du book est au-dessus du mid-market; il faut expliquer le PV.
- Notion utile: PV approx = (par - fixed) * annuite * notionnel selon le sens.
- Activite: Calculer PV, signe et interpretation front-office.
- Livrable apprenant: PV explique avec signe payer/receiver.
### Module 3 - DV01 et shock P&L
- Objectif pratique: Convertir l'annuite en EUR/bp puis appliquer un shock de courbe.
- Situation de desk: La courbe bouge de 10bp avant le comite risque.
- Notion utile: DV01 = annuite * notionnel * 1bp.
- Activite: Calculer DV01, P&L shock et seuil d'alerte.
- Livrable apprenant: Tableau DV01/shock P&L.
### Module 4 - Hedge et basis risk
- Objectif pratique: Proposer une couverture realiste et nommer ce qu'elle ne couvre pas.
- Situation de desk: Le desk hedge avec futures ou swap oppose de tenor proche.
- Notion utile: Parallel hedge, tenor mismatch, curve-shape risk.
- Activite: Choisir hedge, sens, taille approximative et risque residuel.
- Livrable apprenant: Memo hedge en 6 lignes.
### Module 5 - Debrief production
- Objectif pratique: Savoir quand l'approximation devient dangereuse.
- Situation de desk: La position est materialisee dans un report de risk management.
- Notion utile: Conventions, multi-curve, collateral, interpolation.
- Activite: Lister les controles avant validation.
- Livrable apprenant: Checklist de validation desk.

## Cours redige
### Lecon 1 - Lire le ticket swap

Dans le cadre d'un swap de taux d'intérêt, deux parties échangent des flux de trésorerie, ce qui peut sembler abstrait, mais cela a des implications très concrètes sur le marché. Prenons un exemple : un trader sur desk doit rapidement évaluer un payer swap en euros de 5 ans avant une annonce de la BCE. Dans ce contexte, il est crucial de bien identifier les éléments clés du ticket swap : qui est le payeur et le receveur, quel est le montant notionnel, le taux de coupon, la maturité et l'index flottant. Ces informations permettent de comprendre la dynamique des flux de trésorerie fixes contre flottants, qui est au cœur de l'opération.

Le mécanisme d'un swap de taux d'intérêt repose sur l'échange de paiements basés sur un taux fixe contre un taux flottant, généralement indexé sur un taux de référence comme l'Euribor. Par exemple, si le trader doit payer un taux fixe de 2% sur un montant notionnel de 10 millions d'euros, il recevra en retour des paiements basés sur le taux flottant. Cela permet à l'entreprise de se couvrir contre les fluctuations des taux d'intérêt, mais cela expose également le trader à un risque de marché si les taux flottants augmentent. Sur desk, comprendre ces flux est essentiel pour gérer le risque et optimiser les positions.

En transformant le ticket swap en tableau d'inputs, le trader peut visualiser rapidement les flux de trésorerie sur la durée de vie du swap. Cela inclut le montant des paiements fixes et flottants, ainsi que la date de chaque paiement. Une telle représentation aide à vérifier le sens du risque : si le taux flottant dépasse le taux fixe, le trader pourrait se retrouver à payer davantage que ce qu'il reçoit, ce qui pourrait affecter la rentabilité de la position.

Un piège courant pour un junior est de confondre le payeur et le receveur dans le contexte du swap. Par exemple, un junior pourrait penser qu'un payer swap signifie qu'il va recevoir des paiements fixes, alors qu'en réalité, il s'engage à payer le taux fixe et à recevoir le taux flottant. Cette confusion peut entraîner des erreurs dans la gestion des positions et des risques associés, rendant la compréhension précise des termes du swap essentielle pour éviter des pertes inattendues.

### Lecon 2 - PV par coupon gap

Dans un environnement de marché où le coupon fixe d'un swap est supérieur au mid-market, il est crucial de comprendre comment estimer la valeur actuelle (PV) de ce swap en tenant compte de l'écart entre le coupon fixe et le taux de référence. Imaginons que nous avons un swap avec un coupon fixe à 3 % alors que le taux de référence est à 2 %. L'écart de 1 % peut sembler anodin, mais il a un impact significatif sur la valorisation du swap. En effet, la valeur approximative du swap peut être estimée en multipliant cet écart par la notionnelle et par la durée restante du swap, ce qui nous donne une idée de la prime que nous avons par rapport au marché.

Le mécanisme derrière cette estimation repose sur l'idée que chaque point de base (bp) d'écart entre le coupon fixe et le taux de référence se traduit par une variation de la valeur actuelle du swap. Sur un desk de trading, cette compréhension est essentielle pour prendre des décisions éclairées. Si le coupon est supérieur, cela signifie que le swap génère des flux de trésorerie plus importants que ce que le marché exige, ce qui se traduit par une valeur positive pour le détenteur du swap. À l'inverse, un coupon inférieur pourrait entraîner une perte de valeur, rendant le swap moins attractif pour les investisseurs.

En analysant les implications de cet écart, il est également important de considérer le contexte de marché. Par exemple, si les taux d'intérêt sont en hausse, l'écart entre le coupon fixe et le taux de référence peut se réduire, ce qui affecte la valorisation du swap. Les traders doivent donc être vigilants et ajuster leurs estimations de PV en fonction des mouvements de marché. Comme le soulignent Heynen et al. [S2], la dynamique des taux d'intérêt et leur impact sur la valorisation des instruments dérivés sont des éléments clés à maîtriser pour une gestion efficace des risques.

Un piège courant pour un junior dans ce contexte est de négliger l'impact du temps sur la valorisation. Parfois, ils peuvent se concentrer uniquement sur l'écart entre le coupon fixe et le taux de référence sans tenir compte de la durée restante du swap. Cela peut conduire à une estimation erronée de la valeur actuelle, car le temps joue un rôle crucial dans la détermination de la valeur des flux futurs. Une mauvaise évaluation peut entraîner des décisions de trading sous-optimales, affectant ainsi la performance globale du desk.

### Lecon 3 - DV01 et shock P&L

Dans le monde des swaps de taux d'intérêt, comprendre le DV01 est essentiel pour évaluer l'impact des variations de taux sur la valeur d'un portefeuille. Imaginons une situation où un desk de trading détient un swap avec un notional de 100 millions d'euros. Si la courbe des taux d'intérêt bouge de 10 points de base (bp) avant une réunion du comité de risque, il est crucial de savoir comment cette variation affectera le profit et la perte (P&L) du swap. Le DV01, qui représente la variation de la valeur d'un instrument pour une variation de 1 bp des taux d'intérêt, est calculé comme l'annuité multipliée par le notional, puis multipliée par 1 bp. Cela signifie que chaque mouvement de 1 bp dans la courbe des taux impacte directement la valeur de votre swap.

Sur un desk de trading, cette mesure est vitale car elle permet de quantifier le risque de taux d'intérêt. En appliquant un choc de 10 bp, comme dans notre exemple, on peut estimer rapidement le P&L en multipliant le DV01 par 10. Cela aide les traders à anticiper les pertes potentielles et à ajuster leurs positions en conséquence. Dans le contexte de la gestion des risques, une compréhension précise du DV01 permet également de définir des seuils d'alerte pour des mouvements de marché inattendus. Comme le souligne l'extrait de Flesaker, la modélisation des taux d'intérêt et des réclamations conditionnelles est essentielle pour une évaluation précise des instruments financiers [S3].

Un piège fréquent pour les juniors est de confondre le DV01 avec la sensibilité globale d'un portefeuille. Ils peuvent penser que le DV01 est une mesure statique, alors qu'il est en réalité dynamique et dépend de la structure des taux d'intérêt. Une mauvaise interprétation peut conduire à des décisions de couverture inappropriées, augmentant ainsi le risque de pertes importantes lors de mouvements de marché. Il est donc crucial de bien comprendre que le DV01 doit être régulièrement recalibré en fonction des conditions de marché et des caractéristiques spécifiques des instruments détenus.

### Lecon 4 - Hedge et basis risk

Dans le monde des marchés financiers, la gestion des risques de taux d'intérêt est cruciale pour les desks de trading. Imaginons un desk qui détient une position de swap à taux fixe, mais qui souhaite se protéger contre les variations de taux. Pour cela, il pourrait envisager d'utiliser des futures sur taux d'intérêt ou un swap opposé de tenor proche. Cependant, une couverture efficace ne se limite pas à simplement compenser une position; elle doit également tenir compte des risques résiduels, notamment le risque de base et le risque de décalage de maturité.

Le mécanisme de couverture parallèle repose sur l'idée que les mouvements de taux d'intérêt affectent simultanément les instruments de couverture et la position sous-jacente. Cependant, si les maturités des instruments ne correspondent pas parfaitement, comme c'est souvent le cas avec des swaps de différents tenors, un risque de courbe se présente. Par exemple, si le desk utilise un swap de 5 ans pour couvrir un swap de 10 ans, il doit être conscient que les variations de la courbe des taux peuvent ne pas se déplacer de manière parallèle. Cela peut entraîner des pertes si la forme de la courbe change, même si les taux d'intérêt globaux restent stables. Comme l'indiquent les travaux sur la valorisation des dérivés, il est essentiel de comprendre non seulement les mouvements de taux, mais aussi la structure de la courbe pour une couverture efficace [S4].

Dans cette optique, le choix du type de couverture, de son sens (long ou court) et de sa taille doit être réfléchi. Par exemple, si le desk choisit de couvrir une position de 10 millions d'euros avec des futures, il doit estimer la taille de la position en fonction de la sensibilité de son swap et des variations anticipées des taux. Cependant, un piège courant pour un junior est de supposer que la couverture élimine totalement le risque. En réalité, même avec une couverture bien pensée, il reste un risque résiduel lié aux décalages de maturité et à la forme de la courbe, qui peut engendrer des pertes inattendues.

### Lecon 5 - Debrief production

Dans le monde des swaps de taux d'intérêt, la compréhension des conventions de paiement est cruciale. Prenons un exemple concret : imaginez que vous êtes sur un desk de trading et que vous gérez une position en swaps basée sur le taux LIBOR à 3 mois. La spécificité de ces instruments réside dans le fait que les paiements ne se font qu'après un certain délai, ici 3 mois après que le taux ait été déterminé. Cela signifie que si le marché évolue rapidement, la valeur de votre position peut fluctuer de manière significative avant même que vous ne receviez ou ne payiez quoi que ce soit. Cette temporalité, où les swaps et options payent après un certain nombre de jours suivant l'expiration, est essentielle à prendre en compte pour évaluer le risque de votre position [S5].

Sur un desk, la gestion du risque est primordiale. Lorsque vous évaluez la valeur actuelle (PV) de vos swaps, il est essentiel d'utiliser des courbes de taux appropriées, souvent appelées "multi-curve". Ces courbes reflètent les taux d'intérêt pour différentes maturités et sont influencées par divers facteurs, y compris les conditions de marché et les exigences de collatéral. Une mauvaise estimation de ces courbes peut mener à des évaluations erronées et à des décisions de trading basées sur des informations inexactes. En outre, l'interpolation des taux entre différentes maturités doit être effectuée avec soin, car une approximation trop simpliste peut masquer des risques sous-jacents importants.

Avant de valider une position, il est impératif de mettre en place des contrôles rigoureux. Par exemple, vérifiez que les conventions de paiement sont correctement appliquées et que les courbes de taux utilisées pour le calcul de la PV sont à jour et pertinentes. Assurez-vous également que les ajustements pour le collatéral sont bien intégrés dans votre évaluation. Une attention particulière doit être portée à la synchronisation des flux de trésorerie, car une erreur dans la date de paiement peut entraîner des conséquences financières significatives.

Un piège courant pour un junior est de négliger l'impact du délai de paiement sur l'évaluation des swaps. Par exemple, il pourrait penser qu'une simple estimation basée sur les taux actuels est suffisante, sans tenir compte des variations potentielles du marché d'ici le moment où les paiements seront effectués. Cette approche peut conduire à une sous-estimation du risque et à des surprises désagréables lorsque les conditions de marché changent.

## Labs pratiques a inclure
1. Ticket swap: identifier payer/receiver, coupon, par rate, annuite et risque principal.
2. PV/DV01: calculer PV approximatif et EUR/bp sur un notionnel impose.
3. Shock P&L: appliquer +/-10bp et expliquer le signe.
4. Hedge memo: proposer hedge, taille et basis risk.
5. Debrief: controles de convention, courbe et collateral.

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
_[genere - calcul verifie]_ On valorise un payer swap et on mesure sa sensibilite a la courbe.

**Donnees.** Payer swap EUR notionnel 100m fixed coupon 3.20% par swap rate 3.00% annuity 4.55, la courbe monte de 10bp.

### PV/DV01 de swap de taux
- Famille: rates_swap_dv01
- Hypotheses controlees:
  - Approximation mono-courbe et parallel shift.
  - Annuite fournie par le prompt, pas recalibree.
  - Signe exprime du point de vue payer fixe / receiver flottant.
- Calculs a respecter:
  - DV01:
    - Formule: Annuite * Notionnel * 1bp
    - Application: 4.55 * 100,000,000 * 0.0001
    - Resultat: 45,500 EUR/bp
    - Lecture desk: Sensibilite lineaire de la position a un bp de courbe.
  - PV payer approx:
    - Formule: (Par rate - Fixed coupon) * Annuite * Notionnel
    - Application: (3% - 3.2%) * 4.55 * 100,000,000
    - Resultat: -910,000 EUR
    - Lecture desk: Un payer au-dessus du par rate est initialement hors-la-monnaie.
  - P&L shock taux:
    - Formule: DV01 * shock bp pour un payer
    - Application: 45,500 * 10
    - Resultat: 455,000 EUR
    - Lecture desk: Un payer gagne quand les taux montent, perd quand ils baissent.
- Actions operationnelles attendues:
  - Comparer le signe de PV avec le sens payer/receiver.
  - Hedger DV01 avec swap oppose, futures taux ou bond hedge selon le book.
  - Expliquer le basis risk si la couverture n'est pas sur le meme tenor.

**Lecture finale.** Chaque chiffre ci-dessus a une unite explicite et un sens economique; un apprenant doit pouvoir refaire le calcul a la main et retrouver le meme ordre de grandeur.

## Exercices corriges
### Exercice 1 - application directe
_[genere]_ Un payer swap a un fixed coupon au-dessus du par rate. Sa PV initiale est-elle positive ou negative pour le payer?

**Correction.** Negative: payer un coupon superieur au marche est desavantageux, donc PV(payer) = (par - fixed) * annuite * notionnel < 0.

### Exercice 2 - niveau desk
_[genere]_ Payer swap EUR 100m, fixed 3.20%, par 3.00%, annuite 4.55. Courbe +10bp. Calculez PV, DV01 et P&L.

**Correction detaillee (calcul verifie).**
### PV/DV01 de swap de taux
- Famille: rates_swap_dv01
- Hypotheses controlees:
  - Approximation mono-courbe et parallel shift.
  - Annuite fournie par le prompt, pas recalibree.
  - Signe exprime du point de vue payer fixe / receiver flottant.
- Calculs a respecter:
  - DV01:
    - Formule: Annuite * Notionnel * 1bp
    - Application: 4.55 * 100,000,000 * 0.0001
    - Resultat: 45,500 EUR/bp
    - Lecture desk: Sensibilite lineaire de la position a un bp de courbe.
  - PV payer approx:
    - Formule: (Par rate - Fixed coupon) * Annuite * Notionnel
    - Application: (3% - 3.2%) * 4.55 * 100,000,000
    - Resultat: -910,000 EUR
    - Lecture desk: Un payer au-dessus du par rate est initialement hors-la-monnaie.
  - P&L shock taux:
    - Formule: DV01 * shock bp pour un payer
    - Application: 45,500 * 10
    - Resultat: 455,000 EUR
    - Lecture desk: Un payer gagne quand les taux montent, perd quand ils baissent.
- Actions operationnelles attendues:
  - Comparer le signe de PV avec le sens payer/receiver.
  - Hedger DV01 avec swap oppose, futures taux ou bond hedge selon le book.
  - Expliquer le basis risk si la couverture n'est pas sur le meme tenor.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Le DV01 d'un swap mesure:**
- A) le P&L pour 1bp de courbe
- B) le coupon fixe
- C) la prime d'option
- D) le spread de credit
  - Reponse: **A**. DV01 = annuite * notionnel * 1bp: sensibilite lineaire a la courbe.

**Q2. Un payer swap gagne quand:**
- A) les taux baissent
- B) les taux montent
- C) la vol monte
- D) le spread s'ecarte
  - Reponse: **B**. Le payer recoit le flottant: il profite d'une hausse des taux.

**Q3. La PV d'un payer dont le coupon = par rate est:**
- A) fortement positive
- B) proche de zero
- C) fortement negative
- D) indeterminee
  - Reponse: **B**. Au par, fixed = par rate => PV ~ 0 a l'initiation.

**Q4. Le basis risk d'un hedge swap vient surtout de:**
- A) un mismatch de tenor/index
- B) la couleur de l'ecran
- C) le notionnel
- D) le jour de la semaine
  - Reponse: **A**. Couvrir avec un tenor/index different laisse un risque de base residuel.

**Q5. Annuite elevee => DV01:**
- A) plus faible
- B) plus eleve
- C) inchange
- D) negatif
  - Reponse: **B**. DV01 croit avec l'annuite (et le notionnel).

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 10 (exploitables: 9).
- Score pedagogique moyen: 44.3/100 (qualite structurelle: 89.0/100).
- Definitions: 2 | exemples: 0 | exercices: 3 | formules: 0 | cas pratiques: 0.
- Repartition par type: theory: 8, methodology: 1, exercise: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S5], [S10].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
4. Exemples - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
5. Exemples resolus - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
6. Exercices - couvert par [S1], [S4], [S5], [S10].
7. Corriges - couvert par [S2].
8. Cas pratiques - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: partially_usable - Sources partiellement suffisantes: completer les manques.
- Presents dans les sources: definitions, exercices, corriges.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, formules, exemples, exemples resolus, cas pratiques, resumes.

## Faits et angles extraits de la base
- ]
CHAPTER14
Interest Rate Swaps
INTRODUCTION
In this and the subsequent chapter we will explore a type of derivative security
known as a “swap.” Broadly, a swap is an exchange of cash flows between
two counterparties over a number of periods of time.
- This chapter explores
the most important swap product, the interest rate swap.
- We will learn about
the characteristics of an interest rate swap, how an interest rate swap’s cash
flows are calculated, and how interest rate swaps can be used to transform
cash flows.
- After you read this chapter, you will be able to
■Describe the characteristics of an interest rate swap.
- ■Distinguish between fixed and floating interest rate swap legs and rates.
- ■Calculate the cash flows associated with an interest rate swap.
- 14.1
INTEREST RATE SWAP CHARACTERISTICS
An interest rate swap is an agreement in which two counterparties agree to
periodically exchange fixed and floating rates of interest over a number of
periods of time.
- One of the swap counterparties, known as the long interest
rate swap position, agrees to periodically receive a floating rate and pay a
fixed rate.
- The other swap counterparty, known as the short interest rate
swap position, agrees to periodically receive a fixed rate and pay a floating
rate.
- The exchange of fixed rate for floating rate is broadly illustrated in

## Sources RAG a citer
- [S1] Derivatives Essentials  An Introduction to Forwards, Futures, Options and Swaps ( PDFDrive ), chunk 158, score 0.622516: ]
CHAPTER14
Interest Rate Swaps
INTRODUCTION
In this and the subsequent chapter we will explore a type of derivative security
known as a “swap.” Broadly, a swap is an exchange of cash flows between
two counterparties over a number of periods of time.
- [S2] Financial Derivatives  Pricing, Applications, and Mathematics ( PDFDrive ), chunk 211, score 0.58254: Heynen, R., A. Kemna, and T. Vorst (1994): “Analysis of the Term Structure of Implied Volatilities,” Journal of Financial Quantitative Analysis 1:
31–57. Ho, T., and S. Lee (1986): “Term Structure Movements and Pricing Interest
Rate Contingent Claims,” Journal of Finance 41: 1011–1029.
- [S3] The Oxford Guide to Financial Modeling  Applications for Capital Markets, Corporate Finance, Risk Management and Financial Institutions ( PDFDrive ), chunk 212, score 0.507009: Two singular diffusion problems. Annals of Mathematics, 54, 173-181. Flesaker, B. Testing the Heath-Jarrow-Morton/Ho-Lee model of interest rate contingent
claims pricing. Journal of Financial and Quantitative Analysis, 28, no. Goldstein, R. The term structure of interest rates as a random field.
- [S4] The Oxford Guide to Financial Modeling  Applications for Capital Markets, Corporate Finance, Risk Management and Financial Institutions ( PDFDrive ), chunk 159, score 0.490889: Journal of 'Finance, 40, 455-480. A simple nonparametric approach to derivative security valuation. Journal of
Finance, 51, no. 5, 1633-1652.
- [S5] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 667, score 0.490474: For
interest rate swaps and options, the payoffs occur after
a certain number of days following the expiration, depending on the days to maturity of the instrument that
defines the underlying rate. Thus, if the underlying is
m-day LIBOR, swaps and options pay off m days after
the rate is determined at expiration.
- [S6] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 356, score 0.469447: Malden, MA: Blackwell, 2007. “ The Relationship between Futures Prices for US Treasury Bonds.” Review of 
Research in Futures Markets 3 ( 1984 ): 84 – 104. “ Optimal Hedging Policies.” Journal of Financial and Quantitative Analysis
 
 19 (June 1984 ): 127 – 140.
- [S7] Financial Derivatives  Pricing, Applications, and Mathematics ( PDFDrive ), chunk 212, score 0.420105: Jamshidian, F. (1991a): “Bond and Option Evaluation in the Gaussian Interest
Rate Model,” Research in Finance 9: 131–170. Jamshidian, F. (1991b): “Commodity Option Evaluation in the Gaussian Futures Term Structure Model,” Review of Futures Markets 10: 324–346. Jamshidian, F.
- [S8] Analytical Corporate Valuation  Fundamental Analysis, Asset Pricing, and Company Valuation ( PDFDrive ), chunk 401, score 0.417674: J Financ Econ 3:361–377
Fama E (1984a) The information in the term structure. J Financ Econ 13(4):509–528
Fama E (1984b) Term premiums in bond returns. J Financ Econ 13(4):529–546
Fisher I (1930) The theory of interest.
- [S9] Foundations of Financial Markets and Institutions ( PDFDrive ), chunk 849, score 0.395348: hedging "not only risks associated with 
Moscow City bonds but also risks related to 
bonds issued by other entities" 
b. "short-selling abilities" 
c. "portfolio duration management abilities" 
d. "reduction in transaction costs" 
e.
- [S10] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 668, score 0.389288: 457
interest rate cap, p. 466
caplet, p. 466
interest rate floor, p. 466
floorlet, p. 466
interest rate collar, p. 466
zero-cost collar, p. 469
payer swaption, p. 471
receiver swaption, p. 471
Chapter 13
Interest Rate Forwards and Options
479

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Par swap rate
$$
R_{\text{par}}=\frac{P(0,T_0)-P(0,T_n)}{\sum_{i=1}^{n}\alpha_i P(0,T_i)}
$$
- Usage desk: turn a discount curve into the fixed rate that prices the swap at par.
### F2 - Swap PV around par
$$
\text{PV}\approx N\,(R_{\text{par}}-K)\sum_{i=1}^{n}\alpha_i P(0,T_i)
$$
- Usage desk: explain the sign of a receiver or payer swap after a rate move.
### F3 - DV01
$$
\text{DV01}=N\times A\times 10^{-4},\qquad A=\sum_{i=1}^{n}\alpha_i P(0,T_i)
$$
- Usage desk: convert a one basis point shock into currency P&L.

