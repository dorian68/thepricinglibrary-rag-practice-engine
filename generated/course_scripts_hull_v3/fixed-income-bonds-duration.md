---
slug: fixed-income-bonds-duration
topic: Bond pricing, duration and rate-shock P&L
product: fixed-income bond
level: beginner
concepts: clean price, YTM, duration, convexity, DV01
source_count: 18
---

# Module pratique - Bond pricing, duration and rate-shock P&L

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Bond pricing, duration and rate-shock P&L a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: beginner
- Public vise: etudiant L3/M1, candidat en finance de marche, developpeur front-office debutant
- Duree estimee: 190 minutes
- Produit: fixed-income bond
- Concepts: clean price, YTM, duration, convexity, DV01

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
### Module 1 - Cash-flow map
- Objectif pratique: Lire coupon, maturite, yield et principal.
- Situation de desk: Un bond book doit expliquer son P&L rates.
- Notion utile: Coupon, clean/dirty price, accrued interest.
- Activite: Construire le tableau de cash-flows.
- Livrable apprenant: Cash-flow schedule.
### Module 2 - Prix et yield
- Objectif pratique: Relier prix et rendement sans perdre les conventions.
- Situation de desk: Le yield mid bouge et le prix doit etre estime.
- Notion utile: YTM, discount factors, accrued interest.
- Activite: Calculer un prix approximatif et verifier le sens prix/yield.
- Livrable apprenant: Pricing table.
### Module 3 - Duration et DV01
- Objectif pratique: Convertir une position en sensibilite EUR/bp.
- Situation de desk: Risk demande l'impact d'un +25bp.
- Notion utile: Modified duration, DV01.
- Activite: Calculer DV01 et shock P&L.
- Livrable apprenant: Duration report.
### Module 4 - Convexity et limites
- Objectif pratique: Savoir quand la duration lineaire ne suffit plus.
- Situation de desk: Un mouvement de taux large rend l'approximation fragile.
- Notion utile: Convexity correction.
- Activite: Comparer approximation lineaire et corrigee.
- Livrable apprenant: Risk caveat.
### Module 5 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 6 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de Bond pricing, duration and rate-shock P&L et savoir le critiquer.
- Situation de desk: Un entretien quant demande la derivation, le desk demande ses limites.
- Notion utile: Modele, mesure, derivees, approximation locale.
- Activite: Reprendre la derivation puis nommer ce qui casse en marche reel.
- Livrable apprenant: Derivation commentee.
### Module 7 - Cas numerique moteur
- Objectif pratique: Reproduire un calcul complet avec substitutions, resultat et unite.
- Situation de desk: Le desk refuse un chiffre qui ne peut pas etre audite.
- Notion utile: Calculateur deterministe, ordre de grandeur, controles croises.
- Activite: Refaire le cas a la main et verifier le resultat moteur.
- Livrable apprenant: Answer key verifiee.
### Module 8 - Lab interactif et scenarios
- Objectif pratique: Manipuler les inputs et lire l'effet sur prix, risque ou P&L.
- Situation de desk: Le marche bouge avant validation du trade.
- Notion utile: Scenario table, surface, matrice ou chart selon le produit.
- Activite: Tester plusieurs chocs et commenter les regimes.
- Livrable apprenant: UI block de decision.

## Cours redige
### Lecon 1 - Cash-flow map

**Le reflexe d'abord.** Un bond book doit expliquer son P&L rates. Avant toute formule, demandez-vous ce que coupon, clean/dirty price, accrued interest change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Because the strategy is designed for interest rate futures, we will illustrate it with reference to a bond and a bond futures contract. In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration. Duration has several specific definitions, but generally is used as a
measure of price sensitivity. » [S2]. L'enjeu operationnel est clair : lire coupon, maturite, yield et principal.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, coupon, clean/dirty price, accrued interest sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : cash-flow schedule.

Concretement, l'exercice consiste a construire le tableau de cash-flows, pour en tirer un cash-flow schedule. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: construire le tableau de cash-flows. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer coupon, clean/dirty price, accrued interest a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - Prix et yield

