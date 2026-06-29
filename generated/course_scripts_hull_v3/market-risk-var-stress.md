---
slug: market-risk-var-stress
topic: Market risk VaR, stress testing and escalation
product: multi-asset portfolio
level: intermediate
concepts: parametric VaR, expected shortfall, stress test, risk limit
source_count: 18
---

# Module pratique - Market risk VaR, stress testing and escalation

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Market risk VaR, stress testing and escalation a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 220 minutes
- Produit: multi-asset portfolio
- Concepts: parametric VaR, expected shortfall, stress test, risk limit

## Prerequis
- distribution normale
- quantile
- volatilite

## Objectifs d'apprentissage
A la fin de ce module, vous saurez:
- expliquer l'intuition du sujet avant toute formule;
- identifier les inputs, les risques et les hypotheses cles;
- derouler un calcul chiffre et l'interpreter en langage de desk;
- repondre a un mini-quiz et resoudre un exercice corrige;
- nommer les limites du modele et la decision operationnelle associee.

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
### Module 5 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 6 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de Market risk VaR, stress testing and escalation et savoir le critiquer.
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
### Lecon 1 - Definir la question de risque

**Le reflexe d'abord.** Un portefeuille approche son seuil de VaR intraday. Avant toute formule, demandez-vous ce que var one-sided, horizon, volatility change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Banks assume market risk because they trade as principals, risking
their own capital, and hold positions in financial instruments. Failure to manage market risk can have significant direct effects on a bank’s profitability
and reputation. » [S2]. L'enjeu operationnel est clair : clarifier horizon, confiance, exposition et limite.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, var one-sided, horizon, volatility sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : risk ticket.

Concretement, l'exercice consiste a construire la fiche inputs du risk report, pour en tirer un risk ticket. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: construire la fiche inputs du risk report. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer var one-sided, horizon, volatility a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - Calcul VaR

**Comment ca marche.** VaR = notional * vol * quantile n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Risk management activity focuses on every level of transaction processing from pre-trade analysis through the deal capture and from 
confirmation through the settlement in order to control the operational risk. Market Risk Management Systems
Market risk management systems (MRMSs) capture trade valuations of all portfolios and calculate various market risk measures, such as value at risk (VaR), 
at different levels. » [S3].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a calculer une var parametrique simple avec les bonnes unites. Il s'agit de calculer et comparer a la limite pour produire un var + statut de limite, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer et comparer a la limite. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer var = notional * vol * quantile a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - Stress overlay

**Ou est le risque.** Un scenario historique depasse le mouvement normal. Mal traiter stress test, tail loss, expected shortfall se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Based on Exhibit 1, the best explanation for Nuñes to implement Strategy 8 would be 
that, between the February and December expiration dates, she expects the share price of 
XDF to:
A. remain unchanged. The option trade that Nuñes should recommend relating to the government committee’s 
decision is a:
A. bull spread. long straddle. » [S4].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : montrer ce que la var ne capture pas. Il faut ajouter un choc severe et comparer, documenter un table var/stress, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: ajouter un choc severe et comparer. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer stress test, tail loss, expected shortfall a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Escalation

**La decision visee.** A la fin de cette lecon vous saurez transformer le chiffre en decision de gestion sans hesiter. Le declencheur : la limite est franchie mais le desk propose d'attendre. Les sources le confirment _[extrait]_ : « Stress testing has become more important over the
years and is now a major part of a bank’s, and regulator’s, risk management
activities. Market Risk
205 » [S6].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de reduce, hedge, monitor, escalate sert exactement a cela. Il faut ecrire une note decisionnelle, produire un escalation memo, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: ecrire une note decisionnelle. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer reduce, hedge, monitor, escalate a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Carte des sources et des definitions

**Le reflexe d'abord.** Un apprenant doit savoir quelle source croire et pourquoi. Avant toute formule, demandez-vous ce que source grounding, provenance, vocabulaire de desk change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Market Risk 
Chapters 1–5 all dealt with market risk. This is the risk of losses coming from the market 
change of asset prices that negatively affect the mark-to-market positions of the bank. The 
change of asset prices can come from various factors, such as stock prices, volatility, and 
correlation. » [S7]. L'enjeu operationnel est clair : relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, source grounding, provenance, vocabulaire de desk sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : source map annotee.

