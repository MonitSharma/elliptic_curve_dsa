from pathlib import Path
import json,subprocess
a=Path(__file__).resolve().parent;ex=a.parent;r=ex/'breakthrough-public-semantic-finished-20261021';g=ex/'breakthrough-public-semantic-final-gate-20261021';dest='/home/hclau/ecdsa_research/'
for n in ['PIPELINE-ERROR-V2.txt','validation-v2.exit','pipeline-v2.exit','RESULT.json','OUTPUT-STATS.json','resource-preflight-v2.json','v2-native.log','v2-native.exit','v2-build.log','v2-build.exit','v2-generate.log','v2-generate.exit','v2-stats.log','v2-stats.exit']:
 subprocess.run(['scp','-o','BatchMode=yes','smu_server:'+dest+r.name+'/'+n,str(r/n)],check=True)
s=(r/'server-run-v2.py').read_text();prefix=s[:s.index('try:\n')].replace("'v2-'+name", "'v3-'+name")
pre=s[s.index(' assert socket.gethostname()'):s.index(' spec=json.loads')].replace('resource-preflight-v2.json','resource-preflight-v3.json')
checks=''' spec=json.loads((r/'SOURCE-SPEC.json').read_text());freeze=json.loads((r/'SOURCE-FREEZE.json').read_text());result=json.loads((r/'RESULT.json').read_text())
 assert (r/'validation-v2.exit').read_text().strip()=='0'
 assert subprocess.check_output(['git','-C',str(t),'rev-parse','HEAD']).decode().strip()==freeze['source_revision']
 assert all(sha(t/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
 assert sha(r/'SOURCE-FREEZE.json')==result['source_freeze_sha256'] and sha(t/'ops.bin')==result['stream_sha256']
 assert not (ws/'breakthrough-public-semantic-final-gate-20261021/GATE-DECLARATION.json').exists()
 assert not (ws/'breakthrough-public-semantic-finished-development-20261021/public1829.out').exists()
 env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
'''
body=s[s.index(" dev=ws/'breakthrough-public-semantic-finished-development"):s.index('except BaseException:')]
body=body.replace('breakthrough-public1829-reproduction-20261020/candidate/ops.bin','breakthrough-public1829-reproduction-20261020/parent/ops.bin').replace("gate/'run-v2.py'", "gate/'run-v3.py'").replace('PIPELINE-RESULT-V2.json','PIPELINE-RESULT-V3.json').replace('pipeline-v2.exit','pipeline-v3.exit')
ending='''except BaseException:
 (r/'pipeline-v3.exit').write_text('1\\n');(r/'PIPELINE-ERROR-V3.txt').write_text(traceback.format_exc());raise
'''
(r/'server-run-v3.py').write_text(prefix+'try:\n'+pre+checks+body+ending)
(g/'declare-v3.py').write_text((g/'declare-v2.py').read_text().replace("pt=parent/'candidate'", "pt=parent/'parent'"))
(g/'run-v3.py').write_text((g/'run-v2.py').read_text().replace("r/'declare-v2.py'", "r/'declare-v3.py'"))
for p in [r/'server-run-v3.py',g/'declare-v3.py',g/'run-v3.py']:
 compile(p.read_text(),str(p),'exec');subprocess.run(['scp','-o','BatchMode=yes',str(p),'smu_server:'+dest+p.parent.name+'/'+p.name],check=True)
launch=(r/'launch-v2-server.py').read_text().replace('pipeline-v2','pipeline-v3').replace('server-run-v2.py','server-run-v3.py').replace('SERVER-LAUNCH-V2.json','SERVER-LAUNCH-V3.json');p=r/'launch-v3-server.py';p.write_text(launch)
subprocess.run(['scp','-o','BatchMode=yes',str(p),'smu_server:'+dest+r.name+'/'+p.name],check=True)
out=subprocess.check_output(['ssh','-o','BatchMode=yes','smu_server','python3',dest+r.name+'/'+p.name],text=True);(r/'SERVER-LAUNCH-V3.json').write_text(json.dumps(json.loads(out.strip().splitlines()[-1]),indent=2)+'\n');print(out)
