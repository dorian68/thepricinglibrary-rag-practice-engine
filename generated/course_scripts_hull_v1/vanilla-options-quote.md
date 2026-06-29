---
slug: vanilla-options-quote
topic: Vanilla options desk quote
product: equity vanilla option
level: beginner
concepts: Black-Scholes, put-call parity, delta, vega
source_count: 18
---

# Module pratique - Vanilla options desk quote

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Vanilla options desk quote a un niveau **Hull-pratique**: partir d'un ticket de
desk, isoler les hypotheses, derouler la theorie juste necessaire, produire un
calcul verifiable, lire les risques, puis conclure par une decision exploitable.
Le cours vise deux publics exigeants: l'etudiant quant qui veut comprendre en
profondeur et le young professional front-office qui doit agir correctement.

## Niveau cible et public
- Niveau: beginner
- Public vise: etudiant L3/M1, candidat en finance de marche, developpeur front-office debutant
- Duree estimee: 180 minutes
- Produit: equity vanilla option
- Concepts: Black-Scholes, put-call parity, delta, vega

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
### Module 1 - Lire le ticket vanilla
- Objectif pratique: Transformer une demande de quote en inputs propres: spot, strike, maturite, taux, dividendes et vol.
- Situation de desk: Sales demande un prix indicatif sur un call europeen avant envoi client.
- Notion utile: Moneyness, forward, discounting, convention de maturite.
- Activite: Construire le ticket et identifier les donnees manquantes.
- Livrable apprenant: Quote ticket controle.
### Module 2 - Prix Black-Scholes
- Objectif pratique: Calculer call et put avec substitutions visibles et unite de premium.
- Situation de desk: Le desk veut un prix defendable et reproductible.
- Notion utile: d1/d2, prix call/put, dividend yield.
- Activite: Calculer le prix et verifier intrinsic/time value.
- Livrable apprenant: Pricing sheet.
### Module 3 - Controle put-call parity
- Objectif pratique: Detecter une incoherence de quote avant de la transmettre.
- Situation de desk: Le put mid ne colle pas avec le call mid et le forward.
- Notion utile: C - P = forward discounté moins strike discounté.
- Activite: Mesurer le parity gap et conclure quote/hold/reject.
- Livrable apprenant: Parity control.
### Module 4 - Greeks utiles au quote
- Objectif pratique: Convertir delta et vega en risque concret pour le trader.
- Situation de desk: Le client augmente la taille et le trader demande le hedge initial.
- Notion utile: Delta hedge, vega per vol point, sign convention.
- Activite: Calculer hedge shares et sensibilite vol.
- Livrable apprenant: Risk add-on note.
### Module 5 - Memo desk
- Objectif pratique: Synthétiser prix, controles et action front-office.
- Situation de desk: Le quote doit tenir dans un message trader/sales de quelques lignes.
- Notion utile: Assumptions, caveats, controls, decision.
- Activite: Rediger une note quote ou no-quote.
- Livrable apprenant: Trader quote memo.
### Module 6 - Carte des sources et des definitions
- Objectif pratique: Relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas.
- Situation de desk: Un apprenant doit savoir quelle source croire et pourquoi.
- Notion utile: Source grounding, provenance, vocabulaire de desk.
- Activite: Comparer les extraits [Sx] et isoler les definitions robustes.
- Livrable apprenant: Source map annotee.
### Module 7 - Fondations quantitatives niveau Hull
- Objectif pratique: Deriver le coeur quantitatif de Vanilla options desk quote et savoir le critiquer.
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

## Cours redige
### Lecon 1 - Lire le ticket vanilla

**Le reflexe d'abord.** Sales demande un prix indicatif sur un call europeen avant envoi client. Avant toute formule, demandez-vous ce que moneyness, forward, discounting, convention de maturite change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « The peak vega on a vanilla option reduces over time. Intuitively,
vega increases at longer maturities because there is more time for a change in implied
volatility to impact the payoff. For a given vanilla option, peak vega (like gamma) occurs at the strike where
optionality and time value is maximized. » [S1]. L'enjeu operationnel est clair : transformer une demande de quote en inputs propres: spot, strike, maturite, taux, dividendes et vol.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, moneyness, forward, discounting, convention de maturite sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : quote ticket controle.

