"""Try C6 while every other retained field is still available."""
from pathlib import Path
p=Path(__file__).with_name('retained-cubic-cleanup.py');s=p.read_text()
s=s.replace("for name,g in reversed(remaining):","targets=[x for x in remaining if x[0]=='c6']or list(reversed(remaining))\n  for name,g in targets:")
s=s.replace('RETAINED-CUBIC-CLEANUP.json','RETAINED-CARRY-FIRST.json').replace('deterministic greedy choice','carry-first greedy choice')
exec(compile(s,str(p),'exec'))
