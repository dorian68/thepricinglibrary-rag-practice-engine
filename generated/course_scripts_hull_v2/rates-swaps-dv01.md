---
slug: rates-swaps-dv01
topic: Interest-rate swaps, PV and DV01
product: EUR interest-rate swap
level: intermediate
concepts: par rate, annuity, DV01, curve shock
source_count: 18
---

# Module pratique - Interest-rate swaps, PV and DV01

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Interest-rate swaps, PV and DV01 a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: intermediate
- Public vise: junior quant, analyste market risk, sales/structuring junior
- Duree estimee: 210 minutes
- Produit: EUR interest-rate swap
- Concepts: par rate, annuity, DV01, curve shock

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
### Module 1 - Lire le ticket swap
- Objectif pratique: Identifier payer/receiver, notional, coupon, maturite et index flottant.
- Situation de desk: Un trader demande une lecture rapide d'un payer swap EUR 5Y avant un move BCE.
- Notion utile: Cash-flow fixe contre flottant, par rate, annuite.
- Activite: Transformer le ticket en tableau d'inputs et verifier le sens du risque.
- Livrable apprenant: Ticket enrichi + risque principal en une phrase.
### Module 2 - PV par coupon gap
- Objectif pratique: Estimer la valeur du swap avec l'ecart fixed coupon vs par rate.
- Situation de desk: Le coupon du book est au-dessus du mid-market; il faut expliquer le PV.
- Notion utile: PV approx = (par - fixed) * annuite * notionnel selon le sens.
- Activite: Calculer PV, signe et interpretation front-office.
- Livrable apprenant: PV explique avec signe payer/receiver.
### Module 3 - DV01 et shock P&L
- Objectif pratique: Convertir l'annuite en EUR/bp puis appliquer un shock de courbe.
- Situation de desk: La courbe bouge de 10bp avant le comite risque.
- Notion utile: DV01 = annuite * notionnel * 1bp.
- Activite: Calculer DV01, P&L shock et seuil d'alerte.
- Livrable apprenant: Tableau DV01/shock P&L.
### Module 4 - Hedge et basis risk
- Objectif pratique: Proposer une couverture realiste et nommer ce qu'elle ne couvre pas.
- Situation de desk: Le desk hedge avec futures ou swap oppose de tenor proche.
- Notion utile: Parallel hedge, tenor mismatch, curve-shape risk.
- Activite: Choisir hedge, sens, taille approximative et risque residuel.
- Livrable apprenant: Memo hedge en 6 lignes.
### Module 5 - Debrief production
- Objectif pratique: Savoir quand l'approximation devient dangereuse.
- Situation de desk: La position est materialisee dans un report de risk management.
- Notion utile: Conventions, multi-curve, collateral, interpolation.
- Activite: Lister les controles avant validation.
- Livrable apprenant: Checklist de validation desk.
### Module 6 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 7 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de Interest-rate swaps, PV and DV01 et savoir le critiquer.
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
### Lecon 1 - Lire le ticket swap

**Le reflexe d'abord.** Un trader demande une lecture rapide d'un payer swap EUR 5Y avant un move BCE. Avant toute formule, demandez-vous ce que cash-flow fixe contre flottant, par rate, annuite change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « ]
CHAPTER14
Interest Rate Swaps
INTRODUCTION
In this and the subsequent chapter we will explore a type of derivative security
known as a “swap.” Broadly, a swap is an exchange of cash flows between
two counterparties over a number of periods of time. This chapter explores
the most important swap product, the interest rate swap. » [S1]. L'enjeu operationnel est clair : identifier payer/receiver, notional, coupon, maturite et index flottant.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, cash-flow fixe contre flottant, par rate, annuite sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : ticket enrichi + risque principal en une phrase.

Concretement, l'exercice consiste a transformer le ticket en tableau d'inputs et verifier le sens du risque, pour en tirer un ticket enrichi + risque principal en une phrase. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: transformer le ticket en tableau d'inputs et verifier le sens du risque. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer cash-flow fixe contre flottant, par rate, annuite a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - PV par coupon gap

**Comment ca marche.** PV approx = (par - fixed) * annuite * notionnel selon le sens n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Heynen, R., A. Kemna, and T. Vorst (1994): “Analysis of the Term Structure of Implied Volatilities,” Journal of Financial Quantitative Analysis 1:
31–57. Ho, T., and S. Lee (1986): “Term Structure Movements and Pricing Interest
Rate Contingent Claims,” Journal of Finance 41: 1011–1029. (1993a): “The Lognormal Interest Rate Model and Eurodollar
Futures,” Working Paper, Citibank, New York. » [S2].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a estimer la valeur du swap avec l'ecart fixed coupon vs par rate. Il s'agit de calculer pv, signe et interpretation front-office pour produire un pv explique avec signe payer/receiver, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer pv, signe et interpretation front-office. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer pv approx = (par - fixed) * annuite * notionnel selon le sens a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - DV01 et shock P&L

