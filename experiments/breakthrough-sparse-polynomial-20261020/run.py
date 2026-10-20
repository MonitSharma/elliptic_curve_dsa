import json,os,subprocess,time,hashlib
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';os.chdir(r);env=os.environ.copy();env.update(CARGO_BUILD_JOBS='2',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',RAYON_NUM_THREADS='1')
def run(args,log,cwd=r,timeout=1800):
 with(r/log).open('xb')as out:
  p=subprocess.Popen(['timeout',str(timeout)]+args,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(log+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 if rc: (r/'run.exit').write_text(str(rc)+'\n');raise SystemExit(rc)
run(['python3','prepare.py'],'prepare.log')
run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','sparse_polynomial::tests','--','--nocapture','--test-threads=1'],'tests.log',t)
f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());assert sha(Path(f['input_stream']))==f['input_stream_sha256'];env.update(TRUTH_AUDIT_INPUT=f['input_stream'],TRUTH_AUDIT_OUTPUT=str(r/'optimized'));start=time.time()
run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','sparse_polynomial::stream_audit','--','--ignored','--nocapture','--test-threads=1'],'audit.log',t)
(r/'AUDIT-RESULT.json').write_text(json.dumps({'exit':0,'seconds':time.time()-start,'input_stream_sha256':f['input_stream_sha256'],'stages':[l for l in(r/'audit.log').read_text().splitlines()if l.startswith('POLY_STAGE ')],'streams':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size}for p in r.glob('optimized-*.ops.bin')},'scope':'Exact research optimizer on frozen generic stream. No final gate, full benchmark, nonce or resource record; depth weights diagnostic only.'},indent=2)+'\n');(r/'run.exit').write_text('0\n')
