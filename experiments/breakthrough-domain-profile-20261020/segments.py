"""Partition by Boolean membership, independent of diagnostic name ordering."""
import hashlib,json,os,subprocess
from collections import Counter,defaultdict
from pathlib import Path
r=Path(__file__).resolve().parent
freeze=json.loads((r/'SOURCE_FREEZE.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(r/'observer'/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
assert sha(r/'observer/ops.bin')==freeze['expected_native_raw_sha256']
events=defaultdict(Counter); phases=[];calls=Counter()
for l in(r/'generate.log').read_text().splitlines():
    if l.startswith('BREAK_PHASE\t'):
        name,end,*_=l.split('\t')[1:];phases.append((name,int(end)))
    if l.startswith('BREAK_DOMAIN\t'):
        phase,domain,site,begin,end=l.split('\t')[1:]
        begin,end=int(begin),int(end);assert begin<=end
        calls[site]+=1
        if begin<end:events[begin][domain]+=1;events[end][domain]-=1
n=int.from_bytes((r/'observer/ops.bin').read_bytes()[8:16],'little')
assert phases[-1][1]==n
for _,end in phases:events[end]
events[0]; active=Counter();segments=[];phase_index=0
points=sorted(events)
for begin,end in zip(points,points[1:]):
    active.update(events[begin]);assert all(v>=0 for v in active.values())
    while begin>=phases[phase_index][1]:phase_index+=1
    phase=phases[phase_index][0];assert end<=phases[phase_index][1]
    if phase in ['divide','multiply']:
        name=('payload' if active['payload'] else 'other')+('_rotation' if active['rotation'] else '_arithmetic')
        name=phase+'/'+name
    else:name=phase
    if segments and segments[-1][0]==name:segments[-1]=(name,end)
    else:segments.append((name,end))
active.update(events[n]);assert not any(active.values())
(r/'segment-map.tsv').write_text(''.join(f'{name}\t{end}\t{end}\t0\n'for name,end in segments))
(r/'SEGMENTS.json').write_text(json.dumps({'status':'BYTE_IDENTICAL_RAW_DIRECT_MEMBERSHIP_MAP','ops':n,'segments':len(segments),'calls':dict(calls),
    'scope':'Rotation means actual rot4 operations; payload means the listed explicit function union. Other includes rail arithmetic and residual setup/endpoints. No optimized complete-circuit resource claim.'},indent=2)+'\n')
env=os.environ.copy();env['PHASE_MAP']=str(r/'segment-map.tsv')
with(r/'replay.out').open('xb')as out,(r/'replay.err').open('xb')as err:
    subprocess.run([str(r.parent/'breakthrough-profile-20261020/tool/target/release/phase-replay'),str(r/'observer/ops.bin'),
      'breakthrough-raw-subphase-cost-v1','0','512','2',str(r/'region-census.jsonl'),'8'],env=env,stdout=out,stderr=err,check=True)
a=[json.loads(l)for l in(r.parent/'breakthrough-subphase-20261020/region-census-v2.jsonl').read_text().splitlines()]
b=[json.loads(l)for l in(r/'region-census.jsonl').read_text().splitlines()]
assert len(a)==len(b)==512
for x,y in zip(a,b):
    assert sum(x.pop('regional_toffoli'))==x['toffoli'];assert sum(y.pop('regional_toffoli'))==y['toffoli'];assert x==y
(r/'REPLAY-CONTROL.json').write_text(json.dumps({'status':'ALL_512_ROWS_MATCH_PREVIOUS_FROZEN_RAW_STREAM','old_sha256':sha(r.parent/'breakthrough-subphase-20261020/region-census-v2.jsonl'),
    'new_sha256':sha(r/'region-census.jsonl'),'scope':'Same existing diagnostic inputs; no new final correctness census or candidate.'},indent=2)+'\n')
