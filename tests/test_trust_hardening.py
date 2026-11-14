"""Independent numerical and transport acceptance for T01–T04."""
import json
import math

import pytest
import numpy as np

from pricinglibrary_rag.tool_registry import ToolRegistry
from pricinglibrary_rag.mcp_adapter import TplMcpAdapter
from pricinglibrary_rag.trusted_analytics import option_analysis,autocall_analysis,parse_ticket
from pricinglibrary_rag.desk import parse_request,DeskOrchestrator
from pricinglibrary_rag.llm import TemplateLLM


def oracle(s,k,t,r,q,vol,kind='call'):
    d1=(math.log(s/k)+(r-q+vol*vol/2)*t)/(vol*math.sqrt(t));d2=d1-vol*math.sqrt(t)
    n=lambda x:.5*(1+math.erf(x/math.sqrt(2)))
    if kind=='call':return s*math.exp(-q*t)*n(d1)-k*math.exp(-r*t)*n(d2)
    return k*math.exp(-r*t)*n(-d2)-s*math.exp(-q*t)*n(-d1)


@pytest.mark.parametrize('spot,vol',[(100,.2),(200,.8)])
def test_registry_mcp_and_canonical_math_agree(spot,vol):
    payload={'spot':spot,'strike':100,'maturity':1,'rate':.05,'volatility':vol}
    registry=ToolRegistry();direct=registry.run('desk.pricing.price_vanilla_option',payload)
    result=TplMcpAdapter(registry=registry).call_tool('desk.pricing.price_vanilla_option',payload=payload)
    expected=oracle(spot,100,1,.05,0,vol)
    assert direct['ok'] and direct['output']['data']['value']==pytest.approx(expected,abs=2e-5)
    assert result['tool_result']['output']['data']['value']==direct['output']['data']['value']
    assert direct['output']['data']['inputs']['spot']==spot


def test_all_descriptors_retained_but_availability_is_truthful():
    registry=ToolRegistry();coverage=registry.coverage_report()
    assert coverage['tool_count']>=874 and coverage['all_descriptors_valid']
    assert not coverage['all_ok'] and coverage['unavailable_tool_count']>0
    result=registry.run('desk.market_data.load_ois_curve',{})
    assert not result['ok'] and result['output']['status']=='unavailable'
    assert result['output']['data'] is None and not result['output']['evidence']
    assert registry.describe('desk.market_data.load_ois_curve')['executable'] is False
    assert registry.healthcheck('desk.market_data.load_ois_curve')['descriptor_ok'] is True
    assert registry.healthcheck('desk.market_data.load_ois_curve')['ok'] is False


@pytest.mark.parametrize('payload',[{}, {'spot':-1,'strike':100,'volatility':.2,'maturity':1,'rate':.05},
    {'spot':100,'strike':100,'volatility':float('inf'),'maturity':1,'rate':.05}])
def test_invalid_ticket_never_produces_default_price(payload):
    result=ToolRegistry().run('desk.pricing.price_vanilla_option',payload)
    assert not result['ok'] and result['output']['status']=='failed' and result['output']['data'] is None


def test_supplied_risk_limit_is_actually_checked():
    r=ToolRegistry().run('book.limit_usage',{'loss':1e12,'limit':1})
    assert r['ok'] and r['output']['data']['verdict']=='BREACHED'
    assert r['output']['data']['limit_usage']==1e12 and r['output']['data']['blocks_deployment']


def test_black76_and_fx_carry_match_independent_oracles():
    p={'forward':80,'strike':80,'maturity':.5,'rate':.04,'volatility':.1341}
    result=option_analysis(p,model='black76')
    assert result['value']==pytest.approx(oracle(80,80,.5,.04,.04,.1341),abs=2e-5)
    assert result['greeks']['rho']==pytest.approx(-.5*result['value']/100)
    override=option_analysis({'spot':120,'strike':100,'maturity':1,'rate':.04,'volatility':.2},model='black76',defaults={'forward':80})
    assert override['inputs']['forward']==120
    fx=option_analysis({'spot':1.08,'strike':1.10,'maturity':1,'rate':.03,'foreignRate':.02,'volatility':.12},model='gk')
    assert fx['value']==pytest.approx(oracle(1.08,1.1,1,.03,.02,.12),abs=2e-7)


