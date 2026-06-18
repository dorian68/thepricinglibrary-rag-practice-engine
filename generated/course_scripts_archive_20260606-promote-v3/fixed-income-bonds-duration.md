---
slug: fixed-income-bonds-duration
topic: Bond pricing, duration and rate-shock P&L
product: fixed-income bond
level: beginner
concepts: clean price, YTM, duration, convexity, DV01
source_count: 10
---

# Module pratique - Evaluation des obligations, duration et P&L en cas de choc des taux

> Légende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** réécriture pédagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit à partir des concepts; calculs vérifiés par le moteur déterministe, non extraits d'une source.

## Promesse du module
Apprendre l'évaluation des obligations, la duration et le P&L en cas de choc des taux par la pratique : manipuler, calculer, comparer, décider, puis seulement formaliser la théorie nécessaire.

## Niveau cible et public
- Niveau : débutant
- Public visé : étudiant L3/M1, candidat en finance de marché, développeur front-office débutant
- Durée estimée : 100 minutes
- Produit : obligation à revenu fixe
- Concepts : prix net, YTM, duration, convexité, DV01

## Prerequis
- Valeur temps de l'argent
- Courbe de taux
- Actualisation

## Objectifs d'apprentissage
À la fin de ce module, vous saurez :
- Expliquer l'intuition du sujet avant toute formule ;
- Identifier les inputs, les risques et les hypothèses clés ;
- Dérouler un calcul chiffré et l'interpréter en langage de desk ;
- Répondre à un mini-quiz et résoudre un exercice corrigé ;
- Nommer les limites du modèle et la décision opérationnelle associée.

## Positionnement bibliotheque
- Track : Taux & Revenu Fixe
- Type d'asset : module réutilisable de cours.
- Sorties attendues : fiche apprenant, cas pratique, corrigé, quiz, notes instructeur.
- Intégration SaaS : ce module doit pouvoir être découpé en leçons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Carte des flux de tresorerie
- Objectif pratique : Lire coupon, maturité, rendement et principal.
- Situation de desk : Un portefeuille obligataire doit expliquer son P&L en matière de taux.
- Notion utile : Coupon, prix net/prix brut, intérêts courus.
- Activité : Construire le tableau des flux de trésorerie.
- Livrable apprenant : Calendrier des flux de trésorerie.

### Module 2 - Prix et rendement
- Objectif pratique : Relier prix et rendement sans perdre les conventions.
- Situation de desk : Le rendement moyen bouge et le prix doit être estimé.
- Notion utile : YTM, facteurs d'actualisation, intérêts courus.
- Activité : Calculer un prix approximatif et vérifier le sens prix/rendement.
- Livrable apprenant : Tableau de prix.

### Module 3 - Duration et DV01
- Objectif pratique : Convertir une position en sensibilité EUR/bp.
- Situation de desk : Le risque demande l'impact d'un +25bp.
- Notion utile : Duration modifiée, DV01.
- Activité : Calculer DV01 et P&L en cas de choc.
- Livrable apprenant : Rapport sur la duration.

### Module 4 - Convexite et limites
- Objectif pratique : Savoir quand la duration linéaire ne suffit plus.
- Situation de desk : Un mouvement de taux large rend l'approximation fragile.
- Notion utile : Correction de convexité.
- Activité : Comparer approximation linéaire et corrigée.
- Livrable apprenant : Avertissement sur le risque.

## Cours redige
### Lecon 1 - Carte des flux de tresorerie

**Intuition _[reformule]_.** Un portefeuille obligataire doit expliquer son P&L en matière de taux. L'objectif de cette leçon est précisément : Lire coupon, maturité, rendement et principal.

**Ce que disent les sources** _[extrait]_. « Because the strategy is designed for interest rate futures, we will illustrate it with reference to a bond and a bond futures contract. In order to understand the price sensitivity formula, we must first review the concept of a bond’s duration. Duration has several specific definitions, but generally is used as a measure of price sensitivity. » [S2]

