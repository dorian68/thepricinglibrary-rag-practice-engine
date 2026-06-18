---
slug: yield-curve-bootstrapping
topic: Yield curve bootstrapping for desk pricing
product: interest-rate curve
level: intermediate
concepts: discount factors, zero curve, forward rates, interpolation
source_count: 10
---

# Module pratique - Construction de courbes de taux pour le pricing desk

> Légende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** réécriture pédagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit à partir des concepts; calculs vérifiés par le moteur déterministe, non extraits d'une source.

## Promesse du module
Apprendre la construction de courbes de taux pour le pricing desk par la pratique : manipuler, calculer, comparer, décider, puis seulement formaliser la théorie nécessaire.

## Niveau cible et public
- Niveau : intermédiaire
- Public visé : junior quant, analyste de risque de marché, junior sales/structuring
- Durée estimée : 130 minutes
- Produit : courbe de taux d'intérêt
- Concepts : facteurs d'actualisation, courbe zéro, taux forward, interpolation

## Prerequis
- facteur d'actualisation
- interpolation
- conventions de taux

## Objectifs d'apprentissage
À la fin de ce module, vous saurez :
- expliquer l'intuition du sujet avant toute formule ;
- identifier les inputs, les risques et les hypothèses clés ;
- dérouler un calcul chiffré et l'interpréter en langage de desk ;
- répondre à un mini-quiz et résoudre un exercice corrigé ;
- nommer les limites du modèle et la décision opérationnelle associée.

## Positionnement bibliotheque
- Track : Core Finance de Marché
- Type d'asset : module réutilisable de cours.
- Sorties attendues : fiche apprenant, cas pratique, corrigé, quiz, notes instructeur.
- Intégration SaaS : ce module doit pouvoir être découpé en leçons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire les instruments de courbe
- Objectif pratique : Classer les dépôts, futures et swaps par maturité et convention.
- Situation de desk : Le desk doit reconstruire une courbe avant de pricer un swap.
- Notion utile : Tenor, quote, accrual, facteur d'actualisation.
- Activité : Transformer les quotes en tableau de bootstrap.
- Livrable apprenant : Sheet d'input de courbe.

### Module 2 - Bootstrap des facteurs d'actualisation
- Objectif pratique : Extraire les facteurs d'actualisation un par un sans casser les maturités déjà calibrées.
- Situation de desk : Une nouvelle quote 5Y arrive et change le point de courbe.
- Notion utile : Récursion sur coupons, interpolation locale.
- Activité : Calculer un point de courbe et documenter la convention.
- Livrable apprenant : Échelle des facteurs d'actualisation.

### Module 3 - Zeros et forwards
- Objectif pratique : Convertir les facteurs d'actualisation en taux zéro et forwards exploitables.
- Situation de desk : Le trader veut lire le carry implicite entre deux maturités.
- Notion utile : Taux zéro continu, taux forward discret.
- Activité : Calculer les taux zéro/forward et commenter la pente.
- Livrable apprenant : Rapport zéro-forward.

### Module 4 - Controle et usage desk
- Objectif pratique : Vérifier la monotonie, l'interpolation et l'impact sur la valeur actuelle (PV).
- Situation de desk : Une interpolation trop agressive crée un faux signal de risque.
- Notion utile : No-arbitrage local, smoothness, risque de forme de courbe.
- Activité : Comparer deux interpolations et choisir une action.
- Livrable apprenant : Mémo de validation de courbe.

## Cours redige
### Lecon 1 - Lire les instruments de courbe

**Intuition _[reformule]_.** Le desk doit reconstruire une courbe avant de pricer un swap. L'objectif de cette leçon est précisément : Classer les dépôts, futures et swaps par maturité et convention.

**Ce que disent les sources** _[extrait]_. « Distinguishing forward curves from discount curves (representing the collateralization of the forward) motivates an alternative interpolation method, namely interpolation of the forward value (the product of the forward and the discount factor). In addition, treating forward curves as native curves (instead of representing them by pseudo-discount curves) will avoid other problems, like that of overlapping instruments. » [S1]

**Le point clé : Tenor, quote, accrual, facteur d'actualisation.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Transformer les quotes en tableau de bootstrap. Livrable attendu : Sheet d'input de courbe - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Confondre une sensibilité 'par 1%' avec 'par 0.01' : respecter strictement les unités.

### Lecon 2 - Bootstrap des facteurs d'actualisation

**Intuition _[reformule]_.** Une nouvelle quote 5Y arrive et change le point de courbe. L'objectif de cette leçon est précisément : Extraire les facteurs d'actualisation un par un sans casser les maturités déjà calibrées.