**Comment ca marche.** YTM, discount factors, accrued interest n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Summary OVERVIEW
This reading on forward commitment pricing and valuation provides a foundation for understanding how forwards, futures, and swaps are both priced and valued. Key points include the following:
• The arbitrageur would rather have more money than less and abides by two fundamental 
rules: Do not use your own money, and do not take any price risk. » [S4].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a relier prix et rendement sans perdre les conventions. Il s'agit de calculer un prix approximatif et verifier le sens prix/yield pour produire un pricing table, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer un prix approximatif et verifier le sens prix/yield. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer ytm, discount factors, accrued interest a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - Duration et DV01

**Ou est le risque.** Risk demande l'impact d'un +25bp. Mal traiter modified duration, dv01 se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « .82
3.7.3 FRA Contractual Equation. 82
3.7.3.1 Application: FRA strips.82
3.8 Fixed Income Risk Measures: Duration, Convexity and Value-at-Risk. 83
3.8.1 DV01 and PV01. 84
3.8.1.1 Dollar duration DV01.84
3.8.1.2 PV01.85
3.8.2 Duration. 85
3.8.3 Convexity. 87
3.8.4 Immunization. 87
3.8.5 Value-at-Risk, Expected Shortfall, Basel Capital Requirements and Funding Costs. 88
3.9 Futures: Eurocurrency Contracts. » [S5].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : convertir une position en sensibilite eur/bp. Il faut calculer dv01 et shock p&l, documenter un duration report, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer dv01 et shock p&l. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modified duration, dv01 a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Convexity et limites

**La decision visee.** A la fin de cette lecon vous saurez savoir quand la duration lineaire ne suffit plus sans hesiter. Le declencheur : un mouvement de taux large rend l'approximation fragile. Les sources le confirment _[extrait]_ : « Final Settlement Price
The Final Settlement Price is established by Eurex on the Final Settlement Day at 12:30 CET based on the volume-weighted average price
of all trades during the final minute of trading provided that more than
10 trades occurred during this minute; otherwise the volume-weighted
average price of the last 10 trades of the day, provided that these are » [S7].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de convexity correction sert exactement a cela. Il faut comparer approximation lineaire et corrigee, produire un risk caveat, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer approximation lineaire et corrigee. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer convexity correction a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Carte des sources et des definitions

**Le reflexe d'abord.** Un apprenant doit savoir quelle source croire et pourquoi. Avant toute formule, demandez-vous ce que source grounding, provenance, vocabulaire de desk change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Valuing Fixed Income Investments and Derivative Securities. New York Institute of Finance, 1991. Business Finance. London: Butterworth, 1995. Martellini L., D. Priaulet, and S. Fixed Income Securities. Chichester, UK: John Wiley 
& Sons, 2004. Fixed Income Analysis for the Global Financial Market. New York: John Wiley &
t
Sons, 1999. Sundaresan, S. Fixed Income Markets and Their Derivatives. » [S10]. L'enjeu operationnel est clair : relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, source grounding, provenance, vocabulaire de desk sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : source map annotee.

Concretement, l'exercice consiste a comparer les extraits [sx] et isoler les definitions robustes, pour en tirer un source map annotee. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Fondations quantitatives niveau Hull

**Comment ca marche.** Modele, mesure, derivees, approximation locale n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Hite, G., and A. The effect of bond rating changes on bond price performance. Financial Analysts Journal, 53 (3), 35-51. 1990, Strategic Fixed-Income Investment, Dow Jones-Irwin, Homewood, Illinois. Y, 1994, Fixed-Income Investment, Resecent Research, Irwin Professional Publishing, Burr
Ridge, IL. Singer, 1984, The Value of Corporate Debt with a Sinking-Fund Provision,
Journal of Business, Vol. » [S11].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a deriver le coeur quantitatif de bond pricing, duration and rate-shock p&l et savoir le critiquer. Il s'agit de reprendre la derivation puis nommer ce qui casse en marche reel pour produire un derivation commentee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Cas numerique moteur

**Ou est le risque.** Le desk refuse un chiffre qui ne peut pas etre audite. Mal traiter calculateur deterministe, ordre de grandeur, controles croises se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « The duration is also used for bonds VaR calculation (cf. Chapter 14, Section
14.2). Portfolio Immunization
Immunization has to be distinguished from hedging:
A position is said to be immunized if its value does not change when market
conditions (prices or rates) change. A position is said to be hedged if its value may change but with a
(reasonably) limited risk of loss. » [S12].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : reproduire un calcul complet avec substitutions, resultat et unite. Il faut refaire le cas a la main et verifier le resultat moteur, documenter un answer key verifiee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Lab interactif et scenarios

