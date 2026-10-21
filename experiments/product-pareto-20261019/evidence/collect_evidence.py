"""Archive small evidence and inventory all generated streams without moving them."""
import hashlib,io,json,tarfile
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
inventory=[]
for p in sorted(root.glob('*.ops.bin')):
    inventory.append({'path':str(p),'size':p.stat().st_size,'sha256':sha(p),
                      'status':'INVALID_TOOLING_OUTPUT' if p.name in ('parent-exact.ops.bin','product179-exact.ops.bin','product179-v2.ops.bin','parent-v2.ops.bin') else 'DIAGNOSTIC_NOT_SCORED'})
files=[p for p in root.iterdir() if p.is_file() and p.suffix in ('.json','.log','.txt','.sha256','.pid','.exit','.rs','.py','.sh','.toml','.md','.patch') and p.stat().st_size<5_000_000]
files+=list((root/'pilot-parent').glob('*'))
for name in ('DECLARATION.json','PROGRESS.json','stage-001-receipt.json'):
    p=root/'continuation84'/name
    if p.exists():files.append(p)
snapshot={str(p.relative_to(root)):p.read_bytes() for p in files if p.is_file()}
manifest={'captured_utc':datetime.now(timezone.utc).isoformat(),'streams':inventory,
          'files':{name:hashlib.sha256(data).hexdigest() for name,data in snapshot.items()}}
(root/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'quick-evidence.tar.gz','w:gz') as archive:
    for name,data in snapshot.items():
        info=tarfile.TarInfo(name);info.size=len(data);archive.addfile(info,io.BytesIO(data))
print(json.dumps({'archive':str(root/'quick-evidence.tar.gz'),'sha256':sha(root/'quick-evidence.tar.gz'),'files':len(files),'streams':len(inventory)}))
