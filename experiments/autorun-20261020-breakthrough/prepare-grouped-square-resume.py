from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-grouped-square-ports-20261020';s=(r/'run.py').read_text();start=s.index(" assert run(['python3','prepare.py']");end=s.index(" for mode in f['modes']:",start)
replacement=''' assert(r/'run.exit').read_text().strip()=='1';f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());expected=[1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]
 for i,n in enumerate(expected):assert re.findall(r'test result: ok\\. (\\d+) passed; 0 failed;',(r/('tests-'+str(i)+'.log')).read_text())==[str(n)]
 assert 'test result: ok. 1 passed; 0 failed;'in(r/'group-plan-tests.log').read_text();assert 'Independent phase-pebble cap: NotPresent'in(r/'square-unit-groups-safe28-d0.log').read_text();unit=[]
'''
s=s[:start]+replacement+s[end:]
s=s.replace("pins='SQC_G1M='","pins='PEBBLE_HARD_CAP=1536;SQC_G1M='").replace("'G3_UT_PINS':'SQC_G1M=1;","'G3_UT_PINS':'PEBBLE_HARD_CAP=1536;SQC_G1M=1;")
s=s.replace("'square-unit-'+mode","'resumed-square-unit-'+mode").replace("'square-unit-junction-fault'","'resumed-square-unit-junction-fault'").replace("r/'square-unit-junction-fault.log'","r/'resumed-square-unit-junction-fault.log'")
s=s.replace("'build')==0","'resumed-build')==0").replace("'generate-'+mode","'resumed-generate-'+mode").replace("'stats-'+mode","'resumed-stats-'+mode").replace("(r/'run.exit').write_text('0\\n')","(r/'resumed.exit').write_text('0\\n')").replace("(r/'run.exit').write_text('1\\n')","(r/'resumed.exit').write_text('1\\n')")
(r/'resume.py').write_text(s)
(r/'TEST-ENVIRONMENT-CORRECTION.md').write_text('''# Missing native test setting, not an arithmetic verdict

Original27 exact controls and groupedplan control passed. The G3 unit clears
its environment before installing supplied pins; its old driver forgot to put
PEBBLE_HARD_CAP in those pins. It stopped at phase_fit::cap NotPresent during
construction, before simulation. Preserve originalrun.exit1 and all logs.

Resumed unit pins set PEBBLE_HARD_CAP1536 (the unchanged currentT constructor's
own value), with local square phasecap1408, and repeat all three square unit
cases and the deliberate junction fault before any full construction. No
source/freeze/precision/label changes. All native input batches remain fixed.
No statistical gate or nonce exists for this line. Completion is resumed.exit.
''');print(r/'resume.py')
