import ast,difflib,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1];script=r/'checkpoint_filter.py'
tree=ast.parse(script.read_text());block=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='block' for t in n.targets))
old='''One remaining core builds the new source-bound disabled validation tool in
product-classical-nine-filter-20261019. Build1401460 and waiting manager1401461
are recorded.'''
new='''The source-bound disabled validation-tool build1401460 has exited0 in
product-classical-nine-filter-20261019. Its23 source/build archive members are
verified locally; binary SHA2561be42a4d497e172dea7a65ec58f9a3d5cfdf5b06a93c9a2bf5ec54a261db6182.
Waiting manager1401461 remains recorded.'''
assert block.count(old)==1;block=block.replace(old,new)
paths=[script,r/'LOG.md',root/'experiments/product-classical-nine-filter-20261019/STATUS.md']+[root/p for p in ['docs/AGENT_HANDOFF.md','docs/research-plan.md','docs/results-status.md']]
for p in paths:
    s=p.read_text(encoding='utf-8');assert s.count(old)==1,p;p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
patch=[]
for name in ['docs/AGENT_HANDOFF.md','docs/research-plan.md','docs/results-status.md']:
    oldtext=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode('utf-8');h,t=oldtext.split('\n',1);updated=h+'\n\n'+block+t.lstrip('\n')
    patch.extend(difflib.unified_diff(oldtext.splitlines(True),updated.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
(r/'checkpoint-filter-docs.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
print('Recorded successful build and refreshed only the additive checkpoint patch.')
