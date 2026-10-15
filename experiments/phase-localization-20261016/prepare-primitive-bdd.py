from pathlib import Path
import shutil,hashlib,json
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016');s=r/'tool/src'
shutil.copy2(s/'phase_primitive_body.rs',r/'phase_primitive_body-before-bdd.rs')
body=(r/'phase_primitive_body.rs').read_text()
old='let proved_phase=zero(&a,&difference);let mut unresolved='
new='let anf_proved_phase=zero(&a,&difference);let mut order=std::collections::BTreeMap::new();let mut ordered=Vec::new();if let Some(w)=borrow{ordered.push(w);}for j in 0..n{ordered.push(u[j]);ordered.push(v[j]);}ordered.push(measured);for w in ordered{let id=initial[w].0[0].1;let rank=order.len()as u32;order.entry(id).or_insert(rank);}let(bdd,coefficient_roots)=Bdd::coefficients(&a.dag,&order);let proved_phase=difference.0.iter().all(|(_,c)|coefficient_roots[*c as usize]==0);let mut unresolved='
assert body.count(old)==1;body=body.replace(old,new)
body=body.replace('"phase_contract_proved":proved_phase,','"phase_contract_proved":proved_phase,"anf_coefficient_equality_proved":anf_proved_phase,"independent_bdd_nodes":bdd.nodes.len(),"independent_bdd_checks_every_input_dag_union":true,')
(s/'phase_primitive_body.rs').write_text(body)
p=s/'bin/phase_primitive.rs';text=p.read_text();text=text.replace('include!("../phase_primitive_body.rs");','include!("../phase_bdd.rs");\ninclude!("../phase_primitive_body.rs");');p.write_text(text)
shutil.copy2(r/'phase_bdd.rs',s/'phase_bdd.rs')
(r/'primitive-bdd-source-hashes.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[s/'phase_bdd.rs',s/'phase_primitive_body.rs',s/'bin/phase_primitive.rs']},indent=2)+'\n')
