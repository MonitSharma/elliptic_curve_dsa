"""Complete one new second-carry fused value interface, if its exact closure permits."""
import argparse,hashlib,json,time
from pathlib import Path
from toffoli_guided_joint import combination
from toffoli_consume_four_contract_v13 import load_fast
from toffoli_quadratic_closure import closure

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('description',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=int,default=120)
    args=p.parse_args();net=json.loads(args.netlist.read_bytes());desc=json.loads(args.description.read_bytes())
    assert desc['factor_netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    raw,alltargets,_=load_fast(net);targets,extras=alltargets[:-3],alltargets[-3:]
    import toffoli_factor_solver as factor
    factor.load=load_fast;started=time.monotonic();gates=desc['prefix_ANDs']
    report={'status':'running','source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':desc['netlist_sha256'],
            'factor_netlist_sha256':desc['factor_netlist_sha256'],'description_sha256':hashlib.sha256(args.description.read_bytes()).hexdigest(),
            'domain_rows':262144,'desired_span_rank':46,'value_AND_budget':27,'steps':[],
            'formal_proof_certificate_saved':False,'qualified_score':None,
            'limits':'One new fused value interface only. No globaloptimality, native cleanup/phase, physical width or full cost/score.'}
    def save():args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    while time.monotonic()-started<args.seconds:
        result=closure(raw,targets,extras,prefix=gates);gates=result['gates'];step={'closure':result};report['steps'].append(step)
        if result['status']=='value_witness_found':
            check=list(raw)
            for a,b in gates:check.append(combination(a,check)&combination(b,check))
            assert len(gates)<=27 and [combination(mask,check) for mask in result['outputs']]==targets
            report.update(status='atmost27_AND_complete_changed_value_witness',gates=gates,outputs=result['outputs'],AND_count=len(gates),independent_truth_rows_replayed=262144);break
        if result['status']=='exact_quadratic_span_obstruction':report['status']=result['status'];break
        remaining=args.seconds-time.monotonic()+started
        if remaining<1:break
        solved=factor.solve(net,{'gates':gates},len(gates),max(1,int(remaining)))
        if solved.pop('all_16384_truth_rows_verified',False):solved['all_truth_rows_verified']=262144
        step['factor']=solved;save()
        if solved['status']=='sat':gates.append([solved['a'],solved['b']]);continue
        report['status']='fixed_interface_closed_affine_product_UNSAT' if solved['status']=='unsat' else 'factor_unknown_unresolved';break
    if report['status']=='running':report['status']='bounded_search_incomplete'
    report.update(seconds=time.monotonic()-started,final_AND_count=len(gates));save()
    print(json.dumps({'status':report['status'],'ANDs':len(gates),'seconds':report['seconds']}),flush=True)

if __name__=='__main__':main()
