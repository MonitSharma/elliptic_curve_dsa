"""Exact low13/carry13 changed consumer obligations; rank only, no synthesis."""
import argparse,hashlib,json,time
from pathlib import Path
from toffoli_guided_joint import Space
from toffoli_consume_four_contract_v13 import load_fast

def main():
    p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('--netlist',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args();start=time.monotonic()
    old=json.loads(args.original.read_bytes())
    def moved(mask):return (mask&((1<<15)-1))|((mask>>15)<<22)
    gates=[dict(name=g['name'],a=moved(g['a']),b=moved(g['b'])) for g in old['gates']]
    outputs=[moved(mask) for mask in old['outputs']];carry=outputs[27];written=[]
    for i in range(7):
        a=1<<(15+i);field=outputs[2+i];written.append(a^field^carry)
        gates.append({'name':f'consume_carry_{7+i}','a':a^carry,'b':field^carry})
        carry^=1<<(22+len(gates)-1)
    net=dict(old,input_count=21,input_order=old['input_order']+',acc6..acc12',gates=gates,
             outputs=outputs[9:21]+outputs[21:27]+written+[carry],
             outputs_order='U3..U6,sign,H0..H6,low_result0..low_result12,carry13',
             limits='Value obligations/ranks only; consumes Q2..Q5 and U0..U2 (bits6..12), retaining U3..U6/sign/H and carry13. Fullcleanup/phase/higher-word/lifetime cost remain separate.')
    args.netlist.write_bytes((json.dumps(net,indent=2)+'\n').encode());raw,targets,values=load_fast(net)
    assert len(targets)==26
    expected=[bytearray(1<<18) for _ in range(26)];largest_total=0
    for base in range(1<<14):
        acc=base&63;e=(base>>6)&7;nm=(base>>9)&7;k1=(base>>12)&1;k2=(base>>13)&1
        c3=int((acc&7)+e>=8);c4=((acc>>3)&1)&c3
        q=nm+(acc&7);a4=q&1;a5=(q^(q>>1))&1;a,z=(acc>>4)&1,(acc>>5)&1
        c5=(a&a4)|(a&c4)|(a4&c4)
        y3=(k1|k2)*(((acc>>3)&1)^c3);y4=k2*(a^c4^a4);y5=(k1&k2)*(z^c5^a5)
        k=q+8*(y3+2*y4+4*y5-c3)
        addend=(-(2**32+976)*k)&((1<<56)-1)
        retained=[addend>>i&1 for i in range(13,17)]+[addend>>17&1]+[addend>>i&1 for i in range(32,39)]
        # Independent complete remaining original field_map, including both sign bands.
        sign=retained[4];reconstructed=sum(retained[i]<<(13+i) for i in range(4))
        reconstructed|=sum(sign<<i for i in range(17,32))
        reconstructed|=sum(retained[5+i]<<(32+i) for i in range(7))
        reconstructed|=sum(sign<<i for i in range(39,56))
        assert reconstructed==(addend&(((1<<56)-1)^8191))
        for high in range(128):
            row=base|(high<<14);total=(acc|(high<<6))+e+(addend&8191)
            largest_total=max(largest_total,total)
            bits=retained+[total>>i&1 for i in range(14)]
            for index,bit in enumerate(bits):
                if bit:expected[index][row>>3]|=1<<(row&7)
    expected=[int.from_bytes(data,'little') for data in expected];assert targets==expected
    assert largest_total<1<<14
    rank_raw=len(Space(raw).values);rank_target=len(Space(raw+targets).values);source_span=len(Space(values).values)
    report={'status':'low13_carry13_complete_value_obligation_rank_verified','source_lf_sha256':old['source_lf_sha256'],
            'original_netlist_sha256':hashlib.sha256(args.original.read_bytes()).hexdigest(),
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'domain_rows':1<<21,
            'arithmetic_mismatches':0,'independent_integer_outputs_per_input':26,
            'remaining_field_map_bits_checked':[13,55],'remaining_field_map_primitive_patterns':16384,
            'all_seven_added_accumulator_bits_arbitrary':True,'maximum_low_total':largest_total,
            'raw_rank':rank_raw,'target_rank':rank_target,'source_full_span_rank':source_span,
            'rank_AND_lower_bound':rank_target-rank_raw,'source_ANDs':len(gates),
            'target_truth_sha256':[hashlib.sha256(value.to_bytes(1<<18,'little')).hexdigest() for value in targets],
            'seconds':time.monotonic()-start,'qualified_score':None,
            'complete_cost_obligations':['new carry13 must seed unchanged higher ladder','all removed Q/U directions needed by old constructor erasures require new phase cleanup identities','seven ladder carry phase coefficients and any retained chunk endpoints must be discharged','physical lifetime must include all remaining fields and new garbage; raw rank is not qubit width'],
            'limits':net['limits']}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report),flush=True)
if __name__=='__main__':main()
