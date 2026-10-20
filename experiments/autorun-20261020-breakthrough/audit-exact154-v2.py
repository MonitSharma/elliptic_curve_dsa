"""Correct diagnostic zstd-frame binding without altering or regenerating source."""
import hashlib,json,re,subprocess,time
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-public140-exact154-20261020';t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def records(path):
 h=hashlib.sha256();size=0;tail=b''
 with path.open('rb',buffering=0)as raw:
  header=raw.read(16);assert header[:8]==b'QECCOPSZ';count=int.from_bytes(header[8:],'little');p=subprocess.Popen(['zstd','-dc'],stdin=raw,stdout=subprocess.PIPE)
  while chunk:=p.stdout.read(1<<20):h.update(chunk);size+=len(chunk);tail=(tail+chunk)[-96*56:]
  assert p.wait()==0 and size==count*56
 return {'operations':count,'record_sha256':h.hexdigest(),'tail_sha256':hashlib.sha256(tail).hexdigest()}
try:
 while not(r/'run.exit').exists():time.sleep(2)
 assert(r/'generate.exit').read_text().strip()=='0'
 if(r/'run.exit').read_text().strip()!='0':assert 'AssertionError: Native output must reproduce exact prover stream including nonce0 tail'in(r/'supervisor.log').read_text()
 f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());counts=[]
 for i in range(16):
  assert(r/('tests-'+str(i)+'.exit')).read_text().strip()=='0';a=re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/('tests-'+str(i)+'.log')).read_text());assert len(a)==1;counts.append(int(a[0]))
 assert counts==[1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]
 proof=ws/'breakthrough-public140-cache-20261020/extra16.ops.bin';assert sha(proof)==f['proof_rewritten_stream_sha256'];native=records(t/'ops.bin');reference=records(proof);assert native==reference and native['operations']==10553247
 log=(r/'generate.log').read_text();matches=re.findall(r'EXACT154_CACHE leases=(\d+) operations=(\d+) qubits=(\d+) bits=(\d+)',log);assert len(matches)==1;leases,ops,q,bits=map(int,matches[0]);assert leases==154 and ops+96==native['operations']
 result={'status':'FINISHED_NONCE0_NATIVE_RECORDS_REPRODUCE_EXACT_PROVER_NOT_YET_GATED','native_tests':sum(counts),'native_test_counts':counts,'stream_path':str(t/'ops.bin'),'native_stream_sha256':sha(t/'ops.bin'),'prover_framed_sha256':sha(proof),'framed_hashes_equal':sha(t/'ops.bin')==sha(proof),'canonical_records_equal':True,'records':native,'qubits':q,'classical_bits':bits,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'native_binary_sha256':sha(t/'target/release/build_circuit'),'correction':'Initial research runner incorrectly required framed equality: diagnostic io writer sets zstd window_log27; protected writer uses default. Original failure retained. Same native source, build/tests/generation; no rerun. Every uncompressed operation record matches.','scope':'Finished independent exact154 candidate; no final gate or nonce search yet. Compare fresh final gate against exact current official4045 parent.'};(r/'FINISHED-RESULT-v2.json').write_text(json.dumps(result,indent=2)+'\n');(r/'audit-v2.exit').write_text('0\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'audit-v2.exit').write_text('1\n');raise
