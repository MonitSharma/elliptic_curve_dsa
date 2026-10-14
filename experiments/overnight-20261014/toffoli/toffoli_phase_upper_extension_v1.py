"""Independent upper-result coordinates do not open free bank-phase cleanup."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load
from toffoli_check_obstruction import rank


def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('certificate',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    net=json.loads(a.netlist.read_text());receipt=json.loads(a.certificate.read_text());raw,targets,original=load(net)
    s=Space(raw)
    for aa,bb in receipt['gates']:assert s.add(combination(aa,s.values)&combination(bb,s.values))
    n=1<<14
    def repeat(v):return v|(v<<n)|(v<<(2*n))|(v<<(3*n))
    high=[0,0];translations=[]
    for lower in range(n):
        acc,e,nm=lower&63,lower>>6&7,lower>>9&7;k1,k2=lower>>12&1,lower>>13&1
        c3=int((acc&7)+e>=8);c4=(acc>>3&1)&c3;r=nm+(acc&7)
        a4=r&1;a5=(r^(r>>1))&1;acc4,z=acc>>4&1,acc>>5&1
        c5=(acc4&a4)|(acc4&c4)|(a4&c4)
        y3=(k1|k2)&((acc>>3&1)^c3);y4=k2&(acc4^c4^a4);y5=(k1&k2)&(z^c5^a5)
        k=r+8*(y3+2*y4+4*y5-c3)
        delta=e-((1<<32)+976)*k
        result=[(((upper<<6)+acc+delta)&255)>>6 for upper in range(4)]
        assert len(set(result))==4
        translations.append((result[0]-0)%4)
        for upper,value in enumerate(result):
            row=upper*n+lower
            for bit in range(2):high[bit]|=(value>>bit&1)<<row
    sw=[repeat(v) for v in s.values]+high
    w=Space(raw+targets);ww=[repeat(v) for v in w.values]+high
    data=list(raw);data[1:7]=targets[21:27];dd=[repeat(v) for v in data]+high
    products=sw+[x&y for x,y in itertools.combinations(sw,2)]
    sr=rank(sw);wr=rank(ww);pr=rank(products);ur=rank(products+ww)
    assert (sr,wr,pr,ur,pr+wr-ur)==(25,42,275,292,25)
    ss=Space(sw);assert all(ss.express(v) is not None for v in dd)
    result={'status':'upper_result_coordinate_extension_preserves_closed_phase_obstruction',
            'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(a.netlist.read_bytes()).hexdigest(),
            'certificate_sha256':hashlib.sha256(a.certificate.read_bytes()).hexdigest(),
            'checked_inputs':65536,'fixed_lower_input_groups':16384,'upper_translation_groups_bijective':16384,
            'S_rank':sr,'W_rank':wr,'P2_S_rank':pr,'P2_S_plus_W_rank':ur,'intersection_rank':pr+wr-ur,
            'final_data_rank':rank(dd),'translation_distribution':{str(d):translations.count(d) for d in set(translations)},
            'tensor_argument':'For each fixed constructor input, addition translates the arbitrary upper register bijectively, so upper result bits are independent coordinates u. W*=W⊕span(u), S*=S⊕span(u). In a quadratic expression from S*, all coefficients of u_i and u_i*u_j must cancel separately to yield an old-low function. Thus P2(S*)∩W*=S*, inherited from P2(S)∩W=S. The argument extends to any number of independent upper-result bits.',
            'scope':'Unrestricted constructor primitive: arbitrary upper input words, 14 independent low/control inputs, and cleanup using only linear value operations and free quadratic Z/CZ measurement repair. A retained helper outside W, a charged nonlinear value/phase gate, or a restricted producer domain can escape. This is not an all-input point-addition proof, nor a bound on every possible cleanup cost.'}
    a.output.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result,indent=2))


if __name__=='__main__':main()