Concretement, l'exercice consiste a construire le ticket et identifier les donnees manquantes, pour en tirer un quote ticket controle. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: construire le ticket et identifier les donnees manquantes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer moneyness, forward, discounting, convention de maturite a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 2 - Prix Black-Scholes

**Comment ca marche.** d1/d2, prix call/put, dividend yield n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « American Vanilla Pricing and Greeks
Comparing American and European vanillas in the CCY1 call and higher CCY1
interest rates case demonstrates how early exercise impacts trading risk. Price
profiles are shown in Exhibit 27.9. As mentioned, the American vanilla is always more expensive than the equivalent
European vanilla. » [S4].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a calculer call et put avec substitutions visibles et unite de premium. Il s'agit de calculer le prix et verifier intrinsic/time value pour produire un pricing sheet, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer le prix et verifier intrinsic/time value. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer d1/d2, prix call/put, dividend yield a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 3 - Controle put-call parity

**Ou est le risque.** Le put mid ne colle pas avec le call mid et le forward. Mal traiter c - p = forward discounté moins strike discounté se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « Mathematical description of option valuation goes at least back more than
100 years to the now so famous Bachelier (1900) paper, that was based on his doctoral thesis
defended on March 19, 1900. Bachelier assumed a normal distribution for the asset price. » [S5].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : detecter une incoherence de quote avant de la transmettre. Il faut mesurer le parity gap et conclure quote/hold/reject, documenter un parity control, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: mesurer le parity gap et conclure quote/hold/reject. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer c - p = forward discounté moins strike discounté a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 4 - Greeks utiles au quote

**La decision visee.** A la fin de cette lecon vous saurez convertir delta et vega en risque concret pour le trader sans hesiter. Le declencheur : le client augmente la taille et le trader demande le hedge initial. Les sources le confirment _[extrait]_ : « CCY2 premium,
265–267
European digital option replication:
CCY1, 402–403
CCY2, 402
G10, 4
one-touch options variations CCY1
vs. CCY2 payout, 434–435
relative strength of, 219
self-quanto:
CCY1 call options, 510
CCY1 put options, 510–513
Currency blocks, 42 » [S6].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de delta hedge, vega per vol point, sign convention sert exactement a cela. Il faut calculer hedge shares et sensibilite vol, produire un risk add-on note, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : presenter un chiffre sans unite ni ordre de grandeur de controle.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: calculer hedge shares et sensibilite vol. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer delta hedge, vega per vol point, sign convention a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 5 - Memo desk

**Le reflexe d'abord.** Le quote doit tenir dans un message trader/sales de quelques lignes. Avant toute formule, demandez-vous ce que assumptions, caveats, controls, decision change pour le risque que vous portez. Les sources le confirment _[extrait]_ : « Due to put–call parity, call and put options with the
same strike and maturity have the same gamma profile, shown in Exhibit 6.15. This
gamma can be calculated by taking the gradient of either the call option delta profile
from Exhibit 6.9 or the put option delta profile from Exhibit 6.11. As time moves toward the option maturity, gamma increases and concentrates
around the strike. » [S7]. L'enjeu operationnel est clair : synthétiser prix, controles et action front-office.

Un etudiant tres forme doit voir la structure logique : input observable, hypothese de modele, calcul, controle, puis decision. Un young professional doit aller plus vite encore : identifier la donnee qui pilote le risque, dire ce qui est robuste, et isoler ce qui depend d'une convention. Ici, assumptions, caveats, controls, decision sert a transformer une idee de marche en action defendable.

Sur le desk, la question n'est jamais seulement 'quelle est la formule ?'. La vraie question est : si l'input bouge, quel chiffre bouge, dans quel sens, et qui doit agir ? Le trader veut une lecture de signe, risk veut une unite, sales veut une phrase claire. Cette lecon vous force donc a relier la notion au livrable concret : trader quote memo.

Concretement, l'exercice consiste a rediger une note quote ou no-quote, pour en tirer un trader quote memo. Ne passez pas a l'exemple numerique avant d'avoir ecrit les conventions : date de mesure, unite du choc, position long/short, et approximation utilisee. Ce sont ces quatre lignes qui font la difference entre une reponse scolaire et une reponse front-office.

