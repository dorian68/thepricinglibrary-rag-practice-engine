"""T01–T04 reproducible local proof: native CLI, MCP stdio, HTTP, paper, AG-UI.

Uses only authored numerical tickets and a temporary empty SQLite store. No paid
corpus, external LLM, provider, broker, checkout, Docker or Ollama is contacted.
Identity/entitlement fixtures are test data, not real customers or payments.
"""
from __future__ import annotations

import argparse
import gc
from dataclasses import replace
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def oracle(s,k,t,r,q,vol):
    d1=(math.log(s/k)+(r-q+vol*vol/2)*t)/(vol*math.sqrt(t));d2=d1-vol*math.sqrt(t)
    n=lambda x:.5*(1+math.erf(x/math.sqrt(2)))
    return s*math.exp(-q*t)*n(d1)-k*math.exp(-r*t)*n(d2)


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    checks=[];proofs={}
    def check(ok,label,**detail):
        checks.append({'check':label,'pass':bool(ok),**detail})
        print(('PASS' if ok else 'FAIL')+' '+label)
    (ROOT/'.tmp').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='trust-',dir=ROOT/'.tmp',ignore_cleanup_errors=True) as temp:
        env=os.environ.copy()
        env.update({'TPL_DATA_DIR':temp,'TPL_DB_PATH':str(Path(temp)/'isolated.sqlite3'),
                    'TPL_ENVIRONMENT':'production','TPL_EMBEDDING_BACKEND':'local-hashing',
                    'TPL_LLM_PROVIDER':'template','LLM_PROVIDER':'template','GENERATION_MODE':'template',
                    'OPENAI_API_KEY':'','STRIPE_SECRET_KEY':'','TPL_AUTH_TOKEN_SECRET':secrets.token_urlsafe(48),
                    'TPL_API_KEY':secrets.token_urlsafe(48),'TPL_OPERATOR_API_KEY':secrets.token_urlsafe(48),
                    'PYTHONIOENCODING':'utf-8'})
        os.environ.update({k:v for k,v in env.items() if k.startswith('TPL_') or k in {'LLM_PROVIDER','GENERATION_MODE','OPENAI_API_KEY','STRIPE_SECRET_KEY'}})
        from pricinglibrary_rag.config import Settings
        from pricinglibrary_rag.factory import build_services
        from pricinglibrary_rag.api import create_app
        from pricinglibrary_rag.security import mint_session_token
        from pricinglibrary_rag.tool_registry import ToolRegistry
        from pricinglibrary_rag.canonical_tools import list_canonical_tools,tool_example
        from pricinglibrary_rag.agui import _run_offline_agent
        from fastapi.testclient import TestClient
        settings=replace(Settings.from_env(),source_rights_cleared=True,rate_limit_per_min=1000,
                         openai_api_key=None,llm_provider='template',environment='production')
        services=build_services(settings);client=TestClient(create_app(services))
        headers={}
        for suffix,plan in [('a','pro'),('b','pro'),('free','free')]:
            uid='trust-smoke-'+suffix;email=uid+'@isolated.test'
            token=mint_session_token(settings.auth_token_secret,user_id=uid,email=email,expires_at=int(time.time())+900)
            headers[suffix]={'Authorization':'Bearer '+token}
            if plan!='free':services.store.upsert_entitlement(email,plan,user_id=uid,status='active',source='test-fixture')
        operator=mint_session_token(settings.auth_token_secret,user_id='trust-smoke-operator',email='operator@isolated.test',role='operator',expires_at=int(time.time())+900)
        op={'Authorization':'Bearer '+operator}
        tickets=[{'spot':100,'strike':100,'maturity':1,'rate':.05,'volatility':.2},
                 {'spot':200,'strike':100,'maturity':1,'rate':.05,'volatility':.8}]
        def cli(*argv,stdin=None):
            result=subprocess.run([sys.executable,'-m','pricinglibrary_rag.cli',*argv],cwd=ROOT,env=env,
                                  input=stdin,text=True,encoding='utf-8',capture_output=True,timeout=45,check=False)
            return result
        proofs['contrasted_tickets']=[]
        for i,ticket in enumerate(tickets):
            expected=oracle(ticket['spot'],100,1,.05,0,ticket['volatility'])
            command=cli('tool-run','desk.pricing.price_vanilla_option','--payload',json.dumps(ticket))
            result=json.loads(command.stdout)
            actual=result['output']['data']['value']
            check(command.returncode==0 and abs(actual-expected)<2e-5,f'native CLI ticket {i+1}',value=actual,independent_oracle=expected)
            response=client.post('/agent/tools/desk.pricing.price_vanilla_option/run',headers=op,json={'payload':ticket})
            check(response.status_code==200 and abs(response.json()['output']['data']['value']-expected)<2e-5,f'HTTP registry ticket {i+1}')
            proofs['contrasted_tickets'].append({'inputs':ticket,'cli_value':actual,'oracle':expected})
        rpc=[{'jsonrpc':'2.0','id':i+1,'method':'tools/call','params':{'name':'desk.pricing.price_vanilla_option','arguments':ticket}} for i,ticket in enumerate(tickets)]
        stdio=cli('mcp-serve',stdin=''.join(json.dumps(item)+'\n' for item in rpc))
        replies=[json.loads(line) for line in stdio.stdout.splitlines() if line.strip()]
        check(stdio.returncode==0 and len(replies)==2,'native MCP JSONL stdio returned two responses')
        for i,reply in enumerate(replies):
            result=reply['result'];value=result['structuredContent']['tool_result']['output']['data']['value']
            check(not result['isError'] and abs(value-proofs['contrasted_tickets'][i]['oracle'])<2e-5,f'MCP stdio ticket {i+1}',value=value)
        unavailable=cli('tool-run','desk.market_data.load_ois_curve','--payload','{}')
        check(unavailable.returncode==2 and json.loads(unavailable.stdout)['output']['data'] is None,'unimplemented loader fails truthfully with CLI exit 2')
        registry=ToolRegistry();coverage=registry.coverage_report()
        proofs['coverage']={k:coverage[k] for k in ['tool_count','executable_tool_count','unavailable_tool_count','all_descriptors_valid','all_ok']}
        check(coverage['tool_count']>=883 and not coverage['all_ok'],'catalogue retained without inflated operational coverage')
        for tool in list_canonical_tools():
            result=registry.run('canonical.'+tool['id'],{'input':tool_example(tool['id'])})
            check(result['ok']==tool['available'],'canonical gateway '+tool['id'],status=result['output']['status'])
        check(client.get('/agent/desk/state').status_code==401,'anonymous paper state denied')
        check(client.post('/agent/desk/trade',headers=headers['free'],json={'query':'WTI call over 6 months'}).status_code==403,'free account cannot book Pro paper positions')
        requests=[('WTI put quantity 1000 over 6 months','black76'),
                  ('EURUSD call notional 50m over 1 year','gk'),
                  ('Athena memory autocall Euro Stoxx 50 over 3 years','autocall'),
                  ('EUR payer swap notional 2m over 7 years','swap'),
                  ('CDS protection notional 3m over 3 years','cds'),
                  ('BTC put quantity 12 over 6 months','bsm')]
        proofs['paper_contracts']=[]
        first=None
        for index,(query,model) in enumerate(requests):
            response=client.post('/agent/desk/trade',headers=headers['a'],json={'query':query,'idempotency_key':'paper-'+str(index)})
            if response.status_code!=200:
                check(False,'paper booking '+model,http_status=response.status_code,detail=response.json());continue
            payload=response.json();p=payload['paper_position'];quote=payload['result']
            check(p['model_key']==model and abs(p['entry_position_value']-quote['pricing_result']['position_value'])<1e-8 and abs(p['mtm'])<1e-8,'faithful paper '+model)
            proofs['paper_contracts'].append({key:p[key] for key in ['desk','kind','underlying','quantity','notional','ccy','model_key','entry_unit_price','entry_position_value','paper_only','order_submitted']})
            if index==0:first=payload
        state=client.get('/agent/desk/state',headers=headers['b'])
        check(state.status_code==200 and not state.json()['paper_positions'],'owner B cannot see owner A paper contracts')
        moved=client.post('/agent/desk/tick?seconds=2678400',headers=headers['a'])
        check(moved.status_code==200 and any(abs(p['mtm'])>1e-7 for p in moved.json()['paper_positions']),'simulated factor tick genuinely reprices retained contracts')
        retry=client.post('/agent/desk/trade',headers=headers['a'],json={'query':requests[0][0],'idempotency_key':'paper-0'})
        check(retry.status_code==200 and retry.json()['replayed'] and retry.json()['result']==first['result'] and len(retry.json()['snapshot']['paper_positions'])==6,'retry retains original quote without duplicate after market move')
        check(client.post('/agent/desk/tick?seconds=nan',headers=headers['a']).status_code==422,'nonfinite tick rejected')
        check(client.post('/agent/desk/trade',headers=headers['a'],json={'query':requests[0][0],'userId':'trust-smoke-b'}).status_code==422,'forged room owner field rejected')
        canonical={**tool_example('bs-pricer'),'spot':125,'strike':110,'riskFreeRate':.03,'dividendYield':.01,'volatility':.3,'maturityYears':.75}
        events=list(_run_offline_agent(services,{'messages':[{'role':'user','content':'Check Black-Scholes call-put parity on my current ticket unchanged. Answer in English.'}]},{'toolId':'bs-pricer','toolParams':canonical}))
        control=next(e['value']['params'] for e in events if e.get('name')=='app.tool.set_params')
        text=''.join(e.get('delta','') for e in events if e.get('type')=='TextMessageContent')
        check(control['spot']==125 and control['riskFreeRate']==.03 and control['volatility']==.3 and control['maturityYears']==.75,'offline AG-UI uses real canonical UI context and units')
        check('Using your ticket unchanged' in text and 'deterministic local' in text,'offline assistant English and provider limitations explicit')
        proofs['assistant_control']=control
        client.close()
        gc.collect()  # SQLite context managers commit but Windows may hold cycles until GC.
    output={'date_utc':datetime.now(timezone.utc).isoformat(),'scope':'Isolated numerical/test identities; no real clients, payments, market quotes, provider, LLM or broker. ASGI HTTP via TestClient, native CLI and MCP stdio.',
            'verdict':'PASS' if all(c['pass'] for c in checks) else 'FAIL','checks':checks,'proofs':proofs}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(output,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    print(f"{output['verdict']} {sum(c['pass'] for c in checks)}/{len(checks)} checks")
    return 0 if output['verdict']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
