# Technical RL — intégration et livraison locale

Campagne du 14 novembre, validation finale le 15 novembre 2026. CLI, HTTP et
Chromium headless uniquement ; aucun contrôle du bureau. Les identités, plans,
publications et écritures de recette sont des fixtures isolées, pas des clients.

**Verdict Technical RL : PASS local.** Le dernier build respecte les budgets
mobile inchangés. La vente publique et les fournisseurs externes gardent leurs
gates distincts.

## Corrections réellement livrées

- Les outils supportés calculent réellement. Le registre conserve ses anciens
  descripteurs, mais distingue 73 capacités exécutables de 810 indisponibles
  explicitement. Un descripteur ne renvoie plus un faux succès numérique.
- RFQ : Black-76 sur futures, Monte Carlo GBM borné et seedé sur autocall,
  contrat affiché issu des mêmes entrées que le prix, limites non évaluées
  explicites. Six familles de positions papier conservent unités, quantité et
  propriétaire. Une reprise de la même intention récupère une position unique.
- Dashboard : publication du token avant les requêtes, activité Interview
  projetée depuis les véritables tentatives, reprise précise, catégories de
  compteurs séparées et aucun score de maîtrise inventé.
- Exercices : réponses écrites immuables avant comparaison, auto-revue privée,
  historique et exports. Quatorze références originales calculables exposent
  ticket, conventions, limites, Python autonome et notebook Jupyter valide.
- Survival : banque Core réelle, trente secondes serveur, trois vies, feedback
  conservé jusqu'à Next, reprise sans réinitialisation du temps, score non classé.
- Deux notebooks réels, Python dans un Worker annulable, export local et reprise
  explicite en cas d'échec de CDN. Aucun code arbitraire envoyé au serveur.
- Douze programmes anglais / 108 leçons acceptés après deux revues. Le fichier
  servi doit correspondre au SHA-256 approuvé dans l'index privé. Catalogue et
  lecteur refusent une variante absente, non revue ou modifiée. Les douze
  fichiers français et le corpus source sont inchangés.
- Rapport lisible, CSV, cartes Anki limitées aux cas exposés et calendrier UTC.
  Les téléchargements ne sont pas assimilés à de l'assiduité ou une compétence.

## Tests finaux exécutés

| Commande ou preuve | Résultat et limite |
| --- | --- |
| `python -m pytest -q --basetemp=.pytest_tmp_hardening_release_final --tb=short` | **593 PASS en 197,77 s**, deux avertissements de dépréciation websockets/Uvicorn. Suite entière, après les dernières corrections produit. |
| `python scripts/production_check.py` | **PASS** des contrats locaux auth/RBAC, observabilité, API, cycle de facturation simulé, Starter Kit, imports et modèle Compose. La configuration réelle reste PASS-CLOSED. Aucun Docker démarré ou déploiement exécuté. |
| `python scripts/check_learner_package.py` | **PASS** : wheel installé en préfixe isolé ; vrai `tpl` et `create_app` hors checkout ; 96 commandes, 14 références, 20 questions, 2 notebooks, calcul BS, calibration Node et référence exécutés. Dépendances de l'interpréteur courant réutilisées ; pas de preuve d'installation Linux neuve. |
| `scripts/smoke_published_english_courses.py` | **PASS** sur nouvelle API HTTP et vrais sous-processus CLI : 12 versions EN réelles, droits non-admin, refus anonymes/gratuits, `Content-Language: en`, cache privé. |
| Contenu anglais | Gate strict 98 : 12/12 ; revue indépendante des 108 leçons, 60 QCM et 240 feedbacks V2, 12 oracles ; promotion des seuls hashes approuvés. Les scores automatisés ne mesurent pas une satisfaction de clients. |
| Références pratiques | 14 API calculées et 28 exports Python/Jupyter exécutés hors checkout ; oracles indépendants et revue Business séparée. |
| Frontend intégré | 30 contrôles headless frais, 6 états Axe sans violation détectée ; 14 téléchargements Python exécutés et comparés à l'affichage ; RFQ retry après enregistrement effectif ; Survival jusqu'à fin. Détails dans la revue frontend C2. |
| Identité visuelle | 12 étapes de régression du build de production, Courbe signature/logo/navbar et largeurs 320–1440 px. |
| Dépendances frontend | Audit runtime : zéro vulnérabilité signalée. Les avis de la chaîne de développement restent suivis séparément. |

La première attente du nouveau test `jobs sources` était anonyme à tort : la
politique existante réserve la source à l'opérateur. Le test et la documentation
ont été corrigés ; aucune permission produit n'a été affaiblie. Les anciens
smokes UI de Survival/lecture ont aussi été réalignés sur le nouveau contrat
serveur/langue/reprise, avec les vrais tests de règles conservés séparément.

## CLI et reproductibilité

`tpl coverage` liste 96 commandes nommées ; c'est un inventaire de l'interface,
pas une preuve de toutes les combinaisons d'entrées. Le détail des familles,
permissions, erreurs, reprise et dépendances figure dans
`CLI_FEATURE_COVERAGE.md`. Les commandes, formats et codes de sortie sont dans
le backend `docs/LEARNER_CLI.md`. Le launcher public
`scripts/serve_learner_fixture.py` crée une cohorte loopback explicitement QA,
sans corpus ni fournisseur externe et avec fichier de credentials privé.

Les flux auth CLI signup/login/OTP ou hash de lien/recovery/password/refresh/
logout sont testés avec un fournisseur HTTP de protocole. Une réponse recovery
acceptée n'est jamais décrite comme un email livré. `auth dev-session` choisit
explicitement le compte de développement local ; aucune session admin de
production n'est fabriquée.