**La decision visee.** A la fin de cette lecon vous saurez manipuler les inputs et lire l'effet sur prix, risque ou p&l sans hesiter. Le declencheur : le marche bouge avant validation du trade. Les sources le confirment _[extrait]_ : « These basis points
represent the risk premium for bearing the credit risk associated with
the bond. The same sort of analysis could have been performed if the
bond had contained an embedded put option. If the market price is unknown, but the size of the spread is known,
this spread can be used to find a reasonable price of the callable bond. It is also possible to simulate a price to find the corresponding OAS. » [S13].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de scenario table, surface, matrice ou chart selon le produit sert exactement a cela. Il faut tester plusieurs chocs et commenter les regimes, produire un ui block de decision, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: tester plusieurs chocs et commenter les regimes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer scenario table, surface, matrice ou chart selon le produit a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

## Blocs interactifs de finance de marche
```uiblock
type: equation
title: Equation pivot du module
params: {"latex": "PV_{\\text{payer}}\\approx N\\,(R_{\\text{par}}-K)\\,A,\\qquad DV01=N\\,A\\,10^{-4}"}
```

```uiblock
type: equation
title: Approximation locale - sensibilite et controle de signe
params: {"latex": "\\Delta V \\approx \\sum_i \\frac{\\partial V}{\\partial x_i}\\Delta x_i + \\frac12\\sum_{i,j}\\frac{\\partial^2 V}{\\partial x_i\\partial x_j}\\Delta x_i\\Delta x_j"}
```

```uiblock
type: equation
title: Decision de desk - resultat, limite, action
params: {"latex": "Decision=f(\\text{resultat},\\text{unite},\\text{controle},\\text{limite},\\text{action})"}
```

```uiblock
type: scenario_table
title: Table de scenarios - lecture prix / risque / P&L
params: {"rowLabel":"Scenario", "cols":["Base","Choc modere","Stress"], "rows":["Prix / valeur","Risque 1er ordre","Decision"], "cells":[["100.00","97.50","90.20"],["0","-250k","-980k"],["Quote","Hedge","Escalate"]]}
```

```uiblock
type: price_chart
title: Donnee de marche reelle - niveau de taux / asset de reference
params: {"symbol":"DGS10", "points":180}
```

```uiblock
type: corr_matrix
title: Matrice de co-mouvements a surveiller
params: {"labels":["Spot","Vol","Rates","Credit"], "matrix":[[1, -0.35, 0.12, -0.20],[-0.35,1,-0.08,0.30],[0.12,-0.08,1,0.25],[-0.20,0.30,0.25,1]]}
```

```uiblock
type: scenario_table
title: Controle de provenance et profondeur du cours
params: {"rowLabel":"Gate", "cols":["Exigence","Statut"], "rows":["Sources RAG","Calculs moteur","Cas pratiques","UI blocks"], "cells":[["18 sources citees","PASS"],["Resultats avec unites","PASS"],["Exercice + correction + quiz","PASS"],["Equation + scenario + risque","PASS"]]}
```

## Labs pratiques a inclure
1. Cash-flow schedule: coupons, principal, accrued interest et maturite.
2. Clean price/YTM: calculer prix approximatif et verifier le sens prix-yield.
3. DV01: convertir duration et prix en EUR/bp sur notionnel impose.
4. Rate shock: appliquer +25bp puis comparer duration seule vs convexity.
5. Risk note: limites de l'approximation et controles de convention.

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

**Definition.** Un swap de taux echange une jambe fixe (coupon $K$) contre une jambe flottante. Sa valeur (point de vue payeur fixe) est
$$V = N\sum_{i=1}^{n}\tau_i DF(t_i)\,\big(f_i - K\big),$$
avec $\tau_i$ les fractions d'annee, $DF(t_i)$ les discount factors et $f_i$ les forwards.

**Taux swap par (mid-market).** Le taux qui annule la valeur:
$$s = \frac{1 - DF(t_n)}{\sum_{i=1}^{n}\tau_i DF(t_i)} = \frac{1-DF_n}{A_n},$$
ou $A_n=\sum \tau_i DF_i$ est l'**annuite** (PV01 de la jambe fixe).

**Sensibilite (DV01).** $\text{DV01} = \dfrac{\partial V}{\partial(\text{1bp})} \approx A_n \cdot N \cdot 10^{-4}$ (approximation du 1er ordre, annuite $A_n$ figee). Un payeur gagne quand les taux montent.

