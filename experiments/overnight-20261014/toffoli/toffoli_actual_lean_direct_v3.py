"""Exact source-order identities for actual lean one-AND c6 cleanup.

Y16 records can be cleared before ESh restoration without reading any original
E/c1/c2/c3/c4/c5/TT value. Fin3 native scheduling first; fin4 producer still
requires physical boundary verification even though table cleanup frees14 slots.
"""
import argparse
import hashlib
import json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load

def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();net=json.loads(args.netlist.read_bytes());raw,targets,original=load(net)
    c1=1<<15;c2=(1<<16)^c1;c3=(1<<17)^c2;c4=1<<18;c5=(1<<25)^c4;c6=(1<<27)^c5
    r1=1<<20;r2=(1<<21)^r1;r3=(1<<22)^r2;y3=(1<<23)^c3;y4=1<<24;y5=1<<26
    tt=1<<19;g=(1<<13)^(1<<14)^tt;s3=net['outputs'][24];s4=net['outputs'][25];s5=net['outputs'][26]
    a4=net['outputs'][0];a5=net['outputs'][1];t3=1<<28;t4=1<<29;t5=1<<30;sign=1<<31
    physical={0:c1,1:c2,2:c3,3:c4,6:r2,7:r3,8:y3,10:c5,12:c6}
    # Actual precleanup: allthree original E values may be unavailable.
    data=[1,1<<1,1<<2,1<<3,s3,s4,s5]+[1<<i for i in range(10,15)]
    available_names=['1','acc0','acc1','acc2','final3','final4','final5','Nm0','Nm1','Nm2','k1','k2']
    available=list(data);table=[]
    for j in range(31):
        if j in [0,1,2,3,4,10]:continue
        if j>=17:
            basis=Space([combination(mask,original) for mask in available])
            gate=net['gates'][j]
            coordinates=[basis.express(combination(gate[key],original)) for key in ['a','b']]
            assert all(mask is not None for mask in coordinates)
            table.append({'original_gate_index':j,'name':gate['name'],'available_physical_names':list(available_names),
                          'available_original_masks':list(available),'operands_coordinates':coordinates})
        available.append(physical.get(j,1<<(15+j)));available_names.append(net['gates'][j]['name'])
    assert len(table)==14
    def V(mask):return combination(mask,original)
    checks={
        'new_c4_from_final3_and_y3loan':V(c4)==((~V(s3))&V(y3)),
        'upper3_two_quadratic_terms':V(t3)==((V(r3)^raw[0])&V(y3))^(V(g)&(V(y3)^V(c4))),
        'upper4_c3_free':V(t4)==V(t3)&(V(y4)^V(r3)^raw[0]),
        'upper5_c3_free':V(t5)==V(t4)&(V(y5)^V(r3)^raw[0]),
        'sign_c3_free':V(sign)==V(t5)&(V(r3)^raw[0]),
        'y3loan_free_phase_after_E_returns':V(y3)==((V(1<<3)^V(c2))&(V(1<<9)^V(c2)))^V(c2)^(V(g)&V(s3)),
        'y4_final_data':V(y4)==V(1<<14)&V(s4),
        'y5_final_data':V(y5)==V(tt)&V(s5),
    }
    pa,pb=s4^a4,a4^c4;p=V(pa)&V(pb);l5=s5^a5^1
    checks['one_AND_C5_factor']=V(c5)==p^V(c4)
    checks['one_AND_C6_phase']=V(c6)==(p&V(l5))^(V(c4)&V(l5))^(V(a5)&V(s5))^V(a5)
    assert all(checks.values())
    # Low0..2 are unchanged until last carry repairs, then ordinary sums finish.
    low=[(1<<1)^(1<<7),(1<<2)^(1<<8)^c1,(1<<3)^(1<<9)^c2]
    assert all(V(mask)==target for mask,target in zip(low,targets[21:24]))
    result={'status':'actual_lean_direct_schedule_all16384_phase_identities_verified',
            'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'domain_rows':1<<14,'table_records':table,'exact_phase_checks':checks,
            'core_original_masks':{'c1':c1,'c2':c2,'c3':c3,'c4':c4,'c5':c5,'c6':c6,'r1':r1,'r2':r2,'r3':r3,'y3loan':y3,'y4':y4,'y5':y5,'tt':tt,'g':g,'t3':t3,'t4':t4,'t5':t5,'sign':sign,'a4':a4,'a5':a5,'final3':s3,'final4':s4,'final5':s5},
            'C6_conditional_AND_operands':[pa,pb],'C6_L5_mask':l5,
            'schedule':['clear14Y16 records usingc3-free loan-basis operands','restoreESh ifseparatelyadmitted','regeneratec1/c2 atsameold2ANDcost','regenerateTT atsameold1ANDcost','regeneratec4 insteadoldc3 atsame1ANDcost','measurec6;oneconditionalC5factor AND+quadraticphase andexacttemporaryerase','clearupper sign,upper5,upper4,upper3 withquadraticidentities','clearY5/Y4,thennewc4,thenY3loan withrestoredE','clearr3/r2/r1 andTT','ordinarylow2/1/0 writes andc2/c1 measurementerase'],
            'prospective_mean_Toffoli_delta':-0.5,'native_verified':False,
            'native_first_guard':'loan && fin==3 && ttm && lean45 && drop==0',
            'actual_fin4_status':'producer_unadmitted_until_sourcephysicalESH restoration andboundaryphaseverified',
            'limits':'Exact primitive identities do not alone provephysicalwire ownership, ESh producer, peak/freelist orfullpointaddition. No score.'}
    args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({'status':result['status'],'table_erasures_before_ESh':len(table),'checks':checks,'prospective_mean_Toffoli_delta':-0.5}))
if __name__=='__main__':main()
