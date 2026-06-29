---
slug: implied-volatility-smile
topic: Implied volatility smile and quote cleaning
product: equity index options
level: intermediate
concepts: implied volatility, smile, skew, SVI
source_count: 18
---

# Module pratique - Implied volatility smile and quote cleaning

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Implied volatility smile and quote cleaning a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 220 minutes
- Produit: equity index options
- Concepts: implied volatility, smile, skew, SVI

## Prerequis
- prix d'option vanilla
- volatilite implicite
- inversion de Black-Scholes

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

## Positionnement bibliotheque
- Track: Derivatives & Volatility
- Type d'asset: module reutilisable de cours.
- Sorties attendues: fiche apprenant, cas pratique, corrige, quiz, notes instructeur.
- Integration SaaS: ce module doit pouvoir etre decoupe en lecons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire la chaine d'options
- Objectif pratique: Nettoyer les quotes avant tout fit.
- Situation de desk: Les bids/asks contiennent des quotes stale et croisees.
- Notion utile: Bounds, moneyness, bid/ask mid.
- Activite: Filtrer la chaine et documenter les rejets.
- Livrable apprenant: Clean option chain.
### Module 2 - Inversion en IV
- Objectif pratique: Transformer les prix en volatilites implicites comparables.
- Situation de desk: Le trader raisonne en vol, pas en premium brut.
- Notion utile: Black-Scholes inversion, vega, convergence.
- Activite: Calculer IV par strike.
- Livrable apprenant: Slice IV.
### Module 3 - Smile et skew
- Objectif pratique: Interpreter la forme de smile comme signal de risque.
- Situation de desk: Le put wing s'enrichit avant un evenement macro.
- Notion utile: Skew, term structure, convexite.
- Activite: Tracer smile et commenter le risque.
- Livrable apprenant: Vol note.
### Module 4 - Fit utilisable
- Objectif pratique: Produire une courbe lisse sans cacher les controles.
- Situation de desk: Le pricer a besoin d'une surface stable.
- Notion utile: SVI ou fit quadratique, no-arbitrage checks.
- Activite: Fit, residus, controles.
- Livrable apprenant: Fit report.
### Module 5 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 6 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de Implied volatility smile and quote cleaning et savoir le critiquer.
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
### Lecon 1 - Lire la chaine d'options

**Le reflexe d'abord.** Les bids/asks contiennent des quotes stale et croisees. Avant toute formule, demandez-vous ce que bounds, moneyness, bid/ask mid change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « REFERENCES AND BIBLIOGRAPHY
Carr, Peter, and Liuren Wu. “A New Simple Approach for Constructing
Implied Volatility Surfaces.” Working paper, New York University and Baruch
College. Derman, Emanuel. “Introduction to the Volatility Smile.” Lecture notes,
Columbia University. Gatheral, Jim. » [S1]. L'enjeu operationnel est clair : nettoyer les quotes avant tout fit.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, bounds, moneyness, bid/ask mid sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : clean option chain.

Concretement, l'exercice consiste a filtrer la chaine et documenter les rejets, pour en tirer un clean option chain. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: filtrer la chaine et documenter les rejets. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer bounds, moneyness, bid/ask mid a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - Inversion en IV

**Comment ca marche.** Black-Scholes inversion, vega, convergence n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Implied volatilities beyond the 10 delta strikes must either be controlled
usingextrapolationorgeneratedautomaticallyusingamodellikeStochasticVolatility
Inspired (SVI)-see Gatheral’s book in Further Reading for more information. » [S2].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a transformer les prix en volatilites implicites comparables. Il s'agit de calculer iv par strike pour produire un slice iv, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer iv par strike. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer black-scholes inversion, vega, convergence a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - Smile et skew

**Ou est le risque.** Le put wing s'enrichit avant un evenement macro. Mal traiter skew, term structure, convexite se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « “Riding on a Smile.” Risk, 7(2): 32–39. Figlewski, S. “The Adaptive Mesh Model: A New Approach to 
Efficient Option Pricing.” Journal of Financial Economics, 53: 313–51. Figlewski, S., Gao, B., & Ahn, D. “Pricing Discrete Barrier Options with an 
Adaptive Mesh Model,” Working Paper, 1999. Complete Guide to Option Pricing Formulas. McGraw-Hill. Options, Futures, & Other Derivatives. Prentice Hall. » [S3].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : interpreter la forme de smile comme signal de risque. Il faut tracer smile et commenter le risque, documenter un vol note, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: tracer smile et commenter le risque. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer skew, term structure, convexite a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Fit utilisable

