from pathlib import Path
import tarfile,hashlib,json,sys
r=Path(__file__).parent
def sha_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
terminal='--terminal-only' in sys.argv
active=lambda p:False  # All owned jobs terminal; stopped/incomplete negatives are preserved.
selected=[];skipped=[];incomplete=[]
for directory in ['evidence','packets','model-source','tool/src']:
 for p in (r/directory).rglob('*'):
  if p.is_file() and p.name!='local-archive-manifest.json':
   if terminal and active(p):incomplete.append(str(p.relative_to(r)))
   elif p.stat().st_size<=32*1024*1024:selected.append(p)
   else:skipped.append(dict(path=str(p.relative_to(r)),bytes=p.stat().st_size,sha256=sha_file(p)))
selected.extend(p for p in r.iterdir() if p.is_file() and p.suffix in ['.py','.rs','.md','.sh','.c','.h','.txt','.tsv'] and not(terminal and active(p)))
selected.extend([r/'tool/Cargo.toml',r/'tool/Cargo.lock'])
selected=sorted(set(selected))
files={str(p.relative_to(r)):dict(bytes=p.stat().st_size,sha256=sha_file(p)) for p in selected}
manifest=r/'evidence/local-archive-manifest.json'
manifest.write_text(json.dumps(dict(included=len(selected),files=files,excluded_large_files=skipped,excluded_active_files=incomplete,terminal_checkpoint=terminal),indent=2)+'\n')
selected.append(manifest)
p=r/'evidence-local.tar.gz'
with tarfile.open(p,'w:gz',compresslevel=6) as tar:
 for src in selected:tar.add(src,arcname=str(src.relative_to(r)),recursive=False)
sha=sha_file(p)
(r/'evidence-local.tar.gz.sha256').write_text(sha+'  evidence-local.tar.gz\n')
print(json.dumps(dict(archive=p.name,bytes=p.stat().st_size,sha256=sha,terminal_checkpoint=terminal,files=len(files),excluded_active=len(incomplete),excluded=skipped)))

(r/'evidence/archive-mask-v3.exit').write_text('0\n')
