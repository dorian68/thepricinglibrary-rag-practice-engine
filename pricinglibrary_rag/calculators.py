from __future__ import annotations

import math
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CalculationStep:
    label: str
    formula: str
    substitution: str
    result: str
    desk_comment: str


@dataclass(frozen=True)
class CalculationPack:
    family: str
    title: str
    assumptions: list[str] = field(default_factory=list)
    steps: list[CalculationStep] = field(default_factory=list)
    desk_actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_markdown(self) -> str:
        if not self.steps and not self.assumptions and not self.desk_actions:
            return "- Aucun calcul automatique detecte. Le corrige doit expliciter les hypotheses et verifier les ordres de grandeur."
        lines = [f"### {self.title}", f"- Famille: {self.family}"]
        if self.assumptions:
            lines.append("- Hypotheses controlees:")
            lines.extend(f"  - {item}" for item in self.assumptions)
        if self.steps:
            lines.append("- Calculs a respecter:")
            for step in self.steps:
                lines.append(f"  - {step.label}:")
                lines.append(f"    - Formule: {step.formula}")
                lines.append(f"    - Application: {step.substitution}")
                lines.append(f"    - Resultat: {step.result}")
                lines.append(f"    - Lecture desk: {step.desk_comment}")
        if self.desk_actions:
            lines.append("- Actions operationnelles attendues:")
            lines.extend(f"  - {item}" for item in self.desk_actions)
        if self.warnings:
            lines.append("- Points de vigilance:")
            lines.extend(f"  - {item}" for item in self.warnings)
        return "\n".join(lines)

    def model_dump(self) -> dict:
        return {
            "family": self.family,
            "title": self.title,
            "assumptions": self.assumptions,
            "steps": [step.__dict__ for step in self.steps],
            "desk_actions": self.desk_actions,
            "warnings": self.warnings,
        }