**Le point clé : Coupon, prix net/prix brut, intérêts courus.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Construire le tableau des flux de trésorerie. Livrable attendu : Calendrier des flux de trésorerie - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Confondre une sensibilité 'par 1%' avec 'par 0.01' : respecter strictement les unités.

### Lecon 2 - Prix et rendement

**Intuition _[reformule]_.** Le rendement moyen bouge et le prix doit être estimé. L'objectif de cette leçon est précisément : Relier prix et rendement sans perdre les conventions.

**Ce que disent les sources** _[extrait]_. « Summary OVERVIEW This reading on forward commitment pricing and valuation provides a foundation for understanding how forwards, futures, and swaps are both priced and valued. Key points include the following: The arbitrageur would rather have more money than less and abides by two fundamental rules: Do not use your own money, and do not take any price risk. » [S5]

**Le point clé : YTM, facteurs d'actualisation, intérêts courus.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer un prix approximatif et vérifier le sens prix/rendement. Livrable attendu : Tableau de prix - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Oublier le signe de la position (long/short, payer/receiver) dans l'interprétation du P&L.

### Lecon 3 - Duration et DV01

**Intuition _[reformule]_.** Le risque demande l'impact d'un +25bp. L'objectif de cette leçon est précisément : Convertir une position en sensibilité EUR/bp.

**Ce que disent les sources** _[extrait]_. « One important variation of Macaulay’s duration is called modified duration, which measures the bond price change, adjusted for the level of yield (the yield per compounding period). Specifically, modified duration is expressed as MDB = DURB / (1 + yB) * (ΔB/B) / (ΔyB). » [S2]

**Le point clé : Duration modifiée, DV01.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer DV01 et P&L en cas de choc. Livrable attendu : Rapport sur la duration - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Appliquer une approximation locale (Taylor) à un choc trop large sans vérifier sa validité.

### Lecon 4 - Convexite et limites

**Intuition _[reformule]_.** Un mouvement de taux large rend l'approximation fragile. L'objectif de cette leçon est précisément : Savoir quand la duration linéaire ne suffit plus.

**Ce que disent les sources** _[extrait]_. « Final Settlement Price The Final Settlement Price is established by Eurex on the Final Settlement Day at 12:30 CET based on the volume-weighted average price of all trades during the final minute of trading provided that more than 10 trades occurred during this minute; otherwise the volume-weighted average price of the last 10 trades of the day, provided that these are. » [S7]

**Le point clé : Correction de convexité.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Comparer approximation linéaire et corrigée. Livrable attendu : Avertissement sur le risque - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Présenter un chiffre sans unité ni ordre de grandeur de contrôle.

## Labs pratiques a inclure
1. Calendrier des flux de trésorerie : coupons, principal, intérêts courus et maturité.
2. Prix net/YTM : calculer un prix approximatif et vérifier le sens prix-rendement.
3. DV01 : convertir duration et prix en EUR/bp sur notionnel imposé.
4. Choc des taux : appliquer +25bp puis comparer duration seule vs convexité.
5. Note de risque : limites de l'approximation et contrôles de convention.

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
- Chunks sources analyses: 10 (exploitables: 7).
- Score pedagogique moyen: 47.6/100 (qualite structurelle: 73.0/100).
- Definitions: 2 | exemples: 2 | exercices: 0 | formules: 3 | cas pratiques: 1.
- Repartition par type: theory: 4, market_context: 2, solution: 2, definition: 1, worked_example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S2], [S3].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S2], [S7], [S8].
4. Exemples - couvert par [S2], [S10].
5. Exemples resolus - couvert par [S2], [S10].
6. Exercices - couvert par [S8].
7. Corriges - couvert par [S2], [S7], [S8], [S9].
8. Cas pratiques - couvert par [S4].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, resumes.

