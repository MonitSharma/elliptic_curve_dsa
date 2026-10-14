"""Independent exact ANF audit of the exported sequential-escape SMT equations.

Expands parsed SMT Boolean ASTs into canonical square-free polynomials in all
89 solver coefficient variables. Independently constructs coefficient ANFs by
polynomial multiplication, not by the solver's hand-written coefficient list.
Equality therefore checks every coefficient assignment, not random samples.
"""
import argparse,hashlib,itertools,json,time
from pathlib import Path
import z3
from toffoli_guided_joint import combination
from toffoli_producer_range_v21 import load_admitted as load

def mul(left,right):
    out=set()
    for a in left:
        for b in right:
            c=a|b
            if c in out:out.remove(c)
            else:out.add(c)
    return out

def product(left,right):
    out={}
    for a,ap in left.items():
        for b,bp in right.items():
            c=a|b;out.setdefault(c,set()).symmetric_difference_update(mul(ap,bp))
    return {key:value for key,value in out.items() if value}

def rank_low(values):
    rows={}
    for value in values:
        while value:
            bit=(value&-value).bit_length()-1
            if bit not in rows:rows[bit]=value;break
            value^=rows[bit]
    return len(rows)

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('description',type=Path)
    p.add_argument('query',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args();start=time.monotonic()
    net=json.loads(args.netlist.read_bytes());desc=json.loads(args.description.read_bytes())
    assert desc['netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    names=[f'{name}{i}' for name in ['a','b','u','v'] for i in range(1,23)]+['epsilon']
    var={name:1<<i for i,name in enumerate(names)}
    forms={name:{1<<i:{var[f'{name}{i}']} for i in range(1,23)} for name in ['a','b','u','v']}
    first=product(forms['u'],forms['v'])
    full=product(forms['a'],forms['b'])
    for mask,poly in product(first,forms['b']).items():full.setdefault(mask,set()).symmetric_difference_update(poly)
    for mask,poly in first.items():full.setdefault(mask,set()).symmetric_difference_update(mul(poly,{var['epsilon']}))
    monomial_masks=[sum(1<<i for i in item) for item in desc['monomials']]
    coeff=[full.get(mask,set()) for mask in monomial_masks]
    pcoeff=[first.get(mask,set()) for mask in monomial_masks]
    equations=[int(value,16) for value in desc['membership_equations_hex']]
    extension=[int(value,16) for value in desc['extension_equations_hex']]
    def linear(mask,values):
        out=set()
        while mask:
            low=mask&-mask;out.symmetric_difference_update(values[low.bit_length()-1]);mask^=low
        return out
    expected=[linear(eq,coeff)^{0} for eq in equations]+[linear(extension[0],coeff)]
    expected_outside=[linear(eq,pcoeff) for eq in equations]
    parsed=list(z3.parse_smt2_file(str(args.query)));assert len(parsed)==len(expected)+1
    cache={}
    def anf(node):
        identity=node.get_id()
        if identity in cache:return cache[identity]
        kind=node.decl().kind()
        if z3.is_true(node):result={0}
        elif z3.is_false(node):result=set()
        elif kind==z3.Z3_OP_UNINTERPRETED:
            assert node.num_args()==0 and str(node) in var;result={var[str(node)]}
        elif kind==z3.Z3_OP_NOT:result=anf(node.arg(0))^{0}
        elif kind==z3.Z3_OP_XOR:
            result=set()
            for child in node.children():result.symmetric_difference_update(anf(child))
        elif kind==z3.Z3_OP_AND:
            result={0}
            for child in node.children():result=mul(result,anf(child))
        elif kind==z3.Z3_OP_OR and node.num_args()==1:result=anf(node.arg(0))
        else:raise AssertionError(('unsupported Boolean AST',str(node.decl())))
        cache[identity]=result;return result
    actual=[anf(node) for node in parsed[:-1]]
    assert actual==expected
    outside=parsed[-1];assert outside.decl().kind()==z3.Z3_OP_OR and outside.num_args()==len(equations)
    assert [anf(child) for child in outside.children()]==expected_outside
    def digest(polys):
        h=hashlib.sha256()
        for poly in polys:
            h.update(len(poly).to_bytes(4,'little'))
            for monomial in sorted(poly):h.update(monomial.to_bytes(16,'little'))
        return h.hexdigest()
    # Remove one real cubic coefficient term from a parsed membership AST.
    fault_detected=False
    for root,want in zip(parsed[:-1],expected):
        cubic=next((monomial for monomial in want if monomial.bit_count()==3),None)
        if cubic is None:continue
        stack=[root];seen=set()
        while stack:
            node=stack.pop()
            if node.get_id() in seen:continue
            seen.add(node.get_id())
            if node.decl().kind()==z3.Z3_OP_AND and anf(node)=={cubic}:
                faulty=z3.substitute(root,(node,z3.BoolVal(False)))
                assert anf(faulty)!=want;fault_detected=True;break
            stack.extend(node.children())
        if fault_detected:break
    assert fault_detected
    # Independent low-pivot truth rank implementation, separate from search.
    raw,targets,_=load(net);s=list(raw)
    for a,b in desc['seed_ANDs']:s.append(combination(a,s)&combination(b,s))
    pair_values=[s[i]&s[j] for i,j in itertools.combinations(range(1,23),2)]
    triple_values=[s[i]&s[j]&s[k] for i,j,k in itertools.combinations(range(1,23),3)]
    w=raw+targets;values2=s+pair_values;values3=values2+triple_values
    ranks={'raw':rank_low(raw),'S':rank_low(s),'W':rank_low(w),'P2':rank_low(values2),
           'P2_union_W':rank_low(values2+w),'P3':rank_low(values3),'P3_union_W':rank_low(values3+w)}
    assert ranks=={'raw':15,'S':23,'W':40,'P2':228,'P2_union_W':245,'P3':1262,'P3_union_W':1278}
    report={'status':'parsed_SMT_exact_ANF_and_independent_truth_ranks_verified','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':desc['netlist_sha256'],'description_sha256':hashlib.sha256(args.description.read_bytes()).hexdigest(),
            'query_sha256':hashlib.sha256(args.query.read_bytes()).hexdigest(),'coefficient_variables':89,
            'scope':'Exact symbolic ANF equality for every assignment to89 solver coefficient variables; all11776 admitted primitive truth rows in16384-position layout for independent ranks.',
            'monomial_coefficient_ANF_sha256':digest(coeff),'membership_extension_ANF_sha256':digest(actual),
            'outside_p_ANF_sha256':digest(expected_outside),'membership_equations_checked':len(equations),
            'extension_equations_checked':1,'implied_outside_p_equations_checked':len(equations),
            'cubic_term_removal_fault_detected':True,'independent_low_pivot_ranks':ranks,
            'parsed_AST_nodes_audited':len(cache),'seconds':time.monotonic()-start,'qualified_score':None,
            'limits':'Exact encoding/rank audit, not an independent SAT/UNSAT solver proof certificate; no native phase/cleanup/full circuit score.'}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({'status':report['status'],'seconds':report['seconds'],'AST_nodes':len(cache)}),flush=True)

if __name__=='__main__':main()
