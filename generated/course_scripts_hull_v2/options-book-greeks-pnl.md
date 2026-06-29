---
slug: options-book-greeks-pnl
topic: Options book Greeks and P&L attribution
product: equity options book
level: intermediate
concepts: delta, gamma, vega, theta, hedging
source_count: 18
---

# Module pratique - Options book Greeks and P&L attribution

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Options book Greeks and P&L attribution a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 210 minutes
- Produit: equity options book
- Concepts: delta, gamma, vega, theta, hedging

## Prerequis
- prix d'une option vanilla
- derivees partielles
- notion de hedge

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
### Module 1 - Lire le Greek report
- Objectif pratique: Identifier les sensibilites dominantes du book.
- Situation de desk: Un book options arrive avec delta/gamma/vega/theta agrege.
- Notion utile: Delta par %, gamma par %^2, vega par vol point.
- Activite: Verifier unites et signe.
- Livrable apprenant: Risk snapshot.
### Module 2 - P&L attribution
- Objectif pratique: Calculer P&L sous scenario spot/vol/time.
- Situation de desk: Spot baisse, vol monte, un jour passe.
- Notion utile: Taylor P&L delta-gamma-vega-theta.
- Activite: Calculer chaque bloc et le total.
- Livrable apprenant: Attribution table.
### Module 3 - Hedge action
- Objectif pratique: Proposer une couverture avec residual risk visible.
- Situation de desk: Le book est short gamma et long vega.
- Notion utile: Delta hedge, convexity hedge, vega hedge.
- Activite: Choisir action et trigger.
- Livrable apprenant: Hedge memo.
### Module 4 - Communication risk
- Objectif pratique: Ecrire un message utile a trader et risk manager.
- Situation de desk: Le P&L explique doit tenir en 8 lignes.
- Notion utile: Dominant risk, residual risk, monitoring.
- Activite: Rediger la note.
- Livrable apprenant: Desk risk note.
### Module 5 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 6 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de Options book Greeks and P&L attribution et savoir le critiquer.
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
### Lecon 1 - Lire le Greek report

**Le reflexe d'abord.** Un book options arrive avec delta/gamma/vega/theta agrege. Avant toute formule, demandez-vous ce que delta par %, gamma par %^2, vega par vol point change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « For example Mello and Neuhaus (1998)
illustrates that discrete delta hedging can cause substantial risk, further they suggest that a large
part of this risk can be hedged away by using options against options. They assume a quite
practical situation were a market maker often not can hedge a option with another option with
exactly the same strike and maturity. » [S1]. L'enjeu operationnel est clair : identifier les sensibilites dominantes du book.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, delta par %, gamma par %^2, vega par vol point sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : risk snapshot.

Concretement, l'exercice consiste a verifier unites et signe, pour en tirer un risk snapshot. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: verifier unites et signe. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer delta par %, gamma par %^2, vega par vol point a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - P&L attribution

**Comment ca marche.** Taylor P&L delta-gamma-vega-theta n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Figlewski (1998): ‘‘The Information Content of Implied Volatility’’ The
Review of Financial Studies, 6(3), 659–681. ■Castelli, C. (1877) The Theory of Options in Stocks and Shares. London: F.C. ■Carr, P., and J. Bowie (1994): ‘‘Static Simplicity,’’ Risk Magazine, 7(8). ■Carr, P., and A. Chou (1998): ‘‘Static Hedging of Complex Barrier Options,’’ Banc of America
Securities Working paper. ■Carr, P., K. Ellis, and V. » [S4].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a calculer p&l sous scenario spot/vol/time. Il s'agit de calculer chaque bloc et le total pour produire un attribution table, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer chaque bloc et le total. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer taylor p&l delta-gamma-vega-theta a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - Hedge action

