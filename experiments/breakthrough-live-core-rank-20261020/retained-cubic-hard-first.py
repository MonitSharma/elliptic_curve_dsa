"""Keep easy forms live while attempting the seven hard cleanup functions."""
from pathlib import Path
p=Path(__file__).with_name('retained-cubic-cleanup.py');s=p.read_text()
s=s.replace("for name,g in reversed(remaining):","hard={'field3','field4','field5','field6','field7','field8','c6'};targets=[x for x in reversed(remaining)if x[0]in hard]or list(reversed(remaining))\n  for name,g in targets:")
s=s.replace("if options and options[-1]['cubic_terms']==0:break","if options and options[-1]['cubic_terms']==0:break")
s=s.replace('RETAINED-CUBIC-CLEANUP.json','RETAINED-CUBIC-HARD-FIRST.json').replace('deterministic greedy choice','deterministic hard-first greedy choice')
exec(compile(s,str(p),'exec'))
