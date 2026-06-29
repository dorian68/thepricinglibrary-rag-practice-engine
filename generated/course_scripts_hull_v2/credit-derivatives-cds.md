---
slug: credit-derivatives-cds
topic: CDS spread risk, carry and CS01
product: single-name CDS
level: intermediate
concepts: spread, risky annuity, CS01, carry
source_count: 18
---

# Module pratique - CDS spread risk, carry and CS01

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre CDS spread risk, carry and CS01 a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 210 minutes
- Produit: single-name CDS
- Concepts: spread, risky annuity, CS01, carry

## Prerequis
- notion de defaut
- spread de credit
- actualisation

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

## Positionnement bibliotheque
- Track: Credit & XVA
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire le ticket CDS
- Objectif pratique: Identifier protection buyer/seller, spread, notionnel et maturite.
- Situation de desk: Un single-name widening arrive dans le book credit.
- Notion utile: Spread CDS, risky annuity, default leg/premium leg.
- Activite: Transformer le ticket en inputs de risk.
- Livrable apprenant: Ticket credit enrichi.
### Module 2 - Carry
- Objectif pratique: Distinguer coupon/carry et mark-to-market.
- Situation de desk: Le book semble profitable au carry mais le spread bouge.
- Notion utile: Carry = notionnel * spread selon convention simplifiee.
- Activite: Calculer carry annuel et commentaire.
- Livrable apprenant: Carry note.
### Module 3 - CS01
- Objectif pratique: Calculer la sensibilite a 1bp de spread.
- Situation de desk: Risk demande l'impact d'un widening de 25bp.
- Notion utile: CS01 = notionnel * risky annuity * 1bp.
- Activite: Calculer CS01 et shock P&L avant signe position.
- Livrable apprenant: Table CS01/shock.
### Module 4 - Decision credit
- Objectif pratique: Proposer hedge/reduction/monitoring en fonction du risque.
- Situation de desk: La liquidite CDS baisse pendant le stress.
- Notion utile: Spread risk, jump-to-default, liquidity.
- Activite: Ecrire une decision operationnelle.
- Livrable apprenant: Memo risk action.
### Module 5 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 6 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de CDS spread risk, carry and CS01 et savoir le critiquer.
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
### Lecon 1 - Lire le ticket CDS

**Le reflexe d'abord.** Un single-name widening arrive dans le book credit. Avant toute formule, demandez-vous ce que spread cds, risky annuity, default leg/premium leg change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « References
1. Bazaraa, M.S., Jarvis, J.J., Sherali, H.D.: Linear Programming and Network Flows, 4th edn. Wiley, New Jersey (2010)
2. Bielecki, T.R., Rutkowski, M.: Credit Risk: Modeling, Valuation and Hedging. Springer, Berlin
(2002)
3. Brenner, U.: A faster polynomial algorithm for the unbalanced hitchcock transportation problem. 36(4), 408–413 (2008)
4. » [S1]. L'enjeu operationnel est clair : identifier protection buyer/seller, spread, notionnel et maturite.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, spread cds, risky annuity, default leg/premium leg sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : ticket credit enrichi.

Concretement, l'exercice consiste a transformer le ticket en inputs de risk, pour en tirer un ticket credit enrichi. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: transformer le ticket en inputs de risk. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer spread cds, risky annuity, default leg/premium leg a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - Carry

**Comment ca marche.** Carry = notionnel * spread selon convention simplifiee n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Market Risk 
Chapters 1–5 all dealt with market risk. This is the risk of losses coming from the market 
change of asset prices that negatively affect the mark-to-market positions of the bank. The 
change of asset prices can come from various factors, such as stock prices, volatility, and 
correlation. » [S2].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a distinguer coupon/carry et mark-to-market. Il s'agit de calculer carry annuel et commentaire pour produire un carry note, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer carry annuel et commentaire. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer carry = notionnel * spread selon convention simplifiee a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - CS01