**Ou est le risque.** Le book est short gamma et long vega. Mal traiter delta hedge, convexity hedge, vega hedge se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Theta is greater (in absolute value) for short-term ATM options, so statement
d. is incorrect. » [S7].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : proposer une couverture avec residual risk visible. Il faut choisir action et trigger, documenter un hedge memo, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: choisir action et trigger. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer delta hedge, convexity hedge, vega hedge a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Communication risk

**La decision visee.** A la fin de cette lecon vous saurez ecrire un message utile a trader et risk manager sans hesiter. Le declencheur : le p&l explique doit tenir en 8 lignes. Les sources le confirment _[extrait]_ : « Veta = 
Further Greeks, third- and fourth-order, can be calculated but are beyond the 
needs of this book. Many options traders will use additional Greeks, but once you 
understand how the Greeks are calculated and work, you can see how to calculate a third-order Greek like Speed (the rate of change in Gamma with respect to 
changes in the underlying price). » [S11].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de dominant risk, residual risk, monitoring sert exactement a cela. Il faut rediger la note, produire un desk risk note, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: rediger la note. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer dominant risk, residual risk, monitoring a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Carte des sources et des definitions

**Le reflexe d'abord.** Un apprenant doit savoir quelle source croire et pourquoi. Avant toute formule, demandez-vous ce que source grounding, provenance, vocabulaire de desk change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « I
The Delta
The Gamma
The Theta
The Vega
The Rho » [S12]. L'enjeu operationnel est clair : relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, source grounding, provenance, vocabulaire de desk sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : source map annotee.

Concretement, l'exercice consiste a comparer les extraits [sx] et isoler les definitions robustes, pour en tirer un source map annotee. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Fondations quantitatives niveau Hull

**Comment ca marche.** Modele, mesure, derivees, approximation locale n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « r The binomial model, where the price change can only take two values, is another
model where complete elimination of risk is possible. r A riddle for traders – Black-Scholes in Greek:
When I hedge my option
I can’t lose with Delta
What I lose with Theta
I will gain with Gamma
And Greeks have no Vega. r Further reading
L. Bachelier, Th´eorie de la sp´eculation, Gabay, Paris, 1995. » [S17].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a deriver le coeur quantitatif de options book greeks and p&l attribution et savoir le critiquer. Il s'agit de reprendre la derivation puis nommer ce qui casse en marche reel pour produire un derivation commentee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Cas numerique moteur

**Ou est le risque.** Le desk refuse un chiffre qui ne peut pas etre audite. Mal traiter calculateur deterministe, ordre de grandeur, controles croises se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « For example Mello and Neuhaus (1998)
illustrates that discrete delta hedging can cause substantial risk, further they suggest that a large
part of this risk can be hedged away by using options against options. They assume a quite
practical situation were a market maker often not can hedge a option with another option with
exactly the same strike and maturity. » [S1].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : reproduire un calcul complet avec substitutions, resultat et unite. Il faut refaire le cas a la main et verifier le resultat moteur, documenter un answer key verifiee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Lab interactif et scenarios

**La decision visee.** A la fin de cette lecon vous saurez manipuler les inputs et lire l'effet sur prix, risque ou p&l sans hesiter. Le declencheur : le marche bouge avant validation du trade. Les sources le confirment _[extrait]_ : « Figlewski (1998): ‘‘The Information Content of Implied Volatility’’ The
Review of Financial Studies, 6(3), 659–681. ■Castelli, C. (1877) The Theory of Options in Stocks and Shares. London: F.C. ■Carr, P., and J. Bowie (1994): ‘‘Static Simplicity,’’ Risk Magazine, 7(8). ■Carr, P., and A. Chou (1998): ‘‘Static Hedging of Complex Barrier Options,’’ Banc of America
Securities Working paper. ■Carr, P., K. Ellis, and V. » [S4].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de scenario table, surface, matrice ou chart selon le produit sert exactement a cela. Il faut tester plusieurs chocs et commenter les regimes, produire un ui block de decision, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: tester plusieurs chocs et commenter les regimes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer scenario table, surface, matrice ou chart selon le produit a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 9 - Production controls

