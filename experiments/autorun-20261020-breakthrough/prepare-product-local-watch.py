from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-public-best-drop-final-20261020';old=ex/'breakthrough-depth12-final-20261020'
s=(a/'collect-depth12-final.py').read_text().replace('breakthrough-depth12-final-20261020','breakthrough-public-best-drop-final-20261020').replace('205','177').replace('final depth12','final product')
s=s.replace("sha((r/'final-evidence.tar.gz').read_bytes())","hashlib.file_digest((r/'final-evidence.tar.gz').open('rb'),'sha256').hexdigest()")
ast.parse(s);(a/'collect-product-best-final.py').write_text(s)
shutil.copyfile(old/'wait-official.py',r/'wait-official.py')
s=(old/'verify-official-source.py').read_text().replace('==205','==177').replace("'fetch','origin',revision","'fetch','https://github.com/Layr-Labs/ecdsafail-challenge',revision").replace('OFFICIALLY_REPRODUCED_INDEPENDENT_TOFFOLI_IMPROVEMENT','OFFICIALLY_REPRODUCED_COMPLETE_PRODUCT_IMPROVEMENT').replace("'improvement_in_T':747226-b['rounded_mean_executed_toffoli']","'improvement_in_product':933231010-b['product']").replace("'global_product_record_beaten':False","'global_product_record_beaten':True").replace('IndependentT objective; global product remains lower.','Complete measured product improves the exact publicacd0 comparison parent; fresh upload preflight also compared the current public product record.')
ast.parse(s);(r/'verify-official-source.py').write_text(s)
watch='''"""Authorized local evidence verification, then one-shot challenge upload."""
import hashlib,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
a=Path(__file__).resolve().parent;root=a.parents[1];r=root/'experiments/breakthrough-public-best-drop-final-20261020';remote='/home/hclau/ecdsa_research/breakthrough-public-best-drop-final-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args,name):
 with(r/('local-'+name+'.log')).open('xb')as out:p=subprocess.Popen(args,cwd=root,stdout=out,stderr=subprocess.STDOUT);(r/('local-'+name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/('local-'+name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
try:
 assert not(r/'LOCAL-WATCH-DECLARATION.json').exists();collector=a/'collect-product-best-final.py';frozen=sha(collector);(r/'LOCAL-WATCH-DECLARATION.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'collector_sha256':frozen,'policy':'Wait for complete lowest-pass benchmark/seal. Independently verify every immutable evidence/source member locally. Upload local verification receipt; execute prepared one-shot submit only after fresh public product comparison. Never duplicate an uncertain upload, retry a failed gate or select another nonce by cost. Then read official outcome and verify every public source/protected Git-object byte. Automatic shared-main push remains prohibited/pending approval.'},indent=2)+'\\n')
 while True:
  p=subprocess.run(['ssh','smu_server',f'if test -f {remote}/review.exit; then cat {remote}/review.exit; else echo WAITING; fi'],capture_output=True,text=True,timeout=60)
  if p.returncode:raise RuntimeError('SSH read failed; preserve state and inspect before further work')
  state=p.stdout.strip();assert state in['WAITING','0','1'],state
  if state=='1':raise RuntimeError('Final benchmark/packaging failed; preserve evidence and inspect, no upload')
  if state=='0':break
  time.sleep(30)
 assert sha(collector)==frozen;run([sys.executable,str(collector)],'collection')
 receipt=json.loads((r/'LOCAL-VERIFICATION.json').read_text());assert receipt['status']=='EVERY_FINAL_EVIDENCE_AND_SOURCE_MEMBER_VERIFIED_LOCALLY'and receipt['source_files']==177
 run(['scp',str(r/'LOCAL-VERIFICATION.json'),'smu_server:'+remote+'/LOCAL-VERIFICATION.json'],'verification-receipt')
 run(['ssh','smu_server','python3 '+remote+'/submit.py'],'submit')
 # Upload has one-shot markers; any failure above is final for this watcher.
 run(['ssh','smu_server','python3 '+remote+'/wait-official.py'],'official-check')
 for name in['submission-response.json','submission-status.json','PUBLIC-SOURCE-VERIFICATION.json','OFFICIAL-RESULT.json','official-check.exit','PREUPLOAD-AUDIT.json','upload.exit','UPLOAD-STARTED.json']:
  run(['scp','smu_server:'+remote+'/'+name,str(r/name)],'fetch-'+name.replace('.','-'))
 (r/'local-watch.exit').write_text('0\\n');print((r/'OFFICIAL-RESULT.json').read_text(),flush=True)
except BaseException:
 (r/'local-watch.exit').write_text('1\\n');raise
'''
ast.parse(watch);(a/'watch-product-best-local.py').write_text(watch);print('Local verification and one-shot authorized upload watcher prepared.')
