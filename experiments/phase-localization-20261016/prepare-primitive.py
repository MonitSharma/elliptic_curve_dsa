from pathlib import Path
import shutil,hashlib,json
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016');pref=r.parent/'prefilter-20261015/tool/src';s=r/'tool/src';(s/'bin').mkdir(exist_ok=True)
for name in['input_anf_dag_trace.rs','global_rng_anf_retained_masks.rs']:shutil.copy2(pref/name,s/name)
prefix=(s/'main.rs').read_text().split('mod observed;')[0]
(s/'bin/phase_primitive.rs').write_text(prefix+'\ninclude!("../input_anf_dag_trace.rs");\ninclude!("../global_rng_anf_retained_masks.rs");\ninclude!("../phase_primitive_body.rs");\n')
shutil.copy2(r/'phase_primitive_body.rs',s/'phase_primitive_body.rs')
(r/'primitive-source-hashes.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[s/'input_anf_dag_trace.rs',s/'global_rng_anf_retained_masks.rs',s/'phase_primitive_body.rs',s/'bin/phase_primitive.rs']},indent=2)+'\n')
