from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parent
assert (root/'run.exit').read_text().strip()=='127'
assert not (root/'launch-v2.pid').exists() and not (root/'run-v2.exit').exists()
assert int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))>=100*1024*1024
for item in json.loads((root/'COMPOSITE_BINDING.json').read_text())['artifacts']:
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
with (root/'launch-v2.log').open('wb') as log:
    proc=subprocess.Popen(['nohup','bash',str(root/'run-v2.sh')],cwd=root,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(root/'launch-v2.pid').write_text(str(proc.pid)+'\n')
print(json.dumps({'pid':proc.pid,'continuation':'same15preparedfiles_build_environment_PATH_fixed','disabled_only':True}))
