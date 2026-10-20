from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-fold-square-short-20261020'
s=(old/'sweep.py').read_text();assert s.count("env['BREAK_CAP']=str(cap)")==1
s=s.replace("env['BREAK_CAP']=str(cap)","env['BREAK_CAP']='1234';env['BREAK_HARD']=str(cap)")
(r/'sweep.py').write_text(s);(r/'launch.py').write_bytes((old/'launch.py').read_bytes())
