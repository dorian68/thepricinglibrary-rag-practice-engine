---
slug: yield-curve-bootstrapping
topic: Yield curve bootstrapping for desk pricing
product: interest-rate curve
level: intermediate
concepts: discount factors, zero curve, forward rates, interpolation
source_count: 10
---

# Module pratique - Yield curve bootstrapping for desk pricing

## Promesse du module
Apprendre Yield curve bootstrapping for desk pricing par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: intermediate
- Duree: 130 minutes
- Produit: interest-rate curve
- Concepts: discount factors, zero curve, forward rates, interpolation

## Objectifs d'apprentissage
- Comprendre le probleme de marche avant la formule.
- Savoir identifier les inputs, les risques et les hypotheses.
- Produire un raisonnement utilisable en contexte professionnel.
- Transformer une source theorique en decision ou en exercice.

## Positionnement bibliotheque
- Track: Market Finance Core
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire les instruments de courbe
- Objectif pratique: Classer deposits, futures et swaps par maturite et convention.
- Situation de desk: Le desk doit reconstruire une courbe avant de pricer un swap.
- Notion utile: Tenor, quote, accrual, discount factor.
- Activite: Transformer les quotes en tableau de bootstrap.
- Livrable apprenant: Curve input sheet.
### Module 2 - Bootstrap discount factors
- Objectif pratique: Extraire les discount factors un par un sans casser les maturites deja calibrees.
- Situation de desk: Une nouvelle quote 5Y arrive et change le point de courbe.
- Notion utile: Recursion sur coupons, interpolation locale.
- Activite: Calculer un point de courbe et documenter la convention.
- Livrable apprenant: Discount-factor ladder.
### Module 3 - Zeros et forwards
- Objectif pratique: Convertir discount factors en zero rates et forwards exploitables.
- Situation de desk: Le trader veut lire le carry implicite entre deux maturites.
- Notion utile: Zero rate continu, forward rate discret.
- Activite: Calculer zero/forward et commenter la pente.
- Livrable apprenant: Zero-forward report.
### Module 4 - Controle et usage desk
- Objectif pratique: Verifier monotonie, interpolation et impact sur PV.
- Situation de desk: Une interpolation trop agressive cree un faux signal de risque.
- Notion utile: No-arbitrage local, smoothness, curve-shape risk.
- Activite: Comparer deux interpolations et choisir une action.
- Livrable apprenant: Curve validation memo.

## Cours redige
### Lecon 1 - Lire les instruments de courbe

