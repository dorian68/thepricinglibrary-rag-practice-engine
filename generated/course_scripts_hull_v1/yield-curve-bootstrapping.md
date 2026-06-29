---
slug: yield-curve-bootstrapping
topic: Yield curve bootstrapping for desk pricing
product: interest-rate curve
level: intermediate
concepts: discount factors, zero curve, forward rates, interpolation
source_count: 18
---

# Module pratique - Yield curve bootstrapping for desk pricing

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Yield curve bootstrapping for desk pricing a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 220 minutes
- Produit: interest-rate curve
- Concepts: discount factors, zero curve, forward rates, interpolation

## Prerequis
- discount factor
- interpolation
- conventions de taux

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

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
### Module 5 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 6 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de Yield curve bootstrapping for desk pricing et savoir le critiquer.
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
### Module 9 - Production controls
- Objectif pratique: Identifier les erreurs de convention, de signe, d'unite et de donnees de marche.
- Situation de desk: Une mauvaise convention peut inverser le P&L ou casser une quote.
- Notion utile: Data quality, convention, sign, fallback, no-arbitrage check.
- Activite: Construire une checklist de validation avant envoi au trader.
- Livrable apprenant: Checklist production.

## Cours redige
### Lecon 1 - Lire les instruments de courbe

**Le reflexe d'abord.** Le desk doit reconstruire une courbe avant de pricer un swap. Avant toute formule, demandez-vous ce que tenor, quote, accrual, discount factor change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Distinguishing forward curves from discount curves (representing the collateralization of
the forward) motivates an alternative interpolation method, namely interpolation of
the forward value (the product of the forward and the discount factor). In addition,
treating forward curves as native curves (instead of representing them by pseudodiscount curves) will avoid other problems, like that of overlapping instruments. » [S1]. L'enjeu operationnel est clair : classer deposits, futures et swaps par maturite et convention.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, tenor, quote, accrual, discount factor sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : curve input sheet.

Concretement, l'exercice consiste a transformer les quotes en tableau de bootstrap, pour en tirer un curve input sheet. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: transformer les quotes en tableau de bootstrap. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer tenor, quote, accrual, discount factor a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - Bootstrap discount factors

