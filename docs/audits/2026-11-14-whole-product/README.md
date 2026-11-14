> Copie publique expurgée du rapport local du 14 novembre 2026. Les preuves brutes, captures de cours, bases, corpus et identifiants de test restent locaux. Cette copie ne livre pas un nouveau CLI ni une correction produit.

# ThePricingLibrary — audit utilisateur, fonctionnel et commercial

Audit du 14 novembre 2026. Cible : étudiants en master finance anglophones préparant des entretiens de dérivés en banque. **Travail réalisé uniquement en CLI, API et Chromium sans fenêtre ; aucune prise de contrôle du bureau.**

**Le produit possède un cœur utile et réellement exécutable, mais je ne recommande pas de commercialiser aujourd’hui l’ensemble du SaaS sous sa promesse actuelle.** Les calculateurs, l’entraînement Interview et plusieurs fonctions de sauvegarde sont réels. Des fonctions agentiques annoncent cependant des calculs qu’elles ne réalisent pas, le parcours de progression est fragmenté et le produit complet n’est pas utilisable par une CLI utilisateur uniforme.

La décision proposée est de **fiabiliser et vendre un parcours précis de préparation pratique**, puis d’étendre l’offre à partir d’usages mesurés. Ajouter des écrans, des agents ou des connecteurs avant de traiter ces écarts affaiblirait la confiance au centre du positionnement.

## Ce que cet audit prouve

| Contrôle | Portée réellement exécutée | Limite |
| --- | --- | --- |
| Navigation | 175 vues, 77 chemins distincts, douze cours, neuf outils et six cas Interview ; desktop et échantillon mobile | Cinq chemins sont volontairement inexistants. Ce n’est pas l’exécution de toutes les combinaisons ou de tous les états. |
| Usage technique | 22 commandes CLI, 20 commandes de runtime supplémentaires, vrai transport MCP sur stdin/stdout | Ce sont en grande partie des commandes d’opérateur ; leur succès technique ne valide pas les chiffres retournés. |
| API métier | 61 requêtes de parcours et huit requêtes de capacités, identités signées et plans différenciés | Serveur isolé, droits de test ; pas de clients payants ou d’authentification Supabase externe réelle. |
| Mathématiques | Neuf moteurs, dix calculs, sept exports CSV techniques ; neuf outils exécutés avec neuf exports JSON dans l’interface headless | Recette représentative, pas certification de tous les modèles, conventions et extrêmes. |
| Accessibilité | Axe sur 175 contenus `main`, sept documents entiers et essais ciblés de clavier DOM | Pas de certification WCAG, de lecteur d’écran natif ou de recherche auprès de personnes handicapées. |
| Livrables | ZIP Starter Kit réel vérifié et livré à un compte doté d’un droit de test ; exports personnels inspectés | Aucun achat, paiement ou droit de redistribution commerciale validé par ce test. |

Les écritures d’audit vont dans une base séparée. Le corpus original est lu en lecture seule. Les appels sortants du serveur sont bloqués ; le backtest utilise un CSV local et un moteur de simulation inspecté. Aucune transaction financière, publication extérieure, candidature envoyée, réservation ou prise de contact n’a été réalisée.

Les deux rôles du protocole sont séparés : [validation technique](technical.md) et [client mystère](business.md). La [revue des pages et de l’accessibilité](frontend.md) et l’[étude des intégrations](integrations.md) complètent leurs constats. La note antérieure de **94,25 concernait le pilote Interview et ses corrections locales ; elle ne vaut pas validation de toute la plateforme**.

## Ce qui fonctionne et mérite d’être conservé

**La boucle Interview est le meilleur point de départ commercial.** Un cas borné conserve les conventions, demande une réponse avant le corrigé, vérifie les nombres, sépare le raisonnement auto-évalué et propose une variante. La reprise et l’export privés fonctionnent dans la recette. Cela fournit une trace de travail, sans prétendre mesurer une compétence certifiée, remplacer un correcteur humain ou garantir une embauche.

