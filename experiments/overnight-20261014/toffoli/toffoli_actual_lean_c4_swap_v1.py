"""Actual lean alternative: regenerate c4 insteadc3; retain lowc1/c2."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load
from toffoli_carry_cleanup_closure_v1 import phase_closure

def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_bytes());raw,targets,original=load(net)
    c1=1<<15;c2=(1<<16)^c1;c3=(1<<17)^c2;c4=1<<18;c5=(1<<25)^c4;c6=(1<<27)^c5
    r1=1<<20;r2=(1<<21)^r1;r3=(1<<22)^r2
    physical={0:c1,1:c2,3:c4,6:r2,7:r3,8:(1<<23)^c3,10:c5,12:c6}
    masks=[physical.get(j,1<<(15+j)) for j in range(31) if j not in [2,10]]
    bank=[combination(mask,original) for mask in masks];reports=[]
    for e2_available in [True,False]:
        data=list(raw);data[4:7]=targets[24:27]
        if not e2_available:del data[9]
        seed=data+[combination(mask,original) for mask in [c1,c2]]
        result=phase_closure(seed,data+bank,original)
        s=[combination(mask,original) for mask in result['initial_original_masks']+[item['original_affine_mask'] for item in result['chain']]]
        pair=list(itertools.combinations(range(len(s)),2));products=s+[s[i]&s[j] for i,j in pair];q=Space(products)
        l4=net['outputs'][25]^net['outputs'][0]^1;l5=net['outputs'][26]^net['outputs'][1]^1
        p=c4 # p coherent chosencharged carryc4; additional measured-phase temporary is p*L4.
        extra=combination(p,original)&combination(l4,original)
        qplus=Space(products+[extra]+[extra&value for value in s])
        result.update(e2_available=e2_available,physical_bank_original_masks=masks,
                      retained_low_c1_c2_masks=[c1,c2],one_AND_phase_candidate_operands=[p,l4],
                      C6_in_P2_closed=q.express(combination(c6,original)) is not None,
                      C6_in_P2_plus_C4L4_times_closed=qplus.express(combination(c6,original)) is not None,
                      L4_original_mask=l4,L5_original_mask=l5)
        reports.append(result)
    receipt={'status':'actual_lean_c4_for_c3_swap_hypothesis_checked','domain_rows':1<<14,
             'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
             'cases':reports,'native_verified':False,
             'proposal':'One unconditional rebuiltc4 replaces old unconditionalc3; move oldc1/c2 rebuild earlier intoexistingplaceholder slots. For c6measurement, testone conditional AND c4*L4 plusfreequadratic phase insteadtwo conditionalc4/c5 rebuilds. Keep y3 loanbasis.',
             'limits':'Exact abstract14-input changed bank, no producer/allMR/native/fullcost qualification.'}
    args.output.write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
    print(json.dumps([{key:item[key] for key in ['e2_available','status','initial_rank','interface_rank','closed_rank','C6_in_P2_closed','C6_in_P2_plus_C4L4_times_closed']} for item in reports]))
if __name__=='__main__':main()
