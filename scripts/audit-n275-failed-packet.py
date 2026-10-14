"""Fixed failed official packet through previously preserved ideal integer models."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
model=ROOT/'experiments/overnight-20261014/qubits/qubit-screen-n274.py'
spec=importlib.util.spec_from_file_location('model',model)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
packet=Path(sys.argv[1]);output=Path(sys.argv[2])
schedule=ROOT/'agents/qubits/src/point_add/sched_frogdrop.txt'
rows=[list(map(int,l.split()[1:]))for l in schedule.read_text().splitlines()if l.startswith('C ')]
began=time.monotonic();flags=[];target=[]
parameters={'public_c95':dict(small_cutoff=0,small_head=24,large_head=24,mixed_cap=23,pure_cap=23,reserve=7),
            'n275_v2':dict(small_cutoff=96,small_head=32,large_head=24,mixed_cap=22,pure_cap=24,reserve=9),
            'n274_v4':dict(small_cutoff=95,small_head=32,large_head=23,mixed_cap=22,pure_cap=24,reserve=9)}
lines=[l for l in packet.read_text().splitlines()if l and not l.startswith('#')]
assert len(lines)==9024
for line in lines:
    w=line.split();shot=int(w[0]);tx,ty,ox,oy,ex,ey=[int(x,16)for x in w[1:7]]
    # The failure tuple is an independent check of exported index/draw rules.
    if shot==2379:
        assert ex==int('ccd07cb0958eb19c527735b0ac84f9e5059940eefeb1eafe5e16df334236cddc',16)
        assert ey==int('3bb0a34ac68df544e0270ea850636f141f2a338ae980379950c1001aeab05ef6',16)
        (output.parent/'n275-v2-shot2379.txt').write_text(line+'\n',encoding='utf8')
    for division,dx in [(1,(tx-ox)%m.P),(2,(ex-ox)%m.P)]:
        for variant,p in parameters.items():
            stats=collections.Counter();events=m.screen(dx,rows,stats,**p)
            item={'shot':shot,'division':division,'variant':variant,'input':hex(dx),'events':events}
            if events:flags.append(item)
            if shot==2379:target.append(item)
d={'status':'COMPLETED_IDEAL_MODEL_DIAGNOSTIC','scope':'Exact unbounded Euclidean recurrence and preserved approximate reciprocal/parking/map event predictions on a fixed exported official packet. No quantum/source allocation or phase proof and no score.',
   'packet_sha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),
   'schedule_sha256':hashlib.sha256(schedule.read_bytes()).hexdigest(),'parameters':parameters,'point_count':len(lines),
   'divisions_per_variant':len(lines)*2,'shot2379':target,'all_flagged':flags,'seconds':time.monotonic()-began,
   'limitations':'Source schedule envelopes and real intermediate carry truncation are not modeled. Phase and measurement effects are not simulated. Comparing variants here alone cannot establish inherited versus introduced gate-level faults.'}
output.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
print(json.dumps({'shot2379':target,'flagged_by_variant':dict(collections.Counter(e['variant']for e in flags)),'seconds':d['seconds']}))
