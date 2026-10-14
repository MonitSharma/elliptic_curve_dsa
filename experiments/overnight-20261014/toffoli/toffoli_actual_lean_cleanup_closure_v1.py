"""Actual lean hypothesis: retain rebuilt low carries, omit c4/c5 reconstruction."""
import argparse
import hashlib
import json
from pathlib import Path
from toffoli_guided_joint import combination
from toffoli_quadratic_closure import load
from toffoli_carry_cleanup_closure_v1 import phase_closure

def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_bytes());raw,targets,original=load(net)
    c1=1<<15;c2=(1<<16)^c1;c3=(1<<17)^c2;c4=1<<18;c5=(1<<25)^c4;c6=(1<<27)^c5
    r1=1<<20;r2=(1<<21)^r1;r3=(1<<22)^r2
    physical={0:c1,1:c2,2:c3,3:c4,6:r2,7:r3,10:c5,12:c6}
    # Source has already restored original y3 basis, TT and c3 here.
    masks=[physical.get(j,1<<(15+j)) for j in range(31) if j not in [3,10]]
    bank=[combination(mask,original) for mask in masks];reports=[]
    for e2_available in [True,False]:
        for retain_low in [False,True]:
            if not retain_low and not e2_available:continue
            data=list(raw);data[4:7]=targets[24:27]
            seed=list(data)
            if not e2_available:del data[9];del seed[9]
            if retain_low:seed.extend([combination(mask,original) for mask in [c1,c2,c3]])
            else:seed[1:4]=targets[21:24]
            result=phase_closure(seed,data+bank,original)
            result.update(e2_available=e2_available,retain_low_c1_c2_c3=retain_low,
                          bank_original_masks=masks,
                          proposal='Rebuildc1/c2 into clean c4/c5 placeholder slots before corecleanup; keep original c3 and TT regeneration; omit conditionalc4/c5 regeneration only if fullphase cleanup exists')
            reports.append(result)
    receipt={'status':'actual_lean_phase_interface_hypothesis_checked','domain_rows':1<<14,
             'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
             'cases':reports,'native_verified':False,
             'limits':'Physical majority c6 represented as AND+c5 even though c5 is absent. E2-missing case retains original lowdata and rebuilt lowcarries for ordinary tail afteresh. Abstract unrestricted14-input interface only; producer/conditionalbranches/fullcost separate.'}
    args.output.write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
    print(json.dumps([{key:item[key] for key in ['e2_available','retain_low_c1_c2_c3','status','initial_rank','interface_rank','closed_rank']} for item in reports]))
if __name__=='__main__':main()
