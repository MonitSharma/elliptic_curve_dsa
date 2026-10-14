"""Construct minimal one-aux complete constructor interfaces from raw monomials."""
import argparse,hashlib,itertools,json,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure,load

def projection(value,space):
    for bit,(row,_) in sorted(space.rows.items(),reverse=True):
        if value>>bit&1:value^=row
    return value

def choices(raw,targets):
    w=Space(raw+targets);groups={};inside=[]
    for i,j in itertools.combinations(range(1,len(raw)),2):
        value=raw[i]&raw[j];coset=projection(value,w)
        if not coset:inside.append([i,j]);continue
        if coset not in groups:groups[coset]={'pairs':[],'value':value,'representative':[i,j]}
        groups[coset]['pairs'].append([i,j])
    return w,inside,sorted(groups.values(),key=lambda item:item['representative'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path)
    parser.add_argument('--seconds',type=int,default=600);parser.add_argument('--factor-timeout',type=int,default=10)
    parser.add_argument('--describe-only',action='store_true');parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_bytes());raw,targets,old=load(net)
    w,inside,selected=choices(raw,targets);assert len(w.values)==40
    record={'status':'interface_description_only' if args.describe_only else 'running','baseline_revision':net['baseline_revision'],
            'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'domain_rows':16384,'raw_span_rank':15,'target_span_rank':40,'interface_rank':41,'value_AND_budget':26,
            'input_order':net['input_order'],'raw_pairs_total':91,'raw_pairs_insideW':inside,
            'distinct_external_monomial_cosets':len(selected),
            'interfaces':[{'representative':item['representative'],'equivalent_raw_pairs':item['pairs'],
                           'external_truth_sha256':hashlib.sha256(item['value'].to_bytes(2048,'little')).hexdigest()}
                          for item in selected],
            'examined':[],'scope':'All rank41 W40+span(p) interfaces for one selected pure raw-input monomial p outsideW, grouped by exact quotientcoset. No oldextra directions retained bydefault. Other affineproducts/multipleexternaldirections excluded.',
            'limits':'Value synthesis only; nativecleanup/phase/Q/fullcircuitcost andproducer admission separate. TrustedfactorUNSAT without formalcertificate; unknown preserved.', 'qualified_score':None}
    def save():args.output.write_bytes((json.dumps(record,indent=2)+'\n').encode())
    if args.describe_only:save();print(json.dumps({'status':record['status'],'external_cosets':len(selected),'pairs_insideW':len(inside)}));return
    from toffoli_factor_solver import solve
    started=time.monotonic()
    for index,item in enumerate(selected):
        if time.monotonic()-started>=args.seconds:break
        i,j=item['representative'];value=item['value'];assert len(Space(raw+targets+[value]).values)==41
        # The appended gate is the exact outside function, not an altered target.
        current_net=dict(net);current_net['gates']=net['gates']+[{'name':f'minaux_raw_{i}_{j}','a':1<<i,'b':1<<j}]
        current_net['outputs']=net['outputs']+[1<<len(old)]
        row={'index':index,'representative':[i,j],'steps':[]};record['examined'].append(row);gates=[]
        while time.monotonic()-started<args.seconds:
            result=closure(raw,targets,[value],prefix=gates);gates=result['gates'];row['steps'].append({'closure':result})
            if result['status']=='value_witness_found':
                assert len(gates)<=26;check=list(raw)
                for a,b in gates:check.append(combination(a,check)&combination(b,check))
                assert [combination(mask,check) for mask in result['outputs']]==targets
                record.update(status='atmost26_AND_complete_value_witness',AND_count=len(gates),gates=gates,outputs=result['outputs'],
                              witness_representative=[i,j],independent_truth_rows_replayed=16384,seconds=time.monotonic()-started,
                              native_verified=False,cleanup_verified=False)
                save();print(json.dumps({'status':record['status'],'AND_count':len(gates),'pair':[i,j]}),flush=True);return
            if result['status']=='exact_quadratic_span_obstruction':row['status']=result['status'];break
            factor=solve(current_net,{'gates':gates},len(gates),min(args.factor_timeout,max(1,int(args.seconds-time.monotonic()+started))))
            row['steps'][-1]['factor']=factor
            if factor['status']=='sat':gates.append([factor['a'],factor['b']]);continue
            row['status']='fixed_interface_closed_affine_product_UNSAT' if factor['status']=='unsat' else 'factor_unknown_unresolved';break
        row['final_ANDs']=len(gates);save();print(json.dumps({'index':index,'pair':[i,j],'status':row.get('status','incomplete'),'ANDs':len(gates)}),flush=True)
    complete=len(record['examined'])==len(selected) and all(row.get('status','') in ['exact_quadratic_span_obstruction','fixed_interface_closed_affine_product_UNSAT'] for row in record['examined'])
    record.update(status='all_selected_single_aux_interfaces_closed_negative' if complete else 'bounded_sweep_incomplete_or_unknown',
                  completed_all_selected_interfaces=complete,seconds=time.monotonic()-started)
    save()

if __name__=='__main__':main()
