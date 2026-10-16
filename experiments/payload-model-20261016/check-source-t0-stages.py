from pathlib import Path
import sys,re,json,importlib.util
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'source-t0-model'))
import walk_model as m
previous='--previous' in sys.argv
rows=json.loads((root/('previous32-audit-rows.json' if previous else 'packets/audit-rows.json')).read_text())
points={};forward={};seed={}
for line in (root/('previous32-observer.log' if previous else 'observer.log')).read_text().splitlines():
 z=re.match(r'POINT_OBS shot=(\d+) stage=(\w+) x=(0x\w+) y=(0x\w+)',line)
 if z:
  shot,stage,x,y=z.groups();points[int(shot),stage]=int(x,16),int(y,16)
 z=re.match(r'MODEL_OBS shot=(\d+) phase=(\w+) tick=(\d+) r0=(0x\w+) r1=(0x\w+)',line)
 if z:
  shot,phase,tick,r0,r1=z.groups();forward[int(shot),phase,int(tick)]=int(r0,16),int(r1,16)
 z=re.match(r'PAYLOAD_OBS shot=(\d+) .*before=true phase=divide tick=0 .*p0=(0x\w+) p1=(0x\w+)',line)
 if z:
  shot,p0,p1=z.groups();seed[int(shot)]=int(p0,16),int(p1,16)
results=[]
for shot,row in enumerate(rows):
 tx,ty,ox,oy,ex,ey=[int(row[k],16)for k in ['tx','ty','ox','oy','ex','ey']]
 div={};mul={};slope,_,_=m.walk((tx-ox)%m.P,leg='divide',payload=(ty-oy)%m.P,diagnostics=div)
 actualD2=2*forward[shot,'multiply',0][1]%m.P
 modeledD2=(div['recovered_denominator']+3*ox-slope*slope)%m.P
 product,_,_=m.walk(actualD2,False,'multiply',payload=points[shot,'after_square'][1],diagnostics=mul)
 modelseed=m.seed_half_word((ty-oy)%m.P)
 result=dict(shot=shot,family=row.get('family','previous32'),seed_matches=(modelseed==seed[shot][1]) if shot in seed else None,
  divide_payload_matches=slope==points[shot,'after_divide'][1],
  coupled_square_matches=modeledD2==actualD2,
  multiply_payload_on_observed_input_matches=product==points[shot,'after_multiply'][1],
  multiply_recovered_D_matches=(ox-mul['recovered_denominator'])%m.P==points[shot,'after_multiply'][0],
  clean_loan_supported=div['endpoint_unit']and mul['endpoint_unit']and mul.get('FM_loan_clean',False))
 results.append(result)
keys=['seed_matches','divide_payload_matches','coupled_square_matches','multiply_payload_on_observed_input_matches','multiply_recovered_D_matches']
report=dict(source='4b2ec52f',model='source-t0-model',shots=len(rows),summary={k:sum(r[k]is True for r in results)for k in keys},details=results,status='STATE_BOUNDARY_DIFFERENTIAL_NOT_UNIVERSAL_CERTIFICATE')
controls=results[-8:] if previous else results[:12]
report['passing_controls_all_boundaries_match']=all(all(r[k]is not False for k in keys)for r in controls)
assert report['passing_controls_all_boundaries_match']
(root/('source-t0-previous32-boundaries.json'if previous else'source-t0-state-boundaries.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='details'}))
