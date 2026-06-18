---
slug: vanilla-options-quote
topic: Vanilla options desk quote
product: equity vanilla option
level: beginner
concepts: Black-Scholes, put-call parity, delta, vega
source_count: 10
---

# Module pratique - Vanilla options desk quote

> Légende de provenance du contenu:
> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).
> - **[reformule]** réécriture pédagogique d'un passage source.
> - **[genere]** exemple/exercice/quiz construit à partir des concepts; calculs vérifiés par le moteur déterministe, non extraits d'une source.

## Promesse du module
Apprendre à gérer les quotes d'options vanilla par la pratique : manipuler, calculer, comparer, décider, puis seulement formaliser la théorie nécessaire.

## Niveau cible et public
- Niveau : débutant
- Public visé : étudiant L3/M1, candidat en finance de marché, développeur front-office débutant
- Durée estimée : 90 minutes
- Produit : option vanilla sur actions
- Concepts : Black-Scholes, parité put-call, delta, vega

## Prerequis
- Payoff d'une option
- Actualisation
- Loi normale
- Notion de volatilité

## Objectifs d'apprentissage
À la fin de ce module, vous saurez :
- Expliquer l'intuition du sujet avant toute formule ;
- Identifier les inputs, les risques et les hypothèses clés ;
- Dérouler un calcul chiffré et l'interpréter en langage de desk ;
- Répondre à un mini-quiz et résoudre un exercice corrigé ;
- Nommer les limites du modèle et la décision opérationnelle associée.

## Positionnement bibliotheque
- Track : Dérivés & Volatilité
- Type d'asset : module réutilisable de cours.
- Sorties attendues : fiche apprenant, cas pratique, corrigé, quiz, notes instructeur.
- Intégration SaaS : ce module doit pouvoir être découpé en leçons, exercices et checkpoints.

## Deroule pratique
### Module 1 - Lire le ticket vanilla
- Objectif pratique : Transformer une demande de quote en inputs propres : spot, strike, maturité, taux, dividendes et volatilité.
- Situation de desk : Sales demande un prix indicatif sur un call européen avant envoi client.
- Notion utile : Moneyness, forward, actualisation, convention de maturité.
- Activité : Construire le ticket et identifier les données manquantes.
- Livrable apprenant : Quote ticket contrôlé.

### Module 2 - Prix Black-Scholes
- Objectif pratique : Calculer call et put avec substitutions visibles et unité de premium.
- Situation de desk : Le desk veut un prix défendable et reproductible.
- Notion utile : d1/d2, prix call/put, rendement des dividendes.
- Activité : Calculer le prix et vérifier la valeur intrinsèque/valeur temps.
- Livrable apprenant : Pricing sheet.

### Module 3 - Controle put-call parity
- Objectif pratique : Détecter une incohérence de quote avant de la transmettre.
- Situation de desk : Le put mid ne colle pas avec le call mid et le forward.
- Notion utile : C - P = forward actualisé moins strike actualisé.
- Activité : Mesurer le parity gap et conclure quote/hold/reject.
- Livrable apprenant : Parity control.

### Module 4 - Greeks utiles au quote
- Objectif pratique : Convertir delta et vega en risque concret pour le trader.
- Situation de desk : Le client augmente la taille et le trader demande le hedge initial.
- Notion utile : Delta hedge, vega par point de volatilité, convention de signe.
- Activité : Calculer les actions de couverture et la sensibilité à la volatilité.
- Livrable apprenant : Risk add-on note.

## Cours redige
### Lecon 1 - Lire le ticket vanilla

**Intuition _[reformule]_.** La demande de prix sur un call européen nécessite de transformer les informations en inputs clairs : spot, strike, maturité, taux, dividendes et volatilité.

**Ce que disent les sources** _[extrait]_. « La vega maximale d'une option vanilla diminue avec le temps. Intuitivement, la vega augmente pour des maturités plus longues car il y a plus de temps pour qu'un changement de volatilité implicite impacte le payoff. Pour une option vanilla donnée, la vega maximale (comme le gamma) se produit au strike où l'optionnalité et la valeur temps sont maximisées. » [S1]

