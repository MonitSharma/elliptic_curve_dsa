import hashlib,io,json,tarfile
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={};omitted={}
suffixes={'.rs','.py','.sh','.toml','.lock','.md','.json','.log','.txt','.sha256','.exit','.pid','.raw'}
for p in r.iterdir():
    if not p.is_file() or p.name.startswith(('proof-evidence-','EVIDENCE-')):continue
    eligible=p.suffix in suffixes or p.name.endswith(('.smt2.gz','.proof.gz','.model.gz'))
    if not eligible:continue
    item={'sha256':sha(p),'bytes':p.stat().st_size}
    # All passing proof windows/formulas fit here. Larger inconclusive
    # relation cones and windows remain on the server with explicit hashes.
    if p.stat().st_size<=5_000_000:files[p.name]=item
    else:omitted[p.name]=item
dependencies={}
for name in ('libraries/z3/lib/libz3.so','libraries/z3/z3.py','libraries/z3/z3core.py'):
    p=r/name
    if p.exists():dependencies[name]={'sha256':sha(p),'bytes':p.stat().st_size}
manifest={'captured_utc':datetime.now(timezone.utc).isoformat(),'checkpoint_not_a_resource_result':True,
    'server_directory':str(r),'included_files':files,'larger_files_preserved_on_server':omitted,'solver_dependencies':dependencies}
archive=r/f'proof-evidence-{stamp}.tar.gz'
with tarfile.open(archive,'x:gz') as tar:
    for name in sorted(files):tar.add(r/name,arcname=name)
    data=(json.dumps(manifest,indent=2)+'\n').encode();item=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');item.size=len(data);tar.addfile(item,io.BytesIO(data))
receipt={'archive':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,'files':len(files),'omitted_larger_file_count':len(omitted),'source_directory':str(r)}
(r/'EVIDENCE-LATEST.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
