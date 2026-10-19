import hashlib,json,os,resource,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;os.chdir(r);runtime=r.parent/'portable-rust-20261019/runtime';compiler=runtime/'compiler/bin/rustc';deps=runtime/'deps'
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
os.environ.update(CLASSICAL_WIDE_CAP='11',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',RAYON_NUM_THREADS='1')
assert json.loads((runtime.parent/'LOCAL-VERIFICATION.json').read_text())['status']=='ARCHIVE_AND_EVERY_COMPILER_DEPENDENCY_HASH_VERIFIED'
input_path=r.parent/'product-classical-closure-20261019/input.ops.bin';input_raw='2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265'
assert hashlib.file_digest(input_path.open('rb'),'sha256').hexdigest()=='17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7'
base=[str(compiler),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','linker=/usr/bin/gcc','-C','link-arg=-fuse-ld=bfd','-L','dependency='+str(deps)]
for name in ['quantum_ecc','sha3','serde_json','zstd']:
    matches=list(deps.glob('lib'+name+'-*.rlib'));assert len(matches)==1,(name,matches)
    base+=['--extern',name+'='+str(matches[0])]
commands=[]
def run(args,log,env=None):
    commands.append({'argv':args,'log':log})
    (r/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    with (r/log).open('xb') as f:subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
run([str(compiler),'--version','--verbose'],'compiler-version.log')
run(base+['--test','refresh_factors.rs','-o','tests.bin'],'build-tests.log')
run(['./tests.bin','--test-threads=1'],'tests.log')
run(base+['refresh_factors.rs','-o','factor.bin'],'build.log')
run(base+['factor_trace.rs','-o','trace.bin'],'build-trace.log')
env=dict(os.environ,CLASSICAL_WIDE_CAP='9')
run(['/usr/bin/time','-v','./factor.bin',str(input_path),'compat9',input_raw],'compat9.log',env)
assert json.loads((r/'compat9.json').read_text())['output_full_sha3_256']==input_raw
assert not (r/'compat9.ops.bin').exists()
run(['/usr/bin/time','-v','./factor.bin',str(input_path),'cap11',input_raw],'cap11.log')
if (r/'cap11.ops.bin').exists():
    run(['/usr/bin/time','-v','./trace.bin',str(input_path),'cap11.ops.bin','CONTROL.json'],'control.log')
result={'status':'LOCAL_EXACT_CAP11_SOURCE_SCREEN_COMPLETED','source':json.loads((r/'cap11.json').read_text()),'compat9_complete_raw_hash_equal':True,'control':json.loads((r/'CONTROL.json').read_text()) if (r/'CONTROL.json').exists() else None,'new_candidate_frozen':False,'statistical_gate_or_nonce_started':False,'score':None}
(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
