"""Separate cubic phase feasibility query after the negative quadratic query."""
from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'model.py').read_text();a="v=truth(d['c6_mask']);coef=0";assert s.count(a)==1
s=s.replace(a,"for i,j,k in itertools.combinations(range(1,len(fun)),3):terms.append([i,j,k]);add(fun[i]&fun[j]&fun[k],1<<(len(terms)-1))\n"+a)
s=s.replace("'C6_QUADRATIC_LOAN_MODEL_ONLY'","'C6_CUBIC_LOAN_MODEL_ONLY'").replace("r/'MODEL-RESULT.json'","r/'CUBIC-RESULT.json'").replace("'phase_terms':witness","'cubic_terms':sum(len(t)==3 for t in witness)if witness else None,'phase_terms':witness")
s=s.replace("Tests exact C6 erasure", "Separate degree3 query for exact C6 erasure")
(r/'cubic-generated.py').write_bytes(s.encode());exec(compile(s,str(r/'cubic-generated.py'),'exec'),{'__file__':str(r/'cubic-generated.py')})
