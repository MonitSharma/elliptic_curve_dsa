from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-public-e3-cache-finished-20261020';r=root/'experiments/breakthrough-public-e3-cache-finished-v2-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','PLAN.md','cache-tests.rs']:shutil.copyfile(old/p,r/p)
s=(old/'run.py').read_text();needle='rewrite_ops(ops,LEASES,nb);';assert s.count(needle)==1;s=s.replace(needle,'rewrite_ops(ops,LEASES,nb as usize);');(r/'run.py').write_text(s)
with(r/'PLAN.md').open('a')as out:out.write('\nV1 compile stopped before native tests: protected analyze_ops reportsnb asu64 whereas the exact proof rewriter acceptsusize. V2 adds the explicit type conversion, no arithmetic/proof/circuit change. Preserve V1 source/freeze/compile error; V2 rebuilds/freeze/tests/generation from fresh worktree.\n')
print(r)
