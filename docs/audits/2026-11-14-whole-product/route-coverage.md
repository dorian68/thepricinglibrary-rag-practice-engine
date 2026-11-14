> Copie publique expurgée du rapport local du 14 novembre 2026. Les preuves brutes, captures de cours, bases, corpus et identifiants de test restent locaux. Cette copie ne livre pas un nouveau CLI ni une correction produit.

# Chemins réellement parcourus en console headless

77 chemins distincts ; 175 vues. Un rendu ne prouve pas une action métier. Les accès restreints attendus restent distingués des fonctions exécutées dans les autres rapports. Les cinq chemins fictifs testent la récupération et ne sont pas des pages commerciales supplémentaires.

| Chemin | Visiteur 1440 | Pro 1440 | Gratuit 390 | Pro 390 | Opérateur 1440 | Règles Axe observées |
| --- | --- | --- | --- | --- | --- | --- |
| `/` | rendered | rendered | — | rendered | — | color-contrast |
| `/about` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/admin` | access-gate | rendered | — | rendered | rendered | color-contrast |
| `/agent-room` | access-gate | rendered | — | rendered | — | color-contrast, scrollable-region-focusable |
| `/api` | access-gate | rendered | — | — | — | color-contrast, scrollable-region-focusable |
| `/auth/forgot-password` | rendered | rendered | — | — | — | color-contrast |
| `/auth/login` | rendered | rendered | — | — | — | color-contrast |
| `/auth/reset-password` | rendered | rendered | — | — | — | color-contrast |
| `/auth/signup` | rendered | rendered | — | — | — | color-contrast |
| `/billing/cancel` | rendered | rendered | — | — | — | color-contrast |
| `/billing/success` | rendered | rendered | — | — | — | color-contrast |
| `/blog` | rendered | rendered | — | — | — | color-contrast |
| `/blog/not-an-article` | availability-or-empty-state | availability-or-empty-state | — | — | — | Aucune détectée dans cet état |
| `/bug` | rendered | rendered | — | — | — | color-contrast |
| `/cancel` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/challenge` | availability-or-empty-state | availability-or-empty-state | — | availability-or-empty-state | — | color-contrast |
| `/community` | access-gate | rendered | — | — | — | color-contrast |
| `/community/forum` | access-gate | rendered | — | rendered | — | color-contrast |
| `/community/projects` | access-gate | availability-or-empty-state | — | — | — | color-contrast |
| `/community/publications` | access-gate | availability-or-empty-state | — | — | — | color-contrast |
| `/contact` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/courses` | rendered | rendered | — | rendered | — | Aucune détectée dans cet état |
| `/courses/black-scholes` | access-gate | rendered | — | rendered | — | color-contrast |
| `/courses/credit-derivatives` | — | rendered | — | — | — | color-contrast, label |
| `/courses/exotics` | access-gate | rendered | — | — | — | color-contrast |
| `/courses/fixed-income-bonds` | — | rendered | — | — | — | color-contrast |
| `/courses/greeks` | — | rendered | access-gate | rendered | — | color-contrast |
| `/courses/implied-vol` | access-gate | rendered | — | — | — | color-contrast |
| `/courses/market-risk-var` | — | rendered | — | — | — | color-contrast |
| `/courses/monte-carlo` | — | rendered | — | — | — | color-contrast |
| `/courses/not-a-course` | availability-or-empty-state | availability-or-empty-state | — | — | — | color-contrast |
| `/courses/rates-swaps` | — | rendered | — | — | — | color-contrast |
| `/courses/stochastic` | — | rendered | — | — | — | color-contrast |
| `/courses/structured-products` | — | rendered | — | — | — | color-contrast |
| `/courses/yield-curves` | access-gate | rendered | — | — | — | color-contrast |
| `/dashboard` | rendered | rendered | rendered | rendered | — | color-contrast |
| `/exercises` | access-gate | rendered | access-gate | rendered | — | color-contrast |
| `/exercises/not-an-exercise` | access-gate | availability-or-empty-state | — | — | — | color-contrast |
| `/interview` | rendered | rendered | rendered | rendered | — | color-contrast |
| `/interview/call-quote` | rendered | rendered | rendered | rendered | — | color-contrast |
| `/interview/delta-hedge` | — | rendered | — | — | — | Aucune détectée dans cet état |
| `/interview/dividend-parity` | — | rendered | rendered | — | — | Aucune détectée dans cet état |
| `/interview/gamma-vega` | — | rendered | — | — | — | Aucune détectée dans cet état |
| `/interview/quote-memo` | — | rendered | — | — | — | Aucune détectée dans cet état |
| `/interview/time-rates` | — | rendered | — | — | — | Aucune détectée dans cet état |
| `/jobs` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/lab` | access-gate | rendered | — | — | — | color-contrast |
| `/lab/backtest` | access-gate | rendered | — | — | — | color-contrast, label, select-name |
| `/lab/performance` | access-gate | rendered | — | — | — | color-contrast |
| `/lab/scenarios` | access-gate | rendered | — | — | — | color-contrast |
| `/lab/strategies` | access-gate | rendered | — | — | — | color-contrast |
| `/leaderboard` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/legal` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/mentoring` | rendered | rendered | — | — | — | color-contrast |
| `/not-a-page` | availability-or-empty-state | availability-or-empty-state | — | — | — | color-contrast |
| `/notebooks` | access-gate | rendered | — | rendered | — | color-contrast |
| `/practice` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/pricing` | rendered | rendered | rendered | rendered | — | color-contrast |
| `/privacy` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/refund` | availability-or-empty-state | availability-or-empty-state | — | — | — | Aucune détectée dans cet état |
| `/starter-kit` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/starter-kit/cancel` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/starter-kit/success` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/survival` | access-gate | availability-or-empty-state | — | — | — | color-contrast |
| `/survival/core` | access-gate | rendered | — | rendered | — | color-contrast |
| `/terms` | rendered | rendered | — | — | — | Aucune détectée dans cet état |
| `/tools` | rendered | rendered | — | rendered | — | Aucune détectée dans cet état |
| `/tools/binomial` | access-gate | rendered | — | rendered | — | color-contrast |
| `/tools/bond` | access-gate | rendered | — | rendered | — | color-contrast |
| `/tools/bs-pricer` | rendered | rendered | — | rendered | — | color-contrast |
| `/tools/calib` | access-gate | rendered | — | rendered | — | button-name, color-contrast |
| `/tools/curve` | access-gate | rendered | — | rendered | — | color-contrast |
| `/tools/iv-calc` | access-gate | rendered | — | rendered | — | color-contrast |
| `/tools/mc` | access-gate | rendered | access-gate | rendered | — | color-contrast |
| `/tools/not-a-tool` | availability-or-empty-state | availability-or-empty-state | — | — | — | Aucune détectée dans cet état |
| `/tools/payoff` | access-gate | rendered | — | rendered | — | color-contrast, label, select-name |
| `/tools/volsurface` | access-gate | rendered | — | rendered | — | color-contrast |

Le libellé de surface vient d’une heuristique de texte et sert à retrouver la preuve. Il ne remplace pas un verdict fonctionnel ou commercial. Les règles sont des occurrences agrégées entre états. Preuves détaillées : route-matrix.json (preuve locale : `reports/whole-product-cli-audit-2026-11-14/frontend/evidence/route-matrix.json`).
