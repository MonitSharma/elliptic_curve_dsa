from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2];ex=root/'experiments'
changes={'breakthrough-native-context-finished-v3-20261020':'breakthrough-groups-context-finished-20261020','breakthrough-native-context-final-gate-20261020':'breakthrough-groups-context-final-gate-20261020','breakthrough-native-context-nonce-20261020':'breakthrough-groups-context-nonce-20261020','breakthrough-native-context-final-20261020':'breakthrough-groups-context-final-20261020','native-context499-exact-final-20261020-v1':'groups-context230-final-20261020-v1','native_context_cache.rs':'groups_context_cache.rs'}
for suffix,filename in [('nonce','run.py'),('final','finalize.py')]:
 r=ex/('breakthrough-groups-context-'+suffix+'-20261020');r.mkdir(exist_ok=False);old=ex/('breakthrough-native-context-'+suffix+'-20261020');s=(old/filename).read_text()
 for a,b in changes.items():s=s.replace(a,b)
 if suffix=='nonce':
  s=s.replace('import hashlib,json,os,subprocess','import hashlib,json,os,subprocess,time');needle="try:\n g=json.loads((gate/'GATE-RESULT.json').read_text());";assert s.count(needle)==1;s=s.replace(needle,"try:\n start=time.time()\n while not(gate/'GATE-RESULT.json').exists():\n  assert time.time()-start<7200\n  if(gate/'controller.exit').exists():assert(gate/'controller.exit').read_text().strip()=='0','Gate stopped before usable verdict; no nonce'\n  time.sleep(2)\n g=json.loads((gate/'GATE-RESULT.json').read_text());")
 else:
  # The result is loaded after the search has finished, never before source construction.
  needle="finished=json.loads((old/'RESULT.json').read_text());operation_count=finished['operations']";assert s.count(needle)==1;s=s.replace(needle,"finished=None;operation_count=None");needle=" assert(search/'run.exit').read_text().strip()=='0'";assert s.count(needle)==1;s=s.replace(needle,needle+"\n finished=json.loads((old/'RESULT.json').read_text());operation_count=finished['operations']")
 ast.parse(s);(r/filename).write_text(s)
 for n in ['.gitattributes','.gitignore']:(r/n).write_bytes((old/n).read_bytes())
 (r/'PLAN.md').write_text('Wait ownsole groups-context230-final-20261020-v1 PASS on frozen205-source candidate. Only then independent exactnonceengine source/binary/library qualification, ascendinglowest search, discloseallcontrols/screens/overrun, full9024replay. Finalsourcechangesonlynonceconstant; unchangedbenchmark/completeprefix/source/member review andfreshpublicminimum check precede automaticGPT6sol/Codex submission. No cost-basednonce selection or statisticalgate rerun.\n')
print('Prepared gated dependent nonce and unchanged benchmark controllers.')