**Ce que disent les sources** _[extrait]_. « The method is a common practice (also considered in [1]). However, considering forwards for overlapping periods, this may introduce oscillations and result in implausible delta-hedges (see » [S3]

**Le point clé : Récursion sur coupons, interpolation locale.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer un point de courbe et documenter la convention. Livrable attendu : Échelle des facteurs d'actualisation - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Oublier le signe de la position (long/short, payer/receiver) dans l'interprétation du P&L.

### Lecon 3 - Zeros et forwards

**Intuition _[reformule]_.** Le trader veut lire le carry implicite entre deux maturités. L'objectif de cette leçon est précisément : Convertir les facteurs d'actualisation en taux zéro et forwards exploitables.

**Ce que disent les sources** _[extrait]_. « 15(3), 401–419 (2015) 14. Cuchiero, C., Fontana, C., Gnoatto, A.: A general HJM framework for multiple yield curve modeling. 20(2), 267–320 (2016) 15. Filipovi´c, D., Trolle, A.B.: The term structure of interbank risk. 109(3), 707–733 (2013) 16. Fujii, M., Takahashi, A.: Derivative pricing under asymmetric and imperfect collateralization and CVA. 13(5), 749–768 (2013) » [S4]

**Le point clé : Taux zéro continu, taux forward discret.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer les taux zéro/forward et commenter la pente. Livrable attendu : Rapport zéro-forward - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Appliquer une approximation locale (Taylor) à un choc trop large sans vérifier sa validité.

### Lecon 4 - Controle et usage desk

**Intuition _[reformule]_.** Une interpolation trop agressive crée un faux signal de risque. L'objectif de cette leçon est précisément : Vérifier la monotonie, l'interpolation et l'impact sur la valeur actuelle (PV).

**Ce que disent les sources** _[extrait]_. « Note that these two curves are interchangeable, and knowledge of one completely determines the other. » [S5]

**Le point clé : No-arbitrage local, smoothness, risque de forme de courbe.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Comparer deux interpolations et choisir une action. Livrable attendu : Mémo de validation de courbe - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Présenter un chiffre sans unité ni ordre de grandeur de contrôle.

## Labs pratiques a inclure
1. Inputs de courbe : classer dépôts/futures/swaps et conventions de jour.
2. Bootstrap : calculer les facteurs d'actualisation successifs et vérifier la monotonie.
3. Zéro/forward : convertir DF en taux zéro puis en taux forward.
4. Contrôle d'interpolation : comparer deux interpolations et impact sur PV.
5. Mémo de courbe : conventions, contrôles et risques de courbe résiduels.

## Script enseignant
1. Ouvrir par un cas concret.
2. Demander aux apprenants de formuler l'intuition.
3. Introduire la notation minimale.
4. Faire résoudre une micro-tâche.
5. Débrief : erreurs courantes, limites, interprétation marché.

## Supports a produire
- Fiche apprenant d'une page.
- Slides courtes orientées cas.
- Notebook ou tableur de calcul si le sujet s'y prête.
- Corrigé détaillé.
- Quiz de vérification rapide.

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

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 10 (exploitables: 10).
- Score pedagogique moyen: 60.2/100 (qualite structurelle: 94.5/100).
- Definitions: 2 | exemples: 4 | exercices: 1 | formules: 5 | cas pratiques: 0.
- Repartition par type: theory: 6, worked_example: 2, definition: 1, solution: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S1], [S2].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S1], [S3], [S5], [S9].
4. Exemples - couvert par [S1], [S3], [S6], [S9].
5. Exemples resolus - couvert par [S3], [S9].
6. Exercices - couvert par [S9].
7. Corriges - couvert par [S3], [S5].
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
- [S1] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 238, score 0.618846: Distinguishing forward curves from discount curves (representing the collateralization of
the forward) motivates an alternative interpolation method, namely interpolation of
the forward value (the product of the forward and the discount factor).
- [S2] Swaps and Other Derivatives  (With CD ROM) (The Wiley Finance Series) ( PDFDrive ), chunk 390, score 0.580414 (extrait non cite: source bruitee)
- [S3] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 251, score 0.536308: The method is a common practice (also considered in [1]). However,
considering forwards for overlapping periods, this may introduce oscillations and
result in implausible delta-hedges (see
- [S4] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 281, score 0.497778 (extrait non cite: source bruitee)
- [S5] Interest Rate Swaps and Their Derivatives  A Practitioner s Guide ( PDFDrive ), chunk 153, score 0.497127: Note that these two curves are
interchangeable, and knowledge of one completely determines the other.
- [S6] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 349, score 0.490514: “Best-fit” algorithms
start by assuming a functional form for the term structure and calibrate
its parameters such as to minimize the re-pricing error of the chosen
© The Author(s) 2017
529
J.R.M. Röman, Analytical Finance: Volume II,
https://doi.org/10.1007/978-3-319-52584-6_21
- [S7] The Mathematics Of Financial Modeling And Investment Management ( PDFDrive ), chunk 562, score 0.485387: Since 
the swap curve is effectively the LIBOR curve and investors borrow based 
on LIBOR, the swap curve is more useful to funded investors than a government yield curve.
- [S8] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 237, score 0.475076: Jamshidian, F.: An exact bond option pricing formula. 44, 205–209 (1989)
20. Kenyon, C.: Short-rate pricing after the liquidity and credit shocks: including the basis. 83–87 (2010)
21. Kijima, M., Muromachi, Y.: Reformulation of the arbitrage-free pricing method under the
multi-curve environment. Preprint (2015)
22.
- [S9] Quantitative Finance  A Simulation Based Introduction Using Excel ( PDFDrive ), chunk 119, score 0.466182: 13.4  Yield Curves, Discount Factors, and 
Forward Rates
In this section we discuss the spreadsheet YieldDiscountForward, which 
implements the connection between Yield Curve, Discount Factors, and 
Instantaneous forward rates described in Section 13.2.
- [S10] Innovations in Derivatives Markets  Fixed Income Modeling, Valuation Adjustments, Risk Management, and Regulation ( PDFDrive ), chunk 263, score 0.460862: ,Hoboken(2007). http://www.christian-fries.de/finmath/book
11. Fries, C.P.: Curve calibration. Object oriented reference implementation 2010–2015. http://
www.finmath.net/topics/curvecalibration
12.

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

