from pathlib import Path
import json,hashlib,struct,shutil,subprocess
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016');sites=json.loads((r/'flag-regions.json').read_text());assert len(sites)==12
assert(r/'quantum-proofs.exit').read_text().strip()=='0';assert json.loads((r/'flag-prefix-zero-receipt.json').read_text())['proved']
for s in sites:
 for mode in ['old','new']:
  x=json.loads((r/f'{mode}-quantum-contract-{s["site"]}.json').read_text());assert x['phase_contract_proved']and not x['q_contract_unresolved']and x['outer_caps']==0
 assert(r/f'negative-quantum-contract-{s["site"]}.exit').read_text().strip()!='0'
exec((r/'prepare-flag-regions.py').read_text().split('raw=load(')[0])
blob=bytearray(b'QFLAG001'+struct.pack('<Q',len(sites)))
for s in sites:
 old=load(r/f'old-flag-{s["site"]}.bin');new=load(r/f'new-flag-{s["site"]}.bin');blob+=struct.pack('<QQ',len(old)//56,len(new)//56)+old+new
(r/'quantum_flag.bin').write_bytes(blob)
front=(r.parent/'seam-phase-repair-20261016/front_seam.rs').read_text();decode=front[front.index('fn decode'):front.index('fn spec')]
helpers=front[front.index('fn quantum'):front.index('fn static_contract')]
helpers=helpers.replace('assert!(stack.is_empty()&&base==1,"front seam prefix scope");q','q')
head='''//! All source-defined merged flag erasures gain one lower quantum borrow bit.
//! Complete old regions must survive inherited passes unchanged. All original
//! measurement/classical/snapshot operations remain, with one fresh cleanup MR.
use crate::circuit::{Op,OperationType as K,QubitId,BitId,RegisterId,QubitOrBit,analyze_ops};
use std::collections::BTreeSet;
const NONE:u64=u64::MAX;
const DATA:&[u8]=include_bytes!("quantum_flag.bin");
'''
spec='''
fn specs()->Vec<(Vec<Op>,Vec<Op>)>{assert_eq!(&DATA[..8],b"QFLAG001");let u=|i|u64::from_le_bytes(DATA[i..i+8].try_into().unwrap())as usize;assert_eq!(u(8),12);let mut at=16;let mut out=Vec::new();for _ in 0..12{let n=u(at);let m=u(at+8);at+=16;assert_eq!(m,n+16);let old=decode(&DATA[at..at+56*n]);at+=56*n;let new=decode(&DATA[at..at+56*m]);at+=56*m;out.push((old,new));}assert_eq!(at,DATA.len());out}
struct Meta{seed:u64,target:u64,lower:[u64;3],scratch:&'static[u64]}
const META:[Meta;12]=[
'''
for s in sites:spec+=f'Meta{{seed:{s["old_seed"]},target:{s["target"]},lower:{s["lower"]},scratch:&{s["scratch"]}}},\n'
spec+='];\n'
body='''
fn static_contract(old:&[Op],new:&[Op],m:&Meta){
 assert_eq!(new.len(),old.len()+16);assert_eq!(old[0].kind,K::Hmr);assert_eq!(old[0].q_target.0,m.target);assert_eq!(old[1].kind,K::PushCondition);assert_eq!(old.last().unwrap().kind,K::PopCondition);
 assert_eq!(&new[..2],&old[..2]);let cleanup=new.len()-9;assert_eq!(new[cleanup].kind,K::Hmr);assert_eq!(new[cleanup].q_target.0,m.target);assert_eq!(new[cleanup].c_target.0,45701);assert_eq!(new[cleanup+1].kind,K::PushCondition);assert_eq!(new[cleanup+1].c_condition.0,45701);assert_eq!(new[cleanup+7].kind,K::PopCondition);assert_eq!(new.last(),old.last());
 let mut restored=new[..2].to_vec();restored.extend_from_slice(&new[10..cleanup]);restored.push(*new.last().unwrap());let mut replaced=0;
 for o in &mut restored[2..old.len()-1]{if matches!(o.kind,K::CX|K::CZ|K::CCX|K::CCZ){for q in [&mut o.q_target,&mut o.q_control1,&mut o.q_control2]{if q.0==m.target{q.0=m.seed;replaced+=1;}}}}
 assert_eq!(replaced,4,"flag old seed interface");assert_eq!(restored,old,"flag original operation/MR/snapshot sequence changed");
 let used=quantum(new);assert!(used.iter().all(|q|*q<1234));assert!(old.iter().all(|o|o.c_target.0==NONE||o.c_target.0<45701));assert!(old.iter().all(|o|o.c_condition.0==NONE||o.c_condition.0<45701));
 let mut d=0;for o in old{d=depth(d,o);}assert_eq!(d,0);for o in new{d=depth(d,o);}assert_eq!(d,0);
 let count=|s:&[Op],k|s.iter().filter(|o|o.kind==k).count();assert_eq!(count(new,K::CCX),count(old,K::CCX)+1);assert_eq!(count(new,K::Hmr),count(old,K::Hmr)+1);assert_eq!(count(new,K::R),count(old,K::R));
}
fn matches(ops:&[Op],old:&[Op])->Vec<usize>{ops.windows(old.len()).enumerate().filter(|(_,s)|*s==old).map(|(i,_)|i).collect()}
pub fn run(ops:Vec<Op>)->Vec<Op>{
 let(nq,nb,_,regs)=analyze_ops(ops.iter());assert_eq!(nq,1234);assert_eq!(nb,45701);assert_eq!(regs.len(),4);assert!(regs.iter().all(|r|r.len()==256));
 let mut found=Vec::new();for(j,(old,new))in specs().into_iter().enumerate(){let m=&META[j];static_contract(&old,&new,m);let pos=matches(&ops,&old);assert_eq!(pos.len(),1,"entire source-defined flag family missing/edited/ambiguous");let at=pos[0];let zeros=prefix_zeros(&ops,at,nq as usize,nb as usize,&regs);for q in m.scratch{assert_eq!(zeros[*q as usize],0,"flag comparator carry not proved zero");}eprintln!("QUANTUM_FLAG_BORROW site={j} at={at} addedT_guarded=1 addedQ=0 addedMR=1");found.push((at,old,new));}
 found.sort_by_key(|s|s.0);for pair in found.windows(2){assert!(pair[0].0+pair[0].1.len()<=pair[1].0,"flag family overlap");}
 let mut out=Vec::with_capacity(ops.len()+192);let mut cursor=0;for(at,old,new)in found{out.extend_from_slice(&ops[cursor..at]);out.extend_from_slice(&new);cursor=at+old.len();}out.extend_from_slice(&ops[cursor..]);let(nq2,nb2,_,regs2)=analyze_ops(out.iter());assert_eq!(nq,nq2);assert_eq!(nb2,nb+1);assert_eq!(regs,regs2);out
}
#[cfg(test)]mod tests{use super::*;
 #[test]fn twelve_complete_contracts(){for(j,(a,b))in specs().iter().enumerate(){static_contract(a,b,&META[j]);}}
 #[test]fn changed_region_fails_unique_match(){for(a,_)in specs(){let mut b=a.clone();b[0].q_target=QubitId(0);assert!(matches(&b,&a).is_empty());}}
 #[test]fn ambiguity_detected(){let(a,_)=specs().remove(0);let mut b=a.clone();b.extend_from_slice(&a);assert_eq!(matches(&b,&a).len(),2);}
 #[test]#[should_panic]fn changed_original_mr_rejected(){let(a,mut b)=specs().remove(0);b[0].c_target=BitId(123);static_contract(&a,&b,&META[0]);}
 #[test]#[should_panic]fn extra_capacity_rejected(){let(a,mut b)=specs().remove(0);b[3].q_target=QubitId(1234);static_contract(&a,&b,&META[0]);}
 #[test]fn zero_rules_conservative(){assert_eq!(and(0,-1),0);assert_eq!(store(0,-1,0),0);assert_eq!(xor(-1,-1),-1);}
}
'''
(r/'quantum_flag.rs').write_text(head+decode+helpers+spec+body)
tip=r.parent/'product-exact-20261015/tip';dest=r/'candidate';rev='4b2ec52fc55da796aa8f5ef851290297e8706424';assert subprocess.check_output(['git','-C',str(tip),'rev-parse','HEAD'],text=True).strip()==rev
(r/'base-status.txt').write_bytes(subprocess.check_output(['git','-C',str(tip),'status','--short']));subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(dest),rev],check=True)
for name in ['quantum_flag.rs','quantum_flag.bin']:shutil.copy2(r/name,dest/'src/point_add'/name)
p=dest/'src/point_add/mod.rs';s=p.read_text();needle='    ops = apply_tail_nonce(ops, nonce);';assert s.count(needle)==1;p.write_text('mod quantum_flag;\n'+s.replace(needle,needle+'\n    ops = quantum_flag::run(ops);'))
subprocess.run(['git','-C',str(dest),'add','-N','src/point_add/quantum_flag.rs','src/point_add/quantum_flag.bin'],check=True)
(r/'candidate-source.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(r/'candidate-source.json').write_text(json.dumps(dict(base=rev,only_point_add=True,original_table_assertions_retained=True,all12_family_admitted=True,files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
(r/'guard-tests.rs').write_text('#[path="candidate/src/circuit.rs"] mod circuit;\n#[path="quantum_flag.rs"] mod quantum_flag;\n')
print('Prepared whole point_add candidate, all12 frozen sites; universal proofs and original-prefix scratch zeros required')
