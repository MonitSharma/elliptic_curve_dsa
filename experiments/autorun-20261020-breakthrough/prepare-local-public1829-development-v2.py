from pathlib import Path
import hashlib,json,shutil
from datetime import datetime,timezone
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-public1829-local-development-20261020';r=ex/'breakthrough-public1829-local-development-v2-20261020';r.mkdir(exist_ok=False);shutil.copytree(old/'local-tool',r/'local-tool');t=r/'local-tool';sha=lambda b:hashlib.sha256(b).hexdigest()
p=t/'simd8count.c';s=p.read_text();start=s.index('typedef __m512i V;');end=s.index('/* q and bit rows',start);s=s[:start]+'''typedef struct { __m256i lo,hi; } V;
static inline V ld(const uint64_t *p,size_t i){return(V){_mm256_loadu_si256((const __m256i *)(p+8*i)),_mm256_loadu_si256((const __m256i *)(p+8*i+4))};}
static inline void st(uint64_t *p,size_t i,V x){_mm256_storeu_si256((__m256i *)(p+8*i),x.lo);_mm256_storeu_si256((__m256i *)(p+8*i+4),x.hi);}
static inline V vand(V a,V b){return(V){_mm256_and_si256(a.lo,b.lo),_mm256_and_si256(a.hi,b.hi)};}
static inline V vxor(V a,V b){return(V){_mm256_xor_si256(a.lo,b.lo),_mm256_xor_si256(a.hi,b.hi)};}
static inline V vor(V a,V b){return(V){_mm256_or_si256(a.lo,b.lo),_mm256_or_si256(a.hi,b.hi)};}
static inline V vandnot(V a,V b){return(V){_mm256_andnot_si256(a.lo,b.lo),_mm256_andnot_si256(a.hi,b.hi)};}
static inline V vones(void){return(V){_mm256_set1_epi64x(-1),_mm256_set1_epi64x(-1)};}
#define AND(a,b) vand(a,b)
#define XOR(a,b) vxor(a,b)
#define OR(a,b) vor(a,b)
#define ANDNOT(a,b) vandnot(a,b)
''' +s[end:];s=s.replace('_mm512_set1_epi64(-1)','vones()');p.write_text(s)
p=t/'build.rs';p.write_text(p.read_text().replace('-march=skylake-avx512','-march=haswell'))
p=t/'src/main.rs';s=p.read_text().replace('is_x86_feature_detected!("avx512f")','is_x86_feature_detected!("avx2")');s+='\n'+(a/'local-avx2-observer-tests.rs').read_text();p.write_text(s)
(t/'src/fast_curve_c.rs').write_text('''// Portable verification backend: exact protected reference, no external library.
struct FastCurveC;
impl FastCurveC{fn new(_window:usize)->Self{Self}fn points_with_sums(&self,scalars:&[U256])->Vec<((U256,U256),(U256,U256),(U256,U256))>{assert!(scalars.len()%2==0);let c=secp256k1();scalars.chunks_exact(2).map(|pair|{let a=c.mul(c.gx,c.gy,pair[0]);let b=c.mul(c.gx,c.gy,pair[1]);let e=c.add(a.0,a.1,b.0,b.1);(a,b,e)}).collect()}}
''')
(t/'src/shake_rng.rs').write_text('''// Exact protected scalar SHAKE readers, interleaved into eight independent rows.
fn shake_backend(){}
fn rng8(_label:&str,batches:&[Batch],words:usize,out:&mut[u64]){assert_eq!(batches.len(),8);assert_eq!(out.len(),words*8);for j in 0..8{let mut reader=batches[j].xof.clone();let mut bytes=vec![0u8;words*8];XofReader::read(&mut reader,&mut bytes);for(i,v)in bytes.chunks_exact(8).enumerate(){out[i*8+j]=u64::from_le_bytes(v.try_into().unwrap());}}}
''')
for n in ['.gitignore','.gitattributes','diagnostic.py']:shutil.copyfile(old/n,r/n)
plan=json.loads((old/'PLAN.json').read_bytes());plan.update(declared_at_utc=datetime.now(timezone.utc).isoformat(),label='public1829-workspace-cache-local-avx2-development-20261020-v1',scope=plan['scope']+' Portable AVX2 kernel with explicit opcode/guard/RNG/phase/T exhaustive-basis control; all field arithmetic and SHAKE now protected Rust routines, no server shared libraries. Prepared AVX512 predecessor never launched or consumed inputs.');(r/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f.update(tool_source_files={n:sha((t/n).read_bytes())for n in f['tool_source_files']},plan_sha256=sha((r/'PLAN.json').read_bytes()),scope=plan['scope'],previous_prepared_tool_freeze_sha256=sha((old/'SOURCE-FREEZE.json').read_bytes()));(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
for n in ['run-local.sh','launch-local.sh']:
 s=(old/n).read_text().replace(old.name,r.name)
 if n=='run-local.sh':
  needle='/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build';pos=s.index(needle);s=s[:pos]+'''/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path local-tool/Cargo.toml -- --nocapture > tests.log 2>&1
grep -q 'avx2_all_operations_captured_guards_rng_and_toffoli_match_full_protected_simulator ... ok' tests.log
'''+s[pos:]
 (r/n).write_bytes(s.encode())
(r/'PLAN.md').write_text((old/'PLAN.md').read_text()+'''\nPortablev2 changes ONLY verification tools: localCPU has AVX2, not AVX512;
two four-word halves implement the same eight-word ABI, kernel per-op code
unchanged. New 1024basis combinations x3RNG patterns compare every quantum/
classical wire, phase, RNG consumption and executedT to protected Simulator.
Protected Rust curve andSHAKE replace unavailable server shared libraries.
Original AVX512 tool is preserved unlaunched, not a failed circuit/gate.
''');(old/'NOT-LAUNCHED.json').write_text(json.dumps({'status':'PREPARED_NOT_LAUNCHED_HOST_LACKS_AVX512_AND_SERVER_SHARED_LIBRARIES','input_batches_executed':0,'scope':'No circuit, resource or statistical verdict. Separate portablev2 declared before any inputs.'},indent=2)+'\n');print(r.name)
