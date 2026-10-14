"""Source-bound existing-context planning for complete31-bank+7carry schedule."""
import argparse,hashlib,json
from pathlib import Path

def merged(n,budget):
    if budget+1>=n:return [n]
    for k in range(2,n+1):
        wk=budget+2-k
        if wk<=0:return None
        caps=[max(0,budget-j) for j in range(k-1)]
        if 0 in caps:return None
        rest=n-wk
        if rest<0:return None
        if sum(caps)<rest:continue
        if rest<k-1:return None
        left=rest;sizes=[]
        for cap in caps:
            take=min(cap,left-(k-2-len(sizes)));sizes.append(take);left-=take
        if left>0 or 0 in sizes:continue
        return sizes+[wk]
    return None

def plan(n,budget):
    p=merged(n-1,budget)
    if p is not None:p[-1]+=1;return p
    return merged(n,budget)

def splitcost(p):return sum(w-1 for w in p[:-1])/2

def main():
    p=argparse.ArgumentParser();p.add_argument('contexts',type=Path);p.add_argument('source',type=Path)
    p.add_argument('planner_source',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args();data=json.loads(args.contexts.read_bytes())
    source=args.source.read_bytes().replace(b'\r\n',b'\n')
    assert hashlib.sha256(source).hexdigest()=='879b85060f6a5cfa412561d64860f1cab697f7a334f180f5be9102070d5a23b9'
    rows=[]
    for r in data['rows']:
        if r['fin']!=0 or r['ttm'] or r['drop']!=0:continue
        room=1234-r['entry_dims'][0]+len(r['entry_state'][0]);mw=len(r['acc'])
        old=plan(mw-6,room-31)
        if old is None:continue # actual nonlean guard; tick105 is lean
        assert old==r['plan']
        new=plan(mw-13,room-38)
        if new is not None:assert splitcost(new)==splitcost(old)
        rows.append({'payload':r['payload'],'room':room,'mw':mw,'original_plan':old,'new_upper_plan':new,
                     'prefix_peak_fits':room>=38,'split_mean_delta':None if new is None else splitcost(new)-splitcost(old)})
    assert len(rows)==105 and sum(r['payload'] is not None for r in rows)==104
    planner=args.planner_source.read_bytes().replace(b'\r\n',b'\n')
    planner_function=planner.split(b'fn merged_plan(n: usize, budget: usize) -> Option<Vec<usize>> {',1)[1].split(b'fn lf_merged_trace()',1)[0]
    report={'status':'complete_retention_actualcontext_planning_cost_negative','contexts_sha256':hashlib.sha256(args.contexts.read_bytes()).hexdigest(),
            'planner_source_lf_sha256':hashlib.sha256(planner).hexdigest(),
            'merged_plan_function_lf_sha256':hashlib.sha256(planner_function).hexdigest(),
            'source_lf_sha256':hashlib.sha256(source).hexdigest(),'scoped_contexts':len(rows),'payload_contexts':104,
            'oldplans_exactly_reproduced':105,'prefix_fixed_qubits':38,'upper_fixed_qubits':38,'old_fixed_qubits':31,
            'new_upper_plan_infeasible':sum(r['new_upper_plan'] is None for r in rows),
            'feasible_new_upper_plans':sum(r['new_upper_plan'] is not None for r in rows),
            'all_feasible_split_mean_deltas_zero':True,'prefix_main_ANDs':7,'upper_main_AND_delta':-7,
            'main_AND_delta_zero':True,'rows':rows,'qualified_score':None,
            'limits':'Static existing actualcontext sourceplan replay, not emitted operation stream or score. Deterministic31-bank retention incurs7additional livecarries; feasible plans have no meanToffgain, other profiles cannotfit. Early11-bank proposal stillfailsfinal/carryphase and isexcluded.'}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
if __name__=='__main__':main()