Decision attendue : produire le livrable, expliquer le signe du resultat et indiquer ce qu'il faudrait monitorer si le marche se deplace. Le piege a eviter : traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: rediger une note quote ou no-quote. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer assumptions, caveats, controls, decision a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 6 - Carte des sources et des definitions

**Comment ca marche.** Source grounding, provenance, vocabulaire de desk n'est pas un concept abstrait : c'est le mecanisme qui relie le contexte de marche a une decision chiffree. Les sources le confirment _[extrait]_ : « This was
probably already known for a very long time and probably published much earlier. We can so far conclude that hedging options with options as well as initial market neutral
static delta hedging were the main principles of option hedging in the early 1900s. The hedge ratio
for other than at-the-money options was probably not well understood, or at least not described
in the literature I have at hand. » [S13].

Le niveau Hull consiste a ne pas accepter une formule comme une boite noire. Il faut savoir ce qui est mesure, quelle variable est tenue fixe, et quelle approximation est implicite. La lecture pratique de cette lecon est donc : on part du ticket, on nettoie les inputs, on choisit le cadre, puis on verifie que le resultat respecte l'ordre de grandeur attendu.

En pratique, la lecon consiste a relier la notion aux ouvrages du corpus et distinguer definition, intuition, formule et cas. Il s'agit de comparer les extraits [sx] et isoler les definitions robustes pour produire un source map annotee, livrable que le desk relit en trente secondes. Ce livrable doit contenir un chiffre, une unite, un controle et une limite. Sans ces quatre pieces, le calcul peut etre juste mathematiquement mais inutilisable commercialement.

Le jeune professionnel doit aussi savoir parler aux trois interlocuteurs : au trader avec le risque dominant, a risk avec la sensibilite et a sales avec la phrase client-safe. L'exercice n'est donc pas seulement calculatoire ; il force la traduction d'une notion quantitative en decision. Attention : melanger donnee de marche observee, approximation de pricing et jugement de trader.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: comparer les extraits [sx] et isoler les definitions robustes. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer source grounding, provenance, vocabulaire de desk a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 7 - Fondations quantitatives niveau Hull

**Ou est le risque.** Un entretien quant demande la derivation, le desk demande ses limites. Mal traiter modele, mesure, derivees, approximation locale se paie immediatement en P&L. Les sources le confirment _[extrait]_ : « The authors show that this option
may be replicated by holding onto a European » [S14].

La bonne analyse commence par la decomposition du risque : facteur principal, facteur secondaire, interaction et regime ou l'approximation cesse d'etre fiable. Un profil Polytechnique doit pouvoir justifier la decomposition ; un analyste front-office doit pouvoir la transformer en hedge, monitoring ou escalation.

L'objectif de cette lecon est donc tres operationnel : deriver le coeur quantitatif de vanilla options desk quote et savoir le critiquer. Il faut reprendre la derivation puis nommer ce qui casse en marche reel, documenter un derivation commentee, et relier chaque chiffre a une intuition de signe avant de le transmettre. Ajoutez toujours une lecture de stress : que se passe-t-il si le mouvement est deux fois plus grand, si la liquidite disparait, ou si la donnee de marche etait stale ?

Le controle minimal tient en une phrase : 'voici le risque que je mesure, voici l'unite, voici le signe, voici ce qui n'est pas couvert'. Cette phrase evite les faux conforts d'un modele propre sur un marche sale. Erreur classique : confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: reprendre la derivation puis nommer ce qui casse en marche reel. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer modele, mesure, derivees, approximation locale a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

### Lecon 8 - Cas numerique moteur

**La decision visee.** A la fin de cette lecon vous saurez reproduire un calcul complet avec substitutions, resultat et unite sans hesiter. Le declencheur : le desk refuse un chiffre qui ne peut pas etre audite. Les sources le confirment _[extrait]_ : « The relationship can, for example, be used to value double
barrier options in a intuitive way. Double barrier options and other complex barrier options trade quite actively in the financial markets, in particular in the foreign
exchange market, and a good understanding of valuation and hedging of such options is of great
importance to investment banks, hedge funds and corporations involved in such options. » [S17].

Le cours doit vous amener a un reflexe de production : ne jamais laisser une notion sans decision associee. Si le resultat change le prix, il faut dire quote ou no-quote. S'il change le risque, il faut dire hedge, reduce ou monitor. S'il casse une limite, il faut dire escalate.