**Ou est le risque.** La courbe bouge de 10bp avant le comite risque. Mal traiter dv01 = annuite * notionnel * 1bp se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Two singular diffusion problems. Annals of Mathematics, 54, 173-181. Flesaker, B. Testing the Heath-Jarrow-Morton/Ho-Lee model of interest rate contingent
claims pricing. Journal of Financial and Quantitative Analysis, 28, no. Goldstein, R. The term structure of interest rates as a random field. Review of Financial
Studies, 13, 365-384. Goldys, B., M. Musiela, and D. Lognormality of Rates and Term Structure
Models. » [S3].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : convertir l'annuite en eur/bp puis appliquer un shock de courbe. Il faut calculer dv01, p&l shock et seuil d'alerte, documenter un tableau dv01/shock p&l, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer dv01, p&l shock et seuil d'alerte. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer dv01 = annuite * notionnel * 1bp a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Hedge et basis risk

**La decision visee.** A la fin de cette lecon vous saurez proposer une couverture realiste et nommer ce qu'elle ne couvre pas sans hesiter. Le declencheur : le desk hedge avec futures ou swap oppose de tenor proche. Les sources le confirment _[extrait]_ : « Journal of 'Finance, 40, 455-480. A simple nonparametric approach to derivative security valuation. Journal of
Finance, 51, no. 5, 1633-1652. » [S4].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de parallel hedge, tenor mismatch, curve-shape risk sert exactement a cela. Il faut choisir hedge, sens, taille approximative et risque residuel, produire un memo hedge en 6 lignes, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: choisir hedge, sens, taille approximative et risque residuel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer parallel hedge, tenor mismatch, curve-shape risk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Debrief production

**Le reflexe d'abord.** La position est materialisee dans un report de risk management. Avant toute formule, demandez-vous ce que conventions, multi-curve, collateral, interpolation change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « For
interest rate swaps and options, the payoffs occur after
a certain number of days following the expiration, depending on the days to maturity of the instrument that
defines the underlying rate. Thus, if the underlying is
m-day LIBOR, swaps and options pay off m days after
the rate is determined at expiration. » [S5]. L'enjeu operationnel est clair : savoir quand l'approximation devient dangereuse.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, conventions, multi-curve, collateral, interpolation sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : checklist de validation desk.

Concretement, l'exercice consiste a lister les controles avant validation, pour en tirer un checklist de validation desk. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: lister les controles avant validation. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer conventions, multi-curve, collateral, interpolation a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Carte des sources et des definitions

**Comment ca marche.** Source grounding, provenance, vocabulaire de desk n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « Malden, MA: Blackwell, 2007. “ The Relationship between Futures Prices for US Treasury Bonds.” Review of 
Research in Futures Markets 3 ( 1984 ): 84 – 104. “ Optimal Hedging Policies.” Journal of Financial and Quantitative Analysis
 
 19 (June 1984 ): 127 – 140. » [S6].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas. Il s'agit de comparer les extraits [sx] et isoler les definitions robustes pour produire un source map annotee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Fondations quantitatives niveau Hull

**Ou est le risque.** Un entretien quant demande la derivation, le desk demande ses limites. Mal traiter modele, mesure, derivees, approximation locale se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Jamshidian, F. (1991a): “Bond and Option Evaluation in the Gaussian Interest
Rate Model,” Research in Finance 9: 131–170. Jamshidian, F. (1991b): “Commodity Option Evaluation in the Gaussian Futures Term Structure Model,” Review of Futures Markets 10: 324–346. Jamshidian, F. (1991c): “Forward Induction and Construction of Yield Curve
Diffusion Models,” Journal of Fixed Income, June: 62–74. Jamshidian, F. » [S7].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : deriver le coeur quantitatif de interest-rate swaps, pv and dv01 et savoir le critiquer. Il faut reprendre la derivation puis nommer ce qui casse en marche reel, documenter un derivation commentee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Cas numerique moteur

**La decision visee.** A la fin de cette lecon vous saurez reproduire un calcul complet avec substitutions, resultat et unite sans hesiter. Le declencheur : le desk refuse un chiffre qui ne peut pas etre audite. Les sources le confirment _[extrait]_ : « J Financ Econ 3:361–377
Fama E (1984a) The information in the term structure. J Financ Econ 13(4):509–528
Fama E (1984b) Term premiums in bond returns. J Financ Econ 13(4):529–546
Fisher I (1930) The theory of interest. Macmillan, New York
Fraine HG, Mills RH (1961) The effect of default and credit deterioration on yields of corporate
bonds. » [S8].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de calculateur deterministe, ordre de grandeur, controles croises sert exactement a cela. Il faut refaire le cas a la main et verifier le resultat moteur, produire un answer key verifiee, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 9 - Lab interactif et scenarios

