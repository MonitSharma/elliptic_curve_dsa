import hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for hard,expected in[(1234,0),(1233,101)]:
 env=os.environ.copy();env['BREAK_CAP']='1234';env['BREAK_HARD']=str(hard)
 with(r/f'cap{hard}.out').open('xb')as out,(r/f'cap{hard}.log').open('xb')as err:rc=subprocess.run([str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err).returncode
 assert rc==expected,(hard,rc);log=(r/f'cap{hard}.log').read_text();row={'hard':hard,'exit':rc,'fresh_ids':[l for l in log.splitlines()if l.startswith('NEW_PHYSICAL_ID\t')],
 'last_lin_sites':[l for l in log.splitlines()if l.startswith('LIN_ALLOC_SITE\t')][-12:],'last_chunks':[l for l in log.splitlines()if l.startswith('CHUNK_ADMISSION\t')][-12:],'last_modular_contracts':[l for l in log.splitlines()if l.startswith('MODULAR_CONTRACT\t')][-12:]}
 if hard==1234:row['raw_sha256']=sha(t/'ops.bin');assert row['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 else:
  assert'y42: the payload op changed the set of free wires'in log;row['failed_debug_prefix_sha256']=sha(t/'failure-prefix.ops.bin');row['debug_prefix_incomplete']=True
 rows.append(row)
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());(r/'BOUNDARY-STORAGE-AUDIT.json').write_text(json.dumps({'status':'CONTROL_EXACT_SAME_FAILED_CANDIDATE_DIAGNOSED','cases':rows,'scope':'Native circuit-construction storage only. No packet inputs, arithmetic cut, resource record, final gate or nonce.'},indent=2)+'\n');print(json.dumps(rows,indent=2))
