# Technical RL — numerical trust, RFQ and private paper contracts

Date de travail : 14 novembre 2026. Périmètre : constats T01–T04 de l’audit
CLI, puis correction du parcours devis → position papier → rafraîchissement.
Application du protocole `AGENTS.md`, du rôle `AGENT_TECHNICAL_RL.md` et de la
skill `tpl-technical-rl`. Aucun commit/push effectué par ce sous-agent.

**Verdict technique sur ce périmètre : PASS**, avec les limites explicites
ci-dessous. Le verdict Business et la décision de livraison du produit entier
appartiennent à la revue indépendante ; ils ne sont pas déduits de ce PASS.

## Résultat observable

| Constat | Avant | Comportement corrigé et preuve |
|---|---|---|
| T01 — registre | Deux tickets très différents pouvaient recevoir 3,45 ; les descripteurs passaient pour des capacités opérationnelles. | CLI native, MCP JSONL stdio et HTTP appellent les vrais calculs. Deux tickets BSM donnent environ 10,450575 et 114,877191 et correspondent à un oracle `math.erf` indépendant. Aucun prix par défaut pour un ticket vanilla incomplet/invalide. |
| T01 — disponibilité | Loaders/approvals synthétiques présentés comme résultats utilisables. | Les 874 descripteurs existants sont conservés ; neuf IDs `canonical.*` supplémentaires appellent les neuf moteurs. Chaque descripteur expose son implémentation. Sur cet environnement : **883 descripteurs, 73 exécutables, 810 indisponibles**, `all_descriptors_valid=true`, `all_ok=false`. Une capacité sans adaptateur renvoie `unavailable`, `data:null`, aucune preuve d’exécution inventée et un code CLI 2. |
| T02 — modèle commodity | Le ticket forward WTI utilisait une convention spot incompatible. | Black-76 via le noyau BSM canonique avec `q=r`, actualisation explicite et rho tenant le forward constant. F=K=80, r=4 %, σ=13,41 %, T=0,5 donne **2,96528733**, contre **2,96527696** pour l’oracle `erf` indépendant ; tolérance absolue 2e-5 liée à l’approximation CDF du noyau existant. |
| T03 — exotique | PV/Grecs constants ; faux libellés LSV/smile/corrélation ; Euro Stoxx mal routé. | Simulation GBM risque neutre, véritable mémoire de coupons, observations discrètes, autocall et protection finale. Seed et calendrier sont restitués. PV/Grecs dépendent réellement du ticket. Erreur du prix et erreurs des différences finies sont estimées à partir des paires antithétiques indépendantes. Euro Stoxx reste Euro Stoxx. Aucune prétention LSV, smile calibré ou Greek de corrélation. |
| T04 — assistant | Écrasement du ticket par un exemple S100/K100 ; réponse française malgré la demande anglaise. | Lecture du vrai contexte UI canonique en décimaux/années, compatibilité des anciens contrôles en %/jours et émission des clés réellement lues par le frontend. Le ticket S125/K110/r3 %/q1 %/σ30 %/T0,75 est conservé. Les legs/primes du payoff actif et la mesure/seed/méthode Monte Carlo active restent ceux de l’utilisateur. Mode déterministe local et limites annoncés. |
| Papier — fidélité | Exotique transformé en call SPX ; option FX en forward ; quantités modifiées à l’enregistrement. | La position conserve le type, le sous-jacent, les paramètres normalisés, le modèle, la quantité et le PV du devis calculé serveur. Six familles vérifiées : Black-76, Garman–Kohlhagen, BSM crypto, autocall GBM, swap flat-curve et CDS flat-hazard. |
| Papier — confidentialité | Singleton partagé entre comptes. | Carnet par sujet JWT vérifié et par store applicatif. Un compte B ne voit ni positions ni journal ni RFQ du compte A. Une clé opérateur partagée seule ne remplace pas une identité utilisateur. |
| Papier — retries/risque | Nouvelle cotation ou doublon possible lors d’un retry ; approbation implicite trompeuse. | Clé d’idempotence vérifiée **avant** un nouveau pricing ; un retry après mouvement du marché retrouve exactement le devis initial. Même clé + requête différente : 422. Aucun ordre externe ; risque complet `NOT_ASSESSED` et aucune approbation. |

