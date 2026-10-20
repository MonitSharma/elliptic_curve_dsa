from pathlib import Path
from datetime import datetime,timezone
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-width-loan-drop130-20261020';r=root/'experiments/breakthrough-stackv3-width-plan7-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore']:shutil.copyfile(old/p,r/p)
s=(old/'prepare.py').read_text();s=s.replace('return 2;}','return 3;}');s=s.replace('std::env::set_var("STACK_DROP130_RESEARCH",if config.is_some(){"1"}else{"0"})','std::env::set_var("STACK_DROP130_RESEARCH",if config.is_some_and(|(cap,_)|cap<1234){"1"}else{"0"})');needle='assert all(sha(t/p)==h for p,h in protected.items());prior=';assert s.count(needle)==1
injection='''p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'const Y28_PLAN8:';assert raw.count(needle)==1;raw=raw.replace(needle,b'const Y28_PLAN7: ([usize;12],[usize;5])=([7,6,6,5,5,4,4,3,3,2,2,3],[0,2,4,6,8]);\\n'+needle);needle=b'    if drop > 0 && merged_plan(nbits - 1, budget).is_none() && merged_plan(nbits, budget).is_none() {';assert raw.count(needle)==1;raw=raw.replace(needle,b'    if std::env::var("STACK_DROP130_RESEARCH").is_ok_and(|v|v=="1") && nbits==50 && budget==7 && drop>=3 && merged_plan(nbits-1,budget).is_none() && merged_plan(nbits,budget).is_none(){assert_eq!(Y28_PLAN7.0.iter().sum::<usize>(),50);return(Y28_PLAN7.0.to_vec(),lean45,Y28_PLAN7.1.to_vec());}\\n'+needle)
reference=r.parent/'breakthrough-native-both-final-20261020/candidate/src/point_add/y15_onefold.rs';ref=reference.read_bytes();a=ref.index(b'#[cfg(test)]mod plan7_tests{');z=ref.index(b'\\nfn phase_cubic_lin(',a);tests=ref[a:z].replace(b'mod plan7_tests{',b'mod stack_plan7_port_tests{');raw+=b'\\n'+tests+b'\\n'+(r/'additional-tests.rs').read_bytes();p.write_bytes(raw);(r/'ported-native-tests.rs').write_bytes(tests)
assert all(sha(t/p)==h for p,h in protected.items());prior='''
s=s.replace(needle,injection).replace("'supported_forward_drop130':2","'supported_forward_drop130':3,'new_explicit_seven_wire_plan':True");(r/'prepare.py').write_text(s)
(r/'additional-tests.rs').write_text('''
#[cfg(test)]mod stack_plan7_admission_tests{
 use super::*;use crate::circuit::{analyze_ops,OperationType};use crate::sim::Simulator;use sha3::digest::XofReader;
 struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(self.0);}}
 #[test]fn explicit_seven_budget_case_is_admitted_without_weakening_old_contract(){std::env::set_var("STACK_DROP130_RESEARCH","1");let mut c=Builder::new();let cap=cells::cap();let _=c.alloc_qubits(cap-5);let(p,lean,d)=fold_plan_d(&c,56,"forward",3);assert!(lean);assert_eq!(p,Y28_PLAN7.0);assert_eq!(d,Y28_PLAN7.1);std::env::remove_var("STACK_DROP130_RESEARCH");}
 #[test]fn missing_phase_repair_in_seven_wire_plan_is_detected(){let mut b=Builder::new();let a=b.alloc_qubits(56);let target=b.alloc_qubits(56);let cin=b.alloc_qubit();let add:Vec<_>=a.iter().map(|&q|l(q)).collect();ladder_drop(&mut b,&target,&add,6,cin,&Y28_PLAN7.0,&Y28_PLAN7.1);let ops=b.take_ops();let faulty:Vec<_>=ops.iter().filter(|o|!matches!(o.kind,OperationType::Z|OperationType::CZ)).copied().collect();let(nq,nb,_,_)=analyze_ops(ops.iter());let mut caught=0;for word in[0u8,255,0xa5,0x5a]{let mut ra=Fixed(word);let mut rb=Fixed(word);let mut s=Simulator::new(nq as usize,nb as usize,&mut ra);let mut f=Simulator::new(nq as usize,nb as usize,&mut rb);for(i,q)in a.iter().chain(&target).copied().chain([cin]).enumerate(){s.qubits[q.0 as usize]=0x9e3779b97f4a7c15u64.wrapping_mul((i+1)as u64).rotate_left((i%64)as u32);}f.qubits.clone_from(&s.qubits);s.apply_iter(ops.iter());f.apply_iter(faulty.iter());assert_eq!(s.phase,0);assert_eq!(s.qubits,f.qubits);caught+=u64::from(f.phase!=0);}assert!(caught>0);}
}
''')
run=(old/'run.py').read_text();needle="assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build')==0;rows=[]";assert run.count(needle)==1;run=run.replace(needle,"assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','stack_plan7_','--','--nocapture','--test-threads=1'],'tests')==0;assert 'test result: ok. 4 passed; 0 failed;'in(r/'tests.log').read_text();"+needle);(r/'run.py').write_text(run)
(r/'PLAN.md').write_text('''# Explicit independently native-verified seven-wire dropped-carry plan

Recipe SL_N2_DROPN already selects2, so the prior drop2 override was a no-op.
Closed-ripple flags are empty; the earlier closed-path explanation was wrong.
Current fold_plan_d only admits budgets8/9. Add a new explicit50-bit/budget7/
drop>=3 case, using the already independently tested exact plan from prior
plan7 research: lengths7,6,6,5,5,4,4,3,3,2,2,3; nonadjacent drops0,2,4,6,8.
Its ladder is unchanged, all original drop/live-parent/cap assertions stay.
No old8/9 guard is weakened; unsupported cases still follow original rejection.

Retain exact loan128. Requestdrop3 at forward130 only in lowerbudget cases;
baseline1234 and fullpublic control use the original recipe. Port the exact
two existing native controls for full50-bit affine addition/phase/7-and8 width
and adjacent-drop rejection. Add direct new admission and missing-phase fault
controls. All4 must pass before any new full construction. Then fullpublic714c
must reproduce, followed by fixedraw1234/t21,1234/t28,1233/t28,1232/t28.
Stronger28-bit witness for candidates, no new approximation/guard/cut. Keep
all failures as construction results, no final gate/nonce/benchmark here.
''')
log=f'\n{datetime.now(timezone.utc).isoformat()} predeclare explicit nativeplan7 port: old2drop alreadyrecipeoverride; addonly verified50bitbudget7drop3case unchangedladderguards,repeat4native functional/phase/width/fault tests,exactloan128 plusdrop3fwd130onlycap<1234,714c fullpubliccontrolbeforefixedrawgrid,strongwitness28,no gate/nonce.\n';p=root/'experiments/autorun-20261020-breakthrough/LOG.md';p.write_bytes(p.read_bytes().rstrip()+log.encode());print(r)
