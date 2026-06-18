---
slug: structured-products-autocall
topic: Autocallable structured products from term sheet to scenario table
product: autocallable note
level: advanced
concepts: coupon barrier, autocall, protection barrier, redemption
source_count: 10
---

# Module pratique - Autocallable structured products from term sheet to scenario table

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Autocallable structured products from term sheet to scenario table par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: advanced
- Public vise: quant confirme, trader junior, structureur
- Duree estimee: 150 minutes
- Produit: autocallable note
- Concepts: coupon barrier, autocall, protection barrier, redemption

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

## Cours redige
### Lecon 1 - Extraire le term sheet

**Intuition _[reformule]_.** Sales envoie un autocall a expliquer avant client call. L'objectif de cette lecon est precisement: Transformer la fiche produit en conditions calculables.

**Ce que disent les sources** _[extrait]_. « In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market downturn the product leads to losses. Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING » [S1]

**Le point cle: Observation dates, coupon barrier, autocall level.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Construire la table des conditions. Livrable attendu: Term-sheet map - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

### Lecon 2 - Coupon et autocall

**Intuition _[reformule]_.** Le sous-jacent finit au-dessus du niveau autocall a une date d'observation. L'objectif de cette lecon est precisement: Calculer les coupons et l'evenement de remboursement anticipe.

**Ce que disent les sources** _[extrait]_. « At the scheduled maturity date, assuming that no early redemption event took place:
∙If GoldFinal ≥GoldInitial, redemption is equal to (100% + Conditional Coupon) × Notional;
∙If GoldFinal < Put Strike the note-holder is exposed to the downside risk arising from the
short put position and the redemption will be equal to Notional × GoldFinal/GoldInitial. » [S2]

**Le point cle: Indicator functions, memory coupon, early redemption.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Remplir la logique date par date. Livrable attendu: Coupon/autocall grid - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

### Lecon 3 - Protection barrier

**Intuition _[reformule]_.** Le sous-jacent finit sous la barriere. L'objectif de cette lecon est precisement: Expliquer la perte conditionnelle en fin de vie.

**Ce que disent les sources** _[extrait]_. « At the scheduled maturity date, assuming that no early redemption event took place:
∙If GoldFinal ≥GoldInitial, redemption is equal to (100% + Conditional Coupon) × Notional;
∙If GoldFinal < Put Strike the note-holder is exposed to the downside risk arising from the
short put position and the redemption will be equal to Notional × GoldFinal/GoldInitial. » [S3]

**Le point cle: Capital protection, downside participation.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer redemption finale. Livrable attendu: Downside explanation - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

### Lecon 4 - Scenario table client

**Intuition _[reformule]_.** Le client veut comprendre coupon vs capital at risk. L'objectif de cette lecon est precisement: Comparer upside, flat, moderate down et crash scenario.

**Ce que disent les sources** _[extrait]_. « Of course, if the zero-coupon bond were that of any non-government issuer, there is a nonnegligible risk of default. Clearly, Lehman-issued “principal-protected” structured notes failed 
to repay the principal when Lehman Brothers defaulted, much to the chagrin of investors 
who misunderstood the idea. Yet, true principal protection is still possible if a zero-coupon 
government bond is purchased. » [S4]

**Le point cle: Cash-flow path dependency, redemption, loss participation.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Produire une table de scenarios lisible par sales. Livrable attendu: Client scenario table - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** presenter un chiffre sans unite ni ordre de grandeur de controle.

### Lecon 5 - Desk risk

**Intuition _[reformule]_.** La structure vend du coupon mais concentre du tail risk. L'objectif de cette lecon est precisement: Relier attrait client et risques de couverture.

**Ce que disent les sources** _[extrait]_. « Financial engineering provides ways to construct any payoff structure desired by an investor. However, often these payoffs involve complex option positions, and clients may not have the
knowledge, or simply the means, to handle such risks. Market practitioners can do this better. For
example, many structured products offer principal protection or credit enhancements to investors. » [S5]