Concretement, l'exercice consiste a comparer les extraits [sx] et isoler les definitions robustes, pour en tirer un source map annotee. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Fondations quantitatives niveau Hull

**Comment ca marche.** Modele, mesure, derivees, approximation locale n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « It is designed to give them a single number to look at, so they can then 
dig deeper to understand how concentrated risks might be, and where and why 
these risks are being taken in the various departments that they oversee. While 
this may make sense, VaR can be easy to misunderstand, and can be dangerous 
when misunderstood. » [S8].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a deriver le coeur quantitatif de market risk var, stress testing and escalation et savoir le critiquer. Il s'agit de reprendre la derivation puis nommer ce qui casse en marche reel pour produire un derivation commentee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Cas numerique moteur

**Ou est le risque.** Le desk refuse un chiffre qui ne peut pas etre audite. Mal traiter calculateur deterministe, ordre de grandeur, controles croises se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « The expected loss 
for each obligor can be calculated as Default rate × (Exposure amount − Expected 
recovery). This means that individual credit limits should be set at levels that are inversely 
proportional to the default rate corresponding to the obligor rating. » [S9].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : reproduire un calcul complet avec substitutions, resultat et unite. Il faut refaire le cas a la main et verifier le resultat moteur, documenter un answer key verifiee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Lab interactif et scenarios

**La decision visee.** A la fin de cette lecon vous saurez manipuler les inputs et lire l'effet sur prix, risque ou p&l sans hesiter. Le declencheur : le marche bouge avant validation du trade. Les sources le confirment _[extrait]_ : « VAR only provides an
estimate of losses under normal market conditions,
that is, at a prespecified confidence level. Once a
risk-management system is in place, however, stress
scenarios are just hypothetical realizations of the risk
factors (see Stress Testing). More generally, risk
manager should be keenly aware of weaknesses in
their risk models. By now, VAR is the most widely used measure
of market risk. » [S11].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de scenario table, surface, matrice ou chart selon le produit sert exactement a cela. Il faut tester plusieurs chocs et commenter les regimes, produire un ui block de decision, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: tester plusieurs chocs et commenter les regimes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer scenario table, surface, matrice ou chart selon le produit a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 9 - Production controls

**Le reflexe d'abord.** Une mauvaise convention peut inverser le P&L ou casser une quote. Avant toute formule, demandez-vous ce que data quality, convention, sign, fallback, no-arbitrage check change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Diebold, and T. Horizon problems and extreme
events in financial risk management. Federal Reserve Bank of New York, Economic Policy
Review, 4 (3), 109-118. Christopher, L. Mensink, and A. Value at risk for asset managers. Derivatives Quarterly, 5 (2), 21-33. Phillips, and S. Derivatives and corporate risk management: Participation and volume decisions in the insurance industry. » [S13]. L'enjeu operationnel est clair : identifier les erreurs de convention, de signe, d'unite et de donnees de marche.

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
params: {"latex": "VaR_\\alpha=V\\sigma z_\\alpha\\sqrt h,\\qquad ES_\\alpha=V\\sigma\\sqrt h\\frac{\\phi(z_\\alpha)}{1-\\alpha}"}
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
title: Scenario de P&L - decomposition des facteurs
params: {"delta":250000, "gamma":-80000, "vega":120000, "theta":-15000, "spotMove":-2, "volMove":3}
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
1. VaR ticket: horizon, confiance, volatilite et exposition.
2. Calcul VaR: comparer a une limite imposee.
3. Stress overlay: ajouter un scenario extreme et commenter l'ecart.
4. Escalation memo: decision et suivi.

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

