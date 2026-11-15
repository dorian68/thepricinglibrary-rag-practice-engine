# Business indépendant — quatorze références pratiques

14 novembre 2026. **PASS local du sous-périmètre références, API et portabilité** sur les 14 IDs remis. Les anciennes solutions uniquement commentées sont remplacées dans la couche de référence par du code effectivement exécuté. Aucun PASS de parcours UI complet ni de note experte de raisonnement n'est déduit de ce résultat.

Remise relue : [technical-practice-references.md](technical-practice-references.md). Recette indépendante sur API nouvelle `127.0.0.1:8435`, cohorte `business-content-1`, Starter signé **non administrateur**, données de test isolées, pas de corpus attaché ni provider externe. Le port8434était déjà occupé : la première tentative de bind a échoué avant tout appel HTTP, aucun service existant n'a été arrêté et aucun401factice n'a été compté.8435a été sondé libre puis lancé.8430 et ses données n'ont pas changé ;8431reste arrêté.

## Preuves observées

- Pour **chacun des14 IDs**, GET du document de référence, POST du run réellement calculé, export `.py` et `.ipynb` par HTTP. Les **28 exports distincts** ont été exécutés en nouveaux processus `python -I`, hors packageTPL. Leurs tickets et résultats concordent avec l'API, y compris les limites et conventions conservées.
- Le client apprenant a aussi effectué réellement `exercises reference iv-newton`, `run-reference mc-asian`, `export-reference curve-boot` puis exécution du fichier Python téléchargé.
- Anonyme401, gratuit403, ID absent404 et tentative d'envoyer du code arbitraire au POST allowlisté422. Le refus d'un plan attendu n'est pas une panne.
- Le brief source conserve son ID ; le type réel est nommé. L'ID historique `barrier-knock-in` reste associé explicitement au **down-and-out call**, sans prétendre pricer un knock-in. Les hypothèses ajoutées aux paths autocall sont déclarées.

Preuves : première recette API et28 exports (`business/practice-references-review.json` ; preuve locale non publiee), retests ciblés (`business/practice-references-followup.json` ; preuve locale non publiee), CLI (`business/reference-cli-check.json` ; preuve locale non publiee), oracleOHLC (`business/reference-ohlc-oracle.json` ; preuve locale non publiee). Les scripts sont dans le même répertoire. Trois erreurs d'assertion de forme du harness ont été corrigées et leur première trace conservée : type barrière plus précis “down-and-out call”, smile exprimé en moneyness plutôt qu'en strike, tolérance flottante pour59,00000000000001. Elles ne sont pas des défauts produit.

## Contrôles indépendants et utilité pédagogique

| Référence | Contrôle effectué et sens du résultat |
| --- | --- |
| Realized volatility | Reconstruction NumPy indépendante des cinq estimateurs sur les mêmes11séances : CC15,73591361%, Parkinson17,15027235%, GK18,39255738%, RS18,05823305%, YZ17,75005135%. Annualisation252/365 cohérente. |
| European call | CDF normale indépendante, call6,12065411346, put et parité ; unités delta et vega séparées. |
| Options-book Greeks | Attribution signée indépendante : −315000EUR avec facteur1/2 gamma et chocs en points appropriés. |
| SwapDV01 | PayerPV−910000, risque+45500EUR/bp, hausse10bp→+455000 ; annuité figée explicitement. |
| Barrier | Payoffs conditionnels vérifiés ; contact àHannule, retour à1,20après contact ne ressuscite pas le contrat. Aucun prix de barrière général prétendu. |
| Smile fit | Résolution indépendante des équations normales quadratiques sur log-moneyness ; coefficients et résidu cohérents. Pas de fausse validation stale/crossed, SVI ou absence d'arbitrage. |
| AsianMC | Reconstruction indépendante par récurrence des chemins, moyenne arithmétique mensuelle hors t0 et variance échantillonnale : prix5,35668320068, SE0,02563809126.100000échantillons indépendants, pas paires antithétiques inventées. |
| Curve bootstrap | Système linéaire indépendant des trois swaps ; mêmes DF et repricing. |
| Deltahedge | Signes reconstruits : vendre54000, cible−61000, rebalancement−7000actions. |
| IVNewton | Bisection CDF indépendante :26,7311239386%, prix8 ; vega par volatilité1,0 et secours de bracket conservés. |
| Autocall scenarios | Reconstruction chronologique indépendante : up102, flat106, down59par100. Coupon8%p.a./4, **sans mémoire**. Flux non actualisés, ni probabilité ni fairvalue inventées. |
| CDS | Acheteur paie−600000de prime annuelle ; widening25bp→+525000sous annuité figée. Horizons prime et P&L non confondus. |
| ParametricVaR | Quantile arrondi d'origine1,645, VaR658000, limite pédagogique dépassée, stress−1m ; pas de perte maximale ou approbation réelle. |
| Bond duration | DV01 magnitude17000, sensibilité signée−17000, choc25bp→−425000. Pas de convexité non fournie inventée. |

Le bénéfice pour le candidat est concret : refaire le même ticket et comparer méthode, signe, unité et limite, dans Python sans devoir importer une application web. Les sources exécutables sont complètes, les dépendances NumPy des deux références concernées sont annoncées ; les autres utilisent la bibliothèque standard. Il ne s'agit pas d'un environnement Python serveur ouvert : seuls les exemples écrits et bornés sont exécutés.

Deux cas portant un sujet proche peuvent avoir des contrats distincts. Le cours autocall anglais illustre6%parobservation **avec mémoire** ; la référence pratique historique illustre8%annuels trimestriels **sans mémoire**. Les deux calculs sont cohérents avec leurs propres tickets. La future UI doit montrer ce changement de termes avant de comparer leurs chiffres, pas les présenter comme deux sorties du même contrat.

Les 14 références sont des aides à la comparaison et à l'auto-revue. Elles ne notent pas automatiquement la prose et ne certifient pas l'indépendance, la compétence ou le recrutement. Les nouveaux parcours UI de tentative/correction/reprise, les formulaires, les exports au clic et les programmes bilingues restent à recetter après leur remise. Aucune vente, identité fournisseur réelle, disponibilité humaine ou demande de marché n'est validée ici.
