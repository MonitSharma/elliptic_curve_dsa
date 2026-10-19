"""Exact integer adjoint cofactor updates and reversible transcript decoder.

Mathematical feasibility only. No emitted quantum circuit, resource score,
phase proof, fixed-width allocation, or final statistical gate is claimed.
"""
import hashlib,json,math,statistics,time
from pathlib import Path
from datetime import datetime,timezone
from importlib.util import spec_from_file_location,module_from_spec

r=Path(__file__).resolve().parent
spec=spec_from_file_location('history_model',r.parent/'breakthrough-assessment-20261020/history-model.py')
h=module_from_spec(spec);spec.loader.exec_module(h)
P=(1<<256)-(1<<32)-977
LABEL=b'breakthrough-integer-cofactor-v1'
SAMPLES=4096

def width(x):return abs(x).bit_length()+1

def decode_exponent(d):
    bits=[(d>>i)&1 for i in (3,4,5)]
    k2=(1-bits[0])*(1-bits[1])
    k1=(1-bits[0])*(bits[1]|(1-bits[2]))
    e=3+k1+2*k2
    assert d%(1<<e)==0 and (d>>e)&1
    return e,k1,k2

def decode_forced(c,d):
    assert c&1 and d&1
    return (1^(c>>1)^(d>>1))&1,(1^(c>>2)^(d>>2))&1

def decoder_controls():
    cases=0
    for s0 in range(2):
      for s1 in range(2):
       for s3 in range(2):
        q=7-2*s0-4*s1-8*s3
        for e in range(3,7):
         for c in range(-128,129,8):
          for d in range(-63,64,2):
           newc=c+q*d;newd=d<<e
           assert decode_exponent(newd)[0]==e
           assert decode_forced(newc,newd>>e)==(s0,s1)
           recovered_s0,recovered_s1=decode_forced(newc,newd>>e)
           q_back=7-2*recovered_s0-4*recovered_s1-8*s3
           assert newc-q_back*(newd>>e)==c
           cases+=1
    return cases

def one(d):
    a=d if d&1 else d-P
    b=(a+(P if a%4==3 else -P))//2
    rails=[a,b];coefs=[2,1];det=a-2*b
    assert abs(det)==P
    saved=0;old_saved=0;exponent=0;peak=0;maxcoef=0;trace=[]
    for tick in range(1000):
        if abs(rails[0])==abs(rails[1]):
            assert abs(rails[0])==1
            answer=(coefs[0]*rails[0]*pow(pow(2,exponent+1,P),-1,P))%P
            assert answer==pow(d,-1,P)
            return {'ticks':tick,'retained_history_bits':saved,'old_five_bit_history_bits':old_saved,
                    'maximum_combined_rail_cofactor_history_dimensions':peak,'maximum_single_cofactor_bits':maxcoef,
                    'total_halving_exponent':exponent,'first_three_ticks':trace[:3]}
        ti=tick%2;si=1-ti;t=rails[ti];source=rails[si];c=coefs[ti];v=coefs[si]
        t1,s0=h.forced(t,source);t2,s1=h.forced(t1,source)
        newt,s3,k1,k2=h.bits_choice(t2,source,abs(t2)>4*abs(source))
        q=7-2*s0-4*s1-8*s3;e=3+k1+2*k2
        assert newt==(t+q*source)//(1<<e) and (t+q*source)%(1<<e)==0
        newc=c+q*v;newv=v<<e
        if tick:
            assert c%8==0 and v&1
            ee,kk1,kk2=decode_exponent(newv)
            ss0,ss1=decode_forced(newc,newv>>ee)
            assert (ss0,ss1,ee,kk1,kk2)==(s0,s1,e,k1,k2)
            qq=7-2*ss0-4*ss1-8*s3
            assert newc-qq*(newv>>ee)==c
            assert (newt<<ee)-qq*source==t
            saved+=1
        else:
            saved+=5 # first cofactor is 2, not a multiple of8: preserve exception
        old_saved+=5
        rails[ti]=newt;coefs[ti]=newc;coefs[si]=newv;exponent+=e
        assert rails[0]*coefs[1]-rails[1]*coefs[0]==det
        scale=pow(2,exponent+1,P)
        assert all((coefs[i]*d-scale*rails[i])%P==0 for i in range(2))
        state_dimensions=sum(map(width,rails))+sum(map(width,coefs))+saved+exponent.bit_length()
        peak=max(peak,state_dimensions);maxcoef=max(maxcoef,*map(width,coefs))
        if tick<3:trace.append({'tick':tick,'e':e,'q':q,'history_bits_retained_this_tick':1 if tick else 5,
                              'signed_rail_dimensions':list(map(width,rails)),'signed_cofactor_dimensions':list(map(width,coefs))})
    raise RuntimeError('Integer model did not converge within diagnostic bound')

def main():
    start=time.time();controls=decoder_controls()
    inputs=[1+int.from_bytes(hashlib.shake_256(LABEL+i.to_bytes(8,'little')).digest(32),'little')%(P-1)for i in range(SAMPLES)]
    rows=[one(d)for d in inputs]
    keys=[k for k in rows[0]if k!='first_three_ticks']
    result={'status':'EXACT_INTEGER_COFACToR_AND_DECODER_FEASIBILITY_ONLY_NO_CIRCUIT_RESULT',
            'at_utc':datetime.now(timezone.utc).isoformat(),'label':LABEL.decode(),'samples':SAMPLES,
            'exhaustive_decoder_controls':controls,'seconds':time.time()-start,
            'metrics':{key:{'mean':statistics.mean(x[key]for x in rows),'min':min(x[key]for x in rows),'max':max(x[key]for x in rows)}for key in keys},
            'all_inverse_and_determinant_and_modular_scale_checks_passed':True,
            'example_trace':rows[0]['first_three_ticks'],
            'identities':{'cofactor_update':'C_new=C+q*D; D_new=2^e*D; q=7-2*s0-4*s1-8*s3; e=3+k1+2*k2',
                          'admission':'C divisible8, D odd after the first macro-step',
                          'forced_decoder':'s0=1 xor C_new[1] xor D[1]; s1=1 xor C_new[2] xor D[2]',
                          'shift_decoder':'e=v2(D_new), restricted3..6; reversible Boolean decoder uses bits3..5',
                          'retained':'Only s3 remains after reconstructible signs and exponent bits are erased'},
            'unresolved':['No native reversible update circuit or measurement-phase proof yet.','Integer magnitude/space maxima are samples, not universal allocation bounds.','A fixed-iteration endpoint and exceptional final-tick treatment must be proved.','Final variable-power-of-two normalization and complete multiply/cleanup costs must be included.','This does not implement the incumbent truncated W1 window or payload.']}
    (r/'MODEL-RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
