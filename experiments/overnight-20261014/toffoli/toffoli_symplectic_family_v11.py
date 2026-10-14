"""A bounded deterministic symplectic-transform family for the rank-six relation."""
import argparse,hashlib,itertools,json,random,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load,closure

def projection(v,space):
    for bit,(x,_) in sorted(space.rows.items(),reverse=True):
        if v>>bit&1:v ^= x
    return v

def describe(net,desc,limit):
    raw,targets,old=load(net);s=Space(raw)
    for a,b in desc['seed_ANDs']:assert s.add(combination(a,s.values)&combination(b,s.values))
    d=Space(raw+targets+[raw[13]&raw[14]])
    rng=random.Random(0xECDFA411);selected=[];seen=set();trials=0;rank_counts={}
    while len(selected)<limit and trials<8192:
        trials+=1;factors=[list(pair) for pair in desc['affine_product_factors']]
        # Elementary symplectic operations preserve the alternating matrix.
        # Boolean squares introduced by within-pair shears are known linear S24.
        for _ in range(rng.randrange(8,33)):
            i,j=rng.sample(range(3),2);kind=rng.randrange(4)
            if kind==0:
                factors[i][0]^=factors[j][0];factors[j][1]^=factors[i][1]
            elif kind==1:
                factors[i][1]^=factors[j][0];factors[j][1]^=factors[i][0]
            elif kind==2:
                factors[i].reverse()
            else:
                factors[i][0]^=factors[i][1]
        rebuilt=[0]*24
        for a,b in factors:
            for k in range(24):rebuilt[k]^=(b if a>>k&1 else 0)^(a if b>>k&1 else 0)
        assert rebuilt==desc['selected_matrix_rows']
        assert len(factors)==3
        values=[combination(a,s.values)&combination(b,s.values) for a,b in factors]
        assert d.express(values[0]^values[1]^values[2]) is not None
        assert s.express(values[0]^values[1]^values[2]) is None
        cosets=[projection(v,d) for v in values]
        assert cosets[0]^cosets[1]^cosets[2]==0
        key=tuple(sorted(set(cosets)-{0}))
        rank_counts[str(len(Space(cosets).values))]=rank_counts.get(str(len(Space(cosets).values)),0)+1
        if key in seen:continue
        seen.add(key)
        # Only rank43 proposals are selected for this family, as allocated.
        if len(Space(cosets).values)!=2:continue
        expanded=Space(s.values)
        assert all(expanded.add(v) for v in values)
        selected.append({'index':len(selected),'factors':factors,'prefix_ANDs':desc['seed_ANDs']+factors,
                         'outside_plane_truth_sha256':hashlib.sha256(b''.join(v.to_bytes(2048,'little') for v in key)).hexdigest(),
                         'product_truth_sha256':[hashlib.sha256(v.to_bytes(2048,'little')).hexdigest() for v in values]})
    return {'status':'description_only','source_lf_sha256':net['source_lf_sha256'],
            'description_sha256':hashlib.sha256(json.dumps(desc,sort_keys=True).encode()).hexdigest(),
            'domain_rows':16384,'desired_span_rank':43,'value_AND_budget':28,'selected_interface_count':len(selected),
            'deterministic_trial_count':trials,'trial_extra_rank_counts':rank_counts,'interfaces':selected,
            'scope':'First up to256 distinct rank43 outside planes from deterministic elementary symplectic transformations of one fixed rank6 relation, seed0xECDFA411,8..32 elementary steps per trial; not all symplectic decompositions.',
            'limits':'Exact16K partial prefixes only. No complete constructor, native cleanup/phase/width or qualified score.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('description',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--describe-only',action='store_true')
    p.add_argument('--limit',type=int,default=256);p.add_argument('--seconds',type=int,default=900);p.add_argument('--factor-timeout',type=int,default=5)
    args=p.parse_args();net=json.loads(args.netlist.read_bytes());desc=json.loads(args.description.read_bytes())
    assert desc['netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    report=describe(net,desc,args.limit);report['netlist_sha256']=desc['netlist_sha256'];report['input_description_sha256']=hashlib.sha256(args.description.read_bytes()).hexdigest()
    def save():args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    if args.describe_only:save();print(json.dumps({k:report[k] for k in ['selected_interface_count','deterministic_trial_count','trial_extra_rank_counts']}));return
    from toffoli_factor_solver import solve
    raw,targets,old=load(net);report.update(status='running',examined=[],qualified_score=None);started=time.monotonic()
    for item in report['interfaces']:
        if time.monotonic()-started>=args.seconds:break
        gates=[list(gate) for gate in item['prefix_ANDs']];values=list(raw);extra_gates=[]
        def sm(mask):return sum(1<<(i if i<15 else len(old)+i-15) for i in range(mask.bit_length()) if mask>>i&1)
        for index,(a,b) in enumerate(gates):
            values.append(combination(a,values)&combination(b,values))
            extra_gates.append({'name':f'family_prefix_{index}','a':sm(a),'b':sm(b)})
        extras=[raw[13]&raw[14]]+values[-3:];current=dict(net);current['gates']=net['gates']+extra_gates
        current['outputs']=net['outputs']+[1<<19]+[1<<(len(old)+9+i) for i in range(3)]
        row={'index':item['index'],'outside_plane_truth_sha256':item['outside_plane_truth_sha256'],'steps':[]};report['examined'].append(row)
        while time.monotonic()-started<args.seconds:
            result=closure(raw,targets,extras,prefix=gates);gates=result['gates'];step={'closure':result};row['steps'].append(step)
            if result['status']=='value_witness_found':
                check=list(raw)
                for a,b in gates:check.append(combination(a,check)&combination(b,check))
                assert len(gates)<=28 and [combination(mask,check) for mask in result['outputs']]==targets
                report.update(status='atmost28_AND_complete_value_witness',gates=gates,outputs=result['outputs'],AND_count=len(gates),witness_interface=item['index'],independent_truth_rows_replayed=16384)
                save();print(json.dumps({'status':report['status'],'ANDs':len(gates),'interface':item['index']}),flush=True);return
            if result['status']=='exact_quadratic_span_obstruction':row['status']=result['status'];break
            remaining=args.seconds-time.monotonic()+started
            if remaining<1:break
            factor=solve(current,{'gates':gates},len(gates),min(args.factor_timeout,max(1,int(remaining))));step['factor']=factor
            if factor['status']=='sat':gates.append([factor['a'],factor['b']]);continue
            row['status']='fixed_interface_closed_affine_product_UNSAT' if factor['status']=='unsat' else 'factor_unknown_unresolved';break
        row['final_ANDs']=len(gates);save();print(json.dumps({'index':item['index'],'status':row.get('status','incomplete'),'ANDs':len(gates)}),flush=True)
    complete=len(report['examined'])==len(report['interfaces']) and all(row.get('status') in ['exact_quadratic_span_obstruction','fixed_interface_closed_affine_product_UNSAT'] for row in report['examined'])
    report.update(status='selected_symplectic_interfaces_closed_negative' if complete else 'bounded_family_incomplete_or_unknown',completed_all_selected_interfaces=complete,seconds=time.monotonic()-started,formal_proof_certificate_saved=False);save()

if __name__=='__main__':main()
