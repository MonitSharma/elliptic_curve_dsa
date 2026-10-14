"""Exact admitted guard identity permitting original MAJ c3 regeneration."""
import argparse
import hashlib
import json
from pathlib import Path
from toffoli_guided_joint import combination
from toffoli_quadratic_closure import load

def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_bytes());raw,targets,values=load(net)
    c1=values[15];c2=values[16]^c1;c3=values[17]^c2;tt=values[19]
    y3_loan=values[23]^c3;gate=raw[13]^raw[14]^tt;bit3=targets[24]
    original_maj=(raw[3]&raw[9])^(raw[3]&c2)^(raw[9]&c2)
    assert original_maj==c3==y3_loan^(gate&bit3)
    cases=[]
    for m5 in range(2):
        for m3 in range(2):
            need=m5|(m3&(1^m5))
            cases.append({'y5_measurement':m5,'y3_measurement':m3,
                          'tt_built_at_y5':m5,'tt_built_at_y3':m3&(1^m5),'final_need':need,
                          'old_unconditional_TT_ANDs':1,'new_conditional_TT_ANDs':need})
    result={'status':'all16384_original_c3_MAJ_and_consumer_loan_identity_verified',
            'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'domain_rows':1<<14,'guard':'loan && fin==0 && ttm; c2,E2,acc2 coherently live',
            'identity':'c3=MAJ(acc2,E2,c2)=y3_loan+OR(k1,k2)*final_bit3',
            'TT_need_table':cases,'old_TT_regeneration_ANDs':1,'new_mean_TT_regeneration_ANDs':0.75,
            'prospective_mean_saving_per_guarded_fold':0.25,
            'phase_status':'Existing source TtLate OR(y5,y3) protocol restored to normal conditional AND construction; full modified native all-measurement verification pending.',
            'native_verified':False,'limits':'Only original carry availablefin0 guard. No fullcircuit count, measurement phase or record claim. Actual producer contexts and full modified cleanup still need native/exact verification.'}
    args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({'status':result['status'],'domain_rows':result['domain_rows'],'prospective_mean_saving_per_guarded_fold':0.25}))
if __name__=='__main__':main()
