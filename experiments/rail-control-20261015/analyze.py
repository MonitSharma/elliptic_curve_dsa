"""Exact integer certificates, matched-control sets and exceptional-input algebra."""
from pathlib import Path
import ast,re,json,hashlib
root=Path(__file__).resolve().parent;p=2**256-2**32-977
center=lambda x:(x%p)-p if x%p>p//2 else x%p
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
bad=lambda text:{int(m) for m in re.findall(r'FINAL_BAD (?:family=candidate )?shot=(\d+)',text)}
trace=(root/'trace.log').read_text();certs=[]
for line in trace.splitlines():
    if not line.startswith('FIRST_RAIL_BAD family=candidate '):continue
    d=dict(re.findall(r'(\w+)=(\[[^\]]*\]|\S+)',line));tape=ast.literal_eval(d['tape'])
    before=int(d['before_t'],16);source=int(d['before_s'],16);wanted=before
    integer=center(before);s=center(source);remainders=[]
    for sign in tape[:-2]:
        wanted=(wanted+(-1 if sign else 1)*source)*pow(2,-1,p)%p
        z=integer+(-1 if sign else 1)*s;remainders.append(z%2);integer=z//2
    factor=2**(tape[-2]+2*tape[-1]);wanted=wanted*pow(factor,-1,p)%p
    remainders.append(integer%factor);integer//=factor
    assert wanted==int(d['expected_t'],16) and not any(remainders) and integer%p==wanted
    delta=[center(int(d['got_t'],16)-wanted),center(int(d['got_s'],16)-source)]
    certs.append({'shot':int(d['shot']),'phase':d['phase'],'tick':int(d['tick']),'before_target':str(center(before)),'before_source':str(s),'exact_integer_target':str(integer),'delta':list(map(str,delta)),'tape':tape,'log_line':line})
summary=[dict(re.findall(r'(\w+)=(\S+)',line)) for line in trace.splitlines() if line.startswith('RAIL_SUMMARY ')]
assert len(summary)==4 and all(s['observer_equal']=='true' for s in summary)
room=root.parent/'rail-margin-20261015'
control_bad=bad((root/'candidate.log').read_text());room_bad=bad((room/'room-candidate.log').read_text())
raw_bad=bad('\n'.join(l for l in trace.splitlines() if l.startswith('FINAL_BAD family=candidate ')))
assert raw_bad==room_bad and len(certs)==8
rail_bad={c['shot'] for c in certs};assert rail_bad<=room_bad
endpoints={int(d['shot']):[center(int(d['rails'].split(',')[i],16)) for i in range(2)] for d in [dict(re.findall(r'(\w+)=(\S+)',l)) for l in trace.splitlines() if l.startswith('ENDPOINT_BAD family=candidate ')]}
assert room_bad-rail_bad=={421,6972};assert all(s in endpoints for s in room_bad-rail_bad)
rows=[list(map(lambda x:int(x,16),l.split()[1:])) for l in (root/'packets/structured.tsv').read_text().splitlines()]
geometry={'zero_multiplicand':0,'zero_slope':0,'zero_multiplicand_tangent_identity':0}
for i,(x,y,a,b,ex,ey) in enumerate(rows):
    assert x!=a and (y*y-x*x*x-7)%p==0 and (b*b-a*a*a-7)%p==0
    slope=(y-b)*pow((x-a)%p,-1,p)%p;u=(x+2*a-slope*slope)%p
    assert (a-u)%p==ex and (slope*u-b)%p==ey
    if i%2==0:
        assert u==0 and ex==a and ey==(-b)%p
        tangent=3*a*a*pow(2*b,-1,p)%p;assert slope==tangent
        geometry['zero_multiplicand']+=1;geometry['zero_multiplicand_tangent_identity']+=1
    else:
        assert slope==0 and u!=0;geometry['zero_slope']+=1
families={}
for name,folder,prefix in [('control',root,''),('room',room,'room-')]:
    ids=bad((folder/(prefix+'structured.log')).read_text())
    families[name]={'minus_two_offset_wrong':sum(i%2==0 for i in ids),'zero_slope_wrong':sum(i%2==1 for i in ids)}
result={'status':'exact finite arithmetic diagnosis, no score','score':None,'control_wrong':sorted(control_bad),'room_wrong':sorted(room_bad),'removed_failures':sorted(control_bad-room_bad),'new_failures':sorted(room_bad-control_bad),'raw_and_optimized_wrong_sets_equal':True,'forward_rail_certificates':certs,'endpoint_only':{str(s):endpoints[s] for s in sorted(room_bad-rail_bad)},'trace_summaries':summary,'structured_geometry':geometry,'structured_wrong_by_family':families,'source_hashes':{'trace':sha(root/'trace.log'),'control':sha(root/'candidate.log'),'room':sha(room/'room-candidate.log'),'structured_packet':sha(root/'packets/structured.tsv')},'limitations':['Finite fixed inputs; no universal rail envelope proof.','Measurement events across arithmetic variants are unaligned.','Raw forward trace before Y33; it is not an all-optimized-stage phase proof.','Exceptional multiplication wrapper is only a proposed mechanism, not implemented.']}
(root/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['forward_rail_certificates','source_hashes']},indent=2))
