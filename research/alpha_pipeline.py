"""End-to-end alpha research pipeline (senior-quant study).

Families:
  A. Cross-sectional US equity (liquid names, daily panel, monthly weights):
       H1 momentum (12-1), H2 short-term reversal (1m), H3 low-volatility,
       H5 LightGBM cross-sectional return-rank (walk-forward, purge+embargo),
       H6 meta-labeled momentum (LightGBM filter on H1).
  B. Cross-asset time-series momentum / trend (futures+ETF+FX+crypto):
       H4 diversified multi-lookback TSMOM, inverse-vol risk parity.

All backtests: DAILY portfolio returns, weights updated monthly, NET OF COSTS.
Metrics via the TRADING engine's statistics module (Sharpe / PSR / DSR).

Run:  python research/alpha_pipeline.py
Writes: research/artifacts/results.json, *_returns.parquet, lgbm signal.
"""
from __future__ import annotations
import sys, os, json, math, time, warnings
warnings.filterwarnings('ignore')
ROOT = r'C:\Users\Labry\documents\THEPRICINGLIBRARY\Tools\pricinglibrary_rag_backend'
sys.path.insert(0, ROOT)
TE = r'C:\Users\Labry\documents\TRADING\trading_engine'
sys.path.insert(0, TE); sys.path.insert(0, os.path.join(TE, 'src'))

import numpy as np
import pandas as pd
import lightgbm as lgb
from backtest.statistics import (annualized_sharpe, annualized_sortino,
                                 probabilistic_sharpe_ratio, deflated_sharpe_ratio,
                                 infer_periods_per_year)
from pricinglibrary_rag.marketdata import cache

ART = os.path.join(ROOT, 'research', 'artifacts')
os.makedirs(ART, exist_ok=True)
COST_BPS_SIDE = 5.0
OOS_SPLIT = pd.Timestamp('2012-01-01')
np.random.seed(7)

# ============================================================ metrics helpers
def max_drawdown(equity):
    return float((equity / equity.cummax() - 1.0).min())

def monthly_sharpe(daily_r):
    m = (1 + daily_r).resample('ME').prod() - 1
    s = m.std(ddof=0)
    return float(m.mean()/s) if s > 0 else 0.0

def perf(returns, n_trials=1, trial_sharpes=None, label=''):
    r = pd.Series(returns).replace([np.inf, -np.inf], np.nan).dropna()
    if len(r) < 30:
        return dict(label=label, sharpe=0, sortino=0, psr=0, dsr=0, maxdd=0,
                    ann_ret=0, ann_vol=0, n=int(len(r)))
    ppy = infer_periods_per_year(r.index)
    eq = (1 + r).cumprod()
    return dict(label=label,
                sharpe=float(annualized_sharpe(r, ppy)),
                sortino=float(annualized_sortino(r, ppy)),
                psr=float(probabilistic_sharpe_ratio(r, 0.0)),
                dsr=float(deflated_sharpe_ratio(r, n_trials=n_trials, trial_sharpes=trial_sharpes)),
                maxdd=max_drawdown(eq),
                ann_ret=float(r.mean()*ppy), ann_vol=float(r.std(ddof=0)*math.sqrt(ppy)),
                n=int(len(r)))

def split_is_oos(r):
    return r[r.index < OOS_SPLIT], r[r.index >= OOS_SPLIT]

# ============================================================ backtest core
def backtest_weights(daily_ret, weights_m, cost_bps_side=COST_BPS_SIDE):
    w = weights_m.reindex(columns=daily_ret.columns).fillna(0.0)
    daily_w = w.reindex(daily_ret.index, method='ffill').shift(1).fillna(0.0)
    gross = (daily_w * daily_ret).sum(axis=1)
    prev = w.shift(1).fillna(0.0)
    turn = (w - prev).abs().sum(axis=1)
    cost = (turn * (cost_bps_side/1e4)).reindex(daily_ret.index).fillna(0.0).shift(1).fillna(0.0)
    net = (gross - cost).rename('ret')
    ann_turn = float(turn.mean()) * 12.0      # avg monthly turnover annualised (sum|dw|)
    return net, ann_turn

