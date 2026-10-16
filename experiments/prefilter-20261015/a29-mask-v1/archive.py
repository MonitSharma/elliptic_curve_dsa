from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parents[1]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert (r/'a29-mask-v2/global.exit').read_text().strip()=='0'
assert (r/'a29-mask-v2/global-before.sha256').read_bytes()==(r/'a29-mask-v2/global-after.sha256').read_bytes()
files=set()
refs=[]
for folder in ['a29-mask-v1','a29-mask-v2']:
 for p in (r/folder).rglob('*'):
  if not p.is_file():continue
  if p.suffix=='.resources' or p.stat().st_size>2*1024*1024:
   refs.append(p)
  else:files.add(p)
for name in ['bin/a29_contract_map.rs','bin/a29_contract_map_v2.rs','bin/a29_contract_map_v3.rs','bin/a29_rng_mask.rs','bin/a29_rng_mask_v2.rs','a29_mask_program_trace.rs','a29_rng_mask_body.rs','a29_rng_mask_v2_body.rs','input_anf_dag_trace.rs','global_rng_anf_retained_masks.rs','reset_projection.rs','reset_projection_symbols.rs','shadow_value_contract_bound.rs','shadow_apply_region_bound.rs','mask_validate_transfer_body.rs','bin/mask_validate_transfer.rs','reset_projection_all_scopes_body.rs','bin/reset_projection_all_scopes_scan.rs']:
 files.add(r/'tool/src'/name)
files.add(r/'tool/Cargo.toml')
for name in ['a29_rng_mask','a29_rng_mask_v2','reset_projection_all_scopes_scan','mask_validate_transfer']:
 refs.append(r/'tool/target/release'/name)
refs.append(r.parent/'product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin')
manifest=dict(status='FRESH_A29_SOURCE_PROOF_EVIDENCE_PRESERVED_NO_PRODUCTION_CHANGE',files=[dict(path=str(p.relative_to(r)),size=p.stat().st_size,sha256=digest(p)) for p in sorted(files)],server_only_refs=[dict(path=str(p),size=p.stat().st_size,sha256=digest(p))for p in sorted(set(refs))])
out=r/'evidence-a29-mask-supplement.tar.gz'
assert not out.exists()
with tarfile.open(out,'w:gz')as tf:
 for p in sorted(files):tf.add(p,arcname=str(p.relative_to(r)),recursive=False)
 b=(json.dumps(manifest,indent=2)+'\n').encode();t=tarfile.TarInfo('MANIFEST.json');t.size=len(b);tf.addfile(t,io.BytesIO(b))
with tarfile.open(out)as tf:
 for row in manifest['files']:
  assert hashlib.sha256(tf.extractfile(row['path']).read()).hexdigest()==row['sha256']
receipt=dict(status='ALL_ARCHIVED_MANIFEST_ENTRIES_VERIFY',archive=out.name,sha256=digest(out),files=len(manifest['files']),server_only_refs=len(manifest['server_only_refs']))
(r/'evidence/a29-mask-archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
