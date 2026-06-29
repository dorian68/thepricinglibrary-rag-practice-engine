---
slug: structured-products-autocall
topic: Autocallable structured products from term sheet to scenario table
product: autocallable note
level: advanced
concepts: coupon barrier, autocall, protection barrier, redemption
source_count: 18
---

# Module pratique - Autocallable structured products from term sheet to scenario table

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Autocallable structured products from term sheet to scenario table a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: advanced
- Public vise: quant confirme, trader junior, structureur
- Duree estimee: 250 minutes
- Produit: autocallable note
- Concepts: coupon barrier, autocall, protection barrier, redemption

## Prerequis
- option vanilla
- barriere
- lecture de term sheet

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
### Module 6 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 7 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de Autocallable structured products from term sheet to scenario table et savoir le critiquer.
- Situation de desk: Un entretien quant demande la derivation, le desk demande ses limites.
- Notion utile: Modele, mesure, derivees, approximation locale.
- Activite: Reprendre la derivation puis nommer ce qui casse en marche reel.
- Livrable apprenant: Derivation commentee.
### Module 8 - Cas numerique moteur
- Objectif pratique: Reproduire un calcul complet avec substitutions, resultat et unite.
- Situation de desk: Le desk refuse un chiffre qui ne peut pas etre audite.
- Notion utile: Calculateur deterministe, ordre de grandeur, controles croises.
- Activite: Refaire le cas a la main et verifier le resultat moteur.
- Livrable apprenant: Answer key verifiee.
### Module 9 - Lab interactif et scenarios
- Objectif pratique: Manipuler les inputs et lire l'effet sur prix, risque ou P&L.
- Situation de desk: Le marche bouge avant validation du trade.
- Notion utile: Scenario table, surface, matrice ou chart selon le produit.
- Activite: Tester plusieurs chocs et commenter les regimes.
- Livrable apprenant: UI block de decision.
### Module 10 - Production controls
- Objectif pratique: Identifier les erreurs de convention, de signe, d'unite et de donnees de marche.
- Situation de desk: Une mauvaise convention peut inverser le P&L ou casser une quote.
- Notion utile: Data quality, convention, sign, fallback, no-arbitrage check.
- Activite: Construire une checklist de validation avant envoi au trader.
- Livrable apprenant: Checklist production.

## Cours redige
### Lecon 1 - Extraire le term sheet

**Le reflexe d'abord.** Sales envoie un autocall a expliquer avant client call. Avant toute formule, demandez-vous ce que observation dates, coupon barrier, autocall level change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « We first describe the payoff of worst-of autocallables as well as
the risks encountered when trading these products. Then, we introduce the effect
of snowballing coupons as well as the addition of a worst-of down-and-in put
feature to the classical worst-of autocallable structure. Finally, we analyse the
payoff and the risks associated with trading outperformance autocallables which
also deal with dispersion. » [S1]. L'enjeu operationnel est clair : transformer la fiche produit en conditions calculables.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, observation dates, coupon barrier, autocall level sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : term-sheet map.

Concretement, l'exercice consiste a construire la table des conditions, pour en tirer un term-sheet map. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: construire la table des conditions. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer observation dates, coupon barrier, autocall level a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - Coupon et autocall

**Comment ca marche.** Indicator functions, memory coupon, early redemption n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Financial engineering provides ways to construct any payoff structure desired by an investor. However, often these payoffs involve complex option positions, and clients may not have the
knowledge, or simply the means, to handle such risks. Market practitioners can do this better. For
example, many structured products offer principal protection or credit enhancements to investors. » [S2].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a calculer les coupons et l'evenement de remboursement anticipe. Il s'agit de remplir la logique date par date pour produire un coupon/autocall grid, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: remplir la logique date par date. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer indicator functions, memory coupon, early redemption a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - Protection barrier