## Faits et angles extraits de la base
- Because the strategy is designed for interest rate futures, we will illustrate it with reference to a bond and a bond futures contract.
- In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration.
- Duration has several specific definitions, but generally is used as a
measure of price sensitivity.
- The bond price, B, is the sum of the present values of each
of its cash payments—coupon interest and principal.
- These present values can be found
by discounting each cash payment at a single interest rate, which is known as the yield
or sometimes yield to maturity (yB).
- Formally, we have
B ¼
X
T
t¼1
CPt
(1 þ yB)t,
where CPt is the cash payment made at time t and will be either the coupon interest or
principal.
- If the yield changes, we know that the price changes inversely.
- An approximation to the change in price as it relates to the change in yield is given by the formula,
ΔB  B DURB(ΔyB)
1 þ yB,
where DURB represents the bond’s duration and Δ represents the change in B or yB.
- Formally, the duration is a weighted average of the time to each cash payment date and is
specified in units of time.
- This particular one, though often just called duration, is more precisely identified as Macaulay’s
duration, named after one of the first economists to derive it.

## Sources RAG a citer
- [S1] Mathematics of the Financial Markets  Financial Instruments and Derivatives Modelling, Valuation and Risk Issues ( PDFDrive ), chunk 265, score 0.52985 (extrait non cite: source bruitee)
- [S2] Introduction to Derivatives and Risk Management ( PDFDrive ), chunk 515, score 0.482436: Because the strategy is designed for interest rate futures, we will illustrate it with reference to a bond and a bond futures contract. In order to understand the price sensitivity formula, we must first review the concept
of a bond’s duration.
- [S3] Principles of Financial Engineering ( PDFDrive ), chunk 954, score 0.453999 (extrait non cite: source bruitee)
- [S4] Principles of Financial Engineering ( PDFDrive ), chunk 79, score 0.432478 (extrait non cite: source bruitee)
- [S5] Derivatives Workbook ( PDFDrive ), chunk 13, score 0.43012: Summary OVERVIEW
This reading on forward commitment pricing and valuation provides a foundation for understanding how forwards, futures, and swaps are both priced and valued.
- [S6] Principles of Financial Engineering ( PDFDrive ), chunk 947, score 0.423172 (extrait non cite: source bruitee)
- [S7] Analytical Finance  Volume II  The Mathematics of Interest Rate Derivatives, Markets, Risk and Valuation ( PDFDrive ), chunk 78, score 0.405714 (extrait non cite: source bruitee)
- [S8] Derivatives Markets ( PDFDrive ), chunk 525, score 0.381375 (extrait non cite: source bruitee)
- [S9] Derivatives Markets ( PDFDrive ), chunk 509, score 0.358454 (extrait non cite: source bruitee)
- [S10] Fixed Income Markets  Management, Trading and Hedging ( PDFDrive ), chunk 53, score 0.33733: Valuing Fixed Income Investments and Derivative Securities. New York Institute of Finance, 1991. Business Finance. London: Butterworth, 1995. Martellini L., D. Priaulet, and S. Fixed Income Securities. Chichester, UK: John Wiley 
& Sons, 2004. Fixed Income Analysis for the Global Financial Market.

## Formules de desk
Ces formules sont le minimum operationnel a savoir manipuler avant de passer au cas pratique.
### F1 - Bond price
$$
P=\sum_{i=1}^{n}\frac{CF_i}{(1+y)^{t_i}}
$$
- Usage desk: turn cash flows and yield into clean price controls.
### F2 - Modified duration
$$
D_{\text{mod}}=\frac{D_{\text{Mac}}}{1+y/m}
$$
- Usage desk: estimate price sensitivity to a parallel yield move.
### F3 - Duration-convexity P&L
$$
\frac{\Delta P}{P}\approx -D_{\text{mod}}\Delta y+\frac{1}{2}C(\Delta y)^2
$$
- Usage desk: explain why convexity matters for larger rate shocks.

