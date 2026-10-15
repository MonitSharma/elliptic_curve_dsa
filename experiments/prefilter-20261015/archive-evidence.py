from pathlib import Path
import tarfile,hashlib,json,sys
r=Path(__file__).parent
terminal='--terminal-only' in sys.argv
active=lambda p:('hybrid' in p.name or p.name in ['input_bdd.rs','input_anf_bdd_dag.rs','shadow_apply_region.rs','global_rng_anf_shadow.rs','global_rng_anf_shadow_body.rs','run-global-anf-shadow.sh'] or p.name.startswith('global-anf-shadow'))
selected=[];skipped=[];incomplete=[]
for directory in ['evidence','packets','model-source','tool/src']:
 for p in (r/directory).rglob('*'):
  if p.is_file() and p.name!='local-archive-manifest.json':
   if terminal and active(p):incomplete.append(str(p.relative_to(r)))
   elif p.stat().st_size<=32*1024*1024:selected.append(p)
   else:skipped.append(dict(path=str(p.relative_to(r)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
selected.extend(p for p in r.iterdir() if p.is_file() and p.suffix in ['.py','.rs','.md','.sh','.c','.h'] and not(terminal and active(p)))
selected.extend([r/'tool/Cargo.toml',r/'tool/Cargo.lock'])
selected=sorted(set(selected))
files={str(p.relative_to(r)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in selected}
manifest=r/'evidence/local-archive-manifest.json'
manifest.write_text(json.dumps(dict(included=len(selected),files=files,excluded_large_files=skipped,excluded_active_files=incomplete,terminal_checkpoint=terminal),indent=2)+'\n')
selected.append(manifest)
p=r/'evidence-local.tar.gz'
with tarfile.open(p,'w:gz',compresslevel=6) as tar:
 for src in selected:tar.add(src,arcname=str(src.relative_to(r)),recursive=False)
sha=hashlib.sha256(p.read_bytes()).hexdigest()
(r/'evidence-local.tar.gz.sha256').write_text(sha+'  evidence-local.tar.gz\n')
print(json.dumps(dict(archive=p.name,bytes=p.stat().st_size,sha256=sha,terminal_checkpoint=terminal,files=len(files),excluded_active=len(incomplete),excluded=skipped)))
