---
slug: credit-derivatives-cds
topic: CDS spread risk, carry and CS01
product: single-name CDS
level: intermediate
concepts: spread, risky annuity, CS01, carry
source_count: 10
---

# Module pratique - CDS spread risk, carry and CS01

> Légende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** réécriture pédagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit à partir des concepts; calculs vérifiés par le moteur déterministe, non extraits d'une source.

## Promesse du module
Apprendre CDS spread risk, carry and CS01 par la pratique: manipuler, calculer, comparer, décider, puis seulement formaliser la théorie nécessaire.

## Niveau cible et public
- Niveau: intermédiaire
- Public visé: junior quant, analyste market risk, sales/structuring junior
- Durée estimée: 110 minutes
- Produit: single-name CDS
- Concepts: spread, risky annuity, CS01, carry

## Prerequis
- notion de défaut
- spread de crédit
- actualisation

## Objectifs d'apprentissage
À la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypothèses clés;
- dérouler un calcul chiffré et l'interpréter en langage de desk;
- répondre à un mini-quiz et résoudre un exercice corrigé;
- nommer les limites du modèle et la décision opérationnelle associée.

## Positionnement bibliotheque
- Track: Credit & XVA
- Type d'asset: module réutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrigé, quiz, notes instructeur.
- Intégration SaaS: ce module doit pouvoir être découpé en leçons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire le ticket CDS
- Objectif pratique: Identifier protection buyer/seller, spread, notionnel et maturité.
- Situation de desk: Un single-name widening arrive dans le book credit.
- Notion utile: Spread CDS, risky annuity, default leg/premium leg.
- Activité: Transformer le ticket en inputs de risk.
- Livrable apprenant: Ticket credit enrichi.

### Module 2 - Carry
- Objectif pratique: Distinguer coupon/carry et mark-to-market.
- Situation de desk: Le book semble profitable au carry mais le spread bouge.
- Notion utile: Carry = notionnel * spread selon convention simplifiée.
- Activité: Calculer carry annuel et commentaire.
- Livrable apprenant: Carry note.

### Module 3 - CS01
- Objectif pratique: Calculer la sensibilité à 1bp de spread.
- Situation de desk: Risk demande l'impact d'un widening de 25bp.
- Notion utile: CS01 = notionnel * risky annuity * 1bp.
- Activité: Calculer CS01 et shock P&L avant signe position.
- Livrable apprenant: Table CS01/shock.

### Module 4 - Decision credit
- Objectif pratique: Proposer hedge/réduction/monitoring en fonction du risque.
- Situation de desk: La liquidité CDS baisse pendant le stress.
- Notion utile: Spread risk, jump-to-default, liquidity.
- Activité: Écrire une décision opérationnelle.
- Livrable apprenant: Memo risk action.

## Cours redige
### Lecon 1 - Lire le ticket CDS

**Intuition _[reformule]_.** Un single-name widening arrive dans le book credit. L'objectif de cette leçon est précisément : Identifier protection buyer/seller, spread, notionnel et maturité.

**Ce que disent les sources** _[extrait]_. « Market Risk arises from the trading activities of banks and is a consequence of movements in market prices. » [S4]

**Le point clé: Spread CDS, risky annuity, default leg/premium leg.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Transformer le ticket en inputs de risk. Livrable attendu: Ticket credit enrichi - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Confondre une sensibilité 'par 1%' avec 'par 0.01': respecter strictement les unités.

### Lecon 2 - Carry

**Intuition _[reformule]_.** Le book semble profitable au carry mais le spread bouge. L'objectif de cette leçon est précisément : Distinguer coupon/carry et mark-to-market.

**Ce que disent les sources** _[extrait]_. « The change of asset prices can come from various factors, such as stock prices, volatility, and correlation. » [S2]

**Le point clé: Carry = notionnel * spread selon convention simplifiée.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer carry annuel et commentaire. Livrable attendu: Carry note - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Oublier le signe de la position (long/short, payer/receiver) dans l'interprétation du P&L.

### Lecon 3 - CS01

**Intuition _[reformule]_.** Risk demande l'impact d'un widening de 25bp. L'objectif de cette leçon est précisément : Calculer la sensibilité à 1bp de spread.

**Ce que disent les sources** _[extrait]_. « The value of a CDS position is primarily affected by changes in the CDS spread. » [S3]

**Le point clé: CS01 = notionnel * risky annuity * 1bp.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer CS01 et shock P&L avant signe position. Livrable attendu: Table CS01/shock - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Appliquer une approximation locale (Taylor) à un choc trop large sans vérifier sa validité.

### Lecon 4 - Decision credit

**Intuition _[reformule]_.** La liquidité CDS baisse pendant le stress. L'objectif de cette leçon est précisément : Proposer hedge/réduction/monitoring en fonction du risque.

**Ce que disent les sources** _[extrait]_. « Failure to manage market risk can have significant direct effects on a bank’s profitability and reputation. » [S4]

**Le point clé: Spread risk, jump-to-default, liquidity.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Écrire une décision opérationnelle. Livrable attendu: Memo risk action - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Présenter un chiffre sans unité ni ordre de grandeur de contrôle.

