"""Port only qualified source bindings; never launches a production search."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
old=ws/'parent4-operational-sat-20261019';qual=ws/'product-classical-nine-filter-20261019'
native=ws/'product-classical-nine-20261019';proof=ws/'product-classical-nine-proof-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
assert not (r/'tool').exists()
assert (qual/'qualification.exit').read_text().strip()=='0'
q=read(qual/'RESULT.json');assert q['status']=='DISABLED_CLASSICAL_NINE_PIPELINE_QUALIFICATION_PASS'
assert q['all4096_rows_identical'] and q['protected_full9024_q_b_phase_physicalMR'] and q['protected_zeroMR_shadow128_and_partial']
gate=native/'qualification/RESULT.json';g=read(gate);assert g['status']=='FAILURE_GATE_PASS' and all(g['rules'].values())
assert (native/'gate-v2.exit').read_text().strip()=='0'
h='76271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1'
assert h==sha(native/'candidate/ops.bin')==g['stream_sha256']['candidate']==q['candidate_sha256']
freeze=read(native/'SOURCE_FREEZE.json')
assert all(sha(native/'candidate'/p)==v for p,v in {**freeze['source_files'],**freeze['protected_files']}.items())
accepted=read(old/'ACCEPTANCE.json');assert all(sha(Path(p))==v for p,v in accepted['runtime_artifacts'].items())
transfer=read(proof/'TRANSFER.json');assert transfer['status']=='CLASSICAL_NINE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS'
assert all(sha(Path(p))==v for p,v in transfer['required_artifacts'].items())
prep=read(qual/'PREPARATION.json');assert all(sha(qual/'tool'/p)==v['sha256'] for p,v in prep['files'].items())
required=set(Path(p) for p in transfer['required_artifacts'])
required.update([gate,native/'qualification/DECLARATION.json',native/'SOURCE_FREEZE.json',native/'NATIVE-RECEIPT.json',proof/'TRANSFER.json',
                 qual/'RESULT.json',qual/'QUALIFICATION-START.json',qual/'PREPARATION.json',qual/'tool/target/release/value_prefilter',qual/'baseline-0.jsonl'])
tool=r/'tool';shutil.copytree(old/'tool/src',tool/'src')
for name in ['Cargo.toml','Cargo.lock']:shutil.copy2(old/'tool'/name,tool/name)
oldh='9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a'
def replace_once(s,a,b):assert s.count(a)==1,a;return s.replace(a,b)
for name in ['src/packed_body.rs','src/search.rs']:
    p=tool/name;s=replace_once(p.read_text(),oldh,h)
    if name.endswith('packed_body.rs'):s=replace_once(s,'assert_eq!(n,17_889_606)','assert_eq!(n,17_889_627)')
    p.write_text(s)
p=tool/'src/transfer.rs';s=p.read_text();needle='fn bind_transfer(){';assert s.count(needle)==1
extra=''.join(' sha_check('+json.dumps(str(p))+','+json.dumps(sha(p))+');\n' for p in sorted(required))
p.write_text(s.replace(needle,needle+'\n'+extra))
audit={}
for p in tool.rglob('*'):
    if not p.is_file():continue
    name=p.relative_to(tool).as_posix();expected=(old/'tool'/name).read_text()
    if name in ['src/packed_body.rs','src/search.rs']:
        expected=replace_once(expected,oldh,h)
        if name=='src/packed_body.rs':expected=replace_once(expected,'assert_eq!(n,17_889_606)','assert_eq!(n,17_889_627)')
    if name=='src/transfer.rs':expected=expected.replace(needle,needle+'\n'+extra)
    assert p.read_text()==expected,name
    audit[name]={'sha256':sha(p),'scope':'candidate hash/opcount only' if name=='src/packed_body.rs' else 'candidate hash only' if name=='src/search.rs' else 'append qualified evidence bindings only' if name=='src/transfer.rs' else 'identical to reviewed parent4 operational tool'}
(r/'TOOL_DIFF_AUDIT.json').write_text(json.dumps({'status':'ONLY_QUALIFIED_CLASSICAL_NINE_BINDINGS_DIFFER','files':audit,'additional_runtime_artifacts':{str(p):sha(p) for p in sorted(required)},'qualified_gate_sha256':sha(gate),'source_policy':'Frozen source; ascending from1; first full pass only; no score selection; queue mode'},indent=2)+'\n')
print('Operational source prepared with only qualified bindings; no search launched')
