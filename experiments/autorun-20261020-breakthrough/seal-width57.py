"""Preserve native experiments, failed fixtures and final gate without reruns."""
import hashlib,json,os,re,shutil,subprocess,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1];r=ws/name;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert not(r/'EVIDENCE-MANIFEST.json').exists()
config={
 'breakthrough-prefix27-width57-20261020':('observer','SOURCE_FREEZE-v2.json','run-v2.exit',{'tests-'+str(i)+'.log':[v] for i,v in enumerate([2,2,2,1,1,1,1,1,1,1,1,1,3,1,4,3,2,3,1,1])}),
 'breakthrough-public140-cache-20261020':('tool','SOURCE_FREEZE.json','run.exit',{'tests.log':[4]}),
 'breakthrough-public140-cone-cache-20261020':('tool','SOURCE_FREEZE-v2.json','run-v2.exit',{'tests-v2.log':[7]}),
 'breakthrough-prefix-dag-20261020':('primitive','SOURCE_FREEZE-v2.json','run-v2.exit',{'export-v2.log':[1]}),
 'breakthrough-prefix27-native-20261020':('primitive','SOURCE_FREEZE.json','run.exit',{'tests.log':[2],'original-control.log':[1]}),
 'breakthrough-prefix27-fold-native-20261020':('primitive','SOURCE_FREEZE.json','run.exit',{'cleanup.log':[1],'full-fold.log':[1],'retained-control.log':[2]}),
 'breakthrough-prefix27-production-20261020':('observer','SOURCE_FREEZE.json','run.exit',{'tests-'+str(i)+'.log':[v]for i,v in enumerate([2,1,1,1,1,1,1,1,1,1,3,1,4,3,2,3,1,1])}),
 'breakthrough-prefix27-global-reuse-20261020':('observer','SOURCE_FREEZE.json','run.exit',{'tests-'+str(i)+'.log':[v]for i,v in enumerate([2,2,1,1,1,1,1,1,1,1,1,3,1,4,3,2,3,1,1])}),
}
# The exact154 run's16 logs are distinct; the initial framing assertion stays failed.
config['breakthrough-public140-exact154-20261020']=('candidate','SOURCE-FREEZE.json','audit-v2.exit',{'tests-'+str(i)+'.log':[v]for i,v in enumerate([1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1])})
assert name in config or name=='breakthrough-public140-exact154-final-gate-20261020'
if name in config:
 sub,freeze,exitfile,logs=config[name];t=r/sub;assert(r/exitfile).read_text().strip()=='0';f=json.loads((r/freeze).read_text())
 for log,expected in logs.items():assert[int(x)for x in re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/log).read_text())]==expected
 if 'source_files'in f:
  assert len(f['protected_files'])==17 and all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());tracked=set(subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines());added=r/'added-source';added.mkdir()
  for p in(t/'src/point_add').rglob('*'):
   if p.is_file()and p.relative_to(t).as_posix()not in tracked:dest=added/p.relative_to(t/'src/point_add');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 else:
  assert all(sha(t/p)==h for p,h in f['tool_source_files'].items())and all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
 if name=='breakthrough-public140-cone-cache-20261020':
  prior=json.loads((r/'SOURCE_FREEZE.json').read_text());s=(t/'discover.rs').read_text();a=s.index('#[cfg(test)]mod cone_tests{');oldtest=(r/'cone-proof.rs').read_text();oldtest=oldtest[oldtest.index('#[cfg(test)]mod cone_tests{'):];data=(s[:a]+oldtest).encode();assert hashlib.sha256(data).hexdigest()==prior['tool_source_files']['discover.rs'];(r/'discover-failed-fixture-v1.rs').write_bytes(data)
 if name=='breakthrough-prefix-dag-20261020':
  p=t/'src/point_add/y15_onefold.rs';data=p.read_bytes();a=b'use crate::circuit::OperationType::*;let t=o.q_target.0 as usize;';assert data.count(a)==1;data=data.replace(a,b'use OperationType::*;let t=o.q_target.0 as usize;');prior=json.loads((r/'SOURCE_FREEZE.json').read_text());assert hashlib.sha256(data).hexdigest()==prior['source_files']['src/point_add/y15_onefold.rs'];(r/'y15-failed-import-v1.rs').write_bytes(data)
 resultfiles=[p for p in r.iterdir()if p.name in ['RESULT.json','RESULT-v2.json','NATIVE-RESULT.json','FINISHED-RESULT-v2.json','PREFIX-DAG.json','ADMISSION-RESULT.json','ADMISSION-RESULT-v2.json']];audit={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'source_freeze_sha256':sha(r/freeze),'protected_source_checks':len(f.get('protected_files',f.get('protected_dependency_files',{}))),'test_counts':logs,'results':{p.name:json.loads(p.read_text())for p in resultfiles},'scope':'Native/component diagnostics retained separately from complete benchmarks. Every original failure remains. Raw source assertions, scope and stream provenance stay authoritative.'}
 if name=='breakthrough-prefix27-fold-native-20261020':audit['all_six_full_fold_diagnostic_lines']=re.findall(r'PREFIX27_FULL_FOLD[^\n]+',(r/'full-fold.log').read_text());assert len(audit['all_six_full_fold_diagnostic_lines'])==6
 audit['streams_retained_on_server']={p.relative_to(r).as_posix():sha(p)for p in list(r.glob('*.ops.bin'))+list(r.glob('*/ops.bin'))}
else:
 assert(r/'run.exit').read_text().strip()=='0';g=json.loads((r/'GATE-RESULT.json').read_text());assert g['verdict']=='FAILURE_RATE_GATE_PASS'and g['batches']==32768 and all(g['checks'].values())
 for n,row in g['summaries'].items():assert sha(r/(n+'.jsonl'))==row['rows_sha256']and len((r/(n+'.jsonl')).read_text().splitlines())==32768
 audit={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'status':'FINAL_PASS_ARCHIVED_NO_GATE_RERUN','declaration_sha256':sha(r/'GATE-DECLARATION.json'),'gate_result_sha256':sha(r/'GATE-RESULT.json'),'scope':'Final declared gate on independent exact154 source versus exact official4045 parent. All rows and original verdict preserved.'}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n');files=[]
for current,dirs,names in os.walk(r):
 dirs[:]=sorted(d for d in dirs if d not in ['primitive','candidate','observer','target','__pycache__'])
 for n in sorted(names):
  p=Path(current)/n
  if n=='ops.bin'or n.endswith('.ops.bin')or'resource-preflight'in n or n in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']:continue
  files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':audit},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p in sorted(files)+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
(r/'PACKAGE-RESULT.json').write_text(json.dumps({'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')},indent=2)+'\n');print(name,(r/'PACKAGE-RESULT.json').read_text())
