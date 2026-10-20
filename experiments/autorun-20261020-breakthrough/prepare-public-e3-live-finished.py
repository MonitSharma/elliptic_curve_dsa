from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-public-e3-live-finished-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('candidate/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'PLAN.md').write_text('''# Frozen complete public e3 cache plus exact live-product parities

Fixed parent is the completed cache53 source6b39ecd1, fullstream93c783. Use the
first fixed cache53 output of the separately frozen512-term implication/live
parity tool, six native controls before scanning. No gate has been declared for
this source family. Preserve all originalpublic and cache53 constructor/source
bindings byte-for-byte, renaming only the final entrypoint. Bind its fullnonce0
output, remove exactly96 checkedzero identity ops, apply the proved constant/
affine parity replacement rows, bind every resulting prefix record to the
independently emitted tool output and append newnonce0. No quantum wire, RNG
draw, classical operation or metadata changes in this added pass.

The new runtime has an exhaustive basis/phase/guard/constant/fault/RNG control,
and reruns the unchanged guardedcache native control. The17 inherited passing
parent controls and two exact-reproduced parent failures are disclosed; no claim
all original tests pass. Nine cacheproof controls and six compiler controls are
separate evidence. Full fresh comparison must match cache53 bit-for-bit in all
values/ancillas/phase flags, then one own final32768x64 gate vs exactpublice3.
Qualified ascendingnonce/unchangedbenchmark/local review/autosubmit follow only
on finalgatePASS and a complete current-record resource improvement.
''')
(r/'runtime.rs').write_text(r'''use crate::circuit::{Op,OperationType as K,QubitId,analyze_ops};use sha3::{Digest,Sha3_256};
pub(super)const IDENTITY_NONCE:u64=0;
const EDITS:&[(usize,bool,&[u64])]=&[__EDITS__];
fn replace(ops:Vec<Op>,edits:&[(usize,bool,&[u64])])->Vec<Op>{let mut next=0;let mut out=Vec::with_capacity(ops.len());for(i,o)in ops.into_iter().enumerate(){if next<edits.len()&&edits[next].0==i{let(_,one,controls)=edits[next];next+=1;assert!(matches!(o.kind,K::CCX|K::CCZ));assert!(controls.windows(2).all(|w|w[0]<w[1]));if one{let mut x=o;x.kind=if o.kind==K::CCX{K::X}else{K::Z};x.q_control1=QubitId(u64::MAX);x.q_control2=QubitId(u64::MAX);x.validate();out.push(x);}for &w in controls{let mut x=o;x.q_control2=QubitId(u64::MAX);if o.kind==K::CCZ&&w==o.q_target.0{x.kind=K::Z;x.q_control1=QubitId(u64::MAX);}else{assert_ne!(w,o.q_target.0);x.kind=if o.kind==K::CCX{K::CX}else{K::CZ};x.q_control1=QubitId(w);}x.validate();out.push(x);}}else{out.push(o);}}assert_eq!(next,edits.len());out}
fn bind(ops:&[Op],n:usize,want:&str){assert_eq!(ops.len(),n);let mut h=Sha3_256::new();for o in ops{for v in[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(v.to_le_bytes());}}assert_eq!(format!("{:x}",h.finalize()),want,"Complete exact live-parity input/output binding");}
pub(super)fn run(mut ops:Vec<Op>)->Vec<Op>{bind(&ops,__INPUT_COUNT__,"__INPUT_HASH__");let end=ops.len()-96;for o in &ops[end..]{assert_eq!(o.kind,K::X);assert_eq!(o.q_target.0,0);}ops.truncate(end);let mut ops=replace(ops,EDITS);bind(&ops,__OUTPUT_PREFIX_COUNT__,"__OUTPUT_PREFIX_HASH__");let(nq,nb,_,_)=analyze_ops(ops.iter());assert!(nq<=1234);eprintln!("PUBLIC_E3_LIVE parities={} ops={} nq={} nb={} diagnostic_only=1",EDITS.len(),ops.len(),nq,nb);assert!(IDENTITY_NONCE<(1u64<<48));for bit in 0..48{let mut o=Op::empty();o.kind=K::X;o.q_target=QubitId((IDENTITY_NONCE>>bit)&1);o.validate();ops.extend([o,o]);}ops}
#[cfg(test)]mod tests{
use super::*;use crate::circuit::BitId;use crate::sim::Simulator;use sha3::digest::XofReader;
struct Fixed{v:u8,reads:usize}impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){self.reads+=out.len();out.fill(self.v);}}
fn op(k:K,c2:u64,c1:u64,t:u64,ct:u64,cc:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control2=QubitId(c2);o.q_control1=QubitId(c1);o.q_target=QubitId(t);o.c_target=BitId(ct);o.c_condition=BitId(cc);o.validate();o}
#[test]fn exact_runtime_parities_preserve_full_basis_phase_mutating_guards_rng_and_detect_faults(){let n=u64::MAX;let mut phase_faults=0;let mut value_faults=0;for guard in[false,true]{for one in[false,true]{let mut ops=vec![op(K::CCX,0,1,4,n,n),op(K::CX,n,2,4,n,n)];if one{ops.push(op(K::X,n,n,4,n,n));}if guard{ops.push(op(K::PushCondition,n,n,n,n,0));ops.push(op(K::BitInvert,n,n,n,0,n));}let i=ops.len();ops.push(op(K::CCX,0,1,3,n,1));let j=ops.len();ops.push(op(K::CCZ,0,1,3,n,1));if guard{ops.push(op(K::PopCondition,n,n,n,n,n));}ops.extend([op(K::Hmr,n,n,4,2,n),op(K::R,n,n,3,n,2)]);let out=replace(ops.clone(),&[(i,one,&[2,4]),(j,one,&[2,4])]);let badp:Vec<_>=out.iter().filter(|o|o.kind!=K::CZ).copied().collect();let mut badv=out.clone();let at=badv.iter().position(|o|o.kind==K::CX&&o.q_target.0==3).unwrap();badv.remove(at);for word in[0u8,255,0xa5,0x5a]{let mut ra=Fixed{v:word,reads:0};let mut rb=Fixed{v:word,reads:0};let mut rp=Fixed{v:word,reads:0};let mut rv=Fixed{v:word,reads:0};let mut a=Simulator::new(5,3,&mut ra);let mut b=Simulator::new(5,3,&mut rb);let mut p=Simulator::new(5,3,&mut rp);let mut v=Simulator::new(5,3,&mut rv);for lane in 0..64{for q in 0..4{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}for c in 0..2{a.bits[c]|=((lane>>(c+4)&1)as u64)<<lane;}}for s in[&mut b,&mut p,&mut v]{s.qubits.clone_from(&a.qubits);s.bits.clone_from(&a.bits);}a.apply_iter(ops.iter());b.apply_iter(out.iter());p.apply_iter(badp.iter());v.apply_iter(badv.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits);assert_eq!(a.phase,b.phase);phase_faults+=u64::from(a.phase!=p.phase);value_faults+=u64::from(a.qubits!=v.qubits||a.phase!=v.phase);drop(a);drop(b);assert_eq!(ra.reads,rb.reads);}}}assert!(phase_faults>0&&value_faults>0);}
}
''')
(r/'run.py').write_text('''import hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-public-e3-cache-finished-v2-20261020';proof=ws/'breakthrough-live-products-absorption-v2-20261020';t=r/'candidate';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
def prefixhash(path):
 h=hashlib.sha3_256();pos=0
 with path.open('rb',buffering=0)as raw:
  header=raw.read(16);assert header[:8]==b'QECCOPSZ';n=int.from_bytes(header[8:],'little');stop=(n-96)*56;p=subprocess.Popen(['zstd','-dc'],stdin=raw,stdout=subprocess.PIPE)
  while block:=p.stdout.read(1<<20):
   if pos<stop:h.update(block[:min(len(block),stop-pos)])
   pos+=len(block)
  assert p.wait()==0 and pos==n*56
 return n-96,h.hexdigest()
