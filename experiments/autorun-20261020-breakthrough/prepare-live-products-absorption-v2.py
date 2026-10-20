from pathlib import Path
import shutil,py_compile
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-live-products-absorption-20261020';r=root/'experiments/breakthrough-live-products-absorption-v2-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','PLAN.md','run.py','main.rs']:shutil.copyfile(old/p,r/p)
s=(old/'patch-algebra.py').read_text();needle="return v;}\n'+needle)";assert s.count(needle)==1;s=s.replace(needle,"return v;}'+chr(10)+needle)");(r/'patch-algebra.py').write_text(s)
for p in['patch-algebra.py','run.py']:py_compile.compile(str(r/p),doraise=True)
with(r/'PLAN.md').open('a')as out:out.write('\nV1 packaging parser failure occurred before tool/source freeze or native execution: an embedded newline was quoted incorrectly in the patch generator. V2 useschr(10), validates both Python scripts before transfer, and retains the same declared algebra/native controls/input streams. Original parser failure preserved.\n')
print(r)
