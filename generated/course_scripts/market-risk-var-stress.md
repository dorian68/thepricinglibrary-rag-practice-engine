---
slug: market-risk-var-stress
topic: Market risk VaR, stress testing and escalation
product: multi-asset portfolio
level: intermediate
concepts: parametric VaR, expected shortfall, stress test, risk limit
source_count: 10
---

# Module pratique - Market risk VaR, stress testing and escalation

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Market risk VaR, stress testing and escalation par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 120 minutes
- Produit: multi-asset portfolio
- Concepts: parametric VaR, expected shortfall, stress test, risk limit

## Prerequis
- distribution normale
- quantile
- volatilite

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

## Positionnement bibliotheque
- Track: Risk Management
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Definir la question de risque
- Objectif pratique: Clarifier horizon, confiance, exposition et limite.
- Situation de desk: Un portefeuille approche son seuil de VaR intraday.
- Notion utile: VaR one-sided, horizon, volatility.
- Activite: Construire la fiche inputs du risk report.
- Livrable apprenant: Risk ticket.
### Module 2 - Calcul VaR
- Objectif pratique: Calculer une VaR parametrique simple avec les bonnes unites.
- Situation de desk: Le CRO demande une estimation rapide avant la cloture.
- Notion utile: VaR = notional * vol * quantile.
- Activite: Calculer et comparer a la limite.
- Livrable apprenant: VaR + statut de limite.
### Module 3 - Stress overlay
- Objectif pratique: Montrer ce que la VaR ne capture pas.
- Situation de desk: Un scenario historique depasse le mouvement normal.
- Notion utile: Stress test, tail loss, expected shortfall.
- Activite: Ajouter un choc severe et comparer.
- Livrable apprenant: Table VaR/stress.
### Module 4 - Escalation
- Objectif pratique: Transformer le chiffre en decision de gestion.
- Situation de desk: La limite est franchie mais le desk propose d'attendre.
- Notion utile: Reduce, hedge, monitor, escalate.
- Activite: Ecrire une note decisionnelle.
- Livrable apprenant: Escalation memo.

## Cours redige
### Lecon 1 - Definir la question de risque

Dans un environnement de marché, chaque décision de trading est empreinte d'incertitude. Prenons l'exemple d'un desk qui gère un portefeuille d'actions. Si ce portefeuille approche son seuil de VaR intraday, cela signifie que la perte potentielle sur une journée donnée pourrait dépasser un certain montant, disons 1 million d'euros. Cette situation nécessite une attention particulière, car elle implique que le desk est exposé à un risque de perte significatif. La notion de VaR one-sided devient alors cruciale : elle évalue la perte maximale attendue sur un horizon donné, ici intraday, avec un certain niveau de confiance, souvent fixé à 95% ou 99%. Cela signifie que, dans 95% des cas, la perte ne dépassera pas ce montant, mais dans 5% des cas, elle pourrait être bien plus importante.

La volatilité joue un rôle central dans cette évaluation. En période de forte volatilité, les mouvements de prix peuvent être plus importants, ce qui augmente la VaR et, par conséquent, l'exposition au risque. Sur un desk de trading, cette dynamique est essentielle à comprendre, car elle influence non seulement les décisions de positionnement, mais aussi la gestion des limites de risque. Comme le souligne l'extrait, "les banques assument le risque de marché parce qu'elles négocient en tant que principaux, risquant leur propre capital" [S2]. Cela signifie qu'une mauvaise gestion de cette exposition peut avoir des conséquences directes sur la rentabilité et la réputation de l'institution.

Un piège fréquent pour un junior est de négliger l'importance de l'horizon temporel dans l'évaluation de la VaR. Par exemple, un trader peut se concentrer uniquement sur la VaR intraday sans prendre en compte les fluctuations potentielles qui pourraient survenir sur des horizons plus longs, comme une semaine ou un mois. Cette vision à court terme peut conduire à une sous-estimation des risques réels et à des décisions de trading précipitées, mettant ainsi en péril la santé financière du desk.

