//! Exact bounded-word adjoint-cofactor arithmetic with reversible history cleanup.
//! Component only. Integer use additionally requires a proved coefficient bound.
use super::{builder::Builder,cofactor_history};
use crate::circuit::QubitId;

fn signed_add(c:&mut Builder,target:&[QubitId],source:&[QubitId],sign:QubitId,shift:usize){
    let n=target.len();assert_eq!(source.len(),n);assert!(shift<n);
    let low=c.alloc_qubits(shift);
    let add:Vec<_>=low.iter().chain(source[..n-shift].iter()).copied().collect();
    for &q in &add{c.cx(sign,q);}
    super::leapfrog::cofactor_diagnostic_add(c,target,&add,sign);
    for &q in add.iter().rev(){c.cx(sign,q);}
    for q in low.into_iter().rev(){c.release_clean(q);}
}

fn fredkin(c:&mut Builder,control:QubitId,a:QubitId,b:QubitId){
    c.cx(a,b);c.ccx(control,b,a);c.cx(a,b);
}

/// Move old bit i to (i+shift) mod n. The fixed permutation is Clifford-only.
fn rotate(c:&mut Builder,word:&[QubitId],shift:isize,control:Option<QubitId>){
    let n=word.len();let mut seen=vec![false;n];
    for start in 0..n{
        if seen[start]{continue;}
        seen[start]=true;let mut next=(start as isize+shift).rem_euclid(n as isize)as usize;
        while next!=start{
            assert!(!seen[next]);seen[next]=true;
            if let Some(k)=control{fredkin(c,k,word[start],word[next]);}else{c.swap(word[start],word[next]);}
            next=(next as isize+shift).rem_euclid(n as isize)as usize;
        }
    }
}

/// Undo sign bits wrapped into the low e positions. Involutive on all words;
/// realizes ordinary multiplication by2^e when source has e sign-extension bits.
fn sign_wrap(c:&mut Builder,word:&[QubitId],k1:QubitId,k2:QubitId){
    let sign=*word.last().unwrap();
    for &q in &word[..3]{c.cx(sign,q);}
    let u=c.alloc_qubit();c.ccx(k1,k2,u);c.cx(k1,u);c.cx(k2,u);
    c.ccx(u,sign,word[3]);c.cx(k2,u);c.cx(k1,u);
    c.ccx(k2,sign,word[4]);c.ccx(u,sign,word[5]);
    c.ccx(k1,k2,u);c.release_clean(u);
}

fn scale(c:&mut Builder,word:&[QubitId],k1:QubitId,k2:QubitId,inverse:bool){
    assert!(word.len()>=9);
    if inverse{
        sign_wrap(c,word,k1,k2);
        rotate(c,word,-2,Some(k2));rotate(c,word,-1,Some(k1));rotate(c,word,-3,None);
    }else{
        rotate(c,word,3,None);rotate(c,word,1,Some(k1));rotate(c,word,2,Some(k2));
        sign_wrap(c,word,k1,k2);
    }
}

/// Flags are [s0,s1,s3,k1,k2]. The four reconstructible flags become zero.
/// C multiple8,D odd and D fitting signed(n-6) are the admitted input domain.
/// Target C updates modulo2^n; exact integer use must also exclude C overflow.
fn update(c:&mut Builder,target:&[QubitId],source:&[QubitId],f:&[QubitId;5]){
    assert_eq!(target.len(),source.len());assert!(target.len()>=9);
    signed_add(c,target,source,f[0],0);signed_add(c,target,source,f[1],1);signed_add(c,target,source,f[2],2);
    scale(c,source,f[3],f[4],false);
    cofactor_history::erase_history(c,target,source,f[0],f[1],f[3],f[4]);
}

fn restore(c:&mut Builder,target:&[QubitId],source:&[QubitId],f:&[QubitId;5]){
    cofactor_history::restore_history(c,target,source,f[0],f[1],f[3],f[4]);
    scale(c,source,f[3],f[4],true);
    for (i,shift) in [(2,2),(1,1),(0,0)]{c.x(f[i]);signed_add(c,target,source,f[i],shift);c.x(f[i]);}
}

