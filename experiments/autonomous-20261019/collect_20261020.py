"""Seal completed results; never label a running census or search final."""
import datetime,hashlib,io,json,os,subprocess,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v15.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
configs={
 'classical9-final-v3-20261020':'Reviewed source9 queue finalizer, source-hashed registry and complete controls; watcher state is a snapshot.',
 'classical12-final-20261020':'Source12 complete finalizer input/control qualification, queue-only watcher; no final benchmark yet.',
 'product-classical-twelve-filter-20261019':'Completed own-source disabled runtime qualification PASS; all controls and complete rows, not a scored benchmark.',
 'product-classical-twelve-operational-20261019':'Completed operational acceptance and own4096 prefix control; failed admission retained. Future production files are excluded.',
 'product-classical-twelve-gate-audit-20261020':'Independent complete read-only audit of the sole declared passing census; no new shots or verdict.',
 'product-copy-cache-native-20261020':'Completed pinned native reproduction and source/tests; own census is running and excluded, no record.',
 'product-copy-cache-proof-20261020':'Independent exact edit/window/value/phase/physical-RNG proof, corruption controls and server replay; component evidence only.'}
for name,scope in configs.items():
 r=ws/name;files={};data={};omitted={}
 if 'twelve-filter' in name:assert (r/'qualification.exit').read_text().strip()=='0'
 if 'twelve-operational' in name:assert (r/'control.exit').read_text().strip()=='0'
 if 'copy-cache-native' in name:assert (r/'run.exit').read_text().strip()=='0'
 for p in sorted(r.rglob('*')):
  rel=p.relative_to(r);key=rel.as_posix()
  if not p.is_file() or any(x in rel.parts for x in ['target','candidate','__pycache__','evidence','cycle-receipts','gate-receipts','qualification']):continue
  if p.name.startswith(('cycle20','CYCLE20','LOCAL-CYCLE20','review-source','v14-cycle','V14-CYCLE','LOCAL-VERIFICATION')):continue
  if p.suffix in ['.bin','.so'] or p.name in ['worker0.jsonl','worker1.jsonl','worker2.jsonl','worker3.jsonl']:continue
  if name=='product-copy-cache-native-20261020' and (p.name.startswith(('gate','public-before-gate','submissions','benchmark','PUBLIC-RECORD')) or p.name=='qualify.py'):continue
  if name=='product-classical-twelve-operational-20261019' and p.name.startswith(('search','worker','run-record','PUBLIC-RECORD','submissions','benchmark','public-before-search')):continue
  if p.name.endswith('.tar.gz') and p.name!='point-add-source.tar.gz':continue
  size=p.stat().st_size
  if size>25_000_000:omitted[key]={'bytes':size,'sha256':sha(p)};continue
  raw=p.read_bytes();files[key]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};data[key]=raw
 manifest={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'server_directory':str(r),'scope':scope,'included_files':files,'omitted_large_files_retained_on_server':omitted}
 dest=r/'cycle20.tar.gz'
 with tarfile.open(dest,'x:gz') as a:
  for key,raw in data.items():m=tarfile.TarInfo(key);m.size=len(raw);a.addfile(m,io.BytesIO(raw))
  raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
 receipt={'archive':dest.name,'bytes':dest.stat().st_size,'sha256':sha(dest),'files':len(files),'scope':scope}
 (r/'CYCLE20.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'directory':name,**receipt}),flush=True)
r=ws/'autonomous-20261019';extra={}
for p in sorted((ws/'resource-registry-20261020').glob('*.json')):extra['registry/'+p.name]=p.read_bytes()
for p in r.glob('*TRANSITION.json'):extra[p.name]=p.read_bytes()
extra['resource-profile.json']=(json.dumps(profile,indent=2)+'\n').encode()
files={k:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in extra.items()}
with tarfile.open(r/'registry20.tar.gz','x:gz') as a:
 for key,raw in extra.items():m=tarfile.TarInfo(key);m.size=len(raw);a.addfile(m,io.BytesIO(raw))
 raw=(json.dumps({'included_files':files},indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
(r/'REGISTRY20.json').write_text(json.dumps({'archive':'registry20.tar.gz','sha256':sha(r/'registry20.tar.gz'),'files':len(files)},indent=2)+'\n')
