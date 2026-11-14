> Copie publique expurgée du rapport local du 14 novembre 2026. Les preuves brutes, captures de cours, bases, corpus et identifiants de test restent locaux. Cette copie ne livre pas un nouveau CLI ni une correction produit.

# Audit des pages et de l’accessibilité — 14 novembre 2026

**Les pages se rendent correctement, mais le parcours complet n’est pas prêt à recevoir un verdict d’accessibilité ou de fluidité global.** L’inventaire relève des défauts concrets de contraste, de noms de champs et de titre d’onglet. Le dashboard présente en plus les erreurs de progression reproduites dans la recette Business.

## Méthode et portée

- **175 vues, 77 chemins distincts**, incluant cinq chemins volontairement inexistants : 64 vues visiteur à 1440 px, 77 Pro à 1440 px, huit membre gratuit à 390 px, 25 Pro à 390 px et une opérateur à 1440 px.
- Le corpus des pages couvre les douze cours, les neuf outils, les six cas Interview, les familles Trading Lab/communauté, compte, vente, contenu et administration. Les variantes de données et tous les états d’erreur ne sont pas exhaustifs. Voir [les chemins réellement parcourus](route-coverage.md).
- Vrai frontend local de la branche `codex/2026-11-14-interview-lab`, Chromium `headless:true` lancé par Node en console. Aucun navigateur visible, contrôle Windows, clavier ou souris du bureau.
- Sessions signées de test et droits de plans décidés par le vrai backend isolé. Le transport d’identité Supabase est une fixture déclarée ; aucune inscription, connexion externe, délivrance d’email ou transaction réelle n’est certifiée. Les résultats de calcul ne sont pas substitués par le transport.
- **Axe-core 4.14.0**, tags WCAG A/AA 2.0, 2.1 et 2.2 : contrôle de `main` pour la matrice, puis sept contrôles du document entier. Les répétitions par rôle ou largeur ne constituent pas des défauts indépendants.

## Ce qui fonctionne dans les essais

L’inventaire s’est terminé avec **zéro erreur du harness, zéro `pageerror` JavaScript, un seul `main` et un seul H1 visible par vue**. Aucune image cassée ni aucun débordement horizontal du document n’ont été observés dans les états inspectés. Cela ne démontre pas l’absence d’erreur dans les interactions non exécutées.

Le premier Tab atteint le lien « Skip to content » ; Entrée place le focus dans `main`, sur desktop et mobile. À 390 px, le menu s’ouvre au clavier, garde le focus dans ses commandes au fil de dix-huit Tab, se ferme avec Échap et rend le focus au déclencheur. Ces trois contrôles ciblés sont réussis. Le nom du site et les principales commandes de navigation sont exposés aux technologies d’assistance dans les documents inspectés.

Les refus de plans et d’administration ne sont pas assimilés à des pannes. Le Pro non administrateur voit bien « Access denied » sur `/admin` ; la vue opérateur est inspectée séparément. Les erreurs 404 de l’article fictif sont attendues. En revanche, les 401 du dashboard d’un membre signé sont de vrais constats de recette, repris dans le rapport technique et Business.

## Défauts reproduits