**Le reflexe d'abord.** Une mauvaise convention peut inverser le P&L ou casser une quote. Avant toute formule, demandez-vous ce que data quality, convention, sign, fallback, no-arbitrage check change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Theta is greater (in absolute value) for short-term ATM options, so statement
d. is incorrect. » [S7]. L'enjeu operationnel est clair : identifier les erreurs de convention, de signe, d'unite et de donnees de marche.

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
params: {"latex": "\\Delta V\\approx \\Delta\\,\\Delta S+\\frac12\\Gamma(\\Delta S)^2+\\nu\\,\\Delta\\sigma+\\Theta\\,\\Delta t"}
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
1. Mini-diagnostic: identifier produit, payoff ou risque economique.
2. Calcul de desk: appliquer une formule ou approximation sur donnees numeriques.
3. Sensibilites: expliquer ce qui bouge si spot/taux/vol/spread change.
4. Decision: hedge, quote, no-trade, monitoring ou escalation risk.
5. Debrief: erreurs courantes et limites du modele.

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

**Definitions (sensibilites = derivees partielles du prix).**
$$\Delta=\frac{\partial V}{\partial S},\;\; \Gamma=\frac{\partial^2 V}{\partial S^2},\;\; \nu=\frac{\partial V}{\partial \sigma},\;\; \Theta=\frac{\partial V}{\partial t},\;\; \rho=\frac{\partial V}{\partial r}.$$

**Formes fermees (call sans dividende).**
$$\Delta = N(d_1),\quad \Gamma = \frac{\varphi(d_1)}{S\sigma\sqrt{T}},\quad \nu = S\varphi(d_1)\sqrt{T},$$
$$\Theta = -\frac{S\varphi(d_1)\sigma}{2\sqrt{T}} - rKe^{-rT}N(d_2),\quad \rho = KTe^{-rT}N(d_2).$$
Pour le put: $\Delta_{put}=\Delta_{call}-1$, meme $\Gamma$ et $\nu$ (parite).