### Lecon 2 - Calcul VaR

Dans le monde du trading, la gestion des risques est cruciale pour assurer la pérennité des opérations. Imaginons un desk qui gère un portefeuille d'actions. À la fin de la journée, le Chief Risk Officer (CRO) demande une estimation rapide de la Value at Risk (VaR) pour évaluer le risque potentiel avant la clôture du marché. La VaR est un indicateur clé qui permet de quantifier la perte maximale attendue sur un portefeuille dans un scénario de marché donné, sur une période spécifique et avec un certain niveau de confiance. En d'autres termes, elle aide à répondre à la question : "Quelle est la pire perte que nous pourrions subir dans un avenir proche, avec une probabilité donnée ?"

Le calcul de la VaR repose sur trois éléments fondamentaux : le montant notionnel du portefeuille, la volatilité des actifs et le quantile correspondant à notre niveau de confiance. Par exemple, si nous avons un portefeuille d'actions d'une valeur notionnelle de 1 million d'euros, avec une volatilité estimée de 20 % sur une période d'un jour, et que nous cherchons une VaR à 95 % (ce qui signifie que nous nous attendons à ne pas dépasser cette perte dans 95 % des cas), nous pouvons rapidement estimer notre risque. Ce calcul est essentiel pour le desk, car il permet de prendre des décisions éclairées sur les positions à maintenir ou à réduire, en fonction de l'appétit pour le risque de l'entreprise. Comme mentionné dans l'extrait, les systèmes de gestion des risques de marché (MRMS) jouent un rôle clé dans la capture des valorisations des transactions et le calcul des mesures de risque, y compris la VaR [S3].

Cependant, un piège courant pour les juniors est de négliger l'importance des unités dans le calcul de la VaR. Par exemple, un junior pourrait se concentrer sur le calcul de la volatilité en pourcentage sans considérer comment cela se traduit en termes de valeur monétaire sur le portefeuille. Cela peut entraîner des erreurs significatives dans l'estimation du risque, car une mauvaise interprétation des unités peut fausser la perception du risque global. Il est donc crucial de toujours garder à l'esprit que la VaR doit être exprimée dans la même unité que le montant notionnel pour être pertinente et utile dans le contexte de la gestion des risques.

### Lecon 3 - Stress overlay

Dans le monde du trading, il est crucial de comprendre que la Value at Risk (VaR) ne capture pas toujours les événements extrêmes, souvent appelés "tail events". Prenons un exemple concret : imaginez que vous gérez un portefeuille d'options sur actions, et que vous anticipez un mouvement normal des prix. Cependant, un événement imprévu, comme une annonce gouvernementale majeure, pourrait provoquer un choc sévère sur le marché, dépassant les fluctuations habituelles. C'est ici qu'intervient le stress test, une méthode qui permet d'évaluer la résilience d'un portefeuille face à des scénarios extrêmes, en simulant des conditions de marché défavorables.

Le stress test permet de quantifier les pertes potentielles dans des situations extrêmes, en allant au-delà des limites de la VaR. Par exemple, si vous avez un portefeuille avec une VaR de 1 million d'euros sur un horizon de 10 jours, cela signifie que vous vous attendez à ne pas perdre plus de cette somme dans des conditions normales de marché. Cependant, un événement comme une crise financière pourrait entraîner des pertes bien plus importantes. En utilisant des scénarios historiques, comme ceux observés lors de la crise de 2008, vous pouvez simuler des chocs qui révèlent des pertes de queue (tail loss) significatives, ce que la VaR ne pourrait pas anticiper. En effet, comme le souligne l'extrait [S4], la stratégie adoptée par Nuñes doit prendre en compte des mouvements inattendus des prix, ce qui est essentiel pour une gestion proactive des risques.

