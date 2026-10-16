from pathlib import Path
import shutil,json
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016');old=r.parent/'back-seam-repair-20261016/tool';new=r/'proof-tool'
shutil.copytree(old,new,ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
s=new/'src'
prefix=(old/'src/bin/phase_primitive.rs').read_text().split('include!')[0]
(s/'bin/quantum_phase.rs').write_text(prefix+'include!("../input_anf_dag_trace.rs");\ninclude!("../global_rng_anf_retained_masks.rs");\ninclude!("../phase_bdd.rs");\ninclude!("../quantum_phase_body.rs");\n')
body=(old/'src/phase_primitive_body.rs').read_text()
needle='let prepend=if ops[2].kind==X';assert body.count(needle)==1
body=body.replace(needle,'let lower:Option<(usize,usize,usize)>=if args.len()>3{let v:Vec<usize>=args[3].split(\',\').map(|x|x.parse().unwrap()).collect();assert_eq!(v.len(),3);Some((v[0],v[1],v[2]))}else{None};let prepend=if lower.is_none()&&ops[2].kind==X')
body=body.replace('let mut cursor=2+2*usize::from(prepend.is_some());','let mut cursor=2+2*usize::from(prepend.is_some())+8*usize::from(lower.is_some());')
body=body.replace('.filter(|o|o.kind==CCX).map(','.filter(|o|o.kind==CCX&&o.q_target.0 as usize!=measured).map(')
needle='let mut carry=if let Some((w,bit,invert))=prepend';assert body.count(needle)==1
body=body.replace(needle,'let mut carry=if let Some((la,lb,ls))=lower{let x=a.not(&initial[la]);let y=initial[lb].clone();let z=initial[ls].clone();let xy=a.and(&x,&y);let xz=a.and(&x,&z);let yz=a.and(&y,&z);let w=a.xor(&xy,&xz);a.xor(&w,&yz)}else if let Some((w,bit,invert))=prepend')
body=body.replace('let mut ordered=Vec::new();','let mut ordered=Vec::new();if let Some((la,lb,ls))=lower{ordered.extend([ls,la,lb]);}')
needle='let mut ci=if let Some((w,bit,invert))=prepend';assert body.count(needle)==1
body=body.replace(needle,'let mut ci=if let Some((la,lb,ls))=lower{let x=!iq[la];let y=iq[lb];let z=iq[ls];(x&y)^(x&z)^(y&z)}else if let Some((w,bit,invert))=prepend')
body=body.replace('"classical_prepend":prepend,','"classical_prepend":prepend,"quantum_majority_lower_frame":lower,')
body=body.replace('"not_a_repair":true','"not_a_repair":false')
# Paired protected simulation additionally checks every quantum and original
# classical bit, using identical original MR draws plus one independent new draw.
needle='s.apply_iter(ops.iter());assert_eq!(s.phase'
assert body.count(needle)==1
body=body.replace(needle,'s.apply_iter(ops.iter());if lower.is_some()&&args[1].contains("new-flag-"){let old_path=args[1].replacen("new-flag-","old-flag-",1);let old_ops=load_ops(&old_path).unwrap();let mut old_rng=seeded(seed);let mut old_sim=Simulator::new(nq as usize,nb as usize,&mut old_rng);old_sim.qubits.copy_from_slice(&iq);old_sim.bits.copy_from_slice(&ib);old_sim.phase=0x94d049bb133111eb;old_sim.apply_iter(old_ops.iter());assert_eq!(s.qubits,old_sim.qubits,"paired entire quantum state changed");assert_eq!(&s.bits[..45701],&old_sim.bits[..45701],"paired original classical state changed");}assert_eq!(s.phase')
body=body.replace('"protected_arbitrary_bitplane_cases":numeric_cases,','"protected_arbitrary_bitplane_cases":numeric_cases,"protected_paired_every_q_and_original_bit":lower.is_some()&&args[1].contains("new-flag-"),')
# A theorem failure must be a process failure, including the deliberate wrong-CZ controls.
body=body.replace('println!("{}",serde_json::json!', 'assert!(proved_phase&&unresolved.is_empty()&&a.capped==0,"exact quantum-borrow phase/value contract not proved");println!("{}",serde_json::json!')
(s/'quantum_phase_body.rs').write_text(body)
(r/'quantum-proof-source-hashes.json').write_text(json.dumps({str(p.relative_to(new)):__import__('hashlib').sha256(p.read_bytes()).hexdigest()for p in s.rglob('*.rs')},indent=2)+'\n')
print('Prepared private quantum lower-MAJ theorem: arbitrary operands/classical bits/all MR; declared comparator carries zero')
