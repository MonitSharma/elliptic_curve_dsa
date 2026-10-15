from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parent
out=r/'evidence-a29-paired-family-components.tar.gz'
assert not out.exists()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
files=set();refs=[]
for folder in ['a29-conditional-transfer-v1','a29-conditional-transfer-v2','a29-conditional-family-v1','a29-conditional-validation-v1']:
 for p in (r/folder).rglob('*'):
  if not p.is_file():continue
  if p.stat().st_size>2*1024*1024 or p.suffix=='.resources':
   refs.append(dict(path='prefilter-20261015/'+p.relative_to(r).as_posix(),size=p.stat().st_size,sha256=sha(p)))
  else:files.add(p)
for p in (r/'tool/src/bin').glob('a29*'):
 if p.name not in ['a29_pair_fold128.rs','a29_pair_fold128_full.rs','a29_pair_fold_family.rs','a29_pair_fold_validate.rs']:continue
 files.add(p)
for name in ['shadow_apply_region_bound.rs','a29_mask_program_trace.rs','input_anf_dag_trace.rs','global_rng_anf_retained_masks.rs','reset_projection.rs','reset_projection_symbols.rs','shadow_value_contract_bound.rs','shadow_apply_region_bound.rs']:
 p=r/'tool/src'/name
 if p.exists():files.add(p)
files.add(r/'tool/Cargo.toml');files.add(Path(__file__).resolve())
for folder in ['a29-conditional-family-v1','a29-conditional-validation-v1']:
 d=r/folder
 assert(d/'run.exit').read_text().strip()=='0'
 if (d/'before.sha256').exists():assert(d/'before.sha256').read_bytes()==(d/'after.sha256').read_bytes()
 if (d/'source-before.sha256').exists():assert(d/'source-before.sha256').read_bytes()==(d/'source-after.sha256').read_bytes()
refs.extend([dict(path='../product-exact-20261015/tip/ops.bin',sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'),dict(path='../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin',sha256='1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522')])
manifest=dict(status='ALL29_UNIVERSAL_PAIRED_FULL_QUANTUM_INTERFACES_LIVE_CLASSICAL_AND_COMPILED_GUARD_COMPONENTS_PRESERVED',active_prefix_composition_excluded=True,files=[dict(path=p.relative_to(r).as_posix(),size=p.stat().st_size,sha256=sha(p))for p in sorted(files)],server_only_hashrefs=refs)
with tarfile.open(out,'w:gz')as tf:
 for p in sorted(files):tf.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 b=(json.dumps(manifest,indent=2)+'\n').encode();t=tarfile.TarInfo('MANIFEST.json');t.size=len(b);tf.addfile(t,io.BytesIO(b))
with tarfile.open(out)as tf:
 for row in manifest['files']:assert hashlib.sha256(tf.extractfile(row['path']).read()).hexdigest()==row['sha256']
receipt=dict(status='ALL_ARCHIVED_MANIFEST_ENTRIES_VERIFY',archive=out.name,sha256=sha(out),files=len(files),server_only_hashrefs=len(refs))
(r/'evidence/a29-paired-family-archive-receipt.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
