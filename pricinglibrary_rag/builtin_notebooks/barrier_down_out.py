"""Original TPL continuously monitored down-and-out call lab, zero rebate.
Closed form for H <= K, GBM; conditional Brownian-bridge MC with antithetic normals.
100,000 terminal draws = 50,000 independent antithetic pairs. No discrete-time bias.
"""
import json
import random
from math import exp, isfinite, log, sqrt
from statistics import NormalDist, mean, variance

TICKET = {"spot": 100.0, "strike": 100.0, "barrier": 85.0, "rate": 0.02, "volatility": 0.20, "maturity_years": 0.5, "paths": 100000, "seed": 7}

def vanilla_call(spot, strike, rate, volatility, maturity_years):
    root_variance = volatility * sqrt(maturity_years)
    d1 = (log(spot / strike) + (rate + 0.5 * volatility ** 2) * maturity_years) / root_variance
    normal = NormalDist().cdf
    return spot * normal(d1) - strike * exp(-rate * maturity_years) * normal(d1 - root_variance)

def run(ticket=None):
    ticket = dict(TICKET if ticket is None else ticket)
    S, K, H, r, sigma, T = [float(ticket[k]) for k in ["spot", "strike", "barrier", "rate", "volatility", "maturity_years"]]
    paths, seed = ticket["paths"], ticket["seed"]
    if not all(isfinite(x) for x in [S, K, H, r, sigma, T]) or not (0 < H <= K and H < S and 0 < sigma <= 3 and 0 < T <= 30 and abs(r) <= 0.5):
        raise ValueError("Supported ticket: 0 < H <= K, H < S, 0 < sigma <= 3, 0 < T <= 30 and abs(r) <= 0.5; zero dividends/rebate")
    if isinstance(paths, bool) or not isinstance(paths, int) or paths < 2 or paths > 200000 or paths % 2 or isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("paths must be an even integer in [2, 200000]; seed must be an integer")
    vanilla = vanilla_call(S, K, r, sigma, T)
    mu = (r - 0.5 * sigma ** 2) / sigma ** 2
    down_in = (H / S) ** (2 * mu) * vanilla_call(H * H / S, K, r, sigma, T)
    analytic = vanilla - down_in
    rng = random.Random(seed)
    discount = exp(-r * T)
    root_variance = sigma * sqrt(T)
    log_start = log(S / H)
    def discounted_bridge_payoff(z):
        terminal = S * exp((r - 0.5 * sigma ** 2) * T + root_variance * z)
        if terminal <= H:
            return 0.0
        survival_probability = 1.0 - exp(-2.0 * log_start * log(terminal / H) / (sigma ** 2 * T))
        return discount * max(terminal - K, 0.0) * survival_probability
    # Pair means are the independent observations for the MC standard error.
    pairs = []
    for _ in range(paths // 2):
        z = rng.gauss(0.0, 1.0)
        pairs.append(0.5 * (discounted_bridge_payoff(z) + discounted_bridge_payoff(-z)))
    estimate = mean(pairs)
    standard_error = sqrt(variance(pairs) / len(pairs)) if len(pairs) > 1 else None
    ci95 = [estimate - 1.96 * standard_error, estimate + 1.96 * standard_error] if standard_error is not None else None
    return {"schemaVersion": "1", "notebook_id": "barrier-down-out", "ticket": ticket,
            "model": "GBM continuous down-and-out call, zero rebate; H <= K", "closed_form_price": analytic,
            "vanilla_price": vanilla, "down_in_price": down_in, "mc_price": estimate,
            "standard_error": standard_error, "ci95": ci95, "independent_pairs": len(pairs),
            "method": "Conditional Brownian-bridge survival weighting with antithetic terminal normals",
            "limits": ["Non-dividend GBM, flat rate/volatility, continuous monitoring, zero rebate", "CI describes sampling error only, not model risk", "No path discretisation: this conditional estimator is not a generic path-dependent engine"]}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
