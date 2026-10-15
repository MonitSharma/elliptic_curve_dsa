"""Reuse the validated raw observer on the exact combined 140-round source."""
from pathlib import Path
root=Path(__file__).resolve().parent;old=root.parent/'rail-control-20261015'
s=(old/'prepare-trace.py').read_text()
def change(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
change("root/'trace-room-b3'","root/'trace-combined-b3'")
change("source=root.parent/'rail-margin-20261015/margin-room-b3'","source=root/'combined-b3'")
change("'diff','--name-only'","'ls-files','--modified','--others','--exclude-standard'")
change(".replace('rail-repair-20261015','rail-control-20261015')",".replace('rail-repair-20261015','repair-integration-20261015').replace('m.tick==137','m.tick==139')")
exec(compile(s,str(old/'prepare-trace.py'),'exec'))
