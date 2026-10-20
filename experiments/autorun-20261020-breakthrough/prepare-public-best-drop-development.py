from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-groups-context-development-20261020';r=a.parent/'breakthrough-public-best-drop-development-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'diagnostic.py').read_text().replace('breakthrough-groups-context-finished-20261020','breakthrough-public-best-drop-finished-20261020').replace("records['public8d']","records['publicacd0']").replace("name=='public8d'","name=='publicacd0'");ast.parse(s);(r/'diagnostic.py').write_text(s)
s='''import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;source=ws/'breakthrough-public-best-drop-finished-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
try:
 start=time.time()
 while not(source/'run.exit').exists():assert time.time()-start<14400;time.sleep(2)
 assert(source/'run.exit').read_text().strip()=='0';a=json.loads((source/'RESULT.json').read_text());sf=json.loads((source/'SOURCE-FREEZE.json').read_text());assert a['native_tests']==1 and a['independent_proof_controls']==9 and a['qubits']==1233;assert all(sha(source/'candidate'/p)==h for p,h in {**sf['source_files'],**sf['protected_files']}.items());paths={'publicacd0':ws/'breakthrough-public-acd0-reproduction-20261020/parent/ops.bin','bestdrop':source/'candidate/ops.bin'};assert sha(paths['publicacd0'])=='3d7c94f1dea887dd2d4ff13326e350756350cc1044d396444c3f820f8bfad827'and sha(paths['bestdrop'])==a['stream_sha256'];plan={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'public-best-drop-development-20261020-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p)for n,p in paths.items()},'native_source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),'scope':'Fresh full-output development on final resource-selected fixed exact carry schedule and newly proved cache. Source/profile/cache selected before inputs solely by fixed-grid static resources. Parent exactpublicacd0. Preserve full wrongoutput/phase/dirty differences. Not finalgate/nonce/benchmark/score.'};(r/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\\n');subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True);d=json.loads((r/'DIAGNOSTIC.json').read_text());assert d['summaries']['bestdrop']['dirty_shots']==0;assert not d['comparisons']['bestdrop']['different_other_lanes'];(r/'controller.exit').write_text('0\\n')
except BaseException:
 (r/'controller.exit').write_text('1\\n');raise
''';ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Fresh full-output development after resource-only final source selection

Wait final frozen best-drop source with native cache runtime1/independentproof9
and prior exact comparator/plan/policy controls. Labelpublic-best-drop-development-
20261020-v1,512x64 per source, four workers/eight protectedscalarbatches each.
Parent exactpublicacd0 stream3d7c versus complete bound candidate nonce0. Record
all values, phase, dirty, other-register differences and actual executedT.
Resource selection across the fixed grids occurred before these fresh inputs.
No finalgate/nonce/benchmark/record. Planned ownfinalgate131072x64/source has
one fresh label declared before census after this source is independently checked;
never rerun/relabel/extend any declared verdict. Auto official submission only
after qualifiedascendingnonce/fullunchanged9024benchmark/localmember review.
''');print(r)
