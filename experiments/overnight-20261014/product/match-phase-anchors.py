"""Match observed raw gate triples to the byte-identical final stream."""
from pathlib import Path
import importlib.util,json,sys,collections,hashlib
script=Path(sys.argv[1]);log=Path(sys.argv[2]);stream=Path(sys.argv[3]);out=Path(sys.argv[4]);size=int(sys.argv[5]) if len(sys.argv)>5 else 3
spec=importlib.util.spec_from_file_location('stream_reader',script);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
anchors={}
for line in log.read_text().splitlines():
    if not line.startswith('PHASE_ANCHOR '):continue
    f=line.split();phase=f[1];at,end=map(int,f[2:4]);op=tuple(map(int,f[4:]));assert len(op)==7
    anchors.setdefault((phase,end),{})[at]=op
queries={}
for (phase,end),items in anchors.items():
    for at in sorted(items):
        if all(i in items for i in range(at-size+1,at+1)):
            key=tuple(items[i] for i in range(at-size+1,at+1));queries.setdefault(key,[]).append((phase,end,at))
hits={};window=collections.deque(maxlen=size);depth=0
for at,op in enumerate(reader.records(stream)):
    key=(op[0],)+op[2:];window.append(key)
    if key[0]==15:depth+=1
    if key[0]==16:depth-=1
    q=queries.get(tuple(window))
    if q:
        for item in q:hits.setdefault(item,[]).append((at,depth))
selected=[]
for (phase,end),items in anchors.items():
    candidates=[]
    for (p,e,raw_at),matches in hits.items():
        if (p,e)!=(phase,end) or len(matches)!=1 or matches[0][1]!=0:continue
        final_at,depth=matches[0];candidates.append(dict(phase=phase,raw_boundary=end,raw_anchor_end=raw_at,final_anchor_end=final_at,prefix_end=final_at+1,raw_distance=end-1-raw_at,condition_depth=depth,gate_window=[list(items[i]) for i in range(raw_at-size+1,raw_at+1)]))
    if candidates:selected.append(min(candidates,key=lambda x:x['raw_distance']))
result=dict(stream_sha256=hashlib.file_digest(open(stream,'rb'),'sha256').hexdigest(),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),selected=selected,window_length=size,total_raw_windows=len(queries),scope='Observed raw gate windows uniquely matched to final stream at condition depth0. Exact boundary only when raw_distance=0; no score.')
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
