from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-groups-safe-final-20261020'
s='''import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';f=json.loads((r/'SOURCE-FREEZE.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());s=json.loads((r/'submission-status.json').read_text())['submission'];revision=s['submissionCommitSha'];sid=json.loads((r/'submission-response.json').read_text())['submission']['id'];sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert s['id']==sid and s['officialMetrics']=={'qubits':b['qubits'],'toffoli':b['rounded_mean_executed_toffoli']} and s['officialScore']==b['product'];assert s['status']=='accepted' or s['status']=='rejected' and s['rejectionReason']=='score did not improve current best'
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
if subprocess.run(['git','-C',str(t),'cat-file','-e',revision],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:subprocess.run(['git','-C',str(t),'fetch','origin',revision],check=True)
paths=git('ls-tree','-r','--name-only',revision,'--','src/point_add').decode().splitlines();assert set(paths)==set(f['source_files']) and len(paths)==204
for p,h in {**f['source_files'],**f['protected_files']}.items():assert hashlib.sha256(git('show',revision+':'+p)).hexdigest()==h,p
assert sha(t/'ops.bin')==b['native_receipt']['stream_sha256']
v={'status':'OFFICIAL_COMMIT_EVERY_SOURCE_AND_PROTECTED_BYTE_MATCHES_VALIDATED_LOCAL','public_submission':sid,'public_source_revision':revision,'local_source_revision':git('rev-parse','HEAD').decode().strip(),'source_files':len(paths),'protected_files':len(f['protected_files']),'exact_parent_stream':str(t/'ops.bin'),'exact_parent_stream_sha256':sha(t/'ops.bin'),'scope':'Read-only official Git object verification; every source and protected byte matches the complete locally passing benchmark.'};(r/'PUBLIC-SOURCE-VERIFICATION.json').write_text(json.dumps(v,indent=2)+'\\n');(r/'OFFICIAL-RESULT.json').write_text(json.dumps({'status':'OFFICIALLY_REPRODUCED_INDEPENDENT_TOFFOLI_IMPROVEMENT','submission':sid,'Q':b['qubits'],'T':b['rounded_mean_executed_toffoli'],'product':b['product'],'improvement_in_T':748184-b['rounded_mean_executed_toffoli'],'evaluation_status':s['status'],'rejection_reason':s.get('rejectionReason'),'public_source_revision':revision,'global_product_record_beaten':False,'scope':'Official metrics equal complete local benchmark. IndependentT objective; global product remains lower.'},indent=2)+'\\n');print('Official source verified:',len(paths),'source files;',len(f['protected_files']),'protected files',flush=True)
'''
ast.parse(s);(r/'verify-official-source.py').write_text(s)
s='''import json,subprocess,time,urllib.request
from pathlib import Path
r=Path(__file__).resolve().parent;start=time.time();last=None
try:
 while not(r/'submission-response.json').exists() or not(r/'upload.exit').exists():assert time.time()-start<2400;time.sleep(3)
 assert(r/'upload.exit').read_text().strip()=='0';sid=json.loads((r/'submission-response.json').read_text())['submission']['id']
 while True:
  with urllib.request.urlopen('https://api.ecdsa.fail/api/submissions/'+sid,timeout=60) as response:data=json.load(response)
  s=data['submission'];state=(s['status'],s.get('officialMetrics'),s.get('submissionCommitSha'));(r/'submission-status.json').write_text(json.dumps(data,indent=2)+'\\n')
  if state!=last:print(json.dumps({'id':sid,'status':s['status'],'officialMetrics':s.get('officialMetrics'),'officialScore':s.get('officialScore'),'rejectionReason':s.get('rejectionReason')}),flush=True);last=state
  if s.get('officialMetrics') and(s['status']=='accepted' or s['status']=='rejected' and s.get('rejectionReason')=='score did not improve current best'):subprocess.run(['python3',str(r/'verify-official-source.py')],cwd=r,check=True);break
  if s['status'] in ['failed','rejected','cancelled']:raise RuntimeError('Official verification failed; preserve result, never blindly resubmit')
  assert time.time()-start<2400;time.sleep(30)
 (r/'official-check.exit').write_text('0\\n')
except Exception:
 (r/'official-check.exit').write_text('1\\n');raise
'''
ast.parse(s);(r/'wait-official.py').write_text(s);print(r)
