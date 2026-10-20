import hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for hard,expected in[(1234,0),(1233,101)]:
 env=os.environ.copy();env['BREAK_CAP']='1234';env['BREAK_HARD']=str(hard)
 with(r/f'cap{hard}.out').open('xb')as out,(r/f'cap{hard}.log').open('xb')as err:rc=subprocess.run([str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err).returncode
 assert rc==expected,(hard,rc);log=(r/f'cap{hard}.log').read_text();body=[];generic=[];sites=[]
 for line in log.splitlines():
  v=line.split('\t')
  if v[0]=='BODY_STORAGE':phase,tick,rev,active,peak,begin,end=v[1:];body.append({'phase':phase,'tick':int(tick),'reverse':bool(int(rev)),'active':int(active),'peak':int(peak),'begin':int(begin),'end':int(end)})
  if v[0]=='GENERIC_FOLD_STORAGE':phase,begin,end,active,peak,bits,k,caller=v[1:];generic.append({'phase':phase,'begin':int(begin),'end':int(end),'active':int(active),'peak':int(peak),'bits':int(bits),'lowcar':int(k),'caller':caller})
  if v[0]=='LIN_ALLOC_SITE':sites.append(line)
 row={'hard':hard,'exit':rc,'body_storage':body,'generic_fold_storage':generic,'last_lin_sites':sites[-20:]}
 if hard==1234:
  row['complete_raw_sha256']=sha(t/'ops.bin');assert row['complete_raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 else:
  assert'y42: the payload op changed the set of free wires'in log
  row['failed_debug_prefix_sha256']=sha(t/'failure-prefix.ops.bin');assert row['failed_debug_prefix_sha256']=='66ba9d6c055d7d8bbe9260c36f754359ca4df9bea1fe24a689dbc197588288c2'
 rows.append(row)
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
(r/'FOLD-STORAGE-AUDIT.json').write_text(json.dumps({'status':'EXACT_COMPLETE_CONTROL_AND_FAILED_DEBUG_PREFIX','cases':rows,'scope':'Exact native circuit construction storage only. No empirical arithmetic cut, changed circuit, scored result, final gate or nonce.'},indent=2)+'\n')
for row in rows:print(json.dumps({'hard':row['hard'],'body_calls':len(row['body_storage']),'tight_body_calls':[s for s in row['body_storage']if s['peak']>=1234],'tight_generic_folds':[s for s in row['generic_fold_storage']if s['peak']>=1234],'last_lin_sites':row['last_lin_sites'][-4:]},indent=2))
