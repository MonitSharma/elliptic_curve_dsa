"""Correct only the metadata-field assertion; no circuit existed in v1."""
import shutil
from pathlib import Path
r=Path(__file__).resolve().parent
assert(r/'run.exit').read_text().strip()=='1'and not(r/'observer').exists()
saved=r/'failed-trace-field-index-v1';saved.mkdir(exist_ok=False)
for name in['prepare.py','prepare.log','run.exit']:shutil.copyfile(r/name,saved/name)
source=(r/'prepare.py').read_text();needle=".split('\\t')[2:4]==['1234','1233']";assert source.count(needle)==1
source=source.replace(needle,".split('\\t')[3:5]==['1234','1233']")
exec(compile(source,str(r/'prepare.py')+'-corrected-metadata-index','exec'))
