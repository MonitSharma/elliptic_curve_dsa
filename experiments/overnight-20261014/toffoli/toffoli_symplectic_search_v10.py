"""Try completing the exact rank43 symplectic-prefix constructor interface."""
import argparse,hashlib,json,time
from pathlib import Path
from toffoli_guided_joint import combination
from toffoli_quadratic_closure import load,closure

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('description',type=Path)
    p.add_argument('--seconds',type=int,default=900);p.add_argument('--factor-timeout',type=int,default=120)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    net=json.loads(args.netlist.read_bytes());desc=json.loads(args.description.read_bytes())
    assert desc['netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    raw,targets,old=load(net);prefix=desc['prefix_ANDs'];seed=desc['seed_ANDs'];values=list(raw)
    extra_gates=[]
    def source_mask(mask):
        return sum(1<<(i if i<15 else len(old)+i-15) for i in range(mask.bit_length()) if mask>>i&1)
    for index,(a,b) in enumerate(prefix):
        values.append(combination(a,values)&combination(b,values))
        extra_gates.append({'name':f'symplectic_prefix_{index}','a':source_mask(a),'b':source_mask(b)})
    extras=[raw[13]&raw[14]]+[values[15+len(seed)+i] for i in desc['independent_extra_product_indices']]
    factor_net=dict(net);factor_net['gates']=net['gates']+extra_gates
    factor_net['outputs']=net['outputs']+[1<<(15+4)]+[1<<(len(old)+len(seed)+i) for i in desc['independent_extra_product_indices']]
    from toffoli_factor_solver import solve
    report={'status':'running','netlist_sha256':desc['netlist_sha256'],'description_sha256':hashlib.sha256(args.description.read_bytes()).hexdigest(),
            'source_lf_sha256':net['source_lf_sha256'],'domain_rows':16384,'desired_span_rank':43,'value_AND_budget':28,
            'seed_AND_count':12,'steps':[],'qualified_score':None,
            'limits':'One exact rank43 interface only. Trusted solver UNSAT without formal certificate; unknown unresolved. No native cleanup/phase/width/full score.'}
    def save():args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    started=time.monotonic();gates=prefix
    while time.monotonic()-started<args.seconds:
        result=closure(raw,targets,extras,prefix=gates);gates=result['gates'];step={'closure':result};report['steps'].append(step)
        if result['status']=='value_witness_found':
            check=list(raw)
            for a,b in gates:check.append(combination(a,check)&combination(b,check))
            assert [combination(mask,check) for mask in result['outputs']]==targets
            report.update(status='atmost28_AND_complete_value_witness',gates=gates,outputs=result['outputs'],AND_count=len(gates),independent_truth_rows_replayed=16384)
            break
        if result['status']=='exact_quadratic_span_obstruction':
            report['status']=result['status'];break
        remaining=args.seconds-(time.monotonic()-started)
        if remaining<1:break
        factor=solve(factor_net,{'gates':gates},len(gates),min(args.factor_timeout,max(1,int(remaining))));step['factor']=factor;save()
        print(json.dumps({'ANDs':len(gates),'closure':result['status'],'factor':factor['status']}),flush=True)
        if factor['status']=='sat':gates.append([factor['a'],factor['b']]);continue
        report['status']='fixed_interface_closed_affine_product_UNSAT' if factor['status']=='unsat' else 'factor_unknown_unresolved';break
    if report['status']=='running':report['status']='bounded_search_incomplete'
    report.update(seconds=time.monotonic()-started,final_AND_count=len(gates));save()
    print(json.dumps({'status':report['status'],'ANDs':len(gates),'seconds':report['seconds']}),flush=True)

if __name__=='__main__':main()