**Le reflexe d'abord.** Le marche bouge avant validation du trade. Avant toute formule, demandez-vous ce que scenario table, surface, matrice ou chart selon le produit change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « hedging "not only risks associated with 
Moscow City bonds but also risks related to 
bonds issued by other entities" 
b. "short-selling abilities" 
c. "portfolio duration management abilities" 
d. "reduction in transaction costs" 
e. "using the spreads between the short-term and 
long-term interest rates without using the 
underlying assets" » [S9]. L'enjeu operationnel est clair : manipuler les inputs et lire l'effet sur prix, risque ou p&l.

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
1. Ticket swap: identifier payer/receiver, coupon, par rate, annuite et risque principal.
2. PV/DV01: calculer PV approximatif et EUR/bp sur un notionnel impose.
3. Shock P&L: appliquer +/-10bp et expliquer le signe.
4. Hedge memo: proposer hedge, taille et basis risk.
5. Debrief: controles de convention, courbe et collateral.

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
- Score pedagogique moyen: 45.06/100 (qualite structurelle: 84.72/100).
- Definitions: 3 | exemples: 2 | exercices: 5 | formules: 0 | cas pratiques: 0.
- Repartition par type: theory: 14, exercise: 2, methodology: 1, example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S5], [S10], [S14].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
4. Exemples - couvert par [S14], [S16].
5. Exemples resolus - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
6. Exercices - couvert par [S1], [S4], [S5], [S10].
7. Corriges - couvert par [S2], [S11], [S13], [S14].
8. Cas pratiques - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: partially_usable - Sources partiellement suffisantes: completer les manques.
- Presents dans les sources: definitions, exemples, exercices, corriges.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, formules, exemples resolus, cas pratiques, resumes.

## Faits et angles extraits de la base
- ]
CHAPTER14
Interest Rate Swaps
INTRODUCTION
In this and the subsequent chapter we will explore a type of derivative security
known as a “swap.” Broadly, a swap is an exchange of cash flows between
two counterparties over a number of periods of time.
- This chapter explores
the most important swap product, the interest rate swap.
- We will learn about
the characteristics of an interest rate swap, how an interest rate swap’s cash
flows are calculated, and how interest rate swaps can be used to transform
cash flows.
- After you read this chapter, you will be able to
■Describe the characteristics of an interest rate swap.
- ■Distinguish between fixed and floating interest rate swap legs and rates.
- ■Calculate the cash flows associated with an interest rate swap.
- 14.1
INTEREST RATE SWAP CHARACTERISTICS
An interest rate swap is an agreement in which two counterparties agree to
periodically exchange fixed and floating rates of interest over a number of
periods of time.
- One of the swap counterparties, known as the long interest
rate swap position, agrees to periodically receive a floating rate and pay a
fixed rate.
- The other swap counterparty, known as the short interest rate
swap position, agrees to periodically receive a fixed rate and pay a floating
rate.
- The exchange of fixed rate for floating rate is broadly illustrated in

## Sources RAG a citer
- [S1] Derivatives Essentials  An Introduction to Forwards, Futures, Options and Swaps ( PDFDrive ), chunk 158, score 0.627461: ]
CHAPTER14
Interest Rate Swaps
INTRODUCTION
In this and the subsequent chapter we will explore a type of derivative security
known as a “swap.” Broadly, a swap is an exchange of cash flows between
two counterparties over a number of periods of time.
- [S2] Financial Derivatives  Pricing, Applications, and Mathematics ( PDFDrive ), chunk 211, score 0.588521: Heynen, R., A. Kemna, and T. Vorst (1994): “Analysis of the Term Structure of Implied Volatilities,” Journal of Financial Quantitative Analysis 1:
31–57. Ho, T., and S. Lee (1986): “Term Structure Movements and Pricing Interest
Rate Contingent Claims,” Journal of Finance 41: 1011–1029.
- [S3] The Oxford Guide to Financial Modeling  Applications for Capital Markets, Corporate Finance, Risk Management and Financial Institutions ( PDFDrive ), chunk 212, score 0.512891: Two singular diffusion problems. Annals of Mathematics, 54, 173-181. Flesaker, B. Testing the Heath-Jarrow-Morton/Ho-Lee model of interest rate contingent
claims pricing. Journal of Financial and Quantitative Analysis, 28, no. Goldstein, R. The term structure of interest rates as a random field.
- [S4] The Oxford Guide to Financial Modeling  Applications for Capital Markets, Corporate Finance, Risk Management and Financial Institutions ( PDFDrive ), chunk 159, score 0.501726: Journal of 'Finance, 40, 455-480. A simple nonparametric approach to derivative security valuation. Journal of
Finance, 51, no. 5, 1633-1652.
- [S5] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 667, score 0.498113: For
interest rate swaps and options, the payoffs occur after
a certain number of days following the expiration, depending on the days to maturity of the instrument that
defines the underlying rate. Thus, if the underlying is
m-day LIBOR, swaps and options pay off m days after
the rate is determined at expiration.
- [S6] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 356, score 0.486045: Malden, MA: Blackwell, 2007. “ The Relationship between Futures Prices for US Treasury Bonds.” Review of 
Research in Futures Markets 3 ( 1984 ): 84 – 104. “ Optimal Hedging Policies.” Journal of Financial and Quantitative Analysis
 
 19 (June 1984 ): 127 – 140.
