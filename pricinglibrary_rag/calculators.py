from __future__ import annotations

import math
import random
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
            "autocall_structured": self._autocall_pack,
            "monte_carlo_gbm": self._monte_carlo_pack,
            "yield_curve_bootstrap": self._yield_curve_pack,
            "implied_vol_smile": self._implied_vol_pack,
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
        disc_k = strike * math.exp(-r * t)
        call = spot * nd1 - disc_k * nd2
        put = disc_k * self._norm_cdf(-d2) - spot * self._norm_cdf(-d1)
        parity_rhs = spot - disc_k                      # C - P doit egaler S - K e^{-rT}
        delta = nd1
        gamma = self._norm_pdf(d1) / (spot * sigma * math.sqrt(t))
        vega = spot * self._norm_pdf(d1) * math.sqrt(t) / 100
        return CalculationPack(
            family="vanilla_option_black_scholes",
            title="Option vanilla Black-Scholes",
            assumptions=[
                "Pas de dividende ni de carry si non precise (sinon remplacer S par S*exp(-qT) dans d1 et le prix).",
                "Volatilite et taux constants; exercice europeen.",
            ],
            steps=[
                CalculationStep("d1/d2", "BS d1, d2", f"d1={d1:.4f}; d2={d2:.4f}", f"d1={d1:.4f}, d2={d2:.4f}", "Variables pivots du pricing et des greeks."),
                CalculationStep("Prix call", "S*N(d1)-K*exp(-rT)*N(d2)", f"{spot:g}*N({d1:.4f})-{strike:g}*exp(-{r:.4f}*{t:g})*N({d2:.4f})", f"{call:.4f}", "Valeur theorique du call."),
                CalculationStep("Prix put", "K*exp(-rT)*N(-d2)-S*N(-d1)", f"{strike:g}*exp(-{r:.4f}*{t:g})*N({-d2:.4f})-{spot:g}*N({-d1:.4f})", f"{put:.4f}", "Valeur theorique du put europeen de meme strike/maturite."),
                CalculationStep("Verification parite call-put", "C - P = S - K*exp(-rT)", f"{call:.4f} - {put:.4f} = {spot:g} - {disc_k:.4f}", f"{call - put:.4f} = {parity_rhs:.4f}", "Si les deux cotes ne collent pas, une quote est incoherente / arbitrable."),
                CalculationStep("Greeks", "Delta=N(d1); Gamma=phi(d1)/(S sigma sqrt(T)); Vega=S phi(d1) sqrt(T)/100", f"inputs S={spot:g}, sigma={sigma:.2%}, T={t:g}", f"Delta={delta:.4f}; Gamma={gamma:.6f}; Vega/vol pt={vega:.4f}", "Base du hedge delta/vega; delta du put = delta call - 1."),
            ],
            desk_actions=["Comparer prix modele et prix marche.", "Hedger delta puis surveiller vega/gamma.", "Verifier la parite call-put avant de coter les deux jambes."],
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
        annual_premium = spread * 0.0001 * notional       # coupon couru sur un an
        pv_premium_leg = annual_premium * risky_annuity    # = spread*bp * risky_annuity * notionnel
        jtd = notional - 0.4 * notional                    # LGD 60% par defaut: perte si defaut immediat
        steps = [
            CalculationStep("CS01", "Risky annuity * Notionnel * 1bp", f"{risky_annuity:g} * {notional:,.0f} * 0.0001", f"{cs01:,.0f} EUR/bp", "Sensibilite (approx) de la MtM au spread de credit."),
            CalculationStep("Coupon annuel", "Spread (en decimal) * Notionnel", f"{spread:g}bp * {notional:,.0f} = {spread / 100:g}% * {notional:,.0f}", f"{annual_premium:,.0f} EUR/an", "Prime PAYEE chaque annee par l'acheteur de protection (carry negatif pour lui)."),
            CalculationStep("PV jambe de prime", "Coupon annuel * Risky annuity", f"{annual_premium:,.0f} * {risky_annuity:g}", f"{pv_premium_leg:,.0f} EUR", "Valeur actualisee de TOUTES les primes futures; ne pas la confondre avec le coupon annuel."),
            CalculationStep("Jump-to-default (LGD 60%)", "(1 - Recovery) * Notionnel", f"(1 - 0.40) * {notional:,.0f}", f"{jtd:,.0f} EUR", "Gain de l'acheteur de protection si defaut immediat; a comparer au carry paye."),
        ]
        if shock_bp is not None:
            pnl = cs01 * shock_bp
            steps.append(CalculationStep("P&L spread shock protection buyer", "CS01 * shock bp", f"{cs01:,.0f} * {shock_bp:g}", f"{pnl:,.0f} EUR", "Un acheteur de protection gagne en MtM si le spread s'elargit."))
        return CalculationPack(
            family="cds_cs01",
            title="CS01, carry et jump-to-default CDS",
            assumptions=[
                "Approximation spread-DV01; pas de bootstrap de hazard curve.",
                "Signe donne du point de vue acheteur de protection.",
                "Recovery 40% (LGD 60%) si non precise.",
            ],
            steps=steps,
            desk_actions=[
                "Comparer carry annuel paye et jump-to-default protege.",
                "Distinguer coupon annuel (cash/an) et PV de la jambe de prime (valeur du contrat).",
                "Hedger indice/single-name en tenant compte du basis.",
            ],
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
        alpha = confidence / 100
        z = self._norm_inv(alpha)
        sigma_h = (vol / 100) * math.sqrt(horizon)
        var = value * sigma_h * z
        # Parametric (Gaussian) Expected Shortfall: E[loss | loss > VaR].
        es = value * sigma_h * self._norm_pdf(z) / (1 - alpha)
        return CalculationPack(
            family="parametric_var",
            title="VaR et Expected Shortfall parametriques",
            assumptions=[
                f"Quantile normal exact z={z:.4f} pour une confiance de {confidence:g}%.",
                "Rendements gaussiens de moyenne nulle sur l'horizon.",
                "Volatilite exprimee sur le meme pas de temps que l'horizon (sinon mise a l'echelle en sqrt(horizon)).",
            ],
            steps=[
                CalculationStep("VaR", "Valeur * vol * sqrt(horizon) * z(alpha)", f"{value:,.0f} * {vol / 100:.4f} * sqrt({horizon:g}) * {z:.4f}", f"{var:,.0f}", "Perte seuil non depassee avec une probabilite alpha."),
                CalculationStep("Expected Shortfall", "Valeur * vol * sqrt(horizon) * phi(z)/(1-alpha)", f"{value:,.0f} * {vol / 100:.4f} * sqrt({horizon:g}) * {self._norm_pdf(z):.4f}/{1 - alpha:.4f}", f"{es:,.0f}", "Perte moyenne CONDITIONNELLE au-dela de la VaR; toujours >= VaR."),
            ],
            desk_actions=[
                "Comparer VaR et Expected Shortfall a la limite et aux stress tests.",
                "Si l'ES est tres au-dessus de la VaR, la queue est lourde: prioriser les stress scenarios.",
                "Identifier les facteurs dominants du risque avant de reduire.",
            ],
            warnings=[
                "La VaR parametrique sous-estime les queues epaisses et ignore le gap risk.",
                "La VaR n'est pas sous-additive en general: agreger des VaR par desk peut sous-estimer le risque; l'Expected Shortfall, lui, est coherent (sous-additif).",
            ],
        )

    def _autocall_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "autocall" not in lower and "athena" not in lower and "phoenix" not in lower:
            return None
        initial = self._extract_number(lower, r"(?:niveau initial|initial|spot)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        ac_bar = self._extract_number(lower, r"(?:barriere autocall|autocall)\s*(?:de|a|à|:|=)?\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        cpn_bar = self._extract_number(lower, r"(?:barriere coupon|coupon barrier)\s*(?:de|a|à|:|=)?\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        prot_bar = self._extract_number(lower, r"(?:barriere protection|protection)\s*(?:de|a|à|:|=)?\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        coupon = self._extract_number(lower, r"(?<!barriere )coupon\s*(?:de\s*)?([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        notional = (self._extract_m_amount(lower, r"notionnel\s*(?:eur\s*)?([+-]?\s*\d+(?:[.,]\d+)?)\s*m")
                    or self._extract_number(lower, r"notionnel\s*(?:eur\s*)?([+-]?\s*\d+(?:[.,]\d+)?)"))
        levels_txt = re.search(r"(?:niveaux observes|observations|niveaux|observes)\s*[:=]?\s*([0-9.,\s]+)", lower)
        levels = []
        if levels_txt:
            for tok in re.split(r"[,\s]+", levels_txt.group(1).strip()):
                v = self._parse_float(tok)
                if v is not None:
                    levels.append(v)
        if None in (initial, ac_bar, cpn_bar, prot_bar, coupon, notional) or not levels:
            return None
        memory = "memoire" in lower or "mémoire" in lower or "memory" in lower
        ac, cb, pb, cr = ac_bar / 100, cpn_bar / 100, prot_bar / 100, coupon / 100
        steps: list[CalculationStep] = []
        pending = 0
        paid = 0.0
        called_at = None
        redemption = 0.0
        for i, lvl in enumerate(levels, start=1):
            ratio = lvl / initial
            pending += 1
            if ratio >= cb:
                pay = cr * pending * notional
                paid += pay
                detail = f"niveau {lvl:g} (ratio {ratio:.2%}) >= barriere coupon {cpn_bar:g}%: paie {pending} coupon(s)" + (" (memoire)" if memory and pending > 1 else "")
                steps.append(CalculationStep(f"Observation {i} - coupon", "coupon * periodes dues * notionnel", f"{cr:g} * {pending} * {notional:,.0f}", f"+{pay:,.0f} EUR", detail))
                pending = 0
            else:
                steps.append(CalculationStep(f"Observation {i} - coupon", "ratio < barriere coupon", f"ratio {ratio:.2%} < {cpn_bar:g}%", "0 EUR (coupon en memoire)" if memory else "0 EUR", "Coupon non paye; mis en memoire pour la prochaine observation." if memory else "Coupon perdu (pas de memoire)."))
            if ratio >= ac:
                called_at = i
                redemption = notional
                steps.append(CalculationStep(f"Observation {i} - autocall", "ratio >= barriere autocall", f"ratio {ratio:.2%} >= {ac_bar:g}%", f"rappel anticipe: +{notional:,.0f} EUR", "Le produit est rappele: remboursement du nominal puis arret."))
                break
        if called_at is None:
            final_ratio = levels[-1] / initial
            if final_ratio >= pb:
                redemption = notional
                steps.append(CalculationStep("Maturite - capital", "ratio final >= barriere protection", f"{final_ratio:.2%} >= {prot_bar:g}%", f"+{notional:,.0f} EUR", "Capital protege: remboursement au pair."))
            else:
                redemption = notional * final_ratio
                loss = redemption - notional
                steps.append(CalculationStep("Maturite - capital", "Notionnel * ratio final (sous la protection)", f"{notional:,.0f} * {final_ratio:.4f}", f"{redemption:,.0f} EUR ({loss:,.0f})", "Barriere de protection franchie: perte 1:1 sur la baisse."))
        total = paid + redemption
        steps.append(CalculationStep("Payoff total investisseur", "Somme coupons + remboursement", f"{paid:,.0f} + {redemption:,.0f}", f"{total:,.0f} EUR", "Cash total recu sur la vie du produit."))
        return CalculationPack(
            family="autocall_structured",
            title="Payoff d'un autocall (Athena a memoire)",
            assumptions=[
                "Observations periodiques fournies; chaque niveau compare au niveau initial.",
                f"Effet memoire des coupons: {'actif' if memory else 'inactif'}.",
                "Barriere autocall, coupon et protection en % du niveau initial.",
                "Protection du capital de type europeenne (observee a maturite).",
            ],
            steps=steps,
            desk_actions=[
                "Identifier le scenario dominant: rappel anticipe (probable si spot eleve) ou perte en capital.",
                "Lire la sensibilite vendeur: short put down-and-in + short calls digitaux (autocall = combinaison d'options).",
                "Surveiller le gap pres de la barriere de protection a l'approche de la maturite.",
            ],
            warnings=[
                "Le prix reel exige un modele (Monte Carlo sous vol/dividendes/correlation), pas seulement le payoff de scenarios.",
                "Le risque vendeur est non lineaire et path-dependent: la protection peut sauter pres de la barriere.",
            ],
        )

    def _monte_carlo_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "monte carlo" not in lower and "monte-carlo" not in lower and "simulation" not in lower:
            return None
        spot = self._extract_number(lower, r"spot\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        strike = self._extract_number(lower, r"(?:strike|prix d'exercice)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        vol = self._extract_number(lower, r"(?:vol|volatilite|volatility)\s*([+-]?\s*\d+(?:[.,]\d+)?)\s*%")
        maturity = self._extract_number(lower, r"(?:maturite|maturité|maturity)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        rate = self._extract_number(lower, r"(?:taux|rate|risk-free)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*%") or 0.0
        paths = self._extract_number(lower, r"(\d[\d ]{2,})\s*(?:simulations|paths|tirages|trajectoires)")
        if None in (spot, strike, vol, maturity):
            return None
        n = int(paths) if paths else 20000
        n = max(2, n - (n % 2))  # even for antithetic pairing
        sigma, t, r = vol / 100, maturity, rate / 100
        drift = (r - 0.5 * sigma**2) * t
        diff = sigma * math.sqrt(t)
        rng = random.Random(20240617)  # fixed seed -> deterministic & reproducible
        disc = math.exp(-r * t)
        payoffs: list[float] = []
        for _ in range(n // 2):
            z = rng.gauss(0.0, 1.0)
            for zz in (z, -z):  # antithetic variates (variance reduction)
                st = spot * math.exp(drift + diff * zz)
                payoffs.append(max(st - strike, 0.0))
        mean_p = sum(payoffs) / len(payoffs)
        price = disc * mean_p
        var_p = sum((p - mean_p) ** 2 for p in payoffs) / (len(payoffs) - 1)
        se = disc * math.sqrt(var_p) / math.sqrt(len(payoffs))
        ci_lo, ci_hi = price - 1.96 * se, price + 1.96 * se
        # closed-form BS reference for the desk to compare against
        d1 = (math.log(spot / strike) + (r + 0.5 * sigma**2) * t) / (sigma * math.sqrt(t))
        d2 = d1 - sigma * math.sqrt(t)
        bs_ref = spot * self._norm_cdf(d1) - strike * math.exp(-r * t) * self._norm_cdf(d2)
        return CalculationPack(
            family="monte_carlo_gbm",
            title="Pricing Monte Carlo d'un call (GBM) avec intervalle de confiance",
            assumptions=[
                f"GBM risque-neutre, {n:,} trajectoires, graine fixe (resultat reproductible).",
                "Variates antithetiques pour reduire la variance.",
                "Pas de dividende si non precise; vol et taux constants.",
            ],
            steps=[
                CalculationStep("Simulation S_T", "S_T = S0*exp((r-0.5*sigma^2)T + sigma*sqrt(T)*Z)", f"S0={spot:g}, drift={drift:.4f}, diffusion={diff:.4f}", f"{n:,} tirages", "Echantillon de prix terminaux sous mesure risque-neutre."),
                CalculationStep("Prix MC", "exp(-rT) * moyenne(max(S_T-K,0))", f"exp(-{r:.4f}*{t:g}) * {mean_p:.4f}", f"{price:.4f}", "Estimateur du prix; converge en 1/sqrt(N)."),
                CalculationStep("Erreur standard", "exp(-rT)*ecart-type(payoff)/sqrt(N)", f"{disc:.4f}*{math.sqrt(var_p):.4f}/sqrt({len(payoffs)})", f"{se:.4f}", "Precision de l'estimateur; diminue en 1/sqrt(N)."),
                CalculationStep("IC 95%", "Prix +/- 1.96 * SE", f"{price:.4f} +/- {1.96 * se:.4f}", f"[{ci_lo:.4f}; {ci_hi:.4f}]", "L'intervalle doit contenir le prix Black-Scholes ferme."),
                CalculationStep("Reference Black-Scholes", "S*N(d1)-K*exp(-rT)*N(d2)", f"controle ferme", f"{bs_ref:.4f}", "Benchmark analytique: le MC doit tomber dans l'IC."),
            ],
            desk_actions=[
                "Augmenter N pour resserrer l'IC (cout en 1/sqrt(N)).",
                "Utiliser antithetiques/variables de controle pour reduire la variance a cout egal.",
                "Verifier que le prix ferme tombe dans l'IC: sinon, biais d'implementation.",
            ],
            warnings=["Un IC etroit ne corrige pas un biais de modele (drift, discretisation, payoff path-dependent)."],
        )

    def _yield_curve_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "bootstrap" not in lower and "courbe" not in lower and "yield curve" not in lower:
            return None
        pairs = re.findall(r"(\d+)\s*an[s]?\s*([0-9]+(?:[.,][0-9]+)?)\s*%", lower)
        if len(pairs) < 2:
            pairs = re.findall(r"([0-9]+(?:[.,][0-9]+)?)\s*%\s*(?:a|à)?\s*(\d+)\s*an", lower)
            pairs = [(m, r) for (r, m) in pairs]
        if len(pairs) < 2:
            return None
        nodes = sorted(((int(m), self._parse_float(r) / 100) for m, r in pairs), key=lambda x: x[0])
        steps: list[CalculationStep] = []
        dfs: list[float] = []
        cum = 0.0
        for mat, s in nodes:
            df = (1 - s * cum) / (1 + s)
            dfs.append(df)
            cum += df
            zero = df ** (-1 / mat) - 1
            steps.append(CalculationStep(
                f"DF {mat}a (par {s:.2%})",
                "DF_n = (1 - s_n*sum(DF_<n)) / (1 + s_n)",
                f"(1 - {s:.4f}*{cum - df:.4f}) / (1 + {s:.4f})",
                f"DF={df:.4f}; zero {mat}a={zero:.4%}",
                "Discount factor bootstrappe puis taux zero-coupon annualise.",
            ))
        fwds = []
        for i in range(1, len(dfs)):
            f = dfs[i - 1] / dfs[i] - 1
            fwds.append(f)
            steps.append(CalculationStep(
                f"Forward {nodes[i - 1][0]}a->{nodes[i][0]}a",
                "f = DF_{n-1}/DF_n - 1",
                f"{dfs[i - 1]:.4f}/{dfs[i]:.4f} - 1",
                f"{f:.4%}",
                "Taux forward 1 an implicite entre deux noeuds.",
            ))
        return CalculationPack(
            family="yield_curve_bootstrap",
            title="Bootstrap de courbe et taux forward",
            assumptions=[
                "Swaps par annuels, frequence fixe annuelle, day-count simplifie.",
                "Mono-courbe (pas de spread OIS/IBOR), interpolation implicite par noeud.",
            ],
            steps=steps,
            desk_actions=[
                "Verifier la monotonie/cohrence des DF (decroissants) et des forwards.",
                "Utiliser les DF pour actualiser tout cash-flow date sur la courbe.",
                "Reprendre en multi-courbe (OIS discounting) pour un usage production.",
            ],
            warnings=["Le bootstrap est sensible aux instruments choisis et a l'interpolation entre noeuds."],
        )

    def _implied_vol_pack(self, text: str) -> CalculationPack | None:
        lower = text.lower()
        if "implicite" not in lower and "implied" not in lower and "smile" not in lower:
            return None
        spot = self._extract_number(lower, r"spot\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        strike = self._extract_number(lower, r"(?:strike|prix d'exercice)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        maturity = self._extract_number(lower, r"(?:maturite|maturité|maturity)\s*([+-]?\s*\d+(?:[.,]\d+)?)")
        rate = self._extract_number(lower, r"(?:taux|rate|risk-free)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)\s*%") or 0.0
        price = self._extract_number(lower, r"(?:prix de marche|prix marche|prix|market price|premium)[^\d+-]*([+-]?\s*\d+(?:[.,]\d+)?)")
        if None in (spot, strike, maturity, price):
            return None
        t, r = maturity, rate / 100
        sqt = math.sqrt(t)

        def bs_call(sig: float) -> float:
            d1 = (math.log(spot / strike) + (r + 0.5 * sig**2) * t) / (sig * sqt)
            d2 = d1 - sig * sqt
            return spot * self._norm_cdf(d1) - strike * math.exp(-r * t) * self._norm_cdf(d2)

        sig = 0.20  # Newton seed
        iters = 0
        for iters in range(1, 101):
            d1 = (math.log(spot / strike) + (r + 0.5 * sig**2) * t) / (sig * sqt)
            vega = spot * self._norm_pdf(d1) * sqt  # per unit vol
            diff = bs_call(sig) - price
            if vega < 1e-10:
                break
            step = diff / vega
            sig -= step
            sig = min(max(sig, 1e-4), 5.0)
            if abs(step) < 1e-8:
                break
        intrinsic = max(spot - strike * math.exp(-r * t), 0.0)
        return CalculationPack(
            family="implied_vol_smile",
            title="Volatilite implicite (inversion de Black-Scholes)",
            assumptions=[
                "On inverse le prix de marche d'un call vanilla pour retrouver sigma.",
                "Newton-Raphson amorce a 20%, derivee = vega.",
                "Prix de marche superieur a la valeur intrinseque (sinon pas de solution).",
            ],
            steps=[
                CalculationStep("Valeur intrinseque actualisee", "max(S - K*exp(-rT), 0)", f"max({spot:g} - {strike:g}*exp(-{r:.4f}*{t:g}), 0)", f"{intrinsic:.4f}", "Plancher du prix; le market price doit etre au-dessus."),
                CalculationStep("Inversion Newton", "sigma tel que BS(sigma) = prix marche", f"convergence en {iters} iterations", f"vol implicite = {sig:.4%}", "Volatilite que le marche 'price' dans cette option."),
                CalculationStep("Controle", "BS(vol implicite) vs prix marche", f"BS({sig:.4f}) = {bs_call(sig):.4f}", f"cible {price:g}", "Le reprix avec la vol trouvee doit redonner le prix de marche."),
            ],
            desk_actions=[
                "Repeter par strike pour tracer le smile/skew (vol implicite = f(strike)).",
                "Comparer la vol implicite a la vol realisee pour juger cher/pas cher.",
                "Surveiller la pente (skew) et la courbure: signal de risque de queue price par le marche.",
            ],
            warnings=["La vol implicite n'est PAS une prevision: c'est le parametre qui recolle le prix de marche au modele BS."],
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

    def _norm_inv(self, p: float) -> float:
        """Inverse standard-normal CDF, exact to machine precision.

        Acklam rational seed refined with Halley steps against this class' own
        erf-based CDF, so the quantile is internally consistent with _norm_cdf
        and correct for any confidence level (not a hard-coded 1.65/2.33)."""
        if not 0.0 < p < 1.0:
            raise ValueError("p must be in (0,1)")
        a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
             1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
        b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
             6.680131188771972e+01, -1.328068155288572e+01)
        c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
             -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
        d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
             3.754408661907416e+00)
        plow, phigh = 0.02425, 1 - 0.02425
        if p < plow:
            q = math.sqrt(-2 * math.log(p))
            x = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
        elif p > phigh:
            q = math.sqrt(-2 * math.log(1 - p))
            x = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
        else:
            q = p - 0.5
            r = q * q
            x = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
        for _ in range(2):  # Halley refinement against own CDF
            e = self._norm_cdf(x) - p
            u = e / self._norm_pdf(x)
            x = x - u / (1 + x * u / 2)
        return x
