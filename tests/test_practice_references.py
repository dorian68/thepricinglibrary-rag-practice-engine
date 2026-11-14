"""Standalone execution plus independent numerical controls for 14 references."""
import ast
from copy import deepcopy
import csv
import io
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys

import numpy as np
import pytest

from pricinglibrary_rag.practice_references import (
    CATALOG,export_reference,get_reference,list_reference_ids,run_reference,write_reference_catalog,
)


IDS=list_reference_ids()
BRIEFS=json.loads((CATALOG.parent/'practice_exercises.json').read_text(encoding='utf-8'))['exercises']


def assert_same(actual,expected):
    if isinstance(expected,dict):
        assert actual.keys()==expected.keys()
        for key in expected:assert_same(actual[key],expected[key])
    elif isinstance(expected,list):
        assert len(actual)==len(expected)
        for a,b in zip(actual,expected):assert_same(a,b)
    elif type(expected) is float:assert actual==pytest.approx(expected,rel=1e-12,abs=1e-10)
    else:assert actual==expected


@pytest.mark.parametrize('identifier',IDS)
@pytest.mark.parametrize('format',['python','ipynb'])
def test_all_fourteen_scripts_and_notebooks_execute_without_tpl(tmp_path,identifier,format):
    exported=export_reference(identifier,format)
    if format=='ipynb':
        notebook=json.loads(exported)
        assert notebook['nbformat']==4 and notebook['cells'][0]['cell_type']=='markdown'
        code='\n'.join(''.join(cell['source']) for cell in notebook['cells'] if cell['cell_type']=='code')
    else:code=exported
    assert 'pricinglibrary_rag' not in code and 'scipy' not in code
    assert 'pass\n' not in code and 'TODO' not in code
    path=tmp_path/'exercise.py';path.write_text(code,encoding='utf-8')
    env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONIOENCODING']='utf-8'
    process=subprocess.run([sys.executable,'-I',str(path)],cwd=tmp_path,env=env,text=True,encoding='utf-8',capture_output=True,timeout=20)
    assert process.returncode==0,process.stderr
    actual=json.loads(process.stdout);expected=run_reference(identifier)
    assert_same(actual,expected)
    assert expected['checks'] and all(expected['checks'].values())
    reference=get_reference(identifier)
    assert_same(json.loads(reference['output']),actual)


def test_all_immutable_ids_and_catalog_are_complete_and_reproducible(tmp_path):
    assert len(IDS)==14 and set(IDS)=={brief['id'] for brief in BRIEFS}
    generated=write_reference_catalog(tmp_path/'catalog.json')
    artifact=json.loads(CATALOG.read_text(encoding='utf-8'));fresh=json.loads(generated.read_text(encoding='utf-8'))
    assert_same(artifact,fresh)
    for reference in fresh['references']:
        assert reference['ticket'] and reference['conventions'] and reference['limitations']
        assert reference['dependencies']==(['numpy'] if reference['id'] in {'mc-asian','smile-fit'} else [])
        assert reference['solution']==export_reference(reference['id'])


def test_reference_rejects_unknown_ids_formats_and_mutation():
    for name in ['../secret','__import__("os")','smile-fit; raise RuntimeError()',None]:
        with pytest.raises(ValueError):run_reference(name)
        with pytest.raises(ValueError):export_reference(name)
    with pytest.raises(ValueError):export_reference('bs-eur-call','html')
    result=run_reference('bs-eur-call');result['ticket']['spot']=999
    assert run_reference('bs-eur-call')['ticket']['spot']==100


def test_original_csv_and_smile_quotes_are_preserved_without_executing_starter():
    mapping={x['id']:x for x in BRIEFS}
    def assigned(code,name):
        tree=ast.parse(code)
        node=next(node for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets))
        return ast.literal_eval(node.value)
    original=assigned(mapping['realized-vol-estimators']['starterCode'],'CSV')
    rows=[{k:v if k=='date' else float(v) for k,v in row.items()} for row in csv.DictReader(io.StringIO(original))]
    assert run_reference('realized-vol-estimators')['ticket']['rows']==rows
    assert run_reference('smile-fit')['ticket']['quotes']==assigned(mapping['smile-fit']['starterCode'],'quotes')
    original_paths=assigned(mapping['autocall']['starterCode'],'paths')
    extended=run_reference('autocall')['ticket']['paths']
    assert all(extended[key][:len(value)]==value and len(extended[key])==8 for key,value in original_paths.items())


