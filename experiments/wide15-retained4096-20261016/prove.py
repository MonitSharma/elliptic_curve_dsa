"""Expose five fresh zero ancillas through an exact identity-only proof adapter.

Actual input/candidate and the trusted checker remain unchanged. The checker
still proves zeros, functions, lease boundaries, uncompute and every output Op.
"""
from pathlib import Path
import hashlib,json,os,re,resource,struct,subprocess,time
from ops_io import load,save
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;TOOLS=ROOT/'product-exact-20261015'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (HERE/'PROOF_PLAN.json').exists()
resource.setrlimit(resource.RLIMIT_AS,(48*2**30,48*2**30))
preflight=json.loads(subprocess.check_output(['python3',str(ROOT/'server-preflight.py')]))
(HERE/'proof-preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
assert preflight['memory']['MemAvailable_bytes']>=180*2**30
original=ROOT/'wide15-record-20261016/evidence/final-ops.bin';candidate=HERE/'candidate.bin'
assert sha(original)=='1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77'
assert sha(candidate)=='1d4a9e1ed9d0a81bd16b922cfa7b2d2570792d1f91215de7f3300c9f795860b1'
checker=TOOLS/'target-cache-certificate-v2/release/product_paired_diagnostic'
assert sha(checker)=='2e9f5ee6ed4ea1fa5b625f38298a71e05ce885778db7aed1064b23d2ee657091'
a=load(original);b=load(candidate);none=2**64-1
assert len(a)//56==10522755 and len(b)//56==10523283
oldmax=newmax=-1;ports=[]
for row in struct.iter_unpack('<7Q',a):
    for q in row[1:4]:
        if q!=none:oldmax=max(oldmax,q)
    if row[0] in [1,2]:ports.append(row)
for row in struct.iter_unpack('<7Q',b):
    for q in row[1:4]:
        if q!=none:newmax=max(newmax,q)
assert (oldmax,newmax)==(1467,1472)
# Fresh IDs are absent from EVERY original operation, hence all register ports.
# Simulator's non-registered scratch starts0; XX preserves it with no MR/phase.
fresh=list(range(1468,1473));prefix=b''
for q in fresh:
    op=struct.pack('<7Q',6,none,none,q,none,none,none);prefix+=op+op
for bit in [0,1]:assert (bit^1)^1==bit
assert len(prefix)==10*56 and a[-96*56:]==b[-96*56:]
save(HERE/'proof-left.bin',prefix+a);save(HERE/'proof-right.bin',prefix+b)
assert load(HERE/'proof-left.bin')==prefix+a and load(HERE/'proof-right.bin')==prefix+b
log=(HERE/'generation.log').read_text();count=0;leases=[];out=[]
for line in log.splitlines():
    if line.startswith('LAZY_WINDOW '):
        old=line
        fields={k:int(re.search(r'\b'+k+r'=(\d+)',line)[1]) for k in ['donor','start','end']}
        uses=list(map(int,re.search(r'uses=\[([^]]+)\]',line)[1].split(',')))
        assert fields['end']<=len(a)//56-96
        assert fields['start']<=uses[0] and uses[-1]<fields['end']
        for key in ['start','end']:
            line=re.sub(r'\b'+key+r'=\d+',key+'='+str(fields[key]+10),line)
        line=re.sub(r'uses=\[[^]]+\]','uses='+str([i+10 for i in uses]),line)
        fields['uses']=uses;leases.append(fields);count+=1
    out.append(line)
assert count==22 and set(fresh)&set(x['donor'] for x in leases)
(HERE/'proof-leases.log').write_text('\n'.join(out)+'\n')
plan=dict(status='IDENTITY_ONLY_PROOF_ADAPTER_FROZEN',actual_source_sha256=sha(original),actual_candidate_sha256=sha(candidate),
          proof_left_sha256=sha(HERE/'proof-left.bin'),proof_right_sha256=sha(HERE/'proof-right.bin'),
          original_log_sha256=sha(HERE/'generation.log'),translated_log_sha256=sha(HERE/'proof-leases.log'),
          checker_sha256=sha(checker),fresh_ids=fresh,prefix_ops=10,all_leases_shifted=22,
          semantic_premises='Fresh IDs absent every original Op and ABI, start0 as non-input scratch; two unconditional X per fresh wire are identity with no MR/phase; exact same prefix and translation on both sides. No candidate/source changes.',
          atom_cap=4096,pair_cap=256,product_cap=1000000,threads=1,address_limit_GiB=48,wall_limit_seconds=1200,
          files_sha256={n:sha(HERE/n) for n in ['prove.py','ops_io.py','proof.sh']},score=None)
(HERE/'PROOF_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
del a,b
env=os.environ.copy();env.update(CACHE_ATOM_CAP='4096',ANF_PAIR_CAP='256',CACHE_PRODUCT_CAP='1000000',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
start=time.monotonic()
with (HERE/'universal.log').open('wb') as out:
    p=subprocess.Popen(['timeout','--signal=TERM','--kill-after=30','1200','/usr/bin/time','-v',str(checker),str(HERE/'proof-left.bin'),str(HERE/'proof-right.bin'),str(HERE/'proof-leases.log'),'retained'],env=env,stdout=out,stderr=subprocess.STDOUT)
    (HERE/'universal.pid').write_text(str(p.pid)+'\n')
    while p.poll() is None:
        available=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
        if available<110*2**30:
            p.terminate()
            try:p.wait(timeout=35)
            except subprocess.TimeoutExpired:p.kill();p.wait()
            break
        time.sleep(10)
result=dict(status='UNIVERSAL_PADDED_STAGE_PASS' if p.returncode==0 else 'UNIVERSAL_FAILURE_PRESERVED',returncode=p.returncode,seconds=time.monotonic()-start,
            plan_sha256=sha(HERE/'PROOF_PLAN.json'),log_sha256=sha(HERE/'universal.log'),actual_candidate_unchanged_sha256=sha(candidate),no_native_or_census_claim=True)
assert result['actual_candidate_unchanged_sha256']==plan['actual_candidate_sha256']
(HERE/'PROOF_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
