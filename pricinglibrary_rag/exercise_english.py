"""Authored English presentation of verified exercise calculations.

The numerical pack remains the audit record. This module changes presentation,
never recomputes a price, invents a source quote or calls a translation service.
French course prose is not republished or implicitly presented as English.
"""
from __future__ import annotations

import re
from dataclasses import replace

from .calculators import CalculationPack, CalculationStep


FAMILY_TITLES = {
    "vanilla_option_black_scholes": "European option pricing and Greeks",
    "options_book_greeks": "Delta, gamma, vega and theta P&L",
    "rates_swap_dv01": "Interest-rate swap PV and DV01",
    "bond_duration_dv01": "Bond DV01 and rate-shock P&L",
    "fx_barrier_option": "Barrier payoff and gap risk",
    "cds_cs01": "CDS spread risk, premium carry and default protection",
    "parametric_var": "Parametric VaR and Expected Shortfall",
    "autocall_structured": "Autocall cash flows and capital at risk",
    "monte_carlo_gbm": "Monte Carlo European call with sampling uncertainty",
    "yield_curve_bootstrap": "Single-curve discount factors and repricing",
    "implied_vol_smile": "Implied volatility from an observed option premium",
    "generic": "Model assumptions and risk controls",
}

# These explanations are original teaching text, not translated source excerpts.
# The unit conventions deliberately match the current calculator family.
FAMILY_RULES = {
    "vanilla_option_black_scholes": (
        ["European exercise; constant volatility, continuously compounded risk-free rate and continuous dividend yield.",
         "S and K use the same currency per underlying unit; T is in years. Vega is quoted per one volatility percentage point."],
        ["For a long call, sell the calculated call delta in underlying units per option to offset local delta. Reverse the sign for a short call.",
         "Check put-call parity using the same dividend yield and maturity on both sides. A delta hedge leaves gamma and vega risk."],
        ["This model excludes early exercise, transaction costs, jumps, smile and liquidity. A model value is not an executable market quote."]),
    "options_book_greeks": (
        ["Delta is EUR per 1% spot move; gamma is EUR per (1%) squared; vega is EUR per volatility point; theta is EUR per day.",
         "Use the numerical percentage-point shock: a -2% spot move is -2 in this book convention, not -0.02."],
        ["Identify the largest P&L contribution before choosing a hedge. Offset delta with the underlying or futures; options are needed to change vega and gamma.",
         "Recheck gamma as spot moves and distinguish the one-day theta carry from an exact repricing."],
        ["This is a local sensitivity approximation. Large or simultaneous shocks require a full repricing and compatible units."]),
    "rates_swap_dv01": (
        ["Single-curve, parallel-shift approximation. Signs are from the fixed-rate payer / floating-rate receiver perspective.",
         "Rates stated as percentages are divided by 100 in PV calculations; one basis point is 0.0001."],
        ["A fixed-rate payer gains from a rise in the par swap rate under this local approximation. Check the sign of PV against the fixed coupon and par rate.",
         "Offset the calculated DV01 with an opposite, matching-tenor rate exposure. Check key-rate and basis risk before treating the hedge as neutral."],
        ["A single DV01 does not capture curve shape, spread, collateral or discount/projection basis. Revalue large shocks."]),
    "bond_duration_dv01": (
        ["Duration is modified duration. The position is a long bond; the DV01 magnitude is positive and price falls when yield rises.",
         "First-order parallel yield shock; the notional convention is the one supplied in the case."],
        ["Use negative DV01 times an upward yield shock to estimate long-bond P&L. Hedge with an opposite rate sensitivity, then compare tenor exposures."],
        ["Convexity matters for large shocks. Clean/dirty price, accrued interest and credit-spread risk need separate checks."]),
    "fx_barrier_option": (
        ["Down-and-out call: touching the barrier during the contract extinguishes the option. A terminal spot above the barrier alone does not prove survival.",
         "Scenario payoffs are conditional on the stated barrier history. An analytic knock-out price is shown only when the calculator supports the supplied inputs."],
        ["Separate a terminal payoff from the present option value. Monitor distance to the barrier and the loss from a jump through it.",
         "Continuous delta hedging cannot eliminate barrier gap risk; control position size and state the monitoring convention."],
        ["An FX cash payoff uses the base-currency notional convention. An equity-style notional is converted into underlying units. Neither is a live quote."]),
    "cds_cs01": (
        ["Signs are from the protection buyer's perspective. CS01 is an approximate positive EUR-per-basis-point exposure to spread widening.",
         "Recovery is 40% unless explicitly stated otherwise; the calculator uses a spread-DV01 approximation, not a calibrated hazard curve.",
         "Annual premium is a yearly cash payment. Premium-leg PV is the discounted value of all future premiums."],
        ["Compare annual negative premium carry with jump-to-default protection. A protection buyer gains mark-to-market when spreads widen.",
         "Size an offset using the calculated CS01 and the hedge instrument's actual CS01. A credit index leaves single-name/index basis risk."],
        ["Risky annuity, recovery, discounting and default timing affect valuation. A spread shock is not a default-event loss."]),
    "parametric_var": (
        ["Zero-mean Gaussian returns over the stated horizon. Volatility must use the same time step as the horizon or be scaled consistently.",
         "VaR is a loss threshold at the specified confidence; Expected Shortfall is the mean loss beyond that threshold."],
        ["Compare VaR and Expected Shortfall with the stated limit and stress losses. Identify risk drivers before reducing the position.",
         "Escalate an actual limit breach; a probability threshold does not cap the possible loss."],
        ["Gaussian VaR can understate fat tails and gaps. VaR is not generally subadditive; Expected Shortfall is coherent under its usual conditions."]),
    "autocall_structured": (
        ["Observation levels are compared with the initial level. Autocall, coupon and capital-protection barriers are percentages of that level.",
         "Capital protection is observed at maturity in this case. A coupon-memory feature only applies when specified in the supplied terms."],
        ["Process observations in order, including missed coupons, early redemption and the terminal capital payment. Stop cash flows after an autocall.",
         "Distinguish investor cash receipts from profit after the initial investment. Explain the capital loss below protection and the nonlinear hedge risk."],
        ["These are scenario cash flows, not a present fair value. Market valuation needs a model for volatility, dividends and, for multi-asset products, correlation."]),
    "monte_carlo_gbm": (
        ["Risk-neutral GBM; European call, zero continuous dividend yield, constant volatility and rates; ACT/365F.",
         "The engine uses antithetic pairs. Standard error is calculated from independent pair means, not from incorrectly treating the two paths as independent."],
        ["Report the estimated value together with standard error, a 95% confidence interval and path count. Compare the closed-form benchmark on the same inputs.",
         "A benchmark outside one sampled confidence interval does not itself prove bias. Check convergence and repeat sampling."],
        ["A confidence interval describes sampling uncertainty under this model; it does not measure model risk or market liquidity."]),
    "yield_curve_bootstrap": (
        ["Spot-starting par swaps with annual fixed payments and the supplied ACT/365F year fractions.",
         "Discount factors use log-linear interpolation between pillars; extrapolation is not allowed. This educational single curve combines discounting and projection."],
        ["Reprice every calibration instrument and identify forwards by their actual start and end times. Use the relevant discount factor for each dated cash flow.",
         "Increasing discount factors or negative forwards are curve-shape diagnostics, not automatic calibration failures."],
        ["Production rates valuation needs the relevant calendars, stubs, collateral conventions and separate OIS/projection curves."]),
    "implied_vol_smile": (
        ["Invert a European call premium under Black-Scholes. The market premium must respect lower and upper no-arbitrage bounds.",
         "The bounded solver searches volatility from 0 to 500%, with at most 120 iterations and a price tolerance of 1e-12; dividend yield is zero in this calculator family."],
        ["Reprice with the solved volatility to recover the supplied premium. Compare multiple strikes only with compatible maturity and quoting conventions."],
        ["Implied volatility is a parameter matching a market premium under a chosen model, not a prediction of future realised volatility."]),
    "generic": (
        ["No supported numerical calculation was identified. Set the product, numerical inputs and conventions before attempting a valuation."],
        ["State which inputs and model are missing. Do not invent an option value, risk number or market quotation."],
        ["No engine-verified numerical answer is available for an unsupported calculation."]),
}

