import hashlib,json,os,resource,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;os.chdir(r);runtime=r.parent/'portable-rust-20261019/runtime';deps=runtime/'deps'
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3));os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',RAYON_NUM_THREADS='1')
assert json.loads((runtime.parent/'LOCAL-VERIFICATION.json').read_text())['status']=='ARCHIVE_AND_EVERY_COMPILER_DEPENDENCY_HASH_VERIFIED'
inp=r.parent/'product-classical-closure-20261019/input.ops.bin';assert hashlib.file_digest(inp.open('rb'),'sha256').hexdigest()=='17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7'
base=[str(runtime/'compiler/bin/rustc'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','linker=/usr/bin/gcc','-C','link-arg=-fuse-ld=bfd','-L','dependency='+str(deps)]
for name in ['quantum_ecc','sha3','serde_json','zstd']:
    matches=list(deps.glob('libsha3-3855b8dab8fa2d83.rlib' if name=='sha3' else 'lib'+name+'-*.rlib'));assert len(matches)==1;base+=['--extern',name+'='+str(matches[0])]
commands=[]
def run(args,name):
    commands.append({'argv':args,'log':name});(r/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    with (r/name).open('xb') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
run(base+['--test','anf.rs','-o','tests.bin'],'build-tests.log');run(['./tests.bin','--test-threads=1'],'tests.log')
run(base+['anf.rs','-o','anf.bin'],'build.log');run(base+['factor_trace.rs','-o','trace.bin'],'build-trace.log')
run(['/usr/bin/time','-v','./anf.bin',str(inp),'anf256','2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265'],'scan.log')
result=json.loads((r/'anf256.json').read_text());changed=result['input_sha3_256']!=result['output_sha3_256']
if changed:run(['/usr/bin/time','-v','./trace.bin',str(inp),'anf256.ops.bin','CONTROL.json'],'control.log')
(r/'RESULT.json').write_text(json.dumps({'status':'FIXED_ANF256_DEGREE12_SOURCE_SCREEN_COMPLETED','source':result,'control':json.loads((r/'CONTROL.json').read_text()) if changed else None,'new_native_candidate':False,'gate_or_nonce':False,'score':None},indent=2)+'\n')
