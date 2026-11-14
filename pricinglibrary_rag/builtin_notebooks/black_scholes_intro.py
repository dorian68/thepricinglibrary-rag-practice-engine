"""Original TPL vanilla call lab. Flat continuous carry; no market data."""
import json
from math import exp, isfinite, log, sqrt
from statistics import NormalDist

TICKET = {"spot": 100.0, "strike": 100.0, "rate": 0.02, "dividend_yield": 0.0, "volatility": 0.20, "maturity_years": 0.5}

def call_price(spot, strike, rate, dividend_yield, volatility, maturity_years):
    values = [spot, strike, rate, dividend_yield, volatility, maturity_years]
    if not all(isfinite(float(x)) for x in values) or min(spot, strike, volatility, maturity_years) <= 0:
        raise ValueError("Finite inputs and positive spot/strike/volatility/maturity required")
    root_t = sqrt(maturity_years)
    d1 = (log(spot / strike) + (rate - dividend_yield + 0.5 * volatility ** 2) * maturity_years) / (volatility * root_t)
    d2 = d1 - volatility * root_t
    normal = NormalDist().cdf
    return spot * exp(-dividend_yield * maturity_years) * normal(d1) - strike * exp(-rate * maturity_years) * normal(d2)

def run(ticket=None):
    ticket = dict(TICKET if ticket is None else ticket)
    return {"schemaVersion": "1", "notebook_id": "black-scholes-intro", "ticket": ticket,
            "model": "Black-Scholes-Merton European call", "price_per_unit": call_price(**ticket),
            "scenarios": [{"spot": spot, "price_per_unit": call_price(**{**ticket, "spot": spot})} for spot in [80, 90, 100, 110, 120]],
            "limits": ["Flat volatility and continuous rates/yield", "European exercise; educational calculation, not an executable quote"]}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