Le registre est une surface d’intentions plus large que l’implémentation actuelle.
Le chiffre 883 ne signifie donc ni 883 fonctionnalités financières livrées ni un
score de satisfaction. Le parcours RFQ utilise des helpers locaux réellement
calculés ; ses traces l’indiquent et ne prétendent pas avoir exécuté un loader
du registre. Les neuf calculateurs canoniques utilisent leurs moteurs réels ;
ils ne sont pas ramenés au sous-ensemble de modèles RFQ.

## Reproduction sans interface ni provider

Depuis `Tools/pricinglibrary_rag_backend` :

```powershell
python scripts/smoke_trusted_pricing.py --output ../../reports/product-hardening-2026-11-14/trust-evidence.json
python -m pytest tests/test_trust_hardening.py tests/test_tool_registry.py tests/test_agent_interaction_layers.py tests/test_black_scholes.py tests/test_monte_carlo.py tests/test_api_security.py -q --basetemp .tmp/trust-final-review
python scripts/smoke_tool_registry.py
python scripts/smoke_agent_mcp_adapter.py
python scripts/smoke_agent_runtime_state.py
```

Le smoke crée un store SQLite temporaire vide et des identités/entitlements
de test signés, active les règles de sécurité de production et lance de vraies
commandes Python en sous-processus ainsi qu’un transport MCP JSONL stdio.
Les appels HTTP utilisent l’application ASGI réelle avec `TestClient`, sans
serveur desktop. Aucune session Supabase réelle ni vente n’est simulée comme
une preuve commerciale. Aucun prix de marché, corpus privé, broker, checkout,
LLM externe, Docker ou Ollama n’est nécessaire. Node est nécessaire au moteur
de calibration ; s’il manque, sa capacité doit être annoncée indisponible.

Preuve structurée : trust-evidence.json (`trust-evidence.json` ; preuve locale non publiee).
Le smoke donne **33/33 PASS**, sortie native 0, preuve JSON régénérée après les
dernières corrections. L’ensemble ciblé de six fichiers de tests a donné
**111 PASS en 21,75 s**, puis **1 PASS supplémentaire** pour un champ optionnel
non fini et sa sérialisation JSON. Les trois smokes registre, MCP et runtime
ci-dessus donnent également PASS ; `git diff --check` passe sur les fichiers
existants de ce périmètre. Un essai initial a échoué avant toute fixture pour une ACL
du dossier Temp Windows : la commande reproductible choisit maintenant un
`--basetemp` explicite dans `.tmp`, sans modifier les permissions système.
La fermeture du client et un passage GC précèdent le nettoyage du smoke ;
un fichier SQLite encore verrouillé par Windows peut rester dans ce dossier
ignoré, sans masquer les résultats fonctionnels ni interrompre leur export.

Les tests incluent des oracles indépendants BSM/Black-76/GK, cash-flows
déterministes à volatilité nulle, payoff analytique plafonné à une date,
reconstruction indépendante de l’erreur antithétique, PV swap non-par/CDS,
seeds répliqués, bornes CPU, entrées non finies, vrais transports et assertions
sur les snapshots/journaux. Il ne s’agit pas seulement de compter des routes.

## Contrat API papier stable

Toutes les routes nécessitent une identité signée. Le middleware conserve
l’entitlement Pro et le bypass opérateur existant ; le handler exige néanmoins
un sujet pour un carnet privé. Aucun `userId`, nom de room ou propriétaire
fourni par le client n’est accepté.

* `POST /agent/desk/run` : `{query:string}`. Calcule un devis dans le contexte
  du carnet du sujet vérifié, sans créer de position.
* `POST /agent/desk/trade` : `{query:string, side?:1|-1,
  idempotency_key?:string}`. La même clé peut être fournie dans le header
  `Idempotency-Key` ; si les deux clés divergent, 422. Réponse conservant
  `{result,snapshot}` et ajoutant `{paper_position,replayed}`. La side est un
  entier strict ; booléen, zéro, champ propriétaire ou modèle non supporté : 422.