def test_autocall_zero_vol_matches_independent_cashflows_and_errors():
    data={'spot':100,'referenceSpot':100,'riskFreeRate':.03,'dividendYield':0,'volatility':0,
          'maturityYears':3,'paths':256,'observationsPerYear':4}
    result=autocall_analysis(data,sensitivities=False)
    assert result['value']==pytest.approx(101.5*math.exp(-.03*.25),abs=1e-10)
    assert result['standard_error_percent_par']<1e-10
    loss=autocall_analysis({**data,'spot':50,'riskFreeRate':0},sensitivities=False)
    assert loss['value']==pytest.approx(50,abs=1e-10)


def test_autocall_seed_context_sensitivities_and_paired_error_are_real():
    a=autocall_analysis({'maturityYears':3,'paths':4096,'seed':17})
    b=autocall_analysis({'maturityYears':3,'paths':4096,'seed':17})
    changed=autocall_analysis({'maturityYears':5,'paths':4096,'seed':17})
    assert a==b and a['value']!=changed['value']
    assert a['standard_error_percent_par']>0 and a['independent_antithetic_pairs']==2048
    assert a['greeks']['correlation'] is None
    assert all(math.isfinite(a['greeks'][k]) and a['greek_standard_errors'][k]>=0 for k in ['delta','gamma','vega'])
    with pytest.raises(ValueError):autocall_analysis({'paths':4097})
    with pytest.raises(ValueError):autocall_analysis({'paths':2000000})


def test_autocall_one_date_matches_capped_stock_oracle_and_paired_mcse():
    params={'spot':100,'referenceSpot':100,'riskFreeRate':.03,'dividendYield':.01,'volatility':.22,
            'maturityYears':1,'couponRate':0,'observationsPerYear':1,'autocallBarrier':1,'protectionBarrier':1,
            'paths':16384,'seed':123}
    result=autocall_analysis(params,sensitivities=False)
    expected=(math.exp(-.03)-oracle(1,1,1,.03,.01,.22,'put'))*100
    assert abs(result['value']-expected)<=4*result['standard_error_percent_par']
    # A single-date zero-coupon payoff is exactly min(1,S_T/S0), so its error
    # can be independently reconstructed without the coupon/autocall loop.
    z=np.random.default_rng(123).standard_normal(8192)
    up=np.minimum(1,np.exp((.03-.01-.22**2/2)+.22*z))*math.exp(-.03)*100
    down=np.minimum(1,np.exp((.03-.01-.22**2/2)-.22*z))*math.exp(-.03)*100
    paired=(up+down)/2
    assert result['standard_error_percent_par']==pytest.approx(float(paired.std(ddof=1)/math.sqrt(8192)),abs=1e-12)


def test_rfq_model_context_and_unassessed_limits():
    desk=DeskOrchestrator(TemplateLLM())
    call=desk.run('Price a WTI call over 6 months')
    assert call['pricing']['est_price']==pytest.approx(oracle(80,80,.5,.04,.04,.1341),abs=2e-5)
    assert call['risk']['limit_usage'] is None and call['risk']['approved'] is False
    parsed=parse_request('Price an Athena memory coupon autocall on Euro Stoxx 50 over 3 years')
    assert parsed['underlying']=='Euro Stoxx 50'
    result=desk.run('Price an Athena memory coupon autocall on Euro Stoxx 50 over 3 years')
    assert result['product_spec']['underlying']=='Euro Stoxx 50'
    assert 'GBM' in result['model_choice']['model'] and 'Local-stochastic' not in result['model_choice']['model']
    assert result['pricing_result']['calculation']['paths']==8192