STEP_LABELS = {
    "Prix call": "Call price", "Prix put": "Put price",
    "Verification parite call-put": "Put-call parity check",
    "PV payer approx": "Approximate fixed-payer PV", "P&L shock taux": "Rate-shock P&L",
    "DV01 obligation": "Bond DV01", "Coupon annuel": "Annual premium",
    "PV jambe de prime": "Premium-leg PV",
    "Upfront SNAC (coupon fixe 100bp)": "SNAC upfront (100 bp standard coupon)",
    "P&L spread shock protection buyer": "Protection-buyer spread-shock P&L",
    "Comparaison a la limite VaR": "VaR limit utilisation",
    "Payoff total investisseur": "Total investor cash receipts",
    "Maturite - capital": "Maturity capital payment",
    "Prix knock-out (Reiner-Rubinstein + parite in-out)": "Knock-out price (Reiner-Rubinstein and in-out parity)",
    "Prix MC": "Monte Carlo price", "Erreur standard": "Standard error",
    "IC 95%": "95% confidence interval", "Reference Black-Scholes": "Black-Scholes benchmark",
    "Valeur intrinseque actualisee": "Discounted intrinsic value",
    "Inversion bornee": "Bounded implied-volatility inversion", "Controle": "Repricing check",
}

STEP_NOTES = {
    "Call price": "Model value per call, including the continuous dividend yield.",
    "Put price": "European put value with the same strike, maturity and dividend yield.",
    "Put-call parity check": "The two sides must agree under identical inputs and dividend conventions.",
    "Greeks": "Call delta is underlying units per option; gamma is per underlying price unit and vega is per volatility point. Put delta is call delta minus exp(-qT).",
    "d1/d2": "Normal-distribution arguments used consistently in prices and sensitivities.",
    "Approximate fixed-payer PV": "A payer with a fixed coupon above the current par rate has negative PV in this approximation.",
    "Rate-shock P&L": "Apply the position sign: a fixed-rate payer gains on rising par rates, whereas a long bond loses on rising yields.",
    "DV01": "Magnitude of the local cash-value change for a one-basis-point rate move.",
    "Bond DV01": "Positive magnitude; use a negative sign for long-bond P&L under a positive yield shock.",
    "Annual premium": "Cash paid per year by the protection buyer; distinguish this negative carry from premium-leg PV.",
    "Premium-leg PV": "Discounted value of all premium payments in the approximation, not one annual coupon.",
    "CS01": "Local mark-to-market sensitivity to one basis point of credit-spread widening.",
    "Jump-to-default (LGD 60%)": "Immediate default protection at the stated recovery, before other accrual/settlement conventions.",
    "SNAC upfront (100 bp standard coupon)": "The protection buyer pays positive upfront when the quoted spread exceeds the standard coupon.",
    "Protection-buyer spread-shock P&L": "Positive for spread widening under the protection-buyer sign convention.",
    "VaR": "Loss threshold exceeded with probability 1 minus the stated confidence under the Gaussian model.",
    "Expected Shortfall": "Conditional mean loss beyond VaR, which is at least VaR for this distribution.",
    "VaR limit utilisation": "Divide the computed VaR by the stated limit; a value above 100% is a breach.",
    "Total investor cash receipts": "Total coupons and redemption over the product life; subtract the initial investment to calculate profit.",
    "Maturity capital payment": "Apply the terminal protection condition only if no earlier autocall has terminated the contract.",
    "Knock-out price (Reiner-Rubinstein and in-out parity)": "Present option value under the supported analytic assumptions; this is distinct from the terminal payoff.",
    "Monte Carlo price": "Discounted expected payoff estimated from the simulated antithetic pairs.",
    "Standard error": "Sampling precision calculated using the independent effective sample units.",
    "95% confidence interval": "In repeated valid sampling, approximately 95% of these intervals cover the theoretical model price.",
    "Black-Scholes benchmark": "Closed-form control on the same model inputs; compare the gap with standard error and convergence.",
    "Discounted intrinsic value": "Lower no-arbitrage bound for the European call under the supplied assumptions.",
    "Bounded implied-volatility inversion": "The model volatility that recovers the supplied market premium within the solver tolerance.",
    "Repricing check": "Substitute the solved volatility back into the model and compare with the observed premium.",
}

