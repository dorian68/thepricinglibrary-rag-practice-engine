"""Reusable, source-honest pedagogical building blocks for rich courses.

These produce the parts a real lesson needs but that raw retrieval cannot give:
solved numerical examples (computed by the deterministic calculators, so the
numbers are correct), corrected exercises, MCQ quizzes, prerequisites, and a
provenance legend. Everything generated here is explicitly labelled
"genere a partir des concepts" so it is never passed off as extracted source
text — the anti-hallucination contract is structural, not just a prompt line.
"""

from __future__ import annotations

import re

from .calculators import PracticeCalculator

PROVENANCE_LEGEND = (
    "> Legende de provenance du contenu:\n"
    "> - **[extrait]** texte issu directement des sources RAG (marque [Sx]).\n"
    "> - **[reformule]** reecriture pedagogique d'un passage source.\n"
    "> - **[genere]** exemple/exercice/quiz construit a partir des concepts; "
    "calculs verifies par le moteur deterministe, non extraits d'une source."
)


# --- topic routing ---------------------------------------------------------

def detect_topic_key(topic: str, product: str | None, concepts: list[str] | None) -> str:
    focus = f"{topic} {product or ''} {' '.join(concepts or [])}".lower()

    def has(*terms: str) -> bool:
        return any(t in focus for t in terms)

    def word(t: str) -> bool:
        return re.search(rf"\b{re.escape(t)}\b", focus) is not None

    # Order matters: check SPECIFIC topics before generic ones whose keyword is a
    # substring of theirs (e.g. "par swaps" contains "swap"; "vanilla call" contains
    # "vanilla"). vol_smile must NOT key on bare "vol" (matches "volatility").
    if has("smile", "skew", "implied vol", "implied volatility", "svi", "sabr", "local vol", "sticky"):
        return "vol_smile"
    if has("autocall", "athena", "phoenix", "snowball", "structured", "term sheet"):
        return "autocall"
    if has("barrier", "barriere", "knock", "one-touch", "one touch"):
        return "barrier"
    if has("monte carlo", "monte-carlo", "gbm", "asian", "variance reduction"):
        return "monte_carlo"
    if has("yield curve", "bootstrap", "discount factor", "zero curve", "forward rate", "ois"):
        return "yield_curve"
    if has("swap", "dv01", "par rate"):
        return "swap"
    if has("bond", "duration", "convexity", "ytm"):
        return "bond"
    if has("cds", "credit default", "cs01", "hazard rate", "protection buyer", "protection seller") or (has("credit") and has("spread", "default", "protection")):
        return "cds"
    if has("stochastic", "risk-neutral", "girsanov", "feynman") or word("ito") or word("sde"):
        return "stochastic"
    if word("var") or has("value at risk", "stress", "expected shortfall"):
        return "var"
    if has("greek", "delta", "gamma", "vega", "theta"):
        return "greeks"
    if has("vanilla", "black-scholes", "black scholes", "put-call", "put call"):
        return "vanilla_bs"
    return "generic"


# --- solved numerical examples (calculator-backed) -------------------------
# Each seed is a sentence the deterministic calculator can parse into a fully
# worked answer key (formula -> substitution -> result -> desk reading).
_WORKED_SEEDS: dict[str, tuple[str, str, str]] = {
    "vanilla_bs": (
        "vanilla_option_black_scholes",
        "Call vanilla spot 100 strike 100 vol 20% maturite 1 taux 5%.",
        "On price un call europeen a la monnaie et on lit prix, d1, d2 et greeks.",
    ),
    "greeks": (
        "options_book_greeks",
        "Book delta +250k EUR par 1%, gamma -80k EUR par 1%^2, vega +120k EUR par "
        "vol point, theta -15k EUR par jour. Scenario spot -2%, vol +3.",
        "On attribue le P&L intraday d'un book d'options par facteur de risque.",
    ),
    "swap": (
        "rates_swap_dv01",
        "Payer swap EUR notionnel 100m fixed coupon 3.20% par swap rate 3.00% "
        "annuity 4.55, la courbe monte de 10bp.",
        "On valorise un payer swap et on mesure sa sensibilite a la courbe.",
    ),
    "bond": (
        "bond_duration_dv01",
        "Bond notionnel 50m duration 6.2 le taux monte de 25bp.",
        "On convertit la duration en risque EUR/bp et en P&L de choc.",
    ),
    "barrier": (
        "fx_barrier_option",
        "Option barriere FX down-and-out, spot 1.0800, strike 1.1000, barriere "
        "down-and-out 1.0000, notionnel EUR 10m. Spot a 1.0500, spot a 1.2000.",
        "On calcule le payoff conditionnel et on discute le gap risk.",
    ),
    "cds": (
        "cds_cs01",
        "CDS notionnel 50m spread 120bp risky annuity 4.2 widen 25bp.",
        "On mesure le CS01, le carry et le P&L d'un ecartement de spread.",
    ),
    "var": (
        "parametric_var",
        "VaR parametrique: portefeuille 20m volatilite 2% confiance 95% horizon 1 jour.",
        "On calcule une VaR parametrique simple et on la compare a une limite.",
    ),
    "yield_curve": (
        "yield_curve_bootstrap",
        "Bootstrap de courbe, swaps par annuels: 1 an 3.00%, 2 ans 3.20%, 3 ans 3.35%.",
        "On bootstrappe les discount factors et les taux forward d'une courbe de swaps.",
    ),
    "autocall": (
        "autocall_structured",
        "Autocall Athena sur indice, niveau initial 100, barriere autocall 100%, "
        "barriere coupon 70%, barriere protection 60%, coupon 6% par observation "
        "avec memoire, notionnel 1m. Niveaux observes: 65, 102.",
        "On deroule le payoff d'un autocall a memoire selon un scenario d'observations.",
    ),
    "monte_carlo": (
        "monte_carlo_gbm",
        "Monte Carlo call europeen spot 100 strike 100 vol 20% maturite 1 taux 5%, 20000 simulations.",
        "On price un call par simulation GBM et on lit l'intervalle de confiance.",
    ),
    "vol_smile": (
        "implied_vol_smile",
        "Call vanilla spot 100 strike 100 maturite 1 taux 5% prix de marche 10.4506, "
        "trouver la volatilite implicite.",
        "On inverse Black-Scholes pour retrouver la volatilite implicite d'un call.",
    ),
}

# Topics with no dedicated calculator reuse the closest worked example.
_WORKED_ALIAS = {
    "stochastic": "vanilla_bs",
}


def seed_for_topic(topic_key: str) -> tuple[str, str] | None:
    """Return (calculator_family, parseable_seed_scenario) for a topic, or None.

    Lets other generators (e.g. exercises) fall back to a verified numeric
    scenario when the user supplied no parseable numbers, instead of shipping an
    answer key with no computed result."""
    key = topic_key if topic_key in _WORKED_SEEDS else _WORKED_ALIAS.get(topic_key, "")
    if not key:
        return None
    family, seed, _ = _WORKED_SEEDS[key]
    return family, seed


