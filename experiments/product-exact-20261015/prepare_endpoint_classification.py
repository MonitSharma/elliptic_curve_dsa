"""Separate read-only refinement of the completed endpoint census, no renderer."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;old=r/'endpoint-census-tool';tool=r/'endpoint-classification-tool';d=r/'endpoint-classification-20261016'
assert (r/'endpoint-source-census-20261016/launcher.exit').read_text().strip()=='0'
assert not tool.exists() and not d.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((r/'endpoint-source-census-20261016/DECLARATION.json').read_text())
stream=r/plan['stream'];assert sha(stream)==plan['stream_sha256']
shutil.copytree(old,tool,ignore=shutil.ignore_patterns('target'))
p=tool/'src/endpoint_census.rs';s=p.read_text()
before='let mut recovered=0;'
after='let mut recovered=0;let(mut constant_zero,mut constant_one,mut nonconstant)=(0usize,0usize,0usize);let mut nonconstant_groups=BTreeSet::new();'
assert s.count(before)==1;s=s.replace(before,after)
before='recovered+=1;if recovered<=20{'
after='recovered+=1;if before.1.is_empty(){if before.0{constant_one+=1;}else{constant_zero+=1;}}else{nonconstant+=1;nonconstant_groups.insert(before.clone());println!("RECOVERED_NONCONSTANT at={at} end={i} controls={},{}",ops[at].q_control1.0,ops[at].q_control2.0);}if recovered<=20{'
assert s.count(before)==1;s=s.replace(before,after)
before='assert!(expected.is_empty());println!'
after='assert!(expected.is_empty());assert_eq!(recovered,constant_zero+constant_one+nonconstant);println!("ENDPOINT_CLASSIFICATION constant_zero={constant_zero} constant_one={constant_one} nonconstant={nonconstant} distinct_nonconstant_groups={} numerical_executed_T_saving=UNKNOWN source_only=true",nonconstant_groups.len());println!'
assert s.count(before)==1;s=s.replace(before,after);p.write_text(s)
d.mkdir();declaration=dict(status='PREDECLARED_READ_ONLY_ENDPOINT_CLASSIFICATION_NO_GENERATOR',stream=plan['stream'],stream_sha256=plan['stream_sha256'],input_census_declaration_sha256=sha(r/'endpoint-source-census-20261016/DECLARATION.json'),input_census_result_sha256=sha(r/'endpoint-source-census-20261016/RESULTS.json'),atom_cap=1024,pair_cap=64,product_cap=1000000,workers=1,address_limit_GiB=24,time_limit_seconds=7200,sampled_inputs=0,emits_stream=False,purpose='Separate constant-zero/constant-one/nonconstant recovered products and list all nonconstant endpoint positions. No donor allocation, guard reachability, first-use profitability or executed T claim.',source_files_sha256={str(p.relative_to(tool)):sha(p) for p in tool.rglob('*') if p.is_file()})
(d/'DECLARATION.json').write_text(json.dumps(declaration,indent=2)+'\n');print(json.dumps(declaration))