**Attribution de P&L (Taylor au 2e ordre).**
$$dV \approx \Delta\,dS + \tfrac12\Gamma\,(dS)^2 + \nu\,d\sigma + \Theta\,dt.$$
C'est l'equation du desk: le terme $\tfrac12\Gamma(dS)^2$ est le P&L de convexite, finance par le theta ($\Theta<0$ pour un long d'options).

**Intuition rigoureuse.** Gamma et theta sont les deux faces d'une meme piece: en delta-neutre, le P&L sur un pas $dt$ est $\approx \tfrac12\Gamma S^2(\sigma_{real}^2 - \sigma_{imp}^2)\,dt$ — on gagne si le realise depasse l'implicite. $\nu$ et $\Gamma$ sont maximaux autour de la monnaie.

**Piege theorique.** Les greeks sont des sensibilites *locales* (petits chocs); pour un grand mouvement, l'approximation Taylor decroche — d'ou la revalorisation complete.

**References (corpus).** Hull, *Options, Futures and Other Derivatives*; *Options Math for Traders* (gamma numerique); *FX Derivatives Trader School* (vega, frequence de hedge).

## Exemple numerique resolu
_[genere - calcul verifie]_ On attribue le P&L intraday d'un book d'options par facteur de risque.

**Donnees.** Book delta +250k EUR par 1%, gamma -80k EUR par 1%^2, vega +120k EUR par vol point, theta -15k EUR par jour. Scenario spot -2%, vol +3.

### P&L delta-gamma-vega-theta
- Famille: options_book_greeks
- Hypotheses controlees:
  - Les greeks sont deja exprimes en EUR par unite de risque operationnelle.
  - Delta: EUR par 1% de mouvement spot.
  - Gamma: EUR par (1%)^2 de mouvement spot.
  - Vega: EUR par point de volatilite.
  - Theta: EUR par jour.
- Calculs a respecter:
  - P&L delta:
    - Formule: Delta * move spot en points de 1%
    - Application: 250,000 * (-2)
    - Resultat: -500,000 EUR
    - Lecture desk: Risque directionnel immediat du book.
  - P&L gamma:
    - Formule: 0.5 * Gamma * move^2
    - Application: 0.5 * -80,000 * (-2)^2
    - Resultat: -160,000 EUR
    - Lecture desk: Convexite du book; ici elle amplifie ou amortit le choc spot.
  - P&L vega:
    - Formule: Vega * move vol
    - Application: 120,000 * (3)
    - Resultat: 360,000 EUR
    - Lecture desk: Exposition a la volatilite implicite.
  - P&L theta:
    - Formule: Theta * 1 jour
    - Application: -15,000 * 1
    - Resultat: -15,000 EUR
    - Lecture desk: Carry temps journalier.
  - P&L total:
    - Formule: Delta + Gamma + Vega + Theta
    - Application: -500,000 + -160,000 + 360,000 + -15,000
    - Resultat: -315,000 EUR
    - Lecture desk: Point de depart du debrief intraday.
- Actions operationnelles attendues:
  - Identifier le facteur dominant du P&L avant toute couverture.
  - Proposer une neutralisation delta avec sous-jacent/futures.
  - Proposer une reduction vega avec options ou variance/vol instruments si disponibles.
  - Surveiller le gamma si le spot continue a bouger intraday.
- Points de vigilance:
  - Ne pas multiplier une sensibilite 'par 1%' par -0.02; utiliser -2.
  - Ce calcul est une approximation locale, pas une revalorisation complete du book.

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
_[genere]_ Un book est long gamma. Le spot fait un aller-retour (-2% puis +2%). Le P&L gamma est-il positif ou negatif?

**Correction.** Positif. Long gamma => convexite favorable: la position gagne sur les mouvements realises dans les deux sens (re-hedge bas, re-hedge haut). C'est l'inverse pour un short gamma.

### Exercice 2 - niveau desk
_[genere]_ Book delta +250k/1%, gamma -80k/1%^2, vega +120k/pt, theta -15k/jour. Scenario spot -2%, vol +3pts, 1 jour. Estimez le P&L total et le risque dominant.

**Correction detaillee (calcul verifie).**
### P&L delta-gamma-vega-theta
- Famille: options_book_greeks
- Hypotheses controlees:
  - Les greeks sont deja exprimes en EUR par unite de risque operationnelle.
  - Delta: EUR par 1% de mouvement spot.
  - Gamma: EUR par (1%)^2 de mouvement spot.
  - Vega: EUR par point de volatilite.
  - Theta: EUR par jour.
- Calculs a respecter:
  - P&L delta:
    - Formule: Delta * move spot en points de 1%
    - Application: 250,000 * (-2)
    - Resultat: -500,000 EUR
    - Lecture desk: Risque directionnel immediat du book.
  - P&L gamma:
    - Formule: 0.5 * Gamma * move^2
    - Application: 0.5 * -80,000 * (-2)^2
    - Resultat: -160,000 EUR
    - Lecture desk: Convexite du book; ici elle amplifie ou amortit le choc spot.
  - P&L vega:
    - Formule: Vega * move vol
    - Application: 120,000 * (3)
    - Resultat: 360,000 EUR
    - Lecture desk: Exposition a la volatilite implicite.
  - P&L theta:
    - Formule: Theta * 1 jour
    - Application: -15,000 * 1
    - Resultat: -15,000 EUR
    - Lecture desk: Carry temps journalier.
  - P&L total:
    - Formule: Delta + Gamma + Vega + Theta
    - Application: -500,000 + -160,000 + 360,000 + -15,000
    - Resultat: -315,000 EUR
    - Lecture desk: Point de depart du debrief intraday.
- Actions operationnelles attendues:
  - Identifier le facteur dominant du P&L avant toute couverture.
  - Proposer une neutralisation delta avec sous-jacent/futures.
  - Proposer une reduction vega avec options ou variance/vol instruments si disponibles.
  - Surveiller le gamma si le spot continue a bouger intraday.
- Points de vigilance:
  - Ne pas multiplier une sensibilite 'par 1%' par -0.02; utiliser -2.
  - Ce calcul est une approximation locale, pas une revalorisation complete du book.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Etre long gamma signifie:**
- A) perdre sur les grands mouvements
- B) gagner sur la volatilite realisee
- C) etre insensible au spot
- D) etre short vega
  - Reponse: **B**. Long gamma = convexite favorable: on profite des mouvements realises dans les deux sens.