## Limites et suites extérieures

La revue indépendante intégrée a trouvé deux ruptures supplémentaires : les
tentatives écrites et réponses Survival en cours n'alimentaient pas le résumé
du dashboard ; une regex de durée interprétait «50 and Nikkei» comme cinquante
ans, faisant échouer une illustration locale RFQ pendant le rendu. Ces constats
ne sont pas cachés par les 593 tests précédents.

Le correctif backend `16e00d577002f0f53df1dce0a5f909da6a881352` ajoute une
projection `learning` en lecture seule. **75 tests ciblés PASS après ce patch**
(learning progress, workflows et Interview) vérifient les propriétaires,
l'ancienne base, les compteurs, les réponses sauvegardées et l'absence d'écriture
sur les scores/événements. Les 593 et75 tests se recoupent : ce n'est pas un total
de 668 tests uniques. Le paquet final a été reconstruit et exécuté hors checkout,
SHA-256 `ff0a2a4e990b1ab6b2a67421cc965320482af988c18532ef8e1044b4e0024551`.

Côté UI, treize contrôles ciblés et quatre états Axe passent après correction.
La reprise respecte une ancienne tentative revue après une plus récente ; une
réponse Survival sauvegardée apparaît au dashboard. Le parseur de durée respecte
les mots entiers, une durée hors domaine est refusée sans clamp et les
illustrations locales ne font plus tomber React. Le refus laisse la requête
modifiable et une nouvelle cotation valide fonctionne sans rechargement. La
revue indépendante a fermé les deux P1 puis testé la vraie vague Survival de
vingt réponses, le rechargement et les trois vies.

Un dernier défaut clavier a été corrigé dans le renderer math commun : seules
les équations qui débordent deviennent des régions défilables focalisables.
Sur la vraie leçon Stochastic EN à320px, Business a testé le focus et le mouvement
ArrowRight des trois équations (40/40/21px), puis le resize390 : Axe0 et aucune
pageerror. Les contenus et équations ne sont pas modifiés.

La performance a d'abord échoué sous contention de l'hôte. Un profil isolé
retrouve FCP2056/LCP4020ms et interaction médiane/pire112/136ms ; il révèle le
chargement en série du shell puis de la route Starter Kit. Le préchargement
de route seul ne suffit pas : le test standard mesure encore LCP4164ms. Le
build ajoute ensuite un `modulepreload` du shell à faible priorité, résolu depuis
les véritables modules Rollup, et conserve l'exécution lazy des outils. Le
contrôle d'artefact confirme que ce lien pointe vers le fichier généré existant.

**Dernier `npm run smoke:performance` original : PASS**, profil Pixel5,
1,6Mbps/750kbps, 150ms RTT, CPU4x ; budgets inchangés. FCP **2244ms** (≤2500),
LCP **3516ms** (≤4000), CLS **0,01675** (≤0,1), trois interactions de 56/120/136ms
(médiane≤300 et pire≤400), aucune pageerror. Preuve :
`frontend/cycle2/performance-final-prefetch.log`. Les premiers FAIL restent
conservés, y compris le diagnostic supplémentaire interrompu par un timeout
réseau ; ils ne sont pas transformés en succès. La quantité totale de code
n'est pas présentée comme réduite : le gain vient de l'ordre de chargement.
Build final 17,79s, plus gros chunk 437077B≤500000 ; typecheck/budget PASS.
La phrase du fallback global prétendant une notification d'équipe a aussi été
remplacée par une instruction de rechargement honnête.

La validation indépendante du parcours intégré est distincte de ce verdict
technique. La facturation réelle, les emails Supabase, les droits commerciaux
des sources, la configuration légale/support, le déploiement et les retours
d'étudiants réels doivent encore apporter leurs propres preuves. Le checkout
public reste fermé. Le carnet papier est en mémoire de processus et n'annonce
ni persistance multiworker, ni exécution broker, ni modèle calibré de marché.

Le code backend testé est poussé au commit
`27ce8df45136625ee57f718bc1a07702eabd7792`. Les fichiers de cours privés,
corpus, bases, credentials, captures et logs bruts restent hors Git. La
vérification des 63 fichiers source indexés avant ce commit n'a trouvé aucun
secret à haute confiance ou token de session littéral non public.

La dernière projection est au commit backend `16e00d577002f0f53df1dce0a5f909da6a881352`
et le frontend testé au commit `724c2b5fc440b14c75c12028812146c06457e86f`, tous
deux poussés. Les 53 fichiers frontend indexés ont également passé le contrôle
de secrets/token littéral avant publication. Audit npm final : runtime 0 ; arbre
complet 11 modérées de développement, 0 élevée/critique. L'alerte GitHub au push
porte sur 98 vulnérabilités de la branche par défaut, qui n'a pas été fusionnée
ou déployée dans cette intervention.

Le produit local `http://127.0.0.1:5173` a également été rechargé avec le nouveau
backend, sans redémarrer Vite ou réinitialiser les données : compte administrateur
de développement/Pro vérifié par la vraie CLI, catalogue douze EN/FR et lecture
anglaise privée effectivement téléchargée. Aucun navigateur du bureau contrôlé.
Un dernier appel CLI `courses progress` confirme que ce runtime utilisateur
charge aussi `tpl.learning.progress.v1` après le dernier correctif, avec les
blocs Interview et historique conservés. Les cohortes supplémentaires de QA ont
été arrêtées sans effacer leurs enregistrements ; le produit local reste actif.

Le contrôle automatique a refusé le nettoyage d'un ancien répertoire temporaire
de smoke (« blocked by policy »). Le dossier reste local et ignoré par Git ;
aucun contournement ni suppression alternative n'a été tenté après ce refus.
