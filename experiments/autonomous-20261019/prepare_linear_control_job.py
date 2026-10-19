"""Use the spare server slot for primitive controls while the local scan runs."""
import hashlib,json,shutil
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;source=ws/'product-linear-witness-20261020';r=ws/'product-linear-witness-controls-20261020'
assert not r.exists();r.mkdir()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for p in source.glob('*.rs'):shutil.copy2(p,r/p.name)
runtime=ws/'portable-rust-20261019/runtime';deps=runtime/'deps'
bindings={'/home/hclau/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc':sha(runtime/'compiler/bin/rustc')}
for lib in ['quantum_ecc','sha3','serde_json','zstd']:
 found=list(deps.glob('libsha3-3855b8dab8fa2d83.rlib' if lib=='sha3' else 'lib'+lib+'-*.rlib'));assert len(found)==1
 bindings['/home/hclau/ecdsa_research/product-order-20261019/target/release/deps/'+found[0].name]=sha(found[0])
(r/'BINDING.json').write_text(json.dumps({'source_files':{p.name:sha(p) for p in r.glob('*.rs')},'compiler_and_direct_dependencies':bindings,'scope':'Primitive/exhaustive controls only; no circuit input, nonce, census or benchmark.'},indent=2)+'\n')
(r/'.gitignore').write_text('/*.bin\n')
(r/'run.py').write_text('''import hashlib,json,os,resource,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;os.chdir(r)
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
os.environ.update(OMP_NUM_THREADS='1',RAYON_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',ANF_PAIR_WITNESSES='0',ANF_LINEAR_WITNESSES='0')
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
b=json.loads((r/'BINDING.json').read_text());assert all(sha(r/p)==h for p,h in b['source_files'].items())
assert all(sha(Path(p))==h for p,h in b['compiler_and_direct_dependencies'].items())
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v15.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True));(r/'preflight.json').write_text(json.dumps(profile,indent=2)+'\\n')
compiler=next(p for p in b['compiler_and_direct_dependencies'] if p.endswith('/rustc'));deps=ws/'product-order-20261019/target/release/deps'
args=[compiler,'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','linker=/usr/bin/gcc','-C','link-arg=-fuse-ld=bfd','-L','dependency='+str(deps)]
for lib in ['quantum_ecc','sha3','serde_json','zstd']:
 paths=[p for p in b['compiler_and_direct_dependencies'] if Path(p).name.startswith('lib'+lib+'-')];assert len(paths)==1;args+=['--extern',lib+'='+paths[0]]
with (r/'build-tests.log').open('xb') as f:subprocess.run(args+['--test','anf.rs','-o','tests.bin'],stdout=f,stderr=subprocess.STDOUT,check=True)
with (r/'tests.log').open('xb') as f:subprocess.run(['./tests.bin','--test-threads=1'],stdout=f,stderr=subprocess.STDOUT,check=True)
assert '30 passed; 0 failed' in (r/'tests.log').read_text()
(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_LINEAR_WITNESS_30_PRIMITIVE_CONTROLS_PASS','tests':30,'source_files':b['source_files'],'binary_sha256':sha(r/'tests.bin'),'compiler_and_dependencies':b['compiler_and_direct_dependencies'],'full_source_scan_or_score':False},indent=2)+'\\n')
print('All30 primitive controls PASS; full source analysis still required',flush=True)
''',newline='\n')
(r/'run.sh').write_text('''#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-linear-witness-controls-20261020
trap 'rc=$?; printf "%s\\n" "$rc" > run.exit' EXIT
sha256sum *.py *.rs run.sh BINDING.json > SOURCE.sha256
python3 run.py
''',newline='\n')
(r/'launch.py').write_text('''import subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;assert not (r/'run.pid').exists()
with (r/'nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'run.pid').write_text(str(p.pid)+'\\n');print(p.pid)
''',newline='\n')
print('Prepared one-slot server primitive controls, compiler/dependency/source hashes bound')