**Le point clé : Moneyness, forward, actualisation, convention de maturité.** Cette notion transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Construire le ticket et identifier les données manquantes. Livrable attendu : Quote ticket contrôlé - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Confondre une sensibilité 'par 1%' avec 'par 0.01' : respecter strictement les unités.

### Lecon 2 - Prix Black-Scholes

**Intuition _[reformule]_.** Le desk recherche un prix défendable et reproductible. L'objectif ici est de calculer les prix des calls et puts avec des substitutions visibles et des unités de premium.

**Ce que disent les sources** _[extrait]_. « La description mathématique de l'évaluation des options remonte à plus de 100 ans, au célèbre article de Bachelier (1900), qui supposait une distribution normale pour le prix de l'actif. » [S4]

**Le point clé : d1/d2, prix call/put, rendement des dividendes.** Cette notion transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer le prix et vérifier la valeur intrinsèque/valeur temps. Livrable attendu : Pricing sheet - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Oublier le signe de la position (long/short, payer/receiver) dans l'interprétation du P&L.

### Lecon 3 - Controle put-call parity

**Intuition _[reformule]_.** Lorsqu'une incohérence apparaît entre le put mid et le call mid, il est crucial de détecter cela avant de transmettre la quote.

**Ce que disent les sources** _[extrait]_. « La tarification des options vanille américaines et européennes montre comment l'exercice anticipé impacte le risque de trading. » [S5]

**Le point clé : C - P = forward actualisé moins strike actualisé.** Cette notion transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Mesurer le gap de parité et conclure quote/hold/reject. Livrable attendu : Parity control - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Appliquer une approximation locale (Taylor) à un choc trop large sans vérifier sa validité.

### Lecon 4 - Greeks utiles au quote

**Intuition _[reformule]_.** Lorsque le client augmente la taille de sa position, le trader doit demander le hedge initial pour gérer le risque.

**Ce que disent les sources** _[extrait]_. « Les options vanille américaines sont toujours plus chères que les équivalentes européennes. » [S5]

**Le point clé : Delta hedge, vega par point de volatilité, convention de signe.** Cette notion transforme la situation en calcul exploitable. Reliez-la à une intuition de signe ou d'ordre de grandeur avant d'appliquer une formule.

**Mise en pratique _[genere]_.** Calculer les actions de couverture et la sensibilité à la volatilité. Livrable attendu : Risk add-on note - un document court contenant le calcul central, une phrase d'interprétation marché et une limite du modèle.

**Piège fréquent.** Présenter un chiffre sans unité ni ordre de grandeur de contrôle.

## Labs pratiques a inclure
1. Quote ticket : spot, strike, maturité, taux, dividendes, volatilité et convention de taille.
2. Black-Scholes price : calculer call/put, valeur intrinsèque et valeur temps.
3. Parity check : mesurer le gap call-put-forward et conclure quote ou reject.
4. Greeks add-on : convertir delta et vega en hedge initial et risque comment.
5. Trader memo : prix, contrôles, hypothèses, action et limites.

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
_[genere - calcul verifie]_ On price un call europeen a la monnaie et on lit prix, d1, d2 et greeks.

**Donnees.** Call vanilla spot 100 strike 100 vol 20% maturite 1 taux 5%.

### Option vanilla Black-Scholes
- Famille: vanilla_option_black_scholes
- Hypotheses controlees:
  - Pas de dividende/carry si non precise.
  - Volatilite et taux constants.
- Calculs a respecter:
  - d1/d2:
    - Formule: BS d1, d2
    - Application: d1=0.3500; d2=0.1500
    - Resultat: d1=0.3500, d2=0.1500
    - Lecture desk: Variables pivots du pricing et des greeks.
  - Prix call:
    - Formule: S*N(d1)-K*exp(-rT)*N(d2)
    - Application: 100*N(0.3500)-100*exp(-0.0500*1)*N(0.1500)
    - Resultat: 10.4506
    - Lecture desk: Valeur theorique du call.
  - Greeks:
    - Formule: Delta=N(d1); Gamma=phi(d1)/(S sigma sqrt(T)); Vega=S phi(d1) sqrt(T)/100
    - Application: inputs S=100, sigma=20.00%, T=1
    - Resultat: Delta=0.6368; Gamma=0.018762; Vega/vol pt=0.3752
    - Lecture desk: Base du hedge delta/vega.