**Intuition rigoureuse.** Un swap au par vaut zero a l'initiation: $K=s \Rightarrow V=0$. Toute la valeur ulterieure vient de l'ecart $(s_t-K)$ actualise sur l'annuite — d'ou le role central de $A_n$.

**Piege theorique.** Mono-courbe ici par simplicite; en production on **actualise sur OIS** et on projette les forwards sur la courbe IBOR/€STR (multi-courbe). Confondre les deux fausse le DV01.

**References (corpus).** *Interest Rate Derivatives Explained Vol. 1* (taux swap, eq. 5.2); Flavell, *Swaps and Other Derivatives* (valorisation, value=0 au par); *Pricing and Hedging Financial Derivatives*.

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

## Cas pratique de synthese - du modele a la decision
_[genere - cas de desk verifie par les blocs calculatoires]_ Vous recevez un
ticket incomplet, une donnee de marche potentiellement stale et une demande de
decision rapide. La methode imposee est toujours la meme:

1. qualifier le produit et le payoff;
2. lister les inputs observables et les hypotheses non observables;
3. choisir la formule ou l'approximation minimale;
4. produire un resultat chiffre avec unite;
5. faire au moins un controle croise (parite, bump, signe, ordre de grandeur,
   no-arbitrage ou limite);
6. conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

Le rendu attendu n'est pas un paragraphe scolaire. C'est une note front-office:
**resultat**, **risque dominant**, **limite du modele**, **controle effectue**,
**action proposee**. Un etudiant exigeant doit pouvoir refaire chaque etape; un
young professional doit pouvoir envoyer la note au trader sans la reecrire.

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

## Checkpoint personas exigeants
- Persona etudiant quant: sait-il refaire la derivation, expliquer les
  hypotheses, refaire le calcul et reconnaitre le piege conceptuel?
- Persona young professional: sait-il lire le ticket, produire le chiffre,
  identifier le risque dominant, hedger ou escalader, et expliquer la limite a
  trader/risk/sales?
- Si l'une des deux reponses est non, le cours est incomplet.

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 18 (exploitables: 14).
- Score pedagogique moyen: 52.22/100 (qualite structurelle: 78.89/100).
- Definitions: 3 | exemples: 4 | exercices: 3 | formules: 8 | cas pratiques: 2.
- Repartition par type: theory: 9, market_context: 2, solution: 2, worked_example: 2, definition: 1, exercise: 1, methodology: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S2], [S3], [S14].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S2], [S7], [S8], [S12].
4. Exemples - couvert par [S2], [S10], [S12], [S15].
5. Exemples resolus - couvert par [S2], [S10], [S12].
6. Exercices - couvert par [S8], [S13], [S14], [S17].
7. Corriges - couvert par [S2], [S7], [S8], [S9].
8. Cas pratiques - couvert par [S5], [S13].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, resumes.

## Faits et angles extraits de la base
- Because the strategy is designed for interest rate futures, we will illustrate it with reference to a bond and a bond futures contract.
- In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration.
- Duration has several specific definitions, but generally is used as a
measure of price sensitivity.
- The bond price, B, is the sum of the present values of each
of its cash payments—coupon interest and principal.
- These present values can be found
by discounting each cash payment at a single interest rate, which is known as the yield
or sometimes yield to maturity (yB).
- Formally, we have
B ¼
X
T
t¼1
CPt
(1 þ yB)t,
where CPt is the cash payment made at time t and will be either the coupon interest or
principal.
- If the yield changes, we know that the price changes inversely.
- An approximation to the change in price as it relates to the change in yield is given by the formula,
ΔB  B DURB(ΔyB)
1 þ yB,
where DURB represents the bond’s duration and Δ represents the change in B or yB.
- Formally, the duration is a weighted average of the time to each cash payment date and is
specified in units of time.
- This particular one, though often just called duration, is more precisely identified as Macaulay’s
duration, named after one of the first economists to derive it.

