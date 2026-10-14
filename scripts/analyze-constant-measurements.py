"""Count Toffoli guards on provably constant measurements; diagnostic only.

This extends the unchanged conservative Boolean value scan. Every ABI input is
arbitrary; only an unconditional HMR of an exactly constant abstract value is
admitted. Immutable condition snapshots distinguish later bit mutations. No
measurement is changed and no resource saving or equivalence follows.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time

spec=importlib.util.spec_from_file_location('symbolic',Path(__file__).with_name('analyze-symbolic-controls.py'))
symbolic=importlib.util.module_from_spec(spec);spec.loader.exec_module(symbolic)
NO,ZERO,ONE=symbolic.NO,symbolic.ZERO,symbolic.ONE

def analyze_rows(rows):
    began=time.monotonic();quantum,classical=set(),set()
    for _,r in rows():
        if r[0]==2:
            if r[4]!=NO:quantum.add(r[4])
            if r[5]!=NO:classical.add(r[5])
    state=symbolic.Values(quantum,classical);snapshots=[];owners={};sites=[];guarded=[]
    for index,r in rows():
        kind=r[0];condition=None if r[6]==NO else state.bits.get(r[6],ZERO)
        contexts=snapshots+([]if condition is None else[condition])
        if kind in(13,14) and state.guard(r)!=ZERO:
            matches=sorted({owners[value]for value in contexts if value in owners})
            if matches:
                guarded.append({'index':index,'kind':kind,'constant_measurements':[sites[i]['index']for i in matches],
                                'context_depth':len(snapshots),'per_op_condition':condition is not None})
                for i in matches:sites[i]['positive_guarded_toffolis']+=1
        constant=state.q.get(r[4],ZERO)if kind==12 and state.guard(r)==ONE else None
        if kind==15:snapshots.append(condition)
        elif kind==16:snapshots.pop()
        state.step(r)
        if constant in(ZERO,ONE):
            value=state.bits[r[5]];assert value not in(ZERO,ONE)
            owners[value]=len(sites)
            sites.append({'index':index,'qubit':r[4],'bit':r[5],'constant':constant[0],
                          'positive_guarded_toffolis':0})
    assert not snapshots and not state.stack
    useful=[site for site in sites if site['positive_guarded_toffolis']]
    return {'status':'COMPLETE_DIAGNOSTIC_NO_TRANSFORMATION','operations':index+1,
            'constant_unconditional_hmr':len(sites),'useful_sites':useful,
            'distinct_positive_guarded_toffolis':len(guarded),'guarded_operations':guarded,
            'atoms':state.atom,'forgotten':state.forgotten,'cache_resets':state.cache_resets,
            'seconds':time.monotonic()-began,'qualified_score':None,
            'scope':'Arbitrary ABI inputs and measurement outcomes under conservative immutable Boolean abstraction. Counts are emitted guard occurrences, not executed savings. No forced-measurement or whole-point phase equivalence claimed.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stream',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    result=analyze_rows(lambda:symbolic.stream.records(a.stream))
    result['stream_sha256']=hashlib.sha256(a.stream.read_bytes()).hexdigest()
    a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items()if k not in('guarded_operations','useful_sites')}))
