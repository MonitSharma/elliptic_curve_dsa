"""Certify the five residual signed-rail discrepancies without fitting new widths."""
from pathlib import Path
import re,ast,json,hashlib
root=Path(__file__).resolve().parent;p=2**256-2**32-977
center=lambda x:(x%p)-p if x%p>p//2 else x%p
trace=(root/'trace.log').read_text();certs=[]
for line in trace.splitlines():
    if not line.startswith('FIRST_RAIL_BAD family=candidate '):continue
    d=dict(re.findall(r'(\w+)=(\[[^\]]*\]|\S+)',line));tape=ast.literal_eval(d['tape'])
    value=center(int(d['before_t'],16));source=center(int(d['before_s'],16));remainders=[]
    for sign in tape[:-2]:
        value+=(-1 if sign else 1)*source;remainders.append(value%2);value//=2
    factor=2**(tape[-2]+2*tape[-1]);remainders.append(value%factor);value//=factor
    assert not any(remainders) and value%p==int(d['expected_t'],16)
    assert int(d['before_s'],16)==int(d['got_s'],16)
    delta=center(int(d['got_t'],16)-value);assert abs(delta)&(abs(delta)-1)==0
    certs.append({'shot':int(d['shot']),'phase':d['phase'],'tick':int(d['tick']),'tape':tape,'exact_signed_target':str(value),'target_delta':str(delta),'delta_power_of_two':abs(delta).bit_length()-1,'source_unchanged':True,'all_integer_divisions_exact':True,'observed_final_rail_widths':ast.literal_eval(d['widths']),'trace_line':line})
bad=lambda text:sorted(map(int,re.findall(r'FINAL_BAD (?:family=candidate )?shot=(\d+)',text)))
raw=bad('\n'.join(l for l in trace.splitlines() if l.startswith('FINAL_BAD family=candidate ')))
assert raw==[562,720,2777,3447,8322]==sorted(c['shot'] for c in certs)
summary=[dict(re.findall(r'(\w+)=(\S+)',l)) for l in trace.splitlines() if l.startswith('RAIL_SUMMARY ')]
assert len(summary)==4 and all(d['observer_equal']=='true' for d in summary)
assert sum(int(d['shots']) for d in summary)==9551
result={'score':None,'status':'finite exact integer certificates; complete circuit remains failing','certificates':certs,'trace_summaries':summary,'raw_bad':raw,'trace_sha256':hashlib.sha256((root/'trace.log').read_bytes()).hexdigest(),'limitations':['No new widths fitted to these inputs.','Each discrepancy is a signed power of two with unchanged source; this diagnoses rail truncation but does not establish a universal safe envelope.','Raw pre-Y33 trace is not a phase proof of the optimized circuit.']}
(root/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'bad':raw,'certificates':len(certs),'observer_equal_shots':9551,'delta_powers':[c['delta_power_of_two'] for c in certs],'score':None}))
