---
slug: barrier-options-gap-risk
topic: Barrier options and gap risk
product: FX barrier option
level: advanced
concepts: down-and-out, knock-out, gap risk, monitoring
source_count: 10
---

# Module pratique - Barrier options and gap risk

## Promesse du module
Apprendre Barrier options and gap risk par la pratique: manipuler, calculer, comparer,
decider, puis seulement formaliser la theorie necessaire.

## Public et niveau
- Public: learners who want to practice market finance through desk cases, calculations and risk decisions
- Niveau: advanced
- Duree: 130 minutes
- Produit: FX barrier option
- Concepts: down-and-out, knock-out, gap risk, monitoring

## Objectifs d'apprentissage
- Comprendre le probleme de marche avant la formule.
- Savoir identifier les inputs, les risques et les hypotheses.
- Produire un raisonnement utilisable en contexte professionnel.
- Transformer une source theorique en decision ou en exercice.

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

**Cas de depart.** Un client demande le resultat d'un DOC FX sous trois chemins spot. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** own-and-in Call/Down-and-in Put
The down-and-in barrier option has a knock-in barrier
level, which is below the initial underlying asset
level. [S1]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Path-dependence, barrier event, activation/desactivation..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Dessiner la regle de payoff et la table des etats. Le livrable attendu est un document court et actionnable: Schema payoff + condition de barriere.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 2 - Scenario table

**Cas de depart.** Le spot finit au-dessus du strike mais a peut-etre touche la barriere. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Before the maturity, if the underlying asset
goes below the barrier level the barrier option will be
knocked in and become a vanilla option. [S2]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Payoff conditionnel et notionnel FX..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Remplir une table spot, hit/no-hit, payoff. Le livrable attendu est un document court et actionnable: Table de scenarios avec conclusion.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 3 - Gap risk

**Cas de depart.** Le spot approche la barriere en marche illiquide. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Bearish investors can buy down-and-in puts and pay
a lower premium than that on the vanilla put options. [S3]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Discontinuite, jump-to-knock-out, slippage..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Identifier les limites du delta hedge pres de H. Le livrable attendu est un document court et actionnable: Note gap risk pour risk manager.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 4 - Monitoring desk

**Cas de depart.** La position reste ouverte pendant une annonce macro. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** Up-and-out Call/Up-and-out Put
This is the ﬁrst kind of knock-out barrier options. [S4]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Barrier distance, realized vol, liquidity window..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Construire une grille monitor / hedge / escalate. Le livrable attendu est un document court et actionnable: Plan d'action operationnel.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

### Lecon 5 - Debrief modele

**Cas de depart.** Le modele donne un prix mais le trader doit survivre au chemin. Le point important n'est pas de reciter une formule: l'apprenant doit transformer la demande en inputs, controles et decision de desk.

**Ce que la source apporte.** The up-and-out barrier option has a knock-out barrier
level above the initial underlying asset level. [S5]

**Methode de travail.**
1. Identifier le produit, le sens economique et les donnees manquantes.
2. Poser les conventions: unite, horizon, devise, signe de position et source de marche.
3. Appliquer la notion utile: Vol surface, smile, discrete monitoring..
4. Controler le resultat avec une borne simple, une intuition de signe ou une sensibilite.
5. Conclure par une action: quote, hedge, monitor, reduce, reject ou escalate.

**Application pratique.** Lister controles et erreurs courantes. Le livrable attendu est un document court et actionnable: Checklist exotics desk.. Il doit contenir le calcul central, une phrase d'interpretation et une limite du modele.

**Controle de qualite.** Avant de valider, verifier que le chiffre a une unite, que le signe correspond au sens de la position, que l'approximation est raisonnable pour le niveau de risque, et que la decision reste comprehensible par un trader ou un risk manager.

## Labs pratiques a inclure
1. Payoff path rule: definir hit/no-hit et payoff terminal.
2. Scenario table: calculer trois scenarios spot avec et sans knock-out.
3. Gap risk: expliquer la rupture de delta hedge pres de la barriere.
4. Monitoring plan: definir distance barrier, triggers et escalation.
5. Debrief: limites modele, discrete monitoring et smile.

## Banque d'exercices rattaches
- Exercice 1: calcul court avec correction numerique.
- Exercice 2: cas de risque ou P&L avec interpretation operationnelle.
- Exercice 3: question de jugement professionnel, comme en salle de marches.

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