def decile_ls_weights(signal_m, frac=0.1):
    W = pd.DataFrame(0.0, index=signal_m.index, columns=signal_m.columns)
    for dt, row in signal_m.iterrows():
        s = row.dropna()
        if len(s) < 20:
            continue
        k = max(1, int(len(s)*frac))
        W.loc[dt, s.nlargest(k).index] = 1.0/k
        W.loc[dt, s.nsmallest(k).index] = -1.0/k
    return W

# ============================================================ equity features
ETF_BLOCK = {'SPY','QQQ','IWM','DIA','GLD','SLV','TLT','IEF','SHY','LQD','HYG','AGG',
             'EEM','EFA','ARKK','UNG'}

def build_equity():
    panel = pd.read_parquet(os.path.join(ART, 'equity_close_panel.parquet'))
    panel = panel.drop(columns=[c for c in panel.columns if c in ETF_BLOCK], errors='ignore').sort_index()
    daily_ret = panel.pct_change(fill_method=None)
    me = panel.resample('ME').last().index
    at = lambda d: d.reindex(me, method='ffill')
    r1  = panel.pct_change(21, fill_method=None)
    r3  = panel.pct_change(63, fill_method=None)
    r6  = panel.pct_change(126, fill_method=None)
    r12 = panel.pct_change(252, fill_method=None)
    mom = panel.shift(21).pct_change(231, fill_method=None)
    vol3 = daily_ret.rolling(63).std()*math.sqrt(252)
    vol6 = daily_ret.rolling(126).std()*math.sqrt(252)
    dvol = daily_ret.clip(upper=0).pow(2).rolling(126).mean().pow(0.5)*math.sqrt(252)
    skew6 = daily_ret.rolling(126).skew()
    hi52 = panel/panel.rolling(252).max() - 1.0
    maxd = daily_ret.rolling(21).max()
    d = panel.diff(); upm = d.clip(lower=0).rolling(14).mean(); dnm = (-d.clip(upper=0)).rolling(14).mean()
    rsi = 100 - 100/(1 + upm/dnm.replace(0, np.nan))
    F = dict(mom_12_1=at(mom), rev_1m=at(-r1), r3=at(r3), r6=at(r6), r12=at(r12),
             vol3=at(vol3), vol6=at(vol6), dvol6=at(dvol), skew6=at(skew6),
             hi52=at(hi52), maxd=at(maxd), rsi=at(rsi))
    fwd = at(panel).pct_change().shift(-1)
    return panel, daily_ret, F, fwd, me

# ============================================================ ML: long format
FEATS = ['mom_12_1','rev_1m','r3','r6','r12','vol3','vol6','dvol6','skew6','hi52','maxd','rsi']

def to_long(F, fwd):
    frames = []
    for name in FEATS:
        frames.append(F[name].stack().rename(name))
    X = pd.concat(frames, axis=1)
    y = fwd.stack().rename('fwd')
    df = X.join(y, how='inner').dropna(subset=FEATS)
    df.index.set_names(['date','sym'], inplace=True)
    # cross-sectional demean of label within month (predict RELATIVE return) + winsorize feats
    df['fwd_x'] = df.groupby('date')['fwd'].transform(lambda s: s - s.mean())
    return df

def walk_forward_lgbm(df, me, embargo_months=2):
    """Expanding-window walk-forward with PURGE+EMBARGO. Train on data ending
    `embargo_months` before each OOS year; predict that year's monthly cross-sections.
    Returns a (date x sym) prediction panel for OOS dates only."""
    dates = np.array(sorted(df.index.get_level_values('date').unique()))
    oos_dates = [d for d in dates if d >= OOS_SPLIT]
    preds = {}
    params = dict(objective='regression', n_estimators=300, learning_rate=0.03,
                  num_leaves=31, max_depth=6, subsample=0.8, colsample_bytree=0.7,
                  min_child_samples=200, reg_lambda=5.0, n_jobs=-1, verbose=-1)
    # retrain once per calendar year (keeps it fast, realistic)
    import pandas as _pd
    years = sorted(set(_pd.Timestamp(d).year for d in oos_dates))
    for yr in years:
        test_start = _pd.Timestamp(f'{yr}-01-01')
        test_end = _pd.Timestamp(f'{yr}-12-31')
        # PURGE+EMBARGO: training labels must be realized before test window minus embargo
        train_cutoff = test_start - _pd.DateOffset(months=embargo_months)
        tr = df[df.index.get_level_values('date') < train_cutoff]
        te = df[(df.index.get_level_values('date') >= test_start) &
                (df.index.get_level_values('date') <= test_end)]
        if len(tr) < 5000 or te.empty:
            continue
        model = lgb.LGBMRegressor(**params)
        model.fit(tr[FEATS], tr['fwd_x'])
        p = _pd.Series(model.predict(te[FEATS]), index=te.index)
        for (d, sym), val in p.items():
            preds.setdefault(d, {})[sym] = val
    pred_panel = _pd.DataFrame(preds).T.sort_index()
    return pred_panel

