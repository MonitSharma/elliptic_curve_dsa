"""Separate HT storage and reciprocal precision on the preserved failed packet.

Only the ideal arithmetic model is changed, by an exact asserted substitution.
No candidate source, benchmark packet, nonce or measurement stream is changed.
"""
import collections
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
original=ROOT/'experiments/overnight-20261014/qubits/qubit-screen-n274.py'
raw=original.read_bytes();source=raw.decode('utf8')
old='mixed_cap=22,pure_cap=24,reserve=9):'
assert source.count(old)==1
source=source.replace(old,'mixed_cap=22,pure_cap=24,reserve=9,ht_cap=25):')
old='qb=pure_cap if pure else mixed_cap;k='
assert source.count(old)==1
source=source.replace(old,'qb=ht_cap if ph else pure_cap if pure else mixed_cap;k=')
module={'__name__':'ideal_ht25'};exec(compile(source,str(original)+'[HT25-model-only]','exec'),module)
packet,output=map(Path,sys.argv[1:3]);schedule=ROOT/'agents/qubits/src/point_add/sched_frogdrop.txt'
rows=[list(map(int,line.split()[1:]))for line in schedule.read_text().splitlines()if line.startswith('C ')]
lines=[line for line in packet.read_text().splitlines()if line and not line.startswith('#')];assert len(lines)==9024
began=time.monotonic();flags=[];target=[];stats={str(head):collections.Counter()for head in(24,25,32)}
for line in lines:
    w=line.split();shot=int(w[0]);tx,ty,ox,oy,ex,ey=[int(x,16)for x in w[1:7]]
    for division,dx in[(1,(tx-ox)%module['P']),(2,(ex-ox)%module['P'])]:
        for head in(24,25,32):
            events=module['screen'](dx,rows,stats[str(head)],small_cutoff=95,small_head=32,
                                    large_head=head,mixed_cap=22,pure_cap=24,reserve=9,ht_cap=25)
            item={'shot':shot,'division':division,'large_head':head,'input':hex(dx),'events':events}
            if events:flags.append(item)
            if shot==2379:target.append(item)
result={'status':'COMPLETE_IDEAL_ARITHMETIC_DIAGNOSTIC','qualified_score':None,
        'original_model_sha256':hashlib.sha256(raw).hexdigest(),
        'model_with_exact_HT_cap_substitution_sha256':hashlib.sha256(source.encode()).hexdigest(),
        'packet_sha256':hashlib.sha256(packet.read_bytes()).hexdigest(),'schedule_sha256':hashlib.sha256(schedule.read_bytes()).hexdigest(),
        'parameters':{'small_cutoff':95,'small_head':32,'large_heads':[24,25,32],'HT_cap':25,'mixed_HR_cap':22,'pure_HR_cap':24,'reserve':9},
        'fixed_points':9024,'divisions_per_variant':18048,'stats':{k:dict(v)for k,v in stats.items()},
        'shot2379':target,'all_flagged':flags,'seconds':time.monotonic()-began,
        'limits':'Unbounded ideal recurrence and reciprocal predicate only. Physical precision/donors, schedule admission, carry truncation, quantum phase, all-input correctness and official score are not established.'}
output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({'target':target,'flagged_by_head':dict(collections.Counter(str(x['large_head'])for x in flags)),'seconds':result['seconds']}))