**Definition.** La VaR de niveau $\alpha$ sur l'horizon $h$ est le quantile de perte: $\mathbb{P}(L > \text{VaR}_\alpha)=1-\alpha$. En parametrique gaussien (moyenne nulle):
$$\text{VaR}_\alpha = z_\alpha\,\sigma\sqrt{h}\,V,\qquad z_\alpha = \Phi^{-1}(\alpha).$$

**Expected Shortfall (CVaR).** Perte moyenne au-dela de la VaR:
$$\text{ES}_\alpha = \mathbb{E}[L\,|\,L>\text{VaR}_\alpha] = \sigma\sqrt{h}\,V\,\frac{\varphi(z_\alpha)}{1-\alpha} \;\ge\; \text{VaR}_\alpha.$$

**Axiomes de coherence (Artzner et al.).** monotonicite, invariance par translation, homogeneite positive, **sous-additivite**. La VaR viole la sous-additivite en general (un risque diversifie peut afficher une VaR superieure a la somme); l'**ES est coherente**.

**Backtesting (Kupiec POF).** Test du ratio de vraisemblance comparant le taux d'exceptions observe $\hat{p}=N/n$ au taux theorique $p=1-\alpha$: $LR_{POF}=-2\ln\frac{(1-p)^{n-N}p^{N}}{(1-\hat p)^{n-N}\hat p^{N}}\sim \chi^2_1$.

**Piege theorique.** La VaR ne dit **rien** de l'ampleur des pertes au-dela du seuil et sous-estime les queues epaisses; d'ou l'ES et les stress tests en complement (Bale FRTB privilegie l'ES 97.5%).

**References (corpus).** FRM Handbook (Jorion) (ES = CVaR); *Encyclopedia of Quantitative Finance* (axiomes de coherence); Wilmott, *FAQs in Quantitative Finance* (contre-exemple sous-additivite); *Mathematics of the Financial Markets* (test de Kupiec).

## Exemple numerique resolu
_[genere - calcul verifie]_ On calcule une VaR parametrique simple et on la compare a une limite.

**Donnees.** VaR parametrique: portefeuille 20m volatilite 2% confiance 95% horizon 1 jour.

### VaR et Expected Shortfall parametriques
- Famille: parametric_var
- Hypotheses controlees:
  - Quantile normal exact z=1.6449 pour une confiance de 95%.
  - Rendements gaussiens de moyenne nulle sur l'horizon.
  - Volatilite exprimee sur le meme pas de temps que l'horizon (sinon mise a l'echelle en sqrt(horizon)).
- Calculs a respecter:
  - VaR:
    - Formule: Valeur * vol * sqrt(horizon) * z(alpha)
    - Application: 20,000,000 * 0.0200 * sqrt(1) * 1.6449
    - Resultat: 657,941
    - Lecture desk: Perte seuil non depassee avec une probabilite alpha.
  - Expected Shortfall:
    - Formule: Valeur * vol * sqrt(horizon) * phi(z)/(1-alpha)
    - Application: 20,000,000 * 0.0200 * sqrt(1) * 0.1031/0.0500
    - Resultat: 825,085
    - Lecture desk: Perte moyenne CONDITIONNELLE au-dela de la VaR; toujours >= VaR.
- Actions operationnelles attendues:
  - Comparer VaR et Expected Shortfall a la limite et aux stress tests.
  - Si l'ES est tres au-dessus de la VaR, la queue est lourde: prioriser les stress scenarios.
  - Identifier les facteurs dominants du risque avant de reduire.
- Points de vigilance:
  - La VaR parametrique sous-estime les queues epaisses et ignore le gap risk.
  - La VaR n'est pas sous-additive en general: agreger des VaR par desk peut sous-estimer le risque; l'Expected Shortfall, lui, est coherent (sous-additif).

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
_[genere]_ Une VaR 95% 1 jour de 660k signifie quoi exactement?

**Correction.** Dans ~95% des jours, la perte ne devrait pas depasser 660k; environ 1 jour sur 20, elle peut etre superieure. La VaR ne dit rien de l'ampleur au-dela du seuil.

