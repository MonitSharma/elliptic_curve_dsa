from pathlib import Path
import hashlib,json,subprocess,tarfile,gzip,math
a=Path(__file__).resolve().parent;ex=a.parent;r=ex/'breakthrough-public-semantic-finished-20261021';dest='/home/hclau/ecdsa_research/';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
pack='''from pathlib import Path
import json,hashlib,tarfile,gzip,io
ws=Path('/home/hclau/ecdsa_research');r=ws/'breakthrough-public-semantic-finished-20261021'
folders=[r,ws/'breakthrough-public-semantic-finished-development-20261021',ws/'breakthrough-public-semantic-final-gate-20261021']
assert json.loads((folders[2]/'GATE-RESULT.json').read_text())['verdict']=='FAILURE_RATE_GATE_PASS'
files={}
for folder in folders:
 for p in folder.iterdir():
  if not p.is_file()or p.name.endswith(('.tar.gz','.ops.bin'))or p.name.startswith('COLLECTED-'):continue
  data=p.read_bytes();name=folder.name+'/'+p.name
  if p.suffix=='.jsonl':data=gzip.compress(data,mtime=0);name+='.gz'
  files[name]=data
manifest={'files':{k:hashlib.sha256(v).hexdigest()for k,v in files.items()},'scope':'Complete immutable final gate/development/officialcompiler evidence. RawJSONL gzipped with mtime0, originalhashes retained in reports. No scored benchmark or nonce result.'}
data=(json.dumps(manifest,indent=2)+'\\n').encode();manifest_bytes=data;files[r.name+'/COLLECTED-GATE-MANIFEST.json']=data
bundle=r/'COLLECTED-GATE-EVIDENCE.tar.gz'
with tarfile.open(bundle,'w:gz')as ar:
 for name,data in sorted(files.items()):
  info=tarfile.TarInfo(name);info.size=len(data);ar.addfile(info,io.BytesIO(data))
receipt={'archive_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'members':len(files),'manifest_sha256':hashlib.sha256(manifest_bytes).hexdigest()}
(r/'COLLECTED-GATE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\\n');print(json.dumps(receipt))
'''
p=r/'collect-gate-server.py';p.write_text(pack);subprocess.run(['scp','-o','BatchMode=yes',str(p),'smu_server:'+dest+r.name+'/'+p.name],check=True)
subprocess.run(['ssh','-o','BatchMode=yes','smu_server','python3',dest+r.name+'/'+p.name],check=True)
for n in ['COLLECTED-GATE-EVIDENCE.tar.gz','COLLECTED-GATE-RECEIPT.json']:subprocess.run(['scp','-o','BatchMode=yes','smu_server:'+dest+r.name+'/'+n,str(r/n)],check=True)
receipt=json.loads((r/'COLLECTED-GATE-RECEIPT.json').read_text());assert sha(r/'COLLECTED-GATE-EVIDENCE.tar.gz')==receipt['archive_sha256']
with tarfile.open(r/'COLLECTED-GATE-EVIDENCE.tar.gz')as ar:
 members=ar.getmembers();assert len(members)==receipt['members'];manifest=json.loads(ar.extractfile(r.name+'/COLLECTED-GATE-MANIFEST.json').read());assert set(manifest['files'])|{r.name+'/COLLECTED-GATE-MANIFEST.json'}=={m.name for m in members}
 for m in members:
  rel=Path(m.name);assert m.isfile()and not rel.is_absolute()and'..'not in rel.parts and rel.parts[0]in {r.name,'breakthrough-public-semantic-finished-development-20261021','breakthrough-public-semantic-final-gate-20261021'} and len(rel.parts)==2
  data=ar.extractfile(m).read()
  if m.name in manifest['files']:assert hashlib.sha256(data).hexdigest()==manifest['files'][m.name]
  p=ex/rel
  if p.exists()and(p.name.endswith('.py')or p.name in ['SOURCE-SPEC.json','SOURCE-FREEZE.json','source.patch','git-source.patch']):assert p.read_bytes()==data,(p,'Frozen evidence changed')
  p.write_bytes(data)
gate=ex/'breakthrough-public-semantic-final-gate-20261021';g=json.loads((gate/'GATE-RESULT.json').read_text());d=json.loads((gate/'GATE-DECLARATION.json').read_text());assert sha(gate/'GATE-DECLARATION.json')==g['declaration_sha256'];assert sha(r/'SOURCE-FREEZE.json')==g['candidate_source_freeze_sha256']==d['candidate_source_freeze_sha256'];rows={}
for name in ['parent','candidate']:
 raw=gzip.decompress((gate/(name+'.jsonl.gz')).read_bytes());assert hashlib.sha256(raw).hexdigest()==g['summaries'][name]['rows_sha256'];v=[json.loads(x)for x in raw.splitlines()];assert len(v)==32768 and [x['batch']for x in v]==list(range(32768));rows[name]=v
 for channel in ['value','phase','dirty']:assert sum(x[channel+'_shots']for x in v)==g['summaries'][name][channel+'_shots']
 assert sum(bool(x['failures'])for x in v)==g['summaries'][name]['failed_batches']
b=sum(not x['failures']and bool(y['failures'])for x,y in zip(rows['parent'],rows['candidate']));c=sum(bool(x['failures'])and not y['failures']for x,y in zip(rows['parent'],rows['candidate']));assert b==c==0 and g['one_sided_exact_mcnemar_p']==1 and all(g['checks'].values())
assert all(x['failures']==y['failures']for x,y in zip(rows['parent'],rows['candidate']));assert g['summaries']['candidate']['dirty_shots']==0 and g['summaries']['candidate']['value_shots']<=g['summaries']['parent']['value_shots'] and 141*g['summaries']['candidate']['failed_batches']/32768<=18
(r/'LOCAL-GATE-VERIFICATION.json').write_text(json.dumps({'status':'ALL_GATE_AND_DEVELOPMENT_ARCHIVE_MEMBERS_AND_ALL32768_PAIRED_FAILURE_ROWS_VERIFIED_LOCALLY','members':receipt['members'],'archive_sha256':receipt['archive_sha256'],'gate_verdict':g['verdict'],'b':b,'c':c,'one_sided_p':1,'failed_batches_per_packet':g['summaries']['candidate']['failed_batches_per_9024_packet'],'mean_T_delta':g['candidate_minus_parent_mean_executed_toffoli'],'scope':'Full gate, native4-independent semanticproof12 and compiler evidence verified. Native runtime4. No benchmark/nonce score or product improvement claimed.'},indent=2)+'\n');print('Verified complete gate locally',g['verdict'])
