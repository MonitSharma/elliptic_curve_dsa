"""All2604 external rank39 planes for reverse V40 plus selected k1*W3."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure,load
from toffoli_external_mixed_v4 import mixed_planes
from toffoli_external_planes_v2 import subspaces
from toffoli_mixed_enumeration_v4 import reduced_rows


def external_planes():
    # Independent decomposition:651 direct-containing plus1953 mixed planes.
    rows=mixed_planes()+[tuple(list(old)+[64]) for old in subspaces()]
    reduced={reduced_rows(row) for row in rows}
    assert len(rows)==len(reduced)==2604
    # Independently enumerate all rank5 RREF planes in seven coordinates.
    direct=set()
    for pivots in itertools.combinations(range(7),5):
        slots=[(i,j) for i,p in enumerate(pivots) for j in range(p+1,7) if j not in pivots]
        for bits in range(1<<len(slots)):
            basis=[1<<p for p in pivots]
            for k,(i,j) in enumerate(slots):
                if bits>>k&1:basis[i]|=1<<j
            if any(value&64 for value in basis):direct.add(reduced_rows(basis))
    assert direct==reduced
    return sorted(rows,key=lambda basis:(sum(row.bit_count() for row in basis),basis))


def main():
    from toffoli_factor_solver import solve
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path)
    parser.add_argument('--seconds',type=int,default=2700);parser.add_argument('--pair',default='4,13')
    parser.add_argument('--factor-timeout',type=int,default=5);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_text());raw,targets,original=load(net)
    assert len(raw)==15 and len(net['gates'])==25
    i,j=map(int,args.pair.split(','));outside=raw[i]&raw[j]
    assert Space(original).express(outside) is None
    desired=Space(raw+targets);hidden=[]
    for k,value in enumerate(original[len(raw):]):
        if desired.add(value):hidden.append((1<<(len(raw)+k),value))
    assert len(hidden)==6 and len(desired.values)==40 and len(Space(raw+targets).values)==34
    source=dict(net);source['gates']=net['gates']+[{'name':f'outside_raw_{i}_{j}','a':1<<i,'b':1<<j}]
    coordinate_masks=[mask for mask,value in hidden]+[1<<(len(raw)+len(net['gates']))]
    coordinate_values=[value for mask,value in hidden]+[outside]
    first=[net['gates'][0]['a'],net['gates'][0]['b']]
    assert net['gates'][0]['name']=='kp1'
    planes=external_planes();reports=[];started=time.monotonic()
    result={'status':'running','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'domain_rows':1<<14,'original_ANDs':25,'raw_pair':[i,j],'outside_label':'k1*W3',
            'early_kp1_AND':first,'hidden_original_masks':[mask for mask,value in hidden],
            'outside_truth_sha256':hashlib.sha256(outside.to_bytes((1<<14)//8,'little')).hexdigest(),
            'enumeration':{'all_rank5_planes_in_7_dimensions':2667,'old_only_excluded':63,
                           'external_planes':2604,'p_containing':651,'mixed':1953,
                           'independent_methods':'mixed+direct decomposition and full seven-coordinate RREF agree exactly',
                           'set_sha256':hashlib.sha256(json.dumps(sorted(reduced_rows(row) for row in planes)).encode()).hexdigest()},
            'examined':reports,
            'scope':'Every rank39 interface in V40+span(k1*W3) containing the complete W34 reverse output/input span and some external direction. Early kp1 is retained as first AND. Restricted value-interface search; producer, cleanup and complete circuit cost separate.'}
    def save():args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    for number,rows in enumerate(planes):
        if time.monotonic()-started>=args.seconds:break
        masks=[combination(row,coordinate_masks) for row in rows]
        extras=[combination(row,coordinate_values) for row in rows]
        admitted=Space(raw+targets+extras)
        assert len(admitted.values)==39 and admitted.express(original[15]) is not None
        current_net=dict(source);current_net['outputs']=net['outputs']+masks
        gates=[first];record={'plane_number':number,'quotient_basis_rows':rows,'steps':[]};reports.append(record)
        while time.monotonic()-started<args.seconds:
            current=closure(raw,targets,extras,prefix=gates);gates=current['gates'];record['steps'].append({'closure':current})
            if current['status']=='value_witness_found':
                assert len(gates)<=24 and gates[0]==first
                check=list(raw)
                for a,b in gates:check.append(combination(a,check)&combination(b,check))
                assert all(combination(mask,check)==target for mask,target in zip(current['outputs'],targets))
                result.update(status='24_AND_joint_reverse_value_witness',AND_count=len(gates),gates=gates,
                              outputs=current['outputs'],witness_basis_rows=rows,
                              independently_replayed_truth_rows=1<<14,seconds=time.monotonic()-started,
                              cleanup_verified=False,native_verified=False)
                save();print(json.dumps({'status':result['status'],'ANDs':len(gates),'rows':rows}),flush=True);return
            if current['status']=='exact_quadratic_span_obstruction':record['status']=current['status'];break
            factor=solve(current_net,{'gates':gates},len(gates),min(args.factor_timeout,max(1,int(args.seconds-(time.monotonic()-started)))))
            record['steps'][-1]['factor']=factor
            if factor['status']=='sat':gates.append([factor['a'],factor['b']]);continue
            record['status']='chosen_interface_affine_product_obstruction' if factor['status']=='unsat' else 'factor_unknown_unresolved';break
        record['final_ANDs']=len(gates)
        if number%10==0:save()
        print(json.dumps({'plane':number,'rows':rows,'status':record.get('status','incomplete'),'ANDs':len(gates)}),flush=True)
    complete=len(reports)==2604 and all(record.get('status','').endswith('obstruction') for record in reports)
    result.update(status='no_24_AND_witness_in_selected_reverse_extension' if complete else 'bounded_reverse_external_sweep_incomplete',
                  all2604_external_planes_completed=complete,seconds=time.monotonic()-started,
                  limits='Only selected V40+span(k1*W3). Trusted factor UNSAT without formal proof dump; unknown/incomplete preserved; full producer/consumer/phase cost remains separate.')
    save()


if __name__=='__main__':main()
