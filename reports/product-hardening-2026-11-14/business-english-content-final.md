# Business indépendant — acceptation des douze cours anglais V2

15 novembre 2026, suite de la campagne du 14 novembre.

**PASS local de contenu pour les 12 artefacts V2 exacts.** L'approbation de promotion est enregistrée dans [english-business-approval.json](english-business-approval.json), au format demandé : verdict, rôle indépendant et12 couples slug/SHA-256. Aucun cours n'a été copié ou publié par l'agent Business ; le rôle technique peut utiliser ce reçu pour sa promotion contrôlée.

Cette acceptation remplace le refus de la première série décrit dans business-english-content-initial.md (`business-english-content-initial.md` ; preuve locale non publiee), pour les nouveaux hashes seulement. Elle ne vaut ni PASS du produit entier, ni validation du rendu/parcours UI, de la vente, des droits commerciaux ou des fournisseurs externes. Les 14 références pratiques ont leur [recette indépendante distincte](business-practice-references.md).

## Ce qui a été lu et vérifié

Les 12 sujets et leurs108 leçons ont été examinés : vanilla, Greeks/P&L, swaps, courbes, obligations, IV/smile, Monte Carlo, calcul stochastique, barrières, CDS, autocall et VaR/stress. Les concepts, équations, arguments, conventions, erreurs fréquentes, corrections et limites sont réellement anglais et propres à leur sujet. Les60 questions principales avec leurs5 options et positions variées ont été lues ; les **240 explications V2 effectivement attachées aux choix dans les candidats** ont ensuite été relues, pas seulement le module générateur.

Les nouvelles justifications ciblent maintenant les erreurs : annuité versus DV01, pourcentage versus décimal, prime versus payoff, drift physique versus pricing, demi-gamma, monitoring, mémoire, capital versus profit, quantile versus perte maximale. L'ancien feedback hors sujet sur l'annuité Q2B est fermé ; la rotation des positions n'a pas déplacé la justification vers un autre choix. Aucun fallback “The alternative does not follow from that mechanism” ne reste dans ces quiz.

La comparaison avec les originaux privés figés confirme, pour chaque cours, que théorie, exemples, méthodes et limites n'ont pas changé après la seule traduction du label `frequence=annuelle` en `frequency=annual`. Les questions, options et bonnes réponses sont inchangées. Les valeurs numériques du pack sont identiques. Les titres de références n'ont plus la parenthèse orpheline du nettoyage PDFDrive. Les citations courtes peuvent être complètes ; les coupures sont maintenant signalées par une ellipse.

Preuve : delta V2 avec chaque hash (`business/english-v2-delta-checks.json` ; preuve locale non publiee). Une première expression du harness avait traversé une citation pour détecter à tort une parenthèse dans un titre ; le contrôle porte désormais sur les titres effectivement délimités. Cela ne concernait pas un défaut de contenu.

## Niveau, mathématiques et provenance

Pour un master/candidat possédant les prérequis annoncés, les cours fournissent un support structuré et cohérent pour expliquer une décision de pricing/risque. Le niveau pratique retient les bonnes conventions et frontières : annuités figées versus full repricing, carry, mesure, unités des Greeks, erreurs Monte Carlo, barrière conditionnelle et logique d'événements. L'exposition concise ne remplace pas toutes les démonstrations d'un manuel complet ; elle ne prétend pas couvrir tout entretien ou certifier une compétence.

Les contrôles numériques indépendants ont été rejoués sur les 12tickets V2 : CDF normale et parité, P&L signé, swap DV01, système linéaire de courbe, duration, bisection IV, valeur analytique/largeur d'IC Monte Carlo, payoff FX conditionnel, cash-flows CDS/autocall et quantile/ES gaussiens. Les résultats concordent à l'arrondi et aux approximations déclarées. Le contrôle Monte Carlo de ce cours compare notamment le benchmark et l'intervalle ; il ne reconstruit pas tous ses tirages pseudorandom. Preuves numériques V2 (`business/course-numerical-oracles-v2.json` ; preuve locale non publiee).

Les **569 entrées de source ledger** et **28 citations publiques** ont été recontrôlées sur le corpus original en SQLite lecture seule. Les citations correspondent à des passages contigus sous la normalisation OCR déclarée : typographie, ligatures, diacritiques, coupures, ponctuation et espaces. Les hashes sont ceux du snippet complet, pas de son aperçu de 12 mots. Pas de citation inventée trouvée dans ce contrôle. Taille/mtime du corpus inchangés ; **12 hashes FR inchangés**. Preuves de provenance V2 (`business/english-provenance-checks-v2.json` ; preuve locale non publiee).

Le gate strict a été **réellement relancé en CLI avec seuil 98**, sans abaisser ses règles :12/12 PASS. Résultat du gate indépendant (`business/english-strict-gate-v2.json` ; preuve locale non publiee). Les scores automatisés “student 100/junior 99” demeurent des heuristiques de l'artefact ; ils ne représentent ni étudiants observés, ni satisfaction, ni preuve d'apprentissage ou de PMF. Aucun score humain artificiel n'a été construit pour les faire passer.

## Réserves non bloquantes et suite

Le cadre contrat/unités/contrôle/memo revient souvent entre les cours. Il apporte une méthode commune, mais une édition plus concise ou des renvois pourraient réduire la fatigue. Cette recommandation ne repose pas sur un quota de mots ou un objectif de score.

Un détail de bibliographie reste à polir dans un futur candidat : la citation du cours courbe tirée d'Analytical Finance Volume II commence par `gorithms.` avant le passage “Best-fit”. Il s'agit bien d'un fragment de chunk source retrouvé, pas d'une invention ; ce résidu P2 n'affecte ni les calculs ni le sens du passage suivant. Ne pas modifier discrètement les fichiers déjà approuvés : tout changement exige un nouveau hash et une nouvelle acceptation ciblée.

La version autocall du cours utilise 6 % par observation avec mémoire ; l'exercice pratique historique utilise 8 % annuels trimestriels sans mémoire. Les deux tickets sont explicitement différents. La future UI devra garder ces termes visibles et ne pas fusionner leurs chiffres comme s'il s'agissait d'un même contrat.

**Prochaine recette indépendante :** vérifier les variantes réellement publiées et servies sous droits, la continuité cours→outil→tentative→correction→reprise, les références et exports au clic, Survival serveur complet et RFQ affichant le contrat réellement calculé. Auth/email réelle, Stripe, support, droits et déploiement restent des preuves externes distinctes. Les copies privées et extraits de lecture ne doivent pas être publiés.