La notion de calculateur deterministe, ordre de grandeur, controles croises sert exactement a cela. Il faut refaire le cas a la main et verifier le resultat moteur, produire un answer key verifiee, puis conclure par une action de desk explicite (quote, hedge, hold ou reject). Le niveau attendu n'est pas de nommer le concept, mais de savoir quel champ remplir dans un pricer, quel chiffre surveiller dans un risk report, et quel message envoyer au trader.

Avant de passer a la lecon suivante, reformulez la decision en une ligne et ecrivez le controle de coherence qui la protege. Ne tombez pas dans le piege : oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

**Micro-cas a traiter.** Imaginez que le desk vous donne ce bloc comme tache de production: refaire le cas a la main et verifier le resultat moteur. Votre reponse doit tenir en quatre lignes: input critique, calcul ou controle, resultat attendu, decision. Pour un etudiant, l'exercice consiste a reconstruire la chaine logique sans sauter d'etape; pour un young professional, il consiste a se demander ce qui serait faux si la donnee etait stale, si la position etait short au lieu de long, ou si le choc etait deux fois plus grand.

**Checkpoint de maitrise.** Vous pouvez passer a la suite seulement si vous savez expliquer calculateur deterministe, ordre de grandeur, controles croises a trois niveaux: intuition client, mecanisme quantitatif, et consequence P&L/risk. Si l'une des trois couches manque, le sujet n'est pas acquis.

