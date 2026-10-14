"""Restricted constructive search with one temporary outside the old span."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space
from toffoli_quadratic_closure import closure,load
from toffoli_factor_solver import solve


def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('--seconds',type=int,default=600)
    p.add_argument('--factor-timeout',type=int,default=5);p.add_argument('--pairs',type=int,default=6)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    net=json.loads(a.netlist.read_text());raw,targets,original=load(net)
    source_span=Space(original);want=Space(raw+targets);old_extras=[]
    for j,value in enumerate(original[len(raw):]):
        if want.add(value):old_extras.append((1<<(len(raw)+j),value))
    assert len(old_extras)==6
    priority=[(4,13),(4,14),(5,13),(5,14),(6,13),(6,14)]
    pairs=priority+[x for x in itertools.combinations(range(1,len(raw)),2) if x not in priority]
    pairs=[(i,j) for i,j in pairs if source_span.express(raw[i]&raw[j]) is None][:a.pairs]
    reports=[];started=time.monotonic()
    result={'status':'running','source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(a.netlist.read_bytes()).hexdigest(),
            'domain_rows':1<<14,'old_function_span_rank':46,'examined':reports,
            'scope':'One selected pure raw-input quadratic outside the original span plus four selected original extra directions modulo the complete output span. Negative results cover only these explicitly selected interfaces.'}
    def save():a.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    for i,j in pairs:
        pvalue=raw[i]&raw[j]
        assert source_span.express(pvalue) is None
        modified=dict(net);modified['gates']=net['gates']+[{'name':f'raw_{i}_{j}','a':1<<i,'b':1<<j}]
        pmask=1<<(len(raw)+len(net['gates']))
        for chosen in itertools.combinations(range(6),4):
            if time.monotonic()-started>=a.seconds:break
            extras=[old_extras[k][1] for k in chosen]+[pvalue]
            masks=[old_extras[k][0] for k in chosen]+[pmask]
            assert len(Space(raw+targets+extras).values)==45
            target_net=dict(modified);target_net['outputs']=net['outputs']+masks
            gates=[];steps=[];record={'raw_pair':[i,j],'old_extra_indices':list(chosen),'steps':steps};reports.append(record)
            while time.monotonic()-started<a.seconds:
                current=closure(raw,targets,extras,prefix=gates);gates=current['gates'];steps.append({'closure':current});save()
                if current['status']=='value_witness_found':
                    assert len(gates)<=30
                    result.update(status='30_AND_complete_value_witness',AND_count=len(gates),gates=gates,
                                  outputs=current['outputs'],raw_pair=[i,j],old_extra_indices=list(chosen),
                                  seconds=time.monotonic()-started,cleanup_verified=False,native_verified=False,submission_ready=False)
                    save();print(json.dumps({'status':result['status'],'gates':len(gates),'pair':[i,j],'extras':chosen}),flush=True);return
                if current['status']=='exact_quadratic_span_obstruction':record['status']=current['status'];break
                factor=solve(target_net,{'gates':gates},len(gates),min(a.factor_timeout,max(1,int(a.seconds-(time.monotonic()-started)))))
                steps[-1]['factor']=factor
                if factor['status']=='sat':gates.append([factor['a'],factor['b']]);continue
                record['status']='chosen_interface_affine_product_obstruction' if factor['status']=='unsat' else 'factor_unknown_unresolved';break
            record['final_ANDs']=len(gates);save()
            print(json.dumps({'pair':[i,j],'extras':chosen,'status':record.get('status','incomplete'),'gates':len(gates)}),flush=True)
    result.update(status='no_witness_in_selected_interfaces',seconds=time.monotonic()-started,
                  limits='Restricted constructive probe only. Solver UNSAT has no saved formal certificate; unknown/incomplete interfaces remain open. No global optimality or complete gate-cost conclusion.')
    save()


if __name__=='__main__':main()