**Les neuf calculateurs constituent de vrais actifs.** Black-Scholes, payoff, Monte Carlo, volatilité réalisée, calibration, arbre binomial, obligation, courbe et surface de volatilité exécutent des calculs et produisent des fichiers. Leurs résultats ne doivent pas être confondus avec les réponses fictives du registre d’agents. La valeur pour un étudiant vient du problème résolu et de l’explication, pas du nombre d’outils affichés.

**Les exercices générés et la persistance ne sont pas une simple maquette.** Un exercice anglais a été produit, enregistré, relu et protégé contre un autre propriétaire. Le chemin RAG a réellement récupéré huit sources dans le corpus local, puis utilisé le mode template déclaré. Aucun fournisseur LLM externe n’a été certifié pendant cet audit. Un exercice générique fournit encore essentiellement un énoncé, un barème et un corrigé ; il ne possède pas toute la boucle de tentative/évaluation du Lab.

**Plusieurs fonctions annexes sont effectives.** La position de lecture des cours persiste, le forum conserve des contributions de test et un vote répété reste idempotent. Le backtest local a exécuté 2 000 barres et produit deux trades simulés avec une perte de 94,91 USD : l’exécution existe, sans preuve d’efficacité de la stratégie. Le Starter Kit est un véritable artefact. La vente désactivée est un état volontaire, cohérent avec les prérequis non validés.

## Les problèmes à traiter en priorité

| Priorité | Constat reproduit | Effet pour l’utilisateur et décision proposée | Critère de correction |
| --- | --- | --- | --- |
| **P0 — confiance** | Le registre/MCP retourne **3,45** pour deux tickets dont les vrais prix BSM sont **10,450575** et **114,877191**, avec un statut réussi sans avertissement. Des valeurs de qualité/risque sont également constantes. | La promesse « chiffres calculés et vérifiés » devient fausse sur ce chemin. Le registre est opérateur seulement ; les neuf outils étudiants suivent d’autres moteurs. Bloquer ces faux succès ou les relier réellement aux moteurs. | Deux tickets contrastés donnent les résultats des moteurs, erreurs et limites incluses ; toute capacité absente retourne une indisponibilité explicite. |
| **P0 — confiance** | Le RFQ Exotics annonce un Monte Carlo local-stochastique, smile calibré et 20 000 trajectoires ; le code renvoie une formule arithmétique constante. Deux maturités donnent **102,21 % du pair**, avec mauvais sous-jacent dans le ticket retourné. | Un étudiant apprend une fausse attribution de méthode. Corriger l’exécution, ou présenter une illustration arithmétique exactement nommée. | Modèle, sous-jacent, maturité, paramètres, prix et sensibilités concordent ; preuve indépendante sur des cas différents. |
| **P0/P1 — méthode** | Le RFQ WTI annonce Black-76, mais appelle un BSM spot : **3,85** retourné contre **2,965277** en Black-76 avec ses propres inputs. Des statuts de risque/approbation sont fixes. | La méthode et l’interprétation ne sont pas fiables. Garder distincts prix réellement calculés et hypothèses de démonstration. | Convention future/spot vérifiée et même résultat à l’oracle ; aucun badge de contrôle réel sans données et règle correspondantes. |
| **P1 — activation** | L’assistant hors ligne remplace un ticket explicite S125/K110 par S100/K100, change taux, volatilité et échéance, puis répond en français à une demande anglaise. | L’aide détruit le contexte du travail et peut faire croire à un succès. Limiter honnêtement ce mode ou conserver le ticket. | Les paramètres restent identiques de la demande au calcul/export ; aucun changement silencieux ; langue respectée. |
| **P1 — continuité** | Le dashboard peut envoyer sa première requête sans Bearer et afficher une erreur ; un retry réussit. Après un vrai exercice du Lab, il dit encore **« No activity recorded yet »**. | L’utilisateur croit perdre son travail. Le Lab et l’ancien tableau de progression écrivent dans des registres distincts. | Accès direct, reload et navigation SPA fonctionnent dès que la session est prête ; le dashboard reprend le vrai prochain travail sans confondre lecture, tentative et maîtrise. |
| **P1 — pédagogie et langue** | Les douze cours restent principalement français ; la génération CLI de cours ignore `--language en`. Plusieurs quiz réutilisent un schéma de réponses prévisible. | Le parcours anglophone se rompt et la note d’un quiz renseigne mal la compréhension. | Offre et langue explicites ; cas et distracteurs relus ; variantes inédites ; feedback relié au raisonnement, pas seulement à une clé de réponse. |
| **P1 — accessibilité** | Contrastes insuffisants dans 117 vues, champs sans nom dans Payoff, Backtest et Credit, combobox sans nom dans Calibration. | Des actions essentielles deviennent difficiles à lire ou à identifier. | Rejouer les formulaires nommés, les contrastes des états actifs et la navigation clavier ; compléter par une vraie revue d’accessibilité. |
| **P1 — contrat CLI** | Six moteurs ont une CLI native ; les autres utilisent des fonctions Python/Node. De nombreux parcours nécessitent des appels HTTP et des harness d’audit. | **« Tout le produit est utilisable via un CLI livré » n’est pas vrai aujourd’hui.** Le fait de pouvoir tester en console ne suffit pas. | Une CLI de candidat signée couvre au minimum tâche → réponse → correction → reprise → export, puis cours/exercices/outils, avec erreurs et résultats structurés. |
| **P2 — finition et continuité** | Le titre d’onglet peut annoncer un cas impossible à ouvrir alors que la tâche est affichée. Certains départs vers une pratique annexe ne transportent pas le travail demandé. | Orientation confuse et temps perdu, malgré un rendu sans crash. | Titre stable après chargement ; chaque lien de pratique ouvre le bon cas avec ses hypothèses, ou dit clairement la limite. |