**Le point cle: Barrier/gamma/vega/liquidity risk.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Ecrire memo sales + risk. Livrable attendu: Client/risk memo - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

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

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 10 (exploitables: 10).
- Score pedagogique moyen: 64.0/100 (qualite structurelle: 100.0/100).
- Definitions: 3 | exemples: 8 | exercices: 1 | formules: 1 | cas pratiques: 2.
- Repartition par type: theory: 8, example: 2.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S4], [S5], [S7].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S6].
4. Exemples - couvert par [S1], [S2], [S3], [S4].
5. Exemples resolus - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
6. Exercices - couvert par [S6].
7. Corriges - couvert par [S4], [S6], [S8], [S10].
8. Cas pratiques - couvert par [S4], [S9].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: usable - Sources suffisantes pour un cours complet.
- Presents dans les sources: definitions, formules, exemples, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): intuitions, exemples resolus, resumes.

## Faits et angles extraits de la base
- In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market downturn the product leads to losses.
- Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING
- In the 1990s, reverse convertibles were often issued with embedded short at-the-money put
options.
- The downside of such products was that investors would suffer losses if the underlying was
below the initial level.
- As investor demand waned in response to the market downturn following the
bursting of the tech bubble, a new generation of products was developed that embedded a short atthe-money down-and-in put option.
- The barrier feature provided investors with additional protection
since the put option would not be triggered unless the (down) barrier was reached.
- Such barrier
reverse convertibles are popular structured products in Europe and in the United States.
- Moreover, the large number of structured products and the relative illiquidity of the underlying equity
market made hedging such products more difficult than is the case for FX products, for example.
- Some structured products including reverse convertibles have embedded call features.
- Banks that issue structured products refer to these
products with call features as autocallable, which is the abbreviation of automatically callable.

## Sources RAG a citer
- [S1] Principles of Financial Engineering ( PDFDrive ), chunk 764, score 0.791685: In this
case, the buyer takes on a large downside risk and may be surprised that in an equity market downturn the product leads to losses. Thus, investors should carefully compare the yield offered by the
706
CHAPTER 20 ESSENTIALS OF STRUCTURED PRODUCT ENGINEERING
- [S2] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 305, score 0.774355 (extrait non cite: source bruitee)
- [S3] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 305, score 0.774355 (extrait non cite: source bruitee)
- [S4] Demystifying Exotic Products  Interest Rates, Equities and Foreign Exchange  ( PDFDrive ), chunk 205, score 0.773752: Of course, if the zero-coupon bond were that of any non-government issuer, there is a nonnegligible risk of default. Clearly, Lehman-issued “principal-protected” structured notes failed 
to repay the principal when Lehman Brothers defaulted, much to the chagrin of investors 
who misunderstood the idea.
- [S5] Principles of Financial Engineering ( PDFDrive ), chunk 751, score 0.769596: Financial engineering provides ways to construct any payoff structure desired by an investor. However, often these payoffs involve complex option positions, and clients may not have the
knowledge, or simply the means, to handle such risks. Market practitioners can do this better.
- [S6] FX Derivatives Trader School ( PDFDrive ), chunk 294, score 0.731174: Specifically, there are increased exposures to the ATM curve, and additional
exposures to the forward smile. Therefore, when pricing and risk managing window
barrier options it is important to assess exactly which pricing methodology is used. For example:
■Which ATM volatility curve is used to generate TV?
- [S7] Trading and pricing financial derivatives   a guide to futures, options, and swaps ( PDFDrive ), chunk 176, score 0.666189 (extrait non cite: source bruitee)
- [S8] FX Derivatives Trader School ( PDFDrive ), chunk 293, score 0.665453: Also, if the
rear-window barrier is through current spot, this approach does not work because
the American barrier option variation will have already knocked. It may also be useful to assess the probability of the rear-window barriers being
knocked.
- [S9] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 252, score 0.654239: In a later chapter, we
will see how bundling financing and hedging transactions helps reduce total credit costs and
can aid in monetizing the benefits of hedging.
- [S10] Swaps and Other Derivatives ( PDFDrive ), chunk 260, score 0.653885: In this case, the Final coupon ¼ Total accrued coupon (excluding
current)  Knockout level, where the Knockout level ¼ 20%. If there is no early redemption, the
Final coupon ¼ Knockout level  Total accrued coupon (excluding current).

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

