from pathlib import Path
r=Path(__file__).resolve().parent;e=r.parent
s=(e/'product-support-tight-20261019/tight_color.rs').read_text(encoding='utf-8')
s=s.replace('let mut examples=vec![];','let mut examples=vec![];let mut removed=vec![];let mut active_identities=0u64;let mut inactive_identities=0u64;let mut post_live_peak=registered.len();')
needle='  let touched:BTreeSet<_>='
insert='''  if matches!(o.kind,K::CCX|K::CCZ){let sa=&q[o.q_control1.0 as usize];let sb=&q[o.q_control2.0 as usize];let mut product=bounds.and(sa,sb,&d);if o.kind==K::CCZ{product=bounds.and(&product,&q[o.q_target.0 as usize],&d);}let fired=bounds.restrict(&product,eff,&d);if fired.is_no(){if eff==0{inactive_identities+=1;}else{active_identities+=1;}removed.push(serde_json::json!({"op":i,"kind":o.kind as u64,"guard_function":eff,"guard_proved_false":eff==0,"control1_support":sa.0,"control2_support":sb.0}));continue;}}
'''
assert s.count(needle)==1;s=s.replace(needle,insert+needle)
s=s.replace('  if i%1_000_000==0{','  post_live_peak=post_live_peak.max(nq-free.len());\n  if i%1_000_000==0{')
s=s.replace('"TIGHT_GUARD_SUPPORT_LIFETIME_DIAGNOSTIC_NOT_A_SCORE"','"EXACT_GUARD_COFACTOR_TOFFOLI_PRUNING_DIAGNOSTIC_NOT_A_SCORE"')
s=s.replace('"all_original_operations_retained":true','"all_other_original_operations_retained":true')
s=s.replace('"all_original_Toffolis_retained":true','"identity_Toffolis_removed":removed.len(),"potentially_executing_identities_removed":active_identities,"provably_inactive_Toffolis_removed":inactive_identities,"post_operation_live_peak":post_live_peak,"removed_sites":removed')
# Implementation controls still require exact states and physical RNG; costs
# may now decrease because that is the requested optimization.
s=s.replace('assert_eq!(a.3,z.3);','assert!(z.3<=a.3);')
s=s.replace('assert_eq!(r["recolored_Q"],3);assert_eq!(w.iter().filter(|o|o.kind==K::CCX).count(),1);','assert_eq!(r["recolored_Q"],1);assert_eq!(w.iter().filter(|o|o.kind==K::CCX).count(),0);')
s=s.replace('zero_quantum_controls_do_not_remove_a_scored_Toffoli','zero_quantum_controls_remove_an_identity_Toffoli')
# The secondary tight-controls helper compares a tuple containing T; separate
# that field so original value/phase/scratch/RNG checks remain strict.
s=s.replace('let result=(sim.qubits[0],sim.bits.clone(),sim.phase,sim.stats.toffoli_gates,scratch);','let result=(sim.qubits[0],sim.bits.clone(),sim.phase,scratch);')
s+='''
#[cfg(test)]mod cofactor_controls{use super::*;use quantum_ecc::circuit::{BitId,RegisterId};
#[test]fn disjoint_branch_controls_remove_a_potentially_executing_Toffoli(){let mut qr=Op::empty();qr.kind=K::AppendToRegister;qr.q_target=QubitId(0);qr.r_target=RegisterId(0);let mut cr=Op::empty();cr.kind=K::AppendToRegister;cr.c_target=BitId(0);cr.r_target=RegisterId(1);let mut sw=Op::empty();sw.kind=K::Swap;sw.q_control1=QubitId(0);sw.q_target=QubitId(2);sw.c_condition=BitId(0);let mut ccx=Op::empty();ccx.kind=K::CCX;ccx.q_control1=QubitId(0);ccx.q_control2=QubitId(2);ccx.q_target=QubitId(3);let(w,r)=color(&[qr,cr,sw,ccx]);assert_eq!(r["potentially_executing_identities_removed"],1);assert_eq!(r["identity_Toffolis_removed"],1);assert_eq!(w.iter().filter(|o|o.kind==K::CCX).count(),0);assert_eq!(r["recolored_Q"],2);}
}
'''
(r/'prune.rs').write_text(s,encoding='utf-8',newline='\n')
for name in ('io.rs','preflight.py'):(r/name).write_bytes((e/'product-guard-lifetimes-20261019'/name).read_bytes())
print('Prepared exact zero-support Toffoli identity pruning')
