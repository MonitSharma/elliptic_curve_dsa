from pathlib import Path
r=Path(__file__).resolve().parent
entries={
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
 cases=result['cases'];assert len(cases)==(2 if name=='breakthrough-t0-shared-product-20261020'else 3)
 assert cases[0]['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 expected=[0,0,101]if name in['breakthrough-fin1-fold-20261020','breakthrough-reverse-plan7-20261020']else[0]*len(cases)
 assert [c['exit']for c in cases]==expected
 if 101 in expected:result['preserved_negative_case']='cap1232 generation failed; successful controls are raw only'
if resultfile=='AUDIT-RESULT-v2.json':
 assert len(result['cases'])==3 and all(c['exit']==0 for c in result['cases'])
 assert result['cases'][0]['stream_sha256']=='125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501'
if resultfile=='AUDIT-RESULT.json':assert result['exit']==0
if resultfile=='LAYOUT-AUDIT.json':
 assert len(result['cases'])==3 and all(c['exit']==0 for c in result['cases'])
 assert all(not c['identical_site_multiset']for c in result['comparisons'])
'''+s[b:]
s=s.replace("r.glob('cap*/ops.bin')","list(r.glob('*/ops.bin'))+list(r.glob('*.ops.bin'))")
s=s.replace("['observer','primitive','target','__pycache__']","['observer','primitive','tool','target','__pycache__']")
s=s.replace("'no_final_gate_nonce_or_scored_result':True","'no_final_gate_nonce_or_scored_result':True,'scope_correction':'Direct profile constants stay fixed, but tighter global caps change derived replay boundaries. Component equivalence does not establish complete point-add equivalence; exact streams and differing replay metadata preserved in breakthrough-replay-layout-audit-20261020.'")
(r/'seal-width-cycle.py').write_bytes(s.encode())
s=(r/'collect-core-loan-native.py').read_text();a=s.index('allowed=[');b=s.index('\nfor name in sys.argv[1:]:',a);s=s[:a]+'allowed='+repr(list(entries)+['breakthrough-width-correctness-20261020'])+s[b:];(r/'collect-width-cycle.py').write_bytes(s.encode())
