import hashlib,json,os,resource,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;os.chdir(r);ws=r.parent;runtime=ws/'portable-rust-20261019/runtime';deps=runtime/'deps'
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3));os.environ.update(ANF_PAIR_WITNESSES='0',ANF_WITNESSES='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',RAYON_NUM_THREADS='1')
old=ws/'product-copy-cache-witness-20261020';assert (old/'run.exit').read_text().strip()=='0';baseline=json.loads((old/'RESULT.json').read_text())['source']
assert json.loads((runtime.parent/'LOCAL-VERIFICATION.json').read_text())['status']=='ARCHIVE_AND_EVERY_COMPILER_DEPENDENCY_HASH_VERIFIED'
inp=ws/'product-copy-cache-20261019/copy-cache.ops.bin';assert hashlib.file_digest(inp.open('rb'),'sha256').hexdigest()=='53bb99238f013b7308b88e26d063d6d9ec3b364d1f0e2b2501b6abe368a75fb1'
base=[str(runtime/'compiler/bin/rustc'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','linker=/usr/bin/gcc','-C','link-arg=-fuse-ld=bfd','-L','dependency='+str(deps)]
for name in ['quantum_ecc','sha3','serde_json','zstd']:
    matches=list(deps.glob('libsha3-3855b8dab8fa2d83.rlib' if name=='sha3' else 'lib'+name+'-*.rlib'));assert len(matches)==1;base+=['--extern',name+'='+str(matches[0])]
commands=[]
def run(args,name,env=None):
    commands.append({'argv':args,'log':name,'pair_witness_mode':(env or os.environ).get('ANF_PAIR_WITNESSES')});(r/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    with (r/name).open('xb') as f:subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
run(base+['--test','anf.rs','-o','tests.bin'],'build-tests.log');run(['./tests.bin','--test-threads=1'],'tests.log')
run(base+['anf.rs','-o','anf.bin'],'build.log');run(base+['factor_trace.rs','-o','trace.bin'],'build-trace.log')
raw='d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5'
run(['/usr/bin/time','-v','./anf.bin',str(inp),'disabled',raw],'disabled.log',dict(os.environ,ANF_PAIR_WITNESSES='0'))
disabled=json.loads((r/'disabled.json').read_text());assert disabled=={**baseline,'input':str(inp)},'Disabled interpreter must reproduce the complete previous report and stream hash'
run(['/usr/bin/time','-v','./anf.bin',str(inp),'witness',raw],'witness.log',dict(os.environ,ANF_PAIR_WITNESSES='1'))
result=json.loads((r/'witness.json').read_text());changed=result['input_sha3_256']!=result['output_sha3_256']
if changed:run(['/usr/bin/time','-v','./trace.bin',str(inp),'witness.ops.bin','CONTROL.json'],'control.log')
(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_TWO_WIRE_XOR_PRODUCT_SOURCE_SCREEN_COMPLETED','source':result,'disabled_complete_report_and_stream_identical':True,'pair_witness_sites':sum(x.get('kind')=='exact_two_wire_xor_product' for x in result['sites']),'control':json.loads((r/'CONTROL.json').read_text()) if changed else None,'native_candidate_frozen':False,'gate_or_nonce':False,'score':None},indent=2)+'\n')
