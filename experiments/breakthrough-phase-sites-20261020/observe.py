import hashlib,json,os,subprocess
from collections import Counter
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
env=os.environ.copy();env['BREAK_CAP']='1234'
with(r/'generate.out').open('xb')as out,(r/'generate.log').open('xb')as err:subprocess.run([str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err,check=True)
assert sha(t/'ops.bin')==f['raw_control'];assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
arrays=Counter();ands=Counter();sites=[]
for l in(r/'generate.log').read_text().splitlines():
 fields=l.split('\t')
 if fields[0]=='ARRAY_CALL':phase,op,active,n,caller=fields[1:];arrays[(phase,caller,int(active),int(n))]+=1
 if fields[0]=='LIN_AND_CALL':phase,op,active,caller=fields[1:];ands[(phase,caller,int(active))]+=1
 if fields[0]=='FUSION_SITE':family,phase,op,active,n,rank,ok=fields[1:];sites.append({'family':family,'phase':phase,'op':int(op),'active':int(active),'bits':int(n),'rank':int(rank),'admissible':bool(int(ok))})
report={'status':'COMPLETE_RAW_CONTROL_BYTE_IDENTICAL','raw_sha256':f['raw_control'],
 'array_callers':[{'phase':p,'caller':c,'active':a,'requested':n,'occurrences':k}for(p,c,a,n),k in sorted(arrays.items())],
 'lin_and_callers':[{'phase':p,'caller':c,'active':a,'occurrences':k}for(p,c,a),k in sorted(ands.items())],
 'phase_sites':sites,'scope':'Source contracts only; rank<=1 predicts zero extra Toffolis and one less carry if adapted. No changed circuit, scored result or final gate.'}
(r/'PHASE-SITE-AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'arrays':len(arrays),'lin_ands':len(ands),'phase_sites':len(sites),'tight_sites':[s for s in sites if s['active']+s['bits']-1>=1233]},indent=2))
