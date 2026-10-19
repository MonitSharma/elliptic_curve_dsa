import hashlib,json,os,resource,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;os.chdir(r);old=r.parent/'product-anf-witness-20261019'
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
os.environ.update(ANF_WITNESSES='1',OMP_NUM_THREADS='1',RAYON_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
prep=json.loads((r/'PREPARATION.json').read_text());assert all(sha(r/p)==h==sha(old/p) for p,h in prep['source_files'].items())
assert sha(old/'RESULT.json')==prep['prior_complete_result_sha256'] and sha(old/'evidence.tar.gz')==prep['prior_archive_sha256']
assert (old/'run.exit').read_text().strip()=='0' and '16 passed; 0 failed' in (old/'tests.log').read_text()
archive=json.loads((old/'EVIDENCE-MANIFEST.json').read_text());assert sha(old/'evidence.tar.gz')==archive['sha256']
import tarfile
with tarfile.open(old/'evidence.tar.gz') as a:m=json.load(a.extractfile('SNAPSHOT-MANIFEST.json'))
for name in ['anf.bin','trace.bin','tests.bin']:assert sha(old/name)==m['binary_inputs_outputs_and_executables_retained_locally'][name]['sha256']
inp=r.parent/'product-copy-cache-20261019/copy-cache.ops.bin'
record={'input_sha256':sha(inp),'input_raw_sha3_256':'d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5','binaries':{name:sha(old/name) for name in ['anf.bin','trace.bin','tests.bin']},'source_files':prep['source_files'],'new_input_only':True,'no_nonce_or_gate':True}
(r/'RUN-BINDING.json').write_text(json.dumps(record,indent=2)+'\n')
with (r/'tests.log').open('xb') as f:subprocess.run([str(old/'tests.bin'),'--test-threads=1'],stdout=f,stderr=subprocess.STDOUT,check=True)
with (r/'witness.log').open('xb') as f:subprocess.run(['/usr/bin/time','-v',str(old/'anf.bin'),str(inp),'witness',record['input_raw_sha3_256']],stdout=f,stderr=subprocess.STDOUT,check=True)
src=json.loads((r/'witness.json').read_text());changed=src['input_sha3_256']!=src['output_sha3_256']
if changed:
 with (r/'control.log').open('xb') as f:subprocess.run(['/usr/bin/time','-v',str(old/'trace.bin'),str(inp),'witness.ops.bin','CONTROL.json'],stdout=f,stderr=subprocess.STDOUT,check=True)
(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_WITNESS_ON_NEW_COPY_CACHE_INPUT_COMPLETED','source':src,'changed':changed,'current_wire_witness_sites':sum(x.get('kind')=='exact_current_wire_product' for x in src['sites']),'control':json.loads((r/'CONTROL.json').read_text()) if changed else None,'gate_or_nonce':False,'score':None},indent=2)+'\n')
