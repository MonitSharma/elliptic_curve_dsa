"""Selected coordinate auxiliary subspaces for constructor/four-write fusion."""
import argparse,hashlib,itertools,json,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure
from toffoli_consume_four_contract_v13 import load_fast

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--describe-only',action='store_true');p.add_argument('--seconds',type=int,default=900)
    p.add_argument('--keep',type=int,default=7);p.add_argument('--factor-timeout',type=int,default=5)
    args=p.parse_args();net=json.loads(args.netlist.read_bytes());raw,targets,old=load_fast(net)
    w=Space(raw+targets);expanded=Space(w.values);aux=[]
    for index,value in enumerate(old[len(raw):]):
        if expanded.add(value):aux.append(index)
    assert len(w.values)==43 and len(expanded.values)==54 and len(aux)==11
    selected=list(itertools.combinations(aux,args.keep));rank=43+args.keep;budget=rank-19
    report={'status':'description_only' if args.describe_only else 'running','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'domain_rows':262144,
            'raw_rank':19,'target_rank':43,'complete_original_span_rank':54,'source_ANDs':35,
            'auxiliary_gate_indices':aux,'auxiliary_gate_names':[net['gates'][i]['name'] for i in aux],
            'retained_auxiliary_count':args.keep,'candidate_interface_rank':rank,'value_AND_budget':budget,
            'selected_interface_count':len(selected),'interfaces':[list(item) for item in selected],'examined':[],
            'qualified_score':None,'formal_proof_certificate_saved':False,
            'scope':'Every selected coordinate subspace retaining keep-of11 saved source-derived auxiliary directions modulo changed four-write target span; not every linear subspace or outside-original direction.',
            'limits':'Constructor-plus-four-write value interface only. No measurement cleanup, higher-word arithmetic, physical width, complete executed cost or qualified record.'}
    def save():args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    if args.describe_only:save();print(json.dumps({key:report[key] for key in ['auxiliary_gate_names','candidate_interface_rank','value_AND_budget','selected_interface_count']}));return
    import toffoli_factor_solver as factor
    factor.load=load_fast;started=time.monotonic()
    for index,indices in enumerate(selected):
        if time.monotonic()-started>=args.seconds:break
        extras=[old[len(raw)+i] for i in indices]
        assert len(Space(raw+targets+extras).values)==rank
        current=dict(net);current['outputs']=net['outputs']+[1<<(len(raw)+i) for i in indices]
        row={'index':index,'retained_gate_indices':list(indices),'steps':[]};report['examined'].append(row);gates=[]
        while time.monotonic()-started<args.seconds:
            result=closure(raw,targets,extras,prefix=gates);gates=result['gates'];step={'closure':result};row['steps'].append(step)
            if result['status']=='value_witness_found':
                check=list(raw)
                for a,b in gates:check.append(combination(a,check)&combination(b,check))
                assert len(gates)<=budget and [combination(mask,check) for mask in result['outputs']]==targets
                report.update(status='complete_changed_value_witness',gates=gates,outputs=result['outputs'],AND_count=len(gates),witness_retained_indices=list(indices),independent_truth_rows_replayed=262144)
                save();print(json.dumps({'status':report['status'],'ANDs':len(gates),'interface':index}),flush=True);return
            if result['status']=='exact_quadratic_span_obstruction':row['status']=result['status'];break
            remaining=args.seconds-time.monotonic()+started
            if remaining<1:break
            solved=factor.solve(current,{'gates':gates},len(gates),min(args.factor_timeout,max(1,int(remaining))))
            if solved.pop('all_16384_truth_rows_verified',False):solved['all_truth_rows_verified']=262144
            step['factor']=solved
            if solved['status']=='sat':gates.append([solved['a'],solved['b']]);continue
            row['status']='fixed_interface_closed_affine_product_UNSAT' if solved['status']=='unsat' else 'factor_unknown_unresolved';break
        row['final_ANDs']=len(gates);save();print(json.dumps({'index':index,'status':row.get('status','incomplete'),'ANDs':len(gates)}),flush=True)
    complete=len(report['examined'])==len(selected) and all(row.get('status') in ['exact_quadratic_span_obstruction','fixed_interface_closed_affine_product_UNSAT'] for row in report['examined'])
    report.update(status='selected_changed_consumer_subspaces_closed_negative' if complete else 'bounded_sweep_incomplete_or_unknown',completed_all_selected_interfaces=complete,seconds=time.monotonic()-started);save()

if __name__=='__main__':main()
