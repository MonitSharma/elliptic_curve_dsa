"""Solve the exact one-auxiliary sequential escape query, preserving SMT input."""
import argparse,hashlib,itertools,json,time
from pathlib import Path
import z3
from toffoli_guided_joint import Space,combination
from toffoli_producer_range_v21 import load_admitted as load
from toffoli_sequential_escape_prepare_v19 import coefficients

def xor(values):
    out=z3.BoolVal(False)
    for value in values:out=z3.Xor(out,value)
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('description',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--query',type=Path,required=True)
    p.add_argument('--seconds',type=int,default=600);args=p.parse_args()
    net=json.loads(args.netlist.read_bytes());desc=json.loads(args.description.read_bytes())
    assert desc['netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    raw,targets,_=load(net);s=Space(raw);w=Space(raw+targets)
    for a,b in desc['seed_ANDs']:assert s.add(combination(a,s.values)&combination(b,s.values))
    assert hashlib.sha256(b''.join(v.to_bytes(2048,'little') for v in s.values)).hexdigest()==desc['seed_basis_truth_sha256']
    forms={name:[z3.BoolVal(False)]+[z3.Bool(f'{name}{i}') for i in range(1,23)] for name in ['a','b','u','v']}
    a,b,u,v=[forms[name] for name in ['a','b','u','v']];epsilon=z3.Bool('epsilon')
    coeff=[];pcoeff=[]
    for item in desc['monomials']:
        if len(item)==2:
            i,j=item
            pterm=xor([z3.And(u[i],v[j]),z3.And(u[j],v[i])]);pcoeff.append(pterm)
            coeff.append(xor([z3.And(a[i],b[j]),z3.And(a[j],b[i]),
                              z3.And(u[i],v[i],b[j]),z3.And(u[i],v[j],b[i]),z3.And(u[j],v[i],b[i]),
                              z3.And(u[i],v[j],b[j]),z3.And(u[j],v[i],b[j]),z3.And(u[j],v[j],b[i]),
                              z3.And(epsilon,pterm)]))
        else:
            coeff.append(xor([z3.And(u[i],v[j],b[k]) for i,j,k in itertools.permutations(item)]))
            pcoeff.append(z3.BoolVal(False))
    equations=[int(mask,16) for mask in desc['membership_equations_hex']]
    extension=[int(mask,16) for mask in desc['extension_equations_hex']]
    def linear(mask,values):
        terms=[]
        while mask:
            low=mask&-mask;terms.append(values[low.bit_length()-1]);mask^=low
        return xor(terms)
    solver=z3.Solver();solver.set(timeout=args.seconds*1000)
    for eq in equations:solver.add(z3.Not(linear(eq,coeff)))
    solver.add(z3.Or([linear(eq,coeff) for eq in extension]))
    # Implied by the exact P2(S23) intersection result, useful as a solver guide.
    solver.add(z3.Or([linear(eq,pcoeff) for eq in equations]))
    args.query.write_bytes((solver.to_smt2()+'\n').encode());started=time.monotonic();status=solver.check()
    report={'status':str(status),'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':desc['netlist_sha256'],
            'description_sha256':hashlib.sha256(args.description.read_bytes()).hexdigest(),
            'query_sha256':hashlib.sha256(args.query.read_bytes()).hexdigest(),'query_bytes':args.query.stat().st_size,
            'domain_rows':11776,'truth_vector_layout_rows':16384,'seed_span_rank':23,'target_span_rank':40,'monomial_count':1771,
            'quadratic_cubic_membership_equations':len(equations),'extension_quotient_rank':len(extension),
            'seconds':time.monotonic()-started,'timeout_seconds':args.seconds,'solver_version':z3.get_version_string(),
            'solver_statistics':str(solver.statistics()),'formal_proof_certificate_saved':False,'qualified_score':None,
            'scope':'p=u*v, q=(a+p)*b, q+epsilon*p inW40 outsideS23; all four affine S23 operand forms.',
            'limits':'Trusted solver status without formal proof certificate. Reduced source-arithmetic domain only; exact encoding audit and fullproducer gate/phase admission remain separate.'}
    if status==z3.sat:
        model=solver.model();masks={name:sum(int(z3.is_true(model.eval(value,model_completion=True)))<<i for i,value in enumerate(values)) for name,values in forms.items()}
        eps=int(z3.is_true(model.eval(epsilon,model_completion=True)))
        pv=combination(masks['u'],s.values)&combination(masks['v'],s.values)
        qv=(combination(masks['a'],s.values)^pv)&combination(masks['b'],s.values)
        zv=qv^(pv if eps else 0)
        assert w.express(pv) is None and w.express(zv) is not None and s.express(zv) is None
        numeric=coefficients(masks['a'],masks['b'],masks['u'],masks['v'],eps,{sum(1<<i for i in item):j for j,item in enumerate(desc['monomials'])})
        assert all((eq&numeric).bit_count()%2==0 for eq in equations) and any((eq&numeric).bit_count()%2 for eq in extension)
        prefix=desc['seed_ANDs']+[[masks['u'],masks['v']],[masks['a']^(1<<23),masks['b']]]
        replay=list(raw)
        for aa,bb in prefix:replay.append(combination(aa,replay)&combination(bb,replay))
        assert replay[-2:]==[pv,qv]
        report.update(operand_masks=masks,epsilon=eps,prefix_ANDs=prefix,p_truth_sha256=hashlib.sha256(pv.to_bytes(2048,'little')).hexdigest(),
                      q_truth_sha256=hashlib.sha256(qv.to_bytes(2048,'little')).hexdigest(),
                      extension_truth_sha256=hashlib.sha256(zv.to_bytes(2048,'little')).hexdigest(),independent_admitted_rows_replayed=11776,
                      candidate_interface_rank=41,value_AND_budget=26)
    elif status==z3.unknown:report['reason_unknown']=solver.reason_unknown()
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({key:report[key] for key in ['status','seconds','query_sha256','query_bytes']}),flush=True)

if __name__=='__main__':main()
