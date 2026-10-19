from pathlib import Path
r=Path(__file__).resolve().parent;e=r.parent
s=(e/'product-guard-lifetimes-20261019/guard_color.rs').read_text(encoding='utf-8')
needle=' fn factors(&self,a:Id)->Vec<Id>'
insert=''' fn impossible(&self,v:&[Id])->bool{if v.contains(&0){return true;}if v.iter().any(|&a|v.iter().any(|&b|self.opposite(a,b))){return true;}v.iter().any(|&x|if let B::Not(child)=self.nodes[x as usize]{self.factors(child).iter().all(|id|v.binary_search(id).is_ok())}else{false})}
'''
assert s.count(needle)==1;s=s.replace(needle,insert+needle)
s=s.replace('v.iter().any(|&x|v.iter().any(|&y|self.opposite(x,y)))','self.impossible(&v)')
s=s.replace('t.iter().any(|&a|t.iter().any(|&b|d.opposite(a,b)))','d.impossible(&t)')
old='fn reset(&mut self,a:&Support,g:Id,d:&BoolDag)->Support{if g==0||a.is_no(){return a.clone();}if g==1{return Support::no();}let factors=d.factors(g);Support(a.0.iter().filter(|t|!Self::subset(&factors,t)).cloned().collect())}'
new='fn reset(&mut self,a:&Support,g:Id,d:&mut BoolDag)->Support{if g==0||a.is_no(){return a.clone();}if g==1{return Support::no();}let factors=d.factors(g);let remaining=Support(a.0.iter().filter(|t|!Self::subset(&factors,t)).cloned().collect());let ng=d.not(g);self.restrict(&remaining,ng,d)}'
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('bounds.reset(&q[t],eff,&d)','bounds.reset(&q[t],eff,&mut d)').replace('b.reset(st,guard,&d)','b.reset(st,guard,&mut d)').replace('b.reset(&s,g,&d)','b.reset(&s,g,&mut d)').replace('b.reset(&s,gh,&d)','b.reset(&s,gh,&mut d)').replace('b.reset(&only_g,h,&d)','b.reset(&only_g,h,&mut d)')
old_swap='K::Swap=>{let olda=q[a].clone();let oldt=q[t].clone();if eff==1{q[a]=oldt;q[t]=olda;}else{let sa=bounds.restrict(&olda,eff,&d);let st=bounds.restrict(&oldt,eff,&d);q[a]=bounds.union(&olda,&st,&d);q[t]=bounds.union(&oldt,&sa,&d);}},'
new_swap='K::Swap=>{let olda=q[a].clone();let oldt=q[t].clone();if eff==1{q[a]=oldt;q[t]=olda;}else if olda==oldt{q[a]=olda;q[t]=oldt;}else{let ng=d.not(eff);let keepa=bounds.restrict(&olda,ng,&d);let keept=bounds.restrict(&oldt,ng,&d);let sa=bounds.restrict(&olda,eff,&d);let st=bounds.restrict(&oldt,eff,&d);q[a]=bounds.union(&keepa,&st,&d);q[t]=bounds.union(&keept,&sa,&d);}},'
assert s.count(old_swap)==1;s=s.replace(old_swap,new_swap)
old_test='let a_new=if guard==1{oldt.clone()}else{let extra=b.restrict(&oldt,guard,&d);b.union(&olda,&extra,&d)};let t_new=if guard==1{olda.clone()}else{let extra=b.restrict(&olda,guard,&d);b.union(&oldt,&extra,&d)};'
new_test='let ng=d.not(guard);let a_new=if guard==1{oldt.clone()}else{let extra=b.restrict(&oldt,guard,&d);let keep=b.restrict(&olda,ng,&d);b.union(&keep,&extra,&d)};let t_new=if guard==1{olda.clone()}else{let extra=b.restrict(&olda,guard,&d);let keep=b.restrict(&oldt,ng,&d);b.union(&keep,&extra,&d)};'
assert s.count(old_test)==1;s=s.replace(old_test,new_test)
s=s.replace('"GUARD_SUPPORT_LIFETIME_DIAGNOSTIC_NOT_A_SCORE"','"TIGHT_GUARD_SUPPORT_LIFETIME_DIAGNOSTIC_NOT_A_SCORE"')
s+='''
#[cfg(test)]mod tight_controls{use super::*;use quantum_ecc::{circuit::{BitId,RegisterId},sim::Simulator};use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
fn compare(v:&[Op],w:&[Op]){for qi in [0,u64::MAX,0x5555555555555555]{for ci in [0,u64::MAX,0xaaaaaaaaaaaaaaaa]{for seed in 0u64..4{let calc=|v:&[Op]|{let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let mut h=Shake256::default();Update::update(&mut h,&seed.to_le_bytes());let mut rng=h.finalize_xof();let mut sim=Simulator::new(nq,nb,&mut rng);sim.qubits[0]=qi;sim.bits[0]=ci;sim.phase=0x5555aaaa5555aaaa;sim.apply_iter(v.iter());let mut scratch=sim.qubits[1..].to_vec();scratch.resize(8,0);scratch.sort_unstable();let result=(sim.qubits[0],sim.bits.clone(),sim.phase,sim.stats.toffoli_gates,scratch);drop(sim);let mut continuation=[0u8;64];rng.read(&mut continuation);(result,continuation)};assert_eq!(calc(v),calc(w));}}}}
fn op(k:K,a:u64,t:u64)->Op{let mut x=Op::empty();x.kind=k;x.q_control1=QubitId(a);x.q_target=QubitId(t);x}
fn regs()->Vec<Op>{let mut q=op(K::AppendToRegister,NO,0);q.r_target=RegisterId(0);let mut c=Op::empty();c.kind=K::AppendToRegister;c.c_target=BitId(0);c.r_target=RegisterId(1);vec![q,c]}
fn invert()->Op{let mut x=Op::empty();x.kind=K::BitInvert;x.c_target=BitId(0);x}
fn reset(q:u64)->Op{let mut x=op(K::R,NO,q);x.c_condition=BitId(0);x}
#[test]fn complementary_resets_prove_clean_without_an_unconditional_reset(){let mut v=regs();v.extend([reset(0),invert(),reset(0),op(K::X,NO,3),op(K::X,NO,3),op(K::R,NO,3)]);let(w,r)=color(&v);assert_eq!(r["recolored_Q"],1);assert!(r["conditional_clean_releases"].as_u64().unwrap()>0);compare(&v,&w);}
#[test]fn conditional_swap_transfers_the_dirty_support_to_the_other_branch(){let mut v=regs();let mut swap=op(K::Swap,0,2);swap.c_condition=BitId(0);v.extend([swap,invert(),reset(0),op(K::X,NO,3),op(K::X,NO,3),op(K::R,NO,3),invert(),reset(2)]);let(w,r)=color(&v);assert_eq!(r["recolored_Q"],2);assert!(r["conditional_clean_releases"].as_u64().unwrap()>=2);compare(&v,&w);}
#[test]fn negated_conjunction_conflict_is_recognized(){let mut d=BoolDag::new();let a=d.node(B::Input(0));let b=d.node(B::Input(1));let ab=d.and(a,b);let nab=d.not(ab);assert_eq!(d.and(ab,nab),0);let mut bounds=Bounds{cuts:0};assert!(bounds.normalize(vec![vec![a,b,nab]],&d).is_no());}
}
'''
(r/'tight_color.rs').write_text(s,encoding='utf-8',newline='\n')
for name in ('io.rs','preflight.py'):(r/name).write_bytes((e/'product-guard-lifetimes-20261019'/name).read_bytes())
print('Prepared stronger reset/swap support rules with unchanged caps')