def varied_scenario(topic_key: str, rng: "random.Random | None" = None) -> tuple[str, str] | None:
    """Return (calculator_family, parseable_seed) with FRESH randomized-but-sensible
    numbers, so repeated exercise requests on the same topic differ while the
    deterministic calculator stays the oracle of correctness.

    variant 0 (canonical fixed seed) is what courses use; exercises call this for
    variety. Pass a seeded rng for reproducible tests."""
    import random as _random

    r = rng or _random.Random()
    key = topic_key if topic_key in _WORKED_SEEDS else _WORKED_ALIAS.get(topic_key, "")
    if not key:
        return None

    def pick(seq):
        return r.choice(seq)

    if key == "vanilla_bs":
        spot = pick([80, 90, 95, 100, 105, 110, 120])
        strike = spot + pick([-15, -10, -5, 0, 5, 10, 15])
        vol = pick([12, 15, 18, 20, 22, 25, 30, 35])
        mat = pick([0.25, 0.5, 1, 1.5, 2])
        rate = pick([0, 1, 2, 3, 4, 5])
        return "vanilla_option_black_scholes", f"Call vanilla spot {spot} strike {strike} vol {vol}% maturite {mat:g} taux {rate}%."
    if key == "greeks":
        d = pick([100, 150, 200, 250, 300, 400]) * pick([1, -1])
        g = pick([40, 60, 80, 100, 120]) * pick([1, -1])
        v = pick([60, 90, 120, 150, 200]) * pick([1, -1])
        th = -pick([8, 12, 15, 20, 25])
        sm = pick([1, 2, 3, 4]) * pick([1, -1])
        vm = pick([2, 3, 4, 5]) * pick([1, -1])
        return "options_book_greeks", (f"Book delta {d:+d}k EUR par 1%, gamma {g:+d}k EUR par 1%^2, vega {v:+d}k EUR par vol point, "
                                       f"theta {th}k EUR par jour. Scenario spot {sm:+d}%, vol {vm:+d}.")
    if key == "swap":
        notl = pick([50, 100, 150, 200, 300])
        par = pick([2.5, 3.0, 3.2, 3.5, 4.0])
        fixed = round(par + pick([-0.3, -0.2, 0.2, 0.3, 0.5]), 2)
        ann = pick([3.5, 4.0, 4.55, 5.0, 6.5])
        shock = pick([5, 10, 15, 25])
        return "rates_swap_dv01", (f"Payer swap EUR notionnel {notl}m fixed coupon {fixed:.2f}% par swap rate {par:.2f}% "
                                   f"annuity {ann:g}, la courbe monte de {shock}bp.")
    if key == "bond":
        notl = pick([20, 50, 75, 100, 200])
        dur = pick([2.5, 4.0, 5.5, 6.2, 7.8, 9.0])
        shock = pick([10, 15, 25, 40, 50])
        return "bond_duration_dv01", f"Bond notionnel {notl}m duration {dur:g} le taux monte de {shock}bp."
    if key == "barrier":
        spot = pick([1.05, 1.08, 1.10, 1.15, 1.20])
        strike = round(spot + pick([0.0, 0.02, 0.05]), 4)
        barrier = round(spot - pick([0.05, 0.08, 0.10, 0.15]), 4)
        notl = pick([5, 10, 20, 50])
        s1 = round(barrier - 0.02, 4)
        s2 = round(strike + pick([0.05, 0.10, 0.15]), 4)
        return "fx_barrier_option", (f"Option barriere FX down-and-out, spot {spot:g}, strike {strike:g}, barriere down-and-out {barrier:g}, "
                                     f"notionnel EUR {notl}m. Spot a {s1:g}, spot a {s2:g}.")
    if key == "cds":
        notl = pick([20, 50, 75, 100, 150])
        spread = pick([60, 90, 120, 180, 250])
        ann = pick([3.2, 4.0, 4.2, 4.8])
        widen = pick([10, 25, 40, 50])
        return "cds_cs01", f"CDS notionnel {notl}m spread {spread}bp risky annuity {ann:g} widen {widen}bp."
    if key == "var":
        val = pick([10, 20, 35, 50, 100])
        vol = pick([1.0, 1.5, 2.0, 2.5, 3.0])
        conf = pick([95, 97.5, 99])
        hor = pick([1, 5, 10])
        return "parametric_var", f"VaR parametrique: portefeuille {val}m volatilite {vol:g}% confiance {conf:g}% horizon {hor:g} jour."
    if key == "yield_curve":
        s1 = pick([2.0, 2.5, 3.0, 3.5])
        s2 = round(s1 + pick([0.1, 0.2, 0.3]), 2)
        s3 = round(s2 + pick([0.1, 0.15, 0.25]), 2)
        return "yield_curve_bootstrap", f"Bootstrap de courbe, swaps par annuels: 1 an {s1:.2f}%, 2 ans {s2:.2f}%, 3 ans {s3:.2f}%."
    if key == "autocall":
        cpn = pick([4, 5, 6, 8])
        l1 = pick([55, 65, 72, 85])
        l2 = pick([60, 95, 102, 110])
        return "autocall_structured", (f"Autocall Athena sur indice, niveau initial 100, barriere autocall 100%, barriere coupon 70%, "
                                       f"barriere protection 60%, coupon {cpn}% par observation avec memoire, notionnel 1m. Niveaux observes: {l1}, {l2}.")
    if key == "monte_carlo":
        spot = pick([90, 100, 110])
        strike = spot + pick([-10, 0, 10])
        vol = pick([15, 20, 25, 30])
        mat = pick([0.5, 1, 2])
        rate = pick([1, 3, 5])
        paths = pick([10000, 20000, 40000])
        return "monte_carlo_gbm", f"Monte Carlo call europeen spot {spot} strike {strike} vol {vol}% maturite {mat:g} taux {rate}%, {paths} simulations."
    if key == "vol_smile":
        # build a market price from a hidden vol so IV inversion recovers it
        import math as _m
        spot = pick([90, 100, 110])
        strike = spot + pick([-10, -5, 0, 5, 10])
        mat = pick([0.5, 1, 2])
        rate = pick([1, 3, 5])
        hidden = pick([0.15, 0.20, 0.25, 0.30])
        d1 = (_m.log(spot / strike) + (rate / 100 + 0.5 * hidden ** 2) * mat) / (hidden * _m.sqrt(mat))
        d2 = d1 - hidden * _m.sqrt(mat)
        nc = lambda x: 0.5 * (1 + _m.erf(x / _m.sqrt(2)))
        px = spot * nc(d1) - strike * _m.exp(-rate / 100 * mat) * nc(d2)
        return "implied_vol_smile", f"Call vanilla spot {spot} strike {strike} maturite {mat:g} taux {rate}% prix de marche {px:.4f}, trouver la volatilite implicite."
    family, seed, _ = _WORKED_SEEDS[key]
    return family, seed


# --- rigorous theory layer (author-verified formulas, corpus-grounded) -----
# Formulas authored and quant-checked here; book titles are REAL documents in the
# RAG corpus (verified by corpus survey). Provenance is honest: the math is
# [genere - theorie] (engine cannot extract clean formulas from OCR'd chunks),
# the references point to the authoritative texts the corpus actually contains.