## Labs pratiques a inclure
1. Ticket CDS: protection buyer/seller, spread, notionnel, risky annuity.
2. Carry/CS01: calculer carry annuel et sensibilité 1bp.
3. Spread shock: appliquer +25bp et discuter le signe position.
4. Risk action: hedge, reduce ou monitor selon liquidité et jump risk.

## Script enseignant
1. Ouvrir par un cas concret.
2. Demander aux apprenants de formuler l'intuition.
3. Introduire la notation minimale.
4. Faire résoudre une micro-tâche.
5. Debrief: erreurs courantes, limites, interprétation marché.

## Supports a produire
- Fiche apprenant d'une page.
- Slides courtes orientées cas.
- Notebook ou tableur de calcul si le sujet s'y prête.
- Corrigé détaillé.
- Quiz de vérification rapide.

## Exemple numerique resolu
_[genere - calcul verifie]_ On mesure le CS01, le carry et le P&L d'un ecartement de spread.

**Donnees.** CDS notionnel 50m spread 120bp risky annuity 4.2 widen 25bp.

### CS01 et carry CDS
- Famille: cds_cs01
- Hypotheses controlees:
  - Approximation spread-DV01; pas de bootstrap de hazard curve.
  - Signe donne du point de vue acheteur de protection.
- Calculs a respecter:
  - CS01:
    - Formule: Risky annuity * Notionnel * 1bp
    - Application: 4.2 * 50,000,000 * 0.0001
    - Resultat: 21,000 EUR/bp
    - Lecture desk: Sensibilite approximative au spread de credit.
  - Coupon annuel approx:
    - Formule: Spread bp * CS01
    - Application: 120 * 21,000
    - Resultat: 2,520,000 EUR/an
    - Lecture desk: Ordre de grandeur du carry premium.
  - P&L spread shock protection buyer:
    - Formule: CS01 * shock bp
    - Application: 21,000 * 25
    - Resultat: 525,000 EUR
    - Lecture desk: Un acheteur de protection gagne si le spread s'elargit.
- Actions operationnelles attendues:
  - Comparer carry et jump-to-default.
  - Hedger indice/single-name en tenant compte du basis.

**Lecture finale.** Chaque chiffre ci-dessus a une unite explicite et un sens economique; un apprenant doit pouvoir refaire le calcul a la main et retrouver le meme ordre de grandeur.

## Exercices corriges
### Exercice 1 - application directe
_[genere]_ Un acheteur de protection CDS gagne-t-il ou perd-il quand le spread s'ecarte?

**Correction.** Il gagne en mark-to-market: la protection qu'il detient vaut plus cher. P&L approx = CS01 * widening.

### Exercice 2 - niveau desk
_[genere]_ CDS 50m, spread 120bp, risky annuity 4.2, widen 25bp. Calculez CS01, carry et P&L.

**Correction detaillee (calcul verifie).**
### CS01 et carry CDS
- Famille: cds_cs01
- Hypotheses controlees:
  - Approximation spread-DV01; pas de bootstrap de hazard curve.
  - Signe donne du point de vue acheteur de protection.
- Calculs a respecter:
  - CS01:
    - Formule: Risky annuity * Notionnel * 1bp
    - Application: 4.2 * 50,000,000 * 0.0001
    - Resultat: 21,000 EUR/bp
    - Lecture desk: Sensibilite approximative au spread de credit.
  - Coupon annuel approx:
    - Formule: Spread bp * CS01
    - Application: 120 * 21,000
    - Resultat: 2,520,000 EUR/an
    - Lecture desk: Ordre de grandeur du carry premium.
  - P&L spread shock protection buyer:
    - Formule: CS01 * shock bp
    - Application: 21,000 * 25
    - Resultat: 525,000 EUR
    - Lecture desk: Un acheteur de protection gagne si le spread s'elargit.
- Actions operationnelles attendues:
  - Comparer carry et jump-to-default.
  - Hedger indice/single-name en tenant compte du basis.

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
- Chunks sources analyses: 10 (exploitables: 10).
- Score pedagogique moyen: 50.2/100 (qualite structurelle: 90.0/100).
- Definitions: 2 | exemples: 2 | exercices: 1 | formules: 3 | cas pratiques: 2.
- Repartition par type: theory: 9, example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S2], [S9].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S1], [S6], [S8].
4. Exemples - couvert par [S3], [S10].
5. Exemples resolus - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
6. Exercices - couvert par [S1], [S7], [S8], [S9].
7. Corriges - couvert par [S5], [S8].
8. Cas pratiques - couvert par [S3], [S10].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, exemples resolus, resumes.

