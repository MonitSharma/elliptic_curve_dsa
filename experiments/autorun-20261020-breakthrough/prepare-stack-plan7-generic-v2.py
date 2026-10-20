from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-plan7-generic-20261020';r=root/'experiments/breakthrough-stackv3-plan7-generic-v2-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','PLAN.md']:shutil.copyfile(old/p,r/p)
s=(old/'run.py').read_text();needle="copied=['breakthrough_generic.rs','classical_factors_xor.rs','tests_classical_factors.rs']";assert s.count(needle)==1;s=s.replace(needle,"copied=['breakthrough_generic.rs','classical_factors_xor.rs','product7_simplify.rs','tests_classical_factors.rs']");(r/'run.py').write_text(s)
with(r/'PLAN.md').open('a')as out:out.write('\nV1 stopped at compile: classical_factors_xor declares product7_simplify.rs, absent from this public parent. Original failure/source freeze retained. V2 copies that exact additional dependency from the same officially verified source; source and all native14 controls restart fresh before generation. No arithmetic or proof change.\n')
print(r)
