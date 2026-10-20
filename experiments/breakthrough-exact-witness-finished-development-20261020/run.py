import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;source=ws/'breakthrough-exact-witness-finished-20261020';old=ws/'breakthrough-exact-ports-development-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
try:
 start=time.time()
 while not(source/'run.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(source/'run.exit').read_text().strip()=='0';a=json.loads((source/'RESULT.json').read_text());sf=json.loads((source/'SOURCE-FREEZE.json').read_text());assert a['native_tests']==7 and a['independent_proof_controls']==9 and a['qubits']<=1664;assert all(sha(source/'candidate'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());paths={'public2bd':ws/'breakthrough-depth12-final-20261020/candidate/ops.bin','witness':source/'candidate/ops.bin'};assert sha(paths['public2bd'])=='63370be6078a4a80454d5174a5f07bfac094fea6af3dd526f77dc8194012cc29'and sha(paths['witness'])==a['stream_sha256'];plan={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'witness-finished-development-20261020-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p)for n,p in paths.items()},'native_source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),'scope':'Fresh full-output development512x64/source on final selectedfull259witness/sharedsum/literal0/freshcache source, compared against exactpublishedT2bd Q1464/T747218. Native7/proof9 andwholebindings passed before inputs. No new approximatewindow/cut/precision/round. Preserve all output/value/phase/dirty mismatches. Not final-gated, nonce-screened, benchmarked or scored.'};(r/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
 subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True);d=json.loads((r/'DIAGNOSTIC.json').read_text());assert d['summaries']['witness']['dirty_shots']==0;(r/'controller.exit').write_text('0\n')
except Exception:
 (r/'run.exit').write_text('1\n');(r/'controller.exit').write_text('1\n');raise