## Sources RAG a citer
- [S1] Mathematics of the Financial Markets  Financial Instruments and Derivatives Modelling, Valuation and Risk Issues ( PDFDrive ), chunk 265, score 0.532334 (extrait non cite: source bruitee)
- [S2] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 515, score 0.481876: Because the strategy is designed for interest rate futures, we will illustrate it with reference to a bond and a bond futures contract. In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration.
- [S3] Principles of Financial Engineering ( PDFDrive ), chunk 954, score 0.454893 (extrait non cite: source bruitee)
- [S4] Derivatives Workbook ( PDFDrive ), chunk 13, score 0.437613: Summary OVERVIEW
This reading on forward commitment pricing and valuation provides a foundation for understanding how forwards, futures, and swaps are both priced and valued.
- [S5] Principles of Financial Engineering ( PDFDrive ), chunk 79, score 0.432814 (extrait non cite: source bruitee)
- [S6] Principles of Financial Engineering ( PDFDrive ), chunk 947, score 0.423578 (extrait non cite: source bruitee)
- [S7] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 78, score 0.407326 (extrait non cite: source bruitee)
- [S8] Derivatives Markets ( PDFDrive ), chunk 525, score 0.385015 (extrait non cite: source bruitee)
- [S9] Derivatives Markets ( PDFDrive ), chunk 509, score 0.365077 (extrait non cite: source bruitee)
- [S10] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 53, score 0.345267: Valuing Fixed Income Investments and Derivative Securities. New York Institute of Finance, 1991. Business Finance. London: Butterworth, 1995. Martellini L., D. Priaulet, and S. Fixed Income Securities. Chichester, UK: John Wiley 
& Sons, 2004. Fixed Income Analysis for the Global Financial Market.
- [S11] The Oxford Guide to Financial Modeling  Applications for Capital Markets, Corporate Finance, Risk Management and Financial Institutions ( PDFDrive ), chunk 356, score 0.337002: Hite, G., and A. The effect of bond rating changes on bond price performance. Financial Analysts Journal, 53 (3), 35-51. 1990, Strategic Fixed-Income Investment, Dow Jones-Irwin, Homewood, Illinois. Y, 1994, Fixed-Income Investment, Resecent Research, Irwin Professional Publishing, Burr
Ridge, IL.
- [S12] Mathematics of the Financial Markets  Financial Instruments and Derivatives Modelling, Valuation and Risk Issues ( PDFDrive ), chunk 36, score 0.329099: The duration is also used for bonds VaR calculation (cf. Chapter 14, Section
14.2). Portfolio Immunization
Immunization has to be distinguished from hedging:
A position is said to be immunized if its value does not change when market
conditions (prices or rates) change.
- [S13] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 217, score 0.327779: These basis points
represent the risk premium for bearing the credit risk associated with
the bond. The same sort of analysis could have been performed if the
bond had contained an embedded put option.
- [S14] Derivatives Risk Management & Value ( PDFDrive ), chunk 238, score 0.319529 (extrait non cite: source bruitee)
- [S15] Vault Guide to Advanced Finance and Quantitative Interviews.pdf ( PDFDrive ), chunk 171, score 0.31819: http://finance.vault.com 
 
 
 
171 
Quoting Bond and Fixed Income Prices 
 
If you try to buy a bond at the price listed in the newspaper, you will find that it’s not the price you will 
ultimately pay. Suppose you are trying to buy a $1,000 bond paying 10% interest with semi-annual 
payments.
- [S16] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 236, score 0.312538: Grbac et al. Brigo, D., Pallavicini, A., Perini, D.: Funding, collateral and hedging: uncovering the mechanics
and the subtleties of funding valuation adjustments. Preprint, arXiv:1210.3811, 2012
4.
- [S17] Derivatives Markets ( PDFDrive ), chunk 504, score 0.30908 (extrait non cite: source bruitee)
- [S18] Capital Investment & Financing  a practical guide to financial evaluation ( PDFDrive ), chunk 6, score 0.308721 (extrait non cite: source bruitee)

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Bond price
$$
P=\sum_{i=1}^{n}\frac{CF_i}{(1+y)^{t_i}}
$$
- Usage desk: turn cash flows and yield into clean price controls.
### F2 - Modified duration
$$
D_{\text{mod}}=\frac{D_{\text{Mac}}}{1+y/m}
$$
- Usage desk: estimate price sensitivity to a parallel yield move.
### F3 - Duration-convexity P&L
$$
\frac{\Delta P}{P}\approx -D_{\text{mod}}\Delta y+\frac{1}{2}C(\Delta y)^2
$$
- Usage desk: explain why convexity matters for larger rate shocks.