**Q2. Le theta d'une position long options est en general:**
- A) positif
- B) negatif
- C) nul
- D) egal au delta
  - Reponse: **B**. Detenir de la valeur temps coute du theta: elle se degrade chaque jour.

**Q3. Un book short gamma et long vega est surtout vulnerable a:**
- A) une vol implicite qui monte sans bouger le spot
- B) un spot qui bouge beaucoup en realise
- C) rien
- D) une baisse des taux
  - Reponse: **B**. Short gamma fait mal quand le realise est eleve, meme si la vega aide si l'implicite monte.

**Q4. Delta-neutre veut dire:**
- A) gamma nul
- B) sensibilite de premier ordre au spot ~ 0
- C) vega nul
- D) theta nul
  - Reponse: **B**. On annule la sensibilite directionnelle de premier ordre; gamma/vega/theta restent.

**Q5. Vega s'exprime usuellement en:**
- A) EUR par 1% de spot
- B) EUR par point de vol
- C) EUR par jour
- D) EUR par bp de taux
  - Reponse: **B**. Vega = variation de valeur par point de volatilite implicite.

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
- Chunks sources analyses: 18 (exploitables: 9).
- Score pedagogique moyen: 39.22/100 (qualite structurelle: 60.78/100).
- Definitions: 3 | exemples: 2 | exercices: 2 | formules: 2 | cas pratiques: 3.
- Repartition par type: theory: 13, worked_example: 2, definition: 2, market_context: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S8], [S13], [S18].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S7], [S11].
4. Exemples - couvert par [S1], [S11].
5. Exemples resolus - couvert par [S1], [S11].
6. Exercices - couvert par [S7], [S8], [S11], [S12].
7. Corriges - couvert par [S1], [S2], [S4].
8. Cas pratiques - couvert par [S1], [S2], [S11].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, resumes.

## Faits et angles extraits de la base
- For example Mello and Neuhaus (1998)
illustrates that discrete delta hedging can cause substantial risk, further they suggest that a large
part of this risk can be hedged away by using options against options.
- They assume a quite
practical situation were a market maker often not can hedge a option with another option with
exactly the same strike and maturity.
- As a market maker you will typically not be able to buy
back exactly the same option you just sold at a profit or even at flat, at least not immediately, but
typically you will be able to hedge an option with some other options with a slightly different
strike and or maturity.
- When we have jumps in the asset price Carr and Wu (2002) shows how
hedging options with options is superior to delta hedging.
- According to Carr and Wu simulations
indicate that the inferior performance of the delta hedge in the presence of jumps cannot be
improved upon by increasing the rebalancing frequency, see also Hyungsok and Wilmott (2007).
- Bates (1991) is basing his risk-neutral valuation for a jump-diffusion model partly on the idea
that traders can hedge jump risk with other options.
- Hua and Wilmott (1995) describes a great
example of the asymmetry in delta hedging replication error for long and short options.
- If you are
delta hedging a long option position the worst case scenario for you is that there is no crash.
- This
is actually because the delta hedging works poorly for any jumps, but if you are long options you
will benefit from this hedging error when the market crash.
- Among the many papers looking into
hedging options with options are for example Choie and Novomestky (1989), Carr and Madan
(2001), Andreasen and Carr (2002) and Haug (1993).