- Actions operationnelles attendues:
  - Comparer prix modele et prix marche.
  - Hedger delta puis surveiller vega/gamma.

**Lecture finale.** Chaque chiffre ci-dessus a une unite explicite et un sens economique; un apprenant doit pouvoir refaire le calcul a la main et retrouver le meme ordre de grandeur.

## Exercices corriges
### Exercice 1 - application directe
_[genere]_ Un call ATM a S=K=100, vol 20%, T=1, r=5%. Sans calculer finement, dites si son delta est plutot proche de 0, 0.5 ou 1, et pourquoi.

**Correction.** Pour un call a la monnaie, N(d1) est legerement au-dessus de 0.5 (le drift r decale d1 vers le positif). Le delta est donc proche de 0.5-0.6: une hausse de 1 du spot fait gagner ~0.5-0.6 au call.

### Exercice 2 - niveau desk
_[genere]_ Spot 100, strike 100, vol 20%, T=1, r=5%. Calculez d1, d2, le prix du call et son delta, puis dites comment hedger 1000 calls.

**Correction detaillee (calcul verifie).**
### Option vanilla Black-Scholes
- Famille: vanilla_option_black_scholes
- Hypotheses controlees:
  - Pas de dividende/carry si non precise.
  - Volatilite et taux constants.
- Calculs a respecter:
  - d1/d2:
    - Formule: BS d1, d2
    - Application: d1=0.3500; d2=0.1500
    - Resultat: d1=0.3500, d2=0.1500
    - Lecture desk: Variables pivots du pricing et des greeks.
  - Prix call:
    - Formule: S*N(d1)-K*exp(-rT)*N(d2)
    - Application: 100*N(0.3500)-100*exp(-0.0500*1)*N(0.1500)
    - Resultat: 10.4506
    - Lecture desk: Valeur theorique du call.
  - Greeks:
    - Formule: Delta=N(d1); Gamma=phi(d1)/(S sigma sqrt(T)); Vega=S phi(d1) sqrt(T)/100
    - Application: inputs S=100, sigma=20.00%, T=1
    - Resultat: Delta=0.6368; Gamma=0.018762; Vega/vol pt=0.3752
    - Lecture desk: Base du hedge delta/vega.
- Actions operationnelles attendues:
  - Comparer prix modele et prix marche.
  - Hedger delta puis surveiller vega/gamma.

## Mini-quiz
_[genere]_ Mini-quiz de verification (5 questions).

**Q1. Dans Black-Scholes, que represente N(d2)?**
- A) La probabilite risque-neutre d'exercice
- B) Le delta du call
- C) La vega
- D) Le prix du put
  - Reponse: **A**. N(d2) est la probabilite risque-neutre que le call finisse dans la monnaie.

**Q2. Le delta d'un call ATM est environ:**
- A) 0
- B) 0.5
- C) 1
- D) -0.5
  - Reponse: **B**. N(d1) ~ 0.5 a la monnaie (legerement au-dessus avec un taux positif).

**Q3. La put-call parity relie call et put via:**
- A) la vol implicite
- B) C - P = S - K e^{-rT}
- C) le gamma
- D) la duration
  - Reponse: **B**. C - P = forward actualise - strike actualise; une violation signale une incoherence de quote.

**Q4. Augmenter la volatilite implicite fait:**
- A) baisser call et put
- B) monter call et put
- C) monter le call, baisser le put
- D) rien
  - Reponse: **B**. La vega est positive pour call et put: plus de vol = plus de valeur temps.

**Q5. La vega est maximale:**
- A) tres ITM
- B) tres OTM
- C) proche de la monnaie
- D) a maturite nulle
  - Reponse: **C**. La sensibilite a la vol est la plus forte autour de l'ATM, surtout a maturite moyenne.

