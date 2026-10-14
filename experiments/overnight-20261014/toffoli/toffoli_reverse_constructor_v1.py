"""Source-derived reverse quotient prefix fused with the fixed12 addend table.

The14-input value interface is W0..5,E0..2,Nm0..2,k1,k2. The actual producer
also supplies linked accumulator/borrow forms. Their admission and native
cleanup are separate obligations. This script never changes candidate source.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import closure,load

BASELINE_SHA='879b85060f6a5cfa412561d64860f1cab697f7a334f180f5be9102070d5a23b9'


def model(source):
    one=1;w=[1<<(i+1) for i in range(6)];e=[1<<(i+7) for i in range(3)]
    nm=[1<<(i+10) for i in range(3)];k1,k2=1<<13,1<<14;gates=[]
    def AND(name,a,b):
        q=1<<(15+len(gates));gates.append({'name':name,'a':a,'b':b});return q
    def MAJ(name,a,b,c):return AND(name,a^c,b^c)^c
    sg=[e[i]^nm[i]^one^w[i] for i in range(3)]
    kp1=MAJ('kp1',e[0],nm[0]^one,w[0])
    n=[sg[0]^one,sg[1]^kp1^sg[0]]
    tt=AND('tt',k1,k2)
    y3=AND('y3',k1^k2^tt,w[3]);y4=AND('y4',k2,w[4]);y5=AND('y5',tt,w[5])
    kp2=MAJ('kp2',e[1],nm[1]^one,w[1]);kp3=MAJ('kp3',e[2],nm[2]^one,w[2])
    r=MAJ('r2',sg[1],kp1,sg[0]);n.append(sg[2]^kp2^r)
    r=MAJ('r3',sg[2],kp2,r);n.append(y3^one^kp3^r)
    r=MAJ('r4',y3^one,kp3,r);n.append(y4^one^y3^r)
    r=MAJ('r5',y4^one,y3,r);n.append(y5^one^y4^r)
    r=MAJ('r6',y5^one,y4,r);n.append(y5^r^one)
    n.append(AND('n7',y5^one,r^one))
    assert len(gates)==13
    table=re.search(r'const Y16_REV_GATES:.*?=\s*\[(.*?)\];',source,re.S).group(1)
    pairs=[tuple(int(x,16) for x in pair) for pair in re.findall(r'\(\s*(0x[0-9a-f]+),\s*(0x[0-9a-f]+)\s*\)',table)]
    outs=[int(x,16) for x in re.findall(r'0x[0-9a-f]+',re.search(r'const Y16_REV_OUT:.*?=\s*\[(.*?)\];',source,re.S).group(1))]
    assert len(pairs)==12 and len(outs)==21
    values=[one]+n
    for j,(a,b) in enumerate(pairs):values.append(AND(f'addend{j}',combination(a,values),combination(b,values)))
    return {'baseline_revision':'c5bb1ec876db859a3f9f8a9052c140a145df834e',
            'source':'src/point_add/y15_onefold.rs fold_rev_v2 quotient prefix and Y16_REV_GATES/OUT',
            'source_lf_sha256':BASELINE_SHA,'input_count':14,'input_order':'W0..W5,E0..E2,Nm0..Nm2,k1,k2',
            'outputs_order':'Q0..Q5,U0..U6,sign,H0..H6',
            'gates':gates,'outputs':[combination(mask,values) for mask in outs],
            'early_kp1_gate':0,'n_masks':n,'early_n0_n1_masks':n[:2],
            'limits':'Joint value interface only. W producer/borrow admission, accumulator low carries, consumer, all measurement coefficients and complete cost remain separate.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path)
    parser.add_argument('--netlist',type=Path,required=True);parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args();source=args.source.read_bytes().replace(b'\r\n',b'\n')
    assert hashlib.sha256(source).hexdigest()==BASELINE_SHA
    net=model(source.decode());raw,targets,values=load(net);ns=[combination(mask,values) for mask in net['n_masks']]
    histogram={}
    for row in range(1<<14):
        ww,ee,mm=row&63,row>>6&7,row>>9&7;ka,kb=row>>12&1,row>>13&1
        expected_n=ee-mm+(ww&7)+8*(ka|kb)*(ww>>3&1)+16*kb*(ww>>4&1)+32*(ka&kb)*(ww>>5&1)
        got_n=sum((v>>row&1)<<i for i,v in enumerate(ns));got_n=got_n-256 if got_n&128 else got_n
        assert got_n==expected_n
        field=[v>>row&1 for v in targets]
        word=sum(field[i]<<b for i,b in enumerate(range(4,10)))
        word+=sum(field[6+i]<<b for i,b in enumerate(range(10,17)))
        word+=sum(field[13]<<b for b in range(17,32))
        word+=sum(field[14+i]<<b for i,b in enumerate(range(32,39)))
        word+=sum(field[13]<<b for b in range(39,56))
        assert word==((expected_n*((1<<32)+976))&((1<<56)-1))
        histogram[str(expected_n)]=histogram.get(str(expected_n),0)+1
    result=closure(raw,targets)
    summary={'status':'exact_joint_reverse_value_model_checked','domain_rows':1<<14,
             'source_lf_sha256':BASELINE_SHA,'original_ANDs':len(net['gates']),
             'raw_rank':len(Space(raw).values),'raw_plus_output_rank':len(Space(raw+targets).values),
             'original_internal_rank':len(Space(values).values),'n_histogram':histogram,
             'closure':result,'admitted_producer_domain_verified':False,'native_cleanup_verified':False,
             'limits':net['limits']}
    args.netlist.write_bytes((json.dumps(net,indent=2)+'\n').encode())
    summary['netlist_sha256']=hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    args.report.write_bytes((json.dumps(summary,indent=2)+'\n').encode())
    print(json.dumps({key:summary[key] for key in ['status','original_ANDs','raw_rank','raw_plus_output_rank','original_internal_rank']}))
    print(json.dumps({'closure_status':result['status'],'ANDs':result.get('AND_count',result.get('computed_ANDs'))}))


if __name__=='__main__':main()
