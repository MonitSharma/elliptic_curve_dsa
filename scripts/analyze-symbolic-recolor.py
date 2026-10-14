"""Conservative exact-zero physical wire recoloring; diagnostic allocation only."""
import argparse
import hashlib
import heapq
import importlib.util
import json
from pathlib import Path
import time

spec=importlib.util.spec_from_file_location('symbolic',Path(__file__).with_name('analyze-symbolic-controls.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
NO=m.NO

def analyze_rows(rows):
    began=time.monotonic()
    locked,bits=set(),set()
    for _,row in rows():
        if row[0]==2:
            if row[4]!=NO:locked.add(row[4])
            if row[5]!=NO:bits.add(row[5])
    assert locked==set(range(len(locked))),'This compactor requires contiguous input ABI IDs'
    state=m.Values(locked,bits)
    live={q:q for q in locked};free=[];next_id=len(locked)
    peak=len(locked);peak_at=0;retirements=0;remapped_fields=0;old_width=0
    output_hash=hashlib.sha256()
    for index,row in rows():
        touched=set(q for q in row[2:5]if q!=NO)
        if touched:old_width=max(old_width,max(touched)+1)
        for q in sorted(touched):
            if q not in live:
                if free:physical=heapq.heappop(free)
                else:physical=next_id;next_id+=1
                live[q]=physical
        new=list(row)
        for slot in (2,3,4):
            if row[slot]!=NO:
                new[slot]=live[row[slot]]
                remapped_fields+=new[slot]!=row[slot]
        assert len({new[slot]for slot in (2,3,4)if new[slot]!=NO})==len(touched)
        output_hash.update(m.stream.ROW.pack(*new))
        if len(live)>peak:peak=len(live);peak_at=index
        state.step(row)
        for q in sorted(touched-locked):
            if state.q.get(q,m.ZERO)==m.ZERO:
                heapq.heappush(free,live.pop(q));retirements+=1
    assert not state.stack
    return {'scope':'Exact arbitrary-input zero-state abstraction admits conservative safe physical reuse; diagnostic only, no source circuit or official benchmark',
            'operations':index+1,'original_referenced_width':old_width,'diagnostic_colored_width':next_id,
            'peak_active_wire_roles':peak,'peak_at_operation':peak_at,'zero_state_retirements':retirements,
            'changed_qubit_fields':remapped_fields,'colored_uncompressed_rows_sha256':output_hash.hexdigest(),
            'input_qubits':len(locked),'input_bits':len(bits),'remaining_nonABI_roles':len(live)-len(locked),
            'forgotten_expressions':state.forgotten,'cache_resets':state.cache_resets,'seconds':time.monotonic()-began}

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('stream',type=Path);a.add_argument('output',type=Path)
    args=a.parse_args()
    d=analyze_rows(lambda:m.stream.records(args.stream))
    d['stream_sha256']=hashlib.sha256(args.stream.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
    print(json.dumps(d))
