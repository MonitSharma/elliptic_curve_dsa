"""Bounded single raw-product auxiliary interfaces for changed four-write contract."""
import argparse,hashlib,itertools,json,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure
from toffoli_consume_four_contract_v13 import load_fast

def projection(value,space):
    for bit,(other,_) in sorted(space.rows.items(),reverse=True):
        if value>>bit&1:value^=other
    return value

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--describe-only',action='store_true');p.add_argument('--seconds',type=int,default=900)
    p.add_argument('--factor-timeout',type=int,default=5);args=p.parse_args();net=json.loads(args.netlist.read_bytes())
    raw,targets,old=load_fast(net);w=Space(raw+targets);groups={};inside=[]
    for i,j in itertools.combinations(range(1,len(raw)),2):
        value=raw[i]&raw[j];coset=projection(value,w)
        if not coset:inside.append([i,j]);continue
        if coset not in groups:groups[coset]={'representative':[i,j],'pairs':[],'value':value}
        groups[coset]['pairs'].append([i,j])
    selected=sorted(groups.values(),key=lambda item:item['representative'])
    report={'status':'description_only' if args.describe_only else 'running','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'domain_rows':1<<18,
            'raw_rank':19,'base_interface_rank':len(w.values),'candidate_interface_rank':len(w.values)+1,
            'value_AND_budget':len(w.values)+1-19,'source_ANDs':35,'raw_pairs_total':153,'inside_pairs':inside,
            'distinct_external_cosets':len(selected),'interfaces':[{'representative':item['representative'],'equivalent_pairs':item['pairs'],
            'product_truth_sha256':hashlib.sha256(item['value'].to_bytes(32768,'little')).hexdigest()} for item in selected],
            'examined':[],'qualified_score':None,'formal_proof_certificate_saved':False,
            'scope':'Changed constructor plus four writes, one auxiliary raw-coordinate product; all153 pairs deduplicated exactly modulo changedoutput span.',
            'limits':'Selected single raw-product family only. Arbitrary affine products, more auxiliary directions, phase ownership, physical cleanup, higher arithmetic and full record remain open.'}
    def save():args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    if args.describe_only:save();print(json.dumps({'external_cosets':len(selected),'inside_pairs':inside,'candidate_rank':len(w.values)+1,'AND_budget':report['value_AND_budget']}));return
    import toffoli_factor_solver as factor
    # Use exact full18-bit truth loading, preserving the unchanged research equations.
    factor.load=load_fast;started=time.monotonic()
    for index,item in enumerate(selected):
        if time.monotonic()-started>=args.seconds:break
        i,j=item['representative'];value=item['value'];current=dict(net)
        current['gates']=net['gates']+[{'name':f'aux_raw_{i}_{j}','a':1<<i,'b':1<<j}]
        current['outputs']=net['outputs']+[1<<len(old)]
        row={'index':index,'representative':[i,j],'steps':[]};report['examined'].append(row);gates=[]
        while time.monotonic()-started<args.seconds:
            result=closure(raw,targets,[value],prefix=gates);gates=result['gates'];step={'closure':result};row['steps'].append(step)
            if result['status']=='value_witness_found':
                check=list(raw)
                for a,b in gates:check.append(combination(a,check)&combination(b,check))
                assert len(gates)<=report['value_AND_budget'] and [combination(mask,check) for mask in result['outputs']]==targets
                report.update(status='atmost25_AND_complete_changed_value_witness',gates=gates,outputs=result['outputs'],AND_count=len(gates),witness_representative=[i,j],independent_truth_rows_replayed=262144)
                save();print(json.dumps({'status':report['status'],'ANDs':len(gates),'pair':[i,j]}),flush=True);return
            if result['status']=='exact_quadratic_span_obstruction':row['status']=result['status'];break
            remaining=args.seconds-time.monotonic()+started
            if remaining<1:break
            solved=factor.solve(current,{'gates':gates},len(gates),min(args.factor_timeout,max(1,int(remaining))))
            if solved.pop('all_16384_truth_rows_verified',False):solved['all_truth_rows_verified']=262144
            step['factor']=solved
            if solved['status']=='sat':gates.append([solved['a'],solved['b']]);continue
            row['status']='fixed_interface_closed_affine_product_UNSAT' if solved['status']=='unsat' else 'factor_unknown_unresolved';break
        row['final_ANDs']=len(gates);save();print(json.dumps({'index':index,'pair':[i,j],'status':row.get('status','incomplete'),'ANDs':len(gates)}),flush=True)
    complete=len(report['examined'])==len(selected) and all(row.get('status') in ['exact_quadratic_span_obstruction','fixed_interface_closed_affine_product_UNSAT'] for row in report['examined'])
    report.update(status='selected_changed_consumer_interfaces_closed_negative' if complete else 'bounded_sweep_incomplete_or_unknown',completed_all_selected_interfaces=complete,seconds=time.monotonic()-started);save()

if __name__=='__main__':main()