_THEORY: dict[str, str] = {
    "vanilla_bs": r"""**Definition.** Sous la mesure risque-neutre $\mathbb{Q}$, le prix d'un derive europeen est l'esperance actualisee de son payoff: $V_0 = e^{-rT}\,\mathbb{E}^{\mathbb{Q}}[\,\text{payoff}(S_T)\,]$. Le sous-jacent suit $dS_t = (r-q)S_t\,dt + \sigma S_t\,dW_t^{\mathbb{Q}}$.

**Equation de Black-Scholes.** Tout derive $V(S,t)$ replicable verifie l'EDP
$$\frac{\partial V}{\partial t} + \tfrac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + (r-q)S\frac{\partial V}{\partial S} - rV = 0.$$

**Forme fermee (call/put, dividende continu $q$).**
$$C = S_0 e^{-qT}N(d_1) - K e^{-rT}N(d_2), \qquad P = K e^{-rT}N(-d_2) - S_0 e^{-qT}N(-d_1),$$
$$d_1 = \frac{\ln(S_0/K) + (r-q+\tfrac12\sigma^2)T}{\sigma\sqrt{T}}, \qquad d_2 = d_1 - \sigma\sqrt{T}.$$

**Interpretation probabiliste.** $N(d_2) = \mathbb{Q}(S_T > K)$ est la probabilite risque-neutre d'exercice; $S_0 e^{-qT}N(d_1) = e^{-rT}\,\mathbb{E}^{\mathbb{Q}}[S_T\mathbf{1}_{S_T>K}]$ est l'esperance actualisee *partielle* du sous-jacent sur l'evenement d'exercice (valeur d'un asset-or-nothing) — a ne pas confondre avec une esperance conditionnelle, qui diviserait par $N(d_2)$. Le delta du call vaut $e^{-qT}N(d_1)$.

**Parite call-put.** $C - P = S_0 e^{-qT} - K e^{-rT}$ (modele-independante: pur arbitrage).

**Hypotheses (a connaitre et critiquer).** vol et taux constants, pas de saut, marche sans friction, possibilite de hedge continu, log-normalite. Le smile (voir vol_smile) est la trace empirique de leur violation.

**References (corpus).** Joshi, *The Concepts and Practice of Mathematical Finance* (derivation risque-neutre, ex. 6.4); *The Mathematics of Options* (forme avec dividende); *Computational Finance Using C and C#* (d1/d2, A.1.4); Baxter & Rennie, *Financial Calculus* (replication, martingales).""",

    "greeks": r"""**Definitions (sensibilites = derivees partielles du prix).**
$$\Delta=\frac{\partial V}{\partial S},\;\; \Gamma=\frac{\partial^2 V}{\partial S^2},\;\; \nu=\frac{\partial V}{\partial \sigma},\;\; \Theta=\frac{\partial V}{\partial t},\;\; \rho=\frac{\partial V}{\partial r}.$$

**Formes fermees (call sans dividende).**
$$\Delta = N(d_1),\quad \Gamma = \frac{\varphi(d_1)}{S\sigma\sqrt{T}},\quad \nu = S\varphi(d_1)\sqrt{T},$$
$$\Theta = -\frac{S\varphi(d_1)\sigma}{2\sqrt{T}} - rKe^{-rT}N(d_2),\quad \rho = KTe^{-rT}N(d_2).$$
Pour le put: $\Delta_{put}=\Delta_{call}-1$, meme $\Gamma$ et $\nu$ (parite).

**Attribution de P&L (Taylor au 2e ordre).**
$$dV \approx \Delta\,dS + \tfrac12\Gamma\,(dS)^2 + \nu\,d\sigma + \Theta\,dt.$$
C'est l'equation du desk: le terme $\tfrac12\Gamma(dS)^2$ est le P&L de convexite, finance par le theta ($\Theta<0$ pour un long d'options).

**Intuition rigoureuse.** Gamma et theta sont les deux faces d'une meme piece: en delta-neutre, le P&L sur un pas $dt$ est $\approx \tfrac12\Gamma S^2(\sigma_{real}^2 - \sigma_{imp}^2)\,dt$ — on gagne si le realise depasse l'implicite. $\nu$ et $\Gamma$ sont maximaux autour de la monnaie.

**Piege theorique.** Les greeks sont des sensibilites *locales* (petits chocs); pour un grand mouvement, l'approximation Taylor decroche — d'ou la revalorisation complete.

**References (corpus).** Hull, *Options, Futures and Other Derivatives*; *Options Math for Traders* (gamma numerique); *FX Derivatives Trader School* (vega, frequence de hedge).""",

    "swap": r"""**Definition.** Un swap de taux echange une jambe fixe (coupon $K$) contre une jambe flottante. Sa valeur (point de vue payeur fixe) est
$$V = N\sum_{i=1}^{n}\tau_i DF(t_i)\,\big(f_i - K\big),$$
avec $\tau_i$ les fractions d'annee, $DF(t_i)$ les discount factors et $f_i$ les forwards.

**Taux swap par (mid-market).** Le taux qui annule la valeur:
$$s = \frac{1 - DF(t_n)}{\sum_{i=1}^{n}\tau_i DF(t_i)} = \frac{1-DF_n}{A_n},$$
ou $A_n=\sum \tau_i DF_i$ est l'**annuite** (PV01 de la jambe fixe).

**Sensibilite (DV01).** $\text{DV01} = \dfrac{\partial V}{\partial(\text{1bp})} \approx A_n \cdot N \cdot 10^{-4}$ (approximation du 1er ordre, annuite $A_n$ figee). Un payeur gagne quand les taux montent.

**Intuition rigoureuse.** Un swap au par vaut zero a l'initiation: $K=s \Rightarrow V=0$. Toute la valeur ulterieure vient de l'ecart $(s_t-K)$ actualise sur l'annuite — d'ou le role central de $A_n$.

**Piege theorique.** Mono-courbe ici par simplicite; en production on **actualise sur OIS** et on projette les forwards sur la courbe IBOR/€STR (multi-courbe). Confondre les deux fausse le DV01.

**References (corpus).** *Interest Rate Derivatives Explained Vol. 1* (taux swap, eq. 5.2); Flavell, *Swaps and Other Derivatives* (valorisation, value=0 au par); *Pricing and Hedging Financial Derivatives*.""",

    "yield_curve": r"""**Definition.** La courbe se resume en discount factors $DF(0,t)$. Le taux zero-coupon depend de la convention de composition, et le forward simplement compose $f_{t,T}$ s'annualise sur la periode $(T-t)$:
$$DF(0,t) = (1+z_t^{ann})^{-t} = e^{-z_t^{cont}\,t},\quad z_t^{cont}=\ln(1+z_t^{ann}),\qquad f_{t,T} = \frac{1}{T-t}\!\left(\frac{DF(0,t)}{DF(0,T)} - 1\right).$$

**Bootstrap sequentiel (swaps par annuels).** Pour le noeud $n$, en isolant $DF_n$ dans l'equation du par swap $s_n\sum_{i\le n}\tau_i DF_i = 1-DF_n$:
$$\boxed{\,DF_n = \frac{1 - s_n\sum_{i=1}^{n-1}\tau_i DF_i}{1 + s_n\tau_n}\,}$$
On resout de proche en proche: $DF_1$, puis $DF_2$, etc.

**Intuition rigoureuse.** Une obligation a coupon = portefeuille de zero-coupons; le bootstrap "depouille" un instrument a la fois pour extraire le DF marginal de chaque maturite. Les forwards implicites doivent rester positifs et lisses — sinon l'interpolation ou les inputs sont incoherents.

**Piege theorique.** Le resultat depend de l'interpolation (lineaire en taux, en log-DF, splines...) et du jeu d'instruments. En multi-courbe, **la courbe de projection des forwards differe de la courbe d'actualisation (OIS)**.

**References (corpus).** *Interest Rate Derivatives Explained Vol. 1* (bootstrap des swaps par); *Innovations in Derivatives Markets* (courbe forward vs discount, OIS); *Fixed Income Markets* (obligation a coupon = panier de zero-coupons).""",

    "bond": r"""**Prix et rendement.** Pour une obligation a coupon $C$, nominal $F$, rendement $y$:
$$P = \sum_{t=1}^{n}\frac{C}{(1+y)^t} + \frac{F}{(1+y)^n}.$$

**Duration et convexite.**
$$D_{Mac} = \frac{1}{P}\sum_{t} t\,\frac{CF_t}{(1+y)^t},\qquad D^* = \frac{D_{Mac}}{1+y},\qquad Cx = \frac{1}{P}\sum_t \frac{t(t+1)\,CF_t}{(1+y)^{t+2}}.$$

**Approximation prix (2e ordre).**
$$\frac{\Delta P}{P} \approx -D^*\,\Delta y + \tfrac12 Cx\,(\Delta y)^2,\qquad \text{DV01} = D^* \cdot P \cdot 10^{-4}.$$

**Intuition rigoureuse.** La duration est l'echeance moyenne ponderee des cash-flows et la pente locale prix/taux; la convexite ($Cx>0$ pour une obligation classique) est un *ami*: elle amortit les hausses de taux et amplifie les baisses. Elle vaut d'autant plus que la volatilite des taux est elevee.

**Piege theorique.** La seule duration sous-estime la perte pour de gros chocs et ignore les variations de pente/forme de courbe (risque de *key-rate duration*).

**References (corpus).** Fabozzi, *Foundations of Financial Markets and Institutions* (YTM, exemple chiffre); FRM Handbook (Jorion) (duration modifiee vs Macaulay); *Mathematics of the Financial Markets* (convexite, §3.2.3).""",

    "barrier": r"""**Taxonomie.** Knock-out (s'eteint si la barriere est touchee) vs knock-in (nait a ce moment); up/down selon le sens. Le payoff depend du strike **et** du chemin.

**Parite in-out (modele-independante).**
$$C_{KI} + C_{KO} = C_{vanilla}\quad\text{(memes strike/maturite/barriere-sens).}$$
Detenir le knock-in et le knock-out equivaut a detenir le vanilla.

**Forme fermee (down-and-out call, monitoring continu, principe de reflexion).** Avec barriere $B<K$:
$$C_{DO} = C_{BS}(S_0) - \left(\frac{B}{S_0}\right)^{2\lambda-2} C_{BS}\!\left(\frac{B^2}{S_0}\right),\quad \lambda=\frac{r-q+\tfrac12\sigma^2}{\sigma^2},$$
l'image $B^2/S_0$ etant le sous-jacent "reflechi" sur la barriere.

**Monitoring discret (correction Broadie-Glasserman-Kou).** Une barriere observee a pas $\Delta t$ se price comme une barriere continue **decalee** $B \to B\,e^{\pm \beta\sigma\sqrt{\Delta t}}$, $\beta\approx 0.5826$ ($+$ pour up, $-$ pour down).

**Piege theorique.** Pres de la barriere, delta et gamma explosent (discontinuite de payoff): le hedge delta continu peut echouer sur un **gap**. Le risque dominant n'est pas un grec lisse mais le franchissement.

**References (corpus).** *Principles of Financial Engineering* (equation contractuelle in-out, §11.4.2); *Derivatives Models on Models* (arbre + principe de reflexion); *FX Derivatives Trader School* (reverse KO ↔ one-touch, gap).""",

    "autocall": r"""**Mecanique.** A chaque date d'observation $t_i$: si $S_{t_i}\ge$ barriere d'autocall, **rappel anticipe** (nominal + coupon); si $\ge$ barriere de coupon, coupon paye (avec **memoire** des coupons manques); a maturite, si jamais rappele, capital protege tant que $S_T\ge$ barriere de protection, sinon perte $1{:}1$.

**Decomposition vendeur (risque).** Vendre un autocall worst-of revient a etre
$$\text{short les digitales de coupon/autocall} \;+\; \text{long un put down-and-in worst-of},$$
soit, du point de vue du **vendeur**, un profil **long skew, long volatilite, short correlation (= long dispersion)**, en echange du portage paye via les coupons digitaux vendus. (L'investisseur est exactement le miroir: short vol, short skew, long correlation, recoit le coupon.)

**Pricing.** Pas de forme fermee (payoff path-dependent, souvent multi-sous-jacents): on price par **Monte-Carlo** sous vol/dividendes/correlation (lien vers monte_carlo et vol_smile).

**Intuition rigoureuse.** L'investisseur vend de la protection en echange d'un coupon eleve: il est *short* le crash. L'effet "snowball" (memoire) concentre les coupons sur les scenarios de remontee.

**Piege theorique.** Le risque vendeur est non lineaire et explose pres de la barriere de protection a l'approche de la maturite (gap + correlation qui monte en stress).

**References (corpus).** Bouzoubaa & Osseiran, *Exotic Options and Hybrids* (§12.4 snowball, worst-of put, decomposition de risque); *Pricing and Hedging Financial Derivatives* (notes structurees, worst-of digital).""",

    "monte_carlo": r"""**Estimateur.** Pour un payoff europeen,
$$\hat{V} = e^{-rT}\,\frac{1}{N}\sum_{i=1}^{N} \text{payoff}\big(S_T^{(i)}\big),\qquad SE = \frac{e^{-rT}\,\hat{s}}{\sqrt{N}},$$
avec $\hat{s}$ l'ecart-type empirique des payoffs. **Convergence en $O(N^{-1/2})$**: diviser l'erreur par 2 coute $\times 4$ en simulations.

**Schema exact GBM.** $S_T = S_0\exp\!\big((r-\tfrac12\sigma^2)T + \sigma\sqrt{T}\,Z\big)$, $Z\sim\mathcal{N}(0,1)$ (pas de biais de discretisation pour un payoff terminal).

**Reduction de variance.**
- *Antithetiques*: utiliser $(Z,-Z)$ — la correlation negative reduit la variance a cout egal.
- *Variable de controle*: $\hat{V}_{cv} = \hat{V} - \beta^*(\hat{X}-\mathbb{E}X)$, avec $\beta^* = \mathrm{Cov}(V,X)/\mathrm{Var}(X)$ (ex. controle = call BS analytique).

**Intuition rigoureuse.** L'IC $\hat{V}\pm 1.96\,SE$ doit contenir le prix ferme: c'est le test de non-biais d'implementation. Un IC etroit ne corrige **pas** un biais de modele.

**Piege theorique.** Pour les payoffs path-dependent (barrieres, asiatiques, americaines) il faut discretiser le chemin (biais de pas de temps) et, pour l'exercice anticipe, **LSM (Longstaff-Schwartz)**.

**References (corpus).** Glasserman, *Handbook in Monte Carlo Simulation* (variance reduction, importance sampling); *Pricing Derivative Securities* (antithetiques); Tavella, *Quantitative Methods in Derivatives Pricing* (variance vs cout).""",

    "stochastic": r"""**Lemme d'Ito.** Pour $X_t$ avec $dX_t=\mu\,dt+\sigma\,dW_t$ et $f$ reguliere,
$$df(X_t) = \Big(f' \mu + \tfrac12 f'' \sigma^2\Big)dt + f'\sigma\,dW_t,$$
le terme du second ordre venant de la variation quadratique $(dW_t)^2 = dt$.

**Theoreme de Girsanov.** Un changement de mesure $\mathbb{P}\to\mathbb{Q}$ via la derivee de Radon-Nikodym translate le drift: $d\tilde{W}_t = dW_t + \theta_t\,dt$ est un $\mathbb{Q}$-brownien. Avec $\theta=(\mu-r)/\sigma$ (prix de marche du risque), le drift du sous-jacent devient $r$: c'est la **mesure risque-neutre**.

**Feynman-Kac.** La solution de l'EDP $\partial_t u + \mathcal{L}u - ru = 0$, $u(T,\cdot)=g$, admet la representation probabiliste
$$u(t,x) = \mathbb{E}\big[e^{-r(T-t)} g(X_T)\,\big|\,X_t=x\big],$$
pont entre EDP (Black-Scholes) et esperance (pricing risque-neutre).

**Intuition rigoureuse.** Le terme $\tfrac12 f''\sigma^2\,dt$ d'Ito est *exactement* le gamma de l'attribution de P&L: la finance de marche est du calcul d'Ito applique.

**Piege theorique.** $(dW)^2=dt$ n'est pas une heuristique: c'est la variation quadratique non nulle qui distingue le calcul stochastique du calcul classique (ou $(dt)^2\to0$).

**References (corpus).** Joshi, *Concepts and Practice* (Ito, eq. 5.24); Neftci, *An Introduction to the Mathematics of Financial Derivatives* (Feynman-Kac); Baxter & Rennie, *Financial Calculus* (Cameron-Martin-Girsanov, §3.4).""",

    "cds": r"""**Structure.** Deux jambes: l'acheteur de protection paie un spread $s$ (jambe de prime) et recoit $(1-R)\times$ nominal en cas de defaut (jambe de protection), $R$ = taux de recouvrement.

**Spread par (egalite des PV des deux jambes).**
$$s = \frac{(1-R)\sum_i DF_i\,(Q_{i-1}-Q_i)}{\sum_i DF_i\,\tau_i\,Q_i},$$
ou $Q_i=\mathbb{Q}(\tau>t_i)=e^{-\int_0^{t_i}\lambda}$ est la probabilite de survie et $DF_i$ l'actualisation.

**Triangle du credit (approximation).** $\;s \approx \lambda\,(1-R)\;$ — le spread est, au premier ordre, l'intensite de defaut $\lambda$ fois la perte en cas de defaut.

**Sensibilites.** $\text{CS01}=$ P&L pour $1$bp d'ecartement $\approx$ annuite risquee $\times$ nominal $\times 10^{-4}$; **jump-to-default** $=(1-R)\times$ nominal. Ne pas confondre **coupon annuel** $=s\times$ nominal et **PV de la jambe de prime** $=$ coupon annuel $\times$ annuite risquee.

**Intuition rigoureuse.** Le CDS isole le risque de credit pur; on **bootstrappe la courbe de hasard** $\lambda(t)$ a partir des spreads quotes comme on bootstrappe une courbe de taux.

**Piege theorique.** Le carry (coupon paye) est compense seulement par le widening/defaut: l'acheteur de protection est short carry, long crash de credit.

**References (corpus).** *Analytical Finance Vol. II* (jambes prime/protection, Hull-White); *Principles of Financial Engineering* (proba risque-neutre de defaut, eq. 18.42); Choudhry, *Credit Derivatives*.""",

    "var": r"""**Definition.** La VaR de niveau $\alpha$ sur l'horizon $h$ est le quantile de perte: $\mathbb{P}(L > \text{VaR}_\alpha)=1-\alpha$. En parametrique gaussien (moyenne nulle):
$$\text{VaR}_\alpha = z_\alpha\,\sigma\sqrt{h}\,V,\qquad z_\alpha = \Phi^{-1}(\alpha).$$

**Expected Shortfall (CVaR).** Perte moyenne au-dela de la VaR:
$$\text{ES}_\alpha = \mathbb{E}[L\,|\,L>\text{VaR}_\alpha] = \sigma\sqrt{h}\,V\,\frac{\varphi(z_\alpha)}{1-\alpha} \;\ge\; \text{VaR}_\alpha.$$

**Axiomes de coherence (Artzner et al.).** monotonicite, invariance par translation, homogeneite positive, **sous-additivite**. La VaR viole la sous-additivite en general (un risque diversifie peut afficher une VaR superieure a la somme); l'**ES est coherente**.

**Backtesting (Kupiec POF).** Test du ratio de vraisemblance comparant le taux d'exceptions observe $\hat{p}=N/n$ au taux theorique $p=1-\alpha$: $LR_{POF}=-2\ln\frac{(1-p)^{n-N}p^{N}}{(1-\hat p)^{n-N}\hat p^{N}}\sim \chi^2_1$.

**Piege theorique.** La VaR ne dit **rien** de l'ampleur des pertes au-dela du seuil et sous-estime les queues epaisses; d'ou l'ES et les stress tests en complement (Bale FRTB privilegie l'ES 97.5%).

**References (corpus).** FRM Handbook (Jorion) (ES = CVaR); *Encyclopedia of Quantitative Finance* (axiomes de coherence); Wilmott, *FAQs in Quantitative Finance* (contre-exemple sous-additivite); *Mathematics of the Financial Markets* (test de Kupiec).""",

    "vol_smile": r"""**Volatilite implicite.** $\sigma_{imp}(K,T)$ est l'unique vol qui recolle le prix de marche au modele BS: $C_{BS}(\sigma_{imp}) = C_{marche}$. Tracee en fonction du strike, elle dessine le **smile/skew** — preuve directe que BS (vol constante) est faux.

**Volatilite locale (Dupire).** L'unique diffusion $dS=\sigma_{loc}(S,t)S\,dW$ compatible avec tous les prix d'options:
$$\sigma_{loc}^2(K,T) = \frac{\partial_T C + (r-q)K\,\partial_K C + qC}{\tfrac12 K^2\,\partial_{KK}C}.$$

**SABR (Hagan et al. 2002).** $dF=\alpha F^{\beta}dW_1,\; d\alpha=\nu\alpha\,dW_2,\; \langle dW_1,dW_2\rangle=\rho\,dt$. Approximation analytique de $\sigma_{imp}(K,F)$ tres utilisee pour interpoler/extrapoler le smile de taux. Heston ajoute une variance en racine a retour a la moyenne.

**Intuition rigoureuse.** Le skew price l'asymetrie et les queues (crash risk): un put OTM cher = vol implicite elevee a bas strike. La vol implicite est un *prix*, pas une prevision.

**Piege theorique.** La vol locale inversee de Dupire peut etre non-physique (negative) si la surface implicite n'est pas sans arbitrage (monotonie/convexite en $K$, calendar spreads). Sticky-strike vs sticky-delta changent le delta couvert.

**References (corpus).** *FX Derivatives Trader School* (surface de vol locale, Heston); *Mathematics of the Financial Markets* (SABR $\alpha,\beta,\rho$); *Interest Rate Derivatives Explained Vol. 2* (Hagan 2002); *Encyclopedia of Quantitative Finance* (Dupire, non-physicalite).""",
}
_THEORY["stochastic"] = _THEORY["stochastic"]  # explicit own block (no alias)


