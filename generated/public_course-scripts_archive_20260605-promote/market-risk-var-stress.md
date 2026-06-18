---
slug: market-risk-var-stress
topic: Market risk VaR, stress testing and escalation
product: multi-asset portfolio
level: intermediate
concepts: parametric VaR, expected shortfall, stress test, risk limit
source_count: 10
---

# Module pratique - Market risk VaR, stress testing and escalation

## Promesse du module
Apprendre Market risk VaR, stress testing and escalation par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: intermediate
- Duree: 120 minutes
- Produit: multi-asset portfolio
- Concepts: parametric VaR, expected shortfall, stress test, risk limit

## Objectifs d'apprentissage
- Comprendre le probleme de marche avant la formule.
- Savoir identifier les inputs, les risques et les hypotheses.
- Produire un raisonnement utilisable en contexte professionnel.
- Transformer une source theorique en decision ou en exercice.

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

**Cas de depart.** Un portefeuille approche son seuil de VaR intraday. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** [Page 233]
6.4.3 Expected Shortfall
Given the limitations of VaR, regulators and financial organizations are put-
ting more emphasis on another risk measure, expected shortfall (ES), to more
fully estimate risk in the tail of the return distribution. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: VaR one-sided, horizon, volatility..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Construire la fiche inputs du risk report. Le livrable attendu est un document court et actionnable: Risk ticket.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - Calcul VaR

**Cas de depart.** Le CRO demande une estimation rapide avant la cloture. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** ES is also referred to
as conditional VaR (CVaR) or Expected Tail Loss (ETL). [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: VaR = notional * vol * quantile..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer et comparer a la limite. Le livrable attendu est un document court et actionnable: VaR + statut de limite.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Stress overlay

**Cas de depart.** Un scenario historique depasse le mouvement normal. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** For a given time
period and confidence level, ES is the average loss that could occur in excess
of the loss calculated by VaR over the same time period and using the same
confidence level. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Stress test, tail loss, expected shortfall..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Ajouter un choc severe et comparer. Le livrable attendu est un document court et actionnable: Table VaR/stress.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Escalation

**Cas de depart.** La limite est franchie mais le desk propose d'attendre. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** By construction, ES will always be a larger number than its
corresponding VaR because it is estimating the average loss in the extreme
tail of the distribution beyond the VaR loss value. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Reduce, hedge, monitor, escalate..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Ecrire une note decisionnelle. Le livrable attendu est un document court et actionnable: Escalation memo.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. VaR ticket: horizon, confiance, volatilite et exposition.
2. Calcul VaR: comparer a une limite imposee.
3. Stress overlay: ajouter un scenario extreme et commenter l'ecart.
4. Escalation memo: decision et suivi.

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
- [Page 233]
6.4.3 Expected Shortfall
Given the limitations of VaR, regulators and financial organizations are put-
ting more emphasis on another risk measure, expected shortfall (ES), to more
fully estimate risk in the tail of the return distribution.
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
requires even greater information about the extreme tail of the return distri-
bution, ES is more difficult than VaR to calculate and has greater estimation
error.
- 6.4.4 Stress Testing and Scenario Analysis
Although a 99% VaR measure may capture a wide range of all possible out-
comes, risk managers must pay particular attention to the remaining 1% of
outcomes since these events could cause banks serious financial problems.
- Stress testing and scenario analysis are important tools of any risk manage-
ment system that seeks to understand how a portfolio will perform in 
extreme cases.
- Given the reliance on modeling, risk measures need to be
closely examined and tested against extreme events.
- Stress testing considers instances for particular value changes, such as a
rapid change in interest rates or equity indices.

## Sources RAG a citer
- [S1] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 221, score 0.7518: SK [Page 233]
6.4.3 Expected Shortfall
Given the limitations of VaR, regulators and financial organizations are put-
ting more emphasis on another risk measure, expected shortfall (ES), to more
fully estimate risk in the tail of the return distribution. ES is also referred to
as conditional VaR (CVaR) or Expected Tail Loss (ETL).
- [S2] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 190, score 0.60176: uments due to adverse movements in market
prices. Banks assume market risk because they trade as principals, risking
their own capital, and hold positions in financial instruments. Failure to man-
age market risk can have significant direct effects on a bank’s profitability
and reputation.
- [S3] Managing Derivatives Contracts  A Guide to Derivatives Market Structure, Contract Life Cycle, Operations, and Systems ( PDFDrive ), chunk 319, score 0.481804: s—for 
instance, market risk management systems, credit risk management systems, and 
compliance systems. Risk management activity focuses on every level of trans-
action processing from pre-trade analysis through the deal capture and from 
confirmation through the settlement in order to control the operational risk.
- [S4] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2295, score 0.476361: nimal martingale mea-
sure and the F¨ollmer-Schweizer decomposition, Stochas-
tic Analysis and Applications 13, 573–599. [Page 1494]
Mean–Variance Hedging
5
[53]
Schweizer, M. (1996). Approximation pricing and the
variance-optimal martingale measure, Annals of Proba-
bility 24, 206–236. [54]
Schweizer, M. (2001). From actuarial to ﬁnancial valua-
tion principles, Insurance: Mathematics and Economics
28, 31–47.
- [S5] Derivatives Workbook ( PDFDrive ), chunk 31, score 0.474619: imited. 9. Based on Exhibit 1, the best explanation for Nuñes to implement Strategy 8 would be 
that, between the February and December expiration dates, she expects the share price of 
XDF to:
A. decrease. B. remain unchanged. C. increase. 10. The option trade that Nuñes should recommend relating to the government committee’s 
decision is a:
A. collar. B. bull spread. C. long straddle.
- [S6] Practical Methods of Financial Engineering and Risk Management  Tools for Modern Financial Professionals ( PDFDrive ), chunk 222, score 0.4476: following general categories of risk 
must be considered. Market Risk 
Chapters 1–5 all dealt with market risk. This is the risk of losses coming from the market 
change of asset prices that negatively affect the mark-to-market positions of the bank. The 
change of asset prices can come from various factors, such as stock prices, volatility, and 
correlation.
- [S7] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 8, score 0.439414: .......................168
 5.11.2 Internal Ratings-Based Approaches....................................168
 5.11.3 Common Features to IRB Approaches ...............................169
 5.11.4 Minimum Requirements for IRB Approaches.....................169
 5.11.5 Basel III Rules Regarding Securitization .............................171
CHAPTER 6 
 Market Risk .........................................................
- [S8] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 222, score 0.435311: such as ensuring that the assumptions underlying each
stress test are reasonable. Stress testing has become more important over the
years and is now a major part of a bank’s, and regulator’s, risk management
activities. Market Risk
205
- [S9] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 154, score 0.423206: risk level is increasing or 
decreasing. It is designed to give them a single number to look at, so they can then 
dig deeper to understand how concentrated risks might be, and where and why 
these risks are being taken in the various departments that they oversee. While 
this may make sense, VaR can be easy to misunderstand, and can be dangerous 
when misunderstood.
- [S10] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 546, score 0.422254: ystem could aim to 
have a large number of exposures with equal expected losses. The expected loss 
for each obligor can be calculated as Default rate × (Exposure amount − Expected 
recovery). This means that individual credit limits should be set at levels that are inversely 
proportional to the default rate corresponding to the obligor rating.

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

