"""Exact quadratic/cubic equations for one-auxiliary escape from closed S23."""
import argparse,hashlib,itertools,json,random
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_producer_range_v21 import load_admitted as load

def projection(value,space):
    for bit,(other,_) in sorted(space.rows.items(),reverse=True):
        if value>>bit&1:value^=other
    return value

def polynomial(a,b):
    result=set()
    for i in range(1,23):
        if not a>>i&1:continue
        for j in range(1,23):
            if not b>>j&1:continue
            mask=(1<<i)|(1<<j)
            if mask in result:result.remove(mask)
            else:result.add(mask)
    return result

def coefficients(a,b,u,v,epsilon,monomial_index):
    first=polynomial(u,v);result=polynomial(a,b)
    for mask in first:
        for i in range(1,23):
            if b>>i&1:
                new=mask|(1<<i)
                if new in result:result.remove(new)
                else:result.add(new)
    if epsilon:result^=first
    return sum(1<<monomial_index[mask] for mask in result if mask.bit_count()>=2)

def prepare(net,prefix):
    raw,targets,_=load(net);s=Space(raw);w=Space(raw+targets)
    for a,b in prefix:assert s.add(combination(a,s.values)&combination(b,s.values))
    assert len(s.values)==23 and len(w.values)==40
    monomials=list(itertools.combinations(range(1,23),2))+list(itertools.combinations(range(1,23),3))
    index={sum(1<<i for i in item):j for j,item in enumerate(monomials)}
    products=[]
    for item in monomials:
        value=s.values[item[0]]
        for i in item[1:]:value&=s.values[i]
        products.append(value)
    table={};kernel=[]
    for i,value in enumerate(products):
        residual=projection(value,w);mask=1<<i
        while residual:
            bit=residual.bit_length()-1
            if bit not in table:table[bit]=residual,mask;break
            other,other_mask=table[bit];residual^=other;mask^=other_mask
        if not residual:kernel.append(mask)
    k=Space(kernel);equations=[1<<i for i in range(len(monomials))];coordinates=[]
    for bit,(row,_) in sorted(k.rows.items(),reverse=True):
        coefficient=equations[bit];equations[bit]=0;coordinates.append((row,coefficient));mask=row^(1<<bit)
        while mask:
            low=mask&-mask;equations[low.bit_length()-1]^=coefficient;mask^=low
    equations=[mask for mask in equations if mask];extra=Space()
    residuals=[projection(combination(row,products),s) for row,_ in coordinates]
    for value in residuals:extra.add(value)
    extension=[0]*len(extra.values)
    for value,(_,coefficient) in zip(residuals,coordinates):
        mask=extra.express(value);assert mask is not None
        for i in range(len(extension)):
            if mask>>i&1:extension[i]^=coefficient
    assert len(extension)==1 and len(equations)==1238
    # Direct truth-vector tests independently check the square-free coefficient
    # construction, including repeated-index Boolean reductions x_i^2=x_i.
    rng=random.Random(0xECDFA419)
    for _ in range(2000):
        a,b,u,v=[rng.getrandbits(22)<<1 for _ in range(4)];epsilon=rng.randrange(2)
        coeff=coefficients(a,b,u,v,epsilon,index)
        pvalue=combination(u,s.values)&combination(v,s.values)
        qvalue=(combination(a,s.values)^pvalue)&combination(b,s.values)
        zvalue=qvalue^(pvalue if epsilon else 0)
        # The omitted linear terms are in S23, so both projections agree.
        assert s.express(zvalue^combination(coeff,products)) is not None
        inside=all((eq&coeff).bit_count()%2==0 for eq in equations)
        assert inside==(w.express(zvalue) is not None)
        if inside:assert any((eq&coeff).bit_count()%2 for eq in extension)==(s.express(zvalue) is None)
    p2=Space(s.values+products[:231]);p3=Space(s.values+products)
    return {'status':'exact_producer_domain_escape_equations_prepared','source_lf_sha256':net['source_lf_sha256'],
            'domain_rows':11776,'truth_vector_layout_rows':16384,'seed_ANDs':prefix,'seed_span_rank':23,'target_span_rank':40,
            'quadratic_span_rank':len(p2.values),'quadratic_union_target_rank':len(Space(p2.values+w.values).values),
            'cubic_span_rank':len(p3.values),'cubic_union_target_rank':len(Space(p3.values+w.values).values),
            'seed_basis_truth_sha256':hashlib.sha256(b''.join(value.to_bytes(2048,'little') for value in s.values)).hexdigest(),
            'monomial_truth_sha256':hashlib.sha256(b''.join(value.to_bytes(2048,'little') for value in products)).hexdigest(),
            'monomials':monomials,'kernel_dimension':len(kernel),'membership_equations_hex':[hex(mask) for mask in equations],
            'extension_equations_hex':[hex(mask) for mask in extension],'equation_sanity_cases':2000,
            'query':'p=u*v; q=(a+p)*b; q+epsilon*p lies in W40 outside S23; a,b,u,v arbitrary affine S23 forms.',
            'constant_normalization':'Operand constants may be removed: adjust second operand a by an S23 form when changing p, and absorb q-operand constants into known S23 plus epsilon*p. Both-p second operands reduce to one-p form modulo S23+p.',
            'limits':'Reduced source-arithmetic domain only; solver pending. No fullproducer gate-level or phase proof, and no global14input conclusion.',
            'qualified_score':None}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('netlist',type=Path);parser.add_argument('closed_receipt',type=Path)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    net=json.loads(args.netlist.read_bytes());closed=json.loads(args.closed_receipt.read_bytes())
    result=prepare(net,closed['gates']);result.update(netlist_sha256=hashlib.sha256(args.netlist.read_bytes()).hexdigest(),closed_receipt_sha256=hashlib.sha256(args.closed_receipt.read_bytes()).hexdigest())
    args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({key:result[key] for key in ['status','kernel_dimension','cubic_span_rank','cubic_union_target_rank','equation_sanity_cases']}))

if __name__=='__main__':main()