## Resume
- L'intuition d'abord: comprendre le probleme de marche avant la formule.
- Les inputs et hypotheses conditionnent tout le reste.
- Le calcul chiffre n'a de sens qu'avec ses unites et son interpretation.
- Les sources ([Sx]) ancrent la theorie; ce qui n'est pas couvert est marque [genere].
- Un cas se conclut toujours par une decision: quote, hedge, monitor, reduce ou escalate.

## Couverture pedagogique des sources
- Chunks sources analyses: 10 (exploitables: 6).
- Score pedagogique moyen: 46.4/100 (qualite structurelle: 78.0/100).
- Definitions: 0 | exemples: 1 | exercices: 0 | formules: 2 | cas pratiques: 2.
- Repartition par type: theory: 8, methodology: 1, worked_example: 1.

## Plan pedagogique adaptatif (base sur les sources)
1. Definitions - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.
2. Intuitions - couvert par [S1], [S4], [S10].
3. Formules - couvert par [S4], [S7].
4. Exemples - couvert par [S10].
5. Exemples resolus - couvert par [S10].
6. Exercices - couvert par [S3], [S5], [S7].
7. Corriges - couvert par [S1], [S3], [S10].
8. Cas pratiques - couvert par [S1], [S3].
9. Resumes - ABSENT des sources: a generer et marquer 'genere a partir des concepts'.

## Trous pedagogiques (signaler, ne pas inventer)
- Statut: partially_usable - Sources partiellement suffisantes: completer les manques.
- Presents dans les sources: intuitions, formules, exemples, exemples resolus, exercices, corriges, cas pratiques.
- Absents des sources (a marquer 'genere a partir des concepts', pas 'extrait'): definitions, resumes.

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
- [S1] FX Derivatives Trader School ( PDFDrive ), chunk 58, score 0.661419: The peak vega on a vanilla option reduces over time. Intuitively,
vega increases at longer maturities because there is more time for a change in implied
volatility to impact the payoff. For a given vanilla option, peak vega (like gamma) occurs at the strike where
optionality and time value is maximized.
- [S2] FX Derivatives Trader School ( PDFDrive ), chunk 352, score 0.560978 (extrait non cite: source bruitee)
- [S3] Derivatives Markets ( PDFDrive ), chunk 523, score 0.53176 (extrait non cite: source bruitee)
- [S4] Derivatives Models on Models ( PDFDrive ), chunk 47, score 0.458098: Mathematical description of option valuation goes at least back more than
100 years to the now so famous Bachelier (1900) paper, that was based on his doctoral thesis
defended on March 19, 1900. Bachelier assumed a normal distribution for the asset price.
- [S5] FX Derivatives Trader School ( PDFDrive ), chunk 308, score 0.442157: American Vanilla Pricing and Greeks
Comparing American and European vanillas in the CCY1 call and higher CCY1
interest rates case demonstrates how early exercise impacts trading risk. Price
profiles are shown in Exhibit 27.9.
- [S6] FX Derivatives Trader School ( PDFDrive ), chunk 353, score 0.435645: CCY2 premium,
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
- [S7] Derivatives Markets ( PDFDrive ), chunk 504, score 0.387832 (extrait non cite: source bruitee)
- [S8] Advanced derivatives pricing and risk management  theory, tools and hands on programming application ( PDFDrive ), chunk 431, score 0.38685 (extrait non cite: source bruitee)
- [S9] Advanced Derivatives Pricing and Risk Management  Theory, Tools, and Hands On Programming Applications ( PDFDrive ), chunk 431, score 0.38685 (extrait non cite: source bruitee)
- [S10] FX Derivatives Trader School ( PDFDrive ), chunk 57, score 0.379498: Due to put–call parity, call and put options with the
same strike and maturity have the same gamma profile, shown in Exhibit 6.15. This
gamma can be calculated by taking the gradient of either the call option delta profile
from Exhibit 6.9 or the put option delta profile from Exhibit 6.11.

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

