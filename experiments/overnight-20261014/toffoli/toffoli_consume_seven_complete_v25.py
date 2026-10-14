"""One exact rank-minimum closure for the changed low13/carry13 contract."""
import argparse,hashlib,json,time
from pathlib import Path
from toffoli_guided_joint import combination
from toffoli_quadratic_closure import closure
from toffoli_consume_four_contract_v13 import load_fast

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--seconds',type=int,default=120);args=p.parse_args();net=json.loads(args.netlist.read_bytes())
    raw,targets,_=load_fast(net)
    import toffoli_cubic_factor_v23 as factor
    factor.load=load_fast
    start=time.monotonic();gates=[]
    report={'status':'running','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'domain_rows':2097152,
            'desired_span_rank':46,'rank_minimum_value_AND_budget':24,'steps':[],
            'qualified_score':None,'formal_proof_certificate_saved':False,
            'limits':'One rank-minimum changed low13/carry13 value interface. Closure negatives do not exclude34-AND circuits with additional auxiliary directions, nor other nonlinear consumer contracts. No cleanup/phase/native/width/full-cost claim.'}
    def save():args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    while time.monotonic()-start<args.seconds:
        result=closure(raw,targets,prefix=gates);gates=result['gates'];step={'closure':result};report['steps'].append(step)
        if result['status']=='value_witness_found':
            check=list(raw)
            for a,b in gates:check.append(combination(a,check)&combination(b,check))
            assert len(gates)<=24 and [combination(mask,check) for mask in result['outputs']]==targets
            report.update(status='atmost24_AND_complete_value_witness',gates=gates,outputs=result['outputs'],all_truth_rows_replayed=2097152);break
        if result['status']=='exact_quadratic_span_obstruction':report['status']=result['status'];break
        remaining=args.seconds-time.monotonic()+start
        if remaining<1:break
        factor.QUERY_PATH=Path(f'query-{len(report["steps"])}.smt2')
        solved=factor.solve(net,{'gates':gates},len(gates),max(1,int(remaining)))
        if solved.pop('all_16384_truth_rows_verified',False):solved['all_truth_rows_verified']=2097152
        solved.update(query_sha256=hashlib.sha256(factor.QUERY_PATH.read_bytes()).hexdigest(),query_bytes=factor.QUERY_PATH.stat().st_size)
        step['factor']=solved;save()
        if solved['status']=='sat':gates.append([solved['a'],solved['b']]);continue
        report['status']='selected_interface_closed_affine_product_UNSAT' if solved['status']=='unsat' else 'factor_unknown_unresolved';break
    if report['status']=='running':report['status']='bounded_search_incomplete'
    report.update(seconds=time.monotonic()-start,final_AND_count=len(gates));save()
    print(json.dumps({'status':report['status'],'ANDs':len(gates),'seconds':report['seconds']}),flush=True)
if __name__=='__main__':main()
