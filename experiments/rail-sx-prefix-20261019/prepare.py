import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'product-parent-sat-20261019/parent4-filter';helper=ws/'rail-sx-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert (helper/'branch.exit').read_text().strip()=='0'
result=json.loads((helper/'RESULT-BRANCH.json').read_text());assert result['status']=='EXACT_BRANCH_SX_AND_ADVISORY_FLAGS_VERIFIED'
lib=helper/'libbranch.so';assert sha(lib)==result['library_sha256']=='405d6698d4b34f6a7316c9e6a040b68c41fb370c6deb2ccebdc1dd0b0a8a4b58'
assert json.loads((old/'RESULT.json').read_text())['status']=='DISABLED_PARENT4_PIPELINE_QUALIFICATION_PASS'
gate=json.loads((ws/'product-pareto-20261019/parent4-qualification/RESULT.json').read_text());assert gate['status']=='FAILURE_GATE_PASS' and all(gate['rules'].values())
assert sha(ws/'product-pareto-20261019/candidate-parent4/ops.bin')==gate['stream_sha256']['candidate']=='9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a'
tool=r/'tool';assert not tool.exists();shutil.copytree(old/'tool/src',tool/'src')
for name in ['Cargo.toml','Cargo.lock']:shutil.copy2(old/'tool'/name,tool/name)
p=tool/'src/rail_fast_ffi.rs';s=p.read_text();before='let path=CString::new("/home/hclau/ecdsa_research/rail-masks-20261016/librail8_masks.so").unwrap();';assert s.count(before)==1
after='sha_check('+json.dumps(str(lib))+','+json.dumps(sha(lib))+');let path=CString::new('+json.dumps(str(lib))+').unwrap();';p.write_text(s.replace(before,after))
audit={}
for p in tool.rglob('*'):
    if not p.is_file():continue
    name=p.relative_to(tool).as_posix();expected=(old/'tool'/name).read_text()
    if name=='src/rail_fast_ffi.rs':expected=expected.replace(before,after)
    assert p.read_text()==expected,name;audit[name]={'sha256':sha(p),'change':'Exact advisory library path and explicit library hash only' if name=='src/rail_fast_ffi.rs' else 'Byte/normalized-text identical to qualified disabled parent4 tool'}
assert 'const PROOF_ACCEPTED:bool=false;' in (tool/'src/packed_body.rs').read_text()
(r/'PREPARATION.json').write_text(json.dumps({'status':'DISABLED_HELPER_ONLY_RUNTIME_COPY','files':audit,'helper_library_sha256':sha(lib),'old_qualified_prefix_sha256':sha(old/'baseline-0.jsonl'),'baseline_binary_sha256':sha(old/'tool/target/release/value_prefilter'),'source_circuit_unchanged':True,'parent4_gate_rerun':False,'new_candidate_nonce_tests':False,'authoritative_rejection':False,'operational_acceptance':False},indent=2)+'\n')
