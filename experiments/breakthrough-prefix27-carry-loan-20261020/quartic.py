"""Separate degree4 feasibility query; earlier quadratic/cubic negatives stand."""
from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'model.py').read_text();a="v=truth(d['c6_mask']);coef=0";assert s.count(a)==1
s=s.replace(a,"for degree in[3,4]:\n for ids in itertools.combinations(range(1,len(fun)),degree):\n  value=f['one']\n  for i in ids:value&=fun[i]\n  terms.append(list(ids));add(value,1<<(len(terms)-1))\n"+a)
s=s.replace("'C6_QUADRATIC_LOAN_MODEL_ONLY'","'C6_QUARTIC_LOAN_MODEL_ONLY'").replace("r/'MODEL-RESULT.json'","r/'QUARTIC-RESULT.json'").replace("'phase_terms':witness","'cubic_terms':sum(len(t)==3 for t in witness)if witness else None,'quartic_terms':sum(len(t)==4 for t in witness)if witness else None,'phase_terms':witness")
s=s.replace("Tests exact C6 erasure","Separate degree4 query for exact C6 erasure")
(r/'quartic-generated.py').write_bytes(s.encode());exec(compile(s,str(r/'quartic-generated.py'),'exec'),{'__file__':str(r/'quartic-generated.py')})
