"""Decide a remaining affine-product extension through its quadratic kernel."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import time
import z3
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load


def solve(net,receipt,prefix,timeout):
    raw,targets,_=load(net)
    s=Space(raw)
    for a,b in receipt["gates"][:prefix]:
        assert s.add(combination(a,s.values)&combination(b,s.values))
    w=Space(raw+targets)
    def projection(v,space):
        for bit,(x,_) in sorted(space.rows.items(),reverse=True):
            if v>>bit&1:v ^= x
        return v
    pairs=list(itertools.combinations(range(len(s.values)),2))
    products=[s.values[i]&s.values[j] for i,j in pairs]
    table={};kernel=[]
    for i,v in enumerate(products):
        r=projection(v,w);mask=1<<i
        while r:
            bit=r.bit_length()-1
            if bit not in table:
                table[bit]=r,mask;break
            x,m=table[bit];r ^= x;mask ^= m
        if not r:kernel.append(mask)
    k=Space(kernel)
    equations=[1<<i for i in range(len(pairs))]
    coefficients=[]
    for bit,(row,_) in sorted(k.rows.items(),reverse=True):
        c=equations[bit];equations[bit]=0
        coefficients.append((row,c))
        mask=row^(1<<bit)
        while mask:
            low=mask&-mask
            equations[low.bit_length()-1] ^= c
            mask ^= low
    equations=[v for v in equations if v]
    extra=Space()
    residuals=[projection(combination(row,products),s) for row,c in coefficients]
    for v in residuals:extra.add(v)
    extension=[0]*len(extra.values)
    for v,(row,c) in zip(residuals,coefficients):
        m=extra.express(v)
        assert m is not None
        for j in range(len(extension)):
            if m>>j&1:extension[j] ^= c
    assert extension
    def wedge(a,b):
        return sum((((a>>i&1)&(b>>j&1))^((a>>j&1)&(b>>i&1)))<<t for t,(i,j) in enumerate(pairs))
    def parity(mask,q):return (mask&q).bit_count()%2
    rng=random.Random(0xECDFA370)
    # Exact equation construction is additionally checked on unrelated forms.
    for _ in range(1000):
        a=rng.getrandbits(len(s.values));b=rng.getrandbits(len(s.values));q=wedge(a,b)
        value=combination(a,s.values)&combination(b,s.values)
        inside=all(parity(eq,q)==0 for eq in equations)
        assert inside == (w.express(value) is not None)
        if inside:assert any(parity(eq,q) for eq in extension) == (s.express(value) is None)
    solver=z3.Solver();solver.set(timeout=timeout*1000)
    aa=[z3.Bool(f"a{i}") for i in range(len(s.values))]
    bb=[z3.Bool(f"b{i}") for i in range(len(s.values))]
    cross=[z3.Xor(z3.And(aa[i],bb[j]),z3.And(aa[j],bb[i])) for i,j in pairs]
    def linear(mask):
        value=z3.BoolVal(False)
        while mask:
            low=mask&-mask
            value=z3.Xor(value,cross[low.bit_length()-1])
            mask ^= low
        return value
    for eq in equations:solver.add(z3.Not(linear(eq)))
    solver.add(z3.Or([linear(eq) for eq in extension]))
    # Removing either operand's constant changes its product by a function in S.
    solver.add(z3.Not(aa[0]),z3.Not(bb[0]))
    QUERY_PATH.write_bytes((solver.to_smt2()+'\n').encode())
    start=time.monotonic();status=solver.check()
    result={"status":str(status),"prefix_ANDs":prefix,"current_span_rank":len(s.values),
            "desired_span_rank":len(w.values),"pair_products":len(pairs),
            "kernel_dimension":len(kernel),"quadratic_equations":len(equations),
            "extension_quotient_rank":len(extension),"equation_sanity_checks":1000,
            "solver":z3.get_version_string(),"timeout_seconds":timeout,"seconds":time.monotonic()-start}
    if status==z3.sat:
        model=solver.model()
        a=sum(int(z3.is_true(model.eval(v,model_completion=True)))<<i for i,v in enumerate(aa))
        b=sum(int(z3.is_true(model.eval(v,model_completion=True)))<<i for i,v in enumerate(bb))
        value=combination(a,s.values)&combination(b,s.values)
        assert w.express(value) is not None and s.express(value) is None
        result.update(a=a,b=b,all_16384_truth_rows_verified=True)
    elif status==z3.unsat:
        result["proof_scope"]="No AND of arbitrary affine forms of S can extend S inside W. A circuit attaining W-minus-input rank must keep every AND in W, so it cannot reach W from the contained raw-input span."
    else:result["reason"]=solver.reason_unknown()
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("netlist",type=Path);p.add_argument("closure",type=Path)
    p.add_argument("--prefix",type=int,default=7);p.add_argument("--timeout",type=int,default=120)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    net=json.loads(a.netlist.read_text());receipt=json.loads(a.closure.read_text())
    report=solve(net,receipt,a.prefix,a.timeout)
    report.update(source_lf_sha256=net["source_lf_sha256"],netlist_sha256=hashlib.sha256(a.netlist.read_bytes()).hexdigest(),
                  closure_sha256=hashlib.sha256(a.closure.read_bytes()).hexdigest(),
                  limits="Value-interface result; no phase/cleanup or full-circuit cost established.")
    a.output.write_bytes((json.dumps(report,indent=2)+"\n").encode())
    print(json.dumps(report,indent=2),flush=True)


if __name__=="__main__":main()