def test_offline_assistant_preserves_exact_ticket_and_english():
    from pricinglibrary_rag.agui import _run_offline_agent
    # This intent requires no corpus/provider; computations use actual executors.
    class Services:pass
    s=Services()
    prompt='Check Black-Scholes call-put parity for S=125 K=110 r=3% q=1% sigma=30% T=0.75 years; keep my ticket unchanged. Answer in English.'
    payload={'messages':[{'role':'user','content':prompt}]}
    events=list(_run_offline_agent(s,payload,{'toolId':'bs-pricer','toolParams':{}}))
    calls=[json.loads(e['delta']) for e in events if e.get('type')=='ToolCallArgs']
    params=next(c['params'] for c in calls if c.get('tool')=='bs-pricer')
    assert params['S']==125 and params['K']==110 and params['T']==273.75
    assert params['r']==3 and params['q']==1 and params['sigma']==30
    text=''.join(e.get('delta','') for e in events if e.get('type')=='TextMessageContent')
    assert 'ticket unchanged' in text and "J'ai" not in text and '21.977' in text


def test_real_http_registry_and_rfq_models(tmp_path):
    from test_api_security import _settings,AUTH_SECRET
    from pricinglibrary_rag.factory import build_services
    from pricinglibrary_rag.api import create_app
    from pricinglibrary_rag.security import mint_session_token
    from fastapi.testclient import TestClient
    import time
    services=build_services(_settings(tmp_path));client=TestClient(create_app(services))
    token=mint_session_token(AUTH_SECRET,user_id='trust-operator',email='trust@isolated.test',role='operator',expires_at=int(time.time())+300)
    headers={'Authorization':'Bearer '+token}
    for s,v in [(100,.2),(200,.8)]:
        response=client.post('/agent/tools/desk.pricing.price_vanilla_option/run',headers=headers,
            json={'payload':{'spot':s,'strike':100,'maturity':1,'rate':.05,'volatility':v}})
        assert response.status_code==200 and response.json()['output']['data']['value']==pytest.approx(oracle(s,100,1,.05,0,v),abs=2e-5)
    unavailable=client.post('/agent/tools/desk.market_data.load_ois_curve/run',headers=headers,json={'payload':{}})
    assert unavailable.status_code==200 and unavailable.json()['output']['status']=='unavailable' and not unavailable.json()['ok']
    response=client.post('/agent/desk/run',headers=headers,json={'query':'Price an Athena memory coupon autocall on Euro Stoxx 50 over 3 years'})
    assert response.status_code==200
    result=response.json()
    assert result['product_spec']['underlying']=='Euro Stoxx 50' and result['pricing_result']['calculation']['paths']==8192
    assert result['risk']['limit_usage'] is None and result['risk']['approved'] is False


def test_operator_cli_propagates_unavailable_exit(monkeypatch,tmp_path,capsys):
    from pricinglibrary_rag import cli
    from pricinglibrary_rag.factory import build_services
    from test_api_security import _settings
    services=build_services(_settings(tmp_path))
    monkeypatch.setattr(cli,'build_services',lambda:services)
    with pytest.raises(SystemExit) as exc:cli.main(['tool-run','desk.market_data.load_ois_curve','--payload','{}'])
    assert exc.value.code==2 and json.loads(capsys.readouterr().out)['output']['status']=='unavailable'
    with pytest.raises(SystemExit) as exc:cli.main(['mcp-call','desk.market_data.load_ois_curve','--payload','{}'])
    assert exc.value.code==2 and not json.loads(capsys.readouterr().out)['tool_result']['ok']


def test_registry_delegates_to_actual_nine_engine_gateway():
    from pricinglibrary_rag.canonical_tools import tool_example
    r=ToolRegistry();result=r.run('canonical.bs-pricer',{'input':tool_example('bs-pricer')})
    assert result['ok'] and result['output']['data']['selected']['unitPrice']==pytest.approx(10.450575,abs=2e-5)


def _offline(prompt,ctx):
    from pricinglibrary_rag.agui import _run_offline_agent
    return list(_run_offline_agent(object(),{'messages':[{'role':'user','content':prompt}]},ctx))