#[cfg(test)] mod tests{
    use super::*;
    use crate::circuit::{analyze_ops,Op,OperationType,NO_BIT};
    use crate::sim::Simulator;
    use sha3::digest::XofReader;
    struct Words{bytes:Vec<u8>,pos:usize}
    impl XofReader for Words{fn read(&mut self,buffer:&mut[u8]){let end=self.pos+buffer.len();assert!(end<=self.bytes.len());buffer.copy_from_slice(&self.bytes[self.pos..end]);self.pos=end;}}
    fn rng(words:&[u64])->Words{Words{bytes:words.iter().flat_map(|w|w.to_le_bytes()).collect(),pos:0}}
    fn put<R:XofReader>(s:&mut Simulator<'_,R>,qs:&[QubitId],lane:usize,value:i64){for(i,q)in qs.iter().enumerate(){if(value>>i)&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}}
    fn mask(n:usize)->u64{(1u64<<n)-1}
    fn count_rng(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
    fn build(n:usize,inverse:bool)->(Vec<Op>,Vec<QubitId>,Vec<QubitId>,[QubitId;5],Vec<QubitId>,usize){
        let mut b=Builder::new();let c=b.alloc_qubits(n);let d=b.alloc_qubits(n);let f:[QubitId;5]=b.alloc_qubits(5).try_into().unwrap();let p=b.alloc_qubits(3);
        update(&mut b,&c,&d,&f);let split=b.op_count();if inverse{restore(&mut b,&c,&d,&f);}
        (b.take_ops(),c,d,f,p,split)
    }
    fn initial(s:&mut Simulator<'_,Words>,c:&[QubitId],d:&[QubitId],f:&[QubitId;5],p:&[QubitId],cases:&[(i64,i64,i64,i64)]){
        for(lane,&(cv,dv,word,e))in cases.iter().enumerate(){put(s,c,lane,cv);put(s,d,lane,dv);
            for(i,&q)in f.iter().enumerate(){let bit=if i<3{word>>i&1}else{(e-3)>>(i-3)&1};if bit!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}
            put(s,p,lane,(lane as i64*5)^word);
        }
    }
    fn forward_check(s:&Simulator<'_,Words>,original:&[u64],c:&[QubitId],d:&[QubitId],f:&[QubitId;5],cases:&[(i64,i64,i64,i64)]){
        for(lane,&(cv,dv,word,e))in cases.iter().enumerate(){let q=7-2*(word&1)-4*((word>>1)&1)-8*((word>>2)&1);let ec=(cv+q*dv)as u64&mask(c.len());let ed=(dv<<e)as u64&mask(d.len());
            for(i,&w)in c.iter().enumerate(){assert_eq!(s.qubits[w.0 as usize]>>lane&1,ec>>i&1);}
            for(i,&w)in d.iter().enumerate(){assert_eq!(s.qubits[w.0 as usize]>>lane&1,ed>>i&1);}
        }
        for(i,&value)in s.qubits.iter().enumerate(){
            if c.iter().chain(d.iter()).any(|q|q.0 as usize==i){continue;}
            if [f[0],f[1],f[3],f[4]].iter().any(|q|q.0 as usize==i){assert_eq!(value,0);}else{assert_eq!(value,original[i]);}
        }
        assert_eq!(s.phase,0);
    }

    #[test]fn source_preserving_signed_adder_exhaustive_eight_bit_values(){
        let mut b=Builder::new();let a=b.alloc_qubits(8);let t=b.alloc_qubits(8);let sign=b.alloc_qubit();signed_add(&mut b,&t,&a,sign,0);
        let ops=b.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());let nr=count_rng(&ops);
        assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),7);
        for first in(0..131072usize).step_by(64){let words:Vec<_>=(0..nr).map(|j|0x9E3779B97F4A7C15u64.rotate_left((j%64)as u32)).collect();let mut random=rng(&words);let mut s=Simulator::new(nq as usize,nb as usize,&mut random);
            for lane in 0..64{let i=first+lane;put(&mut s,&a,lane,(i&255)as i64);put(&mut s,&t,lane,((i>>8)&255)as i64);put(&mut s,&[sign],lane,(i>>16)as i64);}
            let original=s.qubits.clone();s.apply_iter(ops.iter());
            for lane in 0..64{let i=first+lane;let aa=(i&255)as i64;let tt=((i>>8)&255)as i64;let ss=(i>>16)as i64;let expected=(tt+(1-2*ss)*aa)as u64&255;for j in 0..8{assert_eq!(s.qubits[t[j].0 as usize]>>lane&1,expected>>j&1);}}
            for i in 0..nq as usize{if !t.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}assert_eq!(s.phase,0);
        }
    }

    #[test]fn cofactor_update_signed_edges_wraps_flags_and_inverse(){
        let n=16;let(ops,c,d,f,p,split)=build(n,true);let(nq,nb,_,_)=analyze_ops(ops.iter());let nr=count_rng(&ops);
        assert_eq!(ops[..split].iter().filter(|o|o.kind==OperationType::CCX).count(),93);
        let mut cases=Vec::new();for cv in[-32768i64,-32760,-16,0,16,32752,32760]{for dv in[-511i64,-255,-31,-1,1,31,255,511]{for word in 0..8{for e in 3..7{cases.push((cv,dv,word,e));}}}}
        assert_eq!(cases.len(),1792);
        for chunk in cases.chunks(64){let words:Vec<_>=(0..nr).map(|j|0xD1B54A32D192ED03u64.rotate_left((j%64)as u32)).collect();let mut random=rng(&words);let mut s=Simulator::new(nq as usize,nb as usize,&mut random);
            initial(&mut s,&c,&d,&f,&p,chunk);let original=s.qubits.clone();s.apply_iter(ops[..split].iter());forward_check(&s,&original,&c,&d,&f,chunk);
            s.apply_iter(ops[split..].iter());assert_eq!(s.qubits,original);assert_eq!(s.phase,0);
        }
    }

    #[test]fn every_measurement_phase_coefficient_vanishes_on_sixty_four_basis_states(){
        let(ops,c,d,f,p,split)=build(10,true);let(nq,nb,_,_)=analyze_ops(ops.iter());let nr=count_rng(&ops);
        // A measurement affects values only through a reset to0; every reader
        // of its outcome is a single direct phase condition. Thus phase is
        // linear in physical RNG words for each basis input; one-hot probes
        // cover every coefficient, including draws by redundant resets.
        assert!(!ops.iter().any(|o|matches!(o.kind,OperationType::PushCondition|OperationType::PopCondition)));
        assert!(ops.iter().all(|o|o.c_condition==NO_BIT||matches!(o.kind,OperationType::Z|OperationType::CZ|OperationType::CCZ)));
        let cases:Vec<_>=(0..64i64).map(|i|([-24,0,24][i as usize%3],[-7,-3,1,5][i as usize%4],i%8,3+(i/8)%4)).collect();
        for probe in 0..nr+2{let mut words=vec![0u64;nr];if probe<nr{words[probe]=u64::MAX;}else if probe==nr{words.fill(u64::MAX);}
            let mut random=rng(&words);let mut s=Simulator::new(nq as usize,nb as usize,&mut random);initial(&mut s,&c,&d,&f,&p,&cases);let original=s.qubits.clone();
            s.apply_iter(ops[..split].iter());forward_check(&s,&original,&c,&d,&f,&cases);s.apply_iter(ops[split..].iter());assert_eq!(s.qubits,original);assert_eq!(s.phase,0);
            drop(s);assert_eq!(random.pos,nr*8);
        }
    }
}