Les preuves et chemins de code sont dans le rapport technique. La revue Business distingue les ruptures vécues des hypothèses de préférence. Les corrections ci-dessus sont **proposées**, pas réalisées pendant cet audit.

## Couverture du produit et de ses limites

| Domaine | État observé | Décision commerciale |
| --- | --- | --- |
| Accueil, navigation, Practice Hub | Rendu et destinations inspectés ; premier calcul gratuit accessible ; menu mobile utilisable dans le test clavier | Conserver la DA ; orienter la première action vers un résultat concret pour un candidat. |
| Interview Lab, six cas | Parcours représentatif, réponses/reprise/export réellement exécutés | Meilleure base pour un pilote ciblé ; ne pas vendre comme entretien complet ou certification. |
| Cours, douze références | Pages et scripts privés ouverts, accès par plan appliqué, progression persistante | Le contenu français et la qualité des quiz nécessitent une décision explicite pour l’offre anglophone. |
| Calculateurs, neuf références | Neuf exécutions et exports réels, plus oracles techniques | Les relier aux cas et conserver conventions/limites dans les fichiers. |
| Exercices | RAG/template, génération anglaise, stockage et isolement joués | Distinguer document corrigé et entraînement évalué ; le second contrat n’est pas général aujourd’hui. |
| Trading Lab et backtest | Pages/scénarios inspectés ; backtest natif borné réellement exécuté | Présenter comme recherche sur données locales ; pas de promesse de trading rentable ou connecté. |
| Survival / leaderboard | Règles visibles, quiz et score de test ; score non classé, classement vide | Entraînement secondaire ; ne pas en tirer un classement vérifié ou une maîtrise certifiée. |
| Notebooks | Un lab Python navigateur ; Run a échoué au chargement CDN dans la recette Business, malgré les GET autorisés | Exécution Python non vérifiée ici ; pas de conclusion de panne universelle. Sauvegarde et partage absents, annoncés. |
| Communauté, projets, publications | Forum réel dans la base de test ; espaces voisins inspectés | Aucune communauté active démontrée ; ne pas vendre un effet de réseau inexistant. |
| Agents, RFQ, MCP, runtime | Transports et contrats exécutés ; écarts financiers critiques ci-dessus | Retirer de la promesse vérifiée les chemins non fiables jusqu’à correction. |
| Blog, jobs, mentoring | API de contenu et candidature de test ; états vides inspectés ; réservation humaine non prouvée | Valeur annexe conditionnée à une offre réelle, actualisée et opérée. |
| Auth, compte et administration | Formulaires et rôles inspectés ; vrais refus attendus sur API isolée | Inscription/email/reset externes et gestion de compte publique restent à valider. |
| Plans, paiement, Starter Kit | Preview et refus de checkout attendus ; vrai bundle livré avec droit fixture | Vente publique non validée : paiement, droits, juridique et support doivent être clos séparément. |
| Légal, contact, retours et erreurs | Pages et états de retour accessibles | Leur présence ne vaut pas validation juridique ou service opérationnel. |

