"""Exact parallel two-affine-product extension query over reachable S24.

An UNSAT result excludes this parallel extension only. Sequential uses of a
new product as an operand, other reachable subspaces and all full constructors
are outside the query. No formal solver proof is claimed.
"""
import argparse,hashlib,itertools,json,random,time
from pathlib import Path
import z3
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load

def projection(value,space):
    for bit,(other,_) in sorted(space.rows.items(),reverse=True):
        if value>>bit&1:value^=other
    return value

def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('description',type=Path)
    parser.add_argument('--seconds',type=int,default=600);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--query',type=Path,required=True);args=parser.parse_args()
    net=json.loads(args.netlist.read_bytes());desc=json.loads(args.description.read_bytes())
    assert desc['netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    raw,targets,_=load(net);s=Space(raw)
    for a,b in desc['seed_ANDs']:assert s.add(combination(a,s.values)&combination(b,s.values))
    assert len(s.values)==24
    d=Space(raw+targets+[raw[13]&raw[14]])
    pairs=list(itertools.combinations(range(24),2));products=[s.values[i]&s.values[j] for i,j in pairs]
    kernel=[int(value,16) for value in desc['kernel_basis_hex']]
    assert len(kernel)==53 and all(d.express(combination(mask,products)) is not None for mask in kernel)
    k=Space(kernel);equations=[1<<i for i in range(len(pairs))];coefficients=[]
    for bit,(row,_) in sorted(k.rows.items(),reverse=True):
        coefficient=equations[bit];equations[bit]=0;coefficients.append((row,coefficient));mask=row^(1<<bit)
        while mask:
            low=mask&-mask;equations[low.bit_length()-1]^=coefficient;mask^=low
    equations=[value for value in equations if value];extra=Space()
    residuals=[projection(combination(row,products),s) for row,_ in coefficients]
    for value in residuals:extra.add(value)
    extension=[0]*len(extra.values)
    for value,(_,coefficient) in zip(residuals,coefficients):
        mask=extra.express(value);assert mask is not None
        for j in range(len(extension)):
            if mask>>j&1:extension[j]^=coefficient
    assert len(extension)==1
    def wedge(a,b):
        return sum((((a>>i&1)&(b>>j&1))^((a>>j&1)&(b>>i&1)))<<t for t,(i,j) in enumerate(pairs))
    rng=random.Random(0xECDFA412)
    for _ in range(2000):
        a,b,c,e=[rng.getrandbits(24) for _ in range(4)];q=wedge(a,b)^wedge(c,e)
        value=(combination(a,s.values)&combination(b,s.values))^(combination(c,s.values)&combination(e,s.values))
        inside=all((eq&q).bit_count()%2==0 for eq in equations)
        assert inside==(d.express(value) is not None)
        if inside:assert any((eq&q).bit_count()%2 for eq in extension)==(s.express(value) is None)
    aa=[[z3.Bool(f'a{j}_{i}') for i in range(24)] for j in range(2)]
    bb=[[z3.Bool(f'b{j}_{i}') for i in range(24)] for j in range(2)]
    cross=[z3.Xor(z3.Xor(z3.And(aa[0][i],bb[0][j]),z3.And(aa[0][j],bb[0][i])),
                  z3.Xor(z3.And(aa[1][i],bb[1][j]),z3.And(aa[1][j],bb[1][i]))) for i,j in pairs]
    def linear(mask):
        value=z3.BoolVal(False)
        while mask:
            low=mask&-mask;value=z3.Xor(value,cross[low.bit_length()-1]);mask^=low
        return value
    solver=z3.Solver();solver.set(timeout=args.seconds*1000)
    for eq in equations:solver.add(z3.Not(linear(eq)))
    solver.add(z3.Or([linear(eq) for eq in extension]))
    for row in aa+bb:solver.add(z3.Not(row[0]))
    # No model or packet selection is involved: this is an abstract exact query.
    args.query.write_bytes((solver.to_smt2()+'\n').encode())
    started=time.monotonic();status=solver.check()
    report={'status':str(status),'source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':desc['netlist_sha256'],'description_sha256':hashlib.sha256(args.description.read_bytes()).hexdigest(),
            'query_sha256':hashlib.sha256(args.query.read_bytes()).hexdigest(),'query_bytes':args.query.stat().st_size,
            'domain_rows':16384,'seed_span_rank':24,'desired_span_rank':41,'parallel_products':2,
            'kernel_dimension':53,'quadratic_equations':len(equations),'extension_quotient_rank':1,
            'independent_equation_sanity_cases':2000,'timeout_seconds':args.seconds,'seconds':time.monotonic()-started,
            'solver_version':z3.get_version_string(),'solver_statistics':str(solver.statistics()),
            'formal_proof_certificate_saved':False,'qualified_score':None,
            'scope':'Two arbitrary affine products of fixed reachable S24 whose XOR lies in W40+TT outside S24.',
            'limits':'Parallel extension only; sequential nonlinear use, other reachable subspaces, all full constructors, native cleanup/phase/width and qualified score remain open.'}
    if status==z3.sat:
        model=solver.model();factors=[]
        for a,b in zip(aa,bb):
            factors.append([sum(int(z3.is_true(model.eval(v,model_completion=True)))<<i for i,v in enumerate(a)),
                            sum(int(z3.is_true(model.eval(v,model_completion=True)))<<i for i,v in enumerate(b))])
        values=[combination(a,s.values)&combination(b,s.values) for a,b in factors]
        assert d.express(values[0]^values[1]) is not None and s.express(values[0]^values[1]) is None
        report.update(factors=factors,product_truth_sha256=[hashlib.sha256(v.to_bytes(2048,'little')).hexdigest() for v in values],
                      independent_truth_rows_replayed=16384,candidate_interface_rank=len(Space(d.values+values).values),
                      prefix_ANDs=desc['seed_ANDs']+factors)
    elif status==z3.unknown:report['reason_unknown']=solver.reason_unknown()
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({k:report[k] for k in ['status','seconds','quadratic_equations','query_sha256']}),flush=True)

if __name__=='__main__':main()
