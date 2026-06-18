---
slug: rates-swaps-dv01
topic: Interest-rate swaps, PV and DV01
product: EUR interest-rate swap
level: intermediate
concepts: par rate, annuity, DV01, curve shock
source_count: 10
---

# Module pratique - Interest-rate swaps, PV and DV01

> Légende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** réécriture pédagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit à partir des concepts; calculs vérifiés par le moteur déterministe, non extraits d'une source.

## Promesse du module
Apprendre les swaps de taux d'intérêt, la valeur actuelle (PV) et le DV01 par la pratique : manipuler, calculer, comparer, décider, puis seulement formaliser la théorie nécessaire.

## Niveau cible et public
- Niveau : intermédiaire
- Public visé : junior quant, analyste market risk, sales/structuring junior
- Durée estimée : 120 minutes
- Produit : swap de taux d'intérêt en EUR
- Concepts : par rate, annuité, DV01, choc de courbe

## Prerequis
- Valeur temps de l'argent
- Courbe de taux
- Actualisation

## Objectifs d'apprentissage
À la fin de ce module, vous saurez :
- Expliquer l'intuition du sujet avant toute formule ;
- Identifier les inputs, les risques et les hypothèses clés ;
- Dérouler un calcul chiffré et l'interpréter en langage de desk ;
- Répondre à un mini-quiz et résoudre un exercice corrigé ;
- Nommer les limites du modèle et la décision opérationnelle associée.

## Positionnement bibliotheque
- Track : Rates & Fixed Income
- Type d'asset : module réutilisable de cours.
- Sorties attendues : fiche apprenant, cas pratique, corrigé, quiz, notes instructeur.
- Intégration SaaS : ce module doit pouvoir être découpé en leçons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire le ticket swap
- **Objectif pratique** : Identifier payer/receiver, notional, coupon, maturité et index flottant.
- **Situation de desk** : Un trader demande une lecture rapide d'un payer swap EUR 5Y avant un move BCE.
- **Notion utile** : Cash-flow fixe contre flottant, par rate, annuité.
- **Activité** : Transformer le ticket en tableau d'inputs et vérifier le sens du risque.
- **Livrable apprenant** : Ticket enrichi + risque principal en une phrase.

### Module 2 - PV par coupon gap
- **Objectif pratique** : Estimer la valeur du swap avec l'écart fixed coupon vs par rate.
- **Situation de desk** : Le coupon du book est au-dessus du mid-market ; il faut expliquer le PV.
- **Notion utile** : PV approx = (par - fixed) * annuité * notionnel selon le sens.
- **Activité** : Calculer PV, signe et interprétation front-office.
- **Livrable apprenant** : PV expliqué avec signe payer/receiver.

### Module 3 - DV01 et shock P&L
- **Objectif pratique** : Convertir l'annuité en EUR/bp puis appliquer un choc de courbe.
- **Situation de desk** : La courbe bouge de 10bp avant le comité risque.
- **Notion utile** : DV01 = annuité * notionnel * 1bp.
- **Activité** : Calculer DV01, P&L shock et seuil d'alerte.
- **Livrable apprenant** : Tableau DV01/shock P&L.

### Module 4 - Hedge et basis risk
- **Objectif pratique** : Proposer une couverture réaliste et nommer ce qu'elle ne couvre pas.
- **Situation de desk** : Le desk hedge avec futures ou swap opposé de tenor proche.
- **Notion utile** : Parallel hedge, tenor mismatch, curve-shape risk.
- **Activité** : Choisir hedge, sens, taille approximative et risque résiduel.
- **Livrable apprenant** : Mémo hedge en 6 lignes.

### Module 5 - Debrief production
- **Objectif pratique** : Savoir quand l'approximation devient dangereuse.
- **Situation de desk** : La position est matérialisée dans un report de risk management.
- **Notion utile** : Conventions, multi-curve, collateral, interpolation.
- **Activité** : Lister les contrôles avant validation.
- **Livrable apprenant** : Checklist de validation desk.

