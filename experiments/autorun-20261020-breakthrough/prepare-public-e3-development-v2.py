from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-public-e3-cache-development-20261020';r=root/'experiments/breakthrough-public-e3-cache-development-v2-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','PLAN.md']:shutil.copyfile(old/p,r/p)
s=(old/'run.py').read_text();s=s.replace("source/'run.exit'","source/'resumed.exit'").replace("a['native_tests']==20 and a['qubits']==1234","a['native_tests']==18 and a['inherited_parent_tests_failed']==2 and a['qubits']==1234")
needle=" start=time.time()";assert s.count(needle)==1;s=s.replace(needle," assert not(ws/'breakthrough-public-e3-cache-development-20261020/PLAN.json').exists(),'Original development preflight must have stopped before any declaration/sampling'\n"+needle)
(r/'run.py').write_text(s)
with(r/'PLAN.md').open('a')as out:out.write('\nOriginal development controller stopped at source preflight before PLAN.json or any sampling. V2 waits the unchanged source resumed.exit and baseline audit: candidate18 controls pass, two unchanged parent failures exactly reproduced on Git88869 (parent17 pass/2 fail), isolated cache test passes, independent9 proof controls pass. No claim all20 tests pass. Original planned label is used for its first actual declaration; no final gate is involved.\n')
print(r)
