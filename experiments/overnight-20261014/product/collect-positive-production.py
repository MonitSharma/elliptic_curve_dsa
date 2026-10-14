"""Collect immutable source, binary, stream, protected and packet attestations."""
from pathlib import Path
import hashlib,json,datetime
root=Path('/home/hclau/ecdsa_research/overnight-20261014');e=root/'product-evidence/positive-production';more=root/'product-evidence/positive-production-broader';checkout=root/'product-positive-production';replay=root/'product-positive-production-replay'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=json.loads((e/'receipt/receipt.json').read_text())
assert receipt['protected_tracked_changes']==[] and receipt['exit_status']==101
for f,h in receipt['source_sha256'].items():assert sha(checkout/f)==h,(f,'source changed')
for f,h in receipt['protected_sha256'].items():assert sha(checkout/f)==h,(f,'protected changed')
raw=e/'raw-ops.bin';assert sha(raw)=='f6b272fc274c47db4d5a8f135144acd00582b9cf31022d18fb48e1cd262c346a'
header=raw.open('rb').read(16);assert header[:8]==b'QECCOPSZ';assert int.from_bytes(header[8:],'little')==11319802
native=root/'product-positive-production-target/release/build_circuit';replaybin=root/'product-positive-production-replay-target/release/product_positive_production_replay'
assert sha(native)==(e/'native-builder.sha256').read_text().split()[0]
assert sha(replaybin)==(e/'replay-native.sha256').read_text().split()[0]=='1b3f93e952729f6529f5ef07598ae17c23eb148bf053fd01ee3a0ee0841a60a3'
assert 'RAW_OPS_SNAPSHOT ops=11319802 path='+str(raw) in (e/'run.log').read_text()
assert int((e/'replay.exit').read_text())==0 and int((more/'replay.exit').read_text())==0
result={'collected_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'evidence_kind':'source_bound_arithmetic_diagnostics','qualified_score':None,'status':'partial_repair_full_point_failures_preserved','baseline_revision':receipt['baseline_revision'],'builder_status':101,'builder_failure':'inherited linear_restore fixed operation-table length:11325109 versus11459358','runtime_raw_path_assertion':True,'raw_ops':11319802,'protected_tracked_changes':[],'source_sha256':receipt['source_sha256'],'protected_sha256':receipt['protected_sha256'],'builder_patch_sha256':receipt['candidate_patch_sha256'],'builder_binary_sha256':sha(native),'replay_binary_sha256':sha(replaybin),'replay_source_sha256':{'src/main.rs':sha(replay/'src/main.rs'),'Cargo.toml':sha(replay/'Cargo.toml')},'raw_stream_sha256':sha(raw),'metadata_sha256':sha(e/'metadata.tsv'),'logs':{str(f):sha(f)for f in [e/'run.log',e/'replay.log',more/'replay.log']},'packets':{str(f):sha(f)for f in [root/'product-evidence/structured-detail/structured.tsv',root/'product-evidence/classical-xor-factors/independent.tsv']},'scope':'256 fixed structured and256 independent native point tests; exact producer all-MR fixed-input proof separate; no official benchmark/tail tuning'}
(root/'product-evidence/positive-production/source-bound-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
