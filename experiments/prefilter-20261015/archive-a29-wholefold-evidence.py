from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parent
out=r/'evidence-a29-wholefold-supplement.tar.gz'
assert not out.exists()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
files=set();refs=[]
for folder in ['a29-mask-v3','a29-mask-v4','a29-relations-v1','a29-relations-v2','a29-fold-family-v1','a29-edited-folds-v1','a29-square-map-v1','review/flag12-transfer-v1']:
 for p in (r/folder).rglob('*'):
  if not p.is_file():continue
  if p.stat().st_size>2*1024*1024 or p.suffix=='.resources':
   refs.append(dict(path='prefilter-20261015/'+p.relative_to(r).as_posix(),size=p.stat().st_size,sha256=sha(p)))
  else:files.add(p)
for p in (r/'tool/src/bin').glob('a29*'):
 if p.name=='a29_rng_mask_v5.rs':continue
 files.add(p)
for name in ['a29_rng_mask_v3_body.rs','a29_rng_mask_v4_body.rs','a29_relation_prefix_body.rs','a29_relation_whole_body.rs','a29_relation_obligations.rs','a29_mask_program_trace.rs','input_anf_dag_trace.rs','global_rng_anf_retained_masks.rs','reset_projection.rs','reset_projection_symbols.rs','shadow_value_contract_bound.rs','shadow_apply_region_bound.rs']:
 p=r/'tool/src'/name
 if p.exists():files.add(p)
files.add(r/'tool/Cargo.toml');files.add(Path(__file__).resolve())
for v in ['v3','v4']:
 d=r/('a29-mask-'+v)
 assert(d/'global.exit').read_text().strip()=='0'
 assert(d/'global-before.sha256').read_bytes()==(d/'global-after.sha256').read_bytes()
 for line in (d/'global-before.sha256').read_text().splitlines():
  digest,path=line.split(maxsplit=1)
  if path.startswith('tool/target/')or path.startswith('../'):
   refs.append(dict(path=path,sha256=digest,recorded_by='a29-mask-'+v+'/global-before.sha256'))
manifest=dict(status='TERMINAL_A29_WHOLE_LIFETIME_PROOFS_AND_ZERO_MASK_COVERAGE_NEGATIVE_PRESERVED',active_v5_excluded=True,files=[dict(path=p.relative_to(r).as_posix(),size=p.stat().st_size,sha256=sha(p))for p in sorted(files)],server_only_hashrefs=refs)
with tarfile.open(out,'w:gz')as tf:
 for p in sorted(files):tf.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 b=(json.dumps(manifest,indent=2)+'\n').encode();t=tarfile.TarInfo('MANIFEST.json');t.size=len(b);tf.addfile(t,io.BytesIO(b))
with tarfile.open(out)as tf:
 for row in manifest['files']:assert hashlib.sha256(tf.extractfile(row['path']).read()).hexdigest()==row['sha256']
receipt=dict(status='ALL_ARCHIVED_MANIFEST_ENTRIES_VERIFY',archive=out.name,sha256=sha(out),files=len(files),server_only_hashrefs=len(refs))
(r/'evidence/a29-wholefold-archive-receipt.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
