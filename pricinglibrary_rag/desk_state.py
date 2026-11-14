"""Stateful Fixed-Income & Currency (FIC) trading room.

A live, evolving world: a MarketState advances through time via stochastic
processes (Vasicek rates, GBM FX/spot, Ornstein-Uhlenbeck credit spreads and
vols). Trader books hold positions that are MARKED TO MARKET on every tick, with
Greeks (DV01/CS01/vega/delta), carry/theta and P&L (intraday + since inception)
recomputed from deterministic pricers — never invented.

The TradingRoom is a process-level singleton so state persists across requests:
time really passes, books are live. Seeded RNG => reproducible and testable.
"""
from __future__ import annotations

import math
import random
import time
import uuid
import threading
from dataclasses import dataclass, field

# trading-day fraction per simulated tick of 1 second (8h day, 252d year)
_YEAR_SECONDS = 252 * 8 * 3600


def _ncdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _npdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def bs(S, K, r, sigma, T, kind="call", q=0.0):
    """Fast canonical scalar kernel; callers declare spot carry or forward q=r."""
    from .black_scholes import _option
    from .trusted_analytics import number
    for value,name,low,high in [(S,"spot",1e-8,1e12),(K,"strike",1e-8,1e12),(r,"rate",-1,1),
                                (sigma,"volatility",0,5),(T,"maturity",0,30),(q,"carry",-1,1)]:
        number(value,name,low,high)
    if kind not in {"call","put"}:raise ValueError("Option kind must be call or put.")
    result=_option(S,K,T,r,q,sigma,kind)
    return {"price":result["unitPrice"],**result["greeks"]}


# --- market state -----------------------------------------------------------
@dataclass
class MarketState:
    elapsed: float = 0.0           # years since start
    clock_seconds: int = 15 * 3600 + 42 * 60 + 18  # 15:42:18 like the mockup
    # rates: short level + slope per ccy (decimal)
    # level = 10Y anchor; slope shapes the curve around it (2s10s ~= slope*1.3)
    rates: dict = field(default_factory=lambda: {"EUR": {"level": 0.032, "slope": 0.003},
                                                 "USD": {"level": 0.0428, "slope": 0.003}})
    fx: dict = field(default_factory=lambda: {"EURUSD": 1.0712})
    credit: dict = field(default_factory=lambda: {"IG": 120.0})  # spread bp
    spots: dict = field(default_factory=lambda: {"SPX": 5872.34, "SX5E":5000.0, "WTI": 78.42, "GOLD": 2337.25,
                                                 "BRENT": 82.15, "BTC": 61250.0, "ETH": 3380.0})
    vols: dict = field(default_factory=lambda: {"SPX": 0.18, "WTI": 0.30, "BTC": 0.55, "ETH": 0.66})

    def par_rate(self, ccy: str, tenor: float) -> float:
        # level anchors the 10Y; the curve slopes around it (2Y below, long end above)
        c = self.rates[ccy]
        return c["level"] + c["slope"] * (math.log(tenor + 1) - math.log(11))

    def discount(self, ccy: str, t: float) -> float:
        return math.exp(-self.rates[ccy]["level"] * t)

    def annuity(self, ccy: str, tenor: float) -> float:
        n = max(1, round(tenor))
        return sum(self.discount(ccy, i) for i in range(1, n + 1))

    def clock_str(self) -> str:
        s = self.clock_seconds % 86400
        return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"


class MarketSimulator:
    def __init__(self, seed: int = 20260627):
        self.rng = random.Random(seed)

    def _z(self) -> float:
        return self.rng.gauss(0.0, 1.0)

    def tick(self, m: MarketState, seconds: float = 1.0) -> None:
        from .trusted_analytics import number
        seconds=number(seconds,'seconds',0,2678400)
        dt = seconds / _YEAR_SECONDS
        sq = math.sqrt(dt)
        # Vasicek short rates (mean-revert to anchor), gentle slope drift
        for ccy, anchor in (("EUR", 0.038), ("USD", 0.0428)):
            r = m.rates[ccy]
            r["level"] += 1.5 * (anchor - r["level"]) * dt + 0.012 * sq * self._z()
            r["slope"] += 0.5 * (0.003 - r["slope"]) * dt + 0.003 * sq * self._z()
            r["level"] = max(-0.01, r["level"])
        # FX GBM
        m.fx["EURUSD"] *= math.exp(-0.5 * 0.09 ** 2 * dt + 0.09 * sq * self._z())
        # credit spread OU (bp)
        s = m.credit["IG"]
        m.credit["IG"] = max(20.0, s + 8.0 * (120.0 - s) * dt + 35.0 * sq * self._z())
        # spots GBM, vols OU
        for k, drift, vol in (("SPX", 0.05, m.vols["SPX"]), ("SX5E",0.04,0.22), ("WTI", 0.0, m.vols["WTI"]),
                              ("GOLD", 0.02, 0.16), ("BRENT", 0.0, 0.30),
                              ("BTC", 0.10, m.vols["BTC"]), ("ETH", 0.10, m.vols["ETH"])):
            m.spots[k] *= math.exp((drift - 0.5 * vol ** 2) * dt + vol * sq * self._z())
        for k, anchor in (("SPX", 0.18), ("WTI", 0.30), ("BTC", 0.55), ("ETH", 0.66)):
            m.vols[k] = max(0.05, m.vols[k] + 2.0 * (anchor - m.vols[k]) * dt + 0.6 * sq * self._z())
        m.elapsed += dt
        m.clock_seconds += int(seconds)