def theory_block_markdown(topic_key: str) -> str:
    """Rigorous, author-verified theory layer for a topic (the 'quant' layer).

    Complements the practice-oriented prose: precise definitions, the key
    theorems/closed forms (formulas checked by a finance professional), the
    rigorous intuition, a theoretical pitfall, and citations to the authoritative
    texts actually present in the RAG corpus."""
    body = _THEORY.get(topic_key) or _THEORY.get(_WORKED_ALIAS.get(topic_key, ""), "")
    if not body:
        return (
            "_[genere - theorie]_ Poser les definitions rigoureuses, le ou les "
            "resultats cles (forme fermee, theoreme), une intuition demontree et "
            "un piege theorique, en citant une source faisant autorite."
        )
    return f"_[genere - theorie, formules verifiees par un professionnel]_\n\n{body}"


def worked_example_markdown(topic_key: str, calculator: PracticeCalculator | None = None) -> str:
    calc = calculator or PracticeCalculator()
    key = topic_key if topic_key in _WORKED_SEEDS else _WORKED_ALIAS.get(topic_key, "")
    if not key:
        return (
            "_[genere]_ Construire un exemple chiffre minimal: poser les donnees, "
            "appliquer la formule cle pas a pas, puis interpreter le resultat en "
            "langage de desk. (Aucun calculateur dedie pour ce sujet.)"
        )
    family, seed, intro = _WORKED_SEEDS[key]
    pack = calc.build_pack(seed, family_hint=family)
    lines = [
        f"_[genere - calcul verifie]_ {intro}",
        "",
        f"**Donnees.** {seed}",
        "",
        pack.as_markdown(),
        "",
        "**Lecture finale.** Chaque chiffre ci-dessus a une unite explicite et un "
        "sens economique; un apprenant doit pouvoir refaire le calcul a la main "
        "et retrouver le meme ordre de grandeur.",
    ]
    return "\n".join(lines)


