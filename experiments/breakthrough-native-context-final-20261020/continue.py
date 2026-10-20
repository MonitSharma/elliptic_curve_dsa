"""Run each declared stage once, retaining every outcome; stop on failure."""
import json,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
finished=ws/'breakthrough-native-context-finished-v3-20261020'
gate=ws/'breakthrough-native-context-final-gate-20261020'
nonce=ws/'breakthrough-native-context-nonce-20261020'
def run(directory,script,name):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(['python3',str(directory/script)],cwd=directory,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,(name,rc)
try:
 while not(finished/'run.exit').exists():time.sleep(2)
 assert(finished/'run.exit').read_text().strip()=='0'
 while not(gate/'controller.exit').exists():time.sleep(2)
 assert(gate/'controller.exit').read_text().strip()=='0','Original final gate controller failed; never rerun or relabel'
 assert json.loads((gate/'GATE-RESULT.json').read_text())['verdict']=='FAILURE_RATE_GATE_PASS','Final failed verdict preserved; no nonce screening'
 run(nonce,'run.py','qualified-nonce')
 run(r,'finalize.py','final-rebuild')
 run(r,'seal.py','source-review')
 (r/'continue.exit').write_text('0\n');print('Ready for independent local evidence verification before upload.',flush=True)
except BaseException:
 (r/'continue.exit').write_text('1\n');raise