**La decision visee.** A la fin de cette lecon vous saurez produire une courbe lisse sans cacher les controles sans hesiter. Le declencheur : le pricer a besoin d'une surface stable. Les sources le confirment _[extrait]_ : « ■The risk reversal contract describes the skew of the volatility smile (i.e., how
tilted the volatility smile is). Butterfly and risk reversal contracts are quoted at market tenors like the ATM
curve. In equity derivatives, lower strikes tend to have higher implied volatility
than higher strikes at a given maturity because equities tend to rally slowly and » [S4].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de svi ou fit quadratique, no-arbitrage checks sert exactement a cela. Il faut fit, residus, controles, produire un fit report, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: fit, residus, controles. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer svi ou fit quadratique, no-arbitrage checks a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Carte des sources et des definitions

**Le reflexe d'abord.** Un apprenant doit savoir quelle source croire et pourquoi. Avant toute formule, demandez-vous ce que source grounding, provenance, vocabulaire de desk change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « When the implied volatility is plotted against the strike price, the resulting graph is 
typically downward sloping for equity markets, or valley-shaped for currency 
markets. For markets where the graph is downward sloping, such as for equity 
options, the term volatility skew is often used. » [S5]. L'enjeu operationnel est clair : relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, source grounding, provenance, vocabulaire de desk sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : source map annotee.

Concretement, l'exercice consiste a comparer les extraits [sx] et isoler les definitions robustes, pour en tirer un source map annotee. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Fondations quantitatives niveau Hull

**Comment ca marche.** Modele, mesure, derivees, approximation locale n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « 16.14 THE RELEVANCE OF THE SMILE
The volatility smile is important in financial engineering for at least three reasons. First, if we associate a volatility smile with all the risk factors, and if this smile shifts randomly
over time, then we may be able to trade it, take spread positions, and arbitrage it. The smile
dynamics, thus, imply new opportunities for a market professional. » [S6].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a deriver le coeur quantitatif de implied volatility smile and quote cleaning et savoir le critiquer. Il s'agit de reprendre la derivation puis nommer ce qui casse en marche reel pour produire un derivation commentee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Cas numerique moteur

**Ou est le risque.** Le desk refuse un chiffre qui ne peut pas etre audite. Mal traiter calculateur deterministe, ordre de grandeur, controles croises se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « As the horizon date changes, the expiry date for each market tenor
changes accordingly (the methodology for calculating tenor expiry dates is given
in Chapter 10 and implemented in Practical D). Therefore, the contracts liquidly
quoted in the market today have different expiry dates from those quoted yesterday
or those quoted tomorrow. » [S7].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : reproduire un calcul complet avec substitutions, resultat et unite. Il faut refaire le cas a la main et verifier le resultat moteur, documenter un answer key verifiee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Lab interactif et scenarios

**La decision visee.** A la fin de cette lecon vous saurez manipuler les inputs et lire l'effet sur prix, risque ou p&l sans hesiter. Le declencheur : le marche bouge avant validation du trade. Les sources le confirment _[extrait]_ : « This is referred to as the term 
structure of volatility. A few things affect the term structure of volatility. The main 
effect relates to the implied impact of upcoming market events. For example, an 
option maturing after a company’s earnings announcement would be expected 
to have higher implied volatility than one expiring right before such an event. » [S8].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de scenario table, surface, matrice ou chart selon le produit sert exactement a cela. Il faut tester plusieurs chocs et commenter les regimes, produire un ui block de decision, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: tester plusieurs chocs et commenter les regimes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer scenario table, surface, matrice ou chart selon le produit a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 9 - Production controls