## Faits et angles extraits de la base
- own-and-in Call/Down-and-in Put
The down-and-in barrier option has a knock-in barrier
level, which is below the initial underlying asset
level.
- Before the maturity, if the underlying asset
goes below the barrier level the barrier option will be
knocked in and become a vanilla option.
- Bearish investors can buy down-and-in puts and pay
a lower premium than that on the vanilla put options.
- Up-and-out Call/Up-and-out Put
This is the ﬁrst kind of knock-out barrier options.
- The up-and-out barrier option has a knock-out barrier
level above the initial underlying asset level.
- Before
maturity, if the underlying asset crosses the barrier
level, the option will be knocked out and become
worthless.
- A bearish investor would buy up-and-
out puts to achieve more leverage by paying a lower
premium than that on vanilla puts.
- Down-and-out Call/Down-and-out Put
The down-and-out barrier option has a knock-out
barrier level below the initial underlying asset level.
- Before maturity, if the underlying asset goes below
the barrier level, the option will be knocked out
and become worthless.
- A bullish investor would
buy down-and-out calls to achieve more leverage by
paying a lower premium than that on vanilla calls.

## Sources RAG a citer
- [S1] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 981, score 0.878556: own-and-in Call/Down-and-in Put
The down-and-in barrier option has a knock-in barrier
level, which is below the initial underlying asset
level. Before the maturity, if the underlying asset
goes below the barrier level the barrier option will be
knocked in and become a vanilla option. Otherwise,
the barrier option will expire worthless at maturity. Down-and-in puts are more common in this case.
- [S2] FX Derivatives Trader School ( PDFDrive ), chunk 274, score 0.477479: 24.15
Reverse knock-out and equivalent one-touch option within a pricing tool [Page 470]
AMERICAN BARRIER OPTIONS
452
One-touchbid–offerspreadsaremonitoredanddirectlyobservedintheinterbank
broker market so exotics traders tend to describe reverse barrier bid-offer spreads
in terms of the embedded one-touch bid-offer.
- [S3] FX Derivatives Trader School ( PDFDrive ), chunk 362, score 0.474596: range, 517–518
European, 516–517
Realized skew, 220
Realized (historic) spot volatility:
calculating, 326, 328–331
in market analysis, 325–343
Exponentially Weighted Moving
Average volatility, 331–333
realized spot vs. interest rate
correlations, 336–339
realized spot vs.
- [S4] FX Derivatives Trader School ( PDFDrive ), chunk 275, score 0.468499: plus two
American barriers: one barrier positioned in-the-money and one positioned out-of-
the-money. One of the barriers is knock-out while the other is knock-in. There are
two variations of knock-in/knock-out options:
1. Knock-out until expiry
2.
- [S5] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 241, score 0.463437: r options
are an extension of vanilla options. Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option.
- [S6] Pricing and Hedging Financial Derivatives  A Guide for Practitioners ( PDFDrive ), chunk 241, score 0.463437: r options
are an extension of vanilla options. Standard calls and puts have payoffs that depend on the
strike, while barrier options have payoffs that depend on the strike and the barrier. ∙Where the option is activated, with the price of the underlying asset hitting a barrier, it may
be known as an “up-and-in”, “knock-in” or “down-and-in” option.
- [S7] Vault Guide to Advanced Finance and Quantitative Interviews.pdf ( PDFDrive ), chunk 148, score 0.462179: chase or sell either a call 
or put on S with strike price K2 and expiry T2. The option to purchase the call option itself has exercise 
price K1 and strike T1. Obtaining a price for this option is not difficult. Since the option still depends on 
the price movement of the underlying S, the Black-Scholes equation still applies. The time domain is 
broken into two parts: (0, T1) and (T1, T2).
- [S8] Fuel Hedging and Risk Management  Strategies for Airlines, Shippers and Other Consumers ( PDFDrive ), chunk 178, score 0.453614: rical models use dis-
cretization, which needs to be small enough to avoid cases of simulated negative variance. We
will return to the discussion on volatility models when we discuss local volatility later in the
chapter.
- [S9] Encyclopedia of Quantitative Finance ( PDFDrive ), chunk 1044, score 0.448983: tility
Swaps, Goldman Sachs Quantitative Strategies Research
Notes. [3]
Ren, Y., Madan, D. & Qian, M. (2007). Calibrating and
pricing with embedded local volatility models, Risk 20(9),
138–143. Related Articles
Corridor
Variance
Swap;
Realized
Volatility
Options; Variance Swap; Volatility Index Options;
Weighted Variance Swap. YONG REN
- [S10] Financial Derivatives  Pricing and Risk Management ( PDFDrive ), chunk 199, score 0.432423: rice. When that happens, the option becomes a plain vanilla option. Accordingly, an
“out” option is initially like a plain vanilla option, except if the price of the un-
derlying good penetrates the stated barrier, the option immediately expires worth-
less. Barrier options can be either calls or puts, permitting eight types of barrier
options:
1. Down-and-in call
2. Up-and-in call
3. Down-and-in put
4.

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

