"""Prepare one-AND measured c6 phase repair for actual lean cleanup spaces."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load

def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('closure',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_bytes());raw,targets,original=load(net);receipt=json.loads(args.closure.read_bytes())
    c4=1<<18;c5=(1<<25)^c4;c6=(1<<27)^c5
    a5=net['outputs'][1];l5=net['outputs'][26]^a5^1
    reports=[]
    for case in receipt['cases']:
        if not case['retain_low_c1_c2_c3']:continue
        masks=case['initial_original_masks']+[item['original_affine_mask'] for item in case['chain']]
        s=[combination(mask,original) for mask in masks];assert len(Space(s).values)==case['closed_rank']
        pairs=list(itertools.combinations(range(len(s)),2));products=s+[s[i]&s[j] for i,j in pairs];q=Space(products)
        phase=combination(c6,original);carry5=combination(c5,original);linear5=combination(l5,original)
        assert Space(s).express(linear5) is not None
        triple=[(s[i]&s[j])&linear5 for i,j in pairs]
        allproducts=Space(products+triple)
        reports.append({'e2_available':case['e2_available'],'S_rank':len(s),'P2_S_rank':len(q.values),
                        'C5_in_P2_S':q.express(carry5) is not None,'C6_in_P2_S':q.express(phase) is not None,
                        'C6_in_P2_plus_fixedL5_P2':allproducts.express(phase) is not None,
                        'L5_original_mask':l5,'L5_S_coordinate':Space(s).express(linear5),
                        'S_original_masks':masks,'C6_original_mask':c6,'fixedL5_product_union_rank':len(allproducts.values)})
    result={'status':'fixed_L5_one_AND_phase_search_prepared','source_lf_sha256':net['source_lf_sha256'],
            'domain_rows':1<<14,'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'closure_sha256':hashlib.sha256(args.closure.read_bytes()).hexdigest(),'cases':reports,
            'target':'Find affine a,b of S such that C6+(a*b)*L5 is quadratic in S; one conditional AND plus free quadratic/temporary erase phase instead of two conditional carry ANDs.',
            'limits':'Span membership only, no decomposable factor witness or native/producer/fullcost claim.'}
    args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps([{key:item[key] for key in ['e2_available','S_rank','P2_S_rank','C5_in_P2_S','C6_in_P2_S','C6_in_P2_plus_fixedL5_P2','fixedL5_product_union_rank']} for item in reports]))
if __name__=='__main__':main()
