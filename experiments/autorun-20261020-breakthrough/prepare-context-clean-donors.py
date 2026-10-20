from pathlib import Path
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-plan7-zero-donors-20261020';r=root/'experiments/breakthrough-stackv3-plan7-context-clean-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore']:(r/p).write_bytes((old/p).read_bytes())
(r/'PLAN.md').write_text('''# Exact arbitrary-cut proof of existing donor cleanliness

Fixed1233/t28 generic-v2 stream before any final gate. Earlier zero-added-wire
scan proved117 leases; every proposed pair passed, but conservative reset-only
clean flags excluded other idle wires. Preserve that result and development
measurement: generic1233 mean757702.2428 vs public756477.9651 on512x64, wrongvalue
54/54, zero dirty,36 joint-failure output differences; no record or final gate.

New nomination admits an existing idle donor only after a full arbitrary-cut
symbolic trace proves BOTH that donor's value is exactlyzero at the first endpoint
and equality of the effective products at both endpoints. Same lexical outer
scope,16,384-op earlier cut, all original no-touch/nonoverlap rules. Outside the
common outer guard both endpoints and new donor operations are skipped, so
the original false-world value is preserved. Fingerprints never prove zero.
All prior7 native controls remain; two new controls require exact contextzero,
reject a missing reset or unmatchedX, and replay full basis/phase with newphase
repair fault detection. No extra wires, no new algebra or relaxed guard.
Component output still requires whole-source binding/development/finalgate/
qualified nonce/unchanged benchmark; no scored result is declared here.
''')
(r/'patch-tool.py').write_text('''from pathlib import Path
p=Path(__file__).resolve().parent/'tool/discover.rs';s=p.read_text();start=s.index('fn exact_proof_from(');end=s.index('\\nfn context_start(',start);f=s[start:end];f=f.replace('fn exact_proof_from(','fn exact_zero_donors_from(',1).replace('start:usize)->bool{','start:usize)->Option<Vec<bool>>{',1).replace('return false','return None').replace('let mut expected=None;','let mut expected=None;let mut zeros=None;');needle='if start+i==first{if !stack.is_empty()||base!=vec![0]{return None;}let product';assert f.count(needle)==1;f=f.replace(needle,'if start+i==first{if !stack.is_empty()||base!=vec![0]{return None;}zeros=Some(q.iter().map(|e|e.is_empty()).collect());let product');needle='stack.is_empty()&&base==vec![0]&&Some(actual)==expected';assert f.count(needle)==1;f=f.replace(needle,'if stack.is_empty()&&base==vec![0]&&Some(actual)==expected{zeros}else{None}');s=s[:end]+'\\n'+f+s[end:]
needle='let donor=(0..nq).find(|&d|d!=a&&d!=b&&d!=t&&clean[d]&&touches[d].is_none_or(|j|j<first)&&busy[d].is_none_or(|j|j<first));\\n    if let Some(d)=donor{proposed+=1;if context_proof(&ops,first,i,nq,nb)'
assert s.count(needle)==1
replacement='''+'"""'+'''let idle=|d:usize|d!=a&&d!=b&&d!=t&&touches[d].is_none_or(|j|j<first)&&busy[d].is_none_or(|j|j<first);
    let mut donor=(0..nq).find(|&d|idle(d)&&clean[d]);let mut context_zero_proved=false;
    if donor.is_none(){let cut=context_start(&ops,first);if cut<first&&(0..nq).any(|d|idle(d)&&touches[d].is_some_and(|j|j>=cut)){if let Some(zero)=exact_zero_donors_from(&ops,first,i,nq,nb,cut){donor=(0..nq).find(|&d|idle(d)&&zero[d]);context_zero_proved=donor.is_some();}}}
    if let Some(d)=donor{proposed+=1;if context_zero_proved||context_proof(&ops,first,i,nq,nb)'''+ '"""'+'''
s=s.replace(needle,replacement)
s+='''+'"""'+'''
#[cfg(test)]mod donor_zero_tests{
use super::*;use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;
struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(self.0);}}
fn fixture(outer:bool)->(Vec<Op>,usize,usize){let n=u64::MAX;let mut ops=vec![];if outer{ops.push(make(K::PushCondition,n,n,n,n,0));}ops.extend([make(K::R,n,n,5,n,n),make(K::X,n,n,5,n,n),make(K::X,n,n,5,n,n),make(K::R,n,n,2,n,n),make(K::CX,n,0,2,n,n)]);let first=ops.len();ops.push(make(K::CCX,0,1,3,n,n));ops.push(make(K::X,n,n,4,n,n));let last=ops.len();ops.push(make(K::CCX,2,1,4,n,n));if outer{ops.push(make(K::PopCondition,n,n,n,n,n));}(ops,first,last)}
#[test]fn exact_context_zero_requires_reset_and_all_cancellations(){for outer in[false,true]{let(ops,first,last)=fixture(outer);let cut=context_start(&ops,first);let zeros=exact_zero_donors_from(&ops,first,last,6,1,cut).unwrap();assert!(zeros[5]);assert!(!zeros[0]&&!zeros[1]);let mut bad=ops.clone();bad[usize::from(outer)+2].kind=K::Z;bad[usize::from(outer)+2].validate();assert!(!exact_zero_donors_from(&bad,first,last,6,1,cut).unwrap()[5]);let mut bad=ops.clone();bad[usize::from(outer)].kind=K::X;bad[usize::from(outer)].validate();assert!(!exact_zero_donors_from(&bad,first,last,6,1,cut).unwrap()[5]);}}
#[test]fn context_zero_borrow_preserves_values_phase_and_zero_width_and_detects_bad_fix(){let mut caught=0;for outer in[false,true]{let(ops,first,last)=fixture(outer);let cut=context_start(&ops,first);assert!(exact_zero_donors_from(&ops,first,last,6,1,cut).unwrap()[5]);let f=ops[first];let l=ops[last];let lease=[first as u64,last as u64,5,f.q_control2.0,f.q_control1.0,f.q_target.0,l.q_control2.0,l.q_control1.0,l.q_target.0];let out=rewrite_ops(ops.clone(),&[lease],1);assert!(out.iter().flat_map(|o|[o.q_control2.0,o.q_control1.0,o.q_target.0]).all(|q|q==u64::MAX||q<6));let faulty:Vec<_>=out.iter().filter(|o|o.kind!=K::CZ).copied().collect();for pattern in[0u8,255,0xa5,0x5a]{let mut ra=Fixed(pattern);let mut rb=Fixed(pattern);let mut rf=Fixed(pattern);let mut a=Simulator::new(6,2,&mut ra);let mut b=Simulator::new(6,2,&mut rb);let mut bad=Simulator::new(6,2,&mut rf);for lane in 0..64{for q in 0..6{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}a.bits[0]|=((lane>>5&1)as u64)<<lane;}b.qubits.clone_from(&a.qubits);bad.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);bad.bits.clone_from(&a.bits);a.apply_iter(ops.iter());b.apply_iter(out.iter());bad.apply_iter(faulty.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.phase,b.phase);assert_eq!(a.bits[..1],b.bits[..1]);caught+=u64::from(a.phase!=bad.phase);}}assert!(caught>0);}
}
'''+ '"""'+'''
p.write_text(s)
''')
s=(old/'run.py').read_text();needle="p.write_text(s);subprocess.run(['cp'";assert s.count(needle)==1;s=s.replace(needle,"p.write_text(s);subprocess.run(['python3',str(r/'patch-tool.py')],check=True);subprocess.run(['cp'")
s=s.replace("==['7']","==['9']").replace("'native_controls':7","'native_controls':9").replace("'lookback':16384","'lookback':16384,'context_zero_donor_proof':True").replace("'ZERO_ADDED_WIRE_EXACT_CONTEXT_COMPONENT_NOT_SCORED'","'EXACT_CONTEXT_PROVED_ZERO_DONORS_COMPONENT_NOT_SCORED'")
(r/'run.py').write_text(s);print(r)
