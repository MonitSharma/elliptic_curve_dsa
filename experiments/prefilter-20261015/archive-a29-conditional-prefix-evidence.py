from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parent
out=r/'evidence-a29-conditional-prefix-supplement.tar.gz'
assert not out.exists()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
files=set();refs=[]
for folder in ['a29-conditional-prefix-v1']:
 for p in (r/folder).rglob('*'):
  if not p.is_file():continue
  if p.stat().st_size>2*1024*1024 or p.suffix=='.resources':
   refs.append(dict(path='prefilter-20261015/'+p.relative_to(r).as_posix(),size=p.stat().st_size,sha256=sha(p)))
  else:files.add(p)
for p in (r/'tool/src/bin').glob('a29*'):
 if p.name not in ['a29_conditional_prefix.rs']:continue
 files.add(p)
for name in ['a29_conditional_prefix_body.rs','shadow_apply_region_bound.rs','a29_mask_program_trace.rs','input_anf_dag_trace.rs','global_rng_anf_retained_masks.rs','reset_projection.rs','reset_projection_symbols.rs','shadow_value_contract_bound.rs','shadow_apply_region_bound.rs']:
 p=r/'tool/src'/name
 if p.exists():files.add(p)
files.add(r/'tool/Cargo.toml');files.add(Path(__file__).resolve())
d=r/'a29-conditional-prefix-v1'
assert(d/'global.exit').read_text().strip()=='0'
assert(d/'global-before.sha256').read_bytes()==(d/'global-after.sha256').read_bytes()
refs.append(dict(path='evidence-a29-paired-family-components.tar.gz',sha256='28848e9697a739fee2ca8d0b4bab1f32e0e17bb20f3f64d08cbec34bc8822dab'))
refs.extend([dict(path='../product-exact-20261015/tip/ops.bin',sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'),dict(path='../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin',sha256='1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522')])
manifest=dict(status='FINITE_SOURCE_BOUND_A29_PUBLIC_DISCREPANCY_GUARD_EXPORT_REQUIRES_INDEPENDENT_REVIEW',wider_fixture_coverage_not_yet_included=True,files=[dict(path=p.relative_to(r).as_posix(),size=p.stat().st_size,sha256=sha(p))for p in sorted(files)],server_only_hashrefs=refs)
with tarfile.open(out,'w:gz')as tf:
 for p in sorted(files):tf.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 b=(json.dumps(manifest,indent=2)+'\n').encode();t=tarfile.TarInfo('MANIFEST.json');t.size=len(b);tf.addfile(t,io.BytesIO(b))
with tarfile.open(out)as tf:
 for row in manifest['files']:assert hashlib.sha256(tf.extractfile(row['path']).read()).hexdigest()==row['sha256']
receipt=dict(status='ALL_ARCHIVED_MANIFEST_ENTRIES_VERIFY',archive=out.name,sha256=sha(out),files=len(files),server_only_hashrefs=len(refs))
(r/'evidence/a29-conditional-prefix-archive-receipt.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
