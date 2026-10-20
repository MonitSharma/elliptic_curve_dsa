from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-value-ir-audit-v4-20261020';r=a.parent/'breakthrough-value-abstract-audit-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'audit.rs').read_text();pos=s.index('fn main()')
extra='''#[derive(Clone,Copy,Debug)]struct TV{z:u64,o:u64}
impl TV{fn known(v:u64)->Self{Self{z:!v,o:v}}fn unknown()->Self{Self{z:0,o:0}}fn not(self)->Self{Self{z:self.o,o:self.z}}fn and(self,b:Self)->Self{Self{z:self.z|b.z,o:self.o&b.o}}fn xor(self,b:Self)->Self{Self{z:(self.z&b.z)|(self.o&b.o),o:(self.z&b.o)|(self.o&b.z)}}fn or(self,b:Self)->Self{self.not().and(b.not()).not()}fn ite(self,a:Self,b:Self)->Self{Self{z:(self.o&a.z)|(self.z&b.z)|(a.z&b.z),o:(self.o&a.o)|(self.z&b.o)|(a.o&b.o)}}}
fn abstract_eval(p:&Program,initial_q:&[u64],initial_bits:&[u64])->Vec<TV>{let mut q:Vec<_>=initial_q.iter().map(|&x|TV::known(x)).collect();let mut c=vec![TV::unknown();p.versions];for(i,&b)in initial_bits.iter().enumerate(){c[i]=TV::known(b);}for n in &p.nodes{let g=p.guards[n.g as usize].iter().fold(TV::known(u64::MAX),|v,&x|v.and(c[x as usize]));let t=n.t as usize;match n.k{QX=>q[t]=q[t].xor(g),QCX=>q[t]=q[t].xor(g.and(q[n.a as usize])),QCCX=>q[t]=q[t].xor(g.and(q[n.a as usize]).and(q[n.b as usize])),QSWAP=>{let old=q[t];q[t]=g.ite(q[n.a as usize],old);q[n.a as usize]=g.ite(old,q[n.a as usize]);},QZERO=>q[t]=q[t].and(g.not()),CINV=>c[t]=c[n.a as usize].xor(g),CZERO=>c[t]=c[n.a as usize].and(g.not()),CONE=>c[t]=c[n.a as usize].or(g),CRNG=>c[t]=g.ite(TV::unknown(),c[n.a as usize]),_=>unreachable!()}}q}
fn verify_abstract(abstract_q:&[TV],q:&[u64],outputs:&[usize]){for &x in outputs{let a=abstract_q[x];assert_eq!(a.z&a.o,0);assert_eq!(q[x]&(a.z|a.o),a.o,"Abstract known output disagrees with exact output at wire{x}");}}
fn full_abstract_audit(p:&Program,ops:&[Op],outputs:&[usize])->serde_json::Value{
 use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};use quantum_ecc::sim::Simulator;let mut h=Shake256::default();h.update(b"value-abstract-source-audit-20261020-v1");let mut stream=h.finalize_xof();let mut word=||{let mut x=[0;8];stream.read(&mut x);u64::from_le_bytes(x)};let registered_bits:Vec<_>=ops.iter().filter(|o|o.kind==K::AppendToRegister&&o.c_target.0!=u64::MAX).map(|o|o.c_target.0 as usize).collect();let mut rows=vec![];
 for case in 0..8{let mut q=vec![0;p.nq];let mut bits=vec![0;p.nb];for &x in outputs{q[x]=if case==0{0}else if case==1{u64::MAX}else{word()};}for &x in &registered_bits{bits[x]=if case==0{0}else if case==1{u64::MAX}else{word()};}let started=std::time::Instant::now();let abstract_q=abstract_eval(p,&q,&bits);let seconds=started.elapsed().as_secs_f64();let known:u64=outputs.iter().map(|&x|(abstract_q[x].z|abstract_q[x].o).count_ones()as u64).sum();
  for pattern in 0..3{let words:Vec<u64>=(0..p.rng).map(|_|if pattern==0{0}else if pattern==1{u64::MAX}else{word()}).collect();let mut rng=AuditWords{v:words.iter().flat_map(|x|x.to_le_bytes()).collect(),at:0};let mut sim=Simulator::new(p.nq,p.nb,&mut rng);sim.qubits.copy_from_slice(&q);sim.bits.copy_from_slice(&bits);sim.apply_iter(ops.iter());let mut exact_ir=q.clone();eval(p,&mut exact_ir,&bits,&words);for &x in outputs{assert_eq!(exact_ir[x],sim.qubits[x],"Fullstream valueIR/protected mismatch case{case} pattern{pattern}");}verify_abstract(&abstract_q,&sim.qubits,outputs);drop(sim);assert_eq!(rng.at,p.rng*8);}
  rows.push(serde_json::json!({"case":case,"known_output_bits":known,"total_output_bits":outputs.len()*64,"abstract_seconds":seconds,"protected_concrete_rng_patterns":3}));eprintln!("ABSTRACT_FULLSTREAM_PROTECTED_PASS case={case} known={known} seconds={seconds}");
 }serde_json::json!({"label":"value-abstract-source-audit-20261020-v1","arbitrary_registered_initial_inputs":"allzero/allone/six fixed-label pseudorandom64lane inputs, helperszero; no curve correctness claim","cases":rows,"protected_fullstream_comparisons":24,"nonce_screens":0,"scope":"Three-valued overapproximation of all measurement outcomes, verified against full protected finalpoint values for three concrete RNG patterns per case. Only known output bits can support separately qualified wrongpoint witnesses; no acceptance or phase/dirty certificate. Audit inputs are not challenge packets or a statistical failure gate. No scored counts or submitted quantum circuit."})}
struct AuditWords{v:Vec<u8>,at:usize}impl sha3::digest::XofReader for AuditWords{fn read(&mut self,out:&mut[u8]){out.copy_from_slice(&self.v[self.at..self.at+out.len()]);self.at+=out.len();}}
'''
s=s[:pos]+extra+s[pos:]
s=s.replace('let result=serde_json::json!({','let abstract_result=full_abstract_audit(&p,&ops,&outputs);let result=serde_json::json!({"abstract_audit":abstract_result,',1)
# Every inherited small native fixture also checks abstract known masks against protected values.
s=s.replace('sim.apply_iter(ops.iter());eval(&p,&mut q,&bits,&words);','let abstract_q=abstract_eval(&p,&q,&bits);sim.apply_iter(ops.iter());verify_abstract(&abstract_q,&sim.qubits,outputs);eval(&p,&mut q,&bits,&words);',1)
# checked_known_bits uses its local inputs as outputs.
needle='let bits=sim.bits.clone();sim.apply_iter(ops.iter());eval(&p,&mut q,&bits,&words);'
s=s.replace(needle,'let bits=sim.bits.clone();let abstract_q=abstract_eval(&p,&q,&bits);sim.apply_iter(ops.iter());verify_abstract(&abstract_q,&sim.qubits,&inputs);eval(&p,&mut q,&bits,&words);',1)
pos=s.rfind('\n}')
s=s[:pos]+'''
 #[test]fn abstract_boolean_truth_tables_cover_all_concretizations(){let states=[TV::known(0),TV::known(u64::MAX),TV::unknown()];for a in states{for b in states{for g in states{for av in[0,u64::MAX]{if(av&(a.z|a.o))!=a.o{continue;}for bv in[0,u64::MAX]{if(bv&(b.z|b.o))!=b.o{continue;}for gv in[0,u64::MAX]{if(gv&(g.z|g.o))!=g.o{continue;}for(x,v)in[(a.and(b),av&bv),(a.or(b),av|bv),(a.xor(b),av^bv),(g.ite(a,b),(gv&av)|(!gv&bv))]{assert_eq!(x.z&x.o,0);assert_eq!(v&(x.z|x.o),x.o);}}}}}}}}
 #[test]fn abstract_unknown_measurement_never_certifies_random_output(){let n=u64::MAX;let ops=vec![op(K::Hmr,n,n,3,1,n),op(K::X,n,n,2,n,1)];let p=checked(&ops,&[0,1,2],&[0,1,2]);let q=vec![0;p.nq];let bits=vec![0;p.nb];let a=abstract_eval(&p,&q,&bits);assert_eq!(a[2].z|a[2].o,0);assert_eq!(a[0].z,u64::MAX);}
''' +s[pos:]
(r/'audit.rs').write_text(s)
s=(old/'run.py').read_text().replace('12 passed; 0 failed;','14 passed; 0 failed;').replace("'native_controls':12","'native_controls':14").replace('Twelve protected native','Fourteen protected native')
start=s.index(",'toffoli747226':");end=s.index('};assert all(sha(p)==h',start);s=s[:start]+s[end:]
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Verification-only three-valued output audit, no nonce rejection