La [matrice des chemins](route-coverage.md) et la matrice de plus de trente fonctions du [rapport technique](technical.md) rendent cette couverture vérifiable. Une famille parcourue n’est pas réputée validée dans tous ses états.

## Adoption, utilité et offre proposée

Un candidat ne cherche pas d’abord une plateforme financière complète : l’hypothèse à éprouver est qu’il veut résoudre un ticket, expliquer ses choix et savoir quoi retravailler avant son entretien. Le produit possède des éléments pour cela, mais demande encore de naviguer entre cours, outils, exercices, Lab et dashboard sans dossier de travail commun.

Je propose comme entrée principale **« Pricing & Greeks interview practice »**, avec une séance courte et une suite claire : reprendre → résoudre → expliquer → vérifier → travailler une erreur → réussir une variante. Le catalogue, les outils et les cours deviennent des ressources de cette séance. Les espaces de recherche et de communauté restent accessibles selon l’offre réelle ; leur présence seule ne justifie pas un abonnement.

L’avantage potentiel est l’association d’un ticket, d’un calcul reproductible, d’une réponse conservée, d’un raisonnement et d’une variante. **Sa supériorité face aux cours, notebooks et assistants existants n’est pas démontrée.** L’étude stratégique précédente (preuve locale : `reports/strategy-2026-11-14/strategy-report.md`) reste une base de comparaison ; l’audit présent apporte des preuves supplémentaires sur les parcours et leurs limites.

Tester une offre bornée de préparation avant de multiplier les abonnements : périmètre de compétences, cas et variantes inclus, langue, durée d’accès, modes de feedback et support réellement disponibles. Les prix actuels 9/19/49 EUR sont une grille de preview, pas une validation de volonté de payer. Ni le contenu complet, ni la correction humaine, ni l’ensemble du SaaS ne doivent être promis par défaut dans un pilote de six cas.

## Intégrations utiles dans l’écosystème de l’étudiant

La [recherche détaillée](integrations.md) vérifie dix-huit sources officielles et sépare capacité technique et demande client. Elle recommande cet ordre :

| Étape | Intégration proposée | Valeur à tester et état actuel |
| --- | --- | --- |
| 1 | **Même ticket vers Excel / Python / Jupyter** | Les CSV/JSON et les vrais moteurs existent. Fournir entrées, conventions et contrôle reproductible ; ce n’est pas encore un add-in Excel, un SDK publié ou un export notebook du Lab. |
| 1 | **Lien vers le cas et compte rendu privé lisible** | Retour au bon travail et trace partageable volontairement. Le JSON privé existe ; PDF/rapport humain et partage signé révocable restent à concevoir. |
| 2 | **Petit export Anki** | Réviser ses erreurs conceptuelles, puis revenir à une variante. Absent aujourd’hui ; ne pas importer un faux score de maîtrise. |
| 2 | **Planning iCalendar** | Reprendre une préparation à une date choisie, sans imposer OAuth. Absent aujourd’hui ; un import de calendrier ne prouve pas l’assiduité. |
| 3 | **LTI 1.3 / LMS** | À engager avec enseignant, administrateur et acheteur identifiés. Un vérificateur JWT et un ZIP ne constituent pas une intégration LMS ; identité, classes, droits et éventuelles notes restent à construire. |

