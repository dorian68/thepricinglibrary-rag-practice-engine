"""Independent verification of headline numbers (no engine helpers)."""
import sys, os, math, json
import numpy as np, pandas as pd
from scipy.stats import norm
ART = r'C:\Users\Labry\documents\THEPRICINGLIBRARY\Tools\pricinglibrary_rag_backend\research\artifacts'
OOS = pd.Timestamp('2012-01-01')

def load(name):
    df = pd.read_parquet(os.path.join(ART, f'{name}_returns.parquet'))
    return df.iloc[:,0]

def manual_sharpe(r, ppy=252):
    r = r.dropna(); return r.mean()/r.std(ddof=0)*math.sqrt(ppy)

def manual_psr(r, bench=0.0):
    r = r.dropna(); n=len(r); sr=r.mean()/r.std(ddof=0)
    sk=r.skew(); ku=r.kurt()+3
    denom=math.sqrt(max(1e-12,1-sk*sr+(ku-1)/4*sr*sr))
    return norm.cdf((sr-bench)*math.sqrt(n-1)/denom)

names=['H1_momentum','H2_reversal','H3_lowvol','H5_lgbm_xs','H6_meta_momentum',
       'H4_xasset_trend','COMBO_lgbm_trend','COMBO_all']
S={n:load(n) for n in names}
print('=== independent recompute (OOS 2012+) ===')
for n in names:
    o=S[n][S[n].index>=OOS]
    print(f'{n:18s} ann_sharpe={manual_sharpe(o):6.2f}  PSR={manual_psr(o):.3f}  n={len(o)}')

print('\n=== OOS correlation (key sleeves) ===')
key=['H5_lgbm_xs','H4_xasset_trend','H1_momentum']
M=pd.concat({k:S[k][S[k].index>=OOS] for k in key},axis=1).dropna()
print(M.corr().round(2).to_string())

print('\n=== winner IS vs OOS (H5_lgbm_xs) ===')
r=S['H5_lgbm_xs']
print('IS  sharpe', round(manual_sharpe(r[r.index<OOS]),2))
print('OOS sharpe', round(manual_sharpe(r[r.index>=OOS]),2))
print('COMBO_lgbm_trend IS', round(manual_sharpe(S['COMBO_lgbm_trend'][S['COMBO_lgbm_trend'].index<OOS]),2),
      'OOS', round(manual_sharpe(S['COMBO_lgbm_trend'][S['COMBO_lgbm_trend'].index>=OOS]),2))
