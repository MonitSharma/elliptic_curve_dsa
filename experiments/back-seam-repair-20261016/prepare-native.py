from pathlib import Path
import json,subprocess,hashlib,shutil
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');sites=json.loads((r/'regions-C.json').read_text());front=(r.parent/'seam-phase-repair-20261016/front_seam.rs').read_text();assert len(sites)==2
for j,s in enumerate(sites):
 for mode in ['old','new']:
  p=json.loads((r/f'{mode}-phase-contract-{j}.json').read_text());assert p['phase_contract_proved']and not p['q_contract_unresolved']and p['mr']==39 and p['outer_caps']==0
 assert(r/f'negative-phase-contract-{j}.exit').read_text().strip()=='101'
 assert json.loads((r/f'middle-interface-{j}.json').read_text())['proved']
 q=json.loads((r/'prefix-zero-receipt.json').read_text())['results'];assert all(not row['unresolved']for row in q if row['site']==j and row['kind']!='R5 auxiliary')
head='//! Both source-defined back-seam comparisons gain one classical-source bit.\n//! All inherited checks run first. R5 entry arithmetic cleanliness remains unresolved;\n//! this pass claims only exact local interfaces and higher comparator precision.\nuse crate::circuit::{Op,OperationType as K,QubitId,BitId,RegisterId,QubitOrBit,analyze_ops};\nuse std::collections::BTreeSet;\nconst NONE:u64=u64::MAX;\n'
decode=front[front.index('fn decode'):front.index('fn spec')]
spec=front[front.index('fn spec'):front.index('fn quantum')].replace('fn spec()->','fn spec(data:&[u8])->').replace('DATA','data').replace('FRONTSE1','BACKSEA1').replace('m,n+4','m,n+6')
helpers=front[front.index('fn quantum'):front.index('pub fn run')].replace('front seam','back seams')
decl='const DATA:[&[u8];2]=[include_bytes!("back-seam-0.bin"),include_bytes!("back-seam-1.bin")];\nstruct Meta{component:usize,tv_load:usize,carries:&\'static[u64],v:&\'static[u64],cb:&\'static[u64]}\nconst META:[Meta;2]=[\n'
for j,s in enumerate(sites):
 carries=json.loads((r/f'new-phase-contract-{j}.json').read_text())['clean_scratch_preconditions'];decl+=f'Meta{{component:{s["component_offset"]},tv_load:{s["tv_load_offset"]},carries:&{carries},v:&{s["v"]},cb:&{s["cb"]}}},\n'
decl+='];\n'
run='''
fn matches(ops:&[Op],old:&[Op])->Vec<usize>{ops.windows(old.len()).enumerate().filter(|(_,s)|*s==old).map(|(i,_)|i).collect()}
pub fn run(ops:Vec<Op>)->Vec<Op>{
 let(nq,nb,_,regs)=analyze_ops(ops.iter());assert_eq!(regs.len(),4);assert!(regs.iter().all(|r|r.len()==256));
 let mut sites=Vec::new();
 for j in 0..2{let(old,new)=spec(DATA[j]);static_contract(&old,&new);let found=matches(&ops,&old);assert_eq!(found.len(),1,"both-back-seam complete region missing/changed/ambiguous");let at=found[0];let m=&META[j];
  for (offset,wires)in[(m.tv_load,m.v),(m.component,m.carries)]{let q=prefix_zeros(&ops,at+offset,nq as usize,nb as usize,&regs);for w in wires{assert_eq!(q[*w as usize],0,"back-seam required comparison scratch not proved zero");}}
  assert!(old.iter().all(|o|!(matches!(o.kind,K::Hmr|K::BitInvert|K::BitStore0|K::BitStore1)&&m.cb.contains(&o.c_target.0))),"back-seam classical source changed");
  eprintln!("BACK_SEAMS_CLASSICAL_BORROW site={j} at={at} bits20to21 extraT=0 extraQ=0 extraMR=0 inherited_R5_limit_retained=true");sites.push((at,old,new));
 }
 sites.sort_by_key(|s|s.0);assert!(sites[0].0+sites[0].1.len()<=sites[1].0,"back-seam overlap");let mut out=Vec::with_capacity(ops.len()+12);let mut cursor=0;for(at,old,new)in sites{out.extend_from_slice(&ops[cursor..at]);out.extend_from_slice(&new);cursor=at+old.len();}out.extend_from_slice(&ops[cursor..]);out
}
#[cfg(test)]mod tests{use super::*;
 #[test]fn both_complete_static_interfaces(){for data in DATA{let(a,b)=spec(data);static_contract(&a,&b);}}
 #[test]fn unique_regions_and_changed_region_rejected(){for data in DATA{let(mut a,_)=spec(data);assert_eq!(matches(&a,&a),vec![0]);let original=a.clone();a[3].q_target=QubitId(1233);assert!(matches(&a,&original).is_empty());}}
 #[test]fn ambiguous_region_detected(){let(a,_)=spec(DATA[0]);let mut b=a.clone();b.extend_from_slice(&a);assert_eq!(matches(&b,&a).len(),2);}
 #[test]#[should_panic]fn extra_qubit_rejected(){let(a,mut b)=spec(DATA[0]);b[1].q_target=QubitId(99999);static_contract(&a,&b);}
 #[test]#[should_panic]fn measurement_sequence_rejected(){let(a,mut b)=spec(DATA[0]);let i=b.iter().position(|o|o.kind==K::Hmr).unwrap();b[i].c_target=BitId(99999);static_contract(&a,&b);}
 #[test]#[should_panic]fn extra_toffoli_rejected(){let(a,mut b)=spec(DATA[0]);b.push(*a.iter().find(|o|o.kind==K::CCX).unwrap());static_contract(&a,&b);}
 #[test]fn conservative_snapshot_and_zero_rules(){assert_eq!(store(0,-1,0),0);assert_eq!(and(0,-1),0);assert_eq!(store(-1,1,0),0);}
}
'''
(r/'back_seams.rs').write_text(head+decode+spec+helpers+decl+run)
tip=r.parent/'product-exact-20261015/tip';dest=r/'candidate';rev=json.loads((r/'PREDECLARED.json').read_text())['source_revision'];assert subprocess.check_output(['git','-C',str(tip),'rev-parse','HEAD'],text=True).strip()==rev
(r/'base-status.txt').write_bytes(subprocess.check_output(['git','-C',str(tip),'status','--short']));subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(dest),rev],check=True)
for name in ['back_seams.rs','back-seam-0.bin','back-seam-1.bin']:shutil.copy2(r/name,dest/'src/point_add'/name)
p=dest/'src/point_add/mod.rs';s=p.read_text();needle='    ops = apply_tail_nonce(ops, nonce);';assert s.count(needle)==1;p.write_text('mod back_seams;\n'+s.replace(needle,needle+'\n    ops = back_seams::run(ops);'))
subprocess.run(['git','-C',str(dest),'add','-N','src/point_add/back_seams.rs','src/point_add/back-seam-0.bin','src/point_add/back-seam-1.bin'],check=True)
(r/'candidate-source.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(r/'candidate-source.json').write_text(json.dumps(dict(base=rev,only_point_add=True,original_tables_assertions_retained=True,admission=json.loads((r/'ADMISSION-D.json').read_text()),files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
(r/'guard-tests.rs').write_text('#[path="candidate/src/circuit.rs"] mod circuit;\n#[path="back_seams.rs"] mod back_seams;\n')
