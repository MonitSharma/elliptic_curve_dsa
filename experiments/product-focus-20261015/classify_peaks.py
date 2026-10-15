"""Classify unresolved highest-wire intervals without changing the circuit."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import sys
stream, log, output, helper=map(Path,sys.argv[1:])
spec=importlib.util.spec_from_file_location('wire',helper);w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
entries=[]
for line in log.read_text().splitlines():
    m=re.match(r'PEBBLE_SPAN start=(\d+) end=(\d+) len=(\d+) zero=(\w+) depth=(\d+) choices=(.*?) affine=(.*)',line)
    if m:
        s,e,n,z,d,choices,affine=m.groups()
        entries.append(dict(start=int(s),end=int(e),length=int(n),zero=z=='true',depth=int(d),has_and=choices!='[]',has_affine=affine!='None'))
by_start={e['start']:e for e in entries};active=None;blocks=[];extra=[]
for i,row in w.records(stream):
    if i in by_start:
        active=dict(by_start[i],ops=[],qubits=set(),kinds=Counter(),reads=Counter());blocks.append(active)
    if active:
        if len(active['ops'])<24:active['ops'].append(list(row))
        active['qubits'].update(q for q in row[2:5] if q!=w.NO)
        active['kinds'][row[0]]+=1
        if 1233 in row[2:4] or (row[4]==1233 and row[0] in (7,9,14)):active['reads'][row[0]]+=1
        if i==active['end']:active=None
counts=Counter();examples={}
for b in blocks:
    q=b.pop('qubits');kinds=b.pop('kinds');reads=b.pop('reads')
    b['example_operations_truncated']=b['length']>len(b['ops'])
    key=(b['has_affine'],b['has_and'],b['depth'],b['length'],len(q),tuple(sorted(kinds.items())),tuple(sorted(reads.items())))
    counts[key]+=1;examples.setdefault(key,b)
rows=[dict(count=n,key=k,example=examples[k]) for k,n in counts.most_common()]
output.write_text(json.dumps(dict(status='UNSCORED_STRUCTURAL_DIAGNOSTIC',spans=len(entries),classes=rows),indent=2)+'\n')
for k,n in counts.most_common(35):print(n,k,'example',examples[k]['start'])
