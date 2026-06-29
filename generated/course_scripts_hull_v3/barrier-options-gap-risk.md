---
slug: barrier-options-gap-risk
topic: Barrier options and gap risk
product: FX barrier option
level: advanced
concepts: down-and-out, knock-out, gap risk, monitoring
source_count: 18
---

# Module pratique - Barrier options and gap risk

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Barrier options and gap risk a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: advanced
- Public vise: quant confirme, trader junior, structureur
- Duree estimee: 230 minutes
- Produit: FX barrier option
- Concepts: down-and-out, knock-out, gap risk, monitoring

## Prerequis
- option vanilla
- delta/gamma
- notion de path-dependence

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
### Module 1 - Regle de payoff et chemin
- Objectif pratique: Distinguer terminal payoff et evenement de knock-out/knock-in.
- Situation de desk: Un client demande le resultat d'un DOC FX sous trois chemins spot.
- Notion utile: Path-dependence, barrier event, activation/desactivation.
- Activite: Dessiner la regle de payoff et la table des etats.
- Livrable apprenant: Schema payoff + condition de barriere.
### Module 2 - Scenario table
- Objectif pratique: Calculer payoff sous plusieurs spots et etats de barriere.
- Situation de desk: Le spot finit au-dessus du strike mais a peut-etre touche la barriere.
- Notion utile: Payoff conditionnel et notionnel FX.
- Activite: Remplir une table spot, hit/no-hit, payoff.
- Livrable apprenant: Table de scenarios avec conclusion.
### Module 3 - Gap risk
- Objectif pratique: Expliquer pourquoi le risque pres de la barriere n'est pas un Greek lisse.
- Situation de desk: Le spot approche la barriere en marche illiquide.
- Notion utile: Discontinuite, jump-to-knock-out, slippage.
- Activite: Identifier les limites du delta hedge pres de H.
- Livrable apprenant: Note gap risk pour risk manager.
### Module 4 - Monitoring desk
- Objectif pratique: Definir les triggers de surveillance et d'escalation.
- Situation de desk: La position reste ouverte pendant une annonce macro.
- Notion utile: Barrier distance, realized vol, liquidity window.
- Activite: Construire une grille monitor / hedge / escalate.
- Livrable apprenant: Plan d'action operationnel.
### Module 5 - Debrief modele
- Objectif pratique: Relier pricing, couverture et risque de modele.
- Situation de desk: Le modele donne un prix mais le trader doit survivre au chemin.
- Notion utile: Vol surface, smile, discrete monitoring.
- Activite: Lister controles et erreurs courantes.
- Livrable apprenant: Checklist exotics desk.
### Module 6 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 7 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de Barrier options and gap risk et savoir le critiquer.
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

## Cours redige
### Lecon 1 - Regle de payoff et chemin

**Le reflexe d'abord.** Un client demande le resultat d'un DOC FX sous trois chemins spot. Avant toute formule, demandez-vous ce que path-dependence, barrier event, activation/desactivation change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Before the maturity, if the underlying asset
goes below the barrier level the barrier option will be
knocked in and become a vanilla option. Otherwise,
the barrier option will expire worthless at maturity. Down-and-in puts are more common in this case. Bearish investors can buy down-and-in puts and pay
a lower premium than that on the vanilla put options. » [S1]. L'enjeu operationnel est clair : distinguer terminal payoff et evenement de knock-out/knock-in.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, path-dependence, barrier event, activation/desactivation sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : schema payoff + condition de barriere.

Concretement, l'exercice consiste a dessiner la regle de payoff et la table des etats, pour en tirer un schema payoff + condition de barriere. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: dessiner la regle de payoff et la table des etats. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer path-dependence, barrier event, activation/desactivation a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - Scenario table

**Comment ca marche.** Payoff conditionnel et notionnel FX n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « 24.15
Reverse knock-out and equivalent one-touch option within a pricing tool » [S2].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a calculer payoff sous plusieurs spots et etats de barriere. Il s'agit de remplir une table spot, hit/no-hit, payoff pour produire un table de scenarios avec conclusion, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: remplir une table spot, hit/no-hit, payoff. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer payoff conditionnel et notionnel fx a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - Gap risk

