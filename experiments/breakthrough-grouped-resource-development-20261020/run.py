import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;source=ws/'breakthrough-grouped-exact-resource-grid-v2-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
try:
 start=time.time()
 while not(source/'run.exit').exists():assert time.time()-start<14400;time.sleep(2)
 assert(source/'run.exit').read_text().strip()=='0';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());result=json.loads((source/'RESULT.json').read_text());assert result['native_controls']==34 and all(sha(source/'observer'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());assert next(x for x in result['cases']if x['mode']=='control')['stream_sha256']=='a871e42c3a40aa7fe228f68b8024a7167e57cdafbfd6732e19b650d2e6f845b9';assert next(x for x in result['cases']if x['mode']=='groups-safe28-d8')['stream_sha256']=='dc1478c1ae14c86e6ab8f94d707599c5c74d5b861bb6dfb7e991a15d2a0d679d';paths={'public71':ws/'breakthrough-groups-context-final-20261020/candidate/ops.bin'};assert sha(paths['public71'])=='278802f0728d9233297723c88dffef8544bd9c3ce9968d34a2c3f406b383688a'
 for row in result['cases']:
  if row['exit']==0 and row['mode']!='control':paths[row['mode']]=source/row['mode']/'ops.bin';assert sha(paths[row['mode']])==row['stream_sha256']
 plan={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'grouped-resource-grid-development-20261020-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p)for n,p in paths.items()},'native_source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),'scope':'Fresh full-output development of the predeclared exact square-depth/workspace grid. All architecture choices/source frozen before inputs. Same strong precision/windows/rounds; resource caps may change replay chunks. Compare actual executedT, full outputs/phase/dirty; proxy is unreliable for OR-of-measurement guards. No finished candidate/finalgate/nonce/benchmark/score. Best exact resource architecture may later get regenerated cache and independent finalgate.'};(r/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True);(r/'controller.exit').write_text('0\n')
except BaseException:
 (r/'controller.exit').write_text('1\n');raise