* `GET /agent/desk/state` : marchés explicitement simulés, anciens exemples
  seed distincts, `paper_positions`, `paper_journal`, `paper_summary` avec P&L
  séparé par devise, scope et limites de persistance.
* `POST /agent/desk/tick?seconds=N` : avance uniquement les facteurs simulés du
  carnet du propriétaire. Valeur finie entre 0 et 2 678 400 secondes ; hors
  bornes/non-finie : 422. Un tick nul n’ajoute aucun bruit artificiel.

Le retry idempotent garde le devis d’origine. La quantité d’option FX est en
EUR de base et son PV est en USD ; la devise de notionnel est restituée
séparément. Les options commodities/crypto distinguent quantité physique et
notionnel. Une option Brent est rafraîchie sur le facteur Brent, un contrat
Euro Stoxx sur SX5E, et un swap EUR sur le taux EUR. Aucun mapping vers un
autre sous-jacent n’est admis.

## Modèles, bornes et limites qui restent visibles

Le modèle autocall est un modèle pédagogique original à **un seul actif**,
volatilité constante et taux/carry déterministes. Protection testée uniquement
à maturité, mémoire de coupon, observations régulières et dernier stub réel.
256 à 20 000 chemins pairs, 1 à 12 observations/an, au plus 120 dates,
maturité 0,25 à 10 ans et seed entier explicite. Le SE utilise des moyennes
de paires antithétiques ; les Grecs sont calculés par différences finies avec
nombres aléatoires communs et erreurs d’échantillonnage publiées. Le modèle
ne couvre ni basket/worst-of, LSV, smile calibré, spread émetteur, calendrier
bancaire, funding, ni risque de corrélation.

Le swap utilise une courbe de taux continus plate, paiements fixes annuels et
dernier stub. Le CDS est une approximation à hazard plat et prime continue.
Ces modèles sont identifiés par leur nom réel ; aucune calibration OIS,
multicurve, CDS de marché ou convention accrued-on-default n’est prétendue.
Les demandes sans moteur exact (barrier, range accrual, worst-of, swaption,
forward FX, etc.) gardent leur catalogue mais ne reçoivent **aucune cotation
d’un contrat de remplacement**. Les modèles Black lognormaux refusent les
prix/strikes négatifs ; cela ne couvre pas une situation de marché à prix
négatifs.

La notation papier est un **scénario à maturité contractuelle constante**.
Elle réutilise le même contrat et applique des variations relatives des
facteurs simulés, sans inventer une observation d’autocall, un coupon encaissé
ou un règlement. Un facteur absent est annoncé comme figé. Le refresh
recalcule les PV et les Grecs analytiques des modèles simples ; les Grecs MC
d’entrée sont conservés séparément et les Grecs MC courants restent non
évalués plutôt que de réutiliser silencieusement une ancienne valeur.

La persistance du carnet papier reste **en mémoire du processus**, annoncée
dans chaque position et snapshot : redémarrage ou plusieurs workers ne
constituent pas un portefeuille durable partagé. Au plus 128 carnets actifs,
64 positions par carnet et huit positions MC ; aucun carnet existant n’est
évincé silencieusement. Ces limites sont une frontière du simulateur actuel,
pas une revendication de service de portefeuille de production. Les agrégats
historiques du book seed sont explicitement séparés du risque complet des
nouvelles positions ; aucune approbation ni conversion inter-devises
inventée ne les agrège.

L’assistant offline n’est pas un évaluateur expert du raisonnement écrit et
ne donne plus une fausse note. Le mode LLM optionnel peut fournir une
narration identifiée comme non vérifiée ; le texte déterministe et les
valeurs calculées restent la source de vérité. Un ticket de calcul manquant
est demandé sans écraser le ticket actif.

## Références de conventions

