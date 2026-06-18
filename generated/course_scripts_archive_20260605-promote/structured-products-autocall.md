---
slug: structured-products-autocall
topic: Autocallable structured products from term sheet to scenario table
product: autocallable note
level: advanced
concepts: coupon barrier, autocall, protection barrier, redemption
source_count: 10
---

# Module pratique - Autocallable structured products from term sheet to scenario table

## Promesse du module
Apprendre Autocallable structured products from term sheet to scenario table par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: advanced
- Duree: 150 minutes
- Produit: autocallable note
- Concepts: coupon barrier, autocall, protection barrier, redemption

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

**Cas de depart.** Sales envoie un autocall a expliquer avant client call. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** does not pass all of its value onto the buyer in the form of a coupon. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Observation dates, coupon barrier, autocall level..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Construire la table des conditions. Le livrable attendu est un document court et actionnable: Term-sheet map.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - Coupon et autocall

**Cas de depart.** Le sous-jacent finit au-dessus du niveau autocall a une date d'observation. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market down-
turn the product leads to losses. [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Indicator functions, memory coupon, early redemption..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Remplir la logique date par date. Le livrable attendu est un document court et actionnable: Coupon/autocall grid.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Protection barrier

**Cas de depart.** Le sous-jacent finit sous la barriere. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Capital protection, downside participation..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Calculer redemption finale. Le livrable attendu est un document court et actionnable: Downside explanation.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Scenario table client

**Cas de depart.** Le client veut comprendre coupon vs capital at risk. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** [Page 726]
reverse convertible to money market rates, since if the two diverge significantly it may mean that
the reverse convertible embeds significant risk. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Cash-flow path dependency, redemption, loss participation..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Produire une table de scenarios lisible par sales. Le livrable attendu est un document court et actionnable: Client scenario table.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 5 - Desk risk

**Cas de depart.** La structure vend du coupon mais concentre du tail risk. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** In the 1990s, reverse convertibles were often issued with embedded short at-the-money put
options. [S5]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Barrier/gamma/vega/liquidity risk..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Ecrire memo sales + risk. Le livrable attendu est un document court et actionnable: Client/risk memo.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. Term-sheet map: dates, coupon barrier, autocall level, protection barrier.
2. Coupon/autocall grid: calculer coupon et early redemption date par date.
3. Downside: calculer redemption finale sous la barriere de protection.
4. Scenario table: upside, flat, moderate down et crash scenario.
5. Sales/risk memo: benefice client, risque de couverture et tail risk.

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
- does not pass all of its value onto the buyer in the form of a coupon.
- In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market down-
turn the product leads to losses.
- Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING
- [Page 726]
reverse convertible to money market rates, since if the two diverge significantly it may mean that
the reverse convertible embeds significant risk.
- In the 1990s, reverse convertibles were often issued with embedded short at-the-money put
options.
- The downside of such products was that investors would suffer losses if the underlying was
below the initial level.
- As investor demand waned in response to the market downturn following the
bursting of the tech bubble, a new generation of products was developed that embedded a short at-
the-money down-and-in put option.
- The barrier feature provided investors with additional protection
since the put option would not be triggered unless the (down) barrier was reached.
- Such barrier
reverse convertibles are popular structured products in Europe and in the United States.
- Moreover, the large number of structured products and the relative illiquidity of the underlying equity
market made hedging such products more difficult than is the case for FX products, for example.

## Sources RAG a citer
- [S1] Principles of Financial Engineering ( PDFDrive ), chunk 764, score 0.77413: does not pass all of its value onto the buyer in the form of a coupon. In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market down-
turn the product leads to losses. Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING
- [S2] Principles of Financial Engineering ( PDFDrive ), chunk 751, score 0.757982: neering can be used to service retail clients’ particular needs. Financial engineering provides ways to construct any payoff structure desired by an investor. However, often these payoffs involve complex option positions, and clients may not have the
knowledge, or simply the means, to handle such risks. Market practitioners can do this better.
- [S3] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 305, score 0.754621: e early redemption event occurs and the holder of
the structured note receives a redemption amount equal to (100% + Conditional Coupon)
× Notional;
∙If Gold1Y < Auto-callable barrier level, nothing happens and the structures “survives” until
the scheduled maturity.
- [S4] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 305, score 0.754621: e early redemption event occurs and the holder of
the structured note receives a redemption amount equal to (100% + Conditional Coupon)
× Notional;
∙If Gold1Y < Auto-callable barrier level, nothing happens and the structures “survives” until
the scheduled maturity.
- [S5] Demystifying Exotic Products  Interest Rates, Equities and Foreign Exchange  ( PDFDrive ), chunk 205, score 0.752033: nder left to fund our structured coupons). Of course, if the zero-coupon bond were that of any non-government issuer, there is a non-
negligible risk of default. Clearly, Lehman-issued “principal-protected” structured notes failed 
to repay the principal when Lehman Brothers defaulted, much to the chagrin of investors 
who misunderstood the idea.
- [S6] FX Derivatives Trader School ( PDFDrive ), chunk 294, score 0.723863: w Barrier Risk Management
Window barrier options have additional trading risks to American barrier options. Speciﬁcally, there are increased exposures to the ATM curve, and additional
exposures to the forward smile. Therefore, when pricing and risk managing window
barrier options it is important to assess exactly which pricing methodology is used. For example:
■Which ATM volatility curve is used to generate TV?
- [S7] FX Derivatives Trader School ( PDFDrive ), chunk 293, score 0.660099: oes from horizon to expiry. Also, if the
rear-window barrier is through current spot, this approach does not work because
the American barrier option variation will have already knocked. It may also be useful to assess the probability of the rear-window barriers being
knocked.
- [S8] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 176, score 0.659095: nt
Zero Coupon
Bond
Cash to buy Options
$1000
investment
returned 
$1000
investment
returned
Possible Options
Payoff 
or
Day 1
End of Year 5
Figure 18.2: Principal-Guarantee Payoff Profile
Some of the most popular structured products give investors exposures to the 
performance of: equity, commodities, foreign exchange, interest rates, inflation, 
and hedging of corporate risks.
- [S9] Swaps and Other Derivatives ( PDFDrive ), chunk 260, score 0.64282: ry 2014
Coupon:
First year:
4.75% ANN
Thereafter: 3.75  (10 yr CMS  2 yr CMS)
Subject to the constraint
 0
Mandatory early redemption on any coupon date if Total accrued coupon (including the current
coupon) Knockout level. In this case, the Final coupon ¼ Total accrued coupon (excluding
current)  Knockout level, where the Knockout level ¼ 20%.
- [S10] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 252, score 0.641335: ologies to execute calculations on a portfolio basis). In a later chapter, we
will see how bundling financing and hedging transactions helps reduce total credit costs and
can aid in monetizing the benefits of hedging.

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

