import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;old=r/'loan-normal-forms-tool';tool=r/'loan-affine-factors-tool';d=r/'loan-affine-factors-20261016'
assert (r/'loan-normal-forms.exit').read_text().strip()=='0';assert not tool.exists() and not d.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copytree(old,tool,ignore=shutil.ignore_patterns('target'));p=tool/'src/support.rs';p.write_text(p.read_text()+'\n'+(r/'loan_affine_factors.rs.in').read_text())
p=tool/'src/main.rs';s=p.read_text();assert s.count('state.dirty_rhs_queries(&eligible,&targets)')==1;s=s.replace('state.dirty_rhs_queries(&eligible,&targets)','state.dirty_affine_factor_queries(&eligible,&targets)');p.write_text(s)
d.mkdir();shutil.copy2(r/'loan-normal-forms-20261016/n2-loan-family.json',d/'n2-loan-family.json');oldplan=json.loads((r/'loan-normal-forms-20261016/DECLARATION.json').read_text())
plan=dict(status='PREDECLARED_EXISTING_INVERSE_FACTORS_AFFINE_SPAN_SOURCE_ONLY',stream=oldplan['stream'],stream_sha256=oldplan['stream_sha256'],family_sha256=oldplan['family_sha256'],parent_result_sha256=sha(r/'loan-normal-forms-20261016/RESULTS.json'),atom_cap=512,product_cap=200000,workers=1,address_limit_GiB=24,time_limit_seconds=1800,all16_dirty_targets=True,pair_enumeration=False,max_existing_factor_nodes_per_site=4096,method='Current-classical-first Gaussian span plus650fullyuntouchedq; inspect only existing inverse product IDs in dirtyforms, express both factors, then Gaussian span dirtyRHS with indexed product generators. Costs reflect quantum-factor rank0/1/2 and are feasibility upper bounds only.',stop_rule='If12nonconstantdirtytargets remain unsupported or costs unpromising, stop this cheap-factor route. No generator, candidate or sampling.',source_files_sha256={str(p.relative_to(tool)):sha(p) for p in tool.rglob('*')if p.is_file()})
(d/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan))