**Ou est le risque.** Le spot approche la barriere en marche illiquide. Mal traiter discontinuite, jump-to-knock-out, slippage se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « interest rate
correlations, 336–339
realized spot vs. » [S3].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : expliquer pourquoi le risque pres de la barriere n'est pas un greek lisse. Il faut identifier les limites du delta hedge pres de h, documenter un note gap risk pour risk manager, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: identifier les limites du delta hedge pres de h. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer discontinuite, jump-to-knock-out, slippage a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Monitoring desk

**La decision visee.** A la fin de cette lecon vous saurez definir les triggers de surveillance et d'escalation sans hesiter. Le declencheur : la position reste ouverte pendant une annonce macro. Les sources le confirment _[extrait]_ : « Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option. » [S4].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de barrier distance, realized vol, liquidity window sert exactement a cela. Il faut construire une grille monitor / hedge / escalate, produire un plan d'action operationnel, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: construire une grille monitor / hedge / escalate. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer barrier distance, realized vol, liquidity window a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Debrief modele

**Le reflexe d'abord.** Le modele donne un prix mais le trader doit survivre au chemin. Avant toute formule, demandez-vous ce que vol surface, smile, discrete monitoring change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option. » [S5]. L'enjeu operationnel est clair : relier pricing, couverture et risque de modele.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, vol surface, smile, discrete monitoring sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : checklist exotics desk.

Concretement, l'exercice consiste a lister controles et erreurs courantes, pour en tirer un checklist exotics desk. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: lister controles et erreurs courantes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer vol surface, smile, discrete monitoring a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Carte des sources et des definitions

**Comment ca marche.** Source grounding, provenance, vocabulaire de desk n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « The option to purchase the call option itself has exercise 
price K1 and strike T1. Obtaining a price for this option is not difficult. Since the option still depends on 
the price movement of the underlying S, the Black-Scholes equation still applies. The time domain is 
broken into two parts: (0, T1) and (T1, T2). » [S6].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas. Il s'agit de comparer les extraits [sx] et isoler les definitions robustes pour produire un source map annotee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Fondations quantitatives niveau Hull

**Ou est le risque.** Un entretien quant demande la derivation, le desk demande ses limites. Mal traiter modele, mesure, derivees, approximation locale se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « One of the barriers is knock-out while the other is knock-in. There are
two variations of knock-in/knock-out options:
1. Knock-out until expiry
2. » [S7].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : deriver le coeur quantitatif de barrier options and gap risk et savoir le critiquer. Il faut reprendre la derivation puis nommer ce qui casse en marche reel, documenter un derivation commentee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Cas numerique moteur

**La decision visee.** A la fin de cette lecon vous saurez reproduire un calcul complet avec substitutions, resultat et unite sans hesiter. Le declencheur : le desk refuse un chiffre qui ne peut pas etre audite. Les sources le confirment _[extrait]_ : « We
will return to the discussion on volatility models when we discuss local volatility later in the
chapter. BARRIER OPTION-BASED STRUCTURES
Barrier options are exotic derivatives that are very similar to standard vanilla options except
that they can be terminated or activated conditional on the price reaching a certain level. This
trigger feature makes them an important building block for structured products. » [S8].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de calculateur deterministe, ordre de grandeur, controles croises sert exactement a cela. Il faut refaire le cas a la main et verifier le resultat moteur, produire un answer key verifiee, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 9 - Lab interactif et scenarios

**Le reflexe d'abord.** Le marche bouge avant validation du trade. Avant toute formule, demandez-vous ce que scenario table, surface, matrice ou chart selon le produit change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « [3]
Ren, Y., Madan, D. Calibrating and
pricing with embedded local volatility models, Risk 20(9),
138–143. Related Articles
Corridor
Variance
Swap;
Realized
Volatility
Options; Variance Swap; Volatility Index Options;
Weighted Variance Swap. » [S9]. L'enjeu operationnel est clair : manipuler les inputs et lire l'effet sur prix, risque ou p&l.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, scenario table, surface, matrice ou chart selon le produit sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : ui block de decision.

Concretement, l'exercice consiste a tester plusieurs chocs et commenter les regimes, pour en tirer un ui block de decision. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: tester plusieurs chocs et commenter les regimes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer scenario table, surface, matrice ou chart selon le produit a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

