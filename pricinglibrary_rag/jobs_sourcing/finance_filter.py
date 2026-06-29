"""Finance-relevance filter so the board shows quant/markets roles, not noise.

Scores a posting on market-finance signal and assigns a desk category. A posting
is kept only when it clears the bar AND isn't an obvious non-market role
(accounting, AP/AR, retail banking) — what P1/P2 personas actually want.
"""
from __future__ import annotations

_STRONG = {
    "quant": 5, "quantitative": 5, "derivativ": 5, "trading": 4, "trader": 5,
    "structurer": 5, "structuring": 4, "market maker": 5, "market-making": 5,
    "fixed income": 4, "rates": 3, "credit": 2, "fx": 3, "volatility": 4,
    "options": 3, "exotics": 5, "pricing": 3, "risk": 2, "var": 2, "xva": 5,
    "portfolio manager": 4, "execution": 2, "hedge fund": 4, "asset management": 3,
    "sell-side": 3, "buy-side": 3, "equity research": 3, "financial engineer": 5,
    "model validation": 4, "counterparty risk": 4, "market risk": 4, "p&l": 2,
}
_WEAK = {"finance", "investment", "capital markets", "securities", "banking",
         "analyst", "treasury", "macro", "commodities", "fund"}
_NEGATIVE = {"accounts payable", "accounts receivable", "bookkeep", "payroll",
             "retail bank", "teller", "mortgage loan officer", "insurance agent",
             "tax preparer", "auditor of", "billing", "collections specialist",
             # finance-firm roles that are NOT market-finance jobs for our personas
             "customer success", "account manager", "account executive", "recruiter",
             "recruiting", "talent", "people ops", "human resources", "office manager",
             "executive assistant", "marketing", "sales development", "onboarding",
             "asic", "hardware", "fpga", "mechanical", "facilities", "receptionist",
             "aml", "kyc", "compliance officer", "paralegal", "graphic design"}

# Title-level market-finance signal: a posting must clearly BE a markets role,
# not merely sit at a finance firm. Used to reject "ASIC Engineer @ JaneStreet".
_TITLE_SIGNAL = ("quant", "trader", "trading", "structur", "derivativ", "exotic",
                 "fixed income", "rates ", "credit analyst", "fx ", "volatility",
                 "options", "market mak", "portfolio manager", "market risk",
                 "pricing", "xva", "financial engineer", "model valid", "research analyst",
                 "strategist", "investment analyst", "capital markets", "securities",
                 "execution trader", "risk analyst", "risk manager", "quantitative")

_CATEGORY = [
    (("quant", "quantitative", "financial engineer", "model valid"), "Quant"),
    (("trader", "trading", "market maker", "execution"), "Trading"),
    (("structur", "exotics", "derivativ"), "Structuring & Derivatives"),
    (("risk", "var", "xva", "counterparty"), "Risk"),
    (("fixed income", "rates", "credit", "fx", "bond"), "Rates & FIC"),
    (("research", "macro", "strategist"), "Research & Strategy"),
    (("portfolio", "asset management", "fund", "buy-side"), "Asset Management"),
]


def score(title: str, description: str | None = None, tags=None) -> int:
    hay = " ".join([title or "", description or "", " ".join(str(t) for t in (tags or []))]).lower()
    if any(n in hay for n in _NEGATIVE):
        return -10
    s = 0
    for kw, w in _STRONG.items():
        if kw in hay:
            s += w
    for kw in _WEAK:
        if kw in hay:
            s += 1
    # title hits weigh more than body-only hits
    tl = (title or "").lower()
    for kw, w in _STRONG.items():
        if kw in tl:
            s += w
    return s


def category(title: str, description: str | None = None) -> str:
    hay = (title or "").lower() + " " + (description or "").lower()
    for keys, cat in _CATEGORY:
        if any(k in hay for k in keys):
            return cat
    return "Finance"


def is_relevant(title: str, description: str | None = None, tags=None, *, threshold: int = 4) -> bool:
    tl = (title or "").lower()
    if any(n in tl for n in _NEGATIVE):
        return False
    # The TITLE must signal a markets role (not just a finance employer), and the
    # overall score must clear the bar. This kills "ASIC Engineer @ a hedge fund".
    if not any(sig in tl for sig in _TITLE_SIGNAL):
        return False
    return score(title, description, tags) >= threshold
