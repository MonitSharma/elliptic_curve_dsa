import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;native=ws/'breakthrough-exact-native-ports-v3-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
try:
 while not(native/'resumed.exit').exists():time.sleep(2)
 assert(native/'resumed.exit').read_text().strip()=='0'and not(r/'PLAN.json').exists();f=json.loads((native/'SOURCE-FREEZE.json').read_text());a=json.loads((native/'RESULT.json').read_text());assert a['native_controls']==27 and all(sha(native/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());paths={'publica4ee':ws/'breakthrough-public322-square-final-20261020/candidate/ops.bin'};assert sha(paths['publica4ee'])=='54c8cd60337d1afaa36ff37ae0b29f321838df707350704def8a02e3e8716e69'
 for row in a['cases']:
  name=row['mode'];path=native/name/'ops.bin';assert sha(path)==row['output_compressed_sha256'];paths[name]=path
 plan={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'exact-native-rail-g6-development-20261020-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p)for n,p in paths.items()},'native_source_freeze_sha256':sha(native/'SOURCE-FREEZE.json'),'scope':'Single predeclared512-batch development comparison of fixed frozen control,rail,G6,both sources versus exact officiala4ee. Every full output lane/ancilla hash and value/phase/dirty count retained; source and raw choices frozen before these inputs. Same strengthened comparison/public140 schedule, exact ports only. No final failure-rate gate, nonce screening, benchmark or scored result. All prior failed assembly/environment logs remain.'};(r/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True)
except BaseException:
 (r/'run.exit').write_text('1\n');raise
