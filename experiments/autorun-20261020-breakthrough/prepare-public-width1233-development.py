from pathlib import Path
import ast
a=Path(__file__).parent;r=a.parent/'breakthrough-public-width1233-development-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
template=(a.parent/'breakthrough-groups-context-development-20261020/diagnostic.py').read_text();start=template.index(";candidate=ws/");end=template.index(";paths={name:",start)
template=template[:start]+";observer=ws/'breakthrough-output-audit-20261020';tf=json.loads((observer/'TOOL-SOURCE-FREEZE-v2.json').read_text());exe=observer/'tool/target/release/product_paired_diagnostic'\nassert all(sha(observer/'tool-v2'/p)==h for p,h in tf['source_files'].items());assert all(sha(Path(p))==h for p,h in tf['protected_dependency_files'].items())"+template[end:]
template=template.replace("sha(candidate/'SOURCE-FREEZE.json')","f['candidate_source_freeze_sha256']").replace("records['public8d']","records['publicacd0']").replace("name=='public8d'","name=='publicacd0'")
ast.parse(template);(r/'diagnostic.py').write_text(template)
s='''import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
try:
 sources=[('breakthrough-public-acd0-reproduction-20261020','parent'),('breakthrough-public-acd0-exact-width-20261020','observer')];source_freezes={}
 for name,tree in sources:
  d=ws/name;assert(d/'run.exit').read_text().strip()=='0';sf=json.loads((d/'SOURCE-FREEZE.json').read_text());assert all(sha(d/tree/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());source_freezes[name]=sha(d/'SOURCE-FREEZE.json')
 d=ws/'breakthrough-public-width1233-context-20261020';assert(d/'run.exit').read_text().strip()=='0';pf=json.loads((d/'SOURCE-FREEZE.json').read_text());assert all(sha(d/'tool'/p)==h for p,h in pf['tool_source_files'].items());paths={'publicacd0':ws/'breakthrough-public-acd0-reproduction-20261020/parent/ops.bin','width1233':ws/'breakthrough-public-acd0-exact-width-20261020/cap1233-t21/ops.bin','cache113':d/'zero-donors.ops.bin'};expected={'publicacd0':'3d7c94f1dea887dd2d4ff13326e350756350cc1044d396444c3f820f8bfad827','width1233':'52a065e97ec0cf5159dd52da0df18b427bd906fbbc588028fe750d82c25e3c54','cache113':'71983c1987979228f2d3c4ddf371796dd6c7d9e72e634abf9c0cbdb40764e5d6'};assert all(sha(paths[n])==h for n,h in expected.items())
 plan={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'public-width1233-cache113-development-20261020-v1','batches':512,'shots_per_batch':64,'workers':4,'protected_scalar_batches':8,'paths':{n:str(p)for n,p in paths.items()},'streams':expected,'source_freezes':source_freezes,'candidate_source_freeze_sha256':source_freezes['breakthrough-public-acd0-exact-width-20261020'],'proof_source_freeze_sha256':sha(d/'SOURCE-FREEZE.json'),'scope':'Fresh full-output development on frozen complete prototype streams, not assembled submission sources. Exact width/cache changes only; originalparent21bit witness. Full phase/output/dirty/protected scalar results preserved. Not finalgate/nonce/benchmark/scored.'};(r/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\\n');subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True);(r/'controller.exit').write_text('0\\n')
except BaseException:
 (r/'controller.exit').write_text('1\\n');raise
'''
ast.parse(s);(r/'run.py').write_text(s);(r/'PLAN.md').write_text('Predeclare fresh public-width1233-cache113-development-20261020-v1,512x64 per source, fourworkers, eightprotectedscalarbatches each. Exact publicacd0, frozen width1233 and context113 outputs. Resource and full-function diagnostics only; not finalgate/nonce/benchmark/score.\n');print(r)
