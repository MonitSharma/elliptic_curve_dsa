"""Port only candidate bindings into the previously reviewed operational tool."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
old=ws/'plain67-operational-20261016/tool'
qa=ws/'product67-filter-20261016/tool';qb=ws/'product-parent-sat-20261019/parent4-filter/tool'
proof=ws/'product-parent-sat-20261019';tool=r/'tool'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (proof/'parent4-filter/filter.exit').read_text().strip()=='0'
assert json.loads((qb.parent/'RESULT.json').read_text())['status']=='DISABLED_PARENT4_PIPELINE_QUALIFICATION_PASS'
assert json.loads((proof/'PUBLIC-PARENT-TRANSFER.json').read_text())['status']=='PUBLIC_PARENT_EXTENSION_UNIVERSAL_AUDIT_PASS'
assert not tool.exists()
shutil.copytree(old/'src',tool/'src')
for name in ('Cargo.toml','Cargo.lock'):
    assert (old/name).read_bytes()==(qb/name).read_bytes()
    shutil.copyfile(old/name,tool/name)
replacements=[('268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d','9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a'),
              ('assert_eq!(n,17_891_821)','assert_eq!(n,17_889_606)')]
def bindings(s):
    for a,b in replacements:
        assert s.count(a)==1;s=s.replace(a,b)
    return s
assert bindings((qa/'src/packed_body.rs').read_text())==(qb/'src/packed_body.rs').read_text()
(tool/'src/packed_body.rs').write_text(bindings((old/'src/packed_body.rs').read_text()))
assert (old/'src/transfer.rs').read_bytes()==(qa/'src/transfer.rs').read_bytes()
prep=json.loads((qb.parent/'PREPARATION.json').read_text())
required=prep['additional_proof_artifacts']
assert all(sha(Path(p))==h for p,h in required.items())
extra=''.join(' sha_check('+json.dumps(p)+','+json.dumps(h)+');\n' for p,h in required.items())
original=(qa/'src/transfer.rs').read_text();assert original.count('fn bind_transfer(){')==1
assert original.replace('fn bind_transfer(){','fn bind_transfer(){\n'+extra)==(qb/'src/transfer.rs').read_text()
shutil.copyfile(qb/'src/transfer.rs',tool/'src/transfer.rs')
search=(old/'src/search.rs').read_text();assert search.count(replacements[0][0])==1
search=search.replace(*replacements[0]);assert search==(r/'search.rs').read_text()
(tool/'src/search.rs').write_text(search)
report={}
for p in sorted(tool.rglob('*')):
    if not p.is_file():continue
    name=str(p.relative_to(tool))
    if name not in ('src/packed_body.rs','src/transfer.rs','src/search.rs'):
        assert p.read_bytes()==(old/name).read_bytes(),name
        report[name]={'scope':'IDENTICAL_TO_REVIEWED_PLAIN67_OPERATIONAL_TOOL','sha256':sha(p)}
        continue
    expected=(old/name).read_text()
    if name=='src/packed_body.rs':expected=bindings(expected);label='CANDIDATE_HASH_AND_OPCOUNT_ONLY'
    elif name=='src/transfer.rs':expected=(qb/name).read_text();label='QUALIFIED_TRANSFER_HASH_BINDINGS_ONLY'
    elif name=='src/search.rs':expected=expected.replace(*replacements[0]);label='CANDIDATE_BINDING_ONLY'
    else:label='IDENTICAL_TO_REVIEWED_PLAIN67_OPERATIONAL_TOOL'
    assert p.read_text()==expected,name
    report[name]={'scope':label,'sha256':sha(p)}
(r/'TOOL_DIFF_AUDIT.json').write_text(json.dumps({'status':'ONLY_PARENT4_QUALIFIED_BINDINGS_DIFFER','files':report,
    'qualified_filter_preparation_sha256':sha(qb.parent/'PREPARATION.json'),'reviewed_operational_tool':str(old)},indent=2)+'\n')
print('Operational source differs only in qualified parent4 bindings',flush=True)
