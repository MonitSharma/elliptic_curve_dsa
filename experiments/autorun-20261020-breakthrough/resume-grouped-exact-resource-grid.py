from pathlib import Path
import ast
a=Path(__file__).parent;r=a.parent/'breakthrough-grouped-exact-resource-grid-20261020';s=(r/'run.py').read_text();start=s.index(" assert run(['python3','prepare.py']");end=s.index('\n fault=',start)
replacement=''' assert(r/'run.exit').read_text().strip()=='1';f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert 'Independent phase-pebble cap: NotPresent'in(r/'square-unit-junction-fault.log').read_text();assert 'G3_UT pins='not in(r/'square-unit-junction-fault.log').read_text();expected=[1,2,1,1,1,1,1,1,3,1,4,3,2,3,1,1]
 for i,n in enumerate(expected):assert f'test result: ok. {n} passed; 0 failed;'in(r/('tests-'+str(i)+'.log')).read_text()
 assert'test result: ok. 1 passed; 0 failed;'in(r/'group-plan-tests.log').read_text();unit=[]
 for mode in f['modes']:
  log=(r/('square-unit-'+mode+'.log')).read_text();rc=int((r/('square-unit-'+mode+'.exit')).read_text());assert mode=='control'or rc==0;unit.append({'mode':mode,'exit':rc,'historical_six_walk_domain_edges_excluded_by_existing_unit':True,'g3_summary':re.findall(r'^G3_UT pins=[^\\n]+',log,re.M),'edge_phase_masks':re.findall(r'^G3_UT edge[^\\n]+',log,re.M)})
'''
s=s[:start]+replacement+s[end:];s=s.replace("'G3_UT_PINS':'SQC_G1M=1;","'G3_UT_PINS':'PEBBLE_HARD_CAP=1536;SQC_G1M=1;").replace("'square-unit-junction-fault'","'resumed-square-unit-junction-fault'").replace("r/'square-unit-junction-fault.log'","r/'resumed-square-unit-junction-fault.log'")
# The preflight must continue to inspect the original failed fixture log.
s=s.replace("'Independent phase-pebble cap: NotPresent'in(r/'resumed-square-unit-junction-fault.log')","'Independent phase-pebble cap: NotPresent'in(r/'square-unit-junction-fault.log')").replace("'G3_UT pins='not in(r/'resumed-square-unit-junction-fault.log')","'G3_UT pins='not in(r/'square-unit-junction-fault.log')")
s=s.replace("(r/'run.exit').write_text('0\\n')","(r/'resumed.exit').write_text('0\\n')").replace("(r/'run.exit').write_text('1\\n')","(r/'resumed.exit').write_text('1\\n')");ast.parse(s);(r/'resume.py').write_text(s)
(r/'TEST-ENVIRONMENT-CORRECTION.md').write_text('''# Preserve the failed fault fixture and supply its missing resource setting

All27 inherited exact controls/groupplan and five new fullsquare callers pass.
The deliberate junction-fault fixture omitted PEBBLE_HARD_CAP from its pins;
G3 clears environment then stopped at phase_fit::cap NotPresent during building,
before G3 simulation or fault detection. The assertion correctly stopped all
point construction. Preserve originalrun.exit1 and every original log.

Resume only after rechecking all frozen source/protected hashes and prior
passing controls. Run the SAME predeclared deliberate-fault seed/batch count,
adding the missing unchanged-constructor1536 cap to fixture pins. Require the
intended G3 output/phase failure, then six new leaf native controls and the
fixed full grid. Source/freeze/precision/labels unchanged. No statistical gate
or nonce exists. Completion marker is resumed.exit, originalfailure remains.

Local preparation also initially searched for inherited constructor statements
in the patch generator and for a leading space absent from its controller;
both assertions stopped before a source freeze/workload. Dependent firstlaunch
was refused because run.py was missing. Corrected generatedscripts parsed
before successful transfer/launch. These are packaging/configuration failures,
not arithmetic verdicts, and never count as passed fault tests.
''');print(r/'resume.py')
