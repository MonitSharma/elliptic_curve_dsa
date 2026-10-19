import hashlib,json,os,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;t=r/'observer'
freeze=json.loads((r/'SOURCE_FREEZE.json').read_text())
expected=json.loads((r.parent/'breakthrough-profile-20261020/PHASE-PROFILE.json').read_text())['prepass_stream_sha256']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for cap in freeze['caps']:
 env=os.environ.copy();env['BREAK_CAP']=str(cap)
 start=time.time()
 with (r/f'cap-{cap}.out').open('xb')as output,(r/f'cap-{cap}.log').open('xb')as log:
  run=subprocess.run(['/usr/bin/time','-v',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=output,stderr=log)
 result={'cap':cap,'exit':run.returncode,'seconds':time.time()-start,'status':'GENERATION_FAILED'if run.returncode else'RAW_ARITHMETIC_GENERATION_ONLY'}
 if run.returncode==0:
  dest=r/f'cap-{cap}.ops.bin';(t/'ops.bin').rename(dest)
  result['stream_sha256']=sha(dest)
  result['ops']=int.from_bytes(dest.read_bytes()[8:16],'little')
  phases=[]
  for line in (r/f'cap-{cap}.log').read_text().splitlines():
   if line.startswith('BREAK_PHASE\t'):
    name,end,active,peak,ccx,ccz=line.split('\t')[1:]
    phases.append({'phase':name,'end':int(end),'peak':int(peak),'active_end':int(active),'emitted_ccx':int(ccx),'emitted_ccz':int(ccz)})
  assert phases[-1]['end']==result['ops']
  result['phases']=phases
  result['builder_max_active']=max(p['peak']for p in phases)
  (r/f'cap-{cap}-phase.tsv').write_text(''.join(f"{p['phase']}\t{p['end']}\t{p['end']}\t0\n"for p in phases))
  if cap==1234:
   assert result['stream_sha256']==expected,'Raw baseline control differs; stop all cap experiments'
   result['baseline_exact_stream_control']=True
 elif cap==1234:
  raise RuntimeError('Raw baseline control failed before any other capacity run')
 (r/f'cap-{cap}-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 results.append(result)
 (r/'SWEEP-PROGRESS.json').write_text(json.dumps({'status':'DIAGNOSTIC_ADMISSION_ONLY','results':results},indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items()if k!='phases'}),flush=True)
assert all(sha(t/name)==h for name,h in {**freeze['source_files'],**freeze['protected_files']}.items())
(r/'SWEEP-RESULT.json').write_text(json.dumps({'status':'RAW_ARITHMETIC_CAP_SWEEP_COMPLETED_NO_SCORED_RESULTS','finished_at_utc':datetime.now(timezone.utc).isoformat(),'results':results},indent=2)+'\n')
