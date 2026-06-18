---
slug: barrier-options-gap-risk
topic: Barrier options and gap risk
product: FX barrier option
level: advanced
concepts: down-and-out, knock-out, gap risk, monitoring
source_count: 10
---

# Module pratique - Barrier options and gap risk

> Legende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** reecriture pedagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit a partir des concepts; calculs verifies par le moteur deterministe, non extraits d'une source.

## Promesse du module
Apprendre Barrier options and gap risk par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Niveau cible et public
- Niveau: advanced
- Public vise: quant confirme, trader junior, structureur
- Duree estimee: 130 minutes
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

## Cours redige
### Lecon 1 - Regle de payoff et chemin

**Intuition _[reformule]_.** Un client demande le resultat d'un DOC FX sous trois chemins spot. L'objectif de cette lecon est precisement: Distinguer terminal payoff et evenement de knock-out/knock-in.

**Ce que disent les sources** _[extrait]_. « Before the maturity, if the underlying asset
goes below the barrier level the barrier option will be
knocked in and become a vanilla option. Otherwise,
the barrier option will expire worthless at maturity. Down-and-in puts are more common in this case. Bearish investors can buy down-and-in puts and pay
a lower premium than that on the vanilla put options. » [S1]

**Le point cle: Path-dependence, barrier event, activation/desactivation.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Dessiner la regle de payoff et la table des etats. Livrable attendu: Schema payoff + condition de barriere - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** confondre une sensibilite 'par 1%' avec 'par 0.01': respecter strictement les unites.

### Lecon 2 - Scenario table

**Intuition _[reformule]_.** Le spot finit au-dessus du strike mais a peut-etre touche la barriere. L'objectif de cette lecon est precisement: Calculer payoff sous plusieurs spots et etats de barriere.

**Ce que disent les sources** _[extrait]_. « 24.15
Reverse knock-out and equivalent one-touch option within a pricing tool » [S2]

**Le point cle: Payoff conditionnel et notionnel FX.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Remplir une table spot, hit/no-hit, payoff. Livrable attendu: Table de scenarios avec conclusion - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** oublier le signe de la position (long/short, payer/receiver) dans l'interpretation du P&L.

### Lecon 3 - Gap risk

**Intuition _[reformule]_.** Le spot approche la barriere en marche illiquide. L'objectif de cette lecon est precisement: Expliquer pourquoi le risque pres de la barriere n'est pas un Greek lisse.

**Ce que disent les sources** _[extrait]_. « Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option. » [S3]

**Le point cle: Discontinuite, jump-to-knock-out, slippage.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Identifier les limites du delta hedge pres de H. Livrable attendu: Note gap risk pour risk manager - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** appliquer une approximation locale (Taylor) a un choc trop large sans verifier sa validite.

### Lecon 4 - Monitoring desk

**Intuition _[reformule]_.** La position reste ouverte pendant une annonce macro. L'objectif de cette lecon est precisement: Definir les triggers de surveillance et d'escalation.

**Ce que disent les sources** _[extrait]_. « Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option. » [S4]

**Le point cle: Barrier distance, realized vol, liquidity window.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Construire une grille monitor / hedge / escalate. Livrable attendu: Plan d'action operationnel - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** presenter un chiffre sans unite ni ordre de grandeur de controle.

### Lecon 5 - Debrief modele

**Intuition _[reformule]_.** Le modele donne un prix mais le trader doit survivre au chemin. L'objectif de cette lecon est precisement: Relier pricing, couverture et risque de modele.

**Ce que disent les sources** _[extrait]_. « interest rate
correlations, 336–339
realized spot vs. » [S5]

**Le point cle: Vol surface, smile, discrete monitoring.** C'est la notion qui transforme la situation en calcul exploitable. Reliez-la a une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Lister controles et erreurs courantes. Livrable attendu: Checklist exotics desk - un document court contenant le calcul central, une phrase d'interpretation marche et une limite du modele.

**Piege frequent.** traiter un risque discontinu (barriere, defaut) comme un Greek lisse.

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
- Chunks sources analyses: 10 (exploitables: 9).
- Score pedagogique moyen: 58.7/100 (qualite structurelle: 94.5/100).
- Definitions: 1 | exemples: 6 | exercices: 1 | formules: 3 | cas pratiques: 1.
- Repartition par type: theory: 6, example: 3, worked_example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - couvert par [S6].
2. Intuitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
3. Formules - couvert par [S2], [S6], [S7].
4. Exemples - couvert par [S1], [S3], [S4], [S6].
5. Exemples resolus - couvert par [S6].
6. Exercices - couvert par [S7], [S10].
7. Corriges - couvert par [S2], [S3], [S4], [S6].
8. Cas pratiques - couvert par [S6].
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
- [S1] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 981, score 0.874767: Before the maturity, if the underlying asset
goes below the barrier level the barrier option will be
knocked in and become a vanilla option. Otherwise,
the barrier option will expire worthless at maturity. Down-and-in puts are more common in this case.
- [S2] FX Derivatives Trader School ( PDFDrive ), chunk 274, score 0.473215: 24.15
Reverse knock-out and equivalent one-touch option within a pricing tool
- [S3] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 241, score 0.467431: Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option.
- [S4] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 241, score 0.467431: Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option.
- [S5] FX Derivatives Trader School ( PDFDrive ), chunk 362, score 0.466356: interest rate
correlations, 336–339
realized spot vs.
- [S6] FX Derivatives Trader School ( PDFDrive ), chunk 275, score 0.464466: One of the barriers is knock-out while the other is knock-in. There are
two variations of knock-in/knock-out options:
1. Knock-out until expiry
2.
- [S7] Vault Guide to Advanced Finance and Quantitative Interviews.pdf ( PDFDrive ), chunk 148, score 0.462179: The option to purchase the call option itself has exercise 
price K1 and strike T1. Obtaining a price for this option is not difficult. Since the option still depends on 
the price movement of the underlying S, the Black-Scholes equation still applies. The time domain is 
broken into two parts: (0, T1) and (T1, T2).
- [S8] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 178, score 0.451976: We
will return to the discussion on volatility models when we discuss local volatility later in the
chapter.
- [S9] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 1044, score 0.447626: [3]
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
- [S10] Financial Derivatives  Pricing and Risk Management ( PDFDrive ), chunk 199, score 0.431478: When that happens, the option becomes a plain vanilla option. Accordingly, an
“out” option is initially like a plain vanilla option, except if the price of the underlying good penetrates the stated barrier, the option immediately expires worthless.

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