# Restricted mathematical vocabulary from calculator strings. This is used only
# for units/formula labels and seed tickets, never to silently translate a book.
QUANT_PHRASES = {
    "ecart-type des moyennes de paires antithetiques": "standard deviation of antithetic pair means",
    "coupons manquants en interpolation log-lineaire des DF": "missing coupons use log-linear DF interpolation",
    "Rendement de dividende continu": "Continuous dividend yield",
    "taux sans risque": "risk-free rate", "année(s)": "year(s)",
    "Annuite (PV01) approximee depuis la maturite": "Annuity (PV01) estimated from maturity",
    "Risky PV01 SURVIE-actualisee": "Survival-discounted risky PV01",
    "Quantile normal exact": "Exact normal quantile", "pour une confiance de": "at confidence",
    "Distance initiale a la barriere": "Initial distance to barrier",
    "Effet memoire des coupons": "Coupon memory", "en mesure risque-neutre Q": "under risk-neutral measure Q",
    "graine visible": "visible seed", "echantillons effectifs": "effective samples",
    "Duration = duration MODIFIEE (sensibilite prix au taux), ici": "Modified duration (price sensitivity to yield)",
    "P&L delta": "Delta P&L", "P&L gamma": "Gamma P&L", "P&L vega": "Vega P&L", "P&L theta": "Theta P&L", "P&L total": "Total P&L",
    "en points de 1%": "in 1% points", "Somme coupons + remboursement": "Total coupons + redemption",
    "ratio final >= barriere protection": "terminal ratio >= protection barrier",
    "Notionnel * ratio final (sous la protection)": "Notional * terminal ratio (below protection)",
    "coupon en memoire": "coupon retained in memory", "rappel anticipe": "early redemption",
    "periodes dues": "due periods", "barriere autocall": "autocall barrier", "barriere coupon": "coupon barrier",
    "Payoff down-and-out call (valeur terminale)": "Down-and-out call terminal payoff",
    "parite in-out": "in-out parity", "par unite (soit": "per unit (equivalent to", "sur le notionnel)": "on the notional)",
    "par unite": "per unit", "C_vanille": "C_vanilla", "puis": "then", "soit": "equivalent to",
    "Spread (en decimal)": "Spread (decimal)", "Coupon annuel": "Annual premium",
    "paye par l'acheteur si spread > coupon": "paid by the protection buyer if spread > coupon",
    "VaR vs limite -> utilisation = VaR / limite": "VaR vs limit -> utilisation = VaR / limit",
    "DEPASSEMENT de limite": "LIMIT BREACH", "dans la limite": "within limit",
    "sigma tel que BS(sigma) = prix marche": "sigma such that BS(sigma) = market premium",
    "BS(vol implicite) vs prix marche": "BS(implied vol) vs market premium",
    "vol implicite": "implied volatility", "prix de marche": "market premium",
    "trouver la volatilite implicite": "solve for implied volatility", "volatilite implicite": "implied volatility",
    "convergence en": "convergence in", "residu": "residual", "controle ferme": "closed-form control",
    "a taux plat": "at flat rate", "EUR/an": "EUR/year", "EUR par jour": "EUR per day",
    "par observation avec memoire": "per observation with coupon memory", "sans memoire": "without memory",
    "barriere protection": "protection barrier", "de mouvement spot": "of spot movement",
    "Niveaux observes": "Observed levels", "niveau initial": "initial level",
    "Bootstrap de courbe, swaps par annuels": "Curve bootstrap, annual par swaps",
    "la courbe monte de": "curve rises by", "le taux monte de": "yield rises by",
    "Option barriere FX": "FX barrier option", "Autocall Athena sur indice": "Athena autocall on index",
    "VaR parametrique": "Parametric VaR", "annuite risquee": "risky annuity",
    "simple annualise": "annualised simple", "intervalle": "interval", "continu": "continuous",
    "actif": "enabled", "inactif": "disabled", "tirages": "samples", "trajectoires": "paths",
    "notionnel": "notional", "Notionnel": "Notional", "Annuite": "Annuity",
    "maturite": "maturity", "maturité": "maturity", "volatilite": "volatility",
    "confiance": "confidence", "portefeuille": "portfolio", "barriere": "barrier",
    "protection": "protection", "taux": "rate", "europeen": "European", "Valeur": "Value",
    "moyenne": "mean", "limite": "limit", "utilisation": "utilisation", "cible": "target",
    "memoire": "memory", "jour": "day", "jours": "days", "ans": "years", "an": "year",
}