# --- positions and books ----------------------------------------------------
@dataclass
class Position:
    id: str
    desk: str               # Rates | Credit | FX | Commodities
    kind: str               # swap | option | cds | fx_forward
    label: str
    ccy: str
    notional: float
    side: int               # +1 long/payer/protection-buyer, -1 opposite
    entry: dict             # snapshot of pricing inputs at entry
    maturity_years: float
    entry_t: float = 0.0
    mtm: float = 0.0
    prev_mtm: float = 0.0
    pnl_today: float = 0.0
    greeks: dict = field(default_factory=dict)

    def time_left(self, m: MarketState) -> float:
        return max(0.02, self.maturity_years - (m.elapsed - self.entry_t))

    def revalue(self, m: MarketState) -> None:
        self.prev_mtm = self.mtm
        T = self.time_left(m)
        if self.kind == "swap":
            par = m.par_rate(self.ccy, self.maturity_years)
            ann = m.annuity(self.ccy, self.maturity_years)
            self.mtm = self.side * (par - self.entry["par"]) * ann * self.notional
            self.greeks = {"dv01": round(ann * self.notional * 1e-4)}
        elif self.kind == "cds":
            ra = self.entry["risky_annuity"]
            self.mtm = self.side * (m.credit["IG"] - self.entry["spread"]) * 1e-4 * ra * self.notional
            self.greeks = {"cs01": round(ra * self.notional * 1e-4)}
        elif self.kind == "fx_forward":
            self.mtm = self.side * (m.fx["EURUSD"] - self.entry["rate"]) * self.notional
            self.greeks = {"fx_delta": round(self.side * self.notional)}
        elif self.kind == "option":
            u = self.entry["underlying"]
            S, vol = m.spots[u], m.vols.get(u, 0.2)
            rate=m.rates["USD"]["level"]
            o = bs(S, self.entry["strike"], rate, vol, T, self.entry.get("type", "call"),q=rate if u in {"WTI","BRENT","GOLD"} else 0)
            self.mtm = self.side * (o["price"] - self.entry["premium"]) * self.entry["contracts"]
            self.greeks = {"delta": round(self.side * o["delta"] * self.entry["contracts"], 1),
                           "vega": round(self.side * o["vega"] * self.entry["contracts"], 1)}
        else:
            self.mtm = 0.0
        self.pnl_today += (self.mtm - self.prev_mtm)


@dataclass
class Book:
    desk: str
    positions: list = field(default_factory=list)

    def pnl_today(self) -> float:
        return sum(p.pnl_today for p in self.positions)

    def dv01(self) -> float:
        return sum(p.greeks.get("dv01", 0) for p in self.positions)

    def cs01(self) -> float:
        return sum(p.greeks.get("cs01", 0) for p in self.positions)