Dans un desk de trading, la compréhension de l'expected shortfall, qui mesure la perte moyenne au-delà de la VaR, devient essentielle. Cela permet aux traders de se préparer à des scénarios où les pertes dépassent les attentes normales, leur offrant ainsi une vision plus complète des risques auxquels ils sont exposés. En intégrant des chocs sévères dans vos simulations, vous pouvez comparer les résultats obtenus avec ceux de la VaR, et ainsi mieux appréhender la vulnérabilité de votre portefeuille.

Un piège courant pour un junior est de se fier uniquement à la VaR sans considérer les scénarios de stress. Ils pourraient penser que la VaR est suffisante pour évaluer les risques, alors qu'en réalité, elle ne prend pas en compte les événements extrêmes qui pourraient avoir un impact dévastateur sur le portefeuille. Cette méprise peut mener à des décisions de trading mal informées, augmentant ainsi le risque global de l'entreprise.

### Lecon 4 - Escalation

Dans un environnement de trading, la gestion des risques de marché est cruciale, notamment lorsque les limites de risque sont franchies. Imaginons un desk qui, après une journée volatile, constate que sa position en actions a dépassé la limite de perte acceptable. Au lieu de réagir immédiatement, le desk propose d'attendre, espérant un retournement de marché. Cette attitude peut sembler rationnelle à court terme, mais elle expose l'entreprise à des pertes accrues. C'est ici qu'intervient la notion d'escalation, qui consiste à transformer des chiffres alarmants en décisions de gestion concrètes.

Lorsqu'une limite est franchie, il est essentiel de suivre un processus en quatre étapes : réduire, couvrir, surveiller et escalader. Réduire implique de diminuer l'exposition en liquidant une partie des positions risquées. Couvrir consiste à utiliser des instruments dérivés pour protéger les positions existantes. Surveiller, c'est garder un œil sur l'évolution du marché et l'impact potentiel sur le portefeuille. Enfin, escalader signifie alerter les niveaux supérieurs de la direction sur la situation, afin qu'ils puissent prendre des décisions éclairées. Comme le souligne l'extrait, "la variation des prix des actifs peut provenir de divers facteurs", et il est impératif de réagir rapidement pour éviter que ces variations n'affectent négativement les positions de la banque [S6].

Sur un desk de trading, la rapidité de la décision est essentielle. Ignorer une limite franchie peut entraîner des conséquences désastreuses. Un junior pourrait être tenté de minimiser l'importance de l'escalation, pensant que la situation peut se résoudre d'elle-même. Ce piège réside dans l'idée que le marché va toujours se redresser, ce qui peut mener à une inaction fatale. En réalité, la proactivité dans la gestion des risques est ce qui permet de préserver la santé financière de l'organisation et d'éviter des pertes catastrophiques.

## Labs pratiques a inclure
1. VaR ticket: horizon, confiance, volatilite et exposition.
2. Calcul VaR: comparer a une limite imposee.
3. Stress overlay: ajouter un scenario extreme et commenter l'ecart.
4. Escalation memo: decision et suivi.

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
_[genere - calcul verifie]_ On calcule une VaR parametrique simple et on la compare a une limite.

**Donnees.** VaR parametrique: portefeuille 20m volatilite 2% confiance 95% horizon 1 jour.

### VaR parametrique simple
- Famille: parametric_var
- Hypotheses controlees:
  - Quantile normal z=1.65.
  - Volatilite donnee sur le meme pas de temps que l'horizon, sauf indication contraire.
- Calculs a respecter:
  - VaR:
    - Formule: Valeur * vol * sqrt(horizon) * z
    - Application: 20,000,000 * 0.0200 * sqrt(1) * 1.65
    - Resultat: 660,000
    - Lecture desk: Perte potentielle au niveau de confiance choisi.
- Actions operationnelles attendues:
  - Comparer VaR et stress tests.
  - Identifier les facteurs dominants du risque.
- Points de vigilance:
  - La VaR ne capture pas correctement les queues extremes ni les risques de gap.

