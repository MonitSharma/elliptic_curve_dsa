from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'seal-cleanup-native.py').read_text()
a=s.index("config={");b=s.index("assert name in config",a)
s=s[:a]+'''config={
 'breakthrough-terminal-pebble-20261020':('primitive','SOURCE_FREEZE-v3.json','run-v3.exit','tests-v3.log',[3,1,3],None),
 'breakthrough-terminal-integration-20261020':('observer','SOURCE_FREEZE.json','run.exit','tests.log',[3,1,4,3,2,3,1],'ADMISSION-RESULT.json'),
 'breakthrough-direct-transport-20261020':('observer','SOURCE_FREEZE-v2.json','run-v3.exit','tests-v2.log',[3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-budget-c3-20261020':('observer','SOURCE_FREEZE-v2.json','run-v2.exit','tests-v2.log',[1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-phase-cubic-cap-20261020':('observer','SOURCE_FREEZE.json','run-v2.exit','tests-v2.log',[1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
 'breakthrough-live-core-rank-20261020':('primitive','SOURCE_FREEZE.json','run.exit','tests.log',[1],None),
 'breakthrough-activation-audit-20261020':('observer','SOURCE_FREEZE.json','run.exit',None,[],'ADMISSION-RESULT.json'),
 'breakthrough-phase-cubic-reserve-20261020':('observer','SOURCE_FREEZE.json','run-v2.exit','tests-v2.log',[1,3,1,4,3,2,3,1,1],'ADMISSION-RESULT.json'),
}
'''+s[b:]
a=s.index("assert (r/'tests.log')");b=s.index("added=r/'added-source'",a);s=s[:a]+s[b:]
s=s.replace("text=(r/log).read_text();assert all(f'test result: ok. {n} passed; 0 failed;'in text for n in counts)","import re\n text=(r/log).read_text();actual=[int(x)for x in re.findall(r'test result: ok\\. (\\d+) passed; 0 failed;',text)];assert actual==counts,(actual,counts)")
(r/'seal-workspace-cycle.py').write_bytes(s.encode())
s=(r/'collect-cleanup-native.py').read_text();a=s.index('allowed=');b=s.index('for name in sys.argv',a)
s=s[:a]+"allowed="+repr(['breakthrough-terminal-pebble-20261020','breakthrough-terminal-integration-20261020','breakthrough-direct-transport-20261020','breakthrough-budget-c3-20261020','breakthrough-phase-cubic-cap-20261020','breakthrough-live-core-rank-20261020','breakthrough-activation-audit-20261020','breakthrough-phase-cubic-reserve-20261020'])+'\n'+s[b:]
(r/'collect-workspace-cycle.py').write_bytes(s.encode())