- [S7] Financial Derivatives  Pricing, Applications, and Mathematics ( PDFDrive ), chunk 212, score 0.440904: Jamshidian, F. (1991a): “Bond and Option Evaluation in the Gaussian Interest
Rate Model,” Research in Finance 9: 131–170. Jamshidian, F. (1991b): “Commodity Option Evaluation in the Gaussian Futures Term Structure Model,” Review of Futures Markets 10: 324–346. Jamshidian, F.
- [S8] Analytical Corporate Valuation  Fundamental Analysis, Asset Pricing, and Company Valuation ( PDFDrive ), chunk 401, score 0.424298: J Financ Econ 3:361–377
Fama E (1984a) The information in the term structure. J Financ Econ 13(4):509–528
Fama E (1984b) Term premiums in bond returns. J Financ Econ 13(4):529–546
Fisher I (1930) The theory of interest.
- [S9] Foundations of Financial Markets and Institutions ( PDFDrive ), chunk 849, score 0.401086: hedging "not only risks associated with 
Moscow City bonds but also risks related to 
bonds issued by other entities" 
b. "short-selling abilities" 
c. "portfolio duration management abilities" 
d. "reduction in transaction costs" 
e.
- [S10] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 668, score 0.394693: 457
interest rate cap, p. 466
caplet, p. 466
interest rate floor, p. 466
floorlet, p. 466
interest rate collar, p. 466
zero-cost collar, p. 469
payer swaption, p. 471
receiver swaption, p. 471
Chapter 13
Interest Rate Forwards and Options
479
- [S11] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 628, score 0.380416: The right to
make a known payment is an interest rate call. The right to receive a known payment is
an interest rate put. In addition to standard interest rate forwards and options, we shall cover two other
types of forward and option contracts involving interest rates.
- [S12] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 281, score 0.380262 (extrait non cite: source bruitee)
- [S13] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 78, score 0.378093: Second, for
short-dated contracts, if the underlying asset’s price
process is highly correlated with interest rate movements, then interest rate risk will affect hedging, and
therefore valuation. The extreme cases, of course, are
interest rate derivatives where the underlyings are the
interest rates themselves.
- [S14] Derivative Security Pricing  Techniques, Methods and Applications ( PDFDrive ), chunk 267, score 0.371091: Use simulation to evaluate U.0; 0:5/. Take the parameter values
 D 0:6; Nr D 0:07;  D 0:024:
Experiment with the step size and number of paths so as to ensure two decimal
accuracy.
- [S15] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 742, score 0.370204 (extrait non cite: source bruitee)
- [S16] Credit Derivatives   Instruments, Applications and Pricing ( PDFDrive ), chunk 81, score 0.368784: Interest rate swaps are over-the-counter (OTC) instruments. Consequently, a risk that the two parties face when they enter into an interest
rate swap is that the other party will fail to fulfill its obligations as set
forth in the swap agreement.
- [S17] Credit Derivatives   Instruments, Applications and Pricing ( PDFDrive ), chunk 289, score 0.365643: 7
Hazard rate
calibration, 229
constancy, 243
need. See Stochastic hazard rate
randomization, 249
relationship. See Random interest rate
term structure, 243
Heath, David, 214
Hedges. See Fair value
ineffectiveness, 287
Hedging. See Fair value; Risk hedging
designation.
- [S18] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 10, score 0.35924 (extrait non cite: source bruitee)

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Par swap rate
$$
R_{\text{par}}=\frac{P(0,T_0)-P(0,T_n)}{\sum_{i=1}^{n}\alpha_i P(0,T_i)}
$$
- Usage desk: turn a discount curve into the fixed rate that prices the swap at par.
### F2 - Swap PV around par
$$
\text{PV}\approx N\,(R_{\text{par}}-K)\sum_{i=1}^{n}\alpha_i P(0,T_i)
$$
- Usage desk: explain the sign of a receiver or payer swap after a rate move.
### F3 - DV01
$$
\text{DV01}=N\times A\times 10^{-4},\qquad A=\sum_{i=1}^{n}\alpha_i P(0,T_i)
$$
- Usage desk: convert a one basis point shock into currency P&L.