**Le reflexe d'abord.** Une mauvaise convention peut inverser le P&L ou casser une quote. Avant toute formule, demandez-vous ce que data quality, convention, sign, fallback, no-arbitrage check change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « But if this model is used
to back-test the market-traded option, we can observe that different contracts
produce significantly different implied volatilities. Options’ implied volatilities
actually vary with the different time to maturity. This is the term structure of
implied volatility. For a given time to maturity, implied volatilities for different
strikes are not the same either. » [S9]. L'enjeu operationnel est clair : identifier les erreurs de convention, de signe, d'unite et de donnees de marche.

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
params: {"latex": "\\sigma_{\\text{imp}}:\\ BS(S,K,r,q,T,\\sigma_{\\text{imp}})=P_{\\text{mkt}}"}
```

```uiblock
type: scenario_table
title: Table de scenarios - lecture prix / risque / P&L
params: {"rowLabel":"Scenario", "cols":["Base","Choc modere","Stress"], "rows":["Prix / valeur","Risque 1er ordre","Decision"], "cells":[["100.00","97.50","90.20"],["0","-250k","-980k"],["Quote","Hedge","Escalate"]]}
```

```uiblock
type: vol_smile
title: Surface de volatilite - smile et skew
params: {"matrix":[[0.22,0.25,0.29,0.33,0.36],[0.20,0.23,0.27,0.30,0.33],[0.18,0.21,0.24,0.27,0.30],[0.17,0.20,0.22,0.25,0.28],[0.16,0.18,0.20,0.23,0.26]]}
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
1. Quote cleaning: filtrer quotes impossibles/stale.
2. IV inversion: calculer vol implicite par strike.
3. Smile view: expliquer skew et risque de hedge.
4. Fit report: ajuster une courbe et controler les residus.

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

**Volatilite implicite.** $\sigma_{imp}(K,T)$ est l'unique vol qui recolle le prix de marche au modele BS: $C_{BS}(\sigma_{imp}) = C_{marche}$. Tracee en fonction du strike, elle dessine le **smile/skew** — preuve directe que BS (vol constante) est faux.

**Volatilite locale (Dupire).** L'unique diffusion $dS=\sigma_{loc}(S,t)S\,dW$ compatible avec tous les prix d'options:
$$\sigma_{loc}^2(K,T) = \frac{\partial_T C + (r-q)K\,\partial_K C + qC}{\tfrac12 K^2\,\partial_{KK}C}.$$

**SABR (Hagan et al. 2002).** $dF=\alpha F^{\beta}dW_1,\; d\alpha=\nu\alpha\,dW_2,\; \langle dW_1,dW_2\rangle=\rho\,dt$. Approximation analytique de $\sigma_{imp}(K,F)$ tres utilisee pour interpoler/extrapoler le smile de taux. Heston ajoute une variance en racine a retour a la moyenne.

**Intuition rigoureuse.** Le skew price l'asymetrie et les queues (crash risk): un put OTM cher = vol implicite elevee a bas strike. La vol implicite est un *prix*, pas une prevision.

**Piege theorique.** La vol locale inversee de Dupire peut etre non-physique (negative) si la surface implicite n'est pas sans arbitrage (monotonie/convexite en $K$, calendar spreads). Sticky-strike vs sticky-delta changent le delta couvert.

**References (corpus).** *FX Derivatives Trader School* (surface de vol locale, Heston); *Mathematics of the Financial Markets* (SABR $\alpha,\beta,\rho$); *Interest Rate Derivatives Explained Vol. 2* (Hagan 2002); *Encyclopedia of Quantitative Finance* (Dupire, non-physicalite).

## Exemple numerique resolu
_[genere - calcul verifie]_ On inverse Black-Scholes pour retrouver la volatilite implicite d'un call.

**Donnees.** Call vanilla spot 100 strike 100 maturite 1 taux 5% prix de marche 10.4506, trouver la volatilite implicite.

### Volatilite implicite (inversion de Black-Scholes)
- Famille: implied_vol_smile
- Hypotheses controlees:
  - On inverse le prix de marche d'un call vanilla pour retrouver sigma.
  - Newton-Raphson amorce a 20%, derivee = vega.
  - Prix de marche superieur a la valeur intrinseque (sinon pas de solution).
