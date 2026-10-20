from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-width-live-20261020';r=a.parent/'breakthrough-guarded-live-products-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
(r/'patch-tool.py').write_text('''from pathlib import Path
r=Path(__file__).parent;p=r/'tool/main.rs';s=p.read_text();needle='let mut replacement=None;';assert s.count(needle)==1;s=s.replace(needle,needle+'let gate=if o.c_condition==NO_BIT{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};')
needle='if let Some((controls,one))=parity(&product,&q,&index,if o.kind==K::CCX{Some(t)}else{None}){';assert s.count(needle)==1
s=s.replace(needle,'let skip=if o.kind==K::CCX{Some(t)}else{None};let mut restricted=false;let reduced=parity(&product,&q,&index,skip).or_else(||{if gate==vec![0]{None}else{let target=alg.and(&product,&gate);let result=parity(&target,&q,&index,skip);restricted=result.is_some();result}});if let Some((controls,one))=reduced{')
needle='"expression":product';assert s.count(needle)==1;s=s.replace(needle,'"expression":product,"guard_restricted":restricted');s+=(r/'guarded-tests.rs').read_text();p.write_text(s)
''')
(r/'guarded-tests.rs').write_text('''
#[cfg(test)]mod guard_restricted_tests{
use super::*;
fn fixture(phase:bool,outer:bool,mutate:bool,wrong:bool)->Vec<Op>{let n=u64::MAX;let mut v=vec![];for q in 0..4{let mut o=op(K::AppendToRegister,n,n,q,n,n);o.r_target=quantum_ecc::circuit::RegisterId(0);v.push(o);}for bit in 0..2{let mut o=op(K::AppendToRegister,n,n,n,bit,n);o.r_target=quantum_ecc::circuit::RegisterId(1);v.push(o);}if outer{v.push(op(K::PushCondition,n,n,n,n,0));}v.push(op(K::CCX,0,1,4,n,if outer{1}else{0}));if mutate{v.push(op(K::BitInvert,n,n,n,0,n));}v.push(op(if phase{K::CCZ}else{K::CCX},0,1,3,n,if outer{1}else if wrong{1}else{0}));if outer{v.push(op(K::PopCondition,n,n,n,n,n));}v}
fn op(k:K,a:u64,b:u64,t:u64,ct:u64,cc:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control2=QubitId(a);o.q_control1=QubitId(b);o.q_target=QubitId(t);o.c_target=BitId(ct);o.c_condition=BitId(cc);if k==K::AppendToRegister{o.r_target=quantum_ecc::circuit::RegisterId(0);}o.validate();o}
fn paired(ops:&[Op],out:&[Op]){use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;struct F(u8,usize);impl XofReader for F{fn read(&mut self,b:&mut[u8]){b.fill(self.0);self.1+=b.len();}}let(nq,nb,_,_)=analyze_ops(ops.iter().chain(out));for pattern in[0u8,255,0xa5,0x5a]{let mut ra=F(pattern,0);let mut rb=F(pattern,0);let mut a=Simulator::new(nq as usize,nb as usize,&mut ra);let mut b=Simulator::new(nq as usize,nb as usize,&mut rb);for lane in 0..64{for q in 0..4{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}for bit in 0..2{a.bits[bit]|=((lane>>(bit+4)&1)as u64)<<lane;}}b.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);a.apply_iter(ops.iter());b.apply_iter(out.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits);assert_eq!(a.phase,b.phase);drop(a);drop(b);assert_eq!(ra.1,rb.1);}}
#[test]fn restricted_guard_identity_preserves_full_basis_phase_and_captured_mutations(){for phase in[false,true]{for outer in[false,true]{for mutate in[false,true]{if mutate&&!outer{continue;}let ops=fixture(phase,outer,mutate,false);let(out,hits,_)=simplify(&ops);assert!(hits.iter().any(|h|h["guard_restricted"]==true));paired(&ops,&out);}}}}
#[test]fn nonmatching_guards_or_changed_per_op_guard_are_not_reused(){for mutate in[false,true]{let ops=fixture(false,false,mutate,!mutate);let(out,hits,_)=simplify(&ops);assert!(hits.is_empty());paired(&ops,&out);}}
#[test]fn removing_guarded_phase_repair_is_detected(){let ops=fixture(true,true,true,false);let(out,hits,_)=simplify(&ops);assert!(hits.iter().any(|h|h["guard_restricted"]==true));let faulty:Vec<_>=out.iter().filter(|o|o.kind!=K::CZ).copied().collect();assert_ne!(out.len(),faulty.len());let caught=std::panic::catch_unwind(||paired(&ops,&faulty));assert!(caught.is_err());}
}
''')
s=(old/'run.py').read_text();needle="subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)";assert s.count(needle)==1;s=s.replace(needle,"subprocess.run(['python3',str(r/'patch-tool.py')],check=True);"+needle)
needle="'publicacd0':(ws/'breakthrough-public-acd0-reproduction-20261020/parent/ops.bin','3d7c94f1dea887dd2d4ff13326e350756350cc1044d396444c3f820f8bfad827')";assert s.count(needle)==1;s=s.replace(needle,needle+",'toffoli747226':(ws/'breakthrough-groups-context-final-20261020/candidate/ops.bin','278802f0728d9233297723c88dffef8544bd9c3ce9968d34a2c3f406b383688a')")
s=s.replace("test result: ok. 6 passed; 0 failed;","test result: ok. 9 passed; 0 failed;").replace("'scope':'Same exact512-term original-op live-product algebra/parity proof and six native controls, newly applied to full frozen publicparent and width1233cache113 streams. No point-input sampling/gate/nonce/score.'","'scope':'Exact guard-restricted parity: if g*p equals a live linear parityL, replace guarded product with guardedL, since g*g=g. Same raw proof first; unknown/truncated identities never accepted. Nine native controls including full guards/captured mutations/phase fault. Fixed originalpublic, width1233cache113 and latestT747226 streams. No point-input sampling/gate/nonce/score.'")
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Exact effective-guard parity optimization

For a Toffoli/CCZ with effective captured classical guardg and productp, first
try the unchanged raw identity p=L. If absent, prove g*p=L from the same exact
global Boolean algebra and sparse Gaussian parity over live quantum wires.
Then guardedL equals g*L=g*g*p=g*p. Preserve the original guard, metadata,
RNG/measurements and quantum indices. CCX target is excluded; CCZ self-target
becomes Z as before. Truncation forgets identities conservatively.

Nine native controls must pass: original6 plus guarded basis/phase/captured-
mutation, nonmatching guard rejection and missing phase fault detection.
Fixed inputs frozen before scans: publicacd0, width1233cache113 and latest
T747226 selected stream. No circuit/precision/packet tuning, no point census,
finalgate, nonce or scored result. Any useful finished wrapper needs fresh own
gate against the exact current record and complete unchanged benchmark.
''');print(r)
