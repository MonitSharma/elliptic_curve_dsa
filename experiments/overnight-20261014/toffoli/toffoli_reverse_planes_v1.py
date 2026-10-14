"""Exact original-span reverse joint25->24 AND probe with early kp1 retained."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure,load
from toffoli_factor_solver import solve


def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path)
    parser.add_argument('--seconds',type=int,default=600);parser.add_argument('--timeout',type=int,default=5)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    net=json.loads(args.netlist.read_text());raw,targets,original=load(net)
    full=Space(raw+targets);hidden=[]
    for i,value in enumerate(original[len(raw):]):
        if full.add(value):hidden.append((1<<(len(raw)+i),value))
    assert len(hidden)==6 and len(Space(raw+targets).values)==34 and len(full.values)==40
    first=[net['gates'][0]['a'],net['gates'][0]['b']]
    assert net['gates'][0]['name']=='kp1'
    reports=[];started=time.monotonic()
    result={'status':'running','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'domain_rows':1<<14,'original_AND_count':len(net['gates']),
            'raw_rank':15,'target_plus_raw_rank':34,'original_internal_rank':40,
            'early_kp1_AND':first,'hidden_original_masks':[mask for mask,value in hidden],'planes':reports,
            'scope':'All63 rank39 original-span hyperplanes containing complete reverse addend fields and raw inputs. First AND is original kp1, supporting early low n1/c5/c6 scheduling. W producer admission and complete consumer/measurement cleanup remain separate.'}
    def save():args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    for plane in sorted(range(1,64),key=lambda x:(x.bit_count(),x)):
        if time.monotonic()-started>=args.seconds:break
        pivot=(plane&-plane).bit_length()-1
        extras=[value^(hidden[pivot][1] if plane>>j&1 else 0) for j,(mask,value) in enumerate(hidden) if j!=pivot]
        masks=[mask^(hidden[pivot][0] if plane>>j&1 else 0) for j,(mask,value) in enumerate(hidden) if j!=pivot]
        admitted=Space(raw+targets+extras)
        assert len(admitted.values)==39 and admitted.express(original[15]) is not None
        augmented=dict(net);augmented['outputs']=net['outputs']+masks
        gates=[first];record={'hyperplane':plane,'extra_original_masks':masks,'steps':[]};reports.append(record)
        while time.monotonic()-started<args.seconds:
            current=closure(raw,targets,extras,prefix=gates);gates=current['gates'];record['steps'].append({'closure':current})
            save()
            if current['status']=='value_witness_found':
                assert len(gates)<=24 and gates[0]==first
                check=list(raw)
                for a,b in gates:check.append(combination(a,check)&combination(b,check))
                assert all(combination(mask,check)==value for mask,value in zip(current['outputs'],targets))
                result.update(status='24_AND_joint_reverse_value_witness',AND_count=len(gates),gates=gates,
                              outputs=current['outputs'],hyperplane=plane,seconds=time.monotonic()-started,
                              independently_replayed_rows=1<<14,native_cleanup_verified=False,submission_ready=False)
                save();print(json.dumps({'status':result['status'],'ANDs':len(gates),'hyperplane':plane}),flush=True);return
            if current['status']=='exact_quadratic_span_obstruction':record['status']=current['status'];break
            factor=solve(augmented,{'gates':gates},len(gates),min(args.timeout,max(1,int(args.seconds-(time.monotonic()-started)))))
            record['steps'][-1]['factor']=factor
            if factor['status']=='sat':gates.append([factor['a'],factor['b']]);continue
            record['status']='chosen_interface_affine_product_obstruction' if factor['status']=='unsat' else 'factor_unknown_unresolved';break
        record['final_ANDs']=len(gates);save()
        print(json.dumps({'plane':plane,'status':record.get('status','incomplete'),'ANDs':len(gates)}),flush=True)
    complete=len(reports)==63 and all(record.get('status','').endswith('obstruction') for record in reports)
    result.update(status='no_24_AND_witness_in_original_reverse_span' if complete else 'bounded_reverse_sweep_incomplete',
                  all63_planes_completed=complete,seconds=time.monotonic()-started,
                  limits='Only original internal span. Trusted UNSAT without formal proof certificate; outside functions, actual producer admission and cleanup/full cost separate.')
    save()


if __name__=='__main__':main()