Excel peut importer un CSV et Jupyter attend un vrai document notebook ; ces formats permettent un premier transfert sans construire immédiatement une intégration lourde. [Microsoft — import Texte/CSV](https://learn.microsoft.com/en-us/power-query/connectors/text-csv), [Jupyter — format notebook](https://nbformat.readthedocs.io/en/latest/format_description.html). Le lancement LMS répond à un autre contrat d’identité et de contexte. [1EdTech — LTI 1.3](https://www.imsglobal.org/spec/lti/v1p3/).

Le MCP ne doit pas être utilisé comme argument de distribution financière avant de relier ses outils aux vrais moteurs. Les cas anglais originaux et données synthétiques sont les meilleurs candidats au transfert ; la présence d’un document dans le RAG ne donne pas un droit de redistribution.

## Ordre de travail et preuves de sortie

1. **Fermer les P0 de confiance.** Désactiver les faux succès du registre et les méthodes RFQ mal attribuées, ou implémenter réellement le contrat annoncé. Comparer à un oracle indépendant avec tickets contrastés. Cette étape précède toute nouvelle promesse d’intégration.
2. **Unifier la séance et sa reprise.** Stabiliser le transport du jeton, montrer l’activité Interview dans le dossier personnel et conserver le ticket entre cas, outil et export. Corriger noms de champs, contrastes et titres concernés. Rejouer avec un membre non administrateur, un reload et une erreur récupérable.
3. **Livrer le contrat CLI du cœur.** Un client authentifié distinct des commandes opérateur doit rejouer le même parcours et exposer les limites. Les règles Survival et la gestion de notebooks ne deviennent pas CLI-testables par la seule présence d’une page.
4. **Définir une offre anglaise précise et son transfert Excel/Python.** Un seul paquet utile, original et reproductible d’abord ; Anki/calendrier seulement si la friction est observée.
5. **Observer un petit pilote réel avant la vente élargie.** Proposition : huit candidats de la cible, sans privilèges admin, avec un cas initial puis une variante inédite. Observer première action, blocages, raisonnement, retour ultérieur et usage effectif des fichiers. Ce nombre sert à apprendre qualitativement, pas à estimer statistiquement le marché.

Avant le pilote, fixer les règles de décision : tout participant doit pouvoir retrouver sa tentative sans aide de l’équipe ; chaque prix annoncé doit être reproductible ; aucun blocage critique ne doit rester ; les résultats numériques, l’explication auto-déclarée et une éventuelle revue humaine doivent rester séparés. Mesurer les abandons et leurs causes plutôt que présenter les comptes QA comme des utilisateurs acquis.

Pour décider de vendre, recueillir ensuite la valeur exprimée pour une offre précise, un engagement d’achat réel une fois la vente prête, le coût de support et les raisons de refus. Le téléchargement, le nombre de clics et le retour sur deux dates ne prouvent ni apprentissage, ni rétention D7, ni volonté de payer. La faisabilité économique, l’authentification publique, le paiement, les droits et le support restent des validations distinctes.

## Verdict de livraison de cet audit

**Technical RL : FAIL sur la promesse globale de calculs agentiques et de couverture CLI complète. Business Client Mystère : FAIL pour le produit entier, GO conditionnel pour un pilote local limité au Lab et aux calculateurs.** Le score Business de 57/100 est un jugement interne de revue, sans valeur statistique ou validation marché. L’ensemble du SaaS ne reçoit pas un PASS global.

Cet audit livre les observations, les preuves locales et un ordre de correction. **Aucun code produit n’a été modifié pour masquer les défauts pendant la recette.** Les harness et les données signées restent locaux. La synthèse expurgée peut être versionnée ; les jetons, captures de cours privés, corpus et bases de test ne doivent pas être publiés.

Reproduction : [commandes techniques](replay.md), [navigation headless](frontend.md#reproduction-uniquement-en-cli). Les preuves locales sont horodatées ; elles attestent un état du code et de l’environnement, pas la disponibilité de la production publique.
