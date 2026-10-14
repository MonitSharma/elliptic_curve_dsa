"""Conservative carry/sign-letter domain for the genuine three-add producer.

Uses arbitrary unsigned N-bit T and B, not canonical-field or sampled-input
assumptions. Keeps all low accumulator bits and all shift-control patterns.
"""
import argparse,hashlib,itertools,json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load

def allowed_ranges(bits=256):
    m=1<<bits;result=[]
    for nm in range(8):
        coefficient=7-2*nm
        minimum=(nm+min(0,coefficient))*(m-1)
        maximum=(1+nm+max(0,coefficient))*(m-1)
        result.append((minimum//m,maximum//m))
    return result

def admission_mask():
    allowed=allowed_ranges()
    return sum(1<<row for row in range(16384) if allowed[row>>9&7][0]<=(row>>6&7)<=allowed[row>>9&7][1])

def load_admitted(net):
    raw,targets,values=load(net);mask=admission_mask()
    return [v&mask for v in raw],[v&mask for v in targets],[v&mask for v in values]

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('closed',type=Path)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args();net=json.loads(args.netlist.read_bytes());closed=json.loads(args.closed.read_bytes())
    allowed=allowed_ranges();small=[]
    for bits in [4,6,8]:
        m=1<<bits;observed=[set() for _ in range(8)]
        for nm in range(8):
            for t in range(m):
                for b in range(m):
                    # Independently evaluate three separate signed addends.
                    source=[b if not nm>>i&1 else m-1-b for i in range(3)]
                    x=t+source[0]+2*source[1]+4*source[2]
                    assert x==t+(7-2*nm)*b+nm*(m-1)
                    observed[nm].add(x//m)
        bounds=allowed_ranges(bits)
        assert all(values==set(range(lo,hi+1)) for values,(lo,hi) in zip(observed,bounds))
        small.append({'word_bits':bits,'producer_cases':8*m*m,'E_Nm_support_pairs':sum(len(values) for values in observed)})
    raw,targets,values=load_admitted(net);s=list(raw)
    for a,b in closed['gates']:s.append(combination(a,s)&combination(b,s))
    w=Space(raw+targets);p2=Space(s+[s[i]&s[j] for i,j in itertools.combinations(range(1,23),2)])
    p3=Space(p2.values+[s[i]&s[j]&s[k] for i,j,k in itertools.combinations(range(1,23),3)])
    result={'status':'conservative_source_integer_producer_domain_verified','source_lf_sha256':net['source_lf_sha256'],
            'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),'producer_word_bits':256,
            'producer_integer_identity':'X=T+(7-2Nm)*B+Nm*(2^256-1); E=floor(X/2^256)',
            'source_contract':'body performs T+S0+2S1+4S2 with Si=B XOR broadcast(si), Nm=s0+2s1+4s2; fold receives original high3 E before ESH shedding.',
            'E_ranges_by_Nm':allowed,'E_Nm_pair_count':sum(hi-lo+1 for lo,hi in allowed),
            'all_accLow6_values_retained':True,'all_shift_control_patterns_retained':True,
            'admitted_primitive_rows':admission_mask().bit_count(),'truth_vector_layout_rows':16384,
            'admission_mask_sha256':hashlib.sha256(admission_mask().to_bytes(2048,'little')).hexdigest(),
            'exhaustive_small_word_checks':small,
            'ranks':{'raw':len(Space(raw).values),'W':len(w.values),'S':len(Space(s).values),'P2':len(p2.values),
                     'P2_union_W':len(Space(p2.values+w.values).values),'P3':len(p3.values),'P3_union_W':len(Space(p3.values+w.values).values)},
            'qualified_score':None,
            'limits':'Source-integer range proof and conservative primitive filter. Does not establish actual fullbody phase correctness, all producer gate recurrences or any candidate; narrowfin4 ESH proofs not extrapolated. Existing all14input lower bound cannot automatically transfer to this reduced domain.'}
    args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({key:result[key] for key in ['status','E_Nm_pair_count','admitted_primitive_rows','ranks']}))

if __name__=='__main__':main()