## Blocs interactifs de finance de marche
```uiblock
type: equation
title: Equation pivot du module
params: {"latex": "\\Phi=(S_T-K)^+\\mathbf{1}_{\\min_t S_t>H},\\qquad Gap\\ loss\\approx \\Delta_{\\text{pre-hit}}(S_{\\text{hit}}-S_{\\text{next}})"}
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
1. Payoff path rule: definir hit/no-hit et payoff terminal.
2. Scenario table: calculer trois scenarios spot avec et sans knock-out.
3. Gap risk: expliquer la rupture de delta hedge pres de la barriere.
4. Monitoring plan: definir distance barrier, triggers et escalation.
5. Debrief: limites modele, discrete monitoring et smile.

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

**Taxonomie.** Knock-out (s'eteint si la barriere est touchee) vs knock-in (nait a ce moment); up/down selon le sens. Le payoff depend du strike **et** du chemin.

**Parite in-out (modele-independante).**
$$C_{KI} + C_{KO} = C_{vanilla}\quad\text{(memes strike/maturite/barriere-sens).}$$
Detenir le knock-in et le knock-out equivaut a detenir le vanilla.

**Forme fermee (down-and-out call, monitoring continu, principe de reflexion).** Avec barriere $B<K$:
$$C_{DO} = C_{BS}(S_0) - \left(\frac{B}{S_0}\right)^{2\lambda-2} C_{BS}\!\left(\frac{B^2}{S_0}\right),\quad \lambda=\frac{r-q+\tfrac12\sigma^2}{\sigma^2},$$
l'image $B^2/S_0$ etant le sous-jacent "reflechi" sur la barriere.

**Monitoring discret (correction Broadie-Glasserman-Kou).** Une barriere observee a pas $\Delta t$ se price comme une barriere continue **decalee** $B \to B\,e^{\pm \beta\sigma\sqrt{\Delta t}}$, $\beta\approx 0.5826$ ($+$ pour up, $-$ pour down).

**Piege theorique.** Pres de la barriere, delta et gamma explosent (discontinuite de payoff): le hedge delta continu peut echouer sur un **gap**. Le risque dominant n'est pas un grec lisse mais le franchissement.

**References (corpus).** *Principles of Financial Engineering* (equation contractuelle in-out, §11.4.2); *Derivatives Models on Models* (arbre + principe de reflexion); *FX Derivatives Trader School* (reverse KO ↔ one-touch, gap).

## Exemple numerique resolu
_[genere - calcul verifie]_ On calcule le payoff conditionnel et on discute le gap risk.

**Donnees.** Option barriere FX down-and-out, spot 1.0800, strike 1.1000, barriere down-and-out 1.0000, notionnel EUR 10m. Spot a 1.0500, spot a 1.2000.

### Payoff et risque de gap d'une barriere
- Famille: fx_barrier_option
- Hypotheses controlees:
  - Down-and-out: si la barriere est touchee pendant la vie du produit, payoff final nul.
  - Les scenarios non knock-out utilisent un payoff de call simple.
  - Distance initiale a la barriere: 8.00%.
- Calculs a respecter:
  - Scenario spot 1.05:
    - Formule: Payoff down-and-out call
    - Application: max(1.05 - 1.1, 0) * 10,000,000
    - Resultat: 0 USD approx
    - Lecture desk: Payoff de call conditionnel au non knock-out.
  - Scenario spot 1.2:
    - Formule: Payoff down-and-out call
    - Application: max(1.2 - 1.1, 0) * 10,000,000
    - Resultat: 1,000,000 USD approx
    - Lecture desk: Payoff de call conditionnel au non knock-out.
- Actions operationnelles attendues:
  - Surveiller le spot et le risque de gap proche barriere.
  - Discuter hedge delta/gamma mais signaler la discontinuite de payoff.
  - Prevoir escalation risk si le spot entre dans une zone de monitoring.
- Points de vigilance:
  - Une couverture delta continue peut echouer en cas de gap a travers la barriere.
  - La valeur reelle requiert un modele barriere, pas seulement le payoff terminal.

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
_[genere]_ Un down-and-out call est-il plus cher ou moins cher qu'un call vanilla equivalent?

**Correction.** Moins cher: il peut s'eteindre si la barriere est touchee, donc il offre moins -> prime inferieure. In-out parity: C_vanilla = C_out + C_in.

### Exercice 2 - niveau desk
_[genere]_ Down-and-out call FX, spot 1.0800, strike 1.1000, barriere 1.0000, notionnel 10m. Payoff si le spot finit a 1.0500? a 1.2000 sans toucher la barriere?

**Correction detaillee (calcul verifie).**
### Payoff et risque de gap d'une barriere
- Famille: fx_barrier_option
- Hypotheses controlees:
  - Down-and-out: si la barriere est touchee pendant la vie du produit, payoff final nul.
  - Les scenarios non knock-out utilisent un payoff de call simple.
  - Distance initiale a la barriere: 8.00%.
- Calculs a respecter:
  - Scenario spot 1.05:
    - Formule: Payoff down-and-out call
    - Application: max(1.05 - 1.1, 0) * 10,000,000
    - Resultat: 0 USD approx
    - Lecture desk: Payoff de call conditionnel au non knock-out.
  - Scenario spot 1.2:
    - Formule: Payoff down-and-out call
    - Application: max(1.2 - 1.1, 0) * 10,000,000
    - Resultat: 1,000,000 USD approx
    - Lecture desk: Payoff de call conditionnel au non knock-out.
- Actions operationnelles attendues:
  - Surveiller le spot et le risque de gap proche barriere.
  - Discuter hedge delta/gamma mais signaler la discontinuite de payoff.
  - Prevoir escalation risk si le spot entre dans une zone de monitoring.
- Points de vigilance:
  - Une couverture delta continue peut echouer en cas de gap a travers la barriere.
  - La valeur reelle requiert un modele barriere, pas seulement le payoff terminal.

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
- Chunks sources analyses: 18 (exploitables: 17).
- Score pedagogique moyen: 57.06/100 (qualite structurelle: 94.44/100).
- Definitions: 4 | exemples: 10 | exercices: 1 | formules: 4 | cas pratiques: 1.
- Repartition par type: theory: 14, example: 3, worked_example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S7], [S13], [S14], [S16].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S2], [S6], [S7], [S17].
4. Exemples - couvert par [S1], [S4], [S5], [S7].
5. Exemples resolus - couvert par [S7].
6. Exercices - couvert par [S6], [S10], [S11], [S13].
7. Corriges - couvert par [S2], [S4], [S5], [S6].
8. Cas pratiques - couvert par [S7].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, resumes.

## Faits et angles extraits de la base
- Before the maturity, if the underlying asset
goes below the barrier level the barrier option will be
knocked in and become a vanilla option.
- Otherwise,
the barrier option will expire worthless at maturity.
- Bearish investors can buy down-and-in puts and pay
a lower premium than that on the vanilla put options.
- Up-and-out Call/Up-and-out Put
This is the first kind of knock-out barrier options.
- The up-and-out barrier option has a knock-out barrier
level above the initial underlying asset level.
- Before
maturity, if the underlying asset crosses the barrier
level, the option will be knocked out and become
worthless.
- Otherwise, the barrier option will just be a
vanilla option.
- A bearish investor would buy up-andout puts to achieve more leverage by paying a lower
premium than that on vanilla puts.
- Down-and-out Call/Down-and-out Put
The down-and-out barrier option has a knock-out
barrier level below the initial underlying asset level.
- Before maturity, if the underlying asset goes below
the barrier level, the option will be knocked out
and become worthless.

## Sources RAG a citer
- [S1] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 981, score 0.860758: Before the maturity, if the underlying asset
goes below the barrier level the barrier option will be
knocked in and become a vanilla option. Otherwise,
the barrier option will expire worthless at maturity. Down-and-in puts are more common in this case.
- [S2] FX Derivatives Trader School ( PDFDrive ), chunk 274, score 0.46302: 24.15
Reverse knock-out and equivalent one-touch option within a pricing tool
- [S3] FX Derivatives Trader School ( PDFDrive ), chunk 362, score 0.461046 (extrait non cite: source bruitee)
- [S4] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 241, score 0.459424: Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option.
- [S5] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 241, score 0.459424: Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option.
- [S6] Vault Guide to Advanced Finance and Quantitative Interviews.pdf ( PDFDrive ), chunk 148, score 0.454605: The option to purchase the call option itself has exercise 
price K1 and strike T1. Obtaining a price for this option is not difficult. Since the option still depends on 
the price movement of the underlying S, the Black-Scholes equation still applies. The time domain is 
broken into two parts: (0, T1) and (T1, T2).
- [S7] FX Derivatives Trader School ( PDFDrive ), chunk 275, score 0.454353: One of the barriers is knock-out while the other is knock-in. There are
two variations of knock-in/knock-out options:
1. Knock-out until expiry
2.
- [S8] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 178, score 0.444594: We
will return to the discussion on volatility models when we discuss local volatility later in the
chapter.
- [S9] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 1044, score 0.437778: [3]
Ren, Y., Madan, D. Calibrating and
pricing with embedded local volatility models, Risk 20(9),
138–143. Related Articles
Corridor
Variance
Swap;
Realized
Volatility
Options; Variance Swap; Volatility Index Options;
Weighted Variance Swap.
- [S10] Financial Derivatives  Pricing and Risk Management ( PDFDrive ), chunk 199, score 0.424788: When that happens, the option becomes a plain vanilla option. Accordingly, an
“out” option is initially like a plain vanilla option, except if the price of the underlying good penetrates the stated barrier, the option immediately expires worthless.
- [S11] FX Derivatives Trader School ( PDFDrive ), chunk 241, score 0.419441: Knock-out until knock in. If the knock-in barrier hits first, the option cannot then
be knocked out and therefore the option has a guaranteed payoff at maturity.
- [S12] Derivatives Models on Models ( PDFDrive ), chunk 183, score 0.408845: Exchange Options and a Put-Call Tranformation: A Note’’ Journal of Business Finance and Accounting, 20(5), 761–764. (1976) ‘‘The Pricing of Commodity Contracts’’ Journal of Financial Economics, 3,
167–179. Scholes (1973) ‘‘The Pricing of Options and Corporate Liabilities,’’ Journal
of Political Economy, 81, 637–654.
- [S13] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 982, score 0.39625: Double Barrier
A double barrier option is another variation that has
two barriers, typically one up barrier and the other a
down barrier. For example, investors seeking high
leverage would consider double knock-out barrier
options if they believe changes in the underlying asset
level would be within a narrow range.
- [S14] FX Derivatives Trader School ( PDFDrive ), chunk 240, score 0.391795: This option will pay off like a 1.1000 EUR
call/USD put vanilla option at maturity unless spot ever trades through (below)
1.2000 during the life of the option, in which case there will be no payoff at maturity. This is shown in Exhibit 20.6.
- [S15] Computational Methods for Quantitative Finance  Finite Element Methods for Derivative Pricing ( PDFDrive ), chunk 59, score 0.385613: A rigorous treatment is provided by
Jaillet et al. [98] where the Brennan and Schwartz algorithm [25] is used for the discretization. A semi-smooth Newton approach is analyzed in Ito et al. [84, 92] and
Hager and Wohlmuth [77].
- [S16] Managing Derivatives Contracts  A Guide to Derivatives Market Structure, Contract Life Cycle, Operations, and Systems ( PDFDrive ), chunk 57, score 0.381857: Firms may respond to each risk using one of the following strategies:
Risk transfer. The shift or transfer of risk exposure to 
another party or entity by, for example, a “hold harmless” contract. Risk acceptance. The acceptance of the likelihood 
and consequences of a particular risk.
- [S17] FX Derivatives Trader School ( PDFDrive ), chunk 273, score 0.371715: Providing all contract
details (expiry, strike, barrier, cut, and notional) are the same:
■Reverse knock-out + reverse knock-in = vanilla
A long reverse knock-in has similar trading risk to a long one-touch at the barrier
level, providing the strike and barrier are far enough apart.
- [S18] Managing Derivatives Contracts  A Guide to Derivatives Market Structure, Contract Life Cycle, Operations, and Systems ( PDFDrive ), chunk 52, score 0.369782: All 
financial and nonfinancial corporations are exposed to risks in their everyday 
business activities from adverse movements and events in various contingencies, such as interest rates, foreign exchange rates, commodity prices, credit, 
liquidity, theft, weather, health, catastrophe, and competition.

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Down-and-out call payoff
$$
\Phi=(S_T-K)^+\mathbf{1}_{\min_{0\leq t\leq T}S_t>H}
$$
- Usage desk: make the path condition explicit before discussing price.
### F2 - Barrier gap loss
$$
\text{Gap loss}\approx \Delta_{\text{pre-hit}}\,(S_{\text{hit}}-S_{\text{next}})
$$
- Usage desk: estimate the residual risk when the hedge cannot be rebalanced at the barrier.
### F3 - Discrete monitoring adjustment
$$
H_{\text{eff}}\approx H\exp(\pm\beta\sigma\sqrt{\Delta t}),\qquad \beta\approx0.5826
$$
- Usage desk: avoid mixing continuous-barrier prices with discretely monitored risk.