def test_current_canonical_ui_context_uses_decimals_and_controls_real_keys():
    from pricinglibrary_rag.canonical_tools import tool_example
    ticket={**tool_example('bs-pricer'),'spot':125,'strike':110,'riskFreeRate':.03,'dividendYield':.01,'volatility':.3,'maturityYears':.75}
    events=_offline('Check call-put parity for my current ticket unchanged. Answer in English.',{'toolId':'bs-pricer','toolParams':ticket})
    params=next(e['value']['params'] for e in events if e.get('name')=='app.tool.set_params')
    assert params['spot']==125 and params['riskFreeRate']==pytest.approx(.03)
    assert params['volatility']==pytest.approx(.3) and params['maturityYears']==.75
    text=''.join(e.get('delta','') for e in events if e.get('type')=='TextMessageContent')
    import re
    assert float(re.search(r'Call=([\d.]+)',text).group(1))==pytest.approx(oracle(125,110,.75,.03,.01,.3),abs=2e-5)
    greek=_offline('Show vega sensitivity as maturity increases in English.',{'toolId':'bs-pricer','toolParams':ticket})
    args=next(json.loads(e['delta']) for e in greek if e.get('type')=='ToolCallArgs')
    assert args['S']==125 and args['sigma']==30 and args['r']==3 and args['T']==273.75


def test_canonical_monte_carlo_context_keeps_mode_measure_seed_and_ticket():
    from pricinglibrary_rag.canonical_tools import tool_example
    ticket={**tool_example('mc'),'spot':125,'seed':77,'paths':2000}
    events=_offline('Run Monte Carlo on my current ticket in English.',{'toolId':'mc','toolParams':ticket})
    args=next(json.loads(e['delta']) for e in events if e.get('type')=='ToolCallArgs')
    assert args['input']==ticket
    result=next(json.loads(e['content']) for e in events if e.get('type')=='ToolCallResult')
    assert result['inputs']['spot']==125 and result['inputs']['seed']==77
    assert result['measure']=='Q' and result['pricing'] is not None


def test_active_payoff_strategy_is_not_replaced_by_a_named_example():
    from pricinglibrary_rag.canonical_tools import tool_example
    ticket=tool_example('payoff')
    ticket['legs'][0].update({'strike':137,'quantity':3,'manualPremium':7})
    events=_offline('Explain the payoff of my current strategy and keep my ticket unchanged, in English.',{'toolId':'payoff','toolParams':ticket})
    assert not any(e.get('name')=='app.tool.set_params' for e in events)
    args=next(json.loads(e['delta']) for e in events if e.get('type')=='ToolCallArgs')
    assert args['input']==ticket
    result=next(json.loads(e['content']) for e in events if e.get('type')=='ToolCallResult')
    assert result['bounds']['maxProfit']['kind']=='unlimited'
    assert result['bounds']['maxLoss']['amount']==21


@pytest.mark.parametrize('query,desk,underlying',[
    ('Price EURUSD put rate 3% vol 12% over 1 year','FX','EUR/USD'),
    ('Price a Brent call over 6 months','Commodities','Brent Crude'),
    ('Price an Athena autocall on Euro Stoxx 50 over 3 years','Exotics','Euro Stoxx 50'),
])
def test_routing_preserves_named_underlying(query,desk,underlying):
    q=DeskOrchestrator(TemplateLLM()).run(query)
    assert q['desk']==desk and q['product_spec']['underlying']==underlying


@pytest.mark.parametrize('query',['Price a range accrual on EURUSD over 3 years',
    'Price a worst-of Athena autocall over 3 years','Price a USD swaption over 5 years',
    'Price an EURUSD forward over 1 year','Price a barrier option on WTI over 1 year'])
def test_unimplemented_rfq_contract_never_gets_a_substitute_price(query):
    with pytest.raises(ValueError,match='no substitute'):
        DeskOrchestrator(TemplateLLM()).run(query)


