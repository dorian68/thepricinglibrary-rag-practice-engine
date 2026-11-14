"""Faithful paper/scenario positions from computed desk quotes, never live orders.

The book preserves original contracts/units and applies simulated market-factor
changes at constant contractual maturity. It does not invent autocall observations,
settlements, cash flows or trade execution. All records are process-memory only.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import uuid

from .trusted_analytics import option_analysis,autocall_analysis,swap_analysis,cds_analysis,number


def _factor(room,desk,underlying):
    if desk=='Exotics':
        text=underlying.lower()
        key=next((k for pattern,k in [('euro stoxx','SX5E'),('sx5e','SX5E'),('s&p','SPX'),('spx','SPX'),('brent','BRENT'),('wti','WTI'),('gold','GOLD'),('btc','BTC'),('bitcoin','BTC'),('eth','ETH')] if pattern in text),None)
        if key:return ('spot',key,room.market.spots[key])
    if desk=='FX':return ('fx','EURUSD',room.market.fx['EURUSD'])
    if desk=='Commodities':
        key='GOLD' if 'gold' in underlying.lower() else 'BRENT' if 'brent' in underlying.lower() else 'WTI'
        return ('spot',key,room.market.spots[key])
    if desk=='CryptoVol':
        key='ETH' if 'eth' in underlying.lower() else 'BTC'
        return ('spot',key,room.market.spots[key])
    return None


def _value(model,inputs,quantity):
    if model=='autocall':
        result=autocall_analysis(inputs,sensitivities=False)
        return result['present_value'],result['value'],result
    if model=='swap':
        result=swap_analysis(inputs);return result['value'],result['value'],result
    if model=='cds':
        result=cds_analysis(inputs);return result['value'],result['running_spread']*100,result
    result=option_analysis(inputs,model=model)
    return result['value']*quantity,result['value'],result


def _request_signature(query,side):
    return hashlib.sha256(json.dumps({'query':query,'side':side},sort_keys=True,allow_nan=False).encode()).hexdigest()


def replay_desk_paper_request(room,query:str,side:int,request_id:str|None)->dict|None:
    if request_id is None:return None
    if not isinstance(request_id,str) or not 1<=len(request_id)<=128:raise ValueError('Invalid paper idempotency key.')
    with room.paper_lock:
        previous=room.paper_requests.get(request_id)
        if previous is None:return None
        if previous['request_signature']!=_request_signature(query,side):raise ValueError('Paper idempotency key was used for a different request.')
        position=next(p for p in room.paper_positions if p['id']==previous['position_id'])
        return {'result':deepcopy(previous['quote']),'paper_position':deepcopy(position)}


def apply_desk_quote_to_book(room,quote:dict,side:int=1,request_id:str|None=None)->dict:
    if type(side) is not int or side not in {-1,1}:raise ValueError('Paper side must be +1 or -1.')
    if not isinstance(quote,dict):raise ValueError('A computed desk quote is required.')
    spec=quote.get('product_spec') or {};pricing=quote.get('pricing_result') or {};desk=quote.get('desk')
    calculation=pricing.get('calculation') or {};inputs=deepcopy(calculation.get('inputs'))
    if not isinstance(inputs,dict):raise ValueError('Paper booking requires the verified model input snapshot.')
    kind=spec.get('kind');underlying=str(spec.get('underlying') or '')
    if not underlying:raise ValueError('The original underlying must be specified.')
    if desk=='Exotics' and kind=='exotic':model='autocall';quantity=inputs['notional']
    elif desk=='Rates' and kind=='swap':model='swap';quantity=inputs['notional']
    elif desk=='Credit' and kind=='cds':model='cds';quantity=inputs['notional']
    elif kind=='option' and desk in {'FX','Commodities','CryptoVol'}:
        model={'FX':'gk','Commodities':'black76','CryptoVol':'bsm'}[desk]
        quantity=number(spec.get('quantity'), 'quantity',1e-8,1e12)
    else:raise ValueError('This quote has no matching paper-position model. No substitute product was booked.')
    pv,unit_price,_=_value(model,inputs,quantity)
    quoted=number(pricing.get('theoretical_price'),'quoted price',-1e15,1e15)
    if not math.isclose(unit_price,quoted,rel_tol=1e-9,abs_tol=1e-8):raise ValueError('Quote and retained model inputs do not reconcile; nothing booked.')
    fingerprint=hashlib.sha256(json.dumps({'model':model,'inputs':inputs,'quantity':quantity,'side':side,'underlying':underlying},sort_keys=True,allow_nan=False).encode()).hexdigest()
    with room.paper_lock:
        if request_id:
            if not isinstance(request_id,str) or not 1<=len(request_id)<=128:raise ValueError('Invalid paper idempotency key.')
            for position in room.paper_positions:
                if position.get('request_id')==request_id:
                    if position['fingerprint']!=fingerprint:raise ValueError('Paper idempotency key was used for a different contract.')
                    return deepcopy(position)
        if len(room.paper_positions)>=64:raise ValueError('This teaching paper room is limited to 64 retained positions.')
        if model=='autocall' and sum(p['model_key']=='autocall' for p in room.paper_positions)>=8:raise ValueError('This paper room supports at most eight bounded Monte Carlo positions.')
        position={'id':'PAPER-'+uuid.uuid4().hex[:12],'desk':desk,'kind':kind,'underlying':underlying,
            'label':spec.get('type',kind),'ccy':pricing.get('currency','USD'),'side':side,'quantity':quantity,
            'notional':inputs.get('notional',spec.get('notional')),'notional_currency':spec.get('notional_currency',pricing.get('currency','USD')),
            'quantity_unit': 'EUR base units' if desk=='FX' else 'underlying units' if kind=='option' else 'principal currency units',
            'entry_unit_price':unit_price,'entry_position_value':pv,
            'position_value':pv,'signed_position_value':side*pv,'mtm':0.0,'pnl_today':0.0,
            'entry_greeks':deepcopy(pricing.get('greeks',{})),
            'greeks':{k:None if v is None else side*v for k,v in pricing.get('greeks',{}).items()},
            'model_key':model,'model':calculation.get('model') or quote.get('model_choice',{}).get('model'),
            'input_snapshot':inputs,'valuation_inputs':deepcopy(inputs),'market_anchor':_factor(room,desk,underlying),
            'rate_factor':inputs.get('currency') if inputs.get('currency') in room.market.rates else None,
            'entry_rate_anchor':room.market.rates.get(inputs.get('currency'),{}).get('level'),'entry_spread_anchor':room.market.credit['IG'],
            'fingerprint':fingerprint,'request_id':request_id,'paper_only':True,'order_submitted':False,
            'created_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'persistence':'process_memory','valuation_scope':'Constant-maturity scenario mark-to-model using retained contract inputs and explicitly simulated market-factor moves; no settlement or autocall observation is invented.',
            'risk_status':'NOT_ASSESSED','limit_usage':None,'approved':False,
            'factor_scope': ('Named-currency simulated flat-curve shift; fixed coupon and tenor retained.' if model=='swap' and inputs.get('currency') in room.market.rates else
                             'Simulated IG spread shift; fixed contractual coupon retained.' if model=='cds' else
                             'Relative simulated factor move of the named underlying.' if _factor(room,desk,underlying) else
                             'No matching simulated factor: the supplied contract inputs remain frozen.')}
        room.paper_positions.append(position)
        room.paper_journal.append({'event':'paper_quote_booked','position_id':position['id'],'kind':kind,'underlying':underlying,'fingerprint':fingerprint,'timestamp':position['created_at'],'order_submitted':False})
        if request_id:
            room.paper_requests[request_id]={'request_signature':_request_signature(quote.get('query'),side),'quote':deepcopy(quote),'position_id':position['id']}
        return deepcopy(position)


def paper_snapshot(room)->list[dict]:
    result=[]
    with room.paper_lock:
        for position in room.paper_positions:
            inputs=deepcopy(position['input_snapshot']);anchor=position['market_anchor']
            if anchor:
                domain,key,base=anchor
                current=room.market.fx[key] if domain=='fx' else room.market.spots[key]
                if position['model_key']=='black76':
                    inputs['forward']=position['input_snapshot']['forward']*current/base;inputs['spot']=inputs['forward']
                else:inputs['spot']=position['input_snapshot']['spot']*current/base
            if position['model_key']=='swap' and position['rate_factor']:
                inputs['riskFreeRate']+=room.market.rates[position['rate_factor']]['level']-position['entry_rate_anchor']
            if position['model_key']=='cds':inputs['spread']=max(1e-6,inputs['spread']+(room.market.credit['IG']-position['entry_spread_anchor'])/10000)
            pv,unit,calculation=_value(position['model_key'],inputs,position['quantity'])
            scale=position['quantity'] if position['model_key'] in {'bsm','gk','black76'} else 1
            greeks={k:None if v is None else position['side']*scale*v for k,v in calculation.get('greeks',{}).items()}
            position.update({'valuation_inputs':inputs,'position_value':pv,'signed_position_value':position['side']*pv,'current_unit_price':unit,'greeks':greeks,
                             'greeks_scope':'Autocall entry sensitivities are retained in entry_greeks; refresh reprices PV but does not recompute Monte Carlo Greeks.' if position['model_key']=='autocall' else 'Recomputed position sensitivities from the retained model and scenario inputs.',
                             'mtm':position['side']*(pv-position['entry_position_value']),
                             'pnl_today':position['side']*(pv-position['entry_position_value'])})
            result.append(deepcopy(position))
    return result
