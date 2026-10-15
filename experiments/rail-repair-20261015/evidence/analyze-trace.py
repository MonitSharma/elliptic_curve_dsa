"""Independently check observed rail tick maps with unbounded integer arithmetic."""
from pathlib import Path
import ast,hashlib,json,re
root=Path(__file__).resolve().parent
path=root/'trace-v2.log';text=path.read_text()
p=2**256-2**32-977
def centered(v):
    v%=p
    return v-p if v>p//2 else v
def forward(t,b,tape):
    for sign in tape[:-2]:t=(t+(-1 if sign else 1)*b)*pow(2,-1,p)%p
    return t*pow(2**(tape[-2]+2*tape[-1]),-1,p)%p
def inverse(t,b,tape):
    t=t*2**(tape[-2]+2*tape[-1])%p
    for sign in reversed(tape[:-2]):t=(2*t-(-1 if sign else 1)*b)%p
    return t
for t,b in [(0,0),(p-1,17),(1,p-2),(2**255,2**255+1)]:
    for bits in range(32):
        tape=[bits>>i&1 for i in range(5)]
        assert inverse(forward(t,b,tape),b,tape)==t%p
rows=[]
for line in text.splitlines():
    if not line.startswith('FIRST_RAIL_BAD '):continue
    data=dict(re.findall(r'(\w+)=(\[[^\]]*\]|\S+)',line))
    tape=ast.literal_eval(data['tape']);a=int(data['before_t'],16);b=int(data['before_s'],16)
    want=forward(a,b,tape);assert want==int(data['expected_t'],16)
    assert inverse(want,b,tape)==a
    actual=int(data['got_t'],16);source=int(data['got_s'],16)
    assert want!=actual or source!=b
    integer_certificate=None
    if data['family']=='candidate':
        exact=centered(a);source_integer=centered(b);remainders=[]
        for sign in tape[:-2]:
            total=exact+(-1 if sign else 1)*source_integer
            remainders.append(total%2);exact=total//2
        divisor=2**(tape[-2]+2*tape[-1]);remainders.append(exact%divisor);exact//=divisor
        assert not any(remainders) and exact%p==want
        integer_certificate={'input_target':str(centered(a)),'input_source':str(source_integer),'exact_output':str(exact),'all_divisions_exact':True}
    deltas=[centered(actual-want),centered(source-b)]
    def power(v):return abs(v).bit_length()-1 if v and abs(v)&(abs(v)-1)==0 else None
    rows.append({'family':data['family'],'shot':int(data['shot']),'phase':data['phase'],'tick':int(data['tick']),
        'target_delta':str(deltas[0]),'source_delta':str(deltas[1]),'target_power_of_two':power(deltas[0]),'source_power_of_two':power(deltas[1]),
        'source_preserved':b==source,'tape':tape,'start':int(data['start']),'end':int(data['end']),'integer_certificate':integer_certificate,
        'source_log_line':line})
summaries=[dict(re.findall(r'(\w+)=(\S+)',l)) for l in text.splitlines() if l.startswith('RAIL_SUMMARY ')]
assert len(summaries)==3 and all(s['observer_equal']=='true' for s in summaries)
candidate=[r for r in rows if r['family']=='candidate']
assert len(candidate)==14 and len({r['shot'] for r in candidate})==14
assert all(r['target_power_of_two'] is not None or r['source_power_of_two'] is not None for r in candidate)
old_path=root.parent/'arithmetic-repair-20261015/reset-trace.log'
old=old_path.read_text()
bad={int(s) for s in re.findall(r'FINAL_BAD family=candidate shot=(\d+)',old)}
assert {r['shot'] for r in candidate}<=bad
result={'status':'FINITE_SOURCE_BOUND_DIAGNOSTIC','qualified_score':None,
    'trace_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'prior_reset_trace_sha256':hashlib.sha256(old_path.read_bytes()).hexdigest(),
    'scope':'Forward rail maps only, before the retroactive Y33 rewrite; fixed prefix measurements; modular invariant does not prove tape choice, convergence, reverse behavior or phase. No inference that every observed error is the first full-circuit error.',
    'summaries':summaries,'candidate_value_failures':len(bad),'candidate_failures_with_forward_rail_error':len(candidate),
    'candidate_failures_without_forward_rail_error':sorted(bad-{r['shot'] for r in candidate}),
    'candidate_source_corruptions':sum(not r['source_preserved'] for r in candidate),
    'algebraic_inverse_checks':128,'exact_integer_certificates':len(candidate),'failures':rows}
(root/'trace-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='failures'},indent=2))
