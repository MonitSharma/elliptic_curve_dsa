"""Prepare a source-only endpoint census. This emits no rewritten circuit.

Run only after frozen product95 and a fresh resource check. A zero result ends
this method; a positive result still needs a separately admitted generator and
independent universal checker before any candidate or full-input sampling.
"""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'endpoint-source-census-20261016';tool=r/'endpoint-census-tool'
assert not tool.exists() and not (d/'DECLARATION.json').exists()
freeze=json.loads((r/'PRODUCT95_FREEZE.json').read_text());stream=r/freeze['external_stream']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(stream)==freeze['external_stream_sha256']
shutil.copytree(r/'flags-tool',tool,ignore=shutil.ignore_patterns('target'))
(tool/'src/endpoint_census.rs').write_text((r/'endpoint_census.rs.in').read_text())
p=tool/'src/main.rs';s=p.read_text();at=s.index('fn main(){');s=s[:at]+'''mod endpoint_census;
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);
 let ops=load_ops(&args[1]).unwrap();endpoint_census::analyze(&ops);
}
''';p.write_text(s)
d.mkdir(exist_ok=True)
plan=dict(status='PREDECLARED_SOURCE_ONLY_CENSUS_NOT_A_GENERATOR',stream=str(stream.relative_to(r)),stream_sha256=sha(stream),source_freeze_sha256=sha(r/'PRODUCT95_FREEZE.json'),family='retained',atom_cap=1024,pair_cap=64,product_cap=1000000,workers=1,address_limit_GiB=24,time_limit_seconds=7200,uses_no_inputs_or_measurement_packets=True,emits_no_new_stream=True,endpoint_rule='At every raw-write-rejected last use in a repeated-product group, compare last-use product and cleanup product within one immutable-ID Support instance; query every CCX, sort endpoint queries. The group equality is separately established within the first Support pass; no IDs are compared across passes.',stop_rule='If zero endpoints recover, stop this method without a generator. A positive count only authorizes investigating source-derived proposals; no candidate or correctness claim is made.',source_files_sha256={str(p.relative_to(tool)):sha(p) for p in tool.rglob('*') if p.is_file() and 'target' not in p.relative_to(tool).parts})
(d/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan),flush=True)