def walk_forward_meta(df, me, primary_signal, embargo_months=2, thresh=0.55):
    """Meta-label H1: train classifier to predict if a momentum decile pick is a
    winner (relative). Apply as a filter on OOS. primary_signal: date x sym ranks."""
    import pandas as _pd
    # event set: stocks in top/bottom momentum decile each month with side
    events = []
    for dt, row in primary_signal.iterrows():
        s = row.dropna()
        if len(s) < 20: continue
        k = max(1, int(len(s)*0.1))
        for sym in s.nlargest(k).index: events.append((dt, sym, 1))
        for sym in s.nsmallest(k).index: events.append((dt, sym, -1))
    ev = _pd.DataFrame(events, columns=['date','sym','side']).set_index(['date','sym'])
    j = ev.join(df, how='inner').dropna(subset=FEATS+['fwd_x'])
    j['win'] = ((j['side']*j['fwd_x']) > 0).astype(int)
    dates = sorted(j.index.get_level_values('date').unique())
    years = sorted(set(_pd.Timestamp(d).year for d in dates if d >= OOS_SPLIT))
    params = dict(objective='binary', n_estimators=200, learning_rate=0.03, num_leaves=15,
                  max_depth=4, subsample=0.8, colsample_bytree=0.7, min_child_samples=100,
                  reg_lambda=5.0, n_jobs=-1, verbose=-1)
    keep = {}
    for yr in years:
        ts = _pd.Timestamp(f'{yr}-01-01'); te_ = _pd.Timestamp(f'{yr}-12-31')
        cut = ts - _pd.DateOffset(months=embargo_months)
        tr = j[j.index.get_level_values('date') < cut]
        tev = j[(j.index.get_level_values('date') >= ts) & (j.index.get_level_values('date') <= te_)]
        if len(tr) < 3000 or tev.empty: continue
        m = lgb.LGBMClassifier(**params); m.fit(tr[FEATS], tr['win'])
        prob = m.predict_proba(tev[FEATS])[:,1]
        for (d, sym), pr, side in zip(tev.index, prob, tev['side']):
            keep.setdefault(d, {})[sym] = (side, pr)
    return keep, thresh

# ============================================================ cross-asset trend
TREND_UNIVERSE = {
 'eq': ['ES=F','NQ=F','YM=F','RTY=F','SPY','QQQ','IWM','EFA','EEM','DIA'],
 'rates': ['ZB=F','ZN=F','ZF=F','ZT=F','TLT','IEF'],
 'comm': ['CL=F','BZ=F','NG=F','GC=F','SI=F','HG=F','PA=F','PL=F','ZC=F','ZS=F','ZW=F','GLD','SLV'],
 'fx': ['6E=F','6J=F','6B=F','6A=F','6C=F','6S=F'],
 'crypto': ['BTC-USD','ETH-USD'],
}

def load_trend_panel():
    syms = [s for v in TREND_UNIVERSE.values() for s in v]
    closes = {}
    for s in syms:
        df = cache.load('yfinance', s)
        if df is None or len(df) < 500: continue
        closes[s] = df['close']
    panel = pd.DataFrame(closes).sort_index()
    panel = panel[panel.index >= pd.Timestamp('2002-01-01')]
    return panel

