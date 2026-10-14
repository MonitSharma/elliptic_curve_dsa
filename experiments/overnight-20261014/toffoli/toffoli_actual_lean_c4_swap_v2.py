"""Correct one-AND C5 factor and deferred y3'/TT ownership for missingE2."""
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
    r1=1<<20;r2=(1<<21)^r1;r3=(1<<22)^r2;y3loan=(1<<23)^c3;tt=1<<19
    physical={0:c1,1:c2,3:c4,6:r2,7:r3,8:y3loan,12:c6}
    masks=[physical.get(j,1<<(15+j)) for j in range(31) if j not in [2,10]]
    bank=[combination(mask,original) for mask in masks];reports=[]
    a4=net['outputs'][0];a5=net['outputs'][1];sum4=net['outputs'][25];sum5=net['outputs'][26]
    pa,pb=sum4^a4,a4^c4;l5=sum5^a5^1
    p=combination(pa,original)&combination(pb,original)
    assert p^combination(c4,original)==combination(c5,original)
    expected_phase=(p&combination(l5,original))^(combination(c4,original)&combination(l5,original))^(combination(a5,original)&combination(sum5,original))^combination(a5,original)
    assert expected_phase==combination(c6,original)
    for e2_available in [True,False]:
        data=list(raw);data[4:7]=targets[24:27]
        if not e2_available:del data[9]
        seed=data+[combination(mask,original) for mask in [c1,c2]]
        # If E2 is shed, defer y3' and TT throughesh, then repair y3'=MAJ(low2,E2,c2)+OR(k)*finalbit3.
        if not e2_available:seed.extend([combination(mask,original) for mask in [y3loan,tt]])
        result=phase_closure(seed,data+bank,original)
        s=[combination(mask,original) for mask in result['initial_original_masks']+[item['original_affine_mask'] for item in result['chain']]]
        pair=list(itertools.combinations(range(len(s)),2));products=s+[s[i]&s[j] for i,j in pair];q=Space(products)
        qplus=Space(products+[p]+[p&value for value in s])
        result.update(e2_available=e2_available,physical_bank_original_masks=masks,
                      retained_low_c1_c2_masks=[c1,c2],retained_through_esh_masks=[y3loan,tt] if not e2_available else [],
                      one_AND_phase_operands_original_masks=[pa,pb],
                      C6_in_P2_closed=q.express(combination(c6,original)) is not None,
                      C6_in_P2_plus_one_AND_times_closed=qplus.express(combination(c6,original)) is not None,
                      L5_original_mask=l5,all16384_C5_and_C6_phase_factor_rows_verified=True)
        reports.append(result)
    receipt={'status':'actual_lean_c4_swap_and_one_AND_C6_factor_checked','domain_rows':1<<14,
             'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
             'cases':reports,'native_verified':False,
             'proposal':'Replaceunconditionalc3 regeneration by unconditionalc4; moveoldc1/c2 earlier intoexistingplaceholders. C6 phase usesoneconditional AND p=(sum4+a4)*(a4+c4), with C5=p+c4, insteadtwoconditionalcarry ANDs. MissingE2 casekeepsy3loan+TT throughesh forfreequadratic repair afterE2 returns.',
             'limits':'Exact unrestricted14-input value/phase identities and closed-space construction. Physical schedule, peak/allocator, allMR and fullproducer/native qualification pending.'}
    args.output.write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
    print(json.dumps([{key:item[key] for key in ['e2_available','status','initial_rank','interface_rank','closed_rank','C6_in_P2_closed','C6_in_P2_plus_one_AND_times_closed']} for item in reports]))
if __name__=='__main__':main()
