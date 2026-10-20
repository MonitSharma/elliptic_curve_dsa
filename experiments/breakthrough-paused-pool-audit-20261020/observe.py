import hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for hard,expected in[(1234,0),(1233,101)]:
 env=os.environ.copy();env['BREAK_CAP']='1234';env['BREAK_HARD']=str(hard)
 with(r/f'cap{hard}.out').open('xb')as out,(r/f'cap{hard}.log').open('xb')as err:rc=subprocess.run([str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err).returncode
 assert rc==expected,(hard,rc);log=(r/f'cap{hard}.log').read_text();rows.append({'hard':hard,'exit':rc,'fresh_physical_ids':[l for l in log.splitlines()if l.startswith('NEW_PHYSICAL_ID\t')],
 'last_high_water':[l for l in log.splitlines()if l.startswith(('LOGICAL_HIGH\t','ARRAY_ENTRY\t'))][-30:]})
 if hard==1234:assert sha(t/'ops.bin')=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 else:
  assert'y42: the payload op changed the set of free wires'in log
  p=t/'failure-prefix.ops.bin';rows[-1]['debug_prefix']={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'not_a_complete_circuit':True}
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
(r/'POOL-AUDIT.json').write_text(json.dumps({'status':'ORIGINAL_CONTROL_EXACT_SAME_CANDIDATE_POOL_FAILURE','cases':rows,'scope':'Failed debug prefix only; no complete candidate or resource score.'},indent=2)+'\n')
print(json.dumps(rows,indent=2))