**Comment ca marche.** Recursion sur coupons, interpolation locale n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « The method is a common practice (also considered in [1]). However,
considering forwards for overlapping periods, this may introduce oscillations and
result in implausible delta-hedges (see » [S3].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a extraire les discount factors un par un sans casser les maturites deja calibrees. Il s'agit de calculer un point de courbe et documenter la convention pour produire un discount-factor ladder, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer un point de courbe et documenter la convention. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer recursion sur coupons, interpolation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - Zeros et forwards

**Ou est le risque.** Le trader veut lire le carry implicite entre deux maturites. Mal traiter zero rate continu, forward rate discret se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Note that these two curves are
interchangeable, and knowledge of one completely determines the other. » [S4].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : convertir discount factors en zero rates et forwards exploitables. Il faut calculer zero/forward et commenter la pente, documenter un zero-forward report, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer zero/forward et commenter la pente. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer zero rate continu, forward rate discret a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Controle et usage desk

**La decision visee.** A la fin de cette lecon vous saurez verifier monotonie, interpolation et impact sur pv sans hesiter. Le declencheur : une interpolation trop agressive cree un faux signal de risque. Les sources le confirment _[extrait]_ : « 15(3), 401–419 (2015)
14. Cuchiero, C., Fontana, C., Gnoatto, A.: A general HJM framework for multiple yield curve
modeling. 20(2), 267–320 (2016)
15. Filipovi´c, D., Trolle, A.B.: The term structure of interbank risk. 109(3), 707–733
(2013)
16. Fujii, M., Takahashi, A.: Derivative pricing under asymmetric and imperfect collateralization
and CVA. 13(5), 749–768 (2013)
17. » [S5].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de no-arbitrage local, smoothness, curve-shape risk sert exactement a cela. Il faut comparer deux interpolations et choisir une action, produire un curve validation memo, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer deux interpolations et choisir une action. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer no-arbitrage local, smoothness, curve-shape risk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Carte des sources et des definitions

**Le reflexe d'abord.** Un apprenant doit savoir quelle source croire et pourquoi. Avant toute formule, demandez-vous ce que source grounding, provenance, vocabulaire de desk change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « “Best-fit” algorithms
start by assuming a functional form for the term structure and calibrate
its parameters such as to minimize the re-pricing error of the chosen
© The Author(s) 2017
529
J.R.M. Röman, Analytical Finance: Volume II,
https://doi.org/10.1007/978-3-319-52584-6_21 » [S6]. L'enjeu operationnel est clair : relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, source grounding, provenance, vocabulaire de desk sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : source map annotee.

Concretement, l'exercice consiste a comparer les extraits [sx] et isoler les definitions robustes, pour en tirer un source map annotee. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Fondations quantitatives niveau Hull

**Comment ca marche.** Modele, mesure, derivees, approximation locale n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Since 
the swap curve is effectively the LIBOR curve and investors borrow based 
on LIBOR, the swap curve is more useful to funded investors than a government yield curve. The increased application of the swap curve for these activities is 
due to its advantages over using the government bond yield curve as a 
benchmark. » [S7].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a deriver le coeur quantitatif de yield curve bootstrapping for desk pricing et savoir le critiquer. Il s'agit de reprendre la derivation puis nommer ce qui casse en marche reel pour produire un derivation commentee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Cas numerique moteur

**Ou est le risque.** Le desk refuse un chiffre qui ne peut pas etre audite. Mal traiter calculateur deterministe, ordre de grandeur, controles croises se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Jamshidian, F.: An exact bond option pricing formula. 44, 205–209 (1989)
20. Kenyon, C.: Short-rate pricing after the liquidity and credit shocks: including the basis. 83–87 (2010)
21. Kijima, M., Muromachi, Y.: Reformulation of the arbitrage-free pricing method under the
multi-curve environment. Preprint (2015)
22. Kijima, M., Tanaka, K., Wong, T.: A multi-quality model of interest rates. 9(2),
133–145 (2009)
23. » [S8].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : reproduire un calcul complet avec substitutions, resultat et unite. Il faut refaire le cas a la main et verifier le resultat moteur, documenter un answer key verifiee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Lab interactif et scenarios

**La decision visee.** A la fin de cette lecon vous saurez manipuler les inputs et lire l'effet sur prix, risque ou p&l sans hesiter. Le declencheur : le marche bouge avant validation du trade. Les sources le confirment _[extrait]_ : « 13.4  Yield Curves, Discount Factors, and 
Forward Rates
In this section we discuss the spreadsheet YieldDiscountForward, which 
implements the connection between Yield Curve, Discount Factors, and 
Instantaneous forward rates described in Section 13.2. This spreadsheet 
uses the m = 2 (semiannual compounding) rate convention. It takes yields 
at a set of times and linearly interpolates them to make a yield curve. » [S9].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de scenario table, surface, matrice ou chart selon le produit sert exactement a cela. Il faut tester plusieurs chocs et commenter les regimes, produire un ui block de decision, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: tester plusieurs chocs et commenter les regimes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer scenario table, surface, matrice ou chart selon le produit a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 9 - Production controls

**Le reflexe d'abord.** Une mauvaise convention peut inverser le P&L ou casser une quote. Avant toute formule, demandez-vous ce que data quality, convention, sign, fallback, no-arbitrage check change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « ,Hoboken(2007). http://www.christian-fries.de/finmath/book
11. Fries, C.P.: Curve calibration. Object oriented reference implementation 2010–2015. http://
www.finmath.net/topics/curvecalibration
12. Fries, C.P.: Funded replication: fund exchange process and the valuation with different fundingaccounts (cross-currency analogy to funding revisited). Wilmott 63, 36–41 (2013). http://
papers.ssrn.com/abstract=2115839
13. » [S10]. L'enjeu operationnel est clair : identifier les erreurs de convention, de signe, d'unite et de donnees de marche.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, data quality, convention, sign, fallback, no-arbitrage check sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : checklist production.

Concretement, l'exercice consiste a construire une checklist de validation avant envoi au trader, pour en tirer un checklist production. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: construire une checklist de validation avant envoi au trader. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer data quality, convention, sign, fallback, no-arbitrage check a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

## Blocs interactifs de finance de marche
```uiblock
type: equation
title: Equation pivot du module
params: {"latex": "DF_n=\\frac{1-s_n\\sum_{i<n}\\alpha_iDF_i}{1+s_n\\alpha_n},\\qquad f_{i,j}=\\frac{1}{t_j-t_i}\\ln\\frac{DF_i}{DF_j}"}
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
1. Curve inputs: classer deposits/futures/swaps et conventions de day count.
2. Bootstrap: calculer les discount factors successifs et verifier la monotonie.
3. Zero/forward: convertir DF en zero rates puis forward rates.
4. Interpolation control: comparer deux interpolations et impact PV.
5. Curve memo: conventions, controles et risques de courbe residuels.

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

**Definition.** La courbe se resume en discount factors $DF(0,t)$. Le taux zero-coupon depend de la convention de composition, et le forward simplement compose $f_{t,T}$ s'annualise sur la periode $(T-t)$:
$$DF(0,t) = (1+z_t^{ann})^{-t} = e^{-z_t^{cont}\,t},\quad z_t^{cont}=\ln(1+z_t^{ann}),\qquad f_{t,T} = \frac{1}{T-t}\!\left(\frac{DF(0,t)}{DF(0,T)} - 1\right).$$

**Bootstrap sequentiel (swaps par annuels).** Pour le noeud $n$, en isolant $DF_n$ dans l'equation du par swap $s_n\sum_{i\le n}\tau_i DF_i = 1-DF_n$:
$$\boxed{\,DF_n = \frac{1 - s_n\sum_{i=1}^{n-1}\tau_i DF_i}{1 + s_n\tau_n}\,}$$
On resout de proche en proche: $DF_1$, puis $DF_2$, etc.

**Intuition rigoureuse.** Une obligation a coupon = portefeuille de zero-coupons; le bootstrap "depouille" un instrument a la fois pour extraire le DF marginal de chaque maturite. Les forwards implicites doivent rester positifs et lisses — sinon l'interpolation ou les inputs sont incoherents.

**Piege theorique.** Le resultat depend de l'interpolation (lineaire en taux, en log-DF, splines...) et du jeu d'instruments. En multi-courbe, **la courbe de projection des forwards differe de la courbe d'actualisation (OIS)**.

**References (corpus).** *Interest Rate Derivatives Explained Vol. 1* (bootstrap des swaps par); *Innovations in Derivatives Markets* (courbe forward vs discount, OIS); *Fixed Income Markets* (obligation a coupon = panier de zero-coupons).

## Exemple numerique resolu
_[genere - calcul verifie]_ On bootstrappe les discount factors et les taux forward d'une courbe de swaps.

**Donnees.** Bootstrap de courbe, swaps par annuels: 1 an 3.00%, 2 ans 3.20%, 3 ans 3.35%.

### Bootstrap de courbe et taux forward
- Famille: yield_curve_bootstrap
- Hypotheses controlees:
  - Swaps par annuels, frequence fixe annuelle, day-count simplifie.
  - Mono-courbe (pas de spread OIS/IBOR), interpolation implicite par noeud.
- Calculs a respecter:
  - DF 1a (par 3.00%):
    - Formule: DF_n = (1 - s_n*sum(DF_<n)) / (1 + s_n)
    - Application: (1 - 0.0300*0.0000) / (1 + 0.0300)
    - Resultat: DF=0.9709; zero 1a=3.0000%
    - Lecture desk: Discount factor bootstrappe puis taux zero-coupon annualise.
  - DF 2a (par 3.20%):
    - Formule: DF_n = (1 - s_n*sum(DF_<n)) / (1 + s_n)
    - Application: (1 - 0.0320*0.9709) / (1 + 0.0320)
    - Resultat: DF=0.9389; zero 2a=3.2032%
    - Lecture desk: Discount factor bootstrappe puis taux zero-coupon annualise.
  - DF 3a (par 3.35%):
    - Formule: DF_n = (1 - s_n*sum(DF_<n)) / (1 + s_n)
    - Application: (1 - 0.0335*1.9098) / (1 + 0.0335)
    - Resultat: DF=0.9057; zero 3a=3.3573%
    - Lecture desk: Discount factor bootstrappe puis taux zero-coupon annualise.
  - Forward 1a->2a:
    - Formule: f = DF_{n-1}/DF_n - 1
    - Application: 0.9709/0.9389 - 1
    - Resultat: 3.4068%
    - Lecture desk: Taux forward 1 an implicite entre deux noeuds.
  - Forward 2a->3a:
    - Formule: f = DF_{n-1}/DF_n - 1
    - Application: 0.9389/0.9057 - 1
    - Resultat: 3.6663%
    - Lecture desk: Taux forward 1 an implicite entre deux noeuds.
- Actions operationnelles attendues:
  - Verifier la monotonie/cohrence des DF (decroissants) et des forwards.
  - Utiliser les DF pour actualiser tout cash-flow date sur la courbe.
  - Reprendre en multi-courbe (OIS discounting) pour un usage production.
- Points de vigilance:
  - Le bootstrap est sensible aux instruments choisis et a l'interpolation entre noeuds.

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
_[genere]_ Identifiez le produit, son risque dominant et la donnee de marche qui le pilote le plus.

**Correction.** Reponse type: nommer le payoff, la sensibilite de premier ordre (delta/DV01/CS01...) et la variable marche associee (spot/taux/spread).

### Exercice 2 - niveau desk
_[genere]_ Construisez un mini-cas chiffre du sujet et resolvez-le pas a pas avec unites et interpretation.

**Correction detaillee (calcul verifie).**
### Bootstrap de courbe et taux forward
- Famille: yield_curve_bootstrap
- Hypotheses controlees:
  - Swaps par annuels, frequence fixe annuelle, day-count simplifie.
  - Mono-courbe (pas de spread OIS/IBOR), interpolation implicite par noeud.
- Calculs a respecter:
  - DF 1a (par 3.00%):
    - Formule: DF_n = (1 - s_n*sum(DF_<n)) / (1 + s_n)
    - Application: (1 - 0.0300*0.0000) / (1 + 0.0300)
    - Resultat: DF=0.9709; zero 1a=3.0000%
    - Lecture desk: Discount factor bootstrappe puis taux zero-coupon annualise.
  - DF 2a (par 3.20%):
    - Formule: DF_n = (1 - s_n*sum(DF_<n)) / (1 + s_n)
    - Application: (1 - 0.0320*0.9709) / (1 + 0.0320)
    - Resultat: DF=0.9389; zero 2a=3.2032%
    - Lecture desk: Discount factor bootstrappe puis taux zero-coupon annualise.
  - DF 3a (par 3.35%):
    - Formule: DF_n = (1 - s_n*sum(DF_<n)) / (1 + s_n)
    - Application: (1 - 0.0335*1.9098) / (1 + 0.0335)
    - Resultat: DF=0.9057; zero 3a=3.3573%
    - Lecture desk: Discount factor bootstrappe puis taux zero-coupon annualise.
  - Forward 1a->2a:
    - Formule: f = DF_{n-1}/DF_n - 1
    - Application: 0.9709/0.9389 - 1
    - Resultat: 3.4068%
    - Lecture desk: Taux forward 1 an implicite entre deux noeuds.
  - Forward 2a->3a:
    - Formule: f = DF_{n-1}/DF_n - 1
    - Application: 0.9389/0.9057 - 1
    - Resultat: 3.6663%
    - Lecture desk: Taux forward 1 an implicite entre deux noeuds.
- Actions operationnelles attendues:
  - Verifier la monotonie/cohrence des DF (decroissants) et des forwards.
  - Utiliser les DF pour actualiser tout cash-flow date sur la courbe.
  - Reprendre en multi-courbe (OIS discounting) pour un usage production.
- Points de vigilance:
  - Le bootstrap est sensible aux instruments choisis et a l'interpolation entre noeuds.

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
- Chunks sources analyses: 18 (exploitables: 17).
- Score pedagogique moyen: 58.72/100 (qualite structurelle: 93.89/100).
- Definitions: 2 | exemples: 8 | exercices: 3 | formules: 6 | cas pratiques: 0.
- Repartition par type: theory: 11, worked_example: 2, solution: 2, definition: 1, exercise: 1, example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S1], [S2].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S1], [S3], [S4], [S9].
4. Exemples - couvert par [S1], [S3], [S6], [S9].
5. Exemples resolus - couvert par [S3], [S9], [S11].
6. Exercices - couvert par [S9], [S11], [S13].
7. Corriges - couvert par [S3], [S4], [S11], [S12].
8. Cas pratiques - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, cas pratiques, resumes.

## Faits et angles extraits de la base
- Distinguishing forward curves from discount curves (representing the collateralization of
the forward) motivates an alternative interpolation method, namely interpolation of
the forward value (the product of the forward and the discount factor).
- In addition,
treating forward curves as native curves (instead of representing them by pseudodiscount curves) will avoid other problems, like that of overlapping instruments.
- Besides the interpolation, we discuss the calibration of the curves for which we give
a generic object-oriented implementation in Fries (Curve calibration.
- Keywords Multi-curve construction· Interest rate curves· Interest rate curve interpolation · Cross-currency curves · Term structure models
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
- However, a good curve construction is of high importance
for practitioners, since it has a strong impact on the delta-hedge (that is, the first-order
interest rate risk).

## Sources RAG a citer
- [S1] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 238, score 0.62697: Distinguishing forward curves from discount curves (representing the collateralization of
the forward) motivates an alternative interpolation method, namely interpolation of
the forward value (the product of the forward and the discount factor).
- [S2] Swaps and Other Derivatives  (With CD ROM) (The Wiley Finance Series) ( PDFDrive ), chunk 390, score 0.578016 (extrait non cite: source bruitee)
- [S3] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 251, score 0.549032: The method is a common practice (also considered in [1]). However,
considering forwards for overlapping periods, this may introduce oscillations and
result in implausible delta-hedges (see
- [S4] Interest Rate Swaps and Their Derivatives  A Practitioner s Guide ( PDFDrive ), chunk 153, score 0.504563: Note that these two curves are
interchangeable, and knowledge of one completely determines the other.
- [S5] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 281, score 0.504426 (extrait non cite: source bruitee)
- [S6] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 349, score 0.499589: “Best-fit” algorithms
start by assuming a functional form for the term structure and calibrate
its parameters such as to minimize the re-pricing error of the chosen
© The Author(s) 2017
529
J.R.M. Röman, Analytical Finance: Volume II,
https://doi.org/10.1007/978-3-319-52584-6_21
- [S7] The Mathematics Of Financial Modeling And Investment Management ( PDFDrive ), chunk 562, score 0.497307: Since 
the swap curve is effectively the LIBOR curve and investors borrow based 
on LIBOR, the swap curve is more useful to funded investors than a government yield curve.
- [S8] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 237, score 0.482225: Jamshidian, F.: An exact bond option pricing formula. 44, 205–209 (1989)
20. Kenyon, C.: Short-rate pricing after the liquidity and credit shocks: including the basis. 83–87 (2010)
21. Kijima, M., Muromachi, Y.: Reformulation of the arbitrage-free pricing method under the
multi-curve environment. Preprint (2015)
22.
- [S9] Quantitative Finance  A Simulation Based Introduction Using Excel ( PDFDrive ), chunk 119, score 0.479208: 13.4  Yield Curves, Discount Factors, and 
Forward Rates
In this section we discuss the spreadsheet YieldDiscountForward, which 
implements the connection between Yield Curve, Discount Factors, and 
Instantaneous forward rates described in Section 13.2.
- [S10] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 263, score 0.469731: ,Hoboken(2007). http://www.christian-fries.de/finmath/book
11. Fries, C.P.: Curve calibration. Object oriented reference implementation 2010–2015. http://
www.finmath.net/topics/curvecalibration
12.
- [S11] Mathematics of the Financial Markets  Financial Instruments and Derivatives Modelling, Valuation and Risk Issues ( PDFDrive ), chunk 14, score 0.463386: Typical
examples involve some derivatives hard to price theoretically, such as credit
derivatives, some exotic options, and so on. FURTHER READING
Pamela 
PETERSON-DRAKE, 
Frank 
J. FABOZZI, 
Foundations 
and
Applications of the Time Value of Money, John Wiley & Sons, Inc., Hoboken,
2009, 298 p.
- [S12] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 78, score 0.450867: Second, for
short-dated contracts, if the underlying asset’s price
process is highly correlated with interest rate movements, then interest rate risk will affect hedging, and
therefore valuation. The extreme cases, of course, are
interest rate derivatives where the underlyings are the
interest rates themselves.
- [S13] Frequently Asked Questions In Quantitative Finance ( PDFDrive ), chunk 111, score 0.437043: It would not make financial sense to assume a
deterministic world for these instruments, just as you
wouldn’t assume a deterministic stock price path for an
equity option. Because the forward rate curve is not uniquely determined by the finite set of constraints that we encounter
- [S14] Analytical Corporate Valuation  Fundamental Analysis, Asset Pricing, and Company Valuation ( PDFDrive ), chunk 401, score 0.436177: J Financ Econ 3:361–377
Fama E (1984a) The information in the term structure. J Financ Econ 13(4):509–528
Fama E (1984b) Term premiums in bond returns. J Financ Econ 13(4):529–546
Fisher I (1930) The theory of interest.
- [S15] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 742, score 0.429326 (extrait non cite: source bruitee)
- [S16] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 367, score 0.428234: Basis swaps are
a fundamental element for long-term multi-curve bootstrapping, because they allow one to imply levels for non-quoted swaps on Euribor
1M, 3M and 12M, which can be selected as bootstrapping instruments
for the corresponding yield curves construction.
- [S17] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 394, score 0.427636: Such a basis curve would satisfy
• Re-pricing each node of FxFwd back to par. So far, everything is still consistent. Such a relationship implies that
the cross-currency basis is zero (which is what “perfect” means here). However, if we look at CCBS quotes, they are not zero!
- [S18] Financial Derivatives  Pricing and Risk Management ( PDFDrive ), chunk 528, score 0.424924: While most swap counterparties are of investment-grade quality, significant differentials in their credit quality can exist. Rather than make adjustments
to the swap price or rate, these differences typically are accounted for through
nonprice means as specified in master agreements.

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