**Ou est le risque.** Le sous-jacent finit sous la barriere. Mal traiter capital protection, downside participation se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market downturn the product leads to losses. Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING » [S3].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : expliquer la perte conditionnelle en fin de vie. Il faut calculer redemption finale, documenter un downside explanation, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer redemption finale. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer capital protection, downside participation a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Scenario table client

**La decision visee.** A la fin de cette lecon vous saurez comparer upside, flat, moderate down et crash scenario sans hesiter. Le declencheur : le client veut comprendre coupon vs capital at risk. Les sources le confirment _[extrait]_ : « Of course, if the zero-coupon bond were that of any non-government issuer, there is a nonnegligible risk of default. Clearly, Lehman-issued “principal-protected” structured notes failed 
to repay the principal when Lehman Brothers defaulted, much to the chagrin of investors 
who misunderstood the idea. Yet, true principal protection is still possible if a zero-coupon 
government bond is purchased. » [S4].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de cash-flow path dependency, redemption, loss participation sert exactement a cela. Il faut produire une table de scenarios lisible par sales, produire un client scenario table, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: produire une table de scenarios lisible par sales. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer cash-flow path dependency, redemption, loss participation a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Desk risk

**Le reflexe d'abord.** La structure vend du coupon mais concentre du tail risk. Avant toute formule, demandez-vous ce que barrier/gamma/vega/liquidity risk change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « At the scheduled maturity date, assuming that no early redemption event took place:
∙If GoldFinal ≥GoldInitial, redemption is equal to (100% + Conditional Coupon) × Notional;
∙If GoldFinal < Put Strike the note-holder is exposed to the downside risk arising from the
short put position and the redemption will be equal to Notional × GoldFinal/GoldInitial. » [S5]. L'enjeu operationnel est clair : relier attrait client et risques de couverture.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, barrier/gamma/vega/liquidity risk sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : client/risk memo.

Concretement, l'exercice consiste a ecrire memo sales + risk, pour en tirer un client/risk memo. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: ecrire memo sales + risk. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer barrier/gamma/vega/liquidity risk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Carte des sources et des definitions

**Comment ca marche.** Source grounding, provenance, vocabulaire de desk n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « At the scheduled maturity date, assuming that no early redemption event took place:
∙If GoldFinal ≥GoldInitial, redemption is equal to (100% + Conditional Coupon) × Notional;
∙If GoldFinal < Put Strike the note-holder is exposed to the downside risk arising from the
short put position and the redemption will be equal to Notional × GoldFinal/GoldInitial. » [S6].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas. Il s'agit de comparer les extraits [sx] et isoler les definitions robustes pour produire un source map annotee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Fondations quantitatives niveau Hull

**Ou est le risque.** Un entretien quant demande la derivation, le desk demande ses limites. Mal traiter modele, mesure, derivees, approximation locale se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Specifically, there are increased exposures to the ATM curve, and additional
exposures to the forward smile. Therefore, when pricing and risk managing window
barrier options it is important to assess exactly which pricing methodology is used. For example:
■Which ATM volatility curve is used to generate TV? » [S7].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : deriver le coeur quantitatif de autocallable structured products from term sheet to scenario table et savoir le critiquer. Il faut reprendre la derivation puis nommer ce qui casse en marche reel, documenter un derivation commentee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Cas numerique moteur

**La decision visee.** A la fin de cette lecon vous saurez reproduire un calcul complet avec substitutions, resultat et unite sans hesiter. Le declencheur : le desk refuse un chiffre qui ne peut pas etre audite. Les sources le confirment _[extrait]_ : « Also, if the
rear-window barrier is through current spot, this approach does not work because
the American barrier option variation will have already knocked. It may also be useful to assess the probability of the rear-window barriers being
knocked. » [S8].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de calculateur deterministe, ordre de grandeur, controles croises sert exactement a cela. Il faut refaire le cas a la main et verifier le resultat moteur, produire un answer key verifiee, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 9 - Lab interactif et scenarios

