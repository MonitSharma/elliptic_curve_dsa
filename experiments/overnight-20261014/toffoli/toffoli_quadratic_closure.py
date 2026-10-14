"""Rank-bound closure using the full span of quadratic products.

For current span S inside desired final span W, span every pairwise product of
basis functions. Dependencies modulo W describe all product combinations that
land in W. If each dependency lands in S, then no product of any two affine
forms of S can extend S inside W: an exact closure obstruction. A decomposable
dependency gives a constructive new AND. Nondecomposable nonzero dependencies
are marked unresolved, never mistaken for impossibility.
"""
import argparse
import itertools
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space,combination


def factor(mask,pairs,d):
    rows=[0]*d
    for i,(a,b) in enumerate(pairs):
        if mask>>i&1:
            rows[a] ^= 1<<b;rows[b] ^= 1<<a
    hit=next(((i,j) for i,row in enumerate(rows) for j in range(i+1,d) if row>>j&1),None)
    if hit is None:return None
    i,j=hit
    a,b=rows[j],rows[i]
    if all(rows[k]==((b if a>>k&1 else 0)^(a if b>>k&1 else 0)) for k in range(d)):
        return a,b
    return None


def closure(raw,targets,extras=(),prefix=()):
    desired=Space(raw+targets+list(extras))
    s=Space(raw)
    wp=sorted(desired.rows.items(),reverse=True)
    def project(v):
        for bit,(x,_) in wp:
            if v>>bit&1:v ^= x
        return v
    gates=[];stages=[]
    for a,b in prefix:
        v=combination(a,s.values)&combination(b,s.values)
        assert desired.express(v) is not None and s.add(v)
        gates.append([a,b])
    while True:
        if all(s.express(v) is not None for v in targets):
            return {"status":"value_witness_found","AND_count":len(gates),"gates":gates,
                    "outputs":[s.express(v) for v in targets],"stages":stages}
        pairs=list(itertools.combinations(range(len(s.values)),2))
        products=[s.values[i]&s.values[j] for i,j in pairs]
        table={};kernel=[]
        for i,v in enumerate(products):
            residual=project(v);mask=1<<i
            while residual:
                bit=residual.bit_length()-1
                if bit not in table:
                    table[bit]=residual,mask;break
                x,m=table[bit];residual ^= x;mask ^= m
            if not residual:kernel.append(mask)
        new=[]
        for mask in kernel:
            value=combination(mask,products)
            if s.express(value) is None:new.append((mask,value))
        stage={"current_span_rank":len(s.values),"desired_span_rank":len(desired.values),
               "pair_products":len(pairs),"kernel_dimension":len(kernel),
               "kernel_basis_extensions":len(new)}
        stages.append(stage)
        if not new:
            return {"status":"exact_quadratic_span_obstruction","computed_ANDs":len(gates),
                    "stages":stages,"gates":gates,
                    "proof":"Every quadratic product combination landing in W lands in S. Therefore no single AND of affine forms of S extends S inside W."}
        candidate=None
        for mask,value in new:
            if (f:=factor(mask,pairs,len(s.values))) is not None:
                candidate=f;break
        # Small deterministic combination search is a witness search only.
        if candidate is None:
            selected=kernel[:32]
            for a,b in itertools.combinations(selected,2):
                mask=a^b
                if s.express(combination(mask,products)) is not None:continue
                if (f:=factor(mask,pairs,len(s.values))) is not None:
                    candidate=f;break
        if candidate is None:
            return {"status":"nondecomposable_kernel_unresolved","computed_ANDs":len(gates),
                    "stages":stages,"gates":gates,
                    "limits":"The kernel permits nonzero extensions, but this witness search has not factored them. No impossibility claim."}
        a,b=candidate
        v=combination(a,s.values)&combination(b,s.values)
        assert desired.express(v) is not None and s.express(v) is None
        assert s.add(v)
        gates.append([a,b])


def load(net):
    n=1<<net["input_count"]
    raw=[(1<<n)-1]+[sum((r>>i&1)<<r for r in range(n)) for i in range(net["input_count"])]
    values=list(raw)
    for g in net["gates"]:
        values.append(combination(g["a"],values)&combination(g["b"],values))
    return raw,[combination(m,values) for m in net["outputs"]],values


def main():
    p=argparse.ArgumentParser()
    p.add_argument("netlist",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    net=json.loads(args.netlist.read_text())
    raw,target,values=load(net)
    start=time.monotonic()
    result=closure(raw,target)
    result.update(seconds=time.monotonic()-start,input_count=net["input_count"],
                  exact_domain_size=1<<net["input_count"],old_AND_count=len(net["gates"]),
                  source_lf_sha256=net["source_lf_sha256"],
                  limits="Value interface only; this does not prove native cleanup cost or full-circuit score.")
    args.output.write_bytes((json.dumps(result,indent=2)+"\n").encode())
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