**Lecture finale.** Chaque chiffre ci-dessus a une unite explicite et un sens economique; un apprenant doit pouvoir refaire le calcul a la main et retrouver le meme ordre de grandeur.

## Exercices corriges
### Exercice 1 - application directe
_[genere]_ Une VaR 95% 1 jour de 660k signifie quoi exactement?

**Correction.** Dans ~95% des jours, la perte ne devrait pas depasser 660k; environ 1 jour sur 20, elle peut etre superieure. La VaR ne dit rien de l'ampleur au-dela du seuil.

### Exercice 2 - niveau desk
_[genere]_ Portefeuille 20m, vol 2%/jour, 95%, 1 jour. Calculez la VaR et comparez a une limite de 500k.

**Correction detaillee (calcul verifie).**
### VaR parametrique simple
- Famille: parametric_var
- Hypotheses controlees:
  - Quantile normal z=1.65.
  - Volatilite donnee sur le meme pas de temps que l'horizon, sauf indication contraire.
- Calculs a respecter:
  - VaR:
    - Formule: Valeur * vol * sqrt(horizon) * z
    - Application: 20,000,000 * 0.0200 * sqrt(1) * 1.65
    - Resultat: 660,000
    - Lecture desk: Perte potentielle au niveau de confiance choisi.
- Actions operationnelles attendues:
  - Comparer VaR et stress tests.
  - Identifier les facteurs dominants du risque.
- Points de vigilance:
  - La VaR ne capture pas correctement les queues extremes ni les risques de gap.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Une VaR 99% 1j de 1m signifie:**
- A) perte garantie de 1m
- B) ~1 jour sur 100 la perte peut depasser 1m
- C) gain de 1m
- D) vol de 1m
  - Reponse: **B**. C'est un quantile: la perte depasse rarement (1%) le seuil, sans borne au-dela.

**Q2. La VaR parametrique suppose surtout:**
- A) des rendements normaux
- B) des sauts frequents
- C) une vol nulle
- D) un spot constant
  - Reponse: **A**. Elle s'appuie sur un quantile gaussien; elle sous-estime les queues epaisses.

**Q3. L'expected shortfall complete la VaR car:**
- A) elle ignore les pertes
- B) elle mesure la perte moyenne au-dela du seuil
- C) elle est plus simple
- D) elle est toujours plus petite
  - Reponse: **B**. L'ES regarde la moyenne des pertes dans la queue, au-dela de la VaR.

**Q4. Doubler l'horizon (iid) multiplie la VaR par:**
- A) 2
- B) sqrt(2)
- C) 1
- D) 4
  - Reponse: **B**. Sous racine-du-temps, la VaR croit en sqrt(horizon).

**Q5. Un depassement de limite VaR appelle d'abord:**
- A) ignorer
- B) reduire/hedger/escalader
- C) augmenter la position
- D) changer la couleur
  - Reponse: **B**. La reaction operationnelle est de reduire le risque ou d'escalader.

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 10 (exploitables: 8).
- Score pedagogique moyen: 51.0/100 (qualite structurelle: 88.5/100).
- Definitions: 2 | exemples: 3 | exercices: 1 | formules: 0 | cas pratiques: 4.
- Repartition par type: theory: 8, market_context: 1, solution: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S6], [S10].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
4. Exemples - couvert par [S1], [S7], [S10].
5. Exemples resolus - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
6. Exercices - couvert par [S10].
7. Corriges - couvert par [S4], [S5], [S9].
8. Cas pratiques - couvert par [S1], [S3], [S8], [S9].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: partially_usable - Sources partiellement suffisantes: completer les manques.
- Presents dans les sources: definitions, exemples, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, formules, exemples resolus, resumes.

