"""Executable, authored references for the fourteen existing practice briefs.

Only fixed, allowlisted implementations and fixed tickets are run here. This is
not a Python sandbox and never accepts or executes learner-supplied code. Exports
contain the same functions and inputs, with no dependency on the TPL package.
"""
from __future__ import annotations

from copy import deepcopy
import inspect
import json
import math
from pathlib import Path
import statistics

SCHEMA = 'tpl.practice-reference.v1'
CATALOG = Path(__file__).parent / 'learning_assets' / 'practice_references.json'


def _number(value, label, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{label} must be a finite number in [{low}, {high}].')
    return float(value)


def _cdf(x):
    return .5 * (1 + math.erf(x / math.sqrt(2)))


def _bsm(spot, strike, rate, vol, maturity, dividend=0):
    s=_number(spot,'spot',1e-9,1e9);k=_number(strike,'strike',1e-9,1e9)
    t=_number(maturity,'maturity',1e-9,30);v=_number(vol,'volatility',1e-9,5)
    r=_number(rate,'rate',-1,1);q=_number(dividend,'dividend',-1,1)
    d1=(math.log(s/k)+(r-q+v*v/2)*t)/(v*math.sqrt(t));d2=d1-v*math.sqrt(t)
    call=s*math.exp(-q*t)*_cdf(d1)-k*math.exp(-r*t)*_cdf(d2)
    put=k*math.exp(-r*t)*_cdf(-d2)-s*math.exp(-q*t)*_cdf(-d1)
    phi=math.exp(-d1*d1/2)/math.sqrt(2*math.pi)
    return {'call':call,'put':put,'d1':d1,'d2':d2,
            'delta':math.exp(-q*t)*_cdf(d1),'vega_per_unit_vol':s*math.exp(-q*t)*phi*math.sqrt(t)}


def _newton_iv(target, spot, strike, rate, maturity, guess=.2, tolerance=1e-10, max_iterations=20):
    target=_number(target,'market price',0,1e9)
    lower=max(0,spot-strike*math.exp(-rate*maturity));upper=spot
    if not lower < target < upper:raise ValueError('Target is outside the strict European call price bounds.')
    lo,hi=1e-8,5.0;sigma=_number(guess,'initial guess',lo,hi);trace=[];fallbacks=0
    for index in range(max_iterations):
        value=_bsm(spot,strike,rate,sigma,maturity);error=value['call']-target
        trace.append({'evaluation':index+1,'sigma':sigma,'call_price':value['call'],'price_error':error,
                      'vega_per_unit_vol':value['vega_per_unit_vol']})
        if abs(error)<=tolerance:
            return {'volatility':sigma,'converged':True,'price_evaluations':len(trace),'newton_updates':len(trace)-1,
                    'price_error':error,'repriced_call':value['call'],'fallback_steps':fallbacks,'trace':trace}
        if error>0:hi=sigma
        else:lo=sigma
        candidate=sigma-error/value['vega_per_unit_vol'] if value['vega_per_unit_vol']>1e-12 else float('nan')
        if not math.isfinite(candidate) or not lo<candidate<hi:
            candidate=(lo+hi)/2;fallbacks+=1
        sigma=candidate
    raise ValueError('Implied volatility did not converge within the bounded iteration budget.')


def _solve_realized(t):
    rows=t['rows'];sessions=list(zip(rows,rows[1:]));n=len(sessions)
    close=[math.log(row['close']/previous['close']) for previous,row in sessions]
    overnight=[math.log(row['open']/previous['close']) for previous,row in sessions]
    oc=[math.log(row['close']/row['open']) for _,row in sessions]
    hl=[math.log(row['high']/row['low']) for _,row in sessions]
    rs=statistics.mean(math.log(row['high']/row['open'])*math.log(row['high']/row['close'])+
                       math.log(row['low']/row['open'])*math.log(row['low']/row['close']) for _,row in sessions)
    weight=.34/(1.34+(n+1)/(n-1))
    variances={'closeToClose':statistics.variance(close),'parkinson':statistics.mean(h*h for h in hl)/(4*math.log(2)),
               'garmanKlass':statistics.mean(.5*h*h-(2*math.log(2)-1)*c*c for h,c in zip(hl,oc)),
               'rogersSatchell':rs,'yangZhang':statistics.variance(overnight)+weight*statistics.variance(oc)+(1-weight)*rs}
    annualized={name:math.sqrt(t['annualization']*value) for name,value in variances.items()}
    annualized365={name:math.sqrt(365*value) for name,value in variances.items()}
    valid=all(row['high']>=max(row['open'],row['close']) and row['low']<=min(row['open'],row['close']) and row['low']>0 for row in rows)
    return {'row_count':len(rows),'common_sessions':n,'annualization':t['annualization'],'yang_zhang_weight':weight,
            'daily_variance':variances,'annualized_volatility_decimal':annualized,'annualized_volatility_365':annualized365,
            'annualization_ratio_365_over_252':math.sqrt(365/t['annualization']),
            'checks':{'valid_ohlc':valid,'common_sessions_11':n==11,'daily_variances_nonnegative':all(v>=0 for v in variances.values()),
                      'annualization_changes_only_scale':all(math.isclose(annualized365[k]/annualized[k],math.sqrt(365/t['annualization']),rel_tol=1e-12) for k in variances)}}


def _solve_bs(t):
    v=_bsm(t['spot'],t['strike'],t['rate'],t['volatility'],t['maturity_years'],t['dividend_yield'])
    lhs=v['call']-v['put'];rhs=t['spot']*math.exp(-t['dividend_yield']*t['maturity_years'])-t['strike']*math.exp(-t['rate']*t['maturity_years'])
    return {**v,'vega_per_vol_point':v['vega_per_unit_vol']*.01,'parity_lhs':lhs,'parity_rhs':rhs,'parity_gap':lhs-rhs,
            'price_unit':'currency per underlying unit','checks':{'parity_holds':abs(lhs-rhs)<1e-10,'positive_vega':v['vega_per_unit_vol']>0,'call_delta_above_half':v['delta']>.5}}


def _solve_greeks(t):
    delta=t['delta_per_pct_point']*t['spot_move_pct_points']
    gamma=.5*t['gamma_per_pct_point_squared']*t['spot_move_pct_points']**2
    vega=t['vega_per_vol_point']*t['vol_move_points'];theta=t['theta_per_day']*t['elapsed_days']
    parts={'delta':delta,'gamma':gamma,'vega':vega,'theta':theta}
    return {'currency':t['currency'],'delta_pnl':delta,'gamma_pnl':gamma,'vega_pnl':vega,'theta_pnl':theta,
            'total_pnl':delta+gamma+vega+theta,'largest_absolute_component':max(parts,key=lambda key:abs(parts[key])),
            'checks':{'short_gamma_loses_on_move':gamma<0,'long_vega_gains_on_vol_rise':vega>0,
                      'total_reconciles':math.isclose(delta+gamma+vega+theta,-315000)}}


def _solve_swap(t):
    pv=(t['par_rate']-t['fixed_coupon'])*t['annuity']*t['notional']
    dv01=t['notional']*t['annuity']*.0001;pnl=dv01*t['shock_bp']
    return {'currency':'EUR','position':'payer fixed / receiver floating','pv_approximation':pv,
            'signed_dv01_per_bp_up':dv01,'shock_pnl':pnl,'shocked_pv_approximation':pv+pnl,
            'hedge_direction':'Receive fixed / pay floating to offset the payer rate sensitivity.',
            'checks':{'payer_gains_on_rates_up':pnl>0,'above_market_fixed_coupon_has_negative_pv':pv<0}}


def _barrier_cashflow(spot,strike,barrier,notional,previously_touched=False):
    knocked_out=previously_touched or spot<=barrier
    return knocked_out,0.0 if knocked_out else max(spot-strike,0)*notional


def _solve_barrier(t):
    records=[]
    for spot in t['terminal_spots']:
        knocked_out,payoff=_barrier_cashflow(spot,t['strike'],t['barrier'],t['notional_eur'])
        records.append({'terminal_spot':spot,'earlier_touch_assumed':False,'knocked_out':knocked_out,'payoff_usd':payoff})
    _,rebound_after_prior_touch=_barrier_cashflow(t['terminal_spots'][-1],t['strike'],t['barrier'],t['notional_eur'],previously_touched=True)
    return {'barrier_type':'down-and-out call','notional_currency':'EUR','payoff_currency':'USD','scenarios':records,
            'rebound_to_1_20_after_prior_touch_payoff_usd':rebound_after_prior_touch,
            'checks':{'touch_at_barrier_knocks_out':records[1]['knocked_out'],'positive_no_touch_payoff':records[2]['payoff_usd']>0,
                      'prior_touch_overrides_terminal_recovery':rebound_after_prior_touch==0}}


def _solve_smile(t):
    import numpy as np
    quotes=t['quotes']
    retained=[row for row in quotes if math.isfinite(row['moneyness']) and row['moneyness']>0 and math.isfinite(row['iv']) and 0<row['iv']<=5]
    x=np.log(np.array([row['moneyness'] for row in retained]));y=np.array([row['iv'] for row in retained])
    design=np.column_stack((np.ones(len(x)),x,x*x));coef,_,rank,_=np.linalg.lstsq(design,y,rcond=None)
    fitted=design@coef;residual=y-fitted
    return {'fit_family':'quadratic IV in log(K/S), not SVI','quote_count':len(quotes),'retained_quote_count':len(retained),
            'tenor_years':t['tenor_days']/365,'coefficients':{'a':float(coef[0]),'b':float(coef[1]),'c':float(coef[2])},
            'rms_iv_residual':float(np.sqrt(np.mean(residual**2))),
            'points':[{'moneyness':row['moneyness'],'observed_iv':row['iv'],'fitted_iv':float(fit),'iv_residual':float(err)} for row,fit,err in zip(retained,fitted,residual)],
            'price_bounds_checked':False,'implied_volatility_inversion_performed':False,'stale_or_crossed_quotes_assessed':False,
            'no_arbitrage_proven':False,
            'checks':{'all_five_numeric_iv_quotes_retained':len(retained)==5,'full_rank':int(rank)==3,
                      'negative_atm_log_moneyness_slope':float(coef[1])<0,'downside_iv_exceeds_atm':retained[0]['iv']>retained[2]['iv']}}


def _solve_asian(t):
    import numpy as np
    paths=t['paths'];steps=t['steps']
    if type(paths) is not int or not 2<=paths<=100000 or type(steps) is not int or not 1<=steps<=12:
        raise ValueError('Reference budget: 2..100000 independent paths, 1..12 observations.')
    s=_number(t['spot'],'spot',1e-8,1e6);k=_number(t['strike'],'strike',1e-8,1e6)
    r=_number(t['rate'],'rate',-.2,.5);vol=_number(t['volatility'],'volatility',0,2);maturity=_number(t['maturity_years'],'maturity',1e-8,10)
    dt=maturity/steps;rng=np.random.default_rng(t['seed'])
    # Row-major: each row is one independent path, columns are monthly shocks.
    z=rng.standard_normal((paths,steps))
    spots=s*np.exp(np.cumsum((r-.5*vol*vol)*dt+vol*math.sqrt(dt)*z,axis=1))
    averages=spots.mean(axis=1);discounted=math.exp(-r*maturity)*np.maximum(averages-k,0)
    price=float(discounted.mean());sample_std=float(discounted.std(ddof=1));se=sample_std/math.sqrt(paths)
    return {'price':price,'price_unit':'currency per underlying unit','standard_error':se,
            'sample_std_discounted_payoff':sample_std,'confidence_interval_95':[price-1.96*se,price+1.96*se],
            'paths':paths,'independent_samples':paths,'seed':t['seed'],'measure':'risk-neutral Q',
            'observation_times_years':[(i+1)*dt for i in range(steps)],'sampling_unit':'one independent simulated path',
            'checks':{'t0_excluded_from_average':True,'twelve_monthly_observations':steps==12,
                      'standard_error_positive':se>0,'ci_contains_sample_mean':price-1.96*se<=price<=price+1.96*se}}


def _solve_curve(t):
    dfs={};records=[]
    for years,rate in t['swap_rates']:
        prior=sum(dfs.values());df=(1-rate*prior)/(1+rate);dfs[years]=df
        annuity=sum(dfs.values());repriced=(1-df)/annuity
        records.append({'tenor_years':years,'par_rate':rate,'discount_factor':df,
                        'zero_rate_continuous':-math.log(df)/years,'repriced_par_rate':repriced,
                        'unit_notional_swap_pv':rate*annuity+df-1})
    discounts=list(dfs.values())
    return {'nodes':records,'payment_interval_years':1,
            'checks':{'all_discount_factors_positive':all(v>0 for v in discounts),
                      'discount_factors_decrease':all(a>b for a,b in zip([1]+discounts,discounts)),
                      'all_instruments_reprice':all(abs(p['unit_notional_swap_pv'])<1e-12 for p in records)}}


def _solve_delta(t):
    option0=t['contracts']*t['multiplier']*t['delta_initial'];option1=t['contracts']*t['multiplier']*t['delta_next']
    hedge0=-option0;hedge1=-option1;trade=hedge1-hedge0
    return {'option_delta_initial_shares':option0,'option_delta_next_shares':option1,'initial_hedge_shares':hedge0,
            'new_target_hedge_shares':hedge1,'rebalance_trade_shares':trade,'trade_sign_convention':'positive=buy; negative=sell',
            'checks':{'initial_delta_neutral':abs(option0+hedge0)<1e-10,'rebalanced_delta_neutral':abs(option1+hedge0+trade)<1e-10,
                      'sell_additional_shares_when_long_call_delta_rises':trade<0}}


def _solve_iv(t):
    solved=_newton_iv(t['market_call_price'],t['spot'],t['strike'],t['rate'],t['maturity_years'],t['initial_guess'],t['tolerance'],t['max_iterations'])
    return {**solved,'volatility_percent':100*solved['volatility'],'vega_unit':'price per volatility 1.0, not per vol percentage point',
            'method':'Newton-Raphson with finite positive bracket and bisection safeguard',
            'checks':{'converged':solved['converged'],'target_price_reproduced':abs(solved['price_error'])<=t['tolerance'],
                      'within_iteration_budget':solved['price_evaluations']<=t['max_iterations']}}


def _solve_autocall(t):
    quarterly_coupon=t['annual_coupon_rate']/t['observations_per_year']*t['principal']
    paths=[]
    for name,levels in t['paths'].items():
        if len(levels)!=t['quarters']:raise ValueError('Every authored path must supply all eight quarterly observations.')
        rows=[];coupons=0.0;principal_cash=0.0;called=False
        for index,level in enumerate(levels):
            quarter=index+1;coupon=quarterly_coupon if level>=t['coupon_barrier'] else 0.0
            autocall=level>=t['autocall_level'];matured=quarter==t['quarters']
            redemption=t['principal'] if autocall or (matured and level>=t['protection_barrier']) else t['principal']*level if matured else 0.0
            rows.append({'quarter':quarter,'time_years':quarter/t['observations_per_year'],'level':level,
                         'coupon_eligible':level>=t['coupon_barrier'],'coupon':coupon,'autocalled':autocall,
                         'redemption':redemption,'cashflow':coupon+redemption})
            coupons+=coupon;principal_cash+=redemption
            if autocall:called=True;break
        paths.append({'name':name,'observed_quarters':len(rows),'autocalled':called,'coupon_total':coupons,
                      'principal_redemption':principal_cash,'total_undiscounted_cashflows':coupons+principal_cash,'cashflows':rows})
    return {'principal':t['principal'],'cashflow_unit':'per 100 initial principal; undiscounted','coupon_per_quarter':quarterly_coupon,
            'coupon_memory':False,'maturity_years':t['quarters']/t['observations_per_year'],'scenarios':paths,
            'checks':{'eight_supplied_observations_each':all(len(levels)==8 for levels in t['paths'].values()),
                      'two_percent_coupon_per_quarter':math.isclose(quarterly_coupon,2),'up_redeems_first_quarter':paths[0]['observed_quarters']==1,
                      'downside_loss_when_final_below_protection':paths[2]['principal_redemption']<t['principal']}}


def _solve_cds(t):
    carry=-t['notional']*t['spread'];cs01=t['notional']*t['risky_annuity']*.0001;pnl=cs01*t['shock_bp']
    return {'currency':t['currency'],'position':'protection BUYER','annual_premium_cashflow':carry,
            'cs01_per_bp_widening':cs01,'spread_shock_pnl':pnl,'premium_and_pnl_are_different_horizons':True,
            'checks':{'buyer_pays_premium':carry<0,'buyer_gains_when_spreads_widen':pnl>0,'cs01_positive_for_buyer':cs01>0}}


def _solve_var(t):
    value=t['portfolio_value']*t['daily_volatility']*t['normal_quantile'];stress=t['portfolio_value']*t['stress_return']
    return {'currency':t['currency'],'var_95_one_day':value,'limit':t['limit'],'limit_usage':value/t['limit'],
            'limit_breached':value>t['limit'],'stress_pnl':stress,'used_rounded_normal_quantile':t['normal_quantile'],
            'checks':{'hypothetical_limit_breached':value>t['limit'],'stress_exceeds_var':-stress>value,'var_is_positive_loss_amount':value>0}}


def _solve_bond(t):
    dv01=t['market_value']*t['modified_duration']*.0001;pnl=-dv01*t['yield_shock_bp']
    return {'currency':'EUR','position':'long bond','dv01_magnitude_per_bp':dv01,'signed_pnl_per_bp_up':-dv01,
            'shock_pnl':pnl,'checks':{'long_bond_loses_on_yield_rise':pnl<0,'dv01_magnitude_positive':dv01>0}}


OHLC = [
    ['2024-01-02',100,101.4,99.35,100.9],['2024-01-03',101.05,102.1,100.2,101.55],
    ['2024-01-04',101.4,102,99.8,100.15],['2024-01-05',100.25,101.65,99.9,101.2],
    ['2024-01-08',101.45,102.8,100.95,102.35],['2024-01-09',102.2,103.1,101.2,101.75],
    ['2024-01-10',101.6,102.45,100.7,101.1],['2024-01-11',101.35,103,101.05,102.7],
    ['2024-01-12',102.55,103.25,101.7,102.05],['2024-01-15',102.2,103.6,101.85,103.1],
    ['2024-01-16',103,104.1,102.35,103.75],['2024-01-17',103.9,104.45,102.7,103.05],
]

_SPECS = {
    'realized-vol-estimators':(_solve_realized,{'rows':[dict(zip(['date','open','high','low','close'],row)) for row in OHLC],'annualization':252},[],
        ['All estimators use the same 11 sessions; first row anchors previous close.','Close-to-close/overnight/open-close sample variance uses n-1; range contributions use mean over n.','Volatility is annualized decimal; rates are not implied market quotes.'],
        ['Original synthetic unadjusted OHLC; weekday labels are not an exchange trading calendar.','Estimator assumptions differ; no corporate-action adjustment or prediction is implied.'],[]),
    'bs-eur-call':(_solve_bs,{'spot':100,'strike':100,'rate':.02,'volatility':.2,'maturity_years':.5,'dividend_yield':0},[],
        ['Continuous annual rate and dividend yield; volatility is annualized decimal.','European exercise; 6 months represented as 0.5 years.','Delta per underlying unit; vega per unit volatility and per 1 percentage point are distinguished.'],
        ['Constant volatility and deterministic carry; no bid/ask, early exercise, transaction costs or live price.'],['Dividend yield is assumed zero because the brief does not supply it.']),
    'options-book-greeks':(_solve_greeks,{'delta_per_pct_point':250000,'gamma_per_pct_point_squared':-80000,'vega_per_vol_point':120000,'theta_per_day':-15000,'spot_move_pct_points':-2,'vol_move_points':3,'elapsed_days':1,'currency':'EUR'},[],
        ['Spot shock is -2 percentage points, not -0.02 in these supplied units.','Gamma P&L includes 0.5 times second derivative times squared percent-point move.','Vega is per volatility percentage point; theta is per calendar day.'],
        ['Local Taylor attribution using supplied Greeks; excludes cross-Greeks, higher orders and exact repricing.'],[]),
    'swap-dv01':(_solve_swap,{'notional':100000000,'fixed_coupon':.032,'par_rate':.03,'annuity':4.55,'shock_bp':10},[],
        ['Payer fixed / receiver floating; positive DV01 means gain for a +1 bp rate move.','Annuity is supplied and held fixed; PV=(par-fixed)*annuity*notional.'],
        ['First-order parallel shock; no curve bootstrap, annuity change, basis, convexity or transaction costs.'],[]),
    'barrier-knock-in':(_solve_barrier,{'spot_initial':1.08,'strike':1.1,'barrier':1,'notional_eur':10000000,'terminal_spots':[1.05,1,1.2]},[],
        ['Despite the immutable legacy ID, this brief specifies a DOWN-AND-OUT call.','Touch at or below 1.0000 knocks out with no rebate.','EUR base notional times USD/EUR payoff gives USD cashflow.'],
        ['Scenario cashflows, not a barrier option price or hedge Greek. Terminal spot alone does not reveal earlier barrier touch.'],
        ['For the three listed scenarios, no earlier touch is assumed; terminal touch is tested. A separate recovered-terminal example explicitly assumes prior touch.']),
    'smile-fit':(_solve_smile,{'underlying':'SPX','tenor_days':30,'quotes':[{'moneyness':.8,'iv':.29},{'moneyness':.9,'iv':.23},{'moneyness':1,'iv':.18},{'moneyness':1.1,'iv':.16},{'moneyness':1.2,'iv':.17}]},['numpy'],
        ['Fit IV=a+b*log(K/S)+c*log(K/S)^2 by ordinary least squares; IV is annualized decimal.','Numerical IV validity is checked on the five original supplied quotes.'],
        ['No option prices/bid-ask/timestamps are supplied, so price bounds, stale/crossed cleaning and IV inversion cannot be checked.','Quadratic interpolation is not SVI calibration and does not prove absence of butterfly/calendar arbitrage.','Demand/protection pressure is an interpretation to discuss, not an observed causal fact.'],[]),
    'mc-asian':(_solve_asian,{'spot':100,'strike':100,'rate':.02,'volatility':.2,'maturity_years':1,'steps':12,'paths':100000,'seed':7},['numpy'],
        ['Arithmetic Asian call; 12 equally spaced monthly GBM observations EXCLUDE t=0.','Risk-neutral drift r, zero dividend yield, discount once at maturity.','NumPy default_rng(seed=7); row-major matrix (paths, steps); one independent path is one sampling unit.','Sample SD uses ddof=1; SE=SD/sqrt(paths); approximate normal 95% CI uses 1.96 SE.'],
        ['Original constant-volatility GBM teaching calculation; no calibrated smile, issuer/funding adjustment or live quote.','Sampling interval is fixed by the contract; a Monte Carlo CI does not cover model or input error.'],['Dividend yield assumed zero; the original starter leaves the random matrix layout unspecified, now stated explicitly.']),
    'curve-boot':(_solve_curve,{'swap_rates':[[1,.03],[2,.032],[3,.0335]]},[],
        ['Single discount/forward curve, spot start, annual fixed coupons with accrual factor 1 and unit notional.','DF_n=(1-par_n*sum(previous_DFs))/(1+par_n); floating leg PV=1-DF_n.'],
        ['No market dates, business-day rules, multicurve basis or off-node interpolation are supplied.','Positive decreasing DFs are diagnostic controls, not complete market-data validation.'],[]),
    'delta-hedge':(_solve_delta,{'contracts':1000,'multiplier':100,'delta_initial':.54,'delta_next':.61},[],
        ['Long 1000 call contracts, 100 underlying shares per contract.','Signed underlying trade: positive buys, negative sells.','The supplied deltas are inputs; they are not recomputed or invented.'],
        ['Delta-neutral at the specified instants only; gamma, discrete execution, funding and transaction costs remain.'],[]),
    'iv-newton':(_solve_iv,{'market_call_price':8,'spot':100,'strike':100,'rate':.02,'maturity_years':.5,'initial_guess':.2,'tolerance':1e-10,'max_iterations':20},[],
        ['European call BSM, continuous annual rate, annualized volatility decimal and zero dividends.','Newton uses vega per volatility 1.0, not vega per volatility percentage point.','Positive [1e-8,5] bracket; bisection safeguards an invalid/low-vega Newton step; iterations count price evaluations.'],
        ['Flat volatility inversion is not a live quote. Impossible prices fail; very low vega and boundary prices need care.'],['Dividend yield assumed zero because the brief does not supply it.']),
    'autocall':(_solve_autocall,{'principal':100,'annual_coupon_rate':.08,'observations_per_year':4,'quarters':8,'autocall_level':1,'coupon_barrier':.7,'protection_barrier':.6,
        'paths':{'up':[1.02,1.04,1.06,1.08,1.10,1.12,1.14,1.16],'flat':[.95,.99,1.01,.98,1.02,1.03,1.01,1.05],'down':[.82,.68,.55,.62,.74,.69,.63,.55]}},[],
        ['NON-MEMORY coupon: 8% per year / 4 = 2 per quarter per 100 principal when level >=70%.','At each quarterly date coupon is tested first; level >=100% redeems 100 and ends the note.','At quarter 8: redeem 100 if level >=60%; otherwise redeem 100*final level.','Undiscounted deterministic scenario cashflows only; no probabilities, PV or pricing model is inferred.'],
        ['No coupon memory, issuer default, reinvestment, discounting, fees or live market data.','Eight authored observations describe full hypothetical paths; observations after an early call are unused.'],
        ['The original up/flat/down arrays supplied only 2/3/3 observations. Those prefixes are preserved verbatim and explicitly extended to eight quarterly levels.','Assume first observation at 0.25 years and no lockout; principal is normalized to 100.','Down path completion is [.62,.74,.69,.63,.55] after the original [.82,.68,.55], illustrating a later non-memory coupon without recovery of missed coupons.']),
    'cds-cs01':(_solve_cds,{'notional':50000000,'spread':.012,'risky_annuity':4.2,'shock_bp':25,'currency':'EUR','position':'protection_buyer'},[],
        ['Explicit protection BUYER: pays annual premium, positive CS01 for spread widening.','1bp=0.0001; risky annuity is supplied and held fixed.'],
        ['Annual premium cashflow and instantaneous shock P&L have different horizons and are not added as a guaranteed profit.','No default probability, recovery, accrued-on-default, roll-down, funding, jump-to-default or full curve repricing is supplied.'],
        ['Protection BUYER and EUR are fixed explicitly to resolve the unsigned original brief/output.']),
    'parametric-var':(_solve_var,{'portfolio_value':20000000,'daily_volatility':.02,'confidence':.95,'horizon_days':1,'normal_quantile':1.645,'limit':600000,'stress_return':-.05,'currency':'EUR'},[],
        ['Use the original rounded one-sided Gaussian quantile z=1.645; zero mean and linear one-day exposure.','VaR is a positive loss threshold; stress P&L keeps its signed loss.'],
        ['Gaussian parametric VaR is not maximum loss or a coverage guarantee; no heavy tails, nonlinear repricing or liquidity adjustment.','The 600k limit and -5% stress are hypothetical task inputs, not an institutional approval.'],['Currency EUR follows the original displayed output; the brief does not state a currency.']),
    'bond-duration':(_solve_bond,{'market_value':25000000,'modified_duration':6.8,'yield_shock_bp':25},[],
        ['Long bond; modified-duration DV01 is a positive magnitude, signed P&L for rates up is negative.','1bp=0.0001; shock is +25bp.'],
        ['First-order duration approximation only; no convexity input, coupon cashflows, spread/basis risk or exact repricing is supplied.'],[]),
}


def _pack_reference(exercise_id,ticket,result,conventions,limitations,assumptions):
    result=dict(result);checks=result.pop('checks')
    return {'schema_version':'tpl.practice-reference.v1','id':exercise_id,'ticket':ticket,'result':result,
            'checks':checks,'conventions':conventions,'limitations':limitations,'assumptions':assumptions,
            'execution_mode':'authored_fixed_reference; no learner code executed'}


def _spec(exercise_id):
    if not isinstance(exercise_id,str) or exercise_id not in _SPECS:raise ValueError('Unknown authored practice reference ID.')
    return _SPECS[exercise_id]


def list_reference_ids()->list[str]:
    return list(_SPECS)


def run_reference(exercise_id:str)->dict:
    solver,ticket,_,conventions,limitations,assumptions=_spec(exercise_id)
    ticket=deepcopy(ticket)
    result=_pack_reference(exercise_id,ticket,solver(ticket),conventions,limitations,assumptions)
    json.dumps(result,allow_nan=False)
    return deepcopy(result)


def export_reference(exercise_id:str,format:str='python')->str:
    solver,ticket,dependencies,conventions,limitations,assumptions=_spec(exercise_id)
    source='# Standalone authored TPL practice reference. No learner code is executed by the service.\n'
    source+='from __future__ import annotations\nimport json\nimport math\nimport statistics\n\n'
    source+='\n\n'.join(inspect.getsource(fn).rstrip() for fn in (_number,_cdf,_bsm,_newton_iv,_barrier_cashflow,solver,_pack_reference))+'\n\n'
    for name,value in [('REFERENCE_ID',exercise_id),('TICKET',ticket),('CONVENTIONS',conventions),('LIMITATIONS',limitations),('ASSUMPTIONS',assumptions)]:
        encoded=json.dumps(value,ensure_ascii=True,allow_nan=False)
        source+=f'{name} = json.loads({encoded!r})\n'
    source+=f'\nif __name__ == "__main__":\n    result = _pack_reference(REFERENCE_ID, TICKET, {solver.__name__}(TICKET), CONVENTIONS, LIMITATIONS, ASSUMPTIONS)\n    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))\n'
    if format in {'python','py'}:return source
    if format not in {'ipynb','notebook'}:raise ValueError('Reference export format must be python or ipynb.')
    notice=f'# {exercise_id}\nExecutable authored reference, same ticket as the practice brief.\n\nDependencies: '+(', '.join(dependencies) if dependencies else 'Python standard library only')+'\n\n'
    notice+='\n'.join('- '+line for line in assumptions+conventions+limitations)
    return json.dumps({'nbformat':4,'nbformat_minor':5,
        'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},
        'cells':[{'id':'reference-notes','cell_type':'markdown','metadata':{},'source':notice.splitlines(keepends=True)},
                 {'id':'reference-code','cell_type':'code','metadata':{},'source':source.splitlines(keepends=True),'execution_count':None,'outputs':[]}]},indent=2,allow_nan=False)+'\n'


def get_reference(exercise_id:str)->dict:
    solved=run_reference(exercise_id)
    return {**solved,'solution':export_reference(exercise_id),'output':json.dumps(solved,indent=2,sort_keys=True,allow_nan=False),
            'dependencies':list(_spec(exercise_id)[2]),'python_version':'>=3.10',
            'output_format':'JSON actually produced by the standalone Python reference',
            'assessment_notice':'A computed reference and self-review aid; no expert reasoning grade or hiring certification.'}


def write_reference_catalog(path:Path|None=None)->Path:
    target=Path(path) if path is not None else CATALOG
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps({'schema_version':SCHEMA,'references':[get_reference(identifier) for identifier in list_reference_ids()]},ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return target


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exercise_id',nargs='?')
    parser.add_argument('--write-catalog',action='store_true')
    parser.add_argument('--format',choices=['json','python','ipynb'],default='json')
    args=parser.parse_args()
    if args.write_catalog:
        print(str(write_reference_catalog()))
    elif args.exercise_id:
        print(json.dumps(run_reference(args.exercise_id),indent=2,allow_nan=False) if args.format=='json' else export_reference(args.exercise_id,args.format))
    else:print(json.dumps({'reference_ids':list_reference_ids()}))