def test_paper_positions_retain_all_six_products_and_owner_isolation():
    from pricinglibrary_rag.desk_state import get_room,apply_desk_quote_to_book
    import uuid
    a=get_room('trust-a-'+uuid.uuid4().hex);b=get_room('trust-b-'+uuid.uuid4().hex)
    engine=DeskOrchestrator(TemplateLLM())
    cases=[('WTI put quantity 1000 over 6 months','Commodities','black76'),
           ('EURUSD call notional 50m over 1 year','FX','gk'),
           ('Athena autocall on Euro Stoxx 50 over 3 years','Exotics','autocall'),
           ('USD payer swap notional 2m over 7 years','Rates','swap'),
           ('CDS protection notional 3m over 3 years','Credit','cds'),
           ('BTC put quantity 12 over 6 months','CryptoVol','bsm')]
    positions=[]
    for query,desk,model in cases:
        quote=engine.run(query,room=a);p=apply_desk_quote_to_book(a,quote)
        assert p['desk']==desk and p['model_key']==model and p['underlying']==quote['product_spec']['underlying']
        assert p['entry_unit_price']==pytest.approx(quote['pricing_result']['theoretical_price'])
        assert p['entry_position_value']==pytest.approx(quote['pricing_result']['position_value'])
        assert p['input_snapshot']==quote['pricing_result']['calculation']['inputs']
        assert p['paper_only'] and not p['order_submitted'] and p['mtm']==0
        positions.append(p)
    assert positions[0]['quantity']==1000 and positions[1]['quantity']==50e6
    assert positions[3]['notional']==2e6 and positions[4]['notional']==3e6
    assert positions[4]['input_snapshot']['maturityYears']==3
    assert positions[5]['quantity']==12
    state=a.snapshot()
    assert len(state['paper_positions'])==6 and len(state['paper_journal'])==6
    assert all(abs(p['mtm'])<1e-8 for p in state['paper_positions'])
    assert state['desk']['risk_status']=='NOT_ASSESSED' and state['desk']['limit_usage'] is None
    assert state['paper_summary']['positions']==6 and not b.snapshot()['paper_positions']


def test_paper_idempotence_invalid_price_atomicity_and_exact_scenario_marks():
    from pricinglibrary_rag.desk_state import TradingRoom,apply_desk_quote_to_book
    from copy import deepcopy
    room=TradingRoom();engine=DeskOrchestrator(TemplateLLM())
    query=json.dumps({'underlying':'Brent Crude','ticket':{'forward':110,'strike':100,'maturityYears':.5,'riskFreeRate':.03,'volatility':.4,'quantity':1234}})
    quote=engine.run(query,room=room)
    p=apply_desk_quote_to_book(room,quote,side=-1,request_id='paper-idempotent')
    assert apply_desk_quote_to_book(room,quote,side=-1,request_id='paper-idempotent')['id']==p['id']
    assert len(room.paper_positions)==1 and len(room.paper_journal)==1
    with pytest.raises(ValueError,match='different contract'):apply_desk_quote_to_book(room,quote,side=1,request_id='paper-idempotent')
    bad=deepcopy(quote);bad['pricing_result']['theoretical_price']+=1
    with pytest.raises(ValueError,match='reconcile'):apply_desk_quote_to_book(room,bad)
    assert len(room.paper_positions)==1
    room.market.spots['BRENT']*=1.1
    mark=room.snapshot()['paper_positions'][0]
    expected=option_analysis({**p['input_snapshot'],'forward':121},model='black76')
    assert mark['input_snapshot']==p['input_snapshot'] and mark['valuation_inputs']['forward']==pytest.approx(121)
    assert mark['position_value']==pytest.approx(expected['value']*1234)
    assert mark['mtm']==pytest.approx(p['entry_position_value']-expected['value']*1234)
    assert mark['greeks']['delta']==pytest.approx(-expected['greeks']['delta']*1234)


