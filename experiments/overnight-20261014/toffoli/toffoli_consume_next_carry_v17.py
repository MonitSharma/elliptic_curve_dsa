"""Construct an explicit second fused carry obligation from the changed outputs."""
import argparse,hashlib,itertools,json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_consume_four_contract_v13 import load_fast

def projection(v,s):
    for bit,(x,_) in sorted(s.rows.items(),reverse=True):
        if v>>bit&1:v^=x
    return v

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('previous',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--factor-netlist',type=Path,required=True)
    args=p.parse_args();net=json.loads(args.netlist.read_bytes());prev=json.loads(args.previous.read_bytes())
    assert prev['netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    raw,targets,old=load_fast(net);s=Space(raw)
    for a,b in prev['prefix_ANDs']:assert s.add(combination(a,s.values)&combination(b,s.values))
    assert len(s.values)==25
    f=targets[20]^raw[6]^raw[2]^raw[11]^raw[1]^raw[10]
    q=s.values[23]
    second=targets[21]^raw[15]^raw[3]^raw[12]^raw[2]^raw[11]
    forms=[s.express(v) for v in [raw[1],raw[10],raw[2],raw[11],raw[6],f]]
    assert all(v is not None for v in forms)
    qmask=s.express(q);pairs=list(itertools.combinations(range(len(s.values)),2));pair_index={pair:i for i,pair in enumerate(pairs)}
    coefficients=0;linear=qmask
    def add_product(a,b):
        nonlocal coefficients,linear
        for i in range(25):
            if not a>>i&1:continue
            for j in range(25):
                if not b>>j&1:continue
                if i==j:linear^=1<<i
                else:coefficients^=1<<pair_index[tuple(sorted([i,j]))]
    for a,b in itertools.combinations(forms,2):add_product(a,b)
    add_product(qmask,forms[-1])
    allproducts=[s.values[i]&s.values[j] for i,j in pairs]
    assert second==combination(coefficients,allproducts)^combination(linear,s.values)
    matrix=[0]*25
    for index,(i,j) in enumerate(pairs):
        if coefficients>>index&1:matrix[i]^=1<<j;matrix[j]^=1<<i
    rank=len(Space(matrix).values);assert rank==6
    rows=list(matrix);factors=[]
    while any(rows):
        i,j=next((i,j) for i,row in enumerate(rows) for j in range(i+1,25) if row>>j&1)
        a,b=rows[j],rows[i];factors.append([a,b])
        for k in range(25):rows[k]^=(b if a>>k&1 else 0)^(a if b>>k&1 else 0)
    assert len(factors)==3
    values=[combination(a,s.values)&combination(b,s.values) for a,b in factors]
    correction=s.express(second^values[0]^values[1]^values[2]);assert correction is not None
    desired=Space(raw+targets+[q]);assert desired.express(second) is not None and s.express(second) is None
    expanded=Space(desired.values);chosen=[]
    for i,value in enumerate(values):
        if expanded.add(value):chosen.append(i)
    assert len(chosen)==2 and len(expanded.values)==46
    for value in values:assert s.add(value)
    # Formal source definition for each transformed product reuses the old
    # source followed by the6 previous ANDs, then the3 new ones.
    prefix=prev['prefix_ANDs']+factors
    def source_mask(mask):return sum(1<<(i if i<19 else len(old)+i-19) for i in range(mask.bit_length()) if mask>>i&1)
    current=dict(net);current['gates']=net['gates']+[{'name':f'carry_fusion_prefix_{i}','a':source_mask(a),'b':source_mask(b)} for i,(a,b) in enumerate(prefix)]
    current['outputs']=net['outputs']+[1<<(len(old)+4)]+[1<<(len(old)+6+i) for i in chosen]
    args.factor_netlist.write_bytes((json.dumps(current,indent=2)+'\n').encode())
    report={'status':'exact_second_carry_three_product_prefix_verified','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':prev['netlist_sha256'],'factor_netlist_sha256':hashlib.sha256(args.factor_netlist.read_bytes()).hexdigest(),
            'previous_description_sha256':hashlib.sha256(args.previous.read_bytes()).hexdigest(),'domain_rows':262144,
            'identity':'F2=e2(acc0,Nm0,acc1,Nm1,acc5,F1)+q*F1+q; F1=C5+R1, q=acc4*C4',
            'coefficient_mask_hex':hex(coefficients),'linear_mask':linear,'alternating_matrix_rows':matrix,'alternating_rank':rank,
            'factors':factors,'linear_correction_mask':correction,'desired_span_rank':46,'value_AND_budget':27,
            'independent_extra_product_indices':chosen,'prefix_ANDs':prefix,'prefix_AND_count':len(prefix),'prefix_span_rank':len(s.values),
            'combined_function_truth_sha256':hashlib.sha256(second.to_bytes(32768,'little')).hexdigest(),
            'product_truth_sha256':[hashlib.sha256(v.to_bytes(32768,'little')).hexdigest() for v in values],
            'products_inside_original_span':[Space(old).express(v) is not None for v in values],
            'independent_truth_rows_replayed':262144,'qualified_score':None,
            'limits':'Exact second joint carry identity and partial9AND prefix only. This selected decomposition is not a minimum-rank proof. No complete constructor/cleanup/native/width/full cost claim.'}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({key:report[key] for key in ['status','alternating_rank','desired_span_rank','value_AND_budget','prefix_AND_count','products_inside_original_span']}))

if __name__=='__main__':main()