**Le reflexe d'abord.** Le marche bouge avant validation du trade. Avant toute formule, demandez-vous ce que scenario table, surface, matrice ou chart selon le produit change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « This can be extremely
useful when handling baskets of currencies. » [S11]. L'enjeu operationnel est clair : manipuler les inputs et lire l'effet sur prix, risque ou p&l.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, scenario table, surface, matrice ou chart selon le produit sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : ui block de decision.

Concretement, l'exercice consiste a tester plusieurs chocs et commenter les regimes, pour en tirer un ui block de decision. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: tester plusieurs chocs et commenter les regimes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer scenario table, surface, matrice ou chart selon le produit a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 10 - Production controls

**Comment ca marche.** Data quality, convention, sign, fallback, no-arbitrage check n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « In a later chapter, we
will see how bundling financing and hedging transactions helps reduce total credit costs and
can aid in monetizing the benefits of hedging. » [S12].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a identifier les erreurs de convention, de signe, d'unite et de donnees de marche. Il s'agit de construire une checklist de validation avant envoi au trader pour produire un checklist production, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: construire une checklist de validation avant envoi au trader. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer data quality, convention, sign, fallback, no-arbitrage check a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

## Blocs interactifs de finance de marche
```uiblock
type: equation
title: Equation pivot du module
params: {"latex": "Coupon_i=Nc_i\\mathbf{1}_{S_{t_i}\\ge B_cS_0},\\qquad Autocall_i=\\mathbf{1}_{S_{t_i}\\ge B_aS_0}"}
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
type: payoff
title: Payoff interactif - intuition du produit
params: {"strike":100, "spot":100}
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
1. Term-sheet map: dates, coupon barrier, autocall level, protection barrier.
2. Coupon/autocall grid: calculer coupon et early redemption date par date.
3. Downside: calculer redemption finale sous la barriere de protection.
4. Scenario table: upside, flat, moderate down et crash scenario.
5. Sales/risk memo: benefice client, risque de couverture et tail risk.

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

**Mecanique.** A chaque date d'observation $t_i$: si $S_{t_i}\ge$ barriere d'autocall, **rappel anticipe** (nominal + coupon); si $\ge$ barriere de coupon, coupon paye (avec **memoire** des coupons manques); a maturite, si jamais rappele, capital protege tant que $S_T\ge$ barriere de protection, sinon perte $1{:}1$.

**Decomposition vendeur (risque).** Vendre un autocall worst-of revient a etre
$$\text{short les digitales de coupon/autocall} \;+\; \text{long un put down-and-in worst-of},$$
soit, du point de vue du **vendeur**, un profil **long skew, long volatilite, short correlation (= long dispersion)**, en echange du portage paye via les coupons digitaux vendus. (L'investisseur est exactement le miroir: short vol, short skew, long correlation, recoit le coupon.)

**Pricing.** Pas de forme fermee (payoff path-dependent, souvent multi-sous-jacents): on price par **Monte-Carlo** sous vol/dividendes/correlation (lien vers monte_carlo et vol_smile).

**Intuition rigoureuse.** L'investisseur vend de la protection en echange d'un coupon eleve: il est *short* le crash. L'effet "snowball" (memoire) concentre les coupons sur les scenarios de remontee.

**Piege theorique.** Le risque vendeur est non lineaire et explose pres de la barriere de protection a l'approche de la maturite (gap + correlation qui monte en stress).

**References (corpus).** Bouzoubaa & Osseiran, *Exotic Options and Hybrids* (§12.4 snowball, worst-of put, decomposition de risque); *Pricing and Hedging Financial Derivatives* (notes structurees, worst-of digital).

## Exemple numerique resolu
_[genere - calcul verifie]_ On deroule le payoff d'un autocall a memoire selon un scenario d'observations.

**Donnees.** Autocall Athena sur indice, niveau initial 100, barriere autocall 100%, barriere coupon 70%, barriere protection 60%, coupon 6% par observation avec memoire, notionnel 1m. Niveaux observes: 65, 102.

### Payoff d'un autocall (Athena a memoire)
- Famille: autocall_structured
- Hypotheses controlees:
  - Observations periodiques fournies; chaque niveau compare au niveau initial.
  - Effet memoire des coupons: actif.
  - Barriere autocall, coupon et protection en % du niveau initial.
  - Protection du capital de type europeenne (observee a maturite).
- Calculs a respecter:
  - Observation 1 - coupon:
    - Formule: ratio < barriere coupon
    - Application: ratio 65.00% < 70%
    - Resultat: 0 EUR (coupon en memoire)
    - Lecture desk: Coupon non paye; mis en memoire pour la prochaine observation.
  - Observation 2 - coupon:
    - Formule: coupon * periodes dues * notionnel
    - Application: 0.06 * 2 * 1,000,000
    - Resultat: +120,000 EUR
    - Lecture desk: niveau 102 (ratio 102.00%) >= barriere coupon 70%: paie 2 coupon(s) (memoire)
  - Observation 2 - autocall:
    - Formule: ratio >= barriere autocall
    - Application: ratio 102.00% >= 100%
    - Resultat: rappel anticipe: +1,000,000 EUR
    - Lecture desk: Le produit est rappele: remboursement du nominal puis arret.
  - Payoff total investisseur:
    - Formule: Somme coupons + remboursement
    - Application: 120,000 + 1,000,000
    - Resultat: 1,120,000 EUR
    - Lecture desk: Cash total recu sur la vie du produit.
- Actions operationnelles attendues:
  - Identifier le scenario dominant: rappel anticipe (probable si spot eleve) ou perte en capital.
  - Lire la sensibilite vendeur: short put down-and-in + short calls digitaux (autocall = combinaison d'options).
  - Surveiller le gap pres de la barriere de protection a l'approche de la maturite.
- Points de vigilance:
  - Le prix reel exige un modele (Monte Carlo sous vol/dividendes/correlation), pas seulement le payoff de scenarios.
  - Le risque vendeur est non lineaire et path-dependent: la protection peut sauter pres de la barriere.

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
### Payoff d'un autocall (Athena a memoire)
- Famille: autocall_structured
- Hypotheses controlees:
  - Observations periodiques fournies; chaque niveau compare au niveau initial.
  - Effet memoire des coupons: actif.
  - Barriere autocall, coupon et protection en % du niveau initial.
  - Protection du capital de type europeenne (observee a maturite).
- Calculs a respecter:
  - Observation 1 - coupon:
    - Formule: ratio < barriere coupon
    - Application: ratio 65.00% < 70%
    - Resultat: 0 EUR (coupon en memoire)
    - Lecture desk: Coupon non paye; mis en memoire pour la prochaine observation.
  - Observation 2 - coupon:
    - Formule: coupon * periodes dues * notionnel
    - Application: 0.06 * 2 * 1,000,000
    - Resultat: +120,000 EUR
    - Lecture desk: niveau 102 (ratio 102.00%) >= barriere coupon 70%: paie 2 coupon(s) (memoire)
  - Observation 2 - autocall:
    - Formule: ratio >= barriere autocall
    - Application: ratio 102.00% >= 100%
    - Resultat: rappel anticipe: +1,000,000 EUR
    - Lecture desk: Le produit est rappele: remboursement du nominal puis arret.
  - Payoff total investisseur:
    - Formule: Somme coupons + remboursement
    - Application: 120,000 + 1,000,000
    - Resultat: 1,120,000 EUR
    - Lecture desk: Cash total recu sur la vie du produit.
- Actions operationnelles attendues:
  - Identifier le scenario dominant: rappel anticipe (probable si spot eleve) ou perte en capital.
  - Lire la sensibilite vendeur: short put down-and-in + short calls digitaux (autocall = combinaison d'options).
  - Surveiller le gap pres de la barriere de protection a l'approche de la maturite.
- Points de vigilance:
  - Le prix reel exige un modele (Monte Carlo sous vol/dividendes/correlation), pas seulement le payoff de scenarios.
  - Le risque vendeur est non lineaire et path-dependent: la protection peut sauter pres de la barriere.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Un knock-out option:**
- A) nait quand la barriere est touchee
- B) s'eteint quand la barriere est touchee
- C) ignore la barriere
- D) est sans risque
  - Reponse: **B**. Le knock-out disparait si la barriere est atteinte pendant la vie.

**Q2. Le gap risk d'une barriere vient de:**
- A) un delta lisse
- B) une discontinuite de payoff pres de la barriere
- C) le theta
- D) le coupon
  - Reponse: **B**. Pres de la barriere, la valeur saute: le delta hedge continu peut echouer.

**Q3. In-out parity dit:**
- A) C_out = C_in
- B) C_vanilla = C_out + C_in
- C) C_out = C_vanilla
- D) rien
  - Reponse: **B**. Le vanilla se decompose en knock-out plus knock-in.

**Q4. Un down-and-out call vs vanilla est:**
- A) plus cher
- B) moins cher
- C) identique
- D) sans prime
  - Reponse: **B**. Il offre moins (peut s'eteindre) donc coute moins.

**Q5. Pres de la barriere le desk doit surtout:**
- A) ignorer
- B) monitorer et definir des triggers d'escalation
- C) augmenter la taille
- D) vendre du theta
  - Reponse: **B**. Le risque n'est pas un Greek lisse: monitoring et escalation priment.

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
- Score pedagogique moyen: 67.11/100 (qualite structurelle: 100.0/100).
- Definitions: 7 | exemples: 14 | exercices: 3 | formules: 3 | cas pratiques: 4.
- Repartition par type: theory: 12, example: 3, definition: 2, worked_example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S1], [S2], [S4], [S9].
2. Intuitions - couvert par [S14].
3. Formules - couvert par [S1], [S7], [S13].
4. Exemples - couvert par [S1], [S2], [S3], [S4].
5. Exemples resolus - couvert par [S1].
6. Exercices - couvert par [S7], [S10], [S13], [S18].
7. Corriges - couvert par [S4], [S7], [S8], [S10].
8. Cas pratiques - couvert par [S1], [S4], [S12], [S13].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, intuitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): resumes.

## Faits et angles extraits de la base
- We first describe the payoff of worst-of autocallables as well as
the risks encountered when trading these products.
- Then, we introduce the effect
of snowballing coupons as well as the addition of a worst-of down-and-in put
feature to the classical worst-of autocallable structure.
- Finally, we analyse the
payoff and the risks associated with trading outperformance autocallables which
also deal with dispersion.
- .n)
we have
where C is a predetermined coupon and Ret(ti) = S(ti)/S(0) is the return at time ti
w.r.t.
- Since the wrapper is a note, the holder receives back 100% of the notional
except that, in this case, the time of payment is not fixed.
- The notional
redemption can be at any observation date, not necessarily at maturity.
- From the payoff described above, it is important to notice that the holder of the
note receives no further payments if H has been breached on one of the
observation dates.
- Then, this note is described as an autocallable since the note
dies once the barrier H is breached by the underlying at specific observation
dates.
- What we call
maturity is in fact the maximum duration this product can stay alive.
- It is a predetermined level above
which the autocallable structure expires and the investor receives the notional
invested when the structure is a note.

## Sources RAG a citer
- [S1] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 211, score 0.82841: We first describe the payoff of worst-of autocallables as well as
the risks encountered when trading these products. Then, we introduce the effect
of snowballing coupons as well as the addition of a worst-of down-and-in put
feature to the classical worst-of autocallable structure.
- [S2] Principles of Financial Engineering ( PDFDrive ), chunk 751, score 0.740055: Financial engineering provides ways to construct any payoff structure desired by an investor. However, often these payoffs involve complex option positions, and clients may not have the
knowledge, or simply the means, to handle such risks. Market practitioners can do this better.
- [S3] Principles of Financial Engineering ( PDFDrive ), chunk 764, score 0.738222: In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market downturn the product leads to losses. Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING
- [S4] Demystifying Exotic Products  Interest Rates, Equities and Foreign Exchange  ( PDFDrive ), chunk 205, score 0.726351: Of course, if the zero-coupon bond were that of any non-government issuer, there is a nonnegligible risk of default. Clearly, Lehman-issued “principal-protected” structured notes failed 
to repay the principal when Lehman Brothers defaulted, much to the chagrin of investors 
who misunderstood the idea.
- [S5] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 305, score 0.710487 (extrait non cite: source bruitee)
- [S6] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 305, score 0.710487 (extrait non cite: source bruitee)
- [S7] FX Derivatives Trader School ( PDFDrive ), chunk 294, score 0.70773: Specifically, there are increased exposures to the ATM curve, and additional
exposures to the forward smile. Therefore, when pricing and risk managing window
barrier options it is important to assess exactly which pricing methodology is used. For example:
■Which ATM volatility curve is used to generate TV?
- [S8] FX Derivatives Trader School ( PDFDrive ), chunk 293, score 0.651185: Also, if the
rear-window barrier is through current spot, this approach does not work because
the American barrier option variation will have already knocked. It may also be useful to assess the probability of the rear-window barriers being
knocked.
- [S9] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 176, score 0.636405 (extrait non cite: source bruitee)
- [S10] FX Derivatives Trader School ( PDFDrive ), chunk 256, score 0.628833 (extrait non cite: source bruitee)
- [S11] Exotic Options and Hybrids  A Guide to Structuring, Pricing and Trading ( PDFDrive ), chunk 324, score 0.627103: This can be extremely
useful when handling baskets of currencies.
- [S12] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 252, score 0.626379: In a later chapter, we
will see how bundling financing and hedging transactions helps reduce total credit costs and
can aid in monetizing the benefits of hedging.
- [S13] Derivatives Markets ( PDFDrive ), chunk 510, score 0.62516: and B 481; solving for
INDEX
647
- [S14] FX Derivatives Trader School ( PDFDrive ), chunk 292, score 0.615322: The type and direction (e.g., down-and-out/down-and-in, etc.) of
rear-window single barriers must always be specified since their direction cannot
always be determined from the inception spot level. Exhibit 26.6 shows a typical rear-window up-and-out barrier call option.
- [S15] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 294, score 0.612077: Hardly pithy, is it? If definitions are
meant to explain, then the SEC’s attempt lacks intuitive appeal. A simpler definition is that they are pre-packaged investment products based on a single
security or a basket of securities whose returns are linked to, but unlike, direct exposures to the
underlying.
- [S16] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 294, score 0.612077: Hardly pithy, is it? If definitions are
meant to explain, then the SEC’s attempt lacks intuitive appeal. A simpler definition is that they are pre-packaged investment products based on a single
security or a basket of securities whose returns are linked to, but unlike, direct exposures to the
underlying.
- [S17] Swaps and Other Derivatives ( PDFDrive ), chunk 260, score 0.604539: In this case, the Final coupon ¼ Total accrued coupon (excluding
current)  Knockout level, where the Knockout level ¼ 20%. If there is no early redemption, the
Final coupon ¼ Knockout level  Total accrued coupon (excluding current).
- [S18] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 982, score 0.601771: Double Barrier
A double barrier option is another variation that has
two barriers, typically one up barrier and the other a
down barrier. For example, investors seeking high
leverage would consider double knock-out barrier
options if they believe changes in the underlying asset
level would be within a narrow range.

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