def test_autocall_paper_refresh_uses_sx5e_not_spx_and_preserves_contract():
    from pricinglibrary_rag.desk_state import TradingRoom,apply_desk_quote_to_book
    room=TradingRoom();quote=DeskOrchestrator(TemplateLLM()).run('Athena autocall Euro Stoxx 50 over 3 years',room=room)
    p=apply_desk_quote_to_book(room,quote)
    room.market.spots['SPX']*=2
    assert room.snapshot()['paper_positions'][0]['mtm']==pytest.approx(0,abs=1e-8)
    room.market.spots['SX5E']*=.5
    mark=room.snapshot()['paper_positions'][0]
    expected=autocall_analysis({**p['input_snapshot'],'spot':50},sensitivities=False)
    assert mark['valuation_inputs']['spot']==50 and mark['input_snapshot']['referenceSpot']==100
    assert mark['position_value']==expected['present_value'] and mark['underlying']=='Euro Stoxx 50'
    assert mark['greeks']['delta'] is None and p['entry_greeks']['delta'] is not None


def test_production_paper_http_owner_plans_idempotent_retry_and_bounded_tick(tmp_path):
    from test_api_security import _settings,AUTH_SECRET,OPERATOR_KEY
    from pricinglibrary_rag.factory import build_services
    from pricinglibrary_rag.api import create_app
    from pricinglibrary_rag.security import mint_session_token
    from fastapi.testclient import TestClient
    import time,uuid
    services=build_services(_settings(tmp_path));client=TestClient(create_app(services))
    roles={}
    for suffix,plan in [('a','pro'),('b','pro'),('free','free')]:
        user='paper-http-'+suffix+'-'+uuid.uuid4().hex;email=user+'@isolated.test'
        token=mint_session_token(AUTH_SECRET,user_id=user,email=email,expires_at=int(time.time())+300)
        roles[suffix]={'Authorization':'Bearer '+token}
        if plan!='free':services.store.upsert_entitlement(email,plan,user_id=user,status='active',source='test')
    assert client.get('/agent/desk/state').status_code==401
    assert client.post('/agent/desk/trade',headers={'X-API-Key':OPERATOR_KEY},json={'query':'WTI call 6 months'}).status_code==401
    for route in ['run','trade','tick']:
        assert client.post('/agent/desk/'+route,headers=roles['free'],json={'query':'WTI call 6 months'}).status_code==403
    assert client.get('/agent/desk/state',headers=roles['free']).status_code==403
    query=json.dumps({'underlying':'EUR/USD','ticket':{'spot':1.1,'strike':1.05,'riskFreeRate':.03,'dividendYield':.02,'volatility':.2,'maturityYears':1,'quantity':7654321}})
    first=client.post('/agent/desk/trade',headers=roles['a'],json={'query':query,'side':-1,'idempotency_key':'one-intent'})
    assert first.status_code==200
    payload=first.json();position=payload['paper_position']
    assert not payload['replayed'] and position['desk']=='FX' and position['kind']=='option' and position['quantity']==7654321
    assert position['input_snapshot']['optionType']=='call' and position['mtm']==0
    assert position['entry_position_value']==pytest.approx(oracle(1.1,1.05,1,.03,.02,.2)*7654321,abs=2)
    assert client.get('/agent/desk/state',headers=roles['b']).json()['paper_positions']==[]
    tick=client.post('/agent/desk/tick?seconds=2678400',headers=roles['a'])
    assert tick.status_code==200 and tick.json()['paper_positions'][0]['mtm']!=0
    retry=client.post('/agent/desk/trade',headers=roles['a'],json={'query':query,'side':-1,'idempotency_key':'one-intent'})
    assert retry.status_code==200 and retry.json()['replayed']
    assert retry.json()['paper_position']['id']==position['id'] and retry.json()['result']==payload['result']
    assert len(retry.json()['snapshot']['paper_positions'])==1
    conflict=client.post('/agent/desk/trade',headers=roles['a'],json={'query':query,'side':1,'idempotency_key':'one-intent'})
    assert conflict.status_code==422
    for seconds in ['-1','inf','nan','2678401']:
        assert client.post('/agent/desk/tick?seconds='+seconds,headers=roles['a']).status_code==422
    for invalid in [{'query':query,'userId':'someone-else'},{'query':query,'side':True},{'query':query,'side':0}]:
        assert client.post('/agent/desk/trade',headers=roles['a'],json=invalid).status_code==422
    assert len(client.get('/agent/desk/state',headers=roles['a']).json()['paper_positions'])==1
    assert client.get('/agent/desk/state',headers=roles['b']).json()['paper_journal']==[]


