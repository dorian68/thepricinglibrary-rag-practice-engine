---
slug: rates-swaps-dv01
topic: Interest-rate swaps, PV and DV01
product: EUR interest-rate swap
level: intermediate
concepts: par rate, annuity, DV01, curve shock
source_count: 10
---

# Module pratique - Interest-rate swaps, PV and DV01

## Promesse du module
Apprendre Interest-rate swaps, PV and DV01 par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: intermediate
- Duree: 120 minutes
- Produit: EUR interest-rate swap
- Concepts: par rate, annuity, DV01, curve shock

## Objectifs d'apprentissage
- Comprendre le probleme de marche avant la formule.
- Savoir identifier les inputs, les risques et les hypotheses.
- Produire un raisonnement utilisable en contexte professionnel.
- Transformer une source theorique en decision ou en exercice.

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

**Cas de depart.** Un trader demande une lecture rapide d'un payer swap EUR 5Y avant un move BCE. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** ]
CHAPTER14
Interest Rate Swaps
INTRODUCTION
In this and the subsequent chapter we will explore a type of derivative security
known as a “swap.” Broadly, a swap is an exchange of cash flows between
two counterparties over a number of periods of time. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Cash-flow fixe contre flottant, par rate, annuite..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Transformer le ticket en tableau d'inputs et verifier le sens du risque. Le livrable attendu est un document court et actionnable: Ticket enrichi + risque principal en une phrase.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - PV par coupon gap

**Cas de depart.** Le coupon du book est au-dessus du mid-market; il faut expliquer le PV. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** This chapter explores
the most important swap product, the interest rate swap. [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: PV approx = (par - fixed) * annuite * notionnel selon le sens..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer PV, signe et interpretation front-office. Le livrable attendu est un document court et actionnable: PV explique avec signe payer/receiver.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - DV01 et shock P&L

**Cas de depart.** La courbe bouge de 10bp avant le comite risque. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** We will learn about
the characteristics of an interest rate swap, how an interest rate swap’s cash
flows are calculated, and how interest rate swaps can be used to transform
cash flows. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: DV01 = annuite * notionnel * 1bp..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer DV01, P&L shock et seuil d'alerte. Le livrable attendu est un document court et actionnable: Tableau DV01/shock P&L.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Hedge et basis risk

**Cas de depart.** Le desk hedge avec futures ou swap oppose de tenor proche. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** After you read this chapter, you will be able to
■Describe the characteristics of an interest rate swap. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Parallel hedge, tenor mismatch, curve-shape risk..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Choisir hedge, sens, taille approximative et risque residuel. Le livrable attendu est un document court et actionnable: Memo hedge en 6 lignes.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 5 - Debrief production

**Cas de depart.** La position est materialisee dans un report de risk management. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** ■Distinguish between fixed and floating interest rate swap legs and rates. [S5]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Conventions, multi-curve, collateral, interpolation..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Lister les controles avant validation. Le livrable attendu est un document court et actionnable: Checklist de validation desk.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. Ticket swap: identifier payer/receiver, coupon, par rate, annuite et risque principal.
2. PV/DV01: calculer PV approximatif et EUR/bp sur un notionnel impose.
3. Shock P&L: appliquer +/-10bp et expliquer le signe.
4. Hedge memo: proposer hedge, taille et basis risk.
5. Debrief: controles de convention, courbe et collateral.

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
Figure 14.1.
- Additional interest rate swap characteristics are as follows:
■The fixed rate is agreed-upon at the initiation of the interest rate swap.

## Sources RAG a citer
- [S1] Derivatives Essentials  An Introduction to Forwards, Futures, Options and Swaps ( PDFDrive ), chunk 158, score 0.621111: ]
CHAPTER14
Interest Rate Swaps
INTRODUCTION
In this and the subsequent chapter we will explore a type of derivative security
known as a “swap.” Broadly, a swap is an exchange of cash flows between
two counterparties over a number of periods of time. This chapter explores
the most important swap product, the interest rate swap.
- [S2] Financial Derivatives  Pricing, Applications, and Mathematics ( PDFDrive ), chunk 211, score 0.58222: rest Rate Derivatives with GARCH Volatility: Analytical Solutions and
their Applications, Working Paper, Goldman Sachs. Heynen, R., A. Kemna, and T. Vorst (1994): “Analysis of the Term Struc-
ture of Implied Volatilities,” Journal of Financial Quantitative Analysis 1:
31–57. Ho, T., and S. Lee (1986): “Term Structure Movements and Pricing Interest
Rate Contingent Claims,” Journal of Finance 41: 1011–1029. Hogan, M.
- [S3] The Oxford Guide to Financial Modeling  Applications for Capital Markets, Corporate Finance, Risk Management and Financial Institutions ( PDFDrive ), chunk 212, score 0.508126: aint Louis. Feller, W. 1951. Two singular diffusion problems. Annals of Mathematics, 54, 173-181. Flesaker, B. 1993. Testing the Heath-Jarrow-Morton/Ho-Lee model of interest rate contingent
claims pricing. Journal of Financial and Quantitative Analysis, 28, no. 4, 483-495. Goldstein, R. 2000. The term structure of interest rates as a random field. Review of Financial
Studies, 13, 365-384. Goldys, B., M.
- [S4] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 667, score 0.489316: vatives in that the
payoffs are made at the time the contract expires. For
interest rate swaps and options, the payoffs occur after
a certain number of days following the expiration, de-
pending on the days to maturity of the instrument that
defines the underlying rate. Thus, if the underlying is
m-day LIBOR, swaps and options pay off m days after
the rate is determined at expiration.
- [S5] The Oxford Guide to Financial Modeling  Applications for Capital Markets, Corporate Finance, Risk Management and Financial Institutions ( PDFDrive ), chunk 159, score 0.482076: classes from August 23,1976 through
August 31, 1978. Journal of 'Finance, 40, 455-480. Stutzer, M. 1996. A simple nonparametric approach to derivative security valuation. Journal of
Finance, 51, no. 5, 1633-1652.
- [S6] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 356, score 0.455164: utures, Options, and Swaps . 5th ed. Malden, MA : Blackwell , 2007 . Resnick , B. “ The Relationship between Futures Prices for US Treasury Bonds .” Review of 
Research in Futures Markets 3 ( 1984 ): 84 – 104 . Stultz , R. “ Optimal Hedging Policies .” Journal of Financial and Quantitative Analysis
 
 19 (June 1984 ): 127 – 140 .
