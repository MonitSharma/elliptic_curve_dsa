"""One fixed source-only cache probe on the current official Toffoli minimum.

This is a new parent, not a retry of the old wide95 large-cap experiment.
Nothing here runs a census, selects a nonce, or modifies a submission tree.
"""
from pathlib import Path
import hashlib,json,os,resource,subprocess,time

HERE=Path(__file__).resolve().parent
ROOT=Path('/home/hclau/ecdsa_research')
TOOLS=ROOT/'product-exact-20261015'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (HERE/'DECLARATION.json').exists(), 'Independent case runs once only'
source=ROOT/'wide15-record-20261016/evidence/final-ops.bin'
expected='1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77'
assert sha(source)==expected
optimizer=TOOLS/'target-scratch/release/product_paired_diagnostic'
assert sha(optimizer)=='e25ce2b8c48438f909bd823ac4e31d17fe4877b5ef8510fad79d9715bcc8035d'
old=json.loads((TOOLS/'wide-largecaps-20261016/DECLARATION.json').read_text())
for name,digest in old['optimizer_source_files_sha256'].items():
    assert sha(TOOLS/'scratch-tool'/name)==digest,name
preflight=json.loads(subprocess.check_output(['python3',str(ROOT/'server-preflight.py')]))
(HERE/'launch-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
assert preflight['hostname']=='LHC-104-070'
assert preflight['memory']['MemAvailable_bytes']>=228*2**30
plan={
 'parent':'official753721-Q1468-source-b5adb653',
 'input_stream':str(source),'input_stream_sha256':expected,
 'optimizer_executable':str(optimizer),'optimizer_executable_sha256':sha(optimizer),
 'optimizer_source_files_sha256':old['optimizer_source_files_sha256'],
 'fixed_case':dict(family='retained',atom_cap=4096,pair_cap=256,product_cap=1000000,
                   rank='density',split=True,extra_zero_slots_offered=64,additional_stages=1),
 'analysis_threads':1,'address_limit_GiB':64,'generation_wall_limit_seconds':2700,
 'scope':'Source-only exact optimization on the current best source. No samples or packet data. Extra width acceptable for the independent Toffoli target.',
 'independence':'Different frozen parent from wide95. Old cap4096 24GiB resource failure remains terminal and is not replaced. No changed-limit retry in this declaration.',
 'prospective_native_gate':'Only src/point_add; full source and patch frozen, protected files unchanged, normal builder exact byte identity, universal new-stage semantics/clean donors and independent full q/b/phase/MR anchored replay before any fresh census.',
 'prospective_fresh_gate':dict(label='official753721-plus-retained4096-one-stage-independent-20261016-v1',
                              first_batch=0,batches_per_source=32768,shots_per_batch=64,
                              parent_stream_sha256=expected,
                              runner=str(ROOT/'simd-census-v2-20261016/bin/simd_census_v2'),
                              runner_sha256='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66',
                              no_resampling_or_subset=True,
                              requirements='all rows, failed batches <= same-input parent and <=18/9024, dirty0; actual executed savings must beat current public T with margin'),
 'nonce_search_authorized_by_this_probe':False,'scored_result':None,
}
(HERE/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
output=HERE/'candidate.bin'
env=os.environ.copy()
env.update(RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
           EXACT_MODE='cache-retained',CACHE_ATOM_CAP='4096',ANF_PAIR_CAP='256',
           CACHE_PRODUCT_CAP='1000000',CACHE_RANK='density',CACHE_SPLIT='1',CACHE_EXTRA_QUBITS='64')
def limits():
    resource.setrlimit(resource.RLIMIT_AS,(64*2**30,64*2**30))
start=time.monotonic()
with (HERE/'generation.log').open('wb') as out:
    proc=subprocess.Popen(['timeout','--signal=TERM','--kill-after=30','2700','/usr/bin/time','-v',str(optimizer),str(source),str(output)],
                          stdout=out,stderr=subprocess.STDOUT,env=env,preexec_fn=limits)
    (HERE/'generator.pid').write_text(str(proc.pid)+'\n')
    stopped_for_memory=False
    while proc.poll() is None:
        available=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))*1024
        if available<110*2**30:
            # timeout forwards TERM to its own child process group.
            proc.terminate();stopped_for_memory=True
            try:proc.wait(timeout=35)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
            break
        time.sleep(10)
result=dict(status='GENERATED_SOURCE_ONLY' if proc.returncode==0 else 'GENERATION_RESOURCE_OR_TOOL_FAILURE_PRESERVED',
            returncode=proc.returncode,seconds=time.monotonic()-start,stopped_for_memory=stopped_for_memory,
            declaration_sha256=sha(HERE/'DECLARATION.json'),input_before_after_sha256=sha(source),score=None)
assert result['input_before_after_sha256']==expected
if proc.returncode==0:
    result['candidate_sha256']=sha(output)
    with (HERE/'resources.jsonl').open('w') as out:
        subprocess.run(['python3',str(TOOLS/'stream_resources.py'),str(output)],stdout=out,check=True)
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
