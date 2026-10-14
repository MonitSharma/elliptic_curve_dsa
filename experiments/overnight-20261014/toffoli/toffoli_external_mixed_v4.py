"""The1953 mixed-coset rank45 interfaces in original V46 plus acc3*k1."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure,load


def mixed_planes():
    all_rows=[]
    for pivots in itertools.combinations(range(7),5):
        slots=[(i,j) for i,p in enumerate(pivots) for j in range(p+1,7) if j not in pivots]
        for bits in range(1<<len(slots)):
            rows=[1<<p for p in pivots]
            for k,(i,j) in enumerate(slots):
                if bits>>k&1:rows[i]|=1<<j
            assert len(Space(rows).values)==5
            all_rows.append(tuple(rows))
    assert len(all_rows)==len(set(all_rows))==2667
    old=[r for r in all_rows if not any(x&64 for x in r)]
    contains_p=[r for r in all_rows if Space(r).express(64) is not None]
    mixed=[r for r in all_rows if any(x&64 for x in r) and Space(r).express(64) is None]
    assert len(old)==63 and len(contains_p)==651 and len(mixed)==1953
    return sorted(mixed,key=lambda rows:(sum(r.bit_count() for r in rows),rows))


def main():
    from toffoli_factor_solver import solve
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path)
    parser.add_argument('--seconds',type=int,default=2700);parser.add_argument('--pair',default='4,13')
    parser.add_argument('--factor-timeout',type=int,default=5);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_text());raw,targets,original=load(net)
    i,j=map(int,args.pair.split(','));outside=raw[i]&raw[j]
    assert Space(original).express(outside) is None
    desired=Space(raw+targets);old=[]
    for k,value in enumerate(original[len(raw):]):
        if desired.add(value):old.append((1<<(len(raw)+k),value))
    assert len(old)==6
    source=dict(net);source['gates']=net['gates']+[{'name':f'outside_raw_{i}_{j}','a':1<<i,'b':1<<j}]
    coordinate_masks=[mask for mask,value in old]+[1<<(len(raw)+len(net['gates']))]
    coordinate_values=[value for mask,value in old]+[outside]
    reports=[];started=time.monotonic()
    result={'status':'running','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'domain_rows':1<<14,'raw_pair':[i,j],'old_extra_masks':[mask for mask,value in old],
            'outside_truth_sha256':hashlib.sha256(outside.to_bytes((1<<14)//8,'little')).hexdigest(),
            'enumeration':{'quotient_dimension':7,'plane_dimension':5,'all_planes':2667,
                           'excluded_old_only':63,'excluded_containing_p':651,'selected_mixed':1953},
            'examined':reports,
            'scope':'Every remaining rank45 interface inside V46+span(p) containing W40 but not p itself. The selected external p is acc3*k1. Original-span planes and planes containing p were separate completed searches. Extended constructor domain; producer admission, native cleanup and complete circuit cost separate.'}
    def save():args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    for number,rows in enumerate(mixed_planes()):
        if time.monotonic()-started>=args.seconds:break
        masks=[combination(row,coordinate_masks) for row in rows]
        extras=[combination(row,coordinate_values) for row in rows]
        assert len(Space(raw+targets+extras).values)==45
        current_net=dict(source);current_net['outputs']=net['outputs']+masks
        gates=[];record={'plane_number':number,'quotient_basis_rows':rows,'steps':[]};reports.append(record)
        while time.monotonic()-started<args.seconds:
            current=closure(raw,targets,extras,prefix=gates);gates=current['gates']
            record['steps'].append({'closure':current})
            if current['status']=='value_witness_found':
                assert len(gates)<=30
                check=list(raw)
                for a,b in gates:check.append(combination(a,check)&combination(b,check))
                assert all(combination(mask,check)==target for mask,target in zip(current['outputs'],targets))
                result.update(status='30_AND_complete_value_witness',AND_count=len(gates),gates=gates,
                              outputs=current['outputs'],witness_basis_rows=rows,
                              independently_replayed_truth_rows=1<<14,seconds=time.monotonic()-started,
                              cleanup_verified=False,native_verified=False)
                save();print(json.dumps({'status':result['status'],'gates':len(gates),'rows':rows}),flush=True);return
            if current['status']=='exact_quadratic_span_obstruction':record['status']=current['status'];break
            factor=solve(current_net,{'gates':gates},len(gates),min(args.factor_timeout,max(1,int(args.seconds-(time.monotonic()-started)))))
            record['steps'][-1]['factor']=factor
            if factor['status']=='sat':gates.append([factor['a'],factor['b']]);continue
            record['status']='chosen_interface_affine_product_obstruction' if factor['status']=='unsat' else 'factor_unknown_unresolved';break
        record['final_ANDs']=len(gates)
        if number%10==0:save()
        print(json.dumps({'plane':number,'rows':rows,'status':record.get('status','incomplete'),'gates':len(gates)}),flush=True)
    complete=len(reports)==1953 and all(record.get('status','').endswith('obstruction') for record in reports)
    result.update(status='no_witness_in_chosen_mixed_interfaces' if complete else 'bounded_sweep_incomplete',
                  all1953_mixed_planes_completed=complete,seconds=time.monotonic()-started,
                  limits='Only selected V46+span(acc3*k1). Trusted factor UNSAT without formal proof dump. Unknown, incomplete and native/phase/cost qualification remain distinct.')
    save()


if __name__=='__main__':main()
