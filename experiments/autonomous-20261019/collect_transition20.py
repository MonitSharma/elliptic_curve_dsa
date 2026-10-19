"""Seal audited retirement, actual new launch, and gate-blocked runtime build."""
import datetime,hashlib,io,json,os,subprocess,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v15.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
assert (ws/'product-copy-cache-filter-20261020/build.exit').read_text().strip()=='0'
assert json.loads((ws/'classical9-retirement-20261020/COMPLETE-LOG-AUDIT.json').read_text())['status']=='NO_PASS_COMPLETE_JSONL_AUDIT_PASS'
configs={
 'classical9-retirement-20261020':('Audited every21,577,728 terminal nonce row; no pass. Complete logs remain server-bound with hashes. No score.',None),
 'product-classical-twelve-operational-20261019':('Actual new frozen source12 launch from1 after complete old no-pass audit, refreshed current public parent and own-runtime acceptance. Live counters are provisional; no selected nonce or score.',{'launch_search.py','preflight_search.py','run-search.sh','refresh_record.py','coordinator.py','search.pid','run-record.json','search-preflight.json','SEARCH_SOURCE.sha256','PUBLIC-RECORD.json','public-before-search.log','ACCEPTANCE.json','CONTROL.json','search-nohup.log'}),
 'product-copy-cache-filter-20261020':('Disabled exact source-bound copy-cache runtime build PASS, own source final gate remains pending. Idle watcher waits gate PASS and actual managers terminal before own qualification. No new source nonce tested or selected.',None)}
for name,(scope,selected) in configs.items():
 r=ws/name;data={};files={}
 for p in sorted(r.rglob('*')):
  rel=p.relative_to(r);key=rel.as_posix()
  if not p.is_file() or any(x in rel.parts for x in ['target','__pycache__','evidence','transition20-receipts']):continue
  if selected is not None and key not in selected and not (key.startswith('worker') and p.suffix=='.pid'):continue
  if p.name.startswith(('transition20','TRANSITION20','LOCAL-TRANSITION20')) or p.suffix in ['.bin','.so'] or p.name.endswith('.tar.gz'):continue
  assert p.stat().st_size<5_000_000,key
  raw=p.read_bytes();data[key]=raw;files[key]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 extra={}
 for p in (ws/'resource-registry-20261020').glob('*.json'):extra['registry/'+p.name]=p.read_bytes()
 if name=='product-copy-cache-filter-20261020':
  prep=json.loads((r/'PREPARATION.json').read_text());assert all(sha(r/'tool'/p)==v['sha256'] for p,v in prep['files'].items())
  assert all(sha(Path(p))==h for p,h in prep['additional_proof_artifacts'].items())
  bound=json.loads((r/'WATCH_SOURCE.json').read_text());assert all(sha(r/p)==h for p,h in bound.items())
  extra['ACTUAL-BINARY.json']=(json.dumps({'sha256':sha(r/'tool/target/release/value_prefilter'),'authoritative_rejection':False,'own_gate_pending':True},indent=2)+'\n').encode()
 extra['resource-profile.json']=(json.dumps(profile,indent=2)+'\n').encode()
 for key,raw in extra.items():data[key]=raw;files[key]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 manifest={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'server_directory':str(r),'scope':scope,'included_files':files}
 dest=r/'transition20.tar.gz'
 with tarfile.open(dest,'x:gz') as a:
  for key,raw in data.items():m=tarfile.TarInfo(key);m.size=len(raw);a.addfile(m,io.BytesIO(raw))
  raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
 receipt={'archive':dest.name,'bytes':dest.stat().st_size,'sha256':sha(dest),'files':len(files),'scope':scope}
 (r/'TRANSITION20.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'directory':name,**receipt}),flush=True)
# Preserve the new candidate's original gate declaration and public refresh without partial rows.
r=ws/'product-copy-cache-native-20261020';data={key:(r/key).read_bytes() for key in ['GATE-PLAN.md','gate.pid','qualification/DECLARATION.json','PUBLIC-RECORD.json','benchmark.json','run-gate.sh','qualify.py','refresh_record.py','launch_gate.py']}
files={k:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in data.items()}
with tarfile.open(r/'gate-declaration20.tar.gz','x:gz') as a:
 for key,raw in data.items():m=tarfile.TarInfo(key);m.size=len(raw);a.addfile(m,io.BytesIO(raw))
 raw=(json.dumps({'scope':'Original declared census still live; no verdict or partial count presented as final.','included_files':files},indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
(r/'GATE-DECLARATION20.json').write_text(json.dumps({'archive':'gate-declaration20.tar.gz','sha256':sha(r/'gate-declaration20.tar.gz'),'files':len(files)},indent=2)+'\n')