# --- corrected exercises ---------------------------------------------------

def corrected_exercise_markdown(topic_key: str, calculator: PracticeCalculator | None = None) -> str:
    calc = calculator or PracticeCalculator()
    key = topic_key if topic_key in _WORKED_SEEDS else _WORKED_ALIAS.get(topic_key, "")
    simple = _SIMPLE_EXERCISE.get(topic_key) or _SIMPLE_EXERCISE.get(key) or _SIMPLE_EXERCISE["generic"]
    advanced = _ADVANCED_EXERCISE.get(topic_key) or _ADVANCED_EXERCISE.get(key) or _ADVANCED_EXERCISE["generic"]
    blocks = [
        "### Exercice 1 - application directe",
        f"_[genere]_ {simple['q']}",
        "",
        f"**Correction.** {simple['a']}",
        "",
        "### Exercice 2 - niveau desk",
        f"_[genere]_ {advanced['q']}",
        "",
    ]
    if key:
        family, seed, _ = _WORKED_SEEDS[key]
        pack = calc.build_pack(seed, family_hint=family)
        blocks.append("**Correction detaillee (calcul verifie).**")
        blocks.append(pack.as_markdown())
    else:
        blocks.append(f"**Correction detaillee.** {advanced['a']}")
    return "\n".join(blocks)


