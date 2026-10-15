from pathlib import Path
import shutil,json,hashlib,struct
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');s=r/'tool/src';old=r.parent/'seam-phase-repair-20261016/tool'
for name in['input_anf_dag_trace.rs','global_rng_anf_retained_masks.rs','phase_bdd.rs']:shutil.copy2(old/'src'/name,s/name)
prefix=(old/'src/bin/phase_primitive.rs').read_text().split('include!')[0];(s/'bin/phase_primitive.rs').write_text(prefix+'include!("../input_anf_dag_trace.rs");\ninclude!("../global_rng_anf_retained_masks.rs");\ninclude!("../phase_bdd.rs");\ninclude!("../phase_primitive_body.rs");\n')
body=(old/'src/phase_primitive_body.rs').read_text()
needle='let prepend=if ops[2].kind==CX&&ops[2].q_target.0 as usize==measured&&ops[2].c_condition.0!=u64::MAX{Some((ops[2].q_control1.0 as usize,ops[2].c_condition.0 as usize))}else{None};let mut cursor=2+usize::from(prepend.is_some());';assert body.count(needle)==1
body=body.replace(needle,'let prepend=if ops[2].kind==X&&ops[2].q_target.0 as usize==measured&&ops[2].c_condition.0!=u64::MAX{assert_eq!(ops[3].kind,CX);assert_eq!(ops[3].q_target.0 as usize,measured);assert_eq!(ops[3].c_condition,ops[2].c_condition);Some((ops[3].q_control1.0 as usize,ops[2].c_condition.0 as usize,true))}else{None};let mut cursor=2+2*usize::from(prepend.is_some());')
body=body.replace('Some((w,bit))=prepend','Some((w,bit,invert))=prepend')
body=body.replace('a.and(&initial[w],&b[bit])','{let lower=if invert{a.not(&initial[w])}else{initial[w].clone()};a.and(&lower,&b[bit])}')
body=body.replace('iq[w]&ib[bit]','(if invert{!iq[w]}else{iq[w]})&ib[bit]')
(s/'phase_primitive_body.rs').write_text(body)
exec((r/'prepare-regions.py').read_text().split('raw=load(')[0])
for j,meta in enumerate(json.loads((r/'regions-C.json').read_text())):
 data=load(r/f'new-component-{j}.bin');rows=list(struct.iter_unpack('<7Q',data));index=meta['first_carry_phase_cz_local']+3;assert rows[index][0]==9 and rows[index][2]==meta['target'];row=list(rows[index]);row[2]=meta['u'][0];rows[index]=tuple(row);save(r/f'negative-wrong-clifford-{j}.bin',enc(rows))
(r/'phase-proof-source-hashes.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in s.rglob('*.rs')},indent=2)+'\n')