## Faits et angles extraits de la base
- Bazaraa, M.S., Jarvis, J.J., Sherali, H.D.: Linear Programming and Network Flows, 4th edn.
- Bielecki, T.R., Rutkowski, M.: Credit Risk: Modeling, Valuation and Hedging.
- Brenner, U.: A faster polynomial algorithm for the unbalanced hitchcock transportation problem.
- Brigo, D., Capponi, A.: Bilateral counterparty risk valuation with stochastic dynamical models
and application to credit default swaps.
- Brigo, D., Chourdakis, K.: Counterparty risk for credit default swaps: impact of spread volatility
and default correlation.
- Brigo, D., Pallavicini, A., Papatheodorou, V.: Arbitrage-free valuation of bilateral counterparty
risk for interest-rate products: impact of volatilities and correlations.
- Brigo, D., Morini, M., Pallavicini, A.: Counterparty Credit Risk, Collateral and Funding: With
Pricing Cases for all Asset Classes.
- Cespedes, J.C.G., Herrero, J.A., Rosen, D., Saunders, D.: Effective modeling of wrong way
risk, counterparty credit risk capital and alpha in Basel II.
- Glasserman, P., Yang, L.: Bounding wrong-way risk in CVA calculation.
- Gregory, J.K.: Counterparty Credit Risk: The New Challenge for Global Financial Markets.

## Sources RAG a citer
- [S1] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 106, score 0.669295: References
1. Bazaraa, M.S., Jarvis, J.J., Sherali, H.D.: Linear Programming and Network Flows, 4th edn. Wiley, New Jersey (2010)
2. Bielecki, T.R., Rutkowski, M.: Credit Risk: Modeling, Valuation and Hedging. Springer, Berlin
(2002)
3.
- [S2] Practical Methods of Financial Engineering and Risk Management  Tools for Modern Financial Professionals ( PDFDrive ), chunk 222, score 0.573063: Market Risk 
Chapters 1–5 all dealt with market risk. This is the risk of losses coming from the market 
change of asset prices that negatively affect the mark-to-market positions of the bank. The 
change of asset prices can come from various factors, such as stock prices, volatility, and 
correlation.
- [S3] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 1434, score 0.553319: Risk Management of Credit
Default Swaps
Various factors affect the mark-to-market value of
a CDS position. On a day-to-day basis the main
concern is spread volatility: the value of a CDS
position is primarily affected by changes in the CDS
spread.
- [S4] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 190, score 0.466654: Banks assume market risk because they trade as principals, risking
their own capital, and hold positions in financial instruments. Failure to manage market risk can have significant direct effects on a bank’s profitability
and reputation.
- [S5] Financial Derivatives  Pricing and Risk Management ( PDFDrive ), chunk 397, score 0.456071: Recent government and
industry initiatives are aimed at improving this infrastructure in order to facilitate
more effective management of counterparty risks.
- [S6] Modern Derivatives Pricing and Credit Exposure Analysis  Theory and Practice of CSA and XVA Pricing, Exposure Simulation and Backtesting ( PDFDrive ), chunk 361, score 0.434783: RISK, 27:49, October 2014. [103] Chris Kenyon and Andrew Green. Pricing CDS’s capital relief. RISK, 26(10):62–66,
2014. [104] Chris Kenyon and Andrew Green. Regulatory costs break risk neutrality. RISK,
27:76–80, September 2014. [105] Chris Kenyon and Andrew Green. Dirac Processes and Default Risk.
- [S7] Principles of Financial Engineering ( PDFDrive ), chunk 929, score 0.427762: Goldman
wouldn’t say what specific financials were in the basket, but Viniar confirmed to the analyst asking the
question that the basket contained “a peer group.”
Most would consider peers to Goldman to be other large banks with big investment-banking divisions,
including Morgan Stanley, J.P.
- [S8] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 43, score 0.426235: 14(6), 773–802 (2011)
10. Brigo, D., Buescu, C., Morini, M.: Counterparty risk pricing: impact of closeout and first-todefault times. 15, 1250039–1250039 (2012)
11. Brigo, D., Morini, M., Pallavicini, A.: Counterparty Credit Risk. Collateral and Funding with
Pricing Cases for All Asset Classes.
- [S9] Principles of Financial Engineering ( PDFDrive ), chunk 930, score 0.421454: There is also a tradeoff between single-name and index CDS hedges. Single-name hedging
is more precise in case of bad news affecting a single firm rather than broad market moves, but
10See Ernst & Young (2012) survey “Reflecting credit and funding adjustments in fair value”. 844
CHAPTER 24 COUNTERPARTY RISK
- [S10] Principles of Financial Engineering ( PDFDrive ), chunk 693, score 0.408721: , we obtain a
value of 3:8479 3 cds 1 0:1006 3 cds 5 3:9585 3 cds. Finally, lets consider the protection leg payments. The last three columns of

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Risky annuity
$$
A=\sum_i \alpha_i\,DF_i\,Q(\tau>t_i)
$$
- Usage desk: measure the present value of one spread point on the premium leg.
### F2 - CS01
$$
\text{CS01}=N\times A\times 10^{-4}
$$
- Usage desk: convert a one basis point spread shock into currency P&L.
### F3 - Spread P&L approximation
$$
\Delta V\approx \text{CS01}\times \Delta s_{\text{bp}}
$$
- Usage desk: explain the first-order impact of spread widening or tightening.