def quant_english(text: str) -> str:
    """Preserve numbers/operators while localising a bounded calculator lexicon."""
    result = text
    for fr, en in sorted(QUANT_PHRASES.items(), key=lambda item: len(item[0]), reverse=True):
        # Never replace pieces of symbols/English words (e.g. "an" in "annuity").
        result = re.sub(r"(?<!\w)" + re.escape(fr) + r"(?!\w)", lambda _: en, result)
    result = re.sub(r"(?<=\d)a\b", "y", result)
    # Financial "par swap" and "par rate" must stay par, not become "per".
    result = re.sub(r"\bpar (?=(?:\d|(?:vol )?point\b|day\b|unit\b|observation\b))", "per ", result)
    result = re.sub(r"\bspot a (?=\d)", "spot at ", result, flags=re.I)
    return result


def english_pack(pack: CalculationPack) -> CalculationPack:
    assumptions, actions, warnings = FAMILY_RULES.get(pack.family, FAMILY_RULES["generic"])
    # Keep explicitly stated numerical assumptions (q, r, T, derived annuity,
    # confidence, seed, etc.) with their original digits and units. Engine IDs
    # and hashes remain in the raw audit pack, not in the learner's lesson.
    numerical_prefixes = ("Rendement de dividende continu", "Annuite (PV01)",
                          "Risky PV01 SURVIE", "Quantile normal exact",
                          "Distance initiale a la barriere", "Effet memoire des coupons",
                          "GBM en mesure risque-neutre", "Duration = duration MODIFIEE")
    numerical_assumptions = [quant_english(item) for item in pack.assumptions
                             if item.startswith(numerical_prefixes)]
    steps = []
    for step in pack.steps:
        label = STEP_LABELS.get(step.label, quant_english(step.label))
        if label.startswith("Observation "):
            note = "Apply the coupon or autocall condition in chronological order; include previously missed coupons only when memory applies."
        elif label.startswith("Scenario spot"):
            note = "Terminal payoff conditional on the stated barrier history; a knocked-out contract pays zero."
        elif label.startswith("DF "):
            note = "Discount factor calibrated to the stated instrument; verify that model quote matches the supplied market quote."
        elif label.startswith("Forward "):
            note = "The rate applies to exactly the displayed interval; continuous and simple annualised conventions are distinct."
        elif label.endswith("P&L"):
            note = "Use the book's declared risk units and the signed shock; this is a local contribution to total P&L."
        else:
            note = STEP_NOTES.get(label, "Use the stated formula, substituted inputs, units and position sign to explain the computed result.")
        steps.append(CalculationStep(label, quant_english(step.formula), quant_english(step.substitution),
                                     quant_english(step.result), note))
    # Curve-shape warnings already originate in English from the deterministic
    # curve engine; preserve them rather than reducing them to generic caveats.
    curve_diagnostics = [item for item in pack.warnings if pack.family == "yield_curve_bootstrap"
                         and item.startswith(("Negative forward", "Discount factors", "Absolute continuous", "Explicit 0 bp"))]
    curve_diagnostics += [item for item in pack.warnings if pack.family == "yield_curve_bootstrap"
                          and re.match(r"^\d+ swap coupon nodes", item)]
    return replace(pack, title=FAMILY_TITLES.get(pack.family, "Verified calculation"),
                   assumptions=[*assumptions, *numerical_assumptions], steps=steps,
                   desk_actions=list(actions), warnings=[*warnings, *curve_diagnostics, *([] if pack.steps else ["No numerical result was produced for these inputs."])])


