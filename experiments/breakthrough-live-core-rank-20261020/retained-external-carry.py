"""Conditional model: can all other forms clear after an externally repaired C6?"""
from pathlib import Path
p=Path(__file__).with_name('retained-cubic-cleanup.py');s=p.read_text()
s=s.replace("for name,g in reversed(remaining):","hard={'field3','field4','field5','field6','field7','field8','c6'};targets=[x for x in reversed(remaining)if x[0]in hard]or list(reversed(remaining))\n  for name,g in targets:")
s=s.replace('if not options:break',"if not options:\n   if any(n=='c6'for n,v in remaining):\n    erased.append({'wire_function':'c6','phase_terms':[],'cubic_terms':0,'max_degree':None,'external_repair_required':True});remaining=[(n,v)for n,v in remaining if n!='c6'];continue\n   break")
s=s.replace('RETAINED-CUBIC-CLEANUP.json','RETAINED-EXTERNAL-CARRY.json').replace('EXACT_TRUTH_FUNCTION_MODEL_ONLY','CONDITIONAL_MODEL_REQUIRES_EXTERNAL_C6_REPAIR').replace('deterministic greedy choice','hard-first order; C6 removal is a declared external assumption, not a witnessed repair')
exec(compile(s,str(p),'exec'))
