"""Derive the next exact obstruction relation after the carry prefix plus TT."""
import argparse,hashlib,itertools,json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_consume_four_contract_v13 import load_fast
from toffoli_symplectic_interface_v10 import matrix,matrix_rank,decompose

def projection(value,space):
    for bit,(row,_) in sorted(space.rows.items(),reverse=True):
        if value>>bit&1:value^=row
    return value

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('previous',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--factor-netlist',type=Path,required=True)
    args=p.parse_args();net=json.loads(args.netlist.read_bytes());prev=json.loads(args.previous.read_bytes())
    assert prev['factor_netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    net['outputs']=net['outputs']+[1<<23] # Exact old source TT=k1*k2.
    raw,targets,old=load_fast(net);desired=Space(raw+targets);assert len(desired.values)==47
    prefix=prev['prefix_ANDs']+[[1<<13,1<<14]];s=Space(raw)
    for a,b in prefix:assert s.add(combination(a,s.values)&combination(b,s.values))
    assert len(s.values)==29
    pairs=list(itertools.combinations(range(29),2));products=[s.values[i]&s.values[j] for i,j in pairs]
    table={};kernel=[]
    for i,value in enumerate(products):
        residual=projection(value,desired);mask=1<<i
        while residual:
            bit=residual.bit_length()-1
            if bit not in table:table[bit]=residual,mask;break
            other,other_mask=table[bit];residual^=other;mask^=other_mask
        if not residual:kernel.append(mask)
    known=[mask for mask in kernel if s.express(combination(mask,products)) is not None]
    ext=[mask for mask in kernel if s.express(combination(mask,products)) is None]
    assert len(ext)==1
    current=ext[0];initial_rank=matrix_rank(matrix(current,pairs,29));toggles=[]
    while True:
        best=min((matrix_rank(matrix(current^mask,pairs,29)),i) for i,mask in enumerate(known))
        if best[0]<matrix_rank(matrix(current,pairs,29)):
            toggles.append([best[1]]);current^=known[best[1]];continue
        bestpair=min((matrix_rank(matrix(current^known[i]^known[j],pairs,29)),i,j)
                     for i,j in itertools.combinations(range(len(known)),2))
        if bestpair[0]>=matrix_rank(matrix(current,pairs,29)):break
        toggles.append([bestpair[1],bestpair[2]]);current^=known[bestpair[1]]^known[bestpair[2]]
    rows=matrix(current,pairs,29);factors=decompose(rows)
    values=[combination(a,s.values)&combination(b,s.values) for a,b in factors]
    total=combination((1<<len(values))-1,values)
    assert desired.express(total) is not None and s.express(total) is None
    correction=s.express(total^combination(current,products));assert correction is not None
    expanded=Space(desired.values);chosen=[]
    for i,value in enumerate(values):
        if expanded.add(value):chosen.append(i)
    addedrank=len(expanded.values)-len(desired.values)
    program=prefix+factors;program_values=list(raw)
    for a,b in program:program_values.append(combination(a,program_values)&combination(b,program_values))
    assert program_values[-len(factors):]==values
    def sm(mask):return sum(1<<(i if i<19 else len(old)+i-19) for i in range(mask.bit_length()) if mask>>i&1)
    current_net=dict(net);current_net['gates']=net['gates']+[{'name':f'next_relation_prefix_{i}','a':sm(a),'b':sm(b)} for i,(a,b) in enumerate(program)]
    current_net['outputs']=net['outputs']+[1<<(len(old)+len(prefix)+i) for i in chosen]
    args.factor_netlist.write_bytes((json.dumps(current_net,indent=2)+'\n').encode())
    report={'status':'exact_next_relation_symplectic_prefix_verified','source_lf_sha256':net['source_lf_sha256'],
            'input_netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'factor_netlist_sha256':hashlib.sha256(args.factor_netlist.read_bytes()).hexdigest(),
            'domain_rows':262144,'seed_span_rank':29,'base_interface_rank':47,'pair_products':len(pairs),
            'kernel_basis_hex':[hex(mask) for mask in kernel],'known_kernel_basis_count':len(known),'extension_kernel_basis_count':len(ext),
            'extension_relation_hex':hex(ext[0]),'selected_relation_hex':hex(current),'greedy_known_relation_toggles':toggles,
            'initial_alternating_rank':initial_rank,'selected_alternating_rank':matrix_rank(rows),'selected_matrix_rows':rows,
            'affine_product_factors':factors,'linear_diagonal_correction_mask':correction,
            'product_truth_sha256':[hashlib.sha256(value.to_bytes(32768,'little')).hexdigest() for value in values],
            'combined_product_truth_sha256':hashlib.sha256(total.to_bytes(32768,'little')).hexdigest(),
            'products_inside_previous_source_span':[Space(old).express(value) is not None for value in values],
            'independent_extra_product_indices':chosen,'new_outside_rank':addedrank,
            'desired_span_rank':len(expanded.values),'value_AND_budget':len(expanded.values)-19,
            'extra_output_count':len(current_net['outputs'])-26,'prefix_ANDs':program,'prefix_AND_count':len(program),
            'independent_truth_rows_replayed':262144,'qualified_score':None,
            'limits':'One selected next target relation and partial prefix. Greedy matrix-rank reduction is not minimum. No complete constructor, phase/cleanup/native/width or full executed cost.'}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({key:report[key] for key in ['status','initial_alternating_rank','selected_alternating_rank','desired_span_rank','value_AND_budget','prefix_AND_count','products_inside_previous_source_span']}))

if __name__=='__main__':main()
