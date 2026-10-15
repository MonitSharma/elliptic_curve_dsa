from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parent
assert not (root/'launch.pid').exists() and not (root/'run.exit').exists()
memory={line.split(':',1)[0]:int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines()}
assert memory['MemAvailable']>=100*1024*1024
binding=json.loads((root/'COMPOSITE_BINDING.json').read_text())
checks=[]
for item in binding['artifacts']:
    path=Path(item['path']);assert path.is_relative_to('/home/hclau/ecdsa_research')
    actual=hashlib.sha256(path.read_bytes()).hexdigest();assert actual==item['sha256'],str(path)
    checks.append(item)
(root/'LAUNCH_BINDINGS_VERIFIED.json').write_text(json.dumps({'artifacts':checks,'available_memory_kib':memory['MemAvailable'],'new_build_threads':2,'new_runtime_threads':2,'authority':False},indent=2)+'\n')
with (root/'launch.log').open('wb') as log:
    proc=subprocess.Popen(['nohup','bash',str(root/'run.sh')],cwd=root,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(root/'launch.pid').write_text(str(proc.pid)+'\n')
print(json.dumps({'pid':proc.pid,'root':str(root),'disabled_only':True}))
