"""Resume setup failure without changing the frozen circuit or gate inputs."""
from pathlib import Path
import hashlib, json, subprocess

a = Path(__file__).resolve().parent
ex = a.parent
r = ex / 'breakthrough-public-semantic-finished-20261021'
g = ex / 'breakthrough-public-semantic-final-gate-20261021'
original = (a / 'run-public-semantic-server.py').read_text()
prefix = original[:original.index('try:\n')]
preflight = original[original.index(" assert socket.gethostname()"):original.index(' spec=json.loads')]
verify = ''' spec=json.loads((r/'SOURCE-SPEC.json').read_text());local=json.loads((r/'LOCAL-GENERATION.json').read_text());freeze=json.loads((r/'SOURCE-FREEZE.json').read_text())
 assert (r/'pipeline.exit').read_text().strip()=='1' and (r/'reuse-build.exit').read_text().strip()=='1'
 assert not (ws/'breakthrough-public-semantic-final-gate-20261021/GATE-DECLARATION.json').exists()
 assert subprocess.check_output(['git','-C',str(t),'rev-parse','HEAD']).decode().strip()==freeze['source_revision']
 assert len(freeze['source_files'])==187 and len(freeze['protected_files'])==17
 assert all(sha(t/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
 assert sha(r/'SOURCE-SPEC.json')==freeze['source_spec_sha256']==local['source_spec_sha256']
 assert sha(r/'git-source.patch')==freeze['git_source_patch_sha256']
 assert not (t/'target').exists()
 run(['cp','-a','--reflink=auto',str(ws/'breakthrough-de8-repeat-final-20261020/candidate/target'),str(t/'target')],'reuse-build',r)
'''
body = original[original.index(' env=dict(os.environ'):original.index('except BaseException:')]
for name in ['native','build','generate','stats','finished-development','sole-final-gate']:
    body = body.replace("'"+name+"'", "'v2-"+name+"'")
body = body.replace("r/'native.log'", "r/'v2-native.log'")
body = body.replace("r/'run.exit'", "r/'validation-v2.exit'")
body = body.replace("gate/'run.py'", "gate/'run-v2.py'")
body = body.replace("r/'PIPELINE-RESULT.json'", "r/'PIPELINE-RESULT-V2.json'")
body = body.replace("r/'pipeline.exit'", "r/'pipeline-v2.exit'")
prefix = prefix.replace("name+'.log'", "'v2-'+name+'.log'").replace("name+'.pid'", "'v2-'+name+'.pid'").replace("name+'.exit'", "'v2-'+name+'.exit'")
# Prefix adds v2 once to every operation, so keep original logical names in body.
body = body.replace("'v2-native'", "'native'").replace("'v2-build'", "'build'").replace("'v2-generate'", "'generate'").replace("'v2-stats'", "'stats'").replace("'v2-finished-development'", "'finished-development'").replace("'v2-sole-final-gate'", "'sole-final-gate'")
preflight = preflight.replace("r/'resource-preflight.json'", "r/'resource-preflight-v2.json'")
ending = '''except BaseException:
 if not(r/'validation-v2.exit').exists():(r/'validation-v2.exit').write_text('1\\n')
 (r/'pipeline-v2.exit').write_text('1\\n');(r/'PIPELINE-ERROR-V2.txt').write_text(traceback.format_exc());raise
'''
(r/'server-run-v2.py').write_text(prefix+'try:\n'+preflight+verify+body+ending)
(g/'declare-v2.py').write_text((g/'declare.py').read_text().replace("c/'run.exit'", "c/'validation-v2.exit'"))
(g/'run-v2.py').write_text((g/'run.py').read_text().replace("c/'run.exit'", "c/'validation-v2.exit'").replace("r/'declare.py'", "r/'declare-v2.py'"))
for p in [r/'server-run-v2.py',g/'declare-v2.py',g/'run-v2.py']:
    compile(p.read_text(),str(p),'exec')
    subprocess.run(['scp','-o','BatchMode=yes',str(p),'smu_server:/home/hclau/ecdsa_research/'+p.parent.name+'/'+p.name],check=True)
launch = '''import hashlib,json,os,socket,subprocess
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/breakthrough-public-semantic-finished-20261021')
assert socket.gethostname()=='LHC-104-070' and not(r/'pipeline-v2.pid').exists()
assert int(next(x for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')).split()[1])>100*1024**2
assert not(r.parent/'breakthrough-public-semantic-final-gate-20261021/GATE-DECLARATION.json').exists()
with(r/'pipeline-v2.log').open('xb')as out:
 p=subprocess.Popen(['nohup','python3','-u',str(r/'server-run-v2.py')],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(r/'pipeline-v2.pid').write_text(str(p.pid)+'\\n')
v={'pid':p.pid,'source_revision':json.loads((r/'SOURCE-FREEZE.json').read_text())['source_revision'],'driver_sha256':hashlib.sha256((r/'server-run-v2.py').read_bytes()).hexdigest(),'scope':'Unchanged source, original setup failure preserved. No earlier gate declared.'}
(r/'SERVER-LAUNCH-V2.json').write_text(json.dumps(v,indent=2)+'\\n');print(json.dumps(v))
'''
p=r/'launch-v2-server.py';p.write_text(launch)
subprocess.run(['scp','-o','BatchMode=yes',str(p),'smu_server:/home/hclau/ecdsa_research/'+r.name+'/'+p.name],check=True)
out=subprocess.check_output(['ssh','-o','BatchMode=yes','smu_server','python3','/home/hclau/ecdsa_research/'+r.name+'/'+p.name],text=True)
(r/'SERVER-LAUNCH-V2.json').write_text(json.dumps(json.loads(out.strip().splitlines()[-1]),indent=2)+'\n')
print(out)
