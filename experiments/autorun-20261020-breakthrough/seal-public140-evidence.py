"""Seal complete source and immutable final gate; never rerun the census."""
import hashlib,json,os,re,shutil,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
ws=Path('/home/hclau/ecdsa_research');name=sys.argv[1];r=ws/name;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert not(r/'EVIDENCE-MANIFEST.json').exists()
if name=='breakthrough-public140-finished-20261020':
 f=json.loads((r/'FINAL-SOURCE-FREEZE.json').read_text());t=r/'candidate';assert(r/'run.exit').read_text().strip()=='0';assert len(f['protected_files'])==17
 assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert sha(t/'ops.bin')=='a85c3ffa0ec725b04900ac79d5729dab126a870d566533f53d0f256c0d90cf98'
 actual=[int(x)for x in re.findall(r'test result: ok\. (\d+) passed; 0 failed;',(r/'tests.log').read_text())];assert actual==[2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]
 for p in f['source_files']:
  dest=r/'full-frozen-source'/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t/p,dest)
 audit={'status':'COMPLETE_NONCE0_SOURCE_PRESERVED','source_freeze_sha256':sha(r/'FINAL-SOURCE-FREEZE.json'),'native_tests':sum(actual),'protected_files_checked':17,'stream_sha256':sha(t/'ops.bin'),'binary_sha256':sha(t/'target/release/build_circuit'),'scope':'Frozen full source before gate and nonce screening. Original dated reports remain historical. Gate and selected benchmark have separate evidence.'}
elif name=='breakthrough-public140-final-gate-20261020':
 assert(r/'run.exit').read_text().strip()=='0';result=json.loads((r/'GATE-RESULT.json').read_text());assert result['verdict']=='FAILURE_RATE_GATE_PASS'and result['batches']==32768 and all(result['checks'].values())
 for n,row in result['summaries'].items():
  assert sha(r/(n+'.jsonl'))==row['rows_sha256'];rows=[json.loads(x)for x in(r/(n+'.jsonl')).read_text().splitlines()];assert len(rows)==32768
 audit={'status':'FINAL_GATE_PASS_EVIDENCE_PRESERVED_NO_RERUN','gate_sha256':sha(r/'GATE-RESULT.json'),'declaration_sha256':sha(r/'GATE-DECLARATION.json'),'shots_per_source':2097152,'scope':'Original declared gate verdict is final. Failed original launcher syntax and validated runner both retained; no census existed before validated launch.'}
elif name in ['breakthrough-generic-lease-prover-20261020','breakthrough-guarded-lease-prover-20261020','breakthrough-scope-fingerprints-20261020','breakthrough-scope-clean-20261020','breakthrough-cross-scope-leases-20261020']:
 assert(r/'run.exit').read_text().strip()=='0';f=json.loads((r/'SOURCE_FREEZE.json').read_text());t=r/'tool';assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
 result=json.loads((r/'DISCOVERY-RESULT.json').read_text());assert len(result['cases'])==2
 for row in result['cases']:assert sha(r/(row['name']+'.ops.bin'))==row['output_sha256']
 audit={'status':'EXACT_COMPONENT_DISCOVERY_ARCHIVED','source_freeze_sha256':sha(r/'SOURCE_FREEZE.json'),'result':result,'scope':'Full arbitrary-cut algebra accepts nominated leases; no native point-add integration, benchmark, final gate or scored result.'}
elif name=='breakthrough-certified-leases-20261020':
 assert(r/'run.exit').read_text().strip()=='0';f=json.loads((r/'INPUT-FREEZE.json').read_text())
 for pathfield,hashfield in [('input_path','input_sha256'),('tool_freeze_path','tool_freeze_sha256'),('source_freeze_path','source_freeze_sha256'),('binary_path','binary_sha256')]:assert sha(Path(f[pathfield]))==f[hashfield]
 result=json.loads((r/'RESULT.json').read_text());assert sha(r/'certified.ops.bin')==result['output_sha256'];audit={'status':'LINKED_EXACT_COMPONENT_DISCOVERY_ARCHIVED','input_freeze':f,'result':result,'scope':'Existing source/tool fully preserved separately. Research only, no gate, nonce or record.'}
elif name=='breakthrough-wide-strong-generic-20261020':
 assert(r/'run-v2.exit').read_text().strip()=='0';f=json.loads((r/'INPUT-FREEZE.json').read_text());result=json.loads((r/'AUDIT-RESULT.json').read_text());assert result['exit']==0 and sha(r/'optimized.ops.bin')==result['output_sha256'];assert sha(Path(f['input_stream']))==f['input_sha256']
 assert sha(ws/'breakthrough-wide-stronger-compare-20261020/SOURCE_FREEZE.json')==f['arithmetic_source_freeze_sha256'];assert sha(ws/'breakthrough-wide-generic-20261020/SOURCE_FREEZE.json')==f['optimizer_source_freeze_sha256'];audit={'status':'LINKED_FROZEN_OPTIMIZER_AUDIT_ARCHIVED','input_freeze':f,'result':result,'scope':'Generic optimizer and complete original control preserved separately. Noncompetitive diagnostic, no finalgate, nonce or record.'}
else:raise AssertionError(name)
audit['sealed_at_utc']=datetime.now(timezone.utc).isoformat();(r/'TERMINAL-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
files=[]
for current,dirs,names in os.walk(r):
 dirs[:]=sorted(d for d in dirs if d not in ['candidate','target','__pycache__'])
 for n in sorted(names):
  p=Path(current)/n
  if n=='ops.bin'or n.endswith('.ops.bin')or'resource-preflight'in n or n in ['EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','evidence.tar.gz']:continue
  files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':audit},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as a:
 for p in sorted(files)+[r/'EVIDENCE-MANIFEST.json']:a.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
receipt={'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')};(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
