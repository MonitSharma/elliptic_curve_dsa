"""Supplemental exact negative, without changing the frozen positive proof."""
from pathlib import Path
import hashlib,json,importlib.util
r=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('frozen_terminal',r/'prove-terminal.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
p,a,t,u,d,g=[m.var(s)for s in ['p','a','T','U','dirty_donor','guard']]
dd=m.add(d,m.prod(g,p,a));bad=m.add(u,m.prod(g,dd,t))
dd=m.add(dd,m.prod(g,p,a)) # deliberately omit second CCX(d,T,U)
correct=m.add(u,m.prod(g,p,a,t));error=m.add(bad,correct)
assert dd==d and error==m.prod(g,d,t)and error!=m.ZERO
out=dict(status='PASS: deliberately incomplete dirty-borrow negative rejected by exact ANF',donor_restored=True,nonzero_coordinate_error='guard * dirty_donor * T',node_or_term_caps=0,
 frozen_positive_proof_sha256=hashlib.sha256((r/'prove-terminal.py').read_bytes()).hexdigest(),
 note='The frozen protected test output square_missing_CZ_negative_hits aggregates clean-CZ phase negatives and dirty omitted-second-C3X value negatives. This supplemental exact negative isolates the latter without changing any frozen positive artifact, family, candidate, or sample.')
(r/'dirty-negative-proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
