from pathlib import Path
import json,hashlib,tarfile,gzip,io
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-recycle-finished-v2-20261021'
folders=[r,ws/'breakthrough-recycle-finished-development-20261021',ws/'breakthrough-recycle-final-gate-20261021']
assert json.loads((folders[2]/'GATE-RESULT.json').read_text())['verdict']=='FAILURE_RATE_GATE_PASS'
files={}
for folder in folders:
 for p in folder.iterdir():
  if not p.is_file()or p.name.endswith(('.tar.gz','.ops.bin'))or p.name.startswith('COLLECTED-'):continue
  data=p.read_bytes();name=folder.name+'/'+p.name
  if p.suffix=='.jsonl':data=gzip.compress(data,mtime=0);name+='.gz'
  files[name]=data
manifest={'files':{k:hashlib.sha256(v).hexdigest()for k,v in files.items()},'scope':'Complete immutable final gate/development/officialcompiler evidence. RawJSONL gzipped with mtime0, originalhashes retained in reports. No scored benchmark or nonce result.'}
data=(json.dumps(manifest,indent=2)+'\n').encode();manifest_bytes=data;files[r.name+'/COLLECTED-GATE-MANIFEST.json']=data
bundle=r/'COLLECTED-GATE-EVIDENCE.tar.gz'
with tarfile.open(bundle,'w:gz')as ar:
 for name,data in sorted(files.items()):
  info=tarfile.TarInfo(name);info.size=len(data);ar.addfile(info,io.BytesIO(data))
receipt={'archive_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'members':len(files),'manifest_sha256':hashlib.sha256(manifest_bytes).hexdigest()}
(r/'COLLECTED-GATE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
