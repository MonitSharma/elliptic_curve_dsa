from pathlib import Path
import json,re,collections
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');a=json.loads((r/'ALL-ADD-ATTRIBUTION.json').read_text());phase={};stage={}
for l in(r/'phase-attribution.log').read_text().splitlines():
 if not l.startswith(('PAY_EVENT ','STAGE_EVENT ')):continue
 x=dict(re.findall(r'(\w+)=([^ ]+)',l));shot=int(x['shot'])
 if l.startswith('PAY_EVENT '):phase[(shot,x['phase'])]=x
 else:stage[shot]=x
rows=[]
for x in a['all_events']:
 shot=int(x['shot']);p=phase.get((shot,'divide'));s=stage.get(shot);rows.append(dict(shot=shot,first_bad_global_stage=s['stage']if s else None,first_divide_PAY_tick=int(p['tick'])if p else None,first_divide_PAY_rev=p['rev']=='true'if p else None,first_divide_PAY_at=int(p['at'])if p else None,first_ADD_at=int(x['at'])))
out=dict(status='SAME-INPUT DIAGNOSTIC JOIN; NO REPAIR CLAIM',all89_add_errors=len(rows),by_first_global_stage=dict(collections.Counter(x['first_bad_global_stage']for x in rows)),by_first_divide_PAY=[dict(tick=t,rev=v,shots=n)for(t,v),n in sorted(collections.Counter((x['first_divide_PAY_tick'],x['first_divide_PAY_rev'])for x in rows).items(),key=lambda x:str(x[0]))],all_rows=rows,not_an_end_to_end_repair_count=True)
(r/'all-add-first-global-join.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='all_rows'},indent=2))
