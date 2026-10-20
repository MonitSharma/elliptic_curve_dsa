from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'seal-workspace-cycle.py').read_text();s=s.replace('config={',"config={\n 'breakthrough-core-loan-native-20261020':('primitive','SOURCE_FREEZE-v5.json','run-v5.exit','tests-v5.log',[2,1],None),\n 'breakthrough-core-loan-fold-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[1,1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),\n 'breakthrough-core-loan-select-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[1,1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),",1);(r/'seal-core-loan-native.py').write_bytes(s.encode())
s=(r/'collect-workspace-cycle.py').read_text();s=s.replace('allowed=[',"allowed=['breakthrough-core-loan-native-20261020','breakthrough-core-loan-fold-20261020','breakthrough-core-loan-select-20261020',",1);(r/'collect-core-loan-native.py').write_bytes(s.encode())
s=(r/'seal-core-loan-native.py').read_text().replace('config={',"config={\n 'breakthrough-global-cap-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'ADMISSION-RESULT.json'),",1)
s=s.replace("assert len(result['cases'])==2 and all(row['exit']==0 for row in result['cases'])","assert len(result['cases'])==2\n if name=='breakthrough-global-cap-20261020':\n  assert result['cases'][0]['exit']==0 and result['cases'][1]['exit']==101\n  result['status']='NEGATIVE_CANDIDATE_GENERATION_FAILED_NO_SCORED_RESULT'\n else:assert all(row['exit']==0 for row in result['cases'])")
(r/'seal-core-loan-native.py').write_bytes(s.encode())
s=(r/'collect-core-loan-native.py').read_text().replace('allowed=[',"allowed=['breakthrough-global-cap-20261020',",1)
s=s.replace("for m in members:\n   p=Path(m.name);data=archive.extractfile(m).read()","for m in members:\n   p=Path(m.name);data=archive.extractfile(m).read();retained[m.name]=data")
(r/'collect-core-loan-native.py').write_bytes(s.encode())
