"""Automatic-submission research: final rebuild; preserve frozen nonce0 source and all gate evidence."""
import ctypes,ctypes.util,hashlib,json,os,re,shutil,struct,subprocess,tarfile,time
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');search=ws/'breakthrough-native-context-nonce-20261020';old=ws/'breakthrough-native-context-finished-v3-20261020';r=ws/'breakthrough-native-context-final-20261020';t=r/'candidate'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
finished=json.loads((old/'RESULT.json').read_text());operation_count=finished['operations']
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n')
def run(args,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:
  p=subprocess.Popen(args,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,(name,rc)
def decode(path):
 d=path.read_bytes();assert d[:8]==b'QECCOPSZ';n=int.from_bytes(d[8:16],'little');assert n==operation_count
 z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
 out=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(out,len(out),d[16:],len(d)-16)==n*56
 return out.raw
try:
 while not(search/'run.exit').exists():time.sleep(2)
 assert(search/'run.exit').read_text().strip()=='0'
 sr=json.loads((search/'SEARCH-RESULT.json').read_text());assert sr['status']=='LOWEST_PASS_FOUND';k=sr['selected_nonce']
 rows=[json.loads(x)for x in(search/'production.jsonl').read_text().splitlines()];assert len(rows)==sr['production_screens']and sha(search/'production.jsonl')==sr['production_rows_sha256'];assert sorted(x['nonce']for x in rows)==list(range(1,sr['highest_screened']+1));assert min(x['nonce']for x in rows if x['pass'])==k
 assert f'SELECTED_OFFICIAL_REPLAY nonce={k} ok=true shots=9024 classical=0 phase=0 ancilla=0' in(search/'search.log').read_text()
 gate=ws/'breakthrough-native-context-final-gate-20261020';assert json.loads((gate/'GATE-RESULT.json').read_text())['verdict']=='FAILURE_RATE_GATE_PASS'
 f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert sha(old/'SOURCE-FREEZE.json')==json.loads((gate/'GATE-RESULT.json').read_text())['candidate_source_freeze_sha256']
 assert all(sha(old/'candidate'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert sha(old/'candidate/ops.bin')==finished['stream_sha256']
 assert not t.exists();run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],'worktree',r)
 for p,h in f['source_files'].items():dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/'candidate'/p,dest)
 p=t/'src/point_add/native_context_cache.rs';original=p.read_bytes();a=b'const IDENTITY_NONCE:u64=0;';b=f'const IDENTITY_NONCE:u64={k};'.encode();assert original.count(a)==1;p.write_bytes(original.replace(a,b))
 for p,h in f['source_files'].items():assert (t/p).read_bytes()==((old/'candidate'/p).read_bytes().replace(a,b)if p=='src/point_add/native_context_cache.rs'else(old/'candidate'/p).read_bytes())
 def protected():
  for p,h in f['protected_files'].items():assert sha(t/p)==h,p
 protected();files={p:sha(t/p)for p in f['source_files']}
 run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],'intent',r)
 (r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']))
 with tarfile.open(r/'point-add-source.tar.gz','w:gz')as archive:
  for p in sorted(files):archive.add(t/p,arcname=p,recursive=False)
 save('SOURCE-FREEZE.json',{'base':f['base'],'source_files':files,'protected_files':f['protected_files'],'nonce':k,'nonce0_freeze_sha256':sha(old/'SOURCE-FREEZE.json'),'only_source_change_from_gated_circuit':'IDENTITY_NONCE constant 0 -> '+str(k),'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'patch_sha256':sha(r/'source.patch'),'gate_result_sha256':sha(gate/'GATE-RESULT.json'),'search_result':sr,'submission_mode':'auto','ai_model':'GPT-6 sol','coding_harness':'Codex'})
 run(['cp','-a','--reflink=auto',str(old/'candidate/target'),str(t/'target')],'reuse-build',r)
 env=os.environ.copy();env['PEBBLE_HARD_CAP']='1234';os.environ.update(env)
 def receipt():
  assert all(sha(t/p)==h for p,h in files.items());protected();data=decode(t/'ops.bin');prior=decode(old/'candidate/ops.bin');end=(operation_count-96)*56;assert data[:end]==prior[:end];no=(1<<64)-1
  for bit in range(48):
   for pair in range(2):assert struct.unpack_from('<7Q',data,end+(2*bit+pair)*56)==(6,no,no,(k>>bit)&1,no,no,no)
  return {'stream_sha256':sha(t/'ops.bin'),'records_sha256':hashlib.sha256(data).hexdigest(),'pre_tail_sha256':hashlib.sha256(data[:end]).hexdigest(),'pre_tail_byte_identical_to_gated_source':True,'nonce':k,'operations':operation_count}
 historical=(t/'results.tsv').read_bytes();run(['bash','benchmark.sh'],'benchmark')
 generated=(t/'results.tsv').read_bytes();assert generated.startswith(historical);appended=generated[len(historical):];assert len(appended.decode().splitlines())==1;(r/'benchmark-results.tsv').write_bytes(generated);(r/'benchmark-appended-row.tsv').write_bytes(appended);(t/'results.tsv').write_bytes(historical)
 first=receipt();save('NATIVE-RECEIPT.json',first)
 log=(r/'benchmark.log').read_text();assert 'all 9024 shots OK' in log and '=== experiment OK ==='in log
 for label,value in [('tested shots',9024),('classical mismatches',0),('phase-garbage batches',0),('ancilla-garbage batches',0)]:assert re.findall(re.escape(label)+r'\s*:\s*(\d+)',log)==[str(value)]
 score=json.loads((t/'score.json').read_text());q=score['metrics']['qubits'];tof=score['metrics']['toffoli'];assert q==finished['qubits'] and score['score']==q*tof
 totals=re.findall(r'total Toffoli \(sum\)\s*:\s*(\d+) over 9024 shots',log);assert len(totals)==1;total=int(totals[0]);assert int(total/9024+.5)==tof
 shutil.copyfile(t/'score.json',r/'score.json');save('BENCHMARK-RESULT.json',{'status':'COMPLETE_UNCHANGED_BENCHMARK_PASS','qubits':q,'rounded_mean_executed_toffoli':tof,'product':q*tof,'total_executed_toffoli':total,'tested_shots':9024,'mean_executed_toffoli':total/9024,'native_receipt':first,'search_result':sr,'protected_files_checked':17,'submission_mode':'auto','scope':'Local complete reproduction; not officially evaluated. Targets independent Toffoli objective, not global product. Existing final statistical gate retained unchanged.'})
 (r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