**Cas de depart.** Le desk doit reconstruire une courbe avant de pricer un swap. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Distin-
guishing forward curves from discount curves (representing the collateralization of
the forward) motivates an alternative interpolation method, namely interpolation of
the forward value (the product of the forward and the discount factor). [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Tenor, quote, accrual, discount factor..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Transformer les quotes en tableau de bootstrap. Le livrable attendu est un document court et actionnable: Curve input sheet.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - Bootstrap discount factors

**Cas de depart.** Une nouvelle quote 5Y arrive et change le point de courbe. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** In addition,
treating forward curves as native curves (instead of representing them by pseudo-
discount curves) will avoid other problems, like that of overlapping instruments. [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Recursion sur coupons, interpolation locale..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer un point de courbe et documenter la convention. Le livrable attendu est un document court et actionnable: Discount-factor ladder.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Zeros et forwards

**Cas de depart.** Le trader veut lire le carry implicite entre deux maturites. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Besides the interpolation, we discuss the calibration of the curves for which we give
a generic object-oriented implementation in Fries (Curve calibration. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Zero rate continu, forward rate discret..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer zero/forward et commenter la pente. Le livrable attendu est un document court et actionnable: Zero-forward report.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Controle et usage desk

**Cas de depart.** Une interpolation trop agressive cree un faux signal de risque. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Keywords Multi-curve construction· Interest rate curves· Interest rate curve inter-
polation · Cross-currency curves · Term structure models
C.P. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: No-arbitrage local, smoothness, curve-shape risk..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Comparer deux interpolations et choisir une action. Le livrable attendu est un document court et actionnable: Curve validation memo.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. Curve inputs: classer deposits/futures/swaps et conventions de day count.
2. Bootstrap: calculer les discount factors successifs et verifier la monotonie.
3. Zero/forward: convertir DF en zero rates puis forward rates.
4. Interpolation control: comparer deux interpolations et impact PV.
5. Curve memo: conventions, controles et risques de courbe residuels.

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
- Distin-
guishing forward curves from discount curves (representing the collateralization of
the forward) motivates an alternative interpolation method, namely interpolation of
the forward value (the product of the forward and the discount factor).
- In addition,
treating forward curves as native curves (instead of representing them by pseudo-
discount curves) will avoid other problems, like that of overlapping instruments.
- Besides the interpolation, we discuss the calibration of the curves for which we give
a generic object-oriented implementation in Fries (Curve calibration.
- Keywords Multi-curve construction· Interest rate curves· Interest rate curve inter-
polation · Cross-currency curves · Term structure models
C.P.
- Fries (B)
DZ BANK AG, Frankfurt, Germany
e-mail: email@christian-fries.de
C.P.
- Fries
Department of Mathematics, LMU Munich, Munich, Germany
© The Author(s) 2016
K.
- (eds.), Innovations in Derivatives Markets, Springer Proceedings
in Mathematics & Statistics 165, DOI 10.1007/978-3-319-33446-2_11
227
- Fries
1
Introduction
Dynamic multi-curve term structure models, as the one discussed in this book, often
use given interest rate curves as initial data.
- The classical (single curve) example is
the HJM oder LMM model, where
df (t, T) = μ(t, T)dt + Σ(t, T)dW(t),
f (t0, T) = f0(T).
- While research on multi-curve interest rates models was and is very active, see,
e.g., [5, 6, 15, 20–22], references therein and the other chapters of in this book,
the construction of the initial interest rate curve, here f0(T), naturally does not get a
similar strong attention.

## Sources RAG a citer
- [S1] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 238, score 0.619867: role. Distin-
guishing forward curves from discount curves (representing the collateralization of
the forward) motivates an alternative interpolation method, namely interpolation of
the forward value (the product of the forward and the discount factor).
- [S2] Swaps and Other Derivatives  (With CD ROM) (The Wiley Finance Series) ( PDFDrive ), chunk 390, score 0.589849: onal equity swap 170, 171, 172, 173
floating-floating (cross-currency basis swap,
CCBS) 205–7, 212–13, 229–34
discounting and 211–21
pricing and hedging 207–11
floating interest 3
floating price against floating interest swap 171
floors 288-96
foreign asset, synthetic, creating 222–4
forward inflation curve 163
forward rate agreements (FRAs) 16–20
forward rate sensitivity 339–40
forward rates 14–16
forward volatil...
- [S3] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 251, score 0.537219: count factors deﬁnes a forward with ﬁxing time T in terms
of (interpolated) discount factors at times T and T + d (where d is the period
length). The method is a common practice (also considered in [1]). However,
considering forwards for overlapping periods, this may introduce oscillations and
result in implausible delta-hedges (see Table1).
- [S4] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 281, score 0.515652: r, N., Skovmand, D.: A Lévy HJM multiple-curve model with
application to CVA computation. Quant. Financ. 15(3), 401–419 (2015)
14. Cuchiero, C., Fontana, C., Gnoatto, A.: A general HJM framework for multiple yield curve
modeling. Financ. Stoch. 20(2), 267–320 (2016)
15. Filipovi´c, D., Trolle, A.B.: The term structure of interbank risk. J. Financ. Eng. 109(3), 707–733
(2013)
16.
- [S5] Interest Rate Swaps and Their Derivatives  A Practitioner s Guide ( PDFDrive ), chunk 153, score 0.494386: uivalent forward rate curve. Note that these two curves are
interchangeable, and knowledge of one completely determines the other. In [Page 199]
Full Term-Structure Interest-Rate Models
187
discretized format, we have:
fc(t, [T1, T2], ω) =
1
T2 −T1
ln(D(t, T1, ω)/D(t, T2, ω))
for continuously-compounded rates. On the other hand, given a series of
contiguous forward rates { fc(t, [Ti, Ti+1], ω)}i with t = T0 < T1 < .
- [S6] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 349, score 0.490514: gorithms. “Best-ﬁt” algorithms
start by assuming a functional form for the term structure and calibrate
its parameters such as to minimize the re-pricing error of the chosen
© The Author(s) 2017
529
J.R.M. Röman, Analytical Finance: Volume II,
https://doi.org/10.1007/978-3-319-52584-6_21 [Page 547]
530
J.R.M. Röman
set of calibration instruments.
- [S7] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 237, score 0.482868: 5)
19. Jamshidian, F.: An exact bond option pricing formula. J. Financ. 44, 205–209 (1989)
20. Kenyon, C.: Short-rate pricing after the liquidity and credit shocks: including the basis. Risk
Mag. pp. 83–87 (2010)
21. Kijima, M., Muromachi, Y.: Reformulation of the arbitrage-free pricing method under the
multi-curve environment. Preprint (2015)
22.
- [S8] The Mathematics Of Financial Modeling And Investment Management ( PDFDrive ), chunk 562, score 0.482031: enchmark for evaluating performance 
of ﬁxed-income securities and the pricing of ﬁxed-income securities. Since 
the swap curve is effectively the LIBOR curve and investors borrow based 
on LIBOR, the swap curve is more useful to funded investors than a gov-
ernment yield curve.
- [S9] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 263, score 0.469755: ,Hoboken(2007). http://www.christian-fries.de/ﬁnmath/book
11. Fries, C.P.: Curve calibration. Object oriented reference implementation 2010–2015. http://
www.ﬁnmath.net/topics/curvecalibration
12. Fries, C.P.: Funded replication: fund exchange process and the valuation with different funding-
accounts (cross-currency analogy to funding revisited). Wilmott 63, 36–41 (2013). http://
papers.ssrn.com/abstract=2115839
13.
- [S10] Quantitative Finance  A Simulation Based Introduction Using Excel ( PDFDrive ), chunk 119, score 0.465496: s. 13.4  Yield Curves, Discount Factors, and 
Forward Rates
In this section we discuss the spreadsheet YieldDiscountForward, which 
implements the connection between Yield Curve, Discount Factors, and 
Instantaneous forward rates described in Section 13.2. This spreadsheet 
uses the m = 2 (semiannual compounding) rate convention.

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Discount factor recursion
$$
P(0,T_n)=\frac{1-c_n\sum_{i=1}^{n-1}\alpha_iP(0,T_i)}{1+c_n\alpha_n}
$$
- Usage desk: bootstrap the next point of the curve from a quoted par instrument.
### F2 - Zero rate
$$
z(0,T)=-\frac{\ln P(0,T)}{T}
$$
- Usage desk: convert discount factors into continuously compounded zero rates.
### F3 - Forward rate
$$
f(t_i,t_j)=\frac{1}{t_j-t_i}\ln\left(\frac{P(0,t_i)}{P(0,t_j)}\right)
$$
- Usage desk: read the market-implied carry between two maturities.