Label value-abstract-source-audit-20261020-v1 declared before8source-only input
fixtures: allzero/allone/six deterministic pseudorandom64lane registered inputs;
all physical helper qubits/bitszero. These are arbitrary values, not a curve
correctness census, challengepacket, nonce search or statistical gate. Same
frozen product61927788 source and protected dependency hashes; no candidate edit.

Inherit exact captured-SSA/Boolean-alias/dominance/value-liveness/cancellation
tool. Fourteen protected native tests include exhaustive ternary Boolean truth
tables across every concretization, smallbasis guard/mutation/RNG/reset/fault
fixtures and unknownmeasurement never becoming certifiedknown output. Three-
valued0/1/unknown operations conservatively overapproximate ALL RNG values.
Then8fullstream cases: compare every outputvalue against protected Simulator
for allzero/allone/pseudorandom measurement words, exact original RNG slots,
and require abstract known masks agree with all24protected fullstream outcomes.

Known-output coverage and verifierwalltime only; never quantum resource counts.
No nonce rejected/screened, phase/dirty acceptance or original gate verdict used.
A future rejection filter needs independent FS/tail/source/curve qualification;
only certifiedknown wrongpoint bits may reject and every potentialPASS must
still use originalfullstate engine/protected9024/unchangedbenchmark.
''');print(r)