- [S7] Financial Derivatives  Pricing, Applications, and Mathematics ( PDFDrive ), chunk 212, score 0.418082: gPaper,FinancialStrategiesGroup,MerrillLynch
Capital Markets, New York. Jamshidian, F. (1991a): “Bond and Option Evaluation in the Gaussian Interest
Rate Model,” Research in Finance 9: 131–170. Jamshidian, F. (1991b): “Commodity Option Evaluation in the Gaussian Fu-
tures Term Structure Model,” Review of Futures Markets 10: 324–346. Jamshidian, F.
- [S8] Analytical Corporate Valuation  Fundamental Analysis, Asset Pricing, and Company Valuation ( PDFDrive ), chunk 401, score 0.415535: ates. J Financ Econ 3:361–377
Fama E (1984a) The information in the term structure. J Financ Econ 13(4):509–528
Fama E (1984b) Term premiums in bond returns. J Financ Econ 13(4):529–546
Fisher I (1930) The theory of interest. Macmillan, New York
Fraine HG, Mills RH (1961) The effect of default and credit deterioration on yields of corporate
bonds.
- [S9] Foundations of Financial Markets and Institutions ( PDFDrive ), chunk 849, score 0.393792: nds provide fixed-income traders with 
the following additional advantages: 
• 
portfolio risk management 
• 
short-selling abilities 
• 
bond margin trading abilities 
• 
the ability to create synthetic 
"short-term" bonds 
• 
portfolio duration management 
abilities 
• 
reduction in transaction costs 
• 
using the spreads between the short-term 
and long-term interest rates without 
using the underlying assets...
- [S10] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 668, score 0.387273: e rate, p. 457
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
479 [Page 503]
Further Reading
A good survey article on interest rate derivatives is:
Abken, P. A.

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