## Cours redige
### Lecon 1 - Lire le ticket swap

**Intuition _[reformule]_.** Un trader demande une lecture rapide d'un payer swap EUR 5Y avant un move BCE. L'objectif de cette leçon est précisément : Identifier payer/receiver, notional, coupon, maturité et index flottant.

**Ce que disent les sources** _[extrait]_. « In this and the subsequent chapter we will explore a type of derivative security known as a “swap.” Broadly, a swap is an exchange of cash flows between two counterparties over a number of periods of time. This chapter explores the most important swap product, the interest rate swap. » [S1]

**Le point clé : Cash-flow fixe contre flottant, par rate, annuité.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Transformer le ticket en tableau d'inputs et vérifier le sens du risque. Livrable attendu : Ticket enrichi + risque principal en une phrase - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Confondre une sensibilité 'par 1%' avec 'par 0.01' : respecter strictement les unités.

### Lecon 2 - PV par coupon gap

**Intuition _[reformule]_.** Le coupon du book est au-dessus du mid-market ; il faut expliquer le PV. L'objectif de cette leçon est précisément : Estimer la valeur du swap avec l'écart fixed coupon vs par rate.

**Ce que disent les sources** _[extrait]_. « Analysis of the Term Structure of Implied Volatilities, Journal of Financial Quantitative Analysis. » [S2]

**Le point clé : PV approx = (par - fixed) * annuité * notionnel selon le sens.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer PV, signe et interprétation front-office. Livrable attendu : PV expliqué avec signe payer/receiver - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Oublier le signe de la position (long/short, payer/receiver) dans l'interprétation du P&L.

### Lecon 3 - DV01 et shock P&L

**Intuition _[reformule]_.** La courbe bouge de 10bp avant le comité risque. L'objectif de cette leçon est précisément : Convertir l'annuité en EUR/bp puis appliquer un choc de courbe.

**Ce que disent les sources** _[extrait]_. « The term structure of interest rates as a random field. » [S3]

**Le point clé : DV01 = annuité * notionnel * 1bp.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer DV01, P&L shock et seuil d'alerte. Livrable attendu : Tableau DV01/shock P&L - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Appliquer une approximation locale (Taylor) à un choc trop large sans vérifier sa validité.

### Lecon 4 - Hedge et basis risk

**Intuition _[reformule]_.** Le desk hedge avec futures ou swap opposé de tenor proche. L'objectif de cette leçon est précisément : Proposer une couverture réaliste et nommer ce qu'elle ne couvre pas.

**Ce que disent les sources** _[extrait]_. « A simple nonparametric approach to derivative security valuation. » [S4]

**Le point clé : Parallel hedge, tenor mismatch, curve-shape risk.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Choisir hedge, sens, taille approximative et risque résiduel. Livrable attendu : Mémo hedge en 6 lignes - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Présenter un chiffre sans unité ni ordre de grandeur de contrôle.

### Lecon 5 - Debrief production

**Intuition _[reformule]_.** La position est matérialisée dans un report de risk management. L'objectif de cette leçon est précisément : Savoir quand l'approximation devient dangereuse.

**Ce que disent les sources** _[extrait]_. « For interest rate swaps and options, the payoffs occur after a certain number of days following the expiration, depending on the days to maturity of the instrument that defines the underlying rate. » [S5]

**Le point clé : Conventions, multi-curve, collateral, interpolation.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Lister les contrôles avant validation. Livrable attendu : Checklist de validation desk - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Traiter un risque discontinu (barrière, défaut) comme un Greek lisse.

## Labs pratiques a inclure
1. Ticket swap : identifier payer/receiver, coupon, par rate, annuité et risque principal.
2. PV/DV01 : calculer PV approximatif et EUR/bp sur un notionnel imposé.
3. Shock P&L : appliquer +/-10bp et expliquer le signe.
4. Hedge memo : proposer hedge, taille et basis risk.
5. Debrief : contrôles de convention, courbe et collateral.

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