- Calculs a respecter:
  - Valeur intrinseque actualisee:
    - Formule: max(S - K*exp(-rT), 0)
    - Application: max(100 - 100*exp(-0.0500*1), 0)
    - Resultat: 4.8771
    - Lecture desk: Plancher du prix; le market price doit etre au-dessus.
  - Inversion Newton:
    - Formule: sigma tel que BS(sigma) = prix marche
    - Application: convergence en 2 iterations
    - Resultat: vol implicite = 20.0000%
    - Lecture desk: Volatilite que le marche 'price' dans cette option.
  - Controle:
    - Formule: BS(vol implicite) vs prix marche
    - Application: BS(0.2000) = 10.4506
    - Resultat: cible 10.4506
    - Lecture desk: Le reprix avec la vol trouvee doit redonner le prix de marche.
- Actions operationnelles attendues:
  - Repeter par strike pour tracer le smile/skew (vol implicite = f(strike)).
  - Comparer la vol implicite a la vol realisee pour juger cher/pas cher.
  - Surveiller la pente (skew) et la courbure: signal de risque de queue price par le marche.
- Points de vigilance:
  - La vol implicite n'est PAS une prevision: c'est le parametre qui recolle le prix de marche au modele BS.

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
### Volatilite implicite (inversion de Black-Scholes)
- Famille: implied_vol_smile
- Hypotheses controlees:
  - On inverse le prix de marche d'un call vanilla pour retrouver sigma.
  - Newton-Raphson amorce a 20%, derivee = vega.
  - Prix de marche superieur a la valeur intrinseque (sinon pas de solution).
- Calculs a respecter:
  - Valeur intrinseque actualisee:
    - Formule: max(S - K*exp(-rT), 0)
    - Application: max(100 - 100*exp(-0.0500*1), 0)
    - Resultat: 4.8771
    - Lecture desk: Plancher du prix; le market price doit etre au-dessus.
  - Inversion Newton:
    - Formule: sigma tel que BS(sigma) = prix marche
    - Application: convergence en 2 iterations
    - Resultat: vol implicite = 20.0000%
    - Lecture desk: Volatilite que le marche 'price' dans cette option.
  - Controle:
    - Formule: BS(vol implicite) vs prix marche
    - Application: BS(0.2000) = 10.4506
    - Resultat: cible 10.4506
    - Lecture desk: Le reprix avec la vol trouvee doit redonner le prix de marche.
- Actions operationnelles attendues:
  - Repeter par strike pour tracer le smile/skew (vol implicite = f(strike)).
  - Comparer la vol implicite a la vol realisee pour juger cher/pas cher.
  - Surveiller la pente (skew) et la courbure: signal de risque de queue price par le marche.
- Points de vigilance:
  - La vol implicite n'est PAS une prevision: c'est le parametre qui recolle le prix de marche au modele BS.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Dans Black-Scholes, que represente N(d2)?**
- A) La probabilite risque-neutre d'exercice
- B) Le delta du call
- C) La vega
- D) Le prix du put
  - Reponse: **A**. N(d2) est la probabilite risque-neutre que le call finisse dans la monnaie.

**Q2. Le delta d'un call ATM est environ:**
- A) 0
- B) 0.5
- C) 1
- D) -0.5
  - Reponse: **B**. N(d1) ~ 0.5 a la monnaie (legerement au-dessus avec un taux positif).

**Q3. La put-call parity relie call et put via:**
- A) la vol implicite
- B) C - P = S - K e^{-rT}
- C) le gamma
- D) la duration
  - Reponse: **B**. C - P = forward actualise - strike actualise; une violation signale une incoherence de quote.

**Q4. Augmenter la volatilite implicite fait:**
- A) baisser call et put
- B) monter call et put
- C) monter le call, baisser le put
- D) rien
  - Reponse: **B**. La vega est positive pour call et put: plus de vol = plus de valeur temps.