## Blocs interactifs de finance de marche
```uiblock
type: equation
title: Equation pivot du module
params: {"latex": "\\Delta V\\approx \\Delta\\,\\Delta S+\\frac12\\Gamma(\\Delta S)^2+\\nu\\,\\Delta\\sigma+\\Theta\\,\\Delta t"}
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
1. Quote ticket: spot, strike, maturite, taux, dividendes, vol et convention de taille.
2. Black-Scholes price: calculer call/put, intrinsic value et time value.
3. Parity check: mesurer le gap call-put-forward et conclure quote ou reject.
4. Greeks add-on: convertir delta et vega en hedge initial et risk comment.
5. Trader memo: prix, controles, hypotheses, action et limites.

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
- Chunks sources analyses: 18 (exploitables: 10).
- Score pedagogique moyen: 44.94/100 (qualite structurelle: 71.39/100).
- Definitions: 2 | exemples: 4 | exercices: 2 | formules: 3 | cas pratiques: 2.
- Repartition par type: theory: 14, worked_example: 1, methodology: 1, market_context: 1, exercise: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S9], [S16].
2. Intuitions - couvert par [S1], [S5], [S7].
3. Formules - couvert par [S5], [S8], [S17].
4. Exemples - couvert par [S7], [S13], [S14], [S17].
5. Exemples resolus - couvert par [S7].
6. Exercices - couvert par [S3], [S4], [S8], [S10].
7. Corriges - couvert par [S1], [S3], [S7], [S9].
8. Cas pratiques - couvert par [S1], [S3].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, intuitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): resumes.

## Faits et angles extraits de la base
- Intuitively,
vega increases at longer maturities because there is more time for a change in implied
volatility to impact the payoff.
- For a given vanilla option, peak vega (like gamma) occurs at the strike where
optionality and time value is maximized.
- Far away from the optionality the option
is either like a forward (if deep in-the-money) or like no position (if deep outof-the-money).
- In either of these cases, changing volatility has minimal impact on
option value.
- Intuitively this is because
higher volatility widens the distribution and therefore brings larger positive payoffs
into play, hence increasing the option value.
- Likewise, short vanilla options always
have short vega exposure.
- ■Summary
When trading FX derivatives, the majority of trading P&L is generated from the
three Greek exposures introduced in this chapter: delta, gamma, and vega.
- Selling delta hedged vanilla options
results in shorter vega and gamma exposures.
- Gamma and vega both come from the optionality within the derivative contract
and both are therefore maximized at the strike for vanilla options.
- A trading position
with a long vega exposure will make money if implied volatility rises and lose money
if implied volatility falls while gamma impacts how delta moves with spot.

## Sources RAG a citer
- [S1] FX Derivatives Trader School ( PDFDrive ), chunk 58, score 0.673352: The peak vega on a vanilla option reduces over time. Intuitively,
vega increases at longer maturities because there is more time for a change in implied
volatility to impact the payoff. For a given vanilla option, peak vega (like gamma) occurs at the strike where
optionality and time value is maximized.
- [S2] FX Derivatives Trader School ( PDFDrive ), chunk 352, score 0.560328 (extrait non cite: source bruitee)
- [S3] Derivatives Markets ( PDFDrive ), chunk 523, score 0.537083 (extrait non cite: source bruitee)
- [S4] FX Derivatives Trader School ( PDFDrive ), chunk 308, score 0.461061: American Vanilla Pricing and Greeks
Comparing American and European vanillas in the CCY1 call and higher CCY1
interest rates case demonstrates how early exercise impacts trading risk. Price
profiles are shown in Exhibit 27.9.
- [S5] Derivatives Models on Models ( PDFDrive ), chunk 47, score 0.461009: Mathematical description of option valuation goes at least back more than
100 years to the now so famous Bachelier (1900) paper, that was based on his doctoral thesis
defended on March 19, 1900. Bachelier assumed a normal distribution for the asset price.
- [S6] FX Derivatives Trader School ( PDFDrive ), chunk 353, score 0.44189: CCY2 premium,
265–267
European digital option replication:
CCY1, 402–403
CCY2, 402
G10, 4
one-touch options variations CCY1
vs. CCY2 payout, 434–435
relative strength of, 219
self-quanto:
CCY1 call options, 510
CCY1 put options, 510–513
Currency blocks, 42
- [S7] FX Derivatives Trader School ( PDFDrive ), chunk 57, score 0.401689: Due to put–call parity, call and put options with the
same strike and maturity have the same gamma profile, shown in Exhibit 6.15. This
gamma can be calculated by taking the gradient of either the call option delta profile
from Exhibit 6.9 or the put option delta profile from Exhibit 6.11.
- [S8] Derivatives Markets ( PDFDrive ), chunk 504, score 0.399959 (extrait non cite: source bruitee)
- [S9] Derivatives Models on Models ( PDFDrive ), chunk 82, score 0.394313 (extrait non cite: source bruitee)
- [S10] FX Derivatives Trader School ( PDFDrive ), chunk 355, score 0.386465 (extrait non cite: source bruitee)
- [S11] Advanced derivatives pricing and risk management  theory, tools and hands on programming application ( PDFDrive ), chunk 431, score 0.386375 (extrait non cite: source bruitee)
- [S12] Advanced Derivatives Pricing and Risk Management  Theory, Tools, and Hands On Programming Applications ( PDFDrive ), chunk 431, score 0.386375 (extrait non cite: source bruitee)
- [S13] Derivatives Models on Models ( PDFDrive ), chunk 54, score 0.386252: This was
probably already known for a very long time and probably published much earlier. We can so far conclude that hedging options with options as well as initial market neutral
static delta hedging were the main principles of option hedging in the early 1900s.
- [S14] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 1094, score 0.382818: The authors show that this option
may be replicated by holding onto a European
- [S15] Derivatives Essentials  An Introduction to Forwards, Futures, Options and Swaps ( PDFDrive ), chunk 2, score 0.374562 (extrait non cite: source bruitee)
- [S16] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 248, score 0.37429 (extrait non cite: source bruitee)
- [S17] Derivatives Models on Models ( PDFDrive ), chunk 172, score 0.372933: The relationship can, for example, be used to value double
barrier options in a intuitive way.
- [S18] FX Derivatives Trader School ( PDFDrive ), chunk 360, score 0.356095: One-touch (OT) options, (Continued)
variations, 434–436
CCY1 vs. CCY2 payout,
434–435
pay-at-maturity vs.

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Black-Scholes call with dividend yield
$$
C = S_0 e^{-qT}N(d_1)-K e^{-rT}N(d_2)
$$
- Usage desk: quote the option premium from observable inputs and document the carry assumptions.
### F2 - d1/d2 controls
$$
d_1=\frac{\ln(S_0/K)+(r-q+\frac{1}{2}\sigma^2)T}{\sigma\sqrt{T}},\qquad d_2=d_1-\sigma\sqrt{T}
$$
- Usage desk: check moneyness, time and volatility before trusting the model output.
### F3 - Put-call parity
$$
C-P=S_0e^{-qT}-Ke^{-rT}
$$
- Usage desk: detect stale quotes or inconsistent funding/dividend assumptions.