def build_english_assessment(request, pack: CalculationPack) -> dict:
    view = english_pack(pack)
    count = request.number_of_questions
    focus = {
        "quantitative_problem": "justify the calculation and check units",
        "risk_management": "identify exposures and justify the hedge",
        "trading_decision": "justify a quoting or hedging decision",
        "case_study": "write a desk assessment supported by the supplied data",
        "mixed": "connect calculation, controls and the decision",
    }[request.exercise_format]
    questions = []
    assumptions = "\n".join(f"- {item}" for item in view.assumptions)
    actions = "\n".join(f"- {item}" for item in view.desk_actions)
    limits = "\n".join(f"- {item}" for item in view.warnings)

    def add(prompt, answer, criterion):
        questions.append({"number": len(questions) + 1, "prompt": prompt, "answer": answer, "criterion": criterion})

    if count >= 3:
        add(f"Identify the instrument, position and input conventions, then {focus}.",
            f"Calculation: **{view.title}**.\n\n{assumptions}",
            "Correct instrument, position sign, input units and pricing assumptions.")
    slots = max(1, min(len(view.steps), count - (2 if count >= 3 else 1 if count == 2 else 0)))
    groups = [view.steps[i * len(view.steps) // slots:(i + 1) * len(view.steps) // slots] for i in range(slots)]
    for steps in groups:
        names = ", ".join(step.label for step in steps) or "the missing input requirements"
        scaffold = ""
        if request.difficulty == "beginner":
            scaffold = " Hint: " + "; ".join(f"{step.label} = {step.formula}" for step in steps) + "."
        elif request.difficulty == "advanced":
            scaffold = " Justify conventions and distinguish a full model value from a local approximation."
        elif request.difficulty == "expert":
            scaffold = " Audit the assumptions and signs; explain when these outputs cease to be a reliable valuation."
        answer = "\n\n".join(f"**{step.label}**\n\n- Formula: `{step.formula}`\n- Substitution: `{step.substitution}`\n"
                              f"- Result: **{step.result}**\n- Interpretation: {step.desk_comment}" for step in steps)
        if request.difficulty in {"advanced", "expert"}:
            answer += "\n\n**Assumptions and limits**\n" + limits
        if count == 1:
            answer += "\n\n**Desk decision**\n" + actions
        add(f"Calculate {names}, then {focus}.{scaffold}", answer or assumptions,
            f"Correct formula, substitution, sign, units and interpretation for {names}.")
    reviews = [
        ("Check the units and time horizon of the calculated results.", assumptions),
        ("Explain the economic meaning of the outputs before choosing a hedge.", "\n".join(f"- {s.label}: {s.result}. {s.desk_comment}" for s in view.steps)),
        ("Identify assumptions to revalidate before reusing this calculation on a live ticket.", limits),
        ("Distinguish educational inputs from an executable market quotation.", "The numbers are supplied for this educational case; no live price or executable liquidity is established.\n" + assumptions),
        ("Describe the control needed before selecting the hedge instrument.", actions),
        ("Write a risk note without inventing sensitivities not calculated here.", limits + "\n" + actions),
        ("Explain the limits of reusing the output under another convention.", assumptions + "\n" + limits),
        ("Separate computed outputs from inputs still requiring desk confirmation.", "; ".join(s.label for s in view.steps) + "\n" + limits),
    ]
    while len(questions) < count - 1:
        prompt, answer = reviews[(len(questions) - slots - (1 if count >= 3 else 0)) % len(reviews)]
        add(prompt, answer, "An argued control tied to this model and its inputs; no invented output.")
    if len(questions) < count:
        add(f"Conclude: {focus}. State the action, monitoring trigger and model limitations.",
            actions + "\n\n**Limitations**\n" + limits,
            "Decision supported by the computed outputs, hedge direction and explicit limitations.")
    for i, question in enumerate(questions):
        question["points"] = 100 // count + (1 if i < 100 % count else 0)
    return {"question_count": count, "total_points": 100, "questions": questions,
            "grading_mode": "self_review", "difficulty": request.difficulty,
            "format": request.exercise_format, "language": "en"}


def english_exercise_template(request, title: str, pack: CalculationPack, scenario: str, references: str) -> str:
    from .exercise_assessment import assessment_markdown
    view = english_pack(pack)
    questions, answers, rubric = assessment_markdown(build_english_assessment(request, pack))
    input_lines = "\n".join(f"- {item}" for item in view.assumptions)
    targets = "\n".join(f"- {step.label}" for step in view.steps)
    actions = "\n".join(f"- {item}" for item in view.desk_actions)
    limits = "\n".join(f"- {item}" for item in view.warnings)
    equations = {
        "vanilla_option_black_scholes": r"$$d_1=\frac{\ln(S/K)+(r-q+\sigma^2/2)T}{\sigma\sqrt{T}},\qquad d_2=d_1-\sigma\sqrt{T}$$" + "\n\n" + r"$$C=S e^{-qT}N(d_1)-K e^{-rT}N(d_2)$$",
        "rates_swap_dv01": r"$$V_{\mathrm{payer}}=(R_{\mathrm{par}}-K)AN,\qquad |\mathrm{DV01}|=AN\times 10^{-4}$$",
        "options_book_greeks": r"$$\Delta V\simeq \Delta x+\frac12\Gamma x^2+\mathrm{Vega}\,\Delta\sigma+\Theta\,\Delta t$$",
    }.get(pack.family, "")
    # The ticket is the exact calculator scenario. A supplied French sentence
    # may retain its original wording; the surrounding teaching and answer key
    # are authored English, never passed off as translated source quotations.
    ticket = quant_english(scenario or "No additional numerical constraints were supplied.")
    return f"""# {title}

## Desk brief
You are asked to assess **{view.title}**. Produce a reproducible calculation,
explain the risk in plain English, and justify a quoting, hedging or escalation
decision. Keep model outputs separate from market observations.

## Level and format
- Level: {request.difficulty}
- Format: {request.exercise_format.replace('_', ' ')}
- Audience: {request.target_audience}
- Questions: {request.number_of_questions}
- Assessment: self-review against a verified numerical correction; no automatic certification.

## Problem
Calculator ticket (supplied numerical constraints; original user wording may be retained):

{ticket}

## Given data and assumptions
{input_lines}

Calculate:
{targets}

## Questions
{questions}

---

## Verified solution
{equations}

{answers}

### Desk decision
{actions}

### Model limitations
{limits}

## Assessment rubric
{rubric}

## References
Original source excerpts are kept in their source language; they are not generated translations.

{references}
""".strip()