| ID / priorité | Surface et preuve | Conséquence | Correction et critère de recette |
| --- | --- | --- | --- |
| F01 — P1 | Contraste insuffisant dans **117 des 175 vues**, sur 55 chemins, souvent les mêmes boutons. Exemple : texte blanc sur `#ff3654`, ratio **3,55:1**, taille 12,5–13 px. Le pricer utilise aussi environ 3,52:1. | Des actions importantes sont difficiles à lire pour une partie des utilisateurs. | Ajuster les couleurs des états concernés en conservant la DA. Vérifier au moins 4,5:1 pour ce petit texte normal, y compris focus, hover et erreurs ; ne pas retoucher uniquement une page. |
| F02 — P1 | Champs sans nom accessible dans **Payoff**, **Backtest** et le widget **Credit Derivatives**. Axe retrouve quatre vues `label` et trois `select-name`, avec répétitions mobile/desktop. | Le lecteur d’écran ne peut pas annoncer sans ambiguïté la jambe, le paramètre et sa valeur. Un intitulé visuellement proche n’est pas forcément relié au champ. | Lier de vrais labels aux inputs/selects ; ajouter jambe, unité et contexte lorsque nécessaire. Rejouer chaque champ avec son nom accessible et une saisie DOM. |
| F03 — P1 | Deux combobox de **Calibration** sans nom accessible, reproduites desktop et mobile (`button-name`). | Le modèle et le choix de calibrage ne sont pas identifiables au focus. | Relier label et contrôle Radix, exposer la valeur sélectionnée. Recette : deux noms stables, valeurs annoncées et navigation clavier du menu. |
| F04 — P1/P2 | Zone de code défilante dans `/api` et bandeau défilant de `/agent-room` mobile non accessibles au focus (`scrollable-region-focusable`). | Une partie du contenu peut rester hors d’atteinte au clavier. | Rendre le conteneur défilant atteignable et nommé, ou proposer une représentation équivalente. Vérifier le défilement uniquement par clavier DOM. |
| F05 — P2 | `/interview/call-quote` charge le vrai ticket, mais l’onglet reste **« This case could not be opened. »** après plusieurs secondes, desktop et mobile. Le phénomène apparaît aussi sur d’autres cas de la matrice. | Le titre annonce une panne inexistante et rend l’onglet/historique trompeur. | `RouteMetadata` se déconnecte au premier H1 transitoire : fournir des métadonnées de route stables ou les mettre à jour après le vrai chargement. Recette : titre cohérent après accès direct, navigation SPA, retry et reload. |
| F06 — P1 de contenu | Les 175 documents déclarent `lang=en`, alors que certains cours, le Starter Kit et le desk contiennent principalement du français. | Langue de synthèse vocale potentiellement incorrecte et rupture pour la cible anglophone. | Livrer en anglais les parcours vendus à cette cible ; en attendant, déclarer clairement la langue du contenu et marquer les blocs français. La traduction seule ne valide pas le contenu pédagogique. |

Le seuil de contraste ci-dessus correspond au petit texte normal ; les exceptions pour grands caractères et éléments inactifs ne concernent pas les boutons actifs cités. [W3C — contraste minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).

Le chiffre **118 vues avec au moins une violation Axe** ne signifie ni 118 bugs uniques ni un taux global de conformité. Les règles détaillées et les sélecteurs sont conservés dans route-matrix.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/frontend/evidence/route-matrix.json`). Les tests du document entier et le focus sont dans navigation.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/frontend/evidence/navigation.json`).

## Limites explicites

Pas de test avec utilisateur handicapé ou lecteur d’écran natif, pas de validation exhaustive des graphiques, du zoom 400 %, des contrastes de tous les états, des erreurs de formulaires, des alternatives tactiles, des performances réseau réelles ou de la conformité réglementaire. Une largeur de 390 px n’équivaut pas à tous les appareils mobiles. Une commande DOM n’est pas une expérience humaine mesurée.

Un scanner automatise une partie de l’évaluation ; il ne peut déterminer seul l’accessibilité. Les contrôles marqués `incomplete` exigent une revue supplémentaire. [W3C — possibilités et limites des outils d’évaluation](https://www.w3.org/WAI/test-evaluate/tools/selecting/).

## Reproduction uniquement en CLI

Prérequis : serveur frontend local 5173 déjà lancé, cohorte signée 8427 créée suivant le [README technique](replay.md), Playwright du frontend et binaire Chromium disponibles. `cohort-browser.mjs` utilise le vrai AuthContext et la fixture d’identité, sans ajouter un Bearer absent aux requêtes de l’application.

Depuis la racine du workspace :

```powershell
npm install --prefix reports/whole-product-cli-audit-2026-11-14/harness-deps --no-save --package-lock=false axe-core@4.14.0
node reports/whole-product-cli-audit-2026-11-14/frontend/audit-pages.mjs
node reports/whole-product-cli-audit-2026-11-14/frontend/audit-navigation.mjs
```

L’installation ci-dessus ne modifie pas les dépendances produit. Les captures créées par ces scripts restent locales ; elles peuvent montrer des cours privés et ne doivent pas être publiées avec les preuves publiques. Les identités et clés temporaires restent privées. L’inventaire seul est en lecture ; il ne remplace pas les parcours d’écriture de la recette technique et Business.
