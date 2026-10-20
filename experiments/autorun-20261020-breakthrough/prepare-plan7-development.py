from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-stackv3-plan7-development-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'PLAN.md').write_text('''# Fresh full-output development comparison for fixed1233/t28 source

Wait for generic-v2 generation/native14controls. Freeze its complete source,
output stream and the protected diagnostic tool before any new inputs.
Predeclare512x64 fresh batches under stackv3-plan7-28-generic-development-20261020-v1,
four workers, eight batches additionally replayed in the unchanged scalar
simulator. Compare exactpublice3 stream714c and the fixed stronger28-bit witness,
loan128, both-direction nativeplan7 plus generic exact pipeline. Preserve every
wrongvalue, phase, dirty, target-lane and other-lane difference. Report actual
executedstreamToffolis only as development measurements. This is not a final
failure-rate gate, nonce search, unchanged benchmark or scored record.
''')
(r/'run.py').write_text('''import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;source=ws/'breakthrough-stackv3-plan7-generic-v2-20261020';old=ws/'breakthrough-exact-ports-development-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
try:
 start=time.time()
 while not(source/'run.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(source/'run.exit').read_text().strip()=='0';a=json.loads((source/'RESULT.json').read_text());sf=json.loads((source/'SOURCE-FREEZE.json').read_text());assert a['native_tests']==14 and a['qubits']==1233;assert all(sha(source/'candidate'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());paths={'publice3':ws/'breakthrough-stackv3-width-plan7-both-20261020/public/ops.bin','generic1233':source/'candidate/ops.bin'};assert sha(paths['publice3'])=='714c4e4c1c2c5c59544dcc3ade28587663b616d46a168b0fcd22a06c29c0916f'and sha(paths['generic1233'])==a['stream_sha256'];plan={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'stackv3-plan7-28-generic-development-20261020-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':{n:sha(p)for n,p in paths.items()},'native_source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),'scope':'Fresh full-output development512x64/source, fixed1233/t28 nativeplan7+generic once vs exactpublice3. Preserve all output/value/phase/dirty mismatches. Not final-gated, nonce-screened, benchmarked or scored.'};(r/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\\n')
 s=(old/'diagnostic.py').read_text();s=s.replace("candidate=ws/'breakthrough-exact-native-ports-v3-20261020'","candidate=ws/'breakthrough-stackv3-plan7-generic-v2-20261020'").replace("candidate/'observer'/p","candidate/'candidate'/p").replace("records['publica4ee']","records['publice3']").replace("name=='publica4ee'","name=='publice3'");(r/'diagnostic.py').write_text(s);subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True)
except Exception:
 (r/'run.exit').write_text('1\\n');raise
''');print(r)
