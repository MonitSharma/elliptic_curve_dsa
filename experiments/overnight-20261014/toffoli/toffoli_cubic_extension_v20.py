"""Explicit arithmetic identity for the unique cubic escape direction."""
import argparse,hashlib,json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('closed',type=Path)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    net=json.loads(args.netlist.read_bytes());closed=json.loads(args.closed.read_bytes());raw,targets,old=load(net)
    s=Space(raw)
    for a,b in closed['gates']:assert s.add(combination(a,s.values)&combination(b,s.values))
    c1=old[15];c2=old[16]^c1;c3=old[17]^c2;r1=old[20]
    d=raw[2]^raw[11];u=raw[1];v=raw[10];g0=(u^v)&d
    r2=old[21]^r1;L=r2^g0
    A=raw[3]^raw[12];v3=raw[4]^c3
    qpart=((raw[3]^r1)&(raw[12]^r1))^((A^r1)&(d^L))^r1
    y3=(raw[13]^raw[14]^(raw[13]&raw[14]))&v3
    F=y3^qpart
    assert F==targets[3]^c3^A^L and s.express(F) is None
    assert all(s.express(x) is not None for x in [c3,r1,L,A,v3])
    w=Space(raw+targets);assert w.express(F) is not None
    masks={name:s.express(value) for name,value in [('C3',c3),('R1',r1),('L',L),('A',A),('D',d),('v3',v3)]}
    factors=[[1<<13,1<<14],[((1<<13)^(1<<14)^(1<<23)),masks['v3']],
             [(1<<3)^masks['R1'],(1<<12)^masks['R1']],
             [masks['A']^masks['R1'],masks['D']^masks['L']]]
    replay=list(raw)
    for a,b in closed['gates']+factors:replay.append(combination(a,replay)&combination(b,replay))
    assert replay[-3]^replay[-2]^replay[-1]^r1==F
    expanded=Space(w.values+replay[-4:]);extra_rank=len(expanded.values)-40
    report={'status':'unique_cubic_direction_arithmetic_identity_verified','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'domain_rows':16384,
            'identity':'F=Q3+C3+A+L=OR(k1,k2)*v3+MAJ(acc2,Nm2,R1)+(A+R1)*(D+L)',
            'definitions':{'A':'acc2+Nm2','D':'acc1+Nm1','L':'R2+(acc0+Nm0)*(acc1+Nm1)','v3':'acc3+C3'},
            'S23_affine_masks':masks,'F_truth_sha256':hashlib.sha256(F.to_bytes(2048,'little')).hexdigest(),
            'F_original_coordinate_mask':Space(old).express(F),'four_AND_factors':factors,
            'prefix_ANDs':closed['gates']+factors,'outside_rank_for_explicit_prefix':extra_rank,
            'candidate_interface_rank':len(expanded.values),'candidate_value_AND_budget':len(expanded.values)-15,
            'independent_truth_rows_replayed':16384,'qualified_score':None,
            'hypothesis':'Can these two quadratic carry terms and the gated cubic term merge into3 sequential ANDs relativeS23 using2 outside directions?',
            'limits':'Exact scalar relation and explicit4AND prefix only. No complete value constructor, phase/cleanup/native/width/full cost or minimum proof.'}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({key:report[key] for key in ['status','outside_rank_for_explicit_prefix','candidate_interface_rank','candidate_value_AND_budget']}))

if __name__=='__main__':main()