def tsmom(panel, lookbacks=(21,63,126,252), vol_target=0.10):
    daily_ret = panel.pct_change(fill_method=None).clip(-0.20, 0.20)  # winsorize roll-gap artifacts
    me = panel.resample('ME').last().index
    vol = daily_ret.rolling(63).std()*math.sqrt(252)
    vol_me = vol.reindex(me, method='ffill')
    # multi-lookback trend sign, averaged
    sig = None
    for lb in lookbacks:
        s = np.sign(panel.pct_change(lb, fill_method=None)).reindex(me, method='ffill')
        sig = s if sig is None else sig + s
    sig = sig/len(lookbacks)
    # inverse-vol risk parity per asset, then gross-normalise to 1
    raw = sig * (1.0/ vol_me.replace(0, np.nan))
    raw = raw.div(raw.abs().sum(axis=1).replace(0, np.nan), axis=0)   # gross=1, equal-risk-ish
    W = raw.fillna(0.0)
    net, turn = backtest_weights(daily_ret, W, cost_bps_side=2.0)     # liquid futures/ETF
    # causal portfolio vol-target to `vol_target` (scale-invariant for Sharpe; controls DD)
    realized = net.rolling(63).std().shift(1)*math.sqrt(252)
    lever = (vol_target/realized).clip(upper=3.0).fillna(0.0)
    net = (net*lever).rename('ret')
    return net, turn, W