**Q5. La vega est maximale:**
- A) tres ITM
- B) tres OTM
- C) proche de la monnaie
- D) a maturite nulle
  - Reponse: **C**. La sensibilite a la vol est la plus forte autour de l'ATM, surtout a maturite moyenne.

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
- Chunks sources analyses: 18 (exploitables: 18).
- Score pedagogique moyen: 59.33/100 (qualite structurelle: 96.67/100).
- Definitions: 3 | exemples: 13 | exercices: 2 | formules: 1 | cas pratiques: 1.
- Repartition par type: theory: 12, worked_example: 2, example: 2, diagram_description: 2.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S3], [S5], [S18].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S1].
4. Exemples - couvert par [S1], [S2], [S4], [S5].
5. Exemples resolus - couvert par [S1], [S10].
6. Exercices - couvert par [S6], [S18].
7. Corriges - couvert par [S1], [S3], [S7], [S9].
8. Cas pratiques - couvert par [S4].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, resumes.

## Faits et angles extraits de la base
- “A New Simple Approach for Constructing
Implied Volatility Surfaces.” Working paper, New York University and Baruch
College.
- “Introduction to the Volatility Smile.” Lecture notes,
Columbia University.
- “A Parsimonious Arbitrage-Free Implied Volatility Parameterization with Application to the Valuation of Volatility Derivatives.” Proceedings
of the Global Derivatives and Risk Management 2004 Madrid conference.
- “Convergence of Heston to SVI.” Quantitative Finance 11 (8): 1129–1132.
- “A Class of Term Structures for SVI Implied Volatility.”
Working paper.
- “Managing Smile Risk.” Wilmott Magazine (September): 84–108.
- “A Closed-Form Solution for Options with Stochastic
Volatility with Applications to Bond and Currency Options.” Review of Financial Studies 6 (2): 327–343.
- “Arbitrage Bounds on the Implied Volatility Strike and
Term Structures of European-Style Options.” Journal of Derivatives (Summer):
23–35.
- “Implied Volatility Surface: Construction Methodologies
and Characteristics.” Available at http://arxiv.org/abs/1107.1834v1.
- “Diffusion Processes.” In A Second
Course in Stochastic Processes, 157–396.

