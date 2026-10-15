"""Extract source-bound support contradictions for the admitted CCX removals."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

spec=importlib.util.spec_from_file_location('guarded',Path(__file__).with_name('analyze-guarded-lifetimes.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
path,out=map(Path,sys.argv[1:3]);targets={5378815,11653340}
aq,ab=set(),set()
for _,r in m.plain.records(path):
    if r[0]==2:
        if r[4]!=m.NO:aq.add(r[4])
        if r[5]!=m.NO:ab.add(r[5])
class Trace(m.Support):
    def fresh(self):
        v=super().fresh();self.origin[self.atom]=self.position;return v
    def __init__(self):
        self.origin={};self.position=-1;super().__init__(aq,ab)
s=Trace();hits=[];recent={}
for i,r in m.plain.records(path):
    if i in targets:
        valid,g=s.inactive_quantum_gate(r);assert valid
        supports={str(q):s.q.get(q,m.FALSE) for q in (r[2],r[3])}
        atoms=set(g or ())
        for v in supports.values():atoms.update(v or ())
        hits.append(dict(operation=i,row=r,guard=sorted(g),
                         controls={q:None if v is None else sorted(v) for q,v in supports.items()},
                         atom_origins={str(abs(a)):s.origin[abs(a)] for a in atoms},
                         recent_controls={str(q):recent.get(q,[]) for q in (r[2],r[3])}))
    s.position=i;s.step(r)
    for q in r[2:5]:
        if q!=m.NO:
            recent.setdefault(q,[]).append([i,list(r)])
            recent[q]=recent[q][-8:]
out.write_text(json.dumps(dict(stream_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),hits=hits),indent=2)+'\n')
for h in hits:print({k:v for k,v in h.items() if k!='recent_controls'})
