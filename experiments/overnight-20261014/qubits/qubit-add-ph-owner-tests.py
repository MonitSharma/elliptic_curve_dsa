"""Two-owner lifetime and independent structured q22=1 column fixture.

The arithmetic perturbation creates an independent component input. It does
not alter any benchmark packet, identity-tail nonce or submission schedule.
"""
from pathlib import Path
import json
import sys

root,out=map(Path,sys.argv[1:3]);path=root/'src/point_add/tests_midg_k24.rs';text=path.read_text()
p=2**256-2**32-977;dx=int('36f0fbac70592fc4b0dd5063485688e95619d5bfd049d59dddf6c7f7dc28b5a4',16)
def recurrence(x):
    r,t,qs=[p,x],[0,1],[]
    while r[-1]:
        q=r[-2]//r[-1];qs.append(q);r.append(r[-2]-q*r[-1]);t.append(t[-2]+q*t[-1])
    return r,t,qs
r,t,qs=recurrence(dx);j=25;desired=6000000
# Fixed independent fractional tail keeps the next remainder substantial;
# targeting an exact integer would make it artificially tiny.
fraction=0x6a09e667f3bcc908bb67ae8584caa73b;denominator=1<<128
target=desired*denominator+fraction
delta=(denominator*r[j-1]-target*r[j])//(target*t[j]+denominator*t[j-1])
structured=dx+delta;sr,st,sq=recurrence(structured)
assert qs[:j-1]==sq[:j-1] and st[j]==t[j]
assert 2**22<=sq[j-1]<2**23 and sq[j-1]>>22&1==1
start=text.index('#[test]\nfn cap24_counterexample8048_exact_column_payload_native')
copy=text[start:]
# The cap24 test is the last existing function in this source version.
copy=copy.replace('cap24_counterexample8048_exact_column_payload_native','ph_owner_structured_q22_one_column_payload_native')
copy=copy.replace(format(dx,'x'),format(structured,'x')).replace('8505374u64',str(sq[j-1])+'u64')
copy=copy.replace('assert!(max_digit>=N::from(1u64)<<23);','assert!(max_digit>=N::from(1u64)<<22);')
copy=copy.replace('CAP24_PAYLOAD_CASE_PASS','PH_OWNER_PAYLOAD_CASE_PASS').replace('CAP24_EXACT8048_COMPONENT_PASS','PH_OWNER_STRUCTURED_COMPONENT_PASS')
copy=copy.replace('quotient=8505374',f'quotient={sq[j-1]}').replace('q23_owner=sw','q22_owner=PH q23_owner=sw')
test=r'''

#[test]
fn ph_owner_two_qbits_preposition_inverse_dirty_phase(){
    let mut b=builder();let _ring=b.alloc_n(276);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);let sw=pool[8];let act=pool[12];let mut cycle=q.clone();cycle.push(pool[9]);cycle.extend([pool[11],pool[10],sx[6],sx[7],pool[6],pool[7],ph,sy[7],sw]);let p22=super::midg::preposition_nonlast_qk(&mut b,&cycle,&sy,ph,22,act,(1,104),&dirty);let p23=super::midg::preposition_qk(&mut b,&cycle,&sy,sw,23,act,(1,104),&dirty);let rec=rec(&mut b,|b|{b.play(&p22,false);b.play(&p23,false);});let forward=emitted(&mut b,&rec,false);let inverse=emitted(&mut b,&rec,true);let mut rng=Rng::new(0x20261014_2223);
    for block in 0..4{let mut input=vec![0u64;693];for &id in &dirty{input[id.0 as usize]=rng.next();}input[ph.0 as usize]=rng.next();input[sw.0 as usize]=rng.next();input[act.0 as usize]=u64::MAX;for lane in 0..64{let size=[1usize,41,97,98,99,104][(lane+block)%6];put(&mut input,&sy,lane,N::from(size as u64));put(&mut input,&q[..size],lane,rng.below(size));}let mut expected=input.clone();expected[ph.0 as usize]=0;expected[sw.0 as usize]=0;for lane in 0..64{let size=get(&input,&sy,lane).as_limbs()[0]as usize;expected[q[size+22].0 as usize]|=(input[ph.0 as usize]>>lane&1)<<lane;expected[q[size+23].0 as usize]|=(input[sw.0 as usize]>>lane&1)<<lane;}let got=run(&forward,693,&|words|*words=input.clone());assert_eq!(got.q,expected);assert_eq!(got.phase,0);let back=run(&inverse,693,&|words|*words=got.q.clone());assert_eq!(back.q,input);assert_eq!(back.phase,0);let(sym,_)=symbolic(&forward,input.clone());assert_eq!(sym,got.q);let(sym,_)=symbolic(&inverse,got.q);assert_eq!(sym,input);}
    eprintln!("PH_TWO_OWNER_COMPONENT_PASS cases=256 q22_owner=PH q23_owner=sw owners_return=true dirty_passengers=259 inverse=true phase=0 measurement_coefficients=0 scope=preposition_only");
}
'''
assert 'fn ph_owner_two_qbits' not in text;path.write_text(text+copy+test)
out.write_text(json.dumps(dict(scope='Independent structured arithmetic component input, not benchmark tuning',
                              original_dx=hex(dx),desired_quotient=desired,target_fraction_numerator=hex(fraction),target_fraction_denominator=hex(denominator),delta=hex(delta),structured_dx=hex(structured),
                              actual_quotient=sq[j-1],earlier24_quotients_identical=True,
                              euclid_step=25,source_column=24,sy=st[j].bit_length(),sz=sr[j].bit_length(),PH_owner_bit_one=True),indent=2)+'\n')
