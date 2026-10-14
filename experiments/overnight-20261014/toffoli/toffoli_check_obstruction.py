"""Independent low-pivot rank check of the complete constructor obstruction.

No solver is required. Use dim(P intersect W)=dim(P)+dim(W)-dim(P+W), where
P spans S and every pairwise product of S basis functions. Equality with dim(S)
certifies that every affine product inside W remains in S. The previous seven-
gate prefix is a negative control and must not satisfy that equality.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path


def rank(vectors):
    rows={}
    for value in vectors:
        while value:
            low=value&-value
            if low not in rows:
                rows[low]=value;break
            value ^= rows[low]
    return len(rows)


def xor(mask,values):
    result=0
    for i,v in enumerate(values):
        if mask>>i&1:result ^= v
    return result


def interface_check(outputs):
    for raw in range(1<<14):
        acc,e,nm=raw&63,raw>>6&7,raw>>9&7
        k1,k2=raw>>12&1,raw>>13&1
        c3=int((acc&7)+e>=8);c4=(acc>>3&1)&c3
        r=nm+(acc&7);a4=r&1;a5=(r^(r>>1))&1
        a,z=acc>>4&1,acc>>5&1
        c5=(a&a4)|(a&c4)|(a4&c4)
        c6=(z&a5)|(z&c5)|(a5&c5)
        y3=(k1|k2)&((acc>>3&1)^c3)
        y4=k2&(a^c4^a4);y5=(k1&k2)&(z^c5^a5)
        k=r+8*(y3+2*y4+4*y5-c3)
        assert -7<=k<=70
        bits=[v>>raw&1 for v in outputs]
        value=0
        for b in range(54):
            field=0 if b<4 else bits[b-4] if b<=9 else bits[6+b-10] if b<=16 else bits[13] if b<=31 or b>=39 else bits[14+b-32]
            value |= field<<b
        assert value == (-(2**32+976)*k)%(1<<54)
        assert sum(bits[21+i]<<i for i in range(6))==(acc+e+(value&63))%64
        assert bits[27]==c6==(acc+e+(value&63))//64


def main():
    p=argparse.ArgumentParser();p.add_argument("netlist",type=Path);p.add_argument("receipt",type=Path)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    net=json.loads(a.netlist.read_text());receipt=json.loads(a.receipt.read_text())
    count=1<<net["input_count"]
    raw=[(1<<count)-1]+[sum((r>>i&1)<<r for r in range(count)) for i in range(net["input_count"])]
    original=list(raw)
    for g in net["gates"]:original.append(xor(g["a"],original)&xor(g["b"],original))
    targets=[xor(m,original) for m in net["outputs"]]
    interface_check(targets)
    w=raw+targets
    checks=[]
    for length in [7,8]:
        s=list(raw)
        for aa,bb in receipt["gates"][:length]:s.append(xor(aa,s)&xor(bb,s))
        products=[aa&bb for aa,bb in itertools.combinations(s,2)]
        sr,wr,pr,union=rank(s),rank(w),rank(s+products),rank(s+products+w)
        intersection=pr+wr-union
        assert sr==len(s) and rank(s+w)==wr
        checks.append({"prefix_ANDs":length,"S_rank":sr,"W_rank":wr,"quadratic_product_span_rank":pr,
                       "product_plus_W_rank":union,"intersection_rank":intersection,"closed":intersection==sr})
    assert not checks[0]["closed"] and checks[1]["closed"]
    result={"status":"verified_closed_subspace_obstruction","independent_method":"least-significant-pivot GF(2) rank plus subspace intersection dimension",
            "checks":checks,"source_interface_cases":count,"arithmetic_mismatches":0,
            "minimum_AND_bound_for_complete_value_interface":26,"original_constructor_ANDs":31,
            "source_lf_sha256":net["source_lf_sha256"],
            "netlist_sha256":hashlib.sha256(a.netlist.read_bytes()).hexdigest(),
            "receipt_sha256":hashlib.sha256(a.receipt.read_bytes()).hexdigest(),
            "limits":"Fixed14raw-input/28output value interface; changed interfaces, native phase and full-circuit cost remain separate."}
    a.output.write_bytes((json.dumps(result,indent=2)+"\n").encode());print(json.dumps(result,indent=2))


if __name__=="__main__":main()