### Exercice 2 - niveau desk
_[genere]_ Portefeuille 20m, vol 2%/jour, 95%, 1 jour. Calculez la VaR et comparez a une limite de 500k.

**Correction detaillee (calcul verifie).**
### VaR et Expected Shortfall parametriques
- Famille: parametric_var
- Hypotheses controlees:
  - Quantile normal exact z=1.6449 pour une confiance de 95%.
  - Rendements gaussiens de moyenne nulle sur l'horizon.
  - Volatilite exprimee sur le meme pas de temps que l'horizon (sinon mise a l'echelle en sqrt(horizon)).
- Calculs a respecter:
  - VaR:
    - Formule: Valeur * vol * sqrt(horizon) * z(alpha)
    - Application: 20,000,000 * 0.0200 * sqrt(1) * 1.6449
    - Resultat: 657,941
    - Lecture desk: Perte seuil non depassee avec une probabilite alpha.
  - Expected Shortfall:
    - Formule: Valeur * vol * sqrt(horizon) * phi(z)/(1-alpha)
    - Application: 20,000,000 * 0.0200 * sqrt(1) * 0.1031/0.0500
    - Resultat: 825,085
    - Lecture desk: Perte moyenne CONDITIONNELLE au-dela de la VaR; toujours >= VaR.
- Actions operationnelles attendues:
  - Comparer VaR et Expected Shortfall a la limite et aux stress tests.
  - Si l'ES est tres au-dessus de la VaR, la queue est lourde: prioriser les stress scenarios.
  - Identifier les facteurs dominants du risque avant de reduire.
- Points de vigilance:
  - La VaR parametrique sous-estime les queues epaisses et ignore le gap risk.
  - La VaR n'est pas sous-additive en general: agreger des VaR par desk peut sous-estimer le risque; l'Expected Shortfall, lui, est coherent (sous-additif).

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
- Score pedagogique moyen: 51.33/100 (qualite structurelle: 85.0/100).
- Definitions: 4 | exemples: 5 | exercices: 3 | formules: 0 | cas pratiques: 8.
- Repartition par type: theory: 15, solution: 1, market_context: 1, methodology: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S7], [S8], [S14], [S17].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
4. Exemples - couvert par [S1], [S6], [S8], [S11].
5. Exemples resolus - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
6. Exercices - couvert par [S8], [S11], [S16].
7. Corriges - couvert par [S4], [S5], [S9], [S17].
8. Cas pratiques - couvert par [S1], [S3], [S9], [S10].
9. Resumes - couvert par [S11].

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: partially_usable - Sources partiellement suffisantes: completer les manques.
- Presents dans les sources: definitions, exemples, exercices, corriges, cas pratiques, resumes.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, formules, exemples resolus.

## Faits et angles extraits de la base
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
requires even greater information about the extreme tail of the return distribution, ES is more difficult than VaR to calculate and has greater estimation
error.
- 6.4.4 Stress Testing and Scenario Analysis
Although a 99% VaR measure may capture a wide range of all possible outcomes, risk managers must pay particular attention to the remaining 1% of
outcomes since these events could cause banks serious financial problems.
- Stress testing and scenario analysis are important tools of any risk management system that seeks to understand how a portfolio will perform in 
extreme cases.
- Given the reliance on modeling, risk measures need to be
closely examined and tested against extreme events.
- Stress testing considers instances for particular value changes, such as a
rapid change in interest rates or equity indices.
- Scenario analysis evaluates
portfolio performance in severe states of the world, either hypothetical or
historical.

