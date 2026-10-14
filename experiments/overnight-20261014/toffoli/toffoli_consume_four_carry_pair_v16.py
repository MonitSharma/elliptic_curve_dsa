"""Exact new quotient/low-carry joint obligation and auxiliary proposal."""
import argparse,hashlib,json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_consume_four_contract_v13 import load_fast

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('analysis',type=Path)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--factor-netlist',type=Path,required=True)
    args=p.parse_args();net=json.loads(args.netlist.read_bytes());analysis=json.loads(args.analysis.read_bytes())
    assert analysis['netlist_sha256']==hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    raw,targets,old=load_fast(net);w=Space(raw+targets);s=Space(raw)
    prefix=analysis['closure']['gates'];assert len(prefix)==4
    for a,b in prefix:assert s.add(combination(a,s.values)&combination(b,s.values))
    c4=old[22];c4mask=s.express(c4);assert c4mask is not None
    u,v,a=raw[1],raw[10],raw[5]
    old_c5=old[29]^c4;old_r1=old[24]
    f=old_c5^old_r1
    independent_f=targets[20]^raw[6]^raw[2]^raw[11]^raw[1]^raw[10]
    assert f==independent_f and w.express(f) is not None and s.express(f) is None
    pvalue=(u^a^c4)&(v^a^c4);qvalue=a&c4
    assert f==pvalue^qvalue^a^c4
    extended=Space(raw+targets+[qvalue]);assert len(extended.values)==44
    factors=[[1<<5,c4mask],[(1<<1)^(1<<5)^c4mask,(1<<10)^(1<<5)^c4mask]]
    for aa,bb in factors:assert s.add(combination(aa,s.values)&combination(bb,s.values))
    assert s.values[-2:]==[qvalue,pvalue]
    current=dict(net);current['gates']=net['gates']+[{'name':'joint_acc4_C4','a':1<<5,'b':1<<22}]
    current['outputs']=net['outputs']+[1<<len(old)]
    args.factor_netlist.write_bytes((json.dumps(current,indent=2)+'\n').encode())
    report={'status':'exact_joint_C5_R1_six_AND_prefix_verified','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
            'factor_netlist_sha256':hashlib.sha256(args.factor_netlist.read_bytes()).hexdigest(),
            'domain_rows':262144,'identity':'C5+R1=(acc0+acc4+C4)*(Nm0+acc4+C4)+acc4*C4+acc4+C4',
            'target_coordinate_mask':w.express(f),'joint_function_truth_sha256':hashlib.sha256(f.to_bytes(32768,'little')).hexdigest(),
            'auxiliary_truth_sha256':hashlib.sha256(qvalue.to_bytes(32768,'little')).hexdigest(),
            'auxiliary_inside_original_source_span':Space(old).express(qvalue) is not None,
            'desired_span_rank':44,'value_AND_budget':25,'prefix_ANDs':prefix+factors,'prefix_span_rank':len(s.values),
            'independent_truth_rows_replayed':262144,'qualified_score':None,
            'limits':'Exact partial value identity and changed output obligation only. No complete constructor, cleanup/phase, physical width or full score.'}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({key:report[key] for key in ['status','desired_span_rank','value_AND_budget','auxiliary_inside_original_source_span']}))

if __name__=='__main__':main()
