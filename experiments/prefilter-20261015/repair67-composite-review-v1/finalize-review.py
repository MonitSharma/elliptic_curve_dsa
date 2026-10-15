from pathlib import Path
import json,hashlib,tarfile,io
r=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((r/'PREPARED_SOURCE.json').read_text())
names=['packed_body.rs','guard.rs','transfer.rs','fast_sim_wide.rs','early.rs','masks.rs']
for n in names:assert sha(r/n)==pins['tool/src/'+n]
d=r.parent.parent/'repair67-conditional-filter-20261016'
receipt={
 'status':'INDEPENDENT_GENERATED_SOURCE_REVIEW_PASS_RUNTIME_RECEIPTS_PENDING',
 'reviewed_generated_sources':[{ 'path':'tool/src/'+n,'sha256':sha(r/n)}for n in names],
 'prepared_manifest_sha256':sha(r/'PREPARED_SOURCE.json'),
 'generated_driver_sha256':sha(r/'run.py'),
 'root_inputs':[{'path':str(p),'sha256':sha(p)}for p in[d/n for n in ['DECLARATION.json','COMPOSITE_BINDING.json','prepare.py','guard.rs','run.sh']]],
 'source_checks':[
  'Binding pins conditional theorem b351, source2a/A291cd/candidate0bee, original560c, guard355f, cache67 3cb/0bf and ABI61cb.',
  'Both mask and guard use identical canonical1024 public-input ports P.x/P.y/A.x/A.y, bitLSB first and point-index vector packing.',
  'Raw G=0 is safe. Only provisional old known-wrong points enter guard, and their iterator is consumed only on true original_wrong; final retained certificate is old_wrong AND NOT G.',
  'Original zero-MR IR812f and generic/direct libraries are pinned. Protected shadow explicitly loads original2a and asserts ordered register identity with candidate.',
  'Fixed445 inputs hash pinned;428safe/3excluded old431 and14excluded repair cases asserted;418retained known-wrong checks plus protected original/candidate known-bit equality on safe inputs.',
  'Full fallback compiler uses u32 classical c/bt, asserts66245workspace, and tests65535/66244 through protected state/phase/MR comparisons.',
  'Own candidate Fiat prefix and identity tail are bound, nonce seed tests1/2/17/255. Full fallback uses actual candidate prefix and original post9024-input reader, preserving quantum/classical/phase/garbage and every MR draw.',
  'Generated force=True control enters scheduler done path at nonces1/2/lookahead1, compares exact_early(kind,shots) to protected Simulator on same post-input tape, and compares generic/direct output rows.',
  'PROOF_ACCEPTED remains false, asserted at main; output explicitly unauthoritative and no selected nonce.'
 ],
 'historical_finding':{'receipt_sha256':sha(r/'REVIEW-v1.json'),'finding':'No forced scheduler fallback trial in initial driver','resolution':'Explicit forced scheduler test now present in generated run.py and protected_fallback_kind in guard.rs; source-reviewed, execution receipt pending.'},
 'limitations':['This source review does not claim that pending protected tests or cost gate have passed.','No operational search or runtime authority is issued.','No production or root source edits were made.']}
out=r/'REVIEW-v2.json';data=(json.dumps(receipt,indent=2)+'\n').encode()
if out.exists():assert out.read_bytes()==data
else:out.write_bytes(data)
archive=r.parent/'evidence-repair67-composite-independent-review.tar.gz';assert not archive.exists()
files=[p for p in r.rglob('*')if p.is_file()]
m={'status':'INDEPENDENT_REVIEW_SOURCE_SNAPSHOTS_AND_RECEIPTS_NO_AUTHORITY','files':[{'path':p.relative_to(r).as_posix(),'sha256':sha(p)}for p in files]}
with tarfile.open(archive,'w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 b=(json.dumps(m,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(archive)as t:
 for p in m['files']:assert hashlib.sha256(t.extractfile(p['path']).read()).hexdigest()==p['sha256']
print(json.dumps({'review_sha256':sha(out),'archive_sha256':sha(archive),'files':len(files)}))
