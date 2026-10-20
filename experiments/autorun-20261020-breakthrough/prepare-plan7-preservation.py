from pathlib import Path
root=Path(__file__).resolve().parents[2];a=root/'experiments/autorun-20261020-breakthrough'
names=['breakthrough-stackv3-width-loan-drop130-20261020','breakthrough-stackv3-width-plan7-20261020','breakthrough-stackv3-plan7-stats-20261020']
s=(a/'seal-front-evidence.py').read_text();needle=';assert r.name in allowed';assert s.count(needle)==1
s=s.replace(needle,';allowed+='+repr(names)+needle)
needle="for path in list(r.glob('*.ops.bin'))"
assert s.count(needle)==1
s=s.replace(needle,"if r.name=='breakthrough-stackv3-width-plan7-20261020':\n assert re.findall(r'test result: ok\\. (\\d+) passed; 0 failed;',(r/'tests.log').read_text())==['4'];test_count=4\n assert 'y16 at fwd t=131:'in(r/'generate-cap1233-t28.log').read_text()\n"+needle)
(a/'seal-plan7-evidence.py').write_text(s)
s=(a/'collect-bound-audit-cycle.py').read_text();start=s.index('names=[');end=s.index('\nsha=',start);s=s[:start]+'names='+repr(names)+s[end:]
needle=" (r/'.gitignore').write_text('observer/\\n__pycache__/\\nevidence.tar.gz\\n*resource-preflight*\\n*.records.bin\\n')"
assert needle in s
s=s.replace(needle," p=r/'.gitignore';prior=p.read_text()if p.exists()else'';p.write_text(prior+''.join(x+'\\n'for x in['observer/','candidate/','tool/','__pycache__/','evidence.tar.gz','*resource-preflight*','*.records.bin']if x not in prior.splitlines()))")
(a/'collect-plan7-evidence.py').write_text(s)
print('Three completed diagnostic fronts prepared for evidence preservation.')