_SIMPLE_EXERCISE = {
    "vanilla_bs": {"q": "Un call ATM a S=K=100, vol 20%, T=1, r=5%. Sans calculer finement, dites si son delta est plutot proche de 0, 0.5 ou 1, et pourquoi.",
                   "a": "Pour un call a la monnaie, N(d1) est legerement au-dessus de 0.5 (le drift r decale d1 vers le positif). Le delta est donc proche de 0.5-0.6: une hausse de 1 du spot fait gagner ~0.5-0.6 au call."},
    "greeks": {"q": "Un book est long gamma. Le spot fait un aller-retour (-2% puis +2%). Le P&L gamma est-il positif ou negatif?",
               "a": "Positif. Long gamma => convexite favorable: la position gagne sur les mouvements realises dans les deux sens (re-hedge bas, re-hedge haut). C'est l'inverse pour un short gamma."},
    "swap": {"q": "Un payer swap a un fixed coupon au-dessus du par rate. Sa PV initiale est-elle positive ou negative pour le payer?",
             "a": "Negative: payer un coupon superieur au marche est desavantageux, donc PV(payer) = (par - fixed) * annuite * notionnel < 0."},
    "bond": {"q": "Une obligation a une duration de 6. Les taux montent de 25bp. Le prix monte ou baisse, et d'environ combien en %?",
             "a": "Le prix baisse d'environ duration * choc = 6 * 0.25% = 1.5%. Relation prix/taux inverse."},
    "barrier": {"q": "Un down-and-out call est-il plus cher ou moins cher qu'un call vanilla equivalent?",
                "a": "Moins cher: il peut s'eteindre si la barriere est touchee, donc il offre moins -> prime inferieure. In-out parity: C_vanilla = C_out + C_in."},
    "cds": {"q": "Un acheteur de protection CDS gagne-t-il ou perd-il quand le spread s'ecarte?",
            "a": "Il gagne en mark-to-market: la protection qu'il detient vaut plus cher. P&L approx = CS01 * widening."},
    "var": {"q": "Une VaR 95% 1 jour de 660k signifie quoi exactement?",
            "a": "Dans ~95% des jours, la perte ne devrait pas depasser 660k; environ 1 jour sur 20, elle peut etre superieure. La VaR ne dit rien de l'ampleur au-dela du seuil."},
    "generic": {"q": "Identifiez le produit, son risque dominant et la donnee de marche qui le pilote le plus.",
                "a": "Reponse type: nommer le payoff, la sensibilite de premier ordre (delta/DV01/CS01...) et la variable marche associee (spot/taux/spread)."},
}
_ADVANCED_EXERCISE = {
    "vanilla_bs": {"q": "Spot 100, strike 100, vol 20%, T=1, r=5%. Calculez d1, d2, le prix du call et son delta, puis dites comment hedger 1000 calls.",
                   "a": "Voir le calcul verifie ci-dessous; le hedge initial vend delta*1000 actions."},
    "greeks": {"q": "Book delta +250k/1%, gamma -80k/1%^2, vega +120k/pt, theta -15k/jour. Scenario spot -2%, vol +3pts, 1 jour. Estimez le P&L total et le risque dominant.",
               "a": "Voir l'attribution verifiee ci-dessous; identifier le facteur de plus forte contribution avant de hedger."},
    "swap": {"q": "Payer swap EUR 100m, fixed 3.20%, par 3.00%, annuite 4.55. Courbe +10bp. Calculez PV, DV01 et P&L.",
             "a": "Voir le calcul verifie ci-dessous."},
    "bond": {"q": "Bond 50m, duration 6.2, +25bp. Calculez DV01 et P&L, puis dites quand l'approximation duration devient insuffisante.",
             "a": "Voir le calcul verifie; au-dela de chocs larges, ajouter la convexite."},
    "barrier": {"q": "Down-and-out call FX, spot 1.0800, strike 1.1000, barriere 1.0000, notionnel 10m. Payoff si le spot finit a 1.0500? a 1.2000 sans toucher la barriere?",
                "a": "Voir le calcul verifie ci-dessous; attention au gap risk pres de la barriere."},
    "cds": {"q": "CDS 50m, spread 120bp, risky annuity 4.2, widen 25bp. Calculez CS01, carry et P&L.",
            "a": "Voir le calcul verifie ci-dessous."},
    "var": {"q": "Portefeuille 20m, vol 2%/jour, 95%, 1 jour. Calculez la VaR et comparez a une limite de 500k.",
            "a": "Voir le calcul verifie ci-dessous; ici la VaR depasse la limite -> reduire ou escalader."},
    "generic": {"q": "Construisez un mini-cas chiffre du sujet et resolvez-le pas a pas avec unites et interpretation.",
                "a": "La correction doit exposer hypotheses, formule, application numerique, resultat et lecture marche."},
}