def test_five_estimators_match_separate_canonical_engine_and_original_numbers():
    from pricinglibrary_rag.realized_volatility import analyze_realized_volatility
    record=run_reference('realized-vol-estimators');result=record['result']
    oracle=analyze_realized_volatility(record['ticket']['rows'],{'annualization':252,'window':5,'calendarMode':'weekday_sessions','priceBasis':'unadjusted_ohlc'})
    expected={'closeToClose':.1573591361,'parkinson':.1715027235,'garmanKlass':.1839255738,'rogersSatchell':.1805823305,'yangZhang':.1775005135}
    for name,value in expected.items():
        assert result['annualized_volatility_decimal'][name]==pytest.approx(value,abs=6e-11)
        assert result['annualized_volatility_decimal'][name]==pytest.approx(oracle['estimators'][name]['annualizedVolatility'],abs=1e-14)
        assert result['annualized_volatility_365'][name]/result['annualized_volatility_decimal'][name]==pytest.approx(math.sqrt(365/252))


def test_black_scholes_prices_and_newton_convergence_match_independent_bisection():
    n=statistics.NormalDist().cdf
    def call(vol):
        d1=(.02+.5*vol*vol)*.5/(vol*math.sqrt(.5));d2=d1-vol*math.sqrt(.5)
        return 100*n(d1)-100*math.exp(-.02*.5)*n(d2)
    vanilla=run_reference('bs-eur-call')['result']
    assert vanilla['call']==pytest.approx(call(.2),abs=1e-12)
    assert vanilla['put']==pytest.approx(call(.2)-100+100*math.exp(-.01),abs=1e-12)
    low,high=.001,2
    for _ in range(70):
        mid=(low+high)/2
        if call(mid)>8:high=mid
        else:low=mid
    newton=run_reference('iv-newton')['result']
    assert newton['volatility']==pytest.approx((low+high)/2,abs=1e-12)
    assert abs(newton['price_error'])<=1e-10 and newton['converged']
    assert newton['price_evaluations']==len(newton['trace'])==4
    assert newton['newton_updates']==3 and newton['fallback_steps']==0


def test_asian_price_and_mcse_reconstruct_from_independent_path_loop():
    ref=run_reference('mc-asian');t=ref['ticket'];result=ref['result']
    shocks=np.random.default_rng(7).standard_normal((100000,12));spot=np.full(100000,100.0);running=np.zeros(100000)
    for month in range(12):
        spot*=np.exp((.02-.5*.2**2)/12+.2/math.sqrt(12)*shocks[:,month]);running+=spot
    sample=np.maximum(running/12-100,0)*math.exp(-.02)
    independent_mean=float(np.sum(sample,dtype=np.float64)/100000)
    independent_se=math.sqrt(float(np.sum((sample-independent_mean)**2))/(99999*100000))
    assert result['price']==pytest.approx(independent_mean,abs=1e-12)
    assert result['standard_error']==pytest.approx(independent_se,abs=1e-14)
    assert result['confidence_interval_95']==pytest.approx([independent_mean-1.96*independent_se,independent_mean+1.96*independent_se])
    assert result['price']==pytest.approx(5.356683200676238,abs=1e-10)
    assert run_reference('mc-asian')==ref
    # Exact geometric-average call is an independent lower bound by AM >= GM.
    dates=np.arange(1,13)/12;variance=.2**2*sum(min(a,b) for a in dates for b in dates)/144
    mu=math.log(100)+(.02-.5*.2**2)*float(dates.mean());sd=math.sqrt(variance)
    d2=(mu-math.log(100))/sd;d1=d2+sd;n=statistics.NormalDist().cdf
    geometric=math.exp(-.02)*(math.exp(mu+.5*variance)*n(d1)-100*n(d2))
    assert result['price']>geometric-4*result['standard_error']


