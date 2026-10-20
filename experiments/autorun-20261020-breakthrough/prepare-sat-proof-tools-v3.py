from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'run-sat-proof-tools.py').read_text().replace("resource.setrlimit(resource.RLIMIT_AS,","resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,")
start=s.index(" assert(source/'solver-controller.exit')");end=s.index(" kissat=repos/'kissat'",start)
s=s[:start]+''' import shutil
 previous=r.parent/'breakthrough-sat-proof-tools-20261020';oldfreeze=json.loads((previous/'SOURCE-FREEZE.json').read_text());freeze=oldfreeze['repositories'];original=json.loads((source/'SOLVER-DECLARATION.json').read_text());assert sha(source/'wrongpoint.cnf')==original['cnf_sha256'];repos.mkdir()
 for name,f in freeze.items():
  old=previous/'tool-repos'/name;t=repos/name;t.mkdir()
  for p,h in f['files'].items():
   assert sha(old/p)==h;p2=t/p;p2.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/p,p2,follow_symlinks=False)
  shutil.copytree(old/'.git',t/'.git');assert not subprocess.check_output(['git','-C',str(t),'status','--porcelain']).strip();shutil.copyfile(previous/(name+'-source.tar.gz'),r/(name+'-source.tar.gz'));assert sha(r/(name+'-source.tar.gz'))==f['source_archive_sha256']
 (r/'SOURCE-FREEZE.json').write_text(json.dumps({'repositories':freeze,'driver_sha256':sha(Path(__file__)),'build_mode':'Official configure-g assertion/debug build; all native tests under existing nobody/j2','scope':'Fresh exact tracked source/.git copies, no previous generated build files. Earlier root-permission and too-fast SIGINT timing failures retained; no tests skipped or source changes.'},indent=2)+'\\n')
''' +s[end:]
needle="run(['./configure'],'configure',kissat);run(['make','-j2'],'build-kissat',kissat,timeout=300);run(['make','-j2','test'],'tests-kissat',kissat,timeout=300);"
assert s.count(needle)==1
s=s.replace(needle,"run(['./configure','-g'],'configure-debug',kissat);run(['make','-j2'],'build-kissat-debug',kissat,timeout=300);run(['make','-C','build','-j2','tissat'],'build-native-tests',kissat,timeout=300);run(['runuser','-u','nobody','--',str(kissat/'build/tissat'),'-j2'],'tests-kissat-debug-unprivileged',kissat/'build',timeout=300);")
ast.parse(s);(a/'run-sat-proof-tools-v3.py').write_text(s)
s=(a/'prepare-sat-proof-tools.py').read_text().replace('breakthrough-sat-proof-tools-20261020','breakthrough-sat-proof-tools-v3-20261020').replace("a/'run-sat-proof-tools.py'","a/'run-sat-proof-tools-v3.py'")
ast.parse(s)
exec(compile(s,str(a/'prepare-sat-proof-tools.py'),'exec'))