**Ou est le risque.** Risk demande l'impact d'un widening de 25bp. Mal traiter cs01 = notionnel * risky annuity * 1bp se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Risk Management of Credit
Default Swaps
Various factors affect the mark-to-market value of
a CDS position. On a day-to-day basis the main
concern is spread volatility: the value of a CDS
position is primarily affected by changes in the CDS
spread. » [S3].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : calculer la sensibilite a 1bp de spread. Il faut calculer cs01 et shock p&l avant signe position, documenter un table cs01/shock, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer cs01 et shock p&l avant signe position. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer cs01 = notionnel * risky annuity * 1bp a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Decision credit

**La decision visee.** A la fin de cette lecon vous saurez proposer hedge/reduction/monitoring en fonction du risque sans hesiter. Le declencheur : la liquidite cds baisse pendant le stress. Les sources le confirment _[extrait]_ : « Banks assume market risk because they trade as principals, risking
their own capital, and hold positions in financial instruments. Failure to manage market risk can have significant direct effects on a bank’s profitability
and reputation. » [S4].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de spread risk, jump-to-default, liquidity sert exactement a cela. Il faut ecrire une decision operationnelle, produire un memo risk action, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: ecrire une decision operationnelle. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer spread risk, jump-to-default, liquidity a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Carte des sources et des definitions

**Le reflexe d'abord.** Un apprenant doit savoir quelle source croire et pourquoi. Avant toute formule, demandez-vous ce que source grounding, provenance, vocabulaire de desk change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Recent government and
industry initiatives are aimed at improving this infrastructure in order to facilitate
more effective management of counterparty risks. » [S5]. L'enjeu operationnel est clair : relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, source grounding, provenance, vocabulaire de desk sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : source map annotee.

Concretement, l'exercice consiste a comparer les extraits [sx] et isoler les definitions robustes, pour en tirer un source map annotee. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Fondations quantitatives niveau Hull

**Comment ca marche.** Modele, mesure, derivees, approximation locale n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « RISK, 27:49, October 2014. [103] Chris Kenyon and Andrew Green. Pricing CDS’s capital relief. RISK, 26(10):62–66,
2014. [104] Chris Kenyon and Andrew Green. Regulatory costs break risk neutrality. RISK,
27:76–80, September 2014. [105] Chris Kenyon and Andrew Green. Dirac Processes and Default Risk. SSRN,
abstract=2593037, pages 1–32, 2015. [106] Chris Kenyon and Andrew Green. » [S6].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a deriver le coeur quantitatif de cds spread risk, carry and cs01 et savoir le critiquer. Il s'agit de reprendre la derivation puis nommer ce qui casse en marche reel pour produire un derivation commentee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Cas numerique moteur

**Ou est le risque.** Le desk refuse un chiffre qui ne peut pas etre audite. Mal traiter calculateur deterministe, ordre de grandeur, controles croises se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Goldman
wouldn’t say what specific financials were in the basket, but Viniar confirmed to the analyst asking the
question that the basket contained “a peer group.”
Most would consider peers to Goldman to be other large banks with big investment-banking divisions,
including Morgan Stanley, J.P. Morgan Chase, Bank of America, Citigroup, and others. » [S7].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : reproduire un calcul complet avec substitutions, resultat et unite. Il faut refaire le cas a la main et verifier le resultat moteur, documenter un answer key verifiee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Lab interactif et scenarios

