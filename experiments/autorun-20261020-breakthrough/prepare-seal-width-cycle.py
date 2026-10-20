from pathlib import Path
r=Path(__file__).resolve().parent
entries={
 'breakthrough-certified-prefix-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'AUDIT-RESULT.json'),
 'breakthrough-public-schedule-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'ADMISSION-RESULT.json'),
 'breakthrough-wide-generic-20261020':('tool','SOURCE_FREEZE.json','run.exit',None,[],'AUDIT-RESULT.json'),
 'breakthrough-wide-square-budget-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'ADMISSION-RESULT.json'),
 'breakthrough-wide-uniform-compare-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'ADMISSION-RESULT.json'),
 'breakthrough-spacious-budget-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'ADMISSION-RESULT.json'),
 'breakthrough-primed-pool-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[2],'ADMISSION-RESULT.json'),
 'breakthrough-wide-stronger-compare-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'ADMISSION-RESULT.json'),
 'breakthrough-wide-loan-policy-20261020':('observer','SOURCE_FREEZE.json','run-v2.exit','tests-v2.log',[1,1,1,1,1,1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-local-budget-20261020':('observer','SOURCE_FREEZE.json','run-v2.exit','tests-v2.log',[1,1,1,1,1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-local-budget-runtime-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[1,1,1,1,1,1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-wide-budget-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'ADMISSION-RESULT.json'),
 'breakthrough-sparse-polynomial-20261020':('tool','SOURCE_FREEZE.json','run.exit','tests.log',[3],'AUDIT-RESULT.json'),
 'breakthrough-t0-shared-product-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[1,1,1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-fin1-loan-native-20261020':('primitive','SOURCE_FREEZE.json','run.exit','tests.log',[1,2,1],None),
 'breakthrough-fin1-fold-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[1,1,1,1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-reverse-plan7-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[1,1,1,1,1,3,1,4,3,3,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-reverse-budget-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[1,1,1,1,1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-generic-postpass-20261020':('observer','SOURCE_FREEZE.json','run-v2.exit',None,[],'AUDIT-RESULT-v2.json'),
 'breakthrough-truth14-20261020':('tool','SOURCE_FREEZE.json','run.exit','tests.log',[10],'AUDIT-RESULT.json'),
 'breakthrough-replay-layout-audit-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'LAYOUT-AUDIT.json'),
}
s=(r/'seal-core-loan-native.py').read_text();a=s.index('config={');b=s.index('assert name in config;',a);s=s[:a]+'config='+repr(entries)+'\n'+s[b:]
a=s.index("if resultfile=='ADMISSION-RESULT.json':");b=s.index("added=r/'added-source'",a)
s=s[:a]+'''if resultfile=='ADMISSION-RESULT.json':
 cases=result['cases']
 special={'breakthrough-public-schedule-20261020':[0,0,0],'breakthrough-wide-square-budget-20261020':[0,0,0],'breakthrough-wide-uniform-compare-20261020':[0,0,101,101,101,101],'breakthrough-spacious-budget-20261020':[0,101,101,101,101,101,101,101,101],'breakthrough-primed-pool-20261020':[0,101,101,101,101,0,0,0,0]}
 if name in special:
  assert[c['exit']for c in cases]==special[name]
  assert cases[0]['raw_sha256']=='7fe2bb94f6b68965b87f7af4debd245d53c4b84df91ee0260e032499d49c14df'
 elif name=='breakthrough-wide-stronger-compare-20261020':
  assert len(cases)==2 and[c['mode']for c in cases]==[0,2]
  assert cases[0]['raw_sha256']=='7fe2bb94f6b68965b87f7af4debd245d53c4b84df91ee0260e032499d49c14df' and cases[1]['raw_sha256']=='f97bc5a1be3546e5d123a9007344936fd6a0e769725a941619e1441d0099887c'
 else:
  assert len(cases)==len(f['caps'])
  assert cases[0]['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 expected=special.get(name,{'breakthrough-fin1-fold-20261020':[0,0,101],'breakthrough-reverse-plan7-20261020':[0,0,101],'breakthrough-local-budget-20261020':[0,101,101],'breakthrough-wide-budget-20261020':[0,0,0,0,0,101,101,101],'breakthrough-wide-loan-policy-20261020':[0,0,0,0,101,101,101]}.get(name,[0]*len(cases)))
 assert [c['exit']for c in cases]==expected
 if 101 in expected:result['preserved_negative_cases']=[c['cap']for c in cases if c['exit']!=0]
if resultfile=='AUDIT-RESULT-v2.json':
 assert len(result['cases'])==3 and all(c['exit']==0 for c in result['cases'])
 assert result['cases'][0]['stream_sha256']=='125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501'
if resultfile=='AUDIT-RESULT.json':
 if name=='breakthrough-certified-prefix-20261020':
  assert len(result['cases'])==2 and all(c['exit']==0 for c in result['cases'])
  assert result['cases'][0]['stream_sha256']=='40a55e81af487e4f830eca1827d9904f60ed215b33d3bee9f12a801a46c4479c'
  assert result['cases'][1]['stream_sha256']=='85958b9f90cc93c7bba94d158cba2b4dde890bf9f4231cd70dc5b4fd9f1218b2'
 elif name=='breakthrough-wide-generic-20261020':
  assert result['status']=='COMPLETE_GENERIC_WIDE_AUDIT_NOT_SCORED' and[c['cap']for c in result['cases']]==[1234,1256,1264]
  assert result['cases'][0]['output_records']=={'operations':11268527,'record_sha256':'63eb09e3df3ecc6dc84330089f7100c369a21d8b50380bf792ab253debdf35c0'}
 else:assert result['exit']==0
if resultfile=='LAYOUT-AUDIT.json':
 assert len(result['cases'])==3 and all(c['exit']==0 for c in result['cases'])
 assert all(not c['identical_site_multiset']for c in result['comparisons'])
'''+s[b:]
s=s.replace("r.glob('cap*/ops.bin')","list(r.glob('*/ops.bin'))+list(r.glob('*.ops.bin'))")
s=s.replace("['observer','primitive','target','__pycache__']","['observer','primitive','tool','target','__pycache__']")
s=s.replace("'no_final_gate_nonce_or_scored_result':True","'no_final_gate_nonce_or_scored_result':True,'scope_correction':'Arithmetic scope is defined by the frozen source and experiment report. Budget changes can move derived predicates; stronger-comparison experiments explicitly increase precision. Component equivalence does not establish complete point-add equivalence.'")
(r/'seal-width-cycle.py').write_bytes(s.encode())
s=(r/'collect-core-loan-native.py').read_text();a=s.index('allowed=[');b=s.index('\nfor name in sys.argv[1:]:',a);s=s[:a]+'allowed='+repr(list(entries)+['breakthrough-width-correctness-20261020'])+s[b:];(r/'collect-width-cycle.py').write_bytes(s.encode())