def test_curve_discount_factors_match_linear_system_and_reprice_every_swap():
    result=run_reference('curve-boot')['result'];rates=[.03,.032,.0335]
    matrix=np.zeros((3,3))
    for i,rate in enumerate(rates):
        matrix[i,:i+1]=rate;matrix[i,i]+=1
    expected=np.linalg.solve(matrix,np.ones(3))
    dfs=[node['discount_factor'] for node in result['nodes']]
    assert dfs==pytest.approx(expected,abs=1e-15)
    for i,node in enumerate(result['nodes']):
        assert node['par_rate']*sum(dfs[:i+1])+dfs[i]==pytest.approx(1,abs=1e-15)
        assert abs(node['unit_notional_swap_pv'])<1e-12


def test_quadratic_smile_is_least_squares_but_no_price_cleaning_or_arbitrage_claim():
    record=run_reference('smile-fit');points=record['result']['points'];coef=record['result']['coefficients']
    x=np.log([point['moneyness'] for point in points]);residual=np.array([point['iv_residual'] for point in points])
    for basis in [np.ones(5),x,x*x]:assert float(basis@residual)==pytest.approx(0,abs=1e-15)
    assert coef['b']<0 and coef['c']>0
    assert not record['result']['no_arbitrage_proven'] and not record['result']['price_bounds_checked']
    assert not record['result']['implied_volatility_inversion_performed']


def test_delta_hedge_signed_trades_and_cds_buyer_cashflow_are_correct():
    hedge=run_reference('delta-hedge')['result']
    assert hedge['initial_hedge_shares']==-54000 and hedge['new_target_hedge_shares']==-61000
    assert hedge['rebalance_trade_shares']==-7000
    assert 1000*100*.61+hedge['initial_hedge_shares']+hedge['rebalance_trade_shares']==0
    cds=run_reference('cds-cs01')['result']
    assert cds['annual_premium_cashflow']==-600000 and cds['cs01_per_bp_widening']==21000
    assert cds['spread_shock_pnl']==525000 and cds['position']=='protection BUYER'
    assert 'profit' not in cds


def test_autocall_cashflows_quarterly_nonmemory_and_two_year_path_completion():
    ref=run_reference('autocall');result=ref['result'];paths={row['name']:row for row in result['scenarios']}
    assert result['coupon_per_quarter']==2 and result['coupon_memory'] is False and result['maturity_years']==2
    assert paths['up']['total_undiscounted_cashflows']==102 and paths['up']['observed_quarters']==1
    assert paths['flat']['total_undiscounted_cashflows']==106 and paths['flat']['observed_quarters']==3
    down=paths['down'];assert down['observed_quarters']==8 and not down['autocalled']
    assert down['coupon_total']==4 and down['principal_redemption']==pytest.approx(55)
    assert down['cashflows'][1]['coupon']==0 and down['cashflows'][4]['coupon']==2
    assert down['total_undiscounted_cashflows']==pytest.approx(59)
    assert 'pv' not in result and 'price' not in result
    assert ref['assumptions'] and 'prefixes' in ' '.join(ref['assumptions'])


def test_other_local_approximations_have_correct_units_and_signs():
    greek=run_reference('options-book-greeks')['result']
    assert [greek[key] for key in ['delta_pnl','gamma_pnl','vega_pnl','theta_pnl','total_pnl']]==[-500000,-160000,360000,-15000,-315000]
    swap=run_reference('swap-dv01')['result']
    assert swap['pv_approximation']==pytest.approx(-910000) and swap['signed_dv01_per_bp_up']==45500 and swap['shock_pnl']==455000
    barrier=run_reference('barrier-knock-in')['result']
    assert barrier['barrier_type']=='down-and-out call' and barrier['scenarios'][2]['payoff_usd']==pytest.approx(1e6)
    assert barrier['rebound_to_1_20_after_prior_touch_payoff_usd']==0
    var=run_reference('parametric-var')['result']
    assert var['var_95_one_day']==658000 and var['limit_breached'] and var['stress_pnl']==-1e6
    bond=run_reference('bond-duration')['result']
    assert bond['dv01_magnitude_per_bp']==17000 and bond['shock_pnl']==-425000
