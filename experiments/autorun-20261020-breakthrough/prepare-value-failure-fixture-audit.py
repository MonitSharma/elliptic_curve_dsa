"""Use preserved failing scalars to test filter usefulness, never to alter a circuit."""
import gzip,hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2];ex=root/'experiments';old=ex/'breakthrough-value-curve-audit-v2-20261020';r=ex/'breakthrough-value-failure-fixture-audit-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
fixtures=[];source=ex/'breakthrough-public-best-drop-final-gate-20261020/candidate.jsonl.gz'
with gzip.open(source,'rt')as rows:
 for line in rows:
  row=json.loads(line)
  for failure in row['failures']:
   if failure['value']:fixtures.append({'batch':row['batch'],'lane':failure['lane'],'k1':failure['k1'],'k2':failure['k2']})
   if len(fixtures)==128:break
  if len(fixtures)==128:break
assert len(fixtures)==128;data=(json.dumps(fixtures,indent=2)+'\n').encode();(r/'FAILURE-FIXTURES.json').write_bytes(data);(t/'FAILURE-FIXTURES.json').write_bytes(data)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
for n in ['io.rs','Cargo.lock']:shutil.copyfile(old/'local-tool'/n,t/n)
s=(old/'audit.rs').read_text();needle='let rounds=optimize(&mut p,&outputs);';assert s.count(needle)==1;s=s.replace(needle,'let rounds:Vec<(usize,usize,usize)>=vec![];')
start=s.index('fn curve_abstract_audit(');end=s.index('struct AuditWords',start);body=s[start:end]
needle='let mut rows=vec![];';assert body.count(needle)==1;body=body.replace(needle,needle+'let fixtures:Vec<serde_json::Value>=serde_json::from_str(include_str!("FAILURE-FIXTURES.json")).unwrap();assert_eq!(fixtures.len(),128);')
body=body.replace('for batch in 0..32','for batch in 0..2')
needle='let mut rb=[[0u8;32];2];';pos=body.index(needle);last=body.index('let a=curve.mul',pos)
body=body[:pos]+'''let fixture=&fixtures[batch*64+inputs.len()];let k1=fixture["k1"].as_str().unwrap().parse().unwrap();let k2=fixture["k2"].as_str().unwrap().parse().unwrap();'''+body[last:]
pos=body.index('inputs.push(serde_json::json!(');last=body.index('));}',pos)+3
body=body[:pos]+'inputs.push(fixture.clone());'+body[last:]
body=body.replace('value-valid-curve-source-audit-20261020-v1','value-known-failure-source-audit-20261020-v1').replace('"input_batches":32,"shots":2048,"protected_fullstream_value_comparisons":96','"input_batches":2,"shots":128,"protected_fullstream_value_comparisons":6').replace('Verification-only fixtures on valid secp256k1 points','First128 preserved value-failing scalars from old finalgate, verification-only fixtures on valid secp256k1 points. Raw captured-SSA IR without static optimization; no circuit edits or rerun of a gate verdict')
s=s[:start]+body+s[end:];(r/'audit.rs').write_text(s);(t/'audit.rs').write_text(s)
manifest=(old/'local-tool/Cargo.toml').read_text().replace('name="value_curve_audit"','name="value_failure_fixture_audit"');(t/'Cargo.toml').write_text(manifest)
freeze=json.loads((old/'SOURCE-FREEZE.json').read_bytes());freeze['source_files']={n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs','FAILURE-FIXTURES.json']};freeze.update(scope='Verification-only fixed known-failure corpus; old circuit frozen, unchanged gate verdict and nonce selection. No static IR optimization needed; numeric sound certificates only. Not a resource score, statistical census or submission.',fixture_provenance={'file':source.relative_to(root).as_posix(),'compressed_file_sha256':sha(source.read_bytes()),'selection':'First128 value-failing shot records in ascending existing batch/lane order; no circuit or nonce tuning','fixtures_sha256':sha(data)});(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
for n in ['run-local.sh','launch-local.sh']:
 s=(old/n).read_text().replace(old.name,r.name).replace('value_curve_audit','value_failure_fixture_audit');(r/n).write_bytes(s.encode())
shutil.copyfile(old/'verify-input.py',r/'verify-input.py')
(r/'PLAN.md').write_text('''# Exact filter certificates on preserved failure fixtures

Freeze first128 value-failing scalar pairs from old candidate finalgate in
ascending batch/lane order. The old source and gate verdict remain unchanged.
These are independent verification controls, not a new census or resampling a
statistical verdict. No circuit/nonce modified. Raw captured-SSA value IR, no
static optimizer in main, preserves all old phase-omission qualifications.
21native controls retained;6fullsource protected value comparisons (three RNG
patterns x two64lane batches). Reference points/expected P+A from protected
curve; every abstractwrong mask must be a subset of every concretewrong mask.
Any future nonce rejection requires independent originalFS/source qualification;
this audit alone screens/rejects zero nonces. IR counts never scored.
''')
print(r.name,'128 preserved scalar pairs frozen')