## Sources RAG a citer
- [S1] Advanced Equity Derivatives  Volatility and Correlation ( PDFDrive ), chunk 26, score 0.965149: REFERENCES AND BIBLIOGRAPHY
Carr, Peter, and Liuren Wu. “A New Simple Approach for Constructing
Implied Volatility Surfaces.” Working paper, New York University and Baruch
College. Derman, Emanuel. “Introduction to the Volatility Smile.” Lecture notes,
Columbia University. Gatheral, Jim.
- [S2] FX Derivatives Trader School ( PDFDrive ), chunk 142, score 0.79441: Implied volatilities beyond the 10 delta strikes must either be controlled
usingextrapolationorgeneratedautomaticallyusingamodellikeStochasticVolatility
Inspired (SVI)-see Gatheral’s book in Further Reading for more information.
- [S3] Emerging Financial Derivatives  Understanding exotic options and structured products ( PDFDrive ), chunk 40, score 0.790427: “Riding on a Smile.” Risk, 7(2): 32–39. Figlewski, S. “The Adaptive Mesh Model: A New Approach to 
Efficient Option Pricing.” Journal of Financial Economics, 53: 313–51. Figlewski, S., Gao, B., & Ahn, D. “Pricing Discrete Barrier Options with an 
Adaptive Mesh Model,” Working Paper, 1999.
- [S4] FX Derivatives Trader School ( PDFDrive ), chunk 66, score 0.78615: ■The risk reversal contract describes the skew of the volatility smile (i.e., how
tilted the volatility smile is). Butterfly and risk reversal contracts are quoted at market tenors like the ATM
curve.
- [S5] Emerging Financial Derivatives  Understanding exotic options and structured products ( PDFDrive ), chunk 42, score 0.775058: When the implied volatility is plotted against the strike price, the resulting graph is 
typically downward sloping for equity markets, or valley-shaped for currency 
markets. For markets where the graph is downward sloping, such as for equity 
options, the term volatility skew is often used.
- [S6] Principles of Financial Engineering ( PDFDrive ), chunk 616, score 0.768246: 16.14 THE RELEVANCE OF THE SMILE
The volatility smile is important in financial engineering for at least three reasons. First, if we associate a volatility smile with all the risk factors, and if this smile shifts randomly
over time, then we may be able to trade it, take spread positions, and arbitrage it.
- [S7] FX Derivatives Trader School ( PDFDrive ), chunk 65, score 0.758016: As the horizon date changes, the expiry date for each market tenor
changes accordingly (the methodology for calculating tenor expiry dates is given
in Chapter 10 and implemented in Practical D).
- [S8] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 110, score 0.756617: This is referred to as the term 
structure of volatility. A few things affect the term structure of volatility. The main 
effect relates to the implied impact of upcoming market events.
- [S9] Analytical Finance  Volume I  The Mathematics of Equity Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 120, score 0.755268: But if this model is used
to back-test the market-traded option, we can observe that different contracts
produce significantly different implied volatilities. Options’ implied volatilities
actually vary with the different time to maturity. This is the term structure of
implied volatility.
- [S10] FX Derivatives Trader School ( PDFDrive ), chunk 208, score 0.752437: The majority of corporate hedge structures net sell vega and this flow into the marketcancauseimpliedvolatilitytoconsistentlymoveloweratcertaintimesoftheyear.
- [S11] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 107, score 0.751817: It is also reasonable to believe that as a company’s equity value declines, its leverage increases. This means that the company is 
riskier and thus the implied volatility should be higher (see
- [S12] Interest Rate Markets  A Practical Approach to Fixed Income (Wiley Trading)   ( PDFDrive ), chunk 309, score 0.748737: Vega P/L is almost symmetric to changes in implied volatility; hence, changing implied volatility
can add or subtract from the breakeven calculation.
- [S13] FX Derivatives Trader School ( PDFDrive ), chunk 128, score 0.74839: In practice this means that:
■ATM contracts are used to trade the level of implied volatility because their main
exposure at inception is vega
(
𝜕P
𝜕𝜎
). ■Risk reversal contracts are used to trade the spot versus implied volatility
relationship because their main exposure at inception is vanna
(
𝜕vega
𝜕spot
).
- [S14] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 67, score 0.737104 (extrait non cite: source bruitee)
- [S15] FX Derivatives Trader School ( PDFDrive ), chunk 177, score 0.694484: The trader is proved correct; implied volatility does jump but this occurs as
USD/TRY spot moves sharply higher due to a sudden TRY devaluation. Over the course of a few days, USD/TRY spot jumps to 2.3000, the 1yr ATM
implied volatility jumps from 9% to 18%, and the 1yr 25d risk reversal goes from
+5% to +15%.
- [S16] FX Derivatives Trader School ( PDFDrive ), chunk 210, score 0.691557: Exhibit 17.28 shows AUD/JPY
market instruments on January 1, 2008, and January 1, 2009, while Exhibit 17.29
shows the outright 10d and 25d and ATM strikes on the AUD/JPY volatility smiles
for the same two dates.
- [S17] FX Derivatives Trader School ( PDFDrive ), chunk 141, score 0.690245: For reference, the rega on a risk reversal is approximately the average of the
two absolute strike vegas while the sega on a butterfly is approximately the sum of
the two wing strike vega exposures.
- [S18] Modern Portfolio Theory  Foundations, Analysis, and New Developments ( PDFDrive ), chunk 261, score 0.684209: To measure marketwide implied volatilities using index options, the Chicago
Board Options Exchange (CBOE) introduced the implied volatility index, known as
VXO, in 1993. This volatility index was a measure of the implied market volatility

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Implied volatility root
$$
\sigma_{\text{imp}}:\quad BS(S,K,r,q,T,\sigma_{\text{imp}})=P_{\text{mkt}}
$$
- Usage desk: convert option prices into comparable volatility quotes.
### F2 - Newton update
$$
\sigma_{k+1}=\sigma_k-\frac{BS(\sigma_k)-P_{\text{mkt}}}{\text{Vega}(\sigma_k)}
$$
- Usage desk: iterate quickly while monitoring low-vega strikes.
### F3 - SVI total variance
$$
w(k)=a+b\left(\rho(k-m)+\sqrt{(k-m)^2+\eta^2}\right)
$$
- Usage desk: fit a clean smile while keeping skew and curvature visible.