def test_swap_and_cds_match_independent_non_par_present_values():
    from pricinglibrary_rag.trusted_analytics import swap_analysis,cds_analysis
    ann=math.exp(-.04)+math.exp(-.08)+.5*math.exp(-.1)
    swap=swap_analysis({'notional':1e6,'maturityYears':2.5,'riskFreeRate':.04,'fixedRate':.03})
    assert swap['value']==pytest.approx(1e6*(1-math.exp(-.1)-.03*ann),abs=1e-9)
    receiver=swap_analysis({**swap['inputs'],'direction':'receiver'})
    assert receiver['value']==-swap['value'] and receiver['greeks']['dv01']==-swap['greeks']['dv01']
    cds=cds_analysis({'notional':1e6,'maturityYears':3,'riskFreeRate':.03,'spread':.012,'coupon':.01,'recovery':.4})
    a=.03+.012/.6;ann=-math.expm1(-a*3)/a
    assert cds['value']==pytest.approx(1e6*ann*.002,abs=1e-9)
    derivative=(3*math.exp(-a*3)*a+math.expm1(-a*3))/(a*a)/.6
    assert cds['greeks']['cs01']==pytest.approx(1e6*(ann+.002*derivative)*.0001,rel=1e-7)


def test_eur_swap_paper_refresh_uses_its_currency_curve():
    from pricinglibrary_rag.desk_state import TradingRoom,apply_desk_quote_to_book
    from pricinglibrary_rag.trusted_analytics import swap_analysis
    room=TradingRoom();quote=DeskOrchestrator(TemplateLLM()).run('EUR payer swap notional 2m over 7 years',room=room)
    assert quote['product_spec']['underlying']=='EUR rates (7Y)' and quote['pricing_result']['currency']=='EUR'
    position=apply_desk_quote_to_book(room,quote)
    room.market.rates['USD']['level']+=.01
    assert room.snapshot()['paper_positions'][0]['mtm']==pytest.approx(0,abs=1e-8)
    room.market.rates['EUR']['level']+=.01
    mark=room.snapshot()['paper_positions'][0]
    expected=swap_analysis({**position['input_snapshot'],'riskFreeRate':position['input_snapshot']['riskFreeRate']+.01})
    assert mark['position_value']==expected['value'] and mark['mtm']!=0


def test_optional_nonfinite_ticket_field_is_rejected_before_json_response():
    result=ToolRegistry().run('desk.pricing.price_vanilla_option',{'spot':100,'strike':100,'maturity':1,'rate':.05,'volatility':.2,'unused_field':float('nan')})
    assert not result['ok'] and result['output']['data'] is None
    json.dumps(result,allow_nan=False)


def test_business_btc_put_contract_label_matches_the_computed_ticket():
    result=DeskOrchestrator(TemplateLLM()).run('BTC put quantity 3 over 3 months S=20000 K=21000 r=3% sigma=70% T=0.25 years')
    spec=result['product_spec'];pricing=result['pricing_result'];inputs=pricing['inputs']
    assert spec['optionType']==spec['option_type']==inputs['optionType']=='put'
    assert spec['strike']==inputs['strike']==21000 and spec['spot']==inputs['spot']==20000
    assert spec['maturity_years']==inputs['maturityYears']==.25 and spec['moneyness']=='ITM'
    assert 'Put' in spec['type'] and 'Call' not in spec['type'] and 'ATM' not in spec['type']
    assert '21000' in spec['type'] and '0.25Y' in spec['type'] and 'max(K - S_T, 0)' in spec['payoff_description']
    assert pricing['theoretical_price']==pytest.approx(3278.027771491523,abs=1e-9)
    assert spec['inputs']==inputs and spec['contract_summary']==pricing['contract_summary']
    structurer=next(role for role in result['agents'] if role['role']=='Structurer')
    assert spec['type'] in structurer['output'] and 'Call' not in structurer['output']
    assert result['pricing']['product']==spec['type']