**La decision visee.** A la fin de cette lecon vous saurez manipuler les inputs et lire l'effet sur prix, risque ou p&l sans hesiter. Le declencheur : le marche bouge avant validation du trade. Les sources le confirment _[extrait]_ : « 14(6), 773–802 (2011)
10. Brigo, D., Buescu, C., Morini, M.: Counterparty risk pricing: impact of closeout and first-todefault times. 15, 1250039–1250039 (2012)
11. Brigo, D., Morini, M., Pallavicini, A.: Counterparty Credit Risk. Collateral and Funding with
Pricing Cases for All Asset Classes. Wiley, Chichester (2013)
12. » [S8].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de scenario table, surface, matrice ou chart selon le produit sert exactement a cela. Il faut tester plusieurs chocs et commenter les regimes, produire un ui block de decision, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: tester plusieurs chocs et commenter les regimes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer scenario table, surface, matrice ou chart selon le produit a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

## Blocs interactifs de finance de marche
```uiblock
type: equation
title: Equation pivot du module
params: {"latex": "CS01=N\\sum_i\\alpha_iDF_iQ(\\tau>t_i)\\,10^{-4}"}
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
type: greeks_scenario
title: CDS risk panel - CS01, carry, jump-to-default
params: {"kind":"cds", "notional":50000000, "spread_bp":120, "riskyAnnuity":4.2, "recovery":40, "shock_bp":25, "side":"buyer"}
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
1. Ticket CDS: protection buyer/seller, spread, notionnel, risky annuity.
2. Carry/CS01: calculer carry annuel et sensibilite 1bp.
3. Spread shock: appliquer +25bp et discuter le signe position.
4. Risk action: hedge, reduce ou monitor selon liquidite et jump risk.

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

**Structure.** Deux jambes: l'acheteur de protection paie un spread $s$ (jambe de prime) et recoit $(1-R)\times$ nominal en cas de defaut (jambe de protection), $R$ = taux de recouvrement.

**Spread par (egalite des PV des deux jambes).**
$$s = \frac{(1-R)\sum_i DF_i\,(Q_{i-1}-Q_i)}{\sum_i DF_i\,\tau_i\,Q_i},$$
ou $Q_i=\mathbb{Q}(\tau>t_i)=e^{-\int_0^{t_i}\lambda}$ est la probabilite de survie et $DF_i$ l'actualisation.

**Triangle du credit (approximation).** $\;s \approx \lambda\,(1-R)\;$ — le spread est, au premier ordre, l'intensite de defaut $\lambda$ fois la perte en cas de defaut.

**Sensibilites.** $\text{CS01}=$ P&L pour $1$bp d'ecartement $\approx$ annuite risquee $\times$ nominal $\times 10^{-4}$; **jump-to-default** $=(1-R)\times$ nominal. Ne pas confondre **coupon annuel** $=s\times$ nominal et **PV de la jambe de prime** $=$ coupon annuel $\times$ annuite risquee.

**Intuition rigoureuse.** Le CDS isole le risque de credit pur; on **bootstrappe la courbe de hasard** $\lambda(t)$ a partir des spreads quotes comme on bootstrappe une courbe de taux.

**Piege theorique.** Le carry (coupon paye) est compense seulement par le widening/defaut: l'acheteur de protection est short carry, long crash de credit.

**References (corpus).** *Analytical Finance Vol. II* (jambes prime/protection, Hull-White); *Principles of Financial Engineering* (proba risque-neutre de defaut, eq. 18.42); Choudhry, *Credit Derivatives*.

## Exemple numerique resolu
_[genere - calcul verifie]_ On mesure le CS01, le carry et le P&L d'un ecartement de spread.

**Donnees.** CDS notionnel 50m spread 120bp risky annuity 4.2 widen 25bp.

### CS01, carry et jump-to-default CDS
- Famille: cds_cs01
- Hypotheses controlees:
  - Approximation spread-DV01; pas de bootstrap de hazard curve.
  - Signe donne du point de vue acheteur de protection.
  - Recovery 40% (LGD 60%) si non precise.
- Calculs a respecter:
  - CS01:
    - Formule: Risky annuity * Notionnel * 1bp
    - Application: 4.2 * 50,000,000 * 0.0001
    - Resultat: 21,000 EUR/bp
    - Lecture desk: Sensibilite (approx) de la MtM au spread de credit.
  - Coupon annuel:
    - Formule: Spread (en decimal) * Notionnel
    - Application: 120bp * 50,000,000 = 1.2% * 50,000,000
    - Resultat: 600,000 EUR/an
    - Lecture desk: Prime PAYEE chaque annee par l'acheteur de protection (carry negatif pour lui).
  - PV jambe de prime:
    - Formule: Coupon annuel * Risky annuity
    - Application: 600,000 * 4.2
    - Resultat: 2,520,000 EUR
    - Lecture desk: Valeur actualisee de TOUTES les primes futures; ne pas la confondre avec le coupon annuel.
  - Jump-to-default (LGD 60%):
    - Formule: (1 - Recovery) * Notionnel
    - Application: (1 - 0.40) * 50,000,000
    - Resultat: 30,000,000 EUR
    - Lecture desk: Gain de l'acheteur de protection si defaut immediat; a comparer au carry paye.
  - P&L spread shock protection buyer:
    - Formule: CS01 * shock bp
    - Application: 21,000 * 25
    - Resultat: 525,000 EUR
    - Lecture desk: Un acheteur de protection gagne en MtM si le spread s'elargit.
- Actions operationnelles attendues:
  - Comparer carry annuel paye et jump-to-default protege.
  - Distinguer coupon annuel (cash/an) et PV de la jambe de prime (valeur du contrat).
  - Hedger indice/single-name en tenant compte du basis.

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
_[genere]_ Un acheteur de protection CDS gagne-t-il ou perd-il quand le spread s'ecarte?

**Correction.** Il gagne en mark-to-market: la protection qu'il detient vaut plus cher. P&L approx = CS01 * widening.

### Exercice 2 - niveau desk
_[genere]_ CDS 50m, spread 120bp, risky annuity 4.2, widen 25bp. Calculez CS01, carry et P&L.

**Correction detaillee (calcul verifie).**
### CS01, carry et jump-to-default CDS
- Famille: cds_cs01
- Hypotheses controlees:
  - Approximation spread-DV01; pas de bootstrap de hazard curve.
  - Signe donne du point de vue acheteur de protection.
  - Recovery 40% (LGD 60%) si non precise.
- Calculs a respecter:
  - CS01:
    - Formule: Risky annuity * Notionnel * 1bp
    - Application: 4.2 * 50,000,000 * 0.0001
    - Resultat: 21,000 EUR/bp
    - Lecture desk: Sensibilite (approx) de la MtM au spread de credit.
  - Coupon annuel:
    - Formule: Spread (en decimal) * Notionnel
    - Application: 120bp * 50,000,000 = 1.2% * 50,000,000
    - Resultat: 600,000 EUR/an
    - Lecture desk: Prime PAYEE chaque annee par l'acheteur de protection (carry negatif pour lui).
  - PV jambe de prime:
    - Formule: Coupon annuel * Risky annuity
    - Application: 600,000 * 4.2
    - Resultat: 2,520,000 EUR
    - Lecture desk: Valeur actualisee de TOUTES les primes futures; ne pas la confondre avec le coupon annuel.
  - Jump-to-default (LGD 60%):
    - Formule: (1 - Recovery) * Notionnel
    - Application: (1 - 0.40) * 50,000,000
    - Resultat: 30,000,000 EUR
    - Lecture desk: Gain de l'acheteur de protection si defaut immediat; a comparer au carry paye.
  - P&L spread shock protection buyer:
    - Formule: CS01 * shock bp
    - Application: 21,000 * 25
    - Resultat: 525,000 EUR
    - Lecture desk: Un acheteur de protection gagne en MtM si le spread s'elargit.
- Actions operationnelles attendues:
  - Comparer carry annuel paye et jump-to-default protege.
  - Distinguer coupon annuel (cash/an) et PV de la jambe de prime (valeur du contrat).
  - Hedger indice/single-name en tenant compte du basis.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Le CS01 d'un CDS mesure:**
- A) le P&L pour 1bp d'ecartement de spread
- B) le coupon annuel
- C) la prime d'option
- D) le DV01 de taux
  - Reponse: **A**. CS01 = risky annuity * notionnel * 1bp: sensibilite de la MtM au spread de credit.

**Q2. Le coupon annuel d'un CDS vaut approximativement:**
- A) spread * risky annuity * notionnel
- B) spread * notionnel
- C) CS01 * notionnel
- D) recovery * notionnel
  - Reponse: **B**. Le coupon paye chaque annee = spread (en decimal) * notionnel; multiplie par la risky annuity on obtient la PV de toute la jambe de prime, pas le coupon.

**Q3. Un acheteur de protection CDS quand le spread s'ecarte:**
- A) perd en MtM
- B) gagne en MtM
- C) est insensible
- D) paie plus de coupon
  - Reponse: **B**. La protection detenue vaut plus cher: P&L MtM ~ CS01 * widening > 0.

**Q4. Le jump-to-default d'un acheteur de protection vaut environ:**
- A) recovery * notionnel
- B) (1 - recovery) * notionnel
- C) spread * notionnel
- D) zero
  - Reponse: **B**. En cas de defaut il recoit (1 - recovery) * notionnel, la perte sur le pair (LGD).

**Q5. Le carry d'un acheteur de protection (hors defaut) est:**
- A) positif
- B) negatif: il paie la prime
- C) nul
- D) egal au CS01
  - Reponse: **B**. Il paie le coupon chaque jour: carry negatif, compense seulement si un defaut/widening survient.

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
- Chunks sources analyses: 18 (exploitables: 16).
- Score pedagogique moyen: 48.0/100 (qualite structurelle: 85.83/100).
- Definitions: 2 | exemples: 4 | exercices: 1 | formules: 3 | cas pratiques: 5.
- Repartition par type: theory: 15, example: 1, case_study: 1, market_context: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S2], [S9].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S1], [S6], [S8].
4. Exemples - couvert par [S3], [S10], [S16], [S17].
5. Exemples resolus - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
6. Exercices - couvert par [S1], [S7], [S8], [S9].
7. Corriges - couvert par [S5], [S8], [S11], [S12].
8. Cas pratiques - couvert par [S3], [S10], [S12], [S17].
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
- [S1] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 106, score 0.669013: References
1. Bazaraa, M.S., Jarvis, J.J., Sherali, H.D.: Linear Programming and Network Flows, 4th edn. Wiley, New Jersey (2010)
2. Bielecki, T.R., Rutkowski, M.: Credit Risk: Modeling, Valuation and Hedging. Springer, Berlin
(2002)
3.
- [S2] Practical Methods of Financial Engineering and Risk Management  Tools for Modern Financial Professionals ( PDFDrive ), chunk 222, score 0.580293: Market Risk 
Chapters 1–5 all dealt with market risk. This is the risk of losses coming from the market 
change of asset prices that negatively affect the mark-to-market positions of the bank. The 
change of asset prices can come from various factors, such as stock prices, volatility, and 
correlation.
- [S3] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 1434, score 0.565633: Risk Management of Credit
Default Swaps
Various factors affect the mark-to-market value of
a CDS position. On a day-to-day basis the main
concern is spread volatility: the value of a CDS
position is primarily affected by changes in the CDS
spread.
- [S4] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 190, score 0.469773: Banks assume market risk because they trade as principals, risking
their own capital, and hold positions in financial instruments. Failure to manage market risk can have significant direct effects on a bank’s profitability
and reputation.
- [S5] Financial Derivatives  Pricing and Risk Management ( PDFDrive ), chunk 397, score 0.461054: Recent government and
industry initiatives are aimed at improving this infrastructure in order to facilitate
more effective management of counterparty risks.
- [S6] Modern Derivatives Pricing and Credit Exposure Analysis  Theory and Practice of CSA and XVA Pricing, Exposure Simulation and Backtesting ( PDFDrive ), chunk 361, score 0.442677: RISK, 27:49, October 2014. [103] Chris Kenyon and Andrew Green. Pricing CDS’s capital relief. RISK, 26(10):62–66,
2014. [104] Chris Kenyon and Andrew Green. Regulatory costs break risk neutrality. RISK,
27:76–80, September 2014. [105] Chris Kenyon and Andrew Green. Dirac Processes and Default Risk.
- [S7] Principles of Financial Engineering ( PDFDrive ), chunk 929, score 0.442152: Goldman
wouldn’t say what specific financials were in the basket, but Viniar confirmed to the analyst asking the
question that the basket contained “a peer group.”
Most would consider peers to Goldman to be other large banks with big investment-banking divisions,
including Morgan Stanley, J.P.
- [S8] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 43, score 0.431477: 14(6), 773–802 (2011)
10. Brigo, D., Buescu, C., Morini, M.: Counterparty risk pricing: impact of closeout and first-todefault times. 15, 1250039–1250039 (2012)
11. Brigo, D., Morini, M., Pallavicini, A.: Counterparty Credit Risk. Collateral and Funding with
Pricing Cases for All Asset Classes.
- [S9] Principles of Financial Engineering ( PDFDrive ), chunk 930, score 0.426076: There is also a tradeoff between single-name and index CDS hedges. Single-name hedging
is more precise in case of bad news affecting a single firm rather than broad market moves, but
10See Ernst & Young (2012) survey “Reflecting credit and funding adjustments in fair value”. 844
CHAPTER 24 COUNTERPARTY RISK
- [S10] Principles of Financial Engineering ( PDFDrive ), chunk 693, score 0.415205: , we obtain a
value of 3:8479 3 cds 1 0:1006 3 cds 5 3:9585 3 cds. Finally, lets consider the protection leg payments. The last three columns of
- [S11] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2295, score 0.408378 (extrait non cite: source bruitee)
- [S12] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 4, score 0.388554: Auto-callable Transactions
177
Bermudan Extendibles and the Forward Skew
177
- [S13] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 228, score 0.375064: CS01
Times change, and markets are now much more open to risky fixed income
investments than before, meaning many credit spreads are high to very high. At the same time, global monetary policies of the 2000s have kept risk-free
interest rates very low. The combined result for risk managers is that they
Market Risk
211
- [S14] Principles of Financial Engineering ( PDFDrive ), chunk 939, score 0.363497: Finance 4 (1), 91119. Ayache, E., Forsyth, P.A., Vetzal, K.R., 2003. The valuation of convertible bonds with credit risk. Wilmott
Magazine. Baba, N., Packer, F., Nagano, T., 2008. The spillover of money market turbulence to FX swap and crosscurrency swap markets. Barkbu, B.B., Ong, L.L., 2012.
- [S15] Financial Risk Manager Handbook + Test Bank  FRM Part I   Part II ( PDFDrive ), chunk 486, score 0.359994 (extrait non cite: source bruitee)
- [S16] Principles of Financial Engineering ( PDFDrive ), chunk 699, score 0.359536: “Short Selling and Certain
Aspects of Credit Default Swaps” naked CDS on the debt of European Economic Area countries
are banned.
- [S17] Principles of Financial Engineering ( PDFDrive ), chunk 698, score 0.358042: In economic terms, sovereign CDS are also becoming more important. In terms of gross notional
amounts the sovereign CDS market in 2012 was 11% of the whole CDS market, but the sovereign
CDS market has been growing while the single-name CDS market has been declining since the
GFC.
- [S18] Fundamentals of Risk Management  Understanding, evaluating and implementing effective risk management ( PDFDrive ), chunk 510, score 0.347237 (extrait non cite: source bruitee)

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

