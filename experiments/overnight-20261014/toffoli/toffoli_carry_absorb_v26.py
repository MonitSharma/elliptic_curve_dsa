"""Exact absorption of carry13 into all remaining correction fields; rank only."""
import argparse,hashlib,json,time
from pathlib import Path
from toffoli_guided_joint import Space
from toffoli_consume_four_contract_v13 import load_fast

def main():
    p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('consumer',type=Path)
    p.add_argument('--netlist',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();start=time.monotonic();old=json.loads(args.original.read_bytes());base=json.loads(args.consumer.read_bytes())
    assert base['input_count']==21 and len(base['gates'])==38 and len(base['outputs'])==26
    gates=list(base['gates']);o=base['outputs'];carry=o[25];v=[]
    for i in range(4):
        v.append(o[i]^carry);gates.append({'name':f'absorb_carry_{14+i}','a':o[i],'b':carry})
        carry=1<<(22+len(gates)-1)
    carry17=carry;signlo=o[4]^carry17;hp=[]
    for i in range(3):
        hp.append(o[5+i]^carry);gates.append({'name':f'absorb_H_carry_{i+1}','a':o[5+i],'b':carry})
        carry=1<<(22+len(gates)-1)
    hp+=[o[8]^carry]+o[9:12]
    net=dict(base,gates=gates,outputs=v+[signlo]+hp+[o[4]]+o[12:25],
             outputs_order='V13..V16,signLo17..31,Hprime32..38,signHi39..,low_result0..12',
             limits='Absorbed effective higher addend (addend>>13)+carry13; exact primitive values only. No nonlinear cancellation witness, cleanup/phase/native/width/full-score claim.')
    args.netlist.write_bytes((json.dumps(net,indent=2)+'\n').encode());raw,targets,values=load_fast(net)
    expected=[bytearray(1<<18) for _ in range(26)];carry17k=set();kvalues=set();carry17cases=0
    lowband=sum(1<<i for i in range(4,19));highband=sum(1<<i for i in range(26,243))
    for primitive in range(1<<14):
        acc=primitive&63;e=(primitive>>6)&7;nm=(primitive>>9)&7;k1=(primitive>>12)&1;k2=(primitive>>13)&1
        c3=int((acc&7)+e>=8);c4=((acc>>3)&1)&c3;q=nm+(acc&7)
        a4=q&1;a5=(q^(q>>1))&1;a,z=(acc>>4)&1,(acc>>5)&1
        c5=(a&a4)|(a&c4)|(a4&c4)
        y3=(k1|k2)*(((acc>>3)&1)^c3);y4=k2*(a^c4^a4);y5=(k1&k2)*(z^c5^a5)
        k=q+8*(y3+2*y4+4*y5-c3);kvalues.add(k)
        addend=(-(2**32+976)*k)&((1<<256)-1);oldsign=addend>>17&1;oldh=addend>>32&127
        assert oldsign==int(k>0)
        for high in range(128):
            row=primitive|(high<<14);total=(acc|(high<<6))+e+(addend&8191);cin=total>>13
            upper=(addend>>13)+cin;vv=upper&15;sl=upper>>4&1;hh=upper>>19&127;sh=upper>>26&1
            reconstructed=vv|(sl*lowband)|(hh<<19)|(sh*highband)
            assert reconstructed==upper and sh==oldsign
            c17=((addend>>13&15)+cin)>>4
            assert sl==(oldsign^c17) and hh==oldh+c17 and ((hh^oldh)>>4)==0
            if c17:carry17k.add(k);carry17cases+=1
            bits=[vv>>i&1 for i in range(4)]+[sl]+[hh>>i&1 for i in range(7)]+[sh]+[total>>i&1 for i in range(13)]
            for index,bit in enumerate(bits):
                if bit:expected[index][row>>3]|=1<<(row&7)
    assert kvalues==set(range(-7,71)) and carry17k<=set(range(1,9))
    assert targets==[int.from_bytes(data,'little') for data in expected]
    rank_raw=len(Space(raw).values);rank_target=len(Space(raw+targets).values)
    report={'status':'absorbed_complete_higher_addend_contract_verified','source_lf_sha256':old['source_lf_sha256'],
            'original_netlist_sha256':hashlib.sha256(args.original.read_bytes()).hexdigest(),
            'consumer_netlist_sha256':hashlib.sha256(args.consumer.read_bytes()).hexdigest(),
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'domain_rows':2097152,
            'arithmetic_mismatches':0,'independent_outputs_per_input':26,'complete_effective_higher_addend_bits_verified':[13,255],
            'k_range':[-7,70],'carry17_k_values':sorted(carry17k),'carry17_rows':carry17cases,
            'upper_H_bits4..6_unchanged_proved':True,'higher_word_overflow_rows':0,
            'raw_rank':rank_raw,'target_rank':rank_target,'rank_AND_lower_bound':rank_target-rank_raw,
            'direct_source_ANDs':len(gates),'previous_consumer_source_ANDs':38,
            'direct_AND_delta':len(gates)-38,'source_full_span_rank':len(Space(values).values),
            'construction':'Four carry ANDs absorb13 into U3..6; three ANDs increment H0..3 conditionally. Sourcek bound proves H4..6 unchanged; two separate sign bands retained.',
            'seconds':time.monotonic()-start,'qualified_score':None,
            'limits':'Exact changed nonlinear value obligations and direct45AND source only. No cancellation or cheaper complete netlist found; measurement cleanup/phase, arbitrary incoming quantum highword scheduling and physical allocation/full cost remain unqualified.'}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report),flush=True)
if __name__=='__main__':main()
