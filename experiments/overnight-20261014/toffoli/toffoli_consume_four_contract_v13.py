"""Exact constructor plus first four ladder writes; changed output obligations.

No native cleanup or resource result follows from this value contract.
"""
import argparse,hashlib,json,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure

def load_fast(net):
    count=net['input_count'];size=1<<(count-3)
    raw=[int.from_bytes(b'\xff'*size,'little')]
    for i in range(count):
        if i<3:data=bytes([0xaa,0xcc,0xf0][i:i+1])*size
        else:data=(bytes(1<<(i-3))+b'\xff'*(1<<(i-3)))*(1<<(count-i-1))
        assert len(data)==size;raw.append(int.from_bytes(data,'little'))
    values=list(raw)
    for gate in net['gates']:values.append(combination(gate['a'],values)&combination(gate['b'],values))
    return raw,[combination(mask,values) for mask in net['outputs']],values

def main():
    p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('--netlist',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args();old=json.loads(args.original.read_bytes())
    def moved(mask):return (mask&((1<<15)-1))|((mask>>15)<<19)
    gates=[dict(name=g['name'],a=moved(g['a']),b=moved(g['b'])) for g in old['gates']]
    outputs=[moved(mask) for mask in old['outputs']];carry=outputs[27];written=[]
    for i in range(4):
        a=1<<(15+i);field=outputs[2+i];written.append(a^field^carry)
        gates.append({'name':f'consume_carry_{7+i}','a':a^carry,'b':field^carry})
        carry^=1<<(19+len(gates)-1)
    net=dict(old,input_count=18,input_order=old['input_order']+',acc6,acc7,acc8,acc9',gates=gates,
             outputs=outputs[6:21]+outputs[21:27]+written+[carry],
             outputs_order='U0..U6,sign,H0..H6,low_result0..low_result9,carry10',
             limits='Value contract only: originalQfields consumed into four newly written accumulator bits. Measurement cleanup, arbitrary higher words and physical schedule unproved.')
    args.netlist.write_bytes((json.dumps(net,indent=2)+'\n').encode());raw,targets,values=load_fast(net)
    expected=[bytearray(1<<15) for _ in range(26)]
    for row in range(1<<18):
        acc=(row&63)|((row>>14&15)<<6);e=(row>>6)&7;nm=(row>>9)&7;k1=(row>>12)&1;k2=(row>>13)&1
        c3=int((acc&7)+e>=8);c4=((acc>>3)&1)&c3
        q=nm+(acc&7);a4=q&1;a5=(q^(q>>1))&1;a,z=(acc>>4)&1,(acc>>5)&1
        c5=(a&a4)|(a&c4)|(a4&c4)
        y3=(k1|k2)*(((acc>>3)&1)^c3);y4=k2*(a^c4^a4);y5=(k1&k2)*(z^c5^a5)
        k=q+8*(y3+2*y4+4*y5-c3)
        addend=(-(2**32+976)*k)&((1<<56)-1)
        total=acc+e+(addend&1023)
        bits=[addend>>i&1 for i in range(10,17)]+[addend>>17&1]+[addend>>i&1 for i in range(32,39)]
        bits += [total>>i&1 for i in range(11)]
        for i,bit in enumerate(bits):
            if bit:expected[i][row>>3]|=1<<(row&7)
    expected=[int.from_bytes(data,'little') for data in expected]
    assert targets==expected
    start=time.monotonic();result=closure(raw,targets)
    report={'status':'changed_four_consumer_value_contract_verified','source_lf_sha256':old['source_lf_sha256'],
            'original_netlist_sha256':hashlib.sha256(args.original.read_bytes()).hexdigest(),
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'domain_rows':1<<18,
            'arithmetic_mismatches':0,'independent_integer_outputs_per_input':26,'raw_rank':len(Space(raw).values),'target_rank':len(Space(raw+targets).values),
            'rank_AND_lower_bound':len(Space(raw+targets).values)-len(raw),'source_ANDs':len(gates),
            'closure':result,'closure_seconds':time.monotonic()-start,'qualified_score':None,
            'limits':net['limits']}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({key:value for key,value in report.items() if key!='closure'}),flush=True)
    print(json.dumps({'closure':result['status'],'ANDs':len(result['gates'])}),flush=True)

if __name__=='__main__':main()
