"""Reuse frozen generic exact engine; requalify current source before screening."""
import hashlib,json,os,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=Path(__file__).resolve().parent;old=ws/'breakthrough-public140-nonce-20261020';candidate=ws/'breakthrough-depth12-finished-20261020';t=candidate/'candidate';gate=ws/'breakthrough-depth12-final-gate-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=r,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 start=time.time()
 while not(gate/'GATE-RESULT.json').exists():
  assert time.time()-start<7200
  if(gate/'controller.exit').exists():assert(gate/'controller.exit').read_text().strip()=='0','Gate stopped before usable verdict; no nonce'
  time.sleep(2)
 g=json.loads((gate/'GATE-RESULT.json').read_text());assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values())and g['label']=='depth12-context-final-20261020-v1';f=json.loads((candidate/'SOURCE-FREEZE.json').read_text());assert sha(candidate/'SOURCE-FREEZE.json')==g['candidate_source_freeze_sha256'];assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());ops=t/'ops.bin';assert sha(ops)==g['candidate_stream_sha256']==json.loads((candidate/'RESULT.json').read_text())['stream_sha256']
 engine=json.loads((old/'SEARCH-DECLARATION.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in engine['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in engine['libraries'].items());exe=old/'tool/target/release/value_prefilter';assert sha(exe)==(old/'BINARY.sha256').read_text().strip()
 assert not(r/'SEARCH-DECLARATION.json').exists();(r/'SEARCH-DECLARATION.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'source_freeze_sha256':sha(candidate/'SOURCE-FREEZE.json'),'source_freeze':str(candidate/'SOURCE-FREEZE.json'),'gate_sha256':sha(gate/'GATE-RESULT.json'),'candidate_stream_sha256':sha(ops),'engine_source_freeze':str(old/'SEARCH-DECLARATION.json'),'engine_source_freeze_sha256':sha(old/'SEARCH-DECLARATION.json'),'engine_binary':str(exe),'engine_binary_sha256':sha(exe),'libraries':engine['libraries'],'policy':'Ascending1..65536 in64-nonce windows; lowest pass, never choose by T. All completed screens/overrun retained. Eight additional partial-packet controls1..8 repeat production; full state/RNG/curve at batches0,70,140. Exact full-state rejection only, no arithmetic filters. Passing nonce additionally protected complete9024-attempt packet replay; unchanged benchmark remains mandatory.','unique_nonce_controls':8,'control_scalar_batches':24,'official_packet_attempts':9024},indent=2)+'\n')
 args=[str(exe),str(ops),'1','65536','8',str(r/'production.jsonl'),'UNUSED','64'];run(args,'qualification',dict(os.environ,QUALIFY='1'));assert 'QUALIFICATION_PASS'in(r/'qualification.log').read_text();(r/'QUALIFICATION.json').write_text(json.dumps({'status':'PASS','unique_nonce_controls':8,'protected_full_state_batches':24,'production_screens':0,'qualification_log_sha256':sha(r/'qualification.log')},indent=2)+'\n');run(args,'search');rows=[json.loads(x)for x in(r/'production.jsonl').read_text().splitlines()];nonces=sorted(x['nonce']for x in rows);assert nonces==list(range(1,max(nonces)+1));passed=sorted(x['nonce']for x in rows if x['pass']);result={'status':'LOWEST_PASS_FOUND'if passed else'EXHAUSTED_DECLARED_PREFIX','selected_nonce':min(passed)if passed else None,'production_screens':len(rows),'highest_screened':max(nonces),'passes':passed,'control_unique_nonces':8,'control_nonces':'1..8 partial packets, repeated in production;24 full-state scalar batches','production_rows_sha256':sha(r/'production.jsonl')}
 if passed:assert f'SELECTED_OFFICIAL_REPLAY nonce={passed[0]} ok=true shots=9024 classical=0 phase=0 ancilla=0'in(r/'search.log').read_text()
 (r/'SEARCH-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(r/'run.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\n');raise