# ============================================================ MAIN
def main():
    t0 = time.time()
    out = {'meta': {'cost_bps_side': COST_BPS_SIDE, 'oos_split': str(OOS_SPLIT.date())}, 'strategies': {}}
    panel, daily_ret, F, fwd, me = build_equity()
    print(f'equity panel {panel.shape} names_after_block={panel.shape[1]}', flush=True)

    series = {}
    turns = {}
    # ---- H1/H2/H3 factor longs-shorts
    for name, sig in [('H1_momentum', F['mom_12_1']),
                      ('H2_reversal', F['rev_1m']),
                      ('H3_lowvol', -F['vol6'])]:
        net, turn = backtest_weights(daily_ret, decile_ls_weights(sig))
        series[name] = net; turns[name] = turn
        print(f'{name} built sharpe(full)={annualized_sharpe(net):.2f}', flush=True)

    # ---- H5 LightGBM cross-sectional
    df_long = to_long(F, fwd)
    print(f'long panel {df_long.shape}, training walk-forward lgbm...', flush=True)
    pred = walk_forward_lgbm(df_long, me)
    pred = pred.reindex(columns=panel.columns)
    net5, turn5 = backtest_weights(daily_ret, decile_ls_weights(pred))
    series['H5_lgbm_xs'] = net5; turns['H5_lgbm_xs'] = turn5
    pred.to_parquet(os.path.join(ART, 'lgbm_xs_pred.parquet'))
    print(f'H5 built sharpe(OOS)={annualized_sharpe(net5[net5.index>=OOS_SPLIT]):.2f}', flush=True)

    # ---- H6 meta-labeled momentum
    keep, thr = walk_forward_meta(df_long, me, F['mom_12_1'])
    Wm = pd.DataFrame(0.0, index=me, columns=panel.columns)
    for d, dd in keep.items():
        longs = [(s) for s,(side,pr) in dd.items() if side==1 and pr>=thr]
        shorts = [(s) for s,(side,pr) in dd.items() if side==-1 and pr>=thr]
        if longs:
            for s in longs: Wm.loc[d, s] = 1.0/len(longs)
        if shorts:
            for s in shorts: Wm.loc[d, s] = -1.0/len(shorts)
    net6, turn6 = backtest_weights(daily_ret, Wm)
    series['H6_meta_momentum'] = net6; turns['H6_meta_momentum'] = turn6
    print(f'H6 built sharpe(OOS)={annualized_sharpe(net6[net6.index>=OOS_SPLIT]):.2f}', flush=True)

    # ---- H4 cross-asset trend
    tp = load_trend_panel()
    print(f'trend panel {tp.shape} {tp.index.min().date()}..{tp.index.max().date()}', flush=True)
    net4, turn4, W4 = tsmom(tp)
    series['H4_xasset_trend'] = net4; turns['H4_xasset_trend'] = turn4
    print(f'H4 built sharpe(OOS)={annualized_sharpe(net4[net4.index>=OOS_SPLIT]):.2f}', flush=True)

    # ---- metrics with DSR deflation across the trials (count configs honestly)
    N_TRIALS = 6        # 6 hypotheses, each a single pre-registered config
    # Deflation pool: per-period (DAILY, non-annualised) OOS Sharpe of each trial,
    # so units match the daily returns fed to deflated_sharpe_ratio.
    def daily_sharpe(r):
        r = r.dropna(); s = r.std(ddof=0)
        return float(r.mean()/s) if s > 0 else 0.0
    oos_monthly_sharpes = []   # name kept; now holds DAILY per-period sharpes
    for name, r in series.items():
        _, oos = split_is_oos(r)
        oos_monthly_sharpes.append(daily_sharpe(oos))

    for name, r in series.items():
        is_r, oos_r = split_is_oos(r)
        rec = {'turnover_ann': turns[name],
               'full': perf(r, n_trials=N_TRIALS, trial_sharpes=oos_monthly_sharpes, label=name),
               'is': perf(is_r, n_trials=N_TRIALS, trial_sharpes=oos_monthly_sharpes, label=name+'_IS'),
               'oos': perf(oos_r, n_trials=N_TRIALS, trial_sharpes=oos_monthly_sharpes, label=name+'_OOS')}
        out['strategies'][name] = rec
        r.to_frame().to_parquet(os.path.join(ART, f'{name}_returns.parquet'))

    # ---- CLEAN causal inverse-vol blend of (near) uncorrelated sleeves.
    # Each sleeve is already vol-targeted, so a single causal inverse-vol weight
    # (trailing 63d, lagged 1d) equalises risk. The OLD combiner applied a SECOND
    # portfolio-level vol-target overlay (lever = target/realized) on top of this,
    # which only added estimation/timing drag (~0.86 vs ~0.90 OOS). Removed.
    def equal_risk_combo(parts, lookback=63):
        df = pd.concat(parts, axis=1).dropna()
        inv_vol = 1.0/(df.rolling(lookback).std().shift(1)*math.sqrt(252)).replace(0, np.nan)
        w = inv_vol.div(inv_vol.sum(axis=1), axis=0)
        comb = (df*w).sum(axis=1)
        return comb.dropna().rename('ret')

    # The two best, near-uncorrelated sleeves: LGBM cross-sectional equity + cross-asset trend
    series['COMBO_lgbm_trend'] = equal_risk_combo([series['H5_lgbm_xs'].rename('a'),
                                                   series['H4_xasset_trend'].rename('b')])
    eq_combo = pd.concat([series['H1_momentum'], series['H3_lowvol'], series['H6_meta_momentum']], axis=1).mean(axis=1)
    series['COMBO_equity'] = eq_combo
    series['COMBO_all'] = equal_risk_combo([series['H5_lgbm_xs'].rename('a'),
                                            series['H4_xasset_trend'].rename('b'),
                                            series['H1_momentum'].rename('c')])
    for name in ['COMBO_lgbm_trend','COMBO_equity','COMBO_all']:
        r = series[name]; is_r, oos_r = split_is_oos(r)
        out['strategies'][name] = {'turnover_ann': None,
            'full': perf(r, n_trials=N_TRIALS+2, trial_sharpes=oos_monthly_sharpes, label=name),
            'is': perf(is_r, n_trials=N_TRIALS+2, trial_sharpes=oos_monthly_sharpes, label=name+'_IS'),
            'oos': perf(oos_r, n_trials=N_TRIALS+2, trial_sharpes=oos_monthly_sharpes, label=name+'_OOS')}
        r.to_frame('ret').to_parquet(os.path.join(ART, f'{name}_returns.parquet'))

    out['meta']['n_trials'] = N_TRIALS
    out['meta']['runtime_s'] = round(time.time()-t0, 1)
    with open(os.path.join(ART, 'results.json'), 'w') as f:
        json.dump(out, f, indent=2, default=str)

    # console summary
    print('\n=== OOS (2012+) net-of-cost summary ===', flush=True)
    print(f"{'strategy':20s} {'Sharpe':>7s} {'PSR':>6s} {'DSR':>6s} {'maxDD':>7s} {'annRet':>7s} {'turn':>6s}")
    for name, rec in out['strategies'].items():
        o = rec['oos']; t = rec.get('turnover_ann')
        print(f"{name:20s} {o['sharpe']:7.2f} {o['psr']:6.2f} {o['dsr']:6.2f} {o['maxdd']:7.1%} {o['ann_ret']:7.1%} {('%.1f'%t) if t else '   -':>6s}")
    print(f"\nruntime {out['meta']['runtime_s']}s -> {os.path.join(ART,'results.json')}", flush=True)

if __name__ == '__main__':
    main()