class PracticeCalculator:
    """Small deterministic calculators for exercise answer keys.

    The goal is not to replace full pricers already present in the SaaS. This
    module supplies controlled desk-style approximations for pedagogical cases.
    """

    def build_pack(self, text: str, family_hint: str = "auto") -> CalculationPack:
        normalized = " ".join(text.split())
        calculators = {
            "options_book_greeks": self._options_book_pack,
            "rates_swap_dv01": self._swap_pack,
            "fx_barrier_option": self._barrier_pack,
            "bond_duration_dv01": self._bond_pack,
            "vanilla_option_black_scholes": self._vanilla_option_pack,
            "cds_cs01": self._cds_pack,
            "parametric_var": self._var_pack,
        }
        ordered = list(calculators.items())
        if family_hint != "auto" and family_hint in calculators:
            ordered = [(family_hint, calculators[family_hint])] + [
                item for item in ordered if item[0] != family_hint
            ]
        for _, calculator in ordered:
            pack = calculator(normalized)
            if pack is not None:
                return pack
        return CalculationPack(
            family="generic",
            title="Garde-fous generiques",
            warnings=[
                "Aucun calculateur specialise n'a reconnu toutes les donnees.",
                "Le corrige doit afficher les hypotheses, les formules et les ordres de grandeur.",
            ],
        )

    def _options_book_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if not all(term in lower for term in ["delta", "gamma", "vega", "theta"]):
            return None
        delta = self._extract_k_amount(lower, r"delta\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*k")
        gamma = self._extract_k_amount(lower, r"gamma\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*k")
        vega = self._extract_k_amount(lower, r"vega\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*k")
        theta = self._extract_k_amount(lower, r"theta\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*k")
        spot_move = self._extract_number(lower, r"spot\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        vol_move = self._extract_number(lower, r"vol(?:atilite|atility)?\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        if None in (delta, gamma, vega, theta, spot_move, vol_move):
            return None
        delta_pnl = delta * spot_move
        gamma_pnl = 0.5 * gamma * (spot_move**2)
        vega_pnl = vega * vol_move
        theta_pnl = theta
        total = delta_pnl + gamma_pnl + vega_pnl + theta_pnl
        return CalculationPack(
            family="options_book_greeks",
            title="P&L delta-gamma-vega-theta",
            assumptions=[
                "Les greeks sont deja exprimes en EUR par unite de risque operationnelle.",
                "Delta: EUR par 1% de mouvement spot.",
                "Gamma: EUR par (1%)^2 de mouvement spot.",
                "Vega: EUR par point de volatilite.",
                "Theta: EUR par jour.",
            ],
            steps=[
                CalculationStep("P&L delta", "Delta * move spot en points de 1%", f"{delta:,.0f} * ({spot_move:g})", f"{delta_pnl:,.0f} EUR", "Risque directionnel immediat du book."),
                CalculationStep("P&L gamma", "0.5 * Gamma * move^2", f"0.5 * {gamma:,.0f} * ({spot_move:g})^2", f"{gamma_pnl:,.0f} EUR", "Convexite du book; ici elle amplifie ou amortit le choc spot."),
                CalculationStep("P&L vega", "Vega * move vol", f"{vega:,.0f} * ({vol_move:g})", f"{vega_pnl:,.0f} EUR", "Exposition a la volatilite implicite."),
                CalculationStep("P&L theta", "Theta * 1 jour", f"{theta:,.0f} * 1", f"{theta_pnl:,.0f} EUR", "Carry temps journalier."),
                CalculationStep("P&L total", "Delta + Gamma + Vega + Theta", f"{delta_pnl:,.0f} + {gamma_pnl:,.0f} + {vega_pnl:,.0f} + {theta_pnl:,.0f}", f"{total:,.0f} EUR", "Point de depart du debrief intraday."),
            ],
            desk_actions=[
                "Identifier le facteur dominant du P&L avant toute couverture.",
                "Proposer une neutralisation delta avec sous-jacent/futures.",
                "Proposer une reduction vega avec options ou variance/vol instruments si disponibles.",
                "Surveiller le gamma si le spot continue a bouger intraday.",
            ],
            warnings=[
                "Ne pas multiplier une sensibilite 'par 1%' par -0.02; utiliser -2.",
                "Ce calcul est une approximation locale, pas une revalorisation complete du book.",
            ],
        )

    def _swap_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "swap" not in lower or not any(term in lower for term in ["dv01", "annuity", "annuite", "annuité"]):
            return None
        notional = self._extract_m_amount(lower, r"notionnel\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*m")
        fixed = self._extract_number(lower, r"(?:fixed coupon|taux fixe|coupon fixe)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        par = self._extract_number(lower, r"(?:par swap rate|taux swap actuel|par rate actuel)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        annuity = self._extract_number(lower, r"(?:annuity|annuite|annuité)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)")
        shock_bp = self._extract_number(lower, r"(?:monte|hausse|up|rise|shock)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*bp")
        if None in (notional, fixed, par, annuity):
            return None
        dv01 = annuity * notional * 0.0001
        payer_pv = (par / 100 - fixed / 100) * annuity * notional
        steps = [
            CalculationStep("DV01", "Annuite * Notionnel * 1bp", f"{annuity:g} * {notional:,.0f} * 0.0001", f"{dv01:,.0f} EUR/bp", "Sensibilite lineaire de la position a un bp de courbe."),
            CalculationStep("PV payer approx", "(Par rate - Fixed coupon) * Annuite * Notionnel", f"({par:g}% - {fixed:g}%) * {annuity:g} * {notional:,.0f}", f"{payer_pv:,.0f} EUR", "Un payer au-dessus du par rate est initialement hors-la-monnaie."),
        ]
        if shock_bp is not None:
            pnl = dv01 * shock_bp
            steps.append(
                CalculationStep("P&L shock taux", "DV01 * shock bp pour un payer", f"{dv01:,.0f} * {shock_bp:g}", f"{pnl:,.0f} EUR", "Un payer gagne quand les taux montent, perd quand ils baissent.")
            )
        return CalculationPack(
            family="rates_swap_dv01",
            title="PV/DV01 de swap de taux",
            assumptions=[
                "Approximation mono-courbe et parallel shift.",
                "Annuite fournie par le prompt, pas recalibree.",
                "Signe exprime du point de vue payer fixe / receiver flottant.",
            ],
            steps=steps,
            desk_actions=[
                "Comparer le signe de PV avec le sens payer/receiver.",
                "Hedger DV01 avec swap oppose, futures taux ou bond hedge selon le book.",
                "Expliquer le basis risk si la couverture n'est pas sur le meme tenor.",
            ],
        )

    def _barrier_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "barriere" not in lower and "barrier" not in lower:
            return None
        spot = self._extract_number(lower, r"spot\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        strike = self._extract_number(lower, r"(?:strike|prix d'exercice)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        barrier = (
            self._extract_number(lower, r"(?:barriere|barrière|barrier)\s+(?:down-and-out|down and out|up-and-out|up and out|knock-out|knock out|ko)\s*[:=]?\s*([+-]?\s*\d+(?:[.,]\d+)?)")
            or self._extract_number(lower, r"(?:barriere|barrière|barrier)\s+(?:de|a|à)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        )
        notional = self._extract_m_amount(lower, r"notionnel\s*(?:eur\s*)?([+-]?\s*\d+(?:[.,]\d+)?)\s*m")
        if None in (strike, barrier, notional):
            return None
        steps = []
        for raw in re.findall(r"spot\s*(?:a|à)\s*([+-]?\d+(?:[.,]\d+)?)", lower)[:6]:
            final_spot = self._parse_float(raw)
            if final_spot is None:
                continue
            if final_spot <= barrier:
                result = "0 USD"
                comment = "Barriere touchee ou atteinte: option eteinte."
                substitution = f"spot {final_spot:g} <= barriere {barrier:g}"
            else:
                payoff = max(final_spot - strike, 0) * notional
                result = f"{payoff:,.0f} USD approx"
                comment = "Payoff de call conditionnel au non knock-out."
                substitution = f"max({final_spot:g} - {strike:g}, 0) * {notional:,.0f}"
            steps.append(CalculationStep(f"Scenario spot {final_spot:g}", "Payoff down-and-out call", substitution, result, comment))
        assumptions = [
            "Down-and-out: si la barriere est touchee pendant la vie du produit, payoff final nul.",
            "Les scenarios non knock-out utilisent un payoff de call simple.",
        ]
        if spot is not None:
            assumptions.append(f"Distance initiale a la barriere: {(spot / barrier - 1) * 100:,.2f}%.")
        return CalculationPack(
            family="fx_barrier_option",
            title="Payoff et risque de gap d'une barriere",
            assumptions=assumptions,
            steps=steps,
            desk_actions=[
                "Surveiller le spot et le risque de gap proche barriere.",
                "Discuter hedge delta/gamma mais signaler la discontinuite de payoff.",
                "Prevoir escalation risk si le spot entre dans une zone de monitoring.",
            ],
            warnings=[
                "Une couverture delta continue peut echouer en cas de gap a travers la barriere.",
                "La valeur reelle requiert un modele barriere, pas seulement le payoff terminal.",
            ],
        )

    def _bond_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "bond" not in lower and "obligation" not in lower:
            return None
        price = self._extract_number(lower, r"(?:prix|price)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        duration = self._extract_number(lower, r"(?:duration|dv01 duration)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        notional = self._extract_m_amount(lower, r"notionnel\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*m")
        shock_bp = self._extract_number(lower, r"(?:monte|hausse|baisse|shock)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*bp")
        if None in (duration, notional, shock_bp):
            return None
        dv01 = duration * notional * 0.0001
        pnl = -dv01 * shock_bp
        return CalculationPack(
            family="bond_duration_dv01",
            title="DV01 et P&L obligataire",
            assumptions=["Approximation duration lineaire.", "Prix clean/dirty ignore si non precise."],
            steps=[
                CalculationStep("DV01 obligation", "Duration * Notionnel * 1bp", f"{duration:g} * {notional:,.0f} * 0.0001", f"{dv01:,.0f} EUR/bp", "Sensibilite taux de premier ordre."),
                CalculationStep("P&L shock taux", "-DV01 * shock bp", f"-{dv01:,.0f} * {shock_bp:g}", f"{pnl:,.0f} EUR", "Un long bond perd quand les taux montent."),
            ],
            desk_actions=["Hedger duration avec futures, swap ou bond benchmark.", "Verifier convexite si le choc est large."],
        )

    def _vanilla_option_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "black" not in lower and "vanilla" not in lower and "call" not in lower:
            return None
        spot = self._extract_number(lower, r"spot\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        strike = self._extract_number(lower, r"(?:strike|prix d'exercice)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        vol = self._extract_number(lower, r"(?:vol|volatilite|volatility)\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        maturity = self._extract_number(lower, r"(?:maturite|maturité|maturity)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        rate = self._extract_number(lower, r"(?:taux|rate|risk-free)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*%") or 0.0
        if None in (spot, strike, vol, maturity):
            return None
        sigma = vol / 100
        t = maturity
        r = rate / 100
        d1 = (math.log(spot / strike) + (r + 0.5 * sigma**2) * t) / (sigma * math.sqrt(t))
        d2 = d1 - sigma * math.sqrt(t)
        nd1 = self._norm_cdf(d1)
        nd2 = self._norm_cdf(d2)
        call = spot * nd1 - strike * math.exp(-r * t) * nd2
        delta = nd1
        gamma = self._norm_pdf(d1) / (spot * sigma * math.sqrt(t))
        vega = spot * self._norm_pdf(d1) * math.sqrt(t) / 100
        return CalculationPack(
            family="vanilla_option_black_scholes",
            title="Option vanilla Black-Scholes",
            assumptions=["Pas de dividende/carry si non precise.", "Volatilite et taux constants."],
            steps=[
                CalculationStep("d1/d2", "BS d1, d2", f"d1={d1:.4f}; d2={d2:.4f}", f"d1={d1:.4f}, d2={d2:.4f}", "Variables pivots du pricing et des greeks."),
                CalculationStep("Prix call", "S*N(d1)-K*exp(-rT)*N(d2)", f"{spot:g}*N({d1:.4f})-{strike:g}*exp(-{r:.4f}*{t:g})*N({d2:.4f})", f"{call:.4f}", "Valeur theorique du call."),
                CalculationStep("Greeks", "Delta=N(d1); Gamma=phi(d1)/(S sigma sqrt(T)); Vega=S phi(d1) sqrt(T)/100", f"inputs S={spot:g}, sigma={sigma:.2%}, T={t:g}", f"Delta={delta:.4f}; Gamma={gamma:.6f}; Vega/vol pt={vega:.4f}", "Base du hedge delta/vega."),
            ],
            desk_actions=["Comparer prix modele et prix marche.", "Hedger delta puis surveiller vega/gamma."],
        )

    def _cds_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "cds" not in lower and "credit default swap" not in lower:
            return None
        notional = self._extract_m_amount(lower, r"notionnel\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*m")
        spread = self._extract_number(lower, r"(?:spread|coupon)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*bp")
        risky_annuity = self._extract_number(lower, r"(?:risky annuity|annuite risquee|annuité risquée|risky pv01)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)")
        shock_bp = self._extract_number(lower, r"(?:widen|elarg|élarg|shock)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*bp")
        if None in (notional, spread, risky_annuity):
            return None
        cs01 = risky_annuity * notional * 0.0001
        premium = spread * cs01
        steps = [
            CalculationStep("CS01", "Risky annuity * Notionnel * 1bp", f"{risky_annuity:g} * {notional:,.0f} * 0.0001", f"{cs01:,.0f} EUR/bp", "Sensibilite approximative au spread de credit."),
            CalculationStep("Coupon annuel approx", "Spread bp * CS01", f"{spread:g} * {cs01:,.0f}", f"{premium:,.0f} EUR/an", "Ordre de grandeur du carry premium."),
        ]
        if shock_bp is not None:
            pnl = cs01 * shock_bp
            steps.append(CalculationStep("P&L spread shock protection buyer", "CS01 * shock bp", f"{cs01:,.0f} * {shock_bp:g}", f"{pnl:,.0f} EUR", "Un acheteur de protection gagne si le spread s'elargit."))
        return CalculationPack(
            family="cds_cs01",
            title="CS01 et carry CDS",
            assumptions=["Approximation spread-DV01; pas de bootstrap de hazard curve.", "Signe donne du point de vue acheteur de protection."],
            steps=steps,
            desk_actions=["Comparer carry et jump-to-default.", "Hedger indice/single-name en tenant compte du basis."],
        )

    def _var_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "var" not in lower and "value at risk" not in lower:
            return None
        value = self._extract_m_amount(lower, r"(?:portfolio|book|portefeuille|notionnel|valeur)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*m")
        vol = self._extract_number(lower, r"(?:vol|volatilite|volatility)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        confidence = self._extract_number(lower, r"(?:confidence|confiance|niveau)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*%") or 95.0
        horizon = self._extract_number(lower, r"(?:horizon|jour|jours)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)") or 1.0
        if None in (value, vol):
            return None
        z = 1.65 if confidence <= 95 else 2.33
        var = value * (vol / 100) * math.sqrt(horizon) * z
        return CalculationPack(
            family="parametric_var",
            title="VaR parametrique simple",
            assumptions=[f"Quantile normal z={z:g}.", "Volatilite donnee sur le meme pas de temps que l'horizon, sauf indication contraire."],
            steps=[
                CalculationStep("VaR", "Valeur * vol * sqrt(horizon) * z", f"{value:,.0f} * {vol / 100:.4f} * sqrt({horizon:g}) * {z:g}", f"{var:,.0f}", "Perte potentielle au niveau de confiance choisi."),
            ],
            desk_actions=["Comparer VaR et stress tests.", "Identifier les facteurs dominants du risque."],
            warnings=["La VaR ne capture pas correctement les queues extremes ni les risques de gap."],
        )

    def _extract_number(self, text: str, pattern: str) -> float | None:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            return None
        return self._parse_float(match.group(1))

    def _extract_k_amount(self, text: str, pattern: str) -> float | None:
        value = self._extract_number(text, pattern)
        if value is None:
            return None
        return value * 1000

    def _extract_m_amount(self, text: str, pattern: str) -> float | None:
        value = self._extract_number(text, pattern)
        if value is None:
            return None
        return value * 1_000_000

    def _parse_float(self, raw: str) -> float | None:
        cleaned = raw.replace(" ", "").replace(",", ".").replace("+", "")
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _norm_cdf(self, x: float) -> float:
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _norm_pdf(self, x: float) -> float:
        return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)