try:
 start=time.time()
 while not(proof/'scan-cache53.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(proof/'scan-cache53.exit').read_text().strip()=='0'and(old/'resumed.exit').read_text().strip()=='0';pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());f=json.loads((old/'SOURCE-FREEZE.json').read_text());a=json.loads((old/'RESULT.json').read_text());p=json.loads((proof/'cache53.json').read_text());assert all(sha(proof/'tool'/path)==h for path,h in pf['tool_source_files'].items());assert 'test result: ok. 6 passed; 0 failed;'in(proof/'tests.log').read_text();assert all(sha(old/'candidate'/path)==h for path,h in{**f['source_files'],**f['protected_files']}.items());assert sha(old/'candidate/ops.bin')==pf['inputs']['cache53']['sha256']==a['stream_sha256'];assert p['input_records_sha3']==a['records_sha3']and p['hits'];assert all(x['index']<p['input_count']-96 for x in p['hits']);count,outhash=prefixhash(proof/'cache53.ops.bin');assert count==p['output_count']-96;assert not t.exists();subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
 for path in f['source_files']:dest=t/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/'candidate'/path,dest)
 path=t/'src/point_add/mod.rs';body=path.read_bytes();needle=b'pub fn build()->Vec<Op>{public_e3_cache::run(public_e3_parent_build())}';assert body.count(needle)==1;body=body.replace(needle,b'fn public_e3_cache_parent_build()->Vec<Op>{public_e3_cache::run(public_e3_parent_build())}');body+=b'\\nmod public_e3_live;\\npub fn build()->Vec<Op>{public_e3_live::run(public_e3_cache_parent_build())}\\n';path.write_bytes(body)
 edits=','.join('('+str(x['index'])+','+str(x['one']).lower()+',&['+','.join(map(str,x['controls']))+'])'for x in p['hits']);runtime=(r/'runtime.rs').read_text().replace('__EDITS__',edits).replace('__INPUT_COUNT__',str(p['input_count'])).replace('__INPUT_HASH__',p['input_records_sha3']).replace('__OUTPUT_PREFIX_COUNT__',str(count)).replace('__OUTPUT_PREFIX_HASH__',outhash);(t/'src/point_add/public_e3_live.rs').write_text(runtime);assert all(sha(t/path)==h for path,h in f['protected_files'].items());assert all(sha(t/path)==h for path,h in f['source_files'].items()if path!='src/point_add/mod.rs');subprocess.run(['cp','-a','--reflink=auto',str(old/'candidate/target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));freeze={'base':f['base'],'source_files':{path.relative_to(t).as_posix():sha(path)for path in(t/'src/point_add').rglob('*')if path.is_file()},'protected_files':f['protected_files'],'identity_nonce':0,'parent_cache53_freeze_sha256':sha(old/'SOURCE-FREEZE.json'),'inherited_parent_test_baseline_audit_sha256':sha(old/'TEST-BASELINE-AUDIT.json'),'proof_source_freeze_sha256':sha(proof/'SOURCE-FREEZE.json'),'proof_rows_sha256':sha(proof/'cache53.json'),'cache_leases':53,'live_parity_hits':len(p['hits']),'input_full_count':p['input_count'],'input_full_records_sha3':p['input_records_sha3'],'output_prefix_count':count,'output_prefix_records_sha3':outhash,'scope':'Complete publice3 constructor/cache53 preserved with fullbindings, exact original-op globalBoolean liveparity rewrites, no added quantum wires or measurement/RNG/classical changes in this addedpass; nonce0; pending finalgate/nonce/unchangedbenchmark.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\\n');env=dict(os.environ,PEBBLE_HARD_CAP='1234');counts=[]
 for i,flt in enumerate(['public_e3_live::tests','public_e3_cache::cache_tests']):
  name='tests-'+str(i);run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',flt,'--','--nocapture','--test-threads=1'],name,env=env);ns=re.findall(r'test result: ok\\. (\\d+) passed; 0 failed;',(r/(name+'.log')).read_text());assert ns==['1'];counts.append(1)
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build',env=env);start=time.time();run(['timeout','1800',str(t/'target/release/build_circuit')],'generate',env=env);assert all(sha(t/path)==h for path,h in{**freeze['source_files'],**freeze['protected_files']}.items());stool=ws/'breakthrough-stackv3-width-stats-20261020';run([str(stool/'tool/target/release/native_width_stats'),str(t/'ops.bin'),str(r/'OUTPUT-STATS.json')],'stats',r);st=json.loads((r/'OUTPUT-STATS.json').read_text());assert st['records_sha3']==p['output_records_sha3']and st['operations']==p['output_count']and st['qubits_protected_analyzer']<=1234;result={'status':'PUBLIC_E3_CACHE_PLUS_LIVE_PARITIES_NONCE0_NOT_GATED_OR_SCORED','native_tests':2,'previously_passing_unchanged_parent_controls':17,'inherited_parent_tests_failed':2,'independent_cache_proof_controls':9,'independent_live_proof_controls':6,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'stream_sha256':sha(t/'ops.bin'),'operations':st['operations'],'qubits':st['qubits_protected_analyzer'],'classical_bits':st['classical_bits'],'records_sha3':st['records_sha3'],'diagnostic_weight':st['fair_guard_depth_proxy'],'cache_leases':53,'live_parity_hits':len(p['hits']),'seconds':time.time()-start,'scope':freeze['scope']};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\\n');(r/'run.exit').write_text('0\\n');print(json.dumps(result),flush=True)
except Exception:
 (r/'run.exit').write_text('1\\n');raise
''');print(r)
