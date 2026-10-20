import hashlib,json,os,re,shutil,subprocess,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1];r=ws/name;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
config={
 'breakthrough-exact-branch-alias-20261020':('tool','SOURCE_FREEZE-rank.json','run-rank.exit',{'tests-v2.log':8,'tests-rank.log':9}),
 'breakthrough-prefix27-selective-20261020':('observer','SOURCE_FREEZE.json','run.exit',{'tests-'+str(i)+'.log':v for i,v in enumerate([1,2,2,1,1,2])}),
 'breakthrough-prefix27-cleanup11-native-20261020':('observer','SOURCE_FREEZE.json','run-v2.exit',{'v2-tests-'+str(i)+'.log':v for i,v in enumerate([1,1,1,2,2,1,1,2])}),
 'breakthrough-public54fc-lease-20261020':('tool','SOURCE_FREEZE.json','run.exit',{'tests.log':4}),
 'breakthrough-public8b-lease-20261020':('tool','SOURCE_FREEZE.json','run.exit',{'tests.log':4}),
 'breakthrough-public322-square-grid-20261020':('observer','SOURCE-FREEZE.json','run.exit',{'tests-'+str(i)+'.log':v for i,v in enumerate([2,1,1,4,1])}),
 'breakthrough-wide-tight-color-20261020':('tool','SOURCE_FREEZE.json','run-v2.exit',{'tests.log':12}),
}
assert name in config and not(r/'EVIDENCE-MANIFEST.json').exists();sub,freeze,exitfile,logs=config[name];t=r/sub;f=json.loads((r/freeze).read_text());assert(r/exitfile).read_text().strip()=='0'
for file,n in logs.items():assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/file).read_text())==[str(n)]
if sub=='tool':
 assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());dest=r/'tool-source';dest.mkdir()
 for p in t.iterdir():
  if p.is_file():shutil.copyfile(p,dest/p.name)
 if name=='breakthrough-exact-branch-alias-20261020':
  prior=json.loads((r/'SOURCE_FREEZE-v2.json').read_text());data=(t/'Cargo.toml').read_text().split('\n[[bin]]\nname="exact_rank_probe"')[0].encode();assert hashlib.sha256(data).hexdigest()==prior['tool_source_files']['Cargo.toml'];(r/'Cargo-before-rank.toml').write_bytes(data)
  initial=json.loads((r/'SOURCE_FREEZE.json').read_text());p=ws/'breakthrough-guarded-lease-prover-20261020/tool/Cargo.lock';assert sha(p)==initial['tool_source_files']['Cargo.lock'];shutil.copyfile(p,r/'Cargo-failed-v1.lock')
else:assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
audit={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'source_freeze_sha256':sha(r/freeze),'tests':logs,'status':'PRESERVED_RESEARCH_DIAGNOSTICS_NOT_SCORED','streams_retained_on_server':{p.relative_to(r).as_posix():sha(p)for p in list(r.glob('*.ops.bin'))+list(r.glob('*/ops.bin'))},'scope':'All failed setup/compiler runs and independent corrected runs retained. No statistical gate, nonce or new benchmark from these probes.'};(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');files=[]
for cur,dirs,names in os.walk(r):
 dirs[:]=sorted(d for d in dirs if d not in ['observer','tool','target','__pycache__','.git'])
 for n in sorted(names):
  p=Path(cur)/n
  if n=='ops.bin'or n.endswith('.ops.bin')or'resource-preflight'in n or n in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:continue
  files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':audit},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p in sorted(files)+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(name,len(files)+1)
