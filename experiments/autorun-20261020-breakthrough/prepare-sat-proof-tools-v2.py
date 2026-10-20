from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'run-sat-proof-tools.py').read_text().replace("resource.setrlimit(resource.RLIMIT_AS,","resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,")
start=s.index(" assert(source/'solver-controller.exit')");end=s.index(" kissat=repos/'kissat'",start)
s=s[:start]+''' import shutil
 previous=r.parent/'breakthrough-sat-proof-tools-20261020';assert(previous/'run.exit').read_text().strip()=='1';assert 'shadow' in(previous/'tests-kissat.log').read_text()
 original=json.loads((source/'SOLVER-DECLARATION.json').read_text());assert sha(source/'wrongpoint.cnf')==original['cnf_sha256'];oldfreeze=json.loads((previous/'SOURCE-FREEZE.json').read_text());freeze=oldfreeze['repositories'];assert all(sha(previous/'tool-repos'/name/p)==h for name,f in freeze.items()for p,h in f['files'].items());shutil.copytree(previous/'tool-repos',repos,symlinks=True)
 for name,f in freeze.items():shutil.copyfile(previous/(name+'-source.tar.gz'),r/(name+'-source.tar.gz'));assert sha(r/(name+'-source.tar.gz'))==f['source_archive_sha256']
 (r/'SOURCE-FREEZE.json').write_text(json.dumps({'repositories':freeze,'driver_sha256':sha(Path(__file__)),'previous_failed_driver_sha256':oldfreeze['driver_sha256'],'scope':'Exact previously frozen compiled tool/source copies. Original root-only permission test failure preserved. Rerun ALL tests as existing unprivileged nobody with explicit-j2; no source test skipped or OS permissions changed.'},indent=2)+'\\n')
''' +s[end:]
needle="run(['./configure'],'configure',kissat);run(['make','-j2'],'build-kissat',kissat,timeout=300);run(['make','-j2','test'],'tests-kissat',kissat,timeout=300);"
assert s.count(needle)==1
s=s.replace(needle,"run(['runuser','-u','nobody','--',str(kissat/'build/tissat'),'-j2'],'tests-kissat-unprivileged',kissat/'build',timeout=300);")
ast.parse(s);(a/'run-sat-proof-tools-v2.py').write_text(s)
s=(a/'prepare-sat-proof-tools.py').read_text().replace('breakthrough-sat-proof-tools-20261020','breakthrough-sat-proof-tools-v2-20261020').replace("a/'run-sat-proof-tools.py'","a/'run-sat-proof-tools-v2.py'")
ast.parse(s)
exec(compile(s,str(a/'prepare-sat-proof-tools.py'),'exec'))