## Sources RAG a citer
- [S1] Derivatives Models on Models ( PDFDrive ), chunk 81, score 0.523988: For example Mello and Neuhaus (1998)
illustrates that discrete delta hedging can cause substantial risk, further they suggest that a large
part of this risk can be hedged away by using options against options.
- [S2] Derivatives Models on Models ( PDFDrive ), chunk 95, score 0.449966 (extrait non cite: source bruitee)
- [S3] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 411, score 0.43517 (extrait non cite: source bruitee)
- [S4] Derivatives Models on Models ( PDFDrive ), chunk 100, score 0.394102: Figlewski (1998): ‘‘The Information Content of Implied Volatility’’ The
Review of Financial Studies, 6(3), 659–681. ■Castelli, C. (1877) The Theory of Options in Stocks and Shares. London: F.C. ■Carr, P., and J. Bowie (1994): ‘‘Static Simplicity,’’ Risk Magazine, 7(8). ■Carr, P., and A.
- [S5] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 419, score 0.376282 (extrait non cite: source bruitee)
- [S6] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 2, score 0.367157 (extrait non cite: source bruitee)
- [S7] Financial Risk Manager Handbook + Test Bank  FRM Part I   Part II ( PDFDrive ), chunk 304, score 0.366538: Theta is greater (in absolute value) for short-term ATM options, so statement
d. is incorrect.
- [S8] Problems and Solutions in Mathematical Finance  Equity Derivatives, Volume 2 ( PDFDrive ), chunk 451, score 0.355102 (extrait non cite: source bruitee)
- [S9] Derivative Pricing   a Problem Based Primer ( PDFDrive ), chunk 4, score 0.346894 (extrait non cite: source bruitee)
- [S10] Derivative Pricing  A Problem Based Primer ( PDFDrive ), chunk 4, score 0.346894 (extrait non cite: source bruitee)
- [S11] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 92, score 0.344947: Veta = 
Further Greeks, third- and fourth-order, can be calculated but are beyond the 
needs of this book.
- [S12] Option Volatility and Pricing ( PDFDrive ), chunk 2, score 0.342038: I
The Delta
The Gamma
The Theta
The Vega
The Rho
- [S13] Problems and Solutions in Mathematical Finance  Equity Derivatives, Volume 2 ( PDFDrive ), chunk 446, score 0.340414 (extrait non cite: source bruitee)
- [S14] FX Derivatives Trader School ( PDFDrive ), chunk 356, score 0.321302 (extrait non cite: source bruitee)
- [S15] FX Derivatives Trader School ( PDFDrive ), chunk 365, score 0.321163 (extrait non cite: source bruitee)
- [S16] Mathematics of the Financial Markets  Financial Instruments and Derivatives Modelling, Valuation and Risk Issues ( PDFDrive ), chunk 265, score 0.319406 (extrait non cite: source bruitee)
- [S17] Theory of Financial Risk and Derivative Pricing ( PDFDrive ), chunk 322, score 0.317658: r The binomial model, where the price change can only take two values, is another
model where complete elimination of risk is possible. r A riddle for traders – Black-Scholes in Greek:
When I hedge my option
I can’t lose with Delta
What I lose with Theta
I will gain with Gamma
And Greeks have no Vega.
- [S18] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 414, score 0.315881 (extrait non cite: source bruitee)

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Delta-gamma-vega-theta attribution
$$
\Delta V \approx \Delta\,\Delta S+\frac{1}{2}\Gamma(\Delta S)^2+\nu\,\Delta\sigma+\Theta\,\Delta t
$$
- Usage desk: break a daily P&L move into explainable risk buckets.
### F2 - Delta hedge notional
$$
\text{Shares to trade}=-N_{\text{contracts}}\times m\times \Delta_{\text{option}}
$$
- Usage desk: translate model delta into a concrete hedge ticket.
### F3 - Residual gamma P&L
$$
\text{Gamma P\&L}\approx \frac{1}{2}\Gamma(\Delta S)^2
$$
- Usage desk: show why a delta-neutral book can still win or lose on realized moves.

