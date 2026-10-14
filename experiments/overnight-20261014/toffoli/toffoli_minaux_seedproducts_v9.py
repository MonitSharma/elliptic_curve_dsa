"""Search W40+TT+one product of the reachable TT-interface S24 basis."""
import argparse,hashlib,itertools,json,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure,load
from toffoli_minaux_interfaces_v8 import projection

def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('seed_receipt',type=Path)
    parser.add_argument('--seconds',type=int,default=900);parser.add_argument('--factor-timeout',type=int,default=5)
    parser.add_argument('--describe-only',action='store_true');parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_bytes());seed_record=json.loads(args.seed_receipt.read_bytes())
    assert seed_record['netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    seed_row=next(row for row in seed_record['examined'] if row['representative']==[13,14])
    assert seed_row['status']=='fixed_interface_closed_affine_product_UNSAT'
    prefix=seed_row['steps'][-1]['closure']['gates'];assert len(prefix)==9
    raw,targets,old=load(net);tt=raw[13]&raw[14];d=Space(raw+targets+[tt]);assert len(d.values)==41
    seed=Space(raw)
    for a,b in prefix:
        value=combination(a,seed.values)&combination(b,seed.values)
        assert d.express(value) is not None and seed.add(value)
    assert len(seed.values)==24
    groups={};inside=[]
    for i,j in itertools.combinations(range(24),2):
        value=seed.values[i]&seed.values[j];coset=projection(value,d)
        if not coset:inside.append([i,j]);continue
        if coset not in groups:groups[coset]={'representative':[i,j],'pairs':[],'value':value}
        groups[coset]['pairs'].append([i,j])
    selected=sorted(groups.values(),key=lambda item:(not any(i>=15 for i in item['representative']),item['representative']))
    report={'status':'interface_description_only' if args.describe_only else 'running','baseline_revision':net['baseline_revision'],
            'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'seed_receipt_sha256':hashlib.sha256(args.seed_receipt.read_bytes()).hexdigest(),
            'seed_basis_truth_sha256':hashlib.sha256(b''.join(value.to_bytes(2048,'little') for value in seed.values)).hexdigest(),
            'seed_ANDs':prefix,'seed_span_rank':24,'domain_rows':16384,'target_span_rank':40,'base_interface_rank':41,'candidate_interface_rank':42,'value_AND_budget':27,
            'basis_products_total':276,'pairs_inside_base_interface':inside,'distinct_external_cosets':len(selected),
            'interfaces':[{'representative':item['representative'],'equivalent_pairs':item['pairs'],
                           'uses_constructed_basis_operand':any(i>=15 for i in item['representative']),
                           'external_truth_sha256':hashlib.sha256(item['value'].to_bytes(2048,'little')).hexdigest()} for item in selected],
            'examined':[],'scope':'Complete selected basis-pair-product family over exactreachableS24 inW+TT; groupedbyprojectioncoset moduloW+TT. FixedTT andone additionalp; arbitraryaffineproducts/moreoutsidefunctions excluded.',
            'limits':'No global27minimality ornativecleanup/phase/fullcircuitcost claim. TrustedfactorUNSAT withoutformalcertificate; unknown preserved.', 'qualified_score':None}
    def save():args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    if args.describe_only:save();print(json.dumps({'status':report['status'],'external_cosets':len(selected),'inside_pairs':len(inside),'constructed_operand_cosets':sum(any(i>=15 for i in item['representative']) for item in selected)}));return
    from toffoli_factor_solver import solve
    # Formal source program for p's truth vector: oldsource plus9 seedANDs plusp.
    extra_gates=[]
    def source_mask(mask):
        result=0
        for i in range(mask.bit_length()):
            if mask>>i&1:result|=1<<(i if i<len(raw) else len(old)+i-len(raw))
        return result
    for i,(a,b) in enumerate(prefix):extra_gates.append({'name':f'S24_seed_{i}','a':source_mask(a),'b':source_mask(b)})
    started=time.monotonic()
    for index,item in enumerate(selected):
        if time.monotonic()-started>=args.seconds:break
        i,j=item['representative'];value=item['value'];assert len(Space(raw+targets+[tt,value]).values)==42
        current_net=dict(net);current_net['gates']=net['gates']+extra_gates+[{'name':f'S24_product_{i}_{j}','a':source_mask(1<<i),'b':source_mask(1<<j)}]
        current_net['outputs']=net['outputs']+[1<<(len(raw)+4),1<<(len(old)+len(prefix))]
        row={'index':index,'representative':[i,j],'steps':[]};report['examined'].append(row);gates=[list(gate) for gate in prefix]
        while time.monotonic()-started<args.seconds:
            result=closure(raw,targets,[tt,value],prefix=gates);gates=result['gates'];row['steps'].append({'closure':result})
            if result['status']=='value_witness_found':
                assert len(gates)<=27;check=list(raw)
                for a,b in gates:check.append(combination(a,check)&combination(b,check))
                assert [combination(mask,check) for mask in result['outputs']]==targets
                report.update(status='atmost27_AND_complete_value_witness',AND_count=len(gates),gates=gates,outputs=result['outputs'],witness_representative=[i,j],
                              independent_truth_rows_replayed=16384,seconds=time.monotonic()-started,native_verified=False,cleanup_verified=False)
                save();print(json.dumps({'status':report['status'],'ANDs':len(gates),'pair':[i,j]}),flush=True);return
            if result['status']=='exact_quadratic_span_obstruction':row['status']=result['status'];break
            factor=solve(current_net,{'gates':gates},len(gates),min(args.factor_timeout,max(1,int(args.seconds-time.monotonic()+started))))
            row['steps'][-1]['factor']=factor
            if factor['status']=='sat':gates.append([factor['a'],factor['b']]);continue
            row['status']='fixed_interface_closed_affine_product_UNSAT' if factor['status']=='unsat' else 'factor_unknown_unresolved';break
        row['final_ANDs']=len(gates);save();print(json.dumps({'index':index,'pair':[i,j],'status':row.get('status','incomplete'),'ANDs':len(gates)}),flush=True)
    complete=len(report['examined'])==len(selected) and all(row.get('status','') in ['exact_quadratic_span_obstruction','fixed_interface_closed_affine_product_UNSAT'] for row in report['examined'])
    report.update(status='all_selected_TT_plus_basisproduct_interfaces_closed_negative' if complete else 'bounded_sweep_incomplete_or_unknown',completed_all_selected_interfaces=complete,seconds=time.monotonic()-started);save()

if __name__=='__main__':main()