# --- MCQ quizzes -----------------------------------------------------------
# 5 questions per main topic. Each: question, 4 options, index of answer, why.

def quiz_markdown(topic_key: str) -> str:
    bank = _QUIZ_BANK.get(topic_key) or _QUIZ_BANK["generic"]
    lines = ["_[genere]_ Mini-quiz de verification (5 questions).", ""]
    for i, q in enumerate(bank, start=1):
        lines.append(f"**Q{i}. {q['q']}**")
        for j, opt in enumerate(q["options"]):
            lines.append(f"- {chr(65 + j)}) {opt}")
        ans = chr(65 + q["answer"])
        lines.append(f"  - Reponse: **{ans}**. {q['why']}")
        lines.append("")
    return "\n".join(lines).strip()


_QUIZ_BANK: dict[str, list[dict]] = {
    "vanilla_bs": [
        {"q": "Dans Black-Scholes, que represente N(d2)?", "options": ["La probabilite risque-neutre d'exercice", "Le delta du call", "La vega", "Le prix du put"], "answer": 0, "why": "N(d2) est la probabilite risque-neutre que le call finisse dans la monnaie."},
        {"q": "Le delta d'un call ATM est environ:", "options": ["0", "0.5", "1", "-0.5"], "answer": 1, "why": "N(d1) ~ 0.5 a la monnaie (legerement au-dessus avec un taux positif)."},
        {"q": "La put-call parity relie call et put via:", "options": ["la vol implicite", "C - P = S - K e^{-rT}", "le gamma", "la duration"], "answer": 1, "why": "C - P = forward actualise - strike actualise; une violation signale une incoherence de quote."},
        {"q": "Augmenter la volatilite implicite fait:", "options": ["baisser call et put", "monter call et put", "monter le call, baisser le put", "rien"], "answer": 1, "why": "La vega est positive pour call et put: plus de vol = plus de valeur temps."},
        {"q": "La vega est maximale:", "options": ["tres ITM", "tres OTM", "proche de la monnaie", "a maturite nulle"], "answer": 2, "why": "La sensibilite a la vol est la plus forte autour de l'ATM, surtout a maturite moyenne."},
    ],
    "greeks": [
        {"q": "Etre long gamma signifie:", "options": ["perdre sur les grands mouvements", "gagner sur la volatilite realisee", "etre insensible au spot", "etre short vega"], "answer": 1, "why": "Long gamma = convexite favorable: on profite des mouvements realises dans les deux sens."},
        {"q": "Le theta d'une position long options est en general:", "options": ["positif", "negatif", "nul", "egal au delta"], "answer": 1, "why": "Detenir de la valeur temps coute du theta: elle se degrade chaque jour."},
        {"q": "Un book short gamma et long vega est surtout vulnerable a:", "options": ["une vol implicite qui monte sans bouger le spot", "un spot qui bouge beaucoup en realise", "rien", "une baisse des taux"], "answer": 1, "why": "Short gamma fait mal quand le realise est eleve, meme si la vega aide si l'implicite monte."},
        {"q": "Delta-neutre veut dire:", "options": ["gamma nul", "sensibilite de premier ordre au spot ~ 0", "vega nul", "theta nul"], "answer": 1, "why": "On annule la sensibilite directionnelle de premier ordre; gamma/vega/theta restent."},
        {"q": "Vega s'exprime usuellement en:", "options": ["EUR par 1% de spot", "EUR par point de vol", "EUR par jour", "EUR par bp de taux"], "answer": 1, "why": "Vega = variation de valeur par point de volatilite implicite."},
    ],
    "swap": [
        {"q": "Le DV01 d'un swap mesure:", "options": ["le P&L pour 1bp de courbe", "le coupon fixe", "la prime d'option", "le spread de credit"], "answer": 0, "why": "DV01 = annuite * notionnel * 1bp: sensibilite lineaire a la courbe."},
        {"q": "Un payer swap gagne quand:", "options": ["les taux baissent", "les taux montent", "la vol monte", "le spread s'ecarte"], "answer": 1, "why": "Le payer recoit le flottant: il profite d'une hausse des taux."},
        {"q": "La PV d'un payer dont le coupon = par rate est:", "options": ["fortement positive", "proche de zero", "fortement negative", "indeterminee"], "answer": 1, "why": "Au par, fixed = par rate => PV ~ 0 a l'initiation."},
        {"q": "Le basis risk d'un hedge swap vient surtout de:", "options": ["un mismatch de tenor/index", "la couleur de l'ecran", "le notionnel", "le jour de la semaine"], "answer": 0, "why": "Couvrir avec un tenor/index different laisse un risque de base residuel."},
        {"q": "Annuite elevee => DV01:", "options": ["plus faible", "plus eleve", "inchange", "negatif"], "answer": 1, "why": "DV01 croit avec l'annuite (et le notionnel)."},
    ],
    "var": [
        {"q": "Une VaR 99% 1j de 1m signifie:", "options": ["perte garantie de 1m", "~1 jour sur 100 la perte peut depasser 1m", "gain de 1m", "vol de 1m"], "answer": 1, "why": "C'est un quantile: la perte depasse rarement (1%) le seuil, sans borne au-dela."},
        {"q": "La VaR parametrique suppose surtout:", "options": ["des rendements normaux", "des sauts frequents", "une vol nulle", "un spot constant"], "answer": 0, "why": "Elle s'appuie sur un quantile gaussien; elle sous-estime les queues epaisses."},
        {"q": "L'expected shortfall complete la VaR car:", "options": ["elle ignore les pertes", "elle mesure la perte moyenne au-dela du seuil", "elle est plus simple", "elle est toujours plus petite"], "answer": 1, "why": "L'ES regarde la moyenne des pertes dans la queue, au-dela de la VaR."},
        {"q": "Doubler l'horizon (iid) multiplie la VaR par:", "options": ["2", "sqrt(2)", "1", "4"], "answer": 1, "why": "Sous racine-du-temps, la VaR croit en sqrt(horizon)."},
        {"q": "Un depassement de limite VaR appelle d'abord:", "options": ["ignorer", "reduire/hedger/escalader", "augmenter la position", "changer la couleur"], "answer": 1, "why": "La reaction operationnelle est de reduire le risque ou d'escalader."},
    ],
    "barrier": [
        {"q": "Un knock-out option:", "options": ["nait quand la barriere est touchee", "s'eteint quand la barriere est touchee", "ignore la barriere", "est sans risque"], "answer": 1, "why": "Le knock-out disparait si la barriere est atteinte pendant la vie."},
        {"q": "Le gap risk d'une barriere vient de:", "options": ["un delta lisse", "une discontinuite de payoff pres de la barriere", "le theta", "le coupon"], "answer": 1, "why": "Pres de la barriere, la valeur saute: le delta hedge continu peut echouer."},
        {"q": "In-out parity dit:", "options": ["C_out = C_in", "C_vanilla = C_out + C_in", "C_out = C_vanilla", "rien"], "answer": 1, "why": "Le vanilla se decompose en knock-out plus knock-in."},
        {"q": "Un down-and-out call vs vanilla est:", "options": ["plus cher", "moins cher", "identique", "sans prime"], "answer": 1, "why": "Il offre moins (peut s'eteindre) donc coute moins."},
        {"q": "Pres de la barriere le desk doit surtout:", "options": ["ignorer", "monitorer et definir des triggers d'escalation", "augmenter la taille", "vendre du theta"], "answer": 1, "why": "Le risque n'est pas un Greek lisse: monitoring et escalation priment."},
    ],
    "cds": [
        {"q": "Le CS01 d'un CDS mesure:", "options": ["le P&L pour 1bp d'ecartement de spread", "le coupon annuel", "la prime d'option", "le DV01 de taux"], "answer": 0, "why": "CS01 = risky annuity * notionnel * 1bp: sensibilite de la MtM au spread de credit."},
        {"q": "Le coupon annuel d'un CDS vaut approximativement:", "options": ["spread * risky annuity * notionnel", "spread * notionnel", "CS01 * notionnel", "recovery * notionnel"], "answer": 1, "why": "Le coupon paye chaque annee = spread (en decimal) * notionnel; multiplie par la risky annuity on obtient la PV de toute la jambe de prime, pas le coupon."},
        {"q": "Un acheteur de protection CDS quand le spread s'ecarte:", "options": ["perd en MtM", "gagne en MtM", "est insensible", "paie plus de coupon"], "answer": 1, "why": "La protection detenue vaut plus cher: P&L MtM ~ CS01 * widening > 0."},
        {"q": "Le jump-to-default d'un acheteur de protection vaut environ:", "options": ["recovery * notionnel", "(1 - recovery) * notionnel", "spread * notionnel", "zero"], "answer": 1, "why": "En cas de defaut il recoit (1 - recovery) * notionnel, la perte sur le pair (LGD)."},
        {"q": "Le carry d'un acheteur de protection (hors defaut) est:", "options": ["positif", "negatif: il paie la prime", "nul", "egal au CS01"], "answer": 1, "why": "Il paie le coupon chaque jour: carry negatif, compense seulement si un defaut/widening survient."},
    ],
    "generic": [
        {"q": "Quelle est la premiere etape sur un nouveau cas de desk?", "options": ["calculer tout de suite", "identifier produit, payoff et risque dominant", "hedger au hasard", "ignorer les donnees"], "answer": 1, "why": "On qualifie d'abord le produit et son risque avant de calculer."},
        {"q": "Une approximation locale (Taylor) est valable:", "options": ["pour tout choc", "pour de petits chocs", "jamais", "seulement a maturite"], "answer": 1, "why": "Les sensibilites de premier ordre supposent de petits mouvements."},
        {"q": "Un resultat chiffre sans unite est:", "options": ["acceptable", "inexploitable", "preferable", "plus precis"], "answer": 1, "why": "Sans unite, le chiffre n'a pas de sens economique."},
        {"q": "Distinguer contenu extrait et genere sert a:", "options": ["faire joli", "tracabilite et anti-hallucination", "rien", "ralentir"], "answer": 1, "why": "La provenance protege la credibilite et evite de presenter du genere comme source."},
        {"q": "Conclure un cas de desk, c'est:", "options": ["donner un chiffre seul", "proposer une action (hedge/monitor/quote/escalate)", "citer une formule", "changer de sujet"], "answer": 1, "why": "Une analyse de desk se termine par une decision operationnelle."},
    ],
}
# Topics without a dedicated quiz reuse the closest one, else generic.
for _alias, _src in {"yield_curve": "swap", "bond": "swap", "autocall": "barrier",
                     "monte_carlo": "vanilla_bs", "stochastic": "vanilla_bs",
                     "vol_smile": "vanilla_bs"}.items():
    _QUIZ_BANK.setdefault(_alias, _QUIZ_BANK[_src])


