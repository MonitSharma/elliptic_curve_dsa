"""Selected consumer sum direction k1*(acc3+C3), all651 temporary subspaces."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure,load
from toffoli_external_planes_v2 import subspaces


def main():
    from toffoli_factor_solver import solve
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('--seconds',type=int,default=900)
    p.add_argument('--left-input',type=int,default=13);p.add_argument('--right-output',type=int,default=24)
    p.add_argument('--factor-timeout',type=int,default=5);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    net=json.loads(a.netlist.read_text());raw,targets,original=load(net)
    left=1<<a.left_input;right=net['outputs'][a.right_output]
    outside=combination(left,original)&combination(right,original)
    assert Space(original).express(outside) is None
    want=Space(raw+targets);old=[]
    for k,value in enumerate(original[len(raw):]):
        if want.add(value):old.append((1<<(len(raw)+k),value))
    assert len(old)==6
    source=dict(net);source['gates']=net['gates']+[{'name':'outside_consumer_sum','a':left,'b':right}]
    pmask=1<<(len(raw)+len(net['gates']))
    reports=[];started=time.monotonic()
    result={'status':'running','source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(a.netlist.read_bytes()).hexdigest(),
            'domain_rows':1<<14,'outside_definition':{'left_original_affine_mask':left,'right_original_affine_mask':right,'left_input_index':a.left_input,'right_output_index':a.right_output,'label':'k1*(acc3+C3)'},
            'old_extra_masks':[mask for mask,v in old],'subspaces_total':651,'examined':reports,
            'scope':'All rank45 interfaces in the old span plus this chosen exact external consumer-sum function that contain W40 and the external function. Extended constructor domain; actual producer admission, cleanup and complete circuit cost separate.'}
    def save():a.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    for number,rows in enumerate(subspaces()):
        if time.monotonic()-started>=a.seconds:break
        masks=[combination(r,[mask for mask,v in old]) for r in rows]+[pmask]
        extras=[combination(r,[v for mask,v in old]) for r in rows]+[outside]
        assert len(Space(raw+targets+extras).values)==45
        current_net=dict(source);current_net['outputs']=net['outputs']+masks
        gates=[];record={'subspace_number':number,'old_extra_basis_rows':rows,'steps':[]};reports.append(record)
        while time.monotonic()-started<a.seconds:
            current=closure(raw,targets,extras,prefix=gates);gates=current['gates'];record['steps'].append({'closure':current});save()
            if current['status']=='value_witness_found':
                assert len(gates)<=30
                result.update(status='30_AND_complete_value_witness',AND_count=len(gates),gates=gates,outputs=current['outputs'],witness_basis_rows=rows,
                              seconds=time.monotonic()-started,cleanup_verified=False,native_verified=False)
                save();print(json.dumps({'status':result['status'],'gates':len(gates),'rows':rows}),flush=True);return
            if current['status']=='exact_quadratic_span_obstruction':record['status']=current['status'];break
            factor=solve(current_net,{'gates':gates},len(gates),min(a.factor_timeout,max(1,int(a.seconds-(time.monotonic()-started)))))
            record['steps'][-1]['factor']=factor
            if factor['status']=='sat':gates.append([factor['a'],factor['b']]);continue
            record['status']='chosen_interface_affine_product_obstruction' if factor['status']=='unsat' else 'factor_unknown_unresolved';break
        record['final_ANDs']=len(gates);save()
        print(json.dumps({'subspace':number,'rows':rows,'status':record.get('status','incomplete'),'gates':len(gates)}),flush=True)
    complete=len(reports)==651 and all(r.get('status','').endswith('obstruction') for r in reports)
    result.update(status='no_witness_in_chosen_external_direction' if complete else 'bounded_sweep_incomplete',all651_subspaces_completed=complete,seconds=time.monotonic()-started,
                  limits='Chosen external function only. No global lower bound; trusted factor UNSAT has no saved formal proof certificate. Any witness needs independent full-domain evaluation and complete native cleanup/phase cost.')
    save()


if __name__=='__main__':main()
