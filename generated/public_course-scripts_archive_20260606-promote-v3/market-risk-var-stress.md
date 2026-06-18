---
slug: market-risk-var-stress
topic: Market risk VaR, stress testing and escalation
product: multi-asset portfolio
level: intermediate
concepts: parametric VaR, expected shortfall, stress test, risk limit
source_count: 10
---

# Module pratique - Risque de marche, VaR, stress testing et escalade

> Légende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** réécriture pédagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit à partir des concepts; calculs vérifiés par le moteur déterministe, non extraits d'une source.

## Promesse du module
Apprendre le risque de marché, la VaR, le stress testing et l'escalade par la pratique : manipuler, calculer, comparer, décider, puis seulement formaliser la théorie nécessaire.

## Niveau cible et public
- Niveau : intermédiaire
- Public visé : junior quant, analyste risque de marché, sales/structuring junior
- Durée estimée : 120 minutes
- Produit : portefeuille multi-actifs
- Concepts : VaR paramétrique, expected shortfall, stress test, limite de risque

## Prerequis
- Distribution normale
- Quantile
- Volatilité

## Objectifs d'apprentissage
À la fin de ce module, vous saurez :
- Expliquer l'intuition du sujet avant toute formule ;
- Identifier les inputs, les risques et les hypothèses clés ;
- Dérouler un calcul chiffré et l'interpréter en langage de desk ;
- Répondre à un mini-quiz et résoudre un exercice corrigé ;
- Nommer les limites du modèle et la décision opérationnelle associée.

## Positionnement bibliotheque
- Track : Gestion des risques
- Type d'asset : module réutilisable de cours.
- Sorties attendues : fiche apprenant, cas pratique, corrigé, quiz, notes instructeur.
- Intégration SaaS : ce module doit pouvoir être découpé en leçons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Definir la question de risque
- Objectif pratique : Clarifier horizon, confiance, exposition et limite.
- Situation de desk : Un portefeuille approche son seuil de VaR intraday.
- Notion utile : VaR unilatérale, horizon, volatilité.
- Activité : Construire la fiche inputs du risk report.
- Livrable apprenant : Risk ticket.

### Module 2 - Calcul VaR
- Objectif pratique : Calculer une VaR paramétrique simple avec les bonnes unités.
- Situation de desk : Le CRO demande une estimation rapide avant la clôture.
- Notion utile : VaR = notional * vol * quantile.
- Activité : Calculer et comparer à la limite.
- Livrable apprenant : VaR + statut de limite.

### Module 3 - Stress overlay
- Objectif pratique : Montrer ce que la VaR ne capture pas.
- Situation de desk : Un scénario historique dépasse le mouvement normal.
- Notion utile : Stress test, perte de queue, expected shortfall.
- Activité : Ajouter un choc sévère et comparer.
- Livrable apprenant : Table VaR/stress.

### Module 4 - Escalade
- Objectif pratique : Transformer le chiffre en décision de gestion.
- Situation de desk : La limite est franchie mais le desk propose d'attendre.
- Notion utile : Réduire, couvrir, surveiller, escalader.
- Activité : Écrire une note décisionnelle.
- Livrable apprenant : Escalation memo.

## Cours redige
### Lecon 1 - Definir la question de risque

**Intuition _[reformule]_.** Un portefeuille approche son seuil de VaR intraday. L'objectif de cette leçon est précisément : Clarifier horizon, confiance, exposition et limite.

**Ce que disent les sources** _[extrait]_. « Banks assume market risk because they trade as principals, risking their own capital, and hold positions in financial instruments. Failure to manage market risk can have significant direct effects on a bank’s profitability and reputation. » [S2]

**Le point clé : VaR unilatérale, horizon, volatilité.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Construire la fiche inputs du risk report. Livrable attendu : Risk ticket - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Confondre une sensibilité 'par 1%' avec 'par 0.01' : respecter strictement les unités.

### Lecon 2 - Calcul VaR

**Intuition _[reformule]_.** Le CRO demande une estimation rapide avant la clôture. L'objectif de cette leçon est précisément : Calculer une VaR paramétrique simple avec les bonnes unités.

**Ce que disent les sources** _[extrait]_. « Risk management activity focuses on every level of transaction processing from pre-trade analysis through the deal capture and from confirmation through the settlement in order to control the operational risk. Market Risk Management Systems capture trade valuations of all portfolios and calculate various market risk measures, such as value at risk (VaR), at different levels. » [S3]

**Le point clé : VaR = notional * vol * quantile.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer et comparer à la limite. Livrable attendu : VaR + statut de limite - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Oublier le signe de la position (long/short, payer/receiver) dans l'interprétation du P&L.

### Lecon 3 - Stress overlay

**Intuition _[reformule]_.** Un scénario historique dépasse le mouvement normal. L'objectif de cette leçon est précisément : Montrer ce que la VaR ne capture pas.

**Ce que disent les sources** _[extrait]_. « Stress testing considers instances for particular value changes, such as a rapid change in interest rates or equity indices. » [S1]

**Le point clé : Stress test, perte de queue, expected shortfall.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Ajouter un choc sévère et comparer. Livrable attendu : Table VaR/stress - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Appliquer une approximation locale (Taylor) à un choc trop large sans vérifier sa validité.

### Lecon 4 - Escalade

**Intuition _[reformule]_.** La limite est franchie mais le desk propose d'attendre. L'objectif de cette leçon est précisément : Transformer le chiffre en décision de gestion.

**Ce que disent les sources** _[extrait]_. « Market risk arises from the trading activities of banks and is a consequence of movements in market prices. » [S6]

**Le point clé : Réduire, couvrir, surveiller, escalader.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Écrire une note décisionnelle. Livrable attendu : Escalation memo - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Présenter un chiffre sans unité ni ordre de grandeur de contrôle.

## Labs pratiques a inclure
1. VaR ticket : horizon, confiance, volatilité et exposition.
2. Calcul VaR : comparer à une limite imposée.
3. Stress overlay : ajouter un scénario extrême et commenter l'écart.
4. Escalation memo : décision et suivi.

## Script enseignant
1. Ouvrir par un cas concret.
2. Demander aux apprenants de formuler l'intuition.
3. Introduire la notation minimale.
4. Faire résoudre une micro-tâche.
5. Débrief : erreurs courantes, limites, interprétation marché.

## Supports a produire
- Fiche apprenant d'une page.
- Slides courtes orientées cas.
- Notebook ou tableur de calcul si le sujet s'y prête.
- Corrigé détaillé.
- Quiz de vérification rapide.

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