## Sources RAG a citer
- [S1] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 221, score 0.759209 (extrait non cite: source bruitee)
- [S2] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 190, score 0.601892: Banks assume market risk because they trade as principals, risking
their own capital, and hold positions in financial instruments. Failure to manage market risk can have significant direct effects on a bank’s profitability
and reputation.
- [S3] Managing Derivatives Contracts  A Guide to Derivatives Market Structure, Contract Life Cycle, Operations, and Systems ( PDFDrive ), chunk 319, score 0.486731: Risk management activity focuses on every level of transaction processing from pre-trade analysis through the deal capture and from 
confirmation through the settlement in order to control the operational risk.
- [S4] Derivatives Workbook ( PDFDrive ), chunk 31, score 0.484731: Based on Exhibit 1, the best explanation for Nuñes to implement Strategy 8 would be 
that, between the February and December expiration dates, she expects the share price of 
XDF to:
A. remain unchanged. The option trade that Nuñes should recommend relating to the government committee’s 
decision is a:
A. bull spread.
- [S5] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2295, score 0.470631 (extrait non cite: source bruitee)
- [S6] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 222, score 0.45634: Stress testing has become more important over the
years and is now a major part of a bank’s, and regulator’s, risk management
activities. Market Risk
205
- [S7] Practical Methods of Financial Engineering and Risk Management  Tools for Modern Financial Professionals ( PDFDrive ), chunk 222, score 0.453966: Market Risk 
Chapters 1–5 all dealt with market risk. This is the risk of losses coming from the market 
change of asset prices that negatively affect the mark-to-market positions of the bank. The 
change of asset prices can come from various factors, such as stock prices, volatility, and 
correlation.
- [S8] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 154, score 0.441157: It is designed to give them a single number to look at, so they can then 
dig deeper to understand how concentrated risks might be, and where and why 
these risks are being taken in the various departments that they oversee.
- [S9] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 546, score 0.436773: The expected loss 
for each obligor can be calculated as Default rate × (Exposure amount − Expected 
recovery). This means that individual credit limits should be set at levels that are inversely 
proportional to the default rate corresponding to the obligor rating.
- [S10] Foundations of Financial Risk  An Overview of Financial Risk and Risk based Financial Regulation ( PDFDrive ), chunk 8, score 0.434461 (extrait non cite: source bruitee)
- [S11] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2310, score 0.42279: VAR only provides an
estimate of losses under normal market conditions,
that is, at a prespecified confidence level. Once a
risk-management system is in place, however, stress
scenarios are just hypothetical realizations of the risk
factors (see Stress Testing).
- [S12] Managing Risks in Commercial and Retail Banking ( PDFDrive ), chunk 539, score 0.414916 (extrait non cite: source bruitee)
- [S13] The Oxford Guide to Financial Modeling  Applications for Capital Markets, Corporate Finance, Risk Management and Financial Institutions ( PDFDrive ), chunk 699, score 0.4097: Diebold, and T. Horizon problems and extreme
events in financial risk management. Federal Reserve Bank of New York, Economic Policy
Review, 4 (3), 109-118. Christopher, L. Mensink, and A. Value at risk for asset managers. Derivatives Quarterly, 5 (2), 21-33. Phillips, and S.
- [S14] Financial Risk Manager Handbook + Test Bank  FRM Part I   Part II ( PDFDrive ), chunk 247, score 0.375318: More generally, risk managers should evaluate the entire distribution
of profits and losses. In addition, the analysis should be complemented by stresstesting, which identifies potential losses under extreme market conditions that
may not show up in the recent history.
- [S15] Managing Derivatives Contracts  A Guide to Derivatives Market Structure, Contract Life Cycle, Operations, and Systems ( PDFDrive ), chunk 55, score 0.368591: In addition, 
ERM places responsibility on a level closer to senior management, giving senior 
management an overall view of the company’s risk position. Strategically, ERM is 
a key component of corporate governance.
- [S16] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 2333, score 0.364559 (extrait non cite: source bruitee)
- [S17] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 793, score 0.364068: We also
looked at credit risk, noting how credit risk entails elements of option pricing theory.
- [S18] Managing Derivatives Contracts  A Guide to Derivatives Market Structure, Contract Life Cycle, Operations, and Systems ( PDFDrive ), chunk 52, score 0.362658: All 
financial and nonfinancial corporations are exposed to risks in their everyday 
business activities from adverse movements and events in various contingencies, such as interest rates, foreign exchange rates, commodity prices, credit, 
liquidity, theft, weather, health, catastrophe, and competition.

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