class TradingRoom:
    def __init__(self, seed: int = 20260627):
        self.market = MarketState()
        self.paper_positions=[]
        self.paper_journal=[]
        self.paper_requests={}
        self.paper_lock=threading.RLock()
        self.sim = MarketSimulator(seed)
        self.books: dict[str, Book] = {d: Book(d) for d in ("Rates", "Credit", "FX", "Commodities", "CryptoVol")}
        self.orders: list[dict] = []
        self.limits = {"dv01": 5_000_000, "cs01": 2_000_000, "var": 5_000_000}
        self.last_wall = time.monotonic()
        self.pnl_curve: list[float] = []
        self._seed_book()
        self.revalue()

    # --- seed a realistic starter book (so the room is "live") -------------
    def _seed_book(self) -> None:
        m = self.market
        self.add_swap("EUR", 100_000_000, +1, 5.0, label="EUR 5Y payer")
        self.add_swap("EUR", 60_000_000, -1, 10.0, label="EUR 10Y receiver")
        self.add_swap("USD", 80_000_000, +1, 2.0, label="USD 2Y payer")
        self.add_cds(50_000_000, +1, label="IG 5Y protection")
        self.add_cds(30_000_000, -1, label="IG 5Y sold")
        self.add_fx_forward(25_000_000, +1, label="EURUSD 3M fwd")
        self.add_option("WTI", 1000, +1, 80.0, 5 / 12, label="WTI 5M call")
        self.add_option("SPX", 200, -1, 5900.0, 0.25, label="SPX 3M call (sold)")
        self.add_option("BTC", 10, +1, 65000.0, 2 / 12, label="BTC 2M call")
        self.add_option("ETH", 50, -1, 3600.0, 1 / 12, label="ETH 1M call (sold)")

    # --- tools used by the Trader/Execution agents -------------------------
    def add_swap(self, ccy, notional, side, tenor, label=""):
        m = self.market
        p = Position(id=_pid("SWP"), desk="Rates", kind="swap", label=label or f"{ccy} {tenor:g}Y swap",
                     ccy=ccy, notional=notional, side=side, maturity_years=tenor,
                     entry={"par": m.par_rate(ccy, tenor)}, entry_t=m.elapsed)
        self.books["Rates"].positions.append(p)
        return p

    def add_cds(self, notional, side, label=""):
        m = self.market
        p = Position(id=_pid("CDS"), desk="Credit", kind="cds", label=label or "IG CDS",
                     ccy="EUR", notional=notional, side=side, maturity_years=5.0,
                     entry={"spread": m.credit["IG"], "risky_annuity": 4.2}, entry_t=m.elapsed)
        self.books["Credit"].positions.append(p)
        return p

    def add_fx_forward(self, notional, side, label=""):
        m = self.market
        p = Position(id=_pid("FXF"), desk="FX", kind="fx_forward", label=label or "EURUSD fwd",
                     ccy="EUR", notional=notional, side=side, maturity_years=0.25,
                     entry={"rate": m.fx["EURUSD"]}, entry_t=m.elapsed)
        self.books["FX"].positions.append(p)
        return p

    def add_option(self, underlying, contracts, side, strike, tenor, label=""):
        m = self.market
        vol = m.vols.get(underlying, 0.2)
        rate=m.rates["USD"]["level"]
        prem = bs(m.spots[underlying], strike, rate, vol, tenor, "call",q=rate if underlying in {"WTI","BRENT","GOLD"} else 0)["price"]
        desk = {"WTI": "Commodities", "BTC": "CryptoVol", "ETH": "CryptoVol"}.get(underlying, "FX")
        p = Position(id=_pid("OPT"), desk=desk,
                     kind="option", label=label or f"{underlying} option", ccy="USD",
                     notional=contracts * strike, side=side, maturity_years=tenor,
                     entry={"underlying": underlying, "strike": strike, "premium": prem,
                            "contracts": contracts, "type": "call"}, entry_t=m.elapsed)
        self.books[p.desk].positions.append(p)
        return p

    # --- the clock ---------------------------------------------------------
    def tick(self, seconds: float = 1.0) -> None:
        self.sim.tick(self.market, seconds)
        self.revalue()

    def auto_tick(self) -> None:
        """Advance the market by the real wall-clock time since the last call."""
        now = time.monotonic()
        dt = min(max(now - self.last_wall, 0.0), 30.0)
        self.last_wall = now
        if dt > 0.05:
            self.tick(dt)

    def revalue(self) -> None:
        for b in self.books.values():
            for p in b.positions:
                p.revalue(self.market)
        self.pnl_curve.append(round(self.total_pnl()))
        self.pnl_curve = self.pnl_curve[-60:]

    def reset_session_pnl(self) -> None:
        for b in self.books.values():
            for p in b.positions:
                p.pnl_today = 0.0

    # --- aggregates --------------------------------------------------------
    def total_pnl(self) -> float:
        return sum(p.pnl_today for b in self.books.values() for p in b.positions)

    def total_dv01(self) -> float:
        return sum(b.dv01() for b in self.books.values())

    def total_cs01(self) -> float:
        return sum(b.cs01() for b in self.books.values())

    def positions_count(self) -> int:
        return sum(len(b.positions) for b in self.books.values())+len(self.paper_positions)

    def risk_status(self) -> str:
        dv = abs(self.total_dv01())
        if dv > self.limits["dv01"]:
            return "RED"
        if dv > 0.8 * self.limits["dv01"]:
            return "AMBER"
        return "GREEN"

    # --- snapshot for the frontend / agents --------------------------------
    def snapshot(self) -> dict:
        m = self.market
        from .paper_book import paper_snapshot
        paper=paper_snapshot(self)
        result={
            "clock": m.clock_str(),
            "elapsed_years": round(m.elapsed, 6),
            "market_watch": {
                "US 10Y": {"v": f"{m.par_rate('USD', 10) * 100:.2f}%"},
                "US 2Y": {"v": f"{m.par_rate('USD', 2) * 100:.2f}%"},
                "WTI": {"v": f"{m.spots['WTI']:.2f}"},
                "BRENT": {"v": f"{m.spots['BRENT']:.2f}"},
                "GOLD": {"v": f"{m.spots['GOLD']:,.2f}"},
                "EUR/USD": {"v": f"{m.fx['EURUSD']:.4f}"},
                "SPX": {"v": f"{m.spots['SPX']:,.2f}"},
                "SX5E": {"v": f"{m.spots['SX5E']:,.2f}"},
                "IG CDS": {"v": f"{m.credit['IG']:.0f}bp"},
                "BTC": {"v": f"{m.spots['BTC']:,.0f}"},
                "ETH": {"v": f"{m.spots['ETH']:,.0f}"},
                "BTC IV": {"v": f"{m.vols['BTC'] * 100:.1f}%"},
            },
            "spx": round(m.spots["SPX"], 2),
            "desk": {
                "pnl_today": round(self.total_pnl()),
                "dv01": round(self.total_dv01()),
                "cs01": round(self.total_cs01()),
                "risk_status": 'NOT_ASSESSED' if paper else self.risk_status(),
                "positions": self.positions_count(),
                "orders_in_flight": len(self.orders),
                "limit_usage": None if paper else round(abs(self.total_dv01()) / self.limits["dv01"], 3),
                "risk_scope":"Legacy seeded teaching book only; paper positions have no complete aggregate risk approval.",
                "pnl_curve": self.pnl_curve,
            },
            "books": {d: [{"id": p.id, "label": p.label, "kind": p.kind, "ccy": p.ccy,
                           "notional": p.notional, "side": p.side, "mtm": round(p.mtm),
                           "pnl_today": round(p.pnl_today), "greeks": p.greeks,
                           "time_left": round(p.time_left(m), 2)} for p in b.positions]
                      for d, b in self.books.items()},
        }
        for position in paper:result['books'].setdefault(position['desk'],[]).append(position)
        currencies={p['ccy'] for p in paper}
        result.update({'paper_positions':paper,'paper_journal':list(self.paper_journal),
                       'paper_summary':{'positions':len(paper),'pnl_by_currency':{c:sum(p['mtm'] for p in paper if p['ccy']==c) for c in currencies},'risk_status':'NOT_ASSESSED'},
                       'market_data_status':'simulated_teaching_inputs',
                       'seeded_book_notice':'Existing seed positions are teaching examples; they are separate from faithfully retained RFQ paper contracts.',
                       'paper_book_scope':'Private process-memory teaching book; constant-maturity scenario marks, no broker, settlement or real approval.'})
        return result


def _pid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"


# process-level singleton: the room lives across requests (stateful)
_ROOM: TradingRoom | None = None
_PRIVATE_ROOMS: dict[str,TradingRoom]={}
_ROOM_LOCK=threading.RLock()


def get_room(owner_id: str|None=None) -> TradingRoom:
    if owner_id is not None:
        if not isinstance(owner_id,str) or not 1<=len(owner_id)<=160:raise ValueError('A valid signed owner identifier is required.')
        with _ROOM_LOCK:
            if owner_id not in _PRIVATE_ROOMS:
                if len(_PRIVATE_ROOMS)>=128:raise RuntimeError('Teaching room capacity reached; no existing room was discarded.')
                _PRIVATE_ROOMS[owner_id]=TradingRoom()
            return _PRIVATE_ROOMS[owner_id]
    global _ROOM
    if _ROOM is None:
        _ROOM = TradingRoom()
    return _ROOM


from .paper_book import apply_desk_quote_to_book