Les conventions forward/discount de Black-76 ont été recoupées sur le
[code primaire QuantLib, `blackFormula`](https://github.com/lballabio/QuantLib/blob/master/ql/pricingengines/blackformula.cpp).
L’avis [CME Clearing 20-320](https://www.cmegroup.com/notices/clearing/2020/08/Chadv20-320.pdf)
distingue les méthodes d’options concernées et leur contexte de prix
négatifs. Ces références ne signifient pas que TPL utilise QuantLib comme
dépendance ni qu’un modèle plat pédagogique reproduit les valorisations CME.

## Fichiers de ce sous-périmètre

* Nouveaux helpers : `pricinglibrary_rag/trusted_analytics.py`,
  `pricinglibrary_rag/paper_book.py`.
* Adaptateurs existants : `tool_registry.py`, `mcp_adapter.py`, `desk.py`,
  `desk_agents.py`, `desk_state.py`, `agui.py` et codes de sortie de `cli.py`.
* API : uniquement DTO de trade et blocs `/agent/desk/{run,state,tick,trade}`,
  après transfert explicite de leur ownership par l’agent CLI/root.
* Preuves exécutables : `tests/test_trust_hardening.py`, ajustement de
  `tests/test_tool_registry.py`, `scripts/smoke_trusted_pricing.py` et
  `scripts/smoke_tool_registry.py`.

Le gateway canonique neuf moteurs et les contrats learner CLI/API sont fournis
par l’autre agent ; ce travail les réutilise sans dupliquer leurs calculs.
Les données privées, cours, générateurs et autres blocs API/frontend sont
hors du périmètre de ces modifications.

## Addendum — contrat affiché après la revue Business indépendante

Business a trouvé une incohérence de métadonnées : le ticket
`BTC put quantity 3 over 3 months S=20000 K=21000 r=3% sigma=70% T=0.25 years`
était correctement calculé en **put à 3278,027771491523 USD/BTC**, mais la
spec l’étiquetait `BTC Vanilla Call (ATM)`, avec un strike nul et un payoff de
call. C’est un défaut de confiance même lorsque le prix est juste.

Le 14 novembre, `desk_agents.py` synchronise désormais la spec **après**
validation et calcul, depuis `pricing_result.calculation.inputs`. La
correction couvre les six familles, sans changer de moteur ni de prix :

* Options : mêmes `optionType` et `option_type`, strike, spot/forward,
  maturité exacte, taux/carry/volatilité ; payoff call/put et titre issus de
  ces valeurs. Moneyness ITM/ATM/OTM fondée sur spot pour BSM/GK, forward pour
  Black-76, sans présumer que le strike par défaut est ATM.
* Swap : payer/receiver, coupon, devise et horizon issus du ticket validé,
  avec le bon sens du payoff. CDS : prime fixe, recovery et horizon réels.
  Autocall : coupon, barrières, fréquence et calendrier effectifs, sans
  réutiliser des termes de la configuration par défaut.
* `product_spec.inputs` est une copie identique des inputs du calcul ;
  `product_spec.contract_summary` et `pricing_result.contract_summary` sont
  identiques. Les champs existants restent présents. Les textes Sales et
  Structurer sont alignés sur ce contrat final pour éviter une ancienne
  étiquette dans une carte d’agent ou le rapport.

Le reproducer Business affiche maintenant
`BTC/USD European Put - K 21000, 0.25Y, ITM by spot`, strike 21000 et prix
**inchangé** 3278,027771491523. Un put de strike 19000 sur spot 20000 est
étiqueté OTM, ainsi que les calls OTM contrastés ; FX et commodities ont les
mêmes contrôles. Une maturité non arrondie et des termes swap/CDS/autocall
différents des presets sont également testés.

Validation observée : **123 tests PASS en 27,24 s** sur les six fichiers
ciblés de confiance, registre, interaction, BSM, MC et sécurité, dont onze
nouveaux scénarios de libellés/inputs. Seuls `desk_agents.py` et les tests de
confiance ont été modifiés dans ce dernier sous-cycle ; aucun fichier de
référence pratique gelé, book, frontend ou bloc API n’a été modifié. Le
rapprochement visuel des familles exotiques dans le frontend est pris en
charge par root/frontend et reste distinct de cette preuve backend.