@pytest.mark.parametrize('underlying,basis,base,strike,kind,expected',[
    ('BTC','spot',20000,19000,'put','OTM'),('BTC','spot',20000,21000,'call','OTM'),
    ('EUR/USD','spot',1.1,1,'put','OTM'),('EUR/USD','spot',1.1,1.2,'call','OTM'),
    ('WTI','forward',100,90,'put','OTM'),('WTI','forward',100,110,'call','OTM'),
    ('WTI','forward',100,100,'call','ATM'),
])
def test_all_option_families_publish_strike_type_horizon_and_moneyness_from_actual_engine(underlying,basis,base,strike,kind,expected):
    ticket={basis:base,'strike':strike,'optionType':kind,'maturityYears':.123456789,'riskFreeRate':.03,'dividendYield':.02,'volatility':.4,'quantity':7}
    result=DeskOrchestrator(TemplateLLM()).run(json.dumps({'underlying':underlying,'ticket':ticket}))
    spec=result['product_spec'];pricing=result['pricing_result'];inputs=pricing['calculation']['inputs']
    assert spec['inputs']==inputs and spec['optionType']==spec['option_type']==kind
    assert spec['strike']==strike and spec['maturity_years']==spec['maturityYears']==.123456789
    assert spec['moneyness']==expected and spec['moneyness_basis']==basis
    assert f'K {strike:.12g}' in spec['type'] and '.123456789Y' in spec['type']
    assert spec['contract_summary']==pricing['contract_summary']
    model='black76' if basis=='forward' else 'gk' if underlying=='EUR/USD' else 'bsm'
    independent_run=option_analysis(ticket,model=model)
    assert pricing['theoretical_price']==independent_run['value']
    if kind=='put':assert 'max(K - ' in spec['payoff_description']


@pytest.mark.parametrize('query,kind',[
    (json.dumps({'underlying':'EUR rates','ticket':{'direction':'receiver','currency':'EUR','maturityYears':2.5,'fixedRate':.027,'notional':2345678}}),'swap'),
    (json.dumps({'underlying':'IG credit CDS','ticket':{'maturityYears':3.5,'coupon':.01,'spread':.015,'recovery':.35,'notional':3456789}}),'cds'),
    (json.dumps({'underlying':'Euro Stoxx 50 autocall','autocall':{'maturityYears':4.25,'couponRate':.09,'autocallBarrier':1.1,'couponBarrier':.75,'protectionBarrier':.55,'observationsPerYear':2,'paths':256}}),'exotic'),
])
def test_nonvanilla_spec_contracts_are_synchronized_to_priced_inputs(query,kind):
    result=DeskOrchestrator(TemplateLLM()).run(query);spec=result['product_spec'];pricing=result['pricing_result'];inputs=pricing['inputs']
    assert spec['kind']==kind and spec['inputs']==inputs and spec['maturityYears']==inputs['maturityYears']
    assert spec['contract_summary']==pricing['contract_summary'] and f"{inputs['maturityYears']:.12g}Y" in spec['type']
    assert result['parsed']['horizon']==result['rfq']['horizon']==f"{inputs['maturityYears']:.12g} Years"
    if kind=='swap':
        assert spec['direction']=='receiver' and 'Receiver' in spec['type'] and 'Payer' not in spec['type']
        assert spec['fixedRate']==inputs['fixedRate'] and '(fixed - par)' in spec['payoff_description']
    elif kind=='cds':
        assert spec['coupon']==inputs['coupon']==.01 and spec['recovery']==.35 and 'Protection Buyer' in spec['type']
    else:
        assert spec['couponRate']==.09 and spec['couponBarrier']==.75 and spec['protectionBarrier']==.55
        assert '110%' in spec['payoff_description'] and '75%' in spec['payoff_description'] and '55%' in spec['payoff_description']
        assert spec['observation_times_years']==pricing['calculation']['observation_times_years']
