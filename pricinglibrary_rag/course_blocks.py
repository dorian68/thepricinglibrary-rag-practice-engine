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

    if has("vanilla", "black-scholes", "black scholes", "put-call", "put call"):
        return "vanilla_bs"
    if has("greek", "delta", "gamma", "vega", "theta"):
        return "greeks"
    if has("swap", "dv01", "par rate"):
        return "swap"
    if has("yield curve", "bootstrap", "discount factor", "zero curve", "forward rate"):
        return "yield_curve"
    if has("bond", "duration", "convexity", "ytm"):
        return "bond"
    if has("barrier", "barriere", "knock"):
        return "barrier"
    if has("autocall", "structured", "term sheet"):
        return "autocall"
    if has("monte carlo", "gbm", "asian", "variance reduction"):
        return "monte_carlo"
    if has("stochastic", "risk-neutral", "girsanov") or word("ito") or word("sde"):
        return "stochastic"
    if has("cds", "credit", "cs01", "spread"):
        return "cds"
    if word("var") or has("value at risk", "stress", "expected shortfall"):
        return "var"
    if has("vol", "smile", "skew", "implied vol", "svi"):
        return "vol_smile"
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
}

# Topics with no dedicated calculator reuse the closest worked example.
_WORKED_ALIAS = {
    "yield_curve": "swap",
    "autocall": "barrier",
    "monte_carlo": "vanilla_bs",
    "stochastic": "vanilla_bs",
    "vol_smile": "vanilla_bs",
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
                     "vol_smile": "vanilla_bs", "cds": "var"}.items():
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
