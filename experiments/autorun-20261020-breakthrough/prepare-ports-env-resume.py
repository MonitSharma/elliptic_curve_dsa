from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-exact-native-ports-v3-20261020';s=(r/'run.py').read_text();s=s.replace("r=Path(__file__).resolve().parent;t=r/'observer';", "r=Path(__file__).resolve().parent;t=r/'observer';os.environ['PEBBLE_HARD_CAP']='1234';")
a="run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());counts=[]";assert s.count(a)==1;s=s.replace(a,"assert(r/'run.exit').read_text().strip()=='1'and not(r/'RESULT.json').exists();f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());counts=[]")
s=s.replace("name='tests-'+str(i)","name='tests-env-'+str(i)").replace("(r/'run.exit').write_text('0\\n')","(r/'resumed.exit').write_text('0\\n')").replace("(r/'run.exit').write_text('1\\n')","(r/'resumed.exit').write_text('1\\n')");(r/'resume.py').write_text(s)
(r/'ENVIRONMENT-REPAIR.md').write_text('''The original v3 runner omitted PEBBLE_HARD_CAP for retained native tests.
The first rail strip test passes6,416,896 lanes, then retained tests0..11 pass;
tests12 stop at phase_fit::cap NotPresent before arithmetic execution. Original
run.exit1 and all logs remain. Resume sets the already required baseline1234
environment, changes NO source byte or guard, and reruns all16 filters under new
tests-env-* logs before the four originally declared cases. Source-freeze and
protected hashes must remain equal throughout. Result status is resumed.exit;
the original failed controller status remains recorded. No final gate/nonce.
''');print('Prepared unchanged-source environment repair and independently logged rerun.')
