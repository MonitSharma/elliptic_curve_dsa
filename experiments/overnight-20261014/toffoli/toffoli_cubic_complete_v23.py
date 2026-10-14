"""Complete the explicit source-arithmetic four-AND cubic prefix only."""
import argparse,hashlib,json,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load,closure

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('description',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=int,default=120)
    args=p.parse_args();net=json.loads(args.netlist.read_bytes());desc=json.loads(args.description.read_bytes())
    assert desc['netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    raw,targets,old=load(net);prefix=desc['prefix_ANDs'];values=list(raw)
    extra_gates=[]
    def source_mask(mask):
        return sum(1<<(i if i<15 else len(old)+i-15) for i in range(mask.bit_length()) if mask>>i&1)
    for index,(a,b) in enumerate(prefix):
        values.append(combination(a,values)&combination(b,values))
        extra_gates.append({'name':f'cubic_arithmetic_prefix_{index}','a':source_mask(a),'b':source_mask(b)})
    extras=values[-4:];assert len(Space(raw+targets+extras).values)==43
    factor_net=dict(net);factor_net['gates']=net['gates']+extra_gates
    factor_net['outputs']=net['outputs']+[1<<(len(old)+i) for i in range(8,12)]
    factor_path=Path('factor-netlist.json');factor_path.write_bytes((json.dumps(factor_net,indent=2)+'\n').encode())
    fr,ft,fv=load(factor_net);assert ft==targets+extras
    for i in range(12):assert fv[len(old)+i]==values[15+i]
    import toffoli_cubic_factor_v23 as factor
    started=time.monotonic();gates=list(prefix)
    report={'status':'running','netlist_sha256':desc['netlist_sha256'],
            'description_sha256':hashlib.sha256(args.description.read_bytes()).hexdigest(),
            'factor_netlist_sha256':hashlib.sha256(factor_path.read_bytes()).hexdigest(),
            'source_lf_sha256':net['source_lf_sha256'],'domain_rows':16384,
            'desired_span_rank':43,'value_AND_budget':28,'prefix_AND_count':12,
            'all_prefix_and_mapped_output_rows_verified':16384,'steps':[],
            'formal_proof_certificate_saved':False,'qualified_score':None,
            'limits':'Selected explicit arithmetic rank43 interface only; no global constructor optimality, cleanup/phase/native/width/full-score claim.'}
    def save():args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    while time.monotonic()-started<args.seconds:
        result=closure(raw,targets,extras,prefix=gates);gates=result['gates'];step={'closure':result};report['steps'].append(step)
        if result['status']=='value_witness_found':
            check=list(raw)
            for a,b in gates:check.append(combination(a,check)&combination(b,check))
            assert len(gates)<=28 and [combination(mask,check) for mask in result['outputs']]==targets
            report.update(status='atmost28_AND_complete_value_witness',gates=gates,outputs=result['outputs'],AND_count=len(gates),independent_truth_rows_replayed=16384);break
        if result['status']=='exact_quadratic_span_obstruction':report['status']=result['status'];break
        remaining=args.seconds-(time.monotonic()-started)
        if remaining<1:break
        factor.QUERY_PATH=Path(f'query-{len(report["steps"])}.smt2')
        solved=factor.solve(factor_net,{'gates':gates},len(gates),max(1,int(remaining)))
        solved.update(query_sha256=hashlib.sha256(factor.QUERY_PATH.read_bytes()).hexdigest(),query_bytes=factor.QUERY_PATH.stat().st_size)
        step['factor']=solved;save()
        if solved['status']=='sat':gates.append([solved['a'],solved['b']]);continue
        report['status']='selected_interface_closed_affine_product_UNSAT' if solved['status']=='unsat' else 'factor_unknown_unresolved';break
    if report['status']=='running':report['status']='bounded_search_incomplete'
    report.update(seconds=time.monotonic()-started,final_AND_count=len(gates));save()
    print(json.dumps({'status':report['status'],'ANDs':len(gates),'seconds':report['seconds']}),flush=True)

if __name__=='__main__':main()
