from pathlib import Path
import shutil
r=Path(__file__).resolve().parent
shutil.copyfile(r/'instrumented-cleanup.py',r/'instrumented-failed-path-v2.py')
s=(r/'search-v2.py').read_text();a=".replace(\"r.parent/'breakthrough-live-core-rank-20261020'\",'r')";assert s.count(a)==1;s=s.replace(a,a+".replace(\"r.parent/'breakthrough-live-core-rank-20261020/QUADRATIC-LOAN-REVERSE-MODEL.json'\",\"r/'QUADRATIC-LOAN-REVERSE-MODEL.json'\")")
(r/'search-v3.py').write_text(s)