# --- prerequisites / level / time -----------------------------------------

_PREREQUISITES = {
    "vanilla_bs": ["payoff d'une option", "actualisation", "loi normale", "notion de volatilite"],
    "greeks": ["prix d'une option vanilla", "derivees partielles", "notion de hedge"],
    "swap": ["valeur temps de l'argent", "courbe de taux", "actualisation"],
    "yield_curve": ["discount factor", "interpolation", "conventions de taux"],
    "bond": ["actualisation de cash-flows", "rendement (YTM)"],
    "barrier": ["option vanilla", "delta/gamma", "notion de path-dependence"],
    "autocall": ["option vanilla", "barriere", "lecture de term sheet"],
    "monte_carlo": ["esperance et variance", "mouvement brownien geometrique", "intervalle de confiance"],
    "stochastic": ["calcul differentiel", "mouvement brownien", "esperance conditionnelle"],
    "cds": ["notion de defaut", "spread de credit", "actualisation"],
    "var": ["distribution normale", "quantile", "volatilite"],
    "vol_smile": ["prix d'option vanilla", "volatilite implicite", "inversion de Black-Scholes"],
    "generic": ["bases de finance de marche", "actualisation", "notion de risque"],
}

_LEVEL_AUDIENCE = {
    "beginner": "etudiant L3/M1, candidat en finance de marche, developpeur front-office debutant",
    "intermediate": "junior quant, analyste market risk, sales/structuring junior",
    "advanced": "quant confirme, trader junior, structureur",
    "expert": "quant senior, desk strat",
}


def prerequisites(topic_key: str) -> list[str]:
    return _PREREQUISITES.get(topic_key, _PREREQUISITES["generic"])


def audience_for(level: str) -> str:
    return _LEVEL_AUDIENCE.get(level, _LEVEL_AUDIENCE["intermediate"])
