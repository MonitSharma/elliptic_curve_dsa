from pathlib import Path
import ast,json,shutil
a=Path(__file__).parent;r=a.parent/'breakthrough-public-best-drop-nonce-continuation-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('__pycache__/\n*resource-preflight*\nproduction-*.jsonl\n')
s='''"""Continue ascending exact screens on the same frozen, gate-qualified circuit."""
import hashlib,json,os,socket,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=Path(__file__).resolve().parent;prior=ws/'breakthrough-public-best-drop-nonce-v2-20261020';frozen=ws/'breakthrough-public-best-drop-finished-20261020';gate=ws/'breakthrough-public-best-drop-final-gate-20261020';engine=ws/'breakthrough-public140-nonce-20261020';exe=engine/'tool/target/release/value_prefilter';ops=frozen/'candidate/ops.bin';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\\n')
def check_source():
 g=json.loads((gate/'GATE-RESULT.json').read_text());assert g['verdict']=='FAILURE_RATE_GATE_PASS'and all(g['checks'].values());f=json.loads((frozen/'SOURCE-FREEZE.json').read_text());assert sha(frozen/'SOURCE-FREEZE.json')==g['candidate_source_freeze_sha256'];assert sha(ops)==g['candidate_stream_sha256'];assert all(sha(frozen/'candidate'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());d=json.loads((prior/'SEARCH-DECLARATION.json').read_text());assert sha(exe)==d['engine_binary_sha256'];assert sha(engine/'SEARCH-DECLARATION.json')==d['engine_source_freeze_sha256'];e=json.loads((engine/'SEARCH-DECLARATION.json').read_text());assert all(sha(engine/'tool'/p)==h for p,h in e['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in d['libraries'].items());return g,d
def inspect(path,first,limit):
 seen=bytearray(limit);passes=[];n=0;highest=first-1
 with path.open()as inp:
  for line in inp:
   row=json.loads(line);k=row['nonce'];assert first<=k<first+limit and not seen[k-first];seen[k-first]=1;n+=1;highest=max(highest,k)
   assert row['rejection_policy']=='exact_full_state_only'
   if row['pass']:passes.append(k)
 assert n>0 and n==highest-first+1 and all(seen[:n]);return {'path':str(path),'first':first,'highest':highest,'screens':n,'sha256':sha(path),'passes':sorted(passes)}
def launch(args,name,env=None):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(args,cwd=r,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
try:
 assert socket.gethostname()=='LHC-104-070';assert not(r/'CONTINUATION-DECLARATION.json').exists()
 save('CONTINUATION-DECLARATION.json',{'at_utc':datetime.now(timezone.utc).isoformat(),'policy':'Wait for initial1..65536 exact search. If exhausted continue strictly ascending contiguous65536-nonce prefixes until lowest full PASS or48bit space exhausted. No source/gate/census changes, no T-based nonce choice. One fresh requalification with original8 partial controls/24protected fullstate batches before any continuation screens; all controls/prefixes/overrun disclosed. Full9024 protected replay on first PASS; unchanged benchmark and independent local archive verification still mandatory.','source_freeze_sha256':sha(frozen/'SOURCE-FREEZE.json'),'gate_sha256':sha(gate/'GATE-RESULT.json'),'original_search':str(prior),'chunk_size':65536,'lookahead':256,'workers':16})
 while not(prior/'run.exit').exists():time.sleep(15)
 assert(prior/'run.exit').read_text().strip()=='0';g,d=check_source();pr=json.loads((prior/'SEARCH-RESULT.json').read_text());entry=inspect(prior/'production.jsonl',1,65536);assert entry['screens']==pr['production_screens']and entry['sha256']==pr['production_rows_sha256'];prefixes=[entry];controls=8;next_nonce=entry['highest']+1;selected=min(entry['passes'])if entry['passes']else None
 if selected is None:
  assert pr['status']=='EXHAUSTED_DECLARED_PREFIX'and entry['highest']==65536
  launch([str(exe),str(ops),'65537','65536','16',str(r/'UNUSED-qualification-output'),'UNUSED','256'],'qualification',dict(os.environ,QUALIFY='1'));assert'QUALIFICATION_PASS'in(r/'qualification.log').read_text();controls+=8
 while selected is None and next_nonce<1<<48:
  check_source();available=int(next(l for l in Path('/proc/meminfo').read_text().splitlines()if l.startswith('MemAvailable:')).split()[1]);assert available>100*1024*1024
  label=f'prefix-{next_nonce}';count=min(65536,(1<<48)-next_nonce);output=r/('production-'+str(next_nonce)+'.jsonl');assert not output.exists()
  save(label+'-resource-preflight.json',{'at_utc':datetime.now(timezone.utc).isoformat(),'mem_available_kib':available,'uptime':subprocess.check_output(['uptime']).decode(),'processes':subprocess.check_output(['ps','-eo','pid,pcpu,rss,nlwp,args','--sort=-pcpu']).decode(),'threads':16,'library_threads':1})
  launch([str(exe),str(ops),str(next_nonce),str(count),'16',str(output),'UNUSED','256'],label)
  entry=inspect(output,next_nonce,count);prefixes.append(entry);selected=min(entry['passes'])if entry['passes']else None
  if selected is None:assert entry['screens']==count
  save(label+'-RESULT.json',entry);save('PROGRESS.json',{'at_utc':datetime.now(timezone.utc).isoformat(),'highest_screened':entry['highest'],'cumulative_production_screens':sum(x['screens']for x in prefixes),'selected_nonce':selected,'prefixes':prefixes});next_nonce=entry['highest']+1
 if selected is not None:
  chosen=prefixes[-1];log=prior/'search.log'if len(prefixes)==1 else r/('prefix-'+str(chosen['first'])+'.log');assert f'SELECTED_OFFICIAL_REPLAY nonce={selected} ok=true shots=9024 classical=0 phase=0 ancilla=0'in log.read_text();(r/'selected-search.log').write_bytes(log.read_bytes())
 result={'status':'LOWEST_PASS_FOUND'if selected is not None else'EXHAUSTED_48BIT_SPACE','selected_nonce':selected,'production_screens':sum(x['screens']for x in prefixes),'highest_screened':prefixes[-1]['highest'],'passes':[k for p in prefixes for k in p['passes']],'prefixes':prefixes,'control_partial_packet_attempts':controls,'control_unique_nonces':8,'protected_full_state_control_batches':3*controls,'initial_failed32worker_launch_screens':0,'scope':'All completed exact ascending prefixes and overrun disclosed. Controls repeat1..8, are additional to production. No source/gate/census change or cost-based nonce choice. PASS requires separately unchanged benchmark and independent local archive/source verification.'};save('SEARCH-RESULT.json',result);(r/'run.exit').write_text('0\\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\\n');raise
'''
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Exact ascending continuation of the passed product candidate

Same source b2a01786 / stream61927788 and sole final gate PASS. Wait for current
1..65536 search; never stop/restart it or skip lower nonces. If exhausted,
continue65537 upward in contiguous65536 prefixes,16workers/256nonce windows.
Immutable engine requalification before continuation. Select lowest full PASS,
never by T; disclose every completed screen/prefix/overrun and extra controls.
No new circuit/gate/census. No alternative label/nonce may reverse a gate FAIL.
Each pass still needs unchanged9024benchmark, local source/evidence verification,
fresh public record comparison and automatic authorized challenge submission.
Resource inventories stay server-only; unrelated jobs untouched.
''');print(r)