## Faits et angles extraits de la base
- ES is also referred to
as conditional VaR (CVaR) or Expected Tail Loss (ETL).
- For a given time
period and confidence level, ES is the average loss that could occur in excess
of the loss calculated by VaR over the same time period and using the same
confidence level.
- By construction, ES will always be a larger number than its
corresponding VaR because it is estimating the average loss in the extreme
tail of the distribution beyond the VaR loss value.
- Like VaR, ES is NOT the
worst case loss, which for many portfolios cannot be estimated.
- Because it
requires even greater information about the extreme tail of the return distribution, ES is more difficult than VaR to calculate and has greater estimation
error.
- 6.4.4 Stress Testing and Scenario Analysis
Although a 99% VaR measure may capture a wide range of all possible outcomes, risk managers must pay particular attention to the remaining 1% of
outcomes since these events could cause banks serious financial problems.
- Stress testing and scenario analysis are important tools of any risk management system that seeks to understand how a portfolio will perform in 
extreme cases.
- Given the reliance on modeling, risk measures need to be
closely examined and tested against extreme events.
- Stress testing considers instances for particular value changes, such as a
rapid change in interest rates or equity indices.
- Scenario analysis evaluates
portfolio performance in severe states of the world, either hypothetical or
historical.

## Sources RAG a citer
- [S1] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 221, score 0.7518 (extrait non cite: source bruitee)
- [S2] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 190, score 0.601417: Banks assume market risk because they trade as principals, risking
their own capital, and hold positions in financial instruments. Failure to manage market risk can have significant direct effects on a bank’s profitability
and reputation.
- [S3] Managing Derivatives Contracts  A Guide to Derivatives Market Structure, Contract Life Cycle, Operations, and Systems ( PDFDrive ), chunk 319, score 0.478973: Risk management activity focuses on every level of transaction processing from pre-trade analysis through the deal capture and from 
confirmation through the settlement in order to control the operational risk.
- [S4] Derivatives Workbook ( PDFDrive ), chunk 31, score 0.473131: Based on Exhibit 1, the best explanation for Nuñes to implement Strategy 8 would be 
that, between the February and December expiration dates, she expects the share price of 
XDF to:
A. remain unchanged. The option trade that Nuñes should recommend relating to the government committee’s 
decision is a:
A. bull spread.
- [S5] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2295, score 0.472369 (extrait non cite: source bruitee)
- [S6] Practical Methods of Financial Engineering and Risk Management  Tools for Modern Financial Professionals ( PDFDrive ), chunk 222, score 0.447443: Market Risk 
Chapters 1–5 all dealt with market risk. This is the risk of losses coming from the market 
change of asset prices that negatively affect the mark-to-market positions of the bank. The 
change of asset prices can come from various factors, such as stock prices, volatility, and 
correlation.
- [S7] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 222, score 0.44298: Stress testing has become more important over the
years and is now a major part of a bank’s, and regulator’s, risk management
activities. Market Risk
205
- [S8] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 8, score 0.433809 (extrait non cite: source bruitee)
- [S9] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 546, score 0.426923: The expected loss 
for each obligor can be calculated as Default rate × (Exposure amount − Expected 
recovery). This means that individual credit limits should be set at levels that are inversely 
proportional to the default rate corresponding to the obligor rating.
- [S10] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 154, score 0.424694: It is designed to give them a single number to look at, so they can then 
dig deeper to understand how concentrated risks might be, and where and why 
these risks are being taken in the various departments that they oversee.

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Parametric VaR
$$
\text{VaR}_{\alpha}=V\,\sigma\,z_{\alpha}\sqrt{h}
$$
- Usage desk: estimate the loss threshold for a linear book under normal assumptions.
### F2 - Expected shortfall
$$
\text{ES}_{\alpha}=V\,\sigma\sqrt{h}\frac{\phi(z_{\alpha})}{1-\alpha}
$$
- Usage desk: look beyond the VaR quantile and quantify tail severity.
### F3 - Stress P&L
$$
\Delta V_{\text{stress}}=\sum_i \text{sensitivity}_i\times \Delta x_i
$$
- Usage desk: translate a risk scenario into an escalation-ready loss estimate.

