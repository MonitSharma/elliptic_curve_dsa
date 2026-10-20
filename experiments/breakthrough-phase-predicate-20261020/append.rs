pub(super) fn valid(acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:QubitId,drops:&[usize])->bool{
    let n=acc.len();if n<2||rows.len()!=n||ones.len()!=n{return false;}let m=n-2;if drops.len()>m{return false;}let room=m-drops.len();
    for(j,&i)in drops.iter().enumerate(){if i==0||i>=m||i+1-j>room||j>0&&drops[j-1]+1>=i{return false;}}
    let mut target=BTreeSet::from([cin.0]);if !acc.iter().all(|q|target.insert(q.0)){return false;}
    rows.iter().all(|r|{let mut seen=BTreeSet::new();r.iter().all(|q|!target.contains(&q.0)&&seen.insert(q.0))})
}
pub(super) fn apply(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:QubitId,drops:&[usize],not_carry:bool)->bool{
    if !valid(acc,rows,ones,cin,drops){return false;}let n=acc.len();let m=n-2;let mut cc=vec![None;m+1];cc[0]=Some(cin);
    for i in 0..m{
        let out=carry(c,acc[i],&rows[i],ones[i],cc[i].unwrap());cc[i+1]=Some(out);
        if drops.contains(&i){erase(c,cc[i].take().unwrap(),acc[i-1],&rows[i-1],ones[i-1],cc[i-1].unwrap());}
    }
    assert!(super::phase_fusion::pair(c,acc[n-2],acc[n-1],cc[m].unwrap(),&rows[n-2],ones[n-2],&rows[n-1],ones[n-1],not_carry));
    for i in(1..=m).rev(){if let Some(out)=cc[i]{
        if drops.contains(&(i-1)){
            let bit=c.alloc_bit();c.hmr(out,bit);c.release_clean(out);c.push_condition(bit);
            assert!(super::phase_fusion::pair(c,acc[i-2],acc[i-1],cc[i-2].unwrap(),&rows[i-2],ones[i-2],&rows[i-1],ones[i-1],false));
            c.pop_condition();c.free_bit(bit);
        }else{erase(c,out,acc[i-1],&rows[i-1],ones[i-1],cc[i-1].unwrap());}
    }}true
}

#[cfg(test)]mod tests{
 use super::*;use crate::circuit::{analyze_ops,Op,OperationType};use crate::sim::Simulator;use sha3::digest::XofReader;
 struct Words{data:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
 fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
 fn rank(a:&[QubitId],b:&[QubitId])->usize{if a.is_empty()||b.is_empty()||a==b{1}else{2}}
 fn fixture(n:usize,pattern:usize,drops:&[usize],negative:bool,guard:u64,twice:bool,probe:Option<usize>){
  let mut c=Builder::new();let source=c.alloc_qubits(n);let target=c.alloc_qubits(n);let ci=c.alloc_qubit();let shared=c.alloc_qubit();let bit=c.alloc_bit();
  let interface:Vec<_>=source.iter().chain(&target).copied().chain([ci,shared]).collect();c.declare_qubit_register(&interface);
  let rows:Vec<Vec<QubitId>>=(0..n).map(|i|match pattern{0=>vec![shared],1=>vec![source[i],shared],2=>vec![source[i]],_=>if i%3==1{vec![]}else{vec![source[i]]}}).collect();
  let ones:Vec<_>=(0..n).map(|i|pattern==2&&i%3==0||pattern==3&&i%3==1).collect();let copies=1+usize::from(twice);let active=c.active_qubits();
  c.push_condition(bit);let((),peak)=c.r3_peak(|c|for _ in 0..copies{assert!(apply(c,&target,&rows,&ones,ci,drops,negative));});c.pop_condition();
  let m=n-2;assert_eq!(peak,active+(m-drops.len())as u32);let ops=c.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());assert_eq!(nq as usize,interface.len()+m-drops.len());let nr=draws(&ops);assert_eq!(nr,m*copies);
  let ranks:Vec<_>=drops.iter().map(|&j|rank(&rows[j-1],&rows[j])).collect();let top=rank(&rows[n-2],&rows[n-1]);
  assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),m*copies);assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCZ).count(),(top+ranks.iter().sum::<usize>())*copies);
  let starts:Vec<_>=if probe.is_some(){vec![0x37AC0]}else{(0..1usize<<(2*n+2)).step_by(64).collect()};
  for start in starts{
   let words:Vec<_>=(0..nr).map(|j|match probe{Some(p)=>if p==j||p==nr{u64::MAX}else{0},None=>0xD1B54A32D192ED03u64.wrapping_mul((start+j+1)as u64).rotate_left(j as u32)}).collect();let mut random=Words{data:words.iter().flat_map(|w|w.to_le_bytes()).collect(),pos:0};let mut s=Simulator::new(nq as usize,nb as usize,&mut random);s.bits[bit.0 as usize]=guard;
   for lane in 0..64{for(i,&q)in interface.iter().enumerate(){if(start+lane)>>i&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}}let original=s.qubits.clone();let mut phase=0u64;
   for lane in 0..64{let value=start+lane;let mut a=0usize;for(i,row)in rows.iter().enumerate(){let x=row.iter().fold(usize::from(ones[i]),|v,q|v^(value>>interface.iter().position(|r|r==q).unwrap()&1));a|=x<<i;}let b=value>>n&((1<<n)-1);let cin=value>>(2*n)&1;
    if !twice&&guard>>lane&1!=0&&((((a+b+cin)>>n)!=0)^negative){phase|=1u64<<lane;}}
   let mut wanted_t=(m+top)as u64*copies as u64*guard.count_ones()as u64;
   for copy in 0..copies{for(j,&d)in drops.iter().enumerate(){let i=d+1;let ordinal=drops.len()+m-i-drops.iter().filter(|&&x|x>i).count();wanted_t+=ranks[j]as u64*(words[copy*m+ordinal]&guard).count_ones()as u64;}}
   s.apply_iter(ops.iter());assert_eq!(s.qubits,original);assert_eq!(s.phase,phase,"n={n} pattern={pattern} drops={drops:?} negative={negative} twice={twice}");assert_eq!(s.stats.toffoli_gates as u64,wanted_t);drop(s);assert_eq!(random.pos,nr*8);
  }
 }
 #[test]fn all_small_inputs_all_valid_schedules_both_signs_and_guards(){for n in 2usize..=7{let m=n-2;for mask in 0usize..1usize<<m.saturating_sub(1){let ds:Vec<_>=(1..m).filter(|&i|mask>>(i-1)&1!=0).collect();let room=m-ds.len();if ds.iter().enumerate().any(|(j,&i)|i+1-j>room||j>0&&ds[j-1]+1>=i){continue;}for pattern in 0..4{for negative in[false,true]{for guard in[u64::MAX,0xA9563C78F012DE4B]{fixture(n,pattern,&ds,negative,guard,false,None);}}}}}}
 #[test]fn every_measurement_position_double_application_and_false_guard(){for ds in[vec![1],vec![2],vec![1,3],vec![2,4],vec![1,3,5]]{for pattern in 0..4{for twice in[false,true]{let nr=7*(1+usize::from(twice));for probe in 0..nr+2{for guard in[0u64,u64::MAX,0xAA55AA55AA55AA55]{fixture(9,pattern,&ds,true,guard,twice,Some(probe));}}}}}}
 #[test]fn invalid_schedules_and_aliases_reject_before_emission(){let mut c=Builder::new();let a=c.alloc_qubits(7);let b=c.alloc_qubits(7);let ci=c.alloc_qubit();let mut rows:Vec<_>=a.iter().map(|&q|vec![q]).collect();let before=c.op_count();assert!(!apply(&mut c,&b,&rows,&[false;7],ci,&[1,2],false));assert!(!apply(&mut c,&b,&rows,&[false;7],ci,&[3,4],false));rows[2]=vec![b[1]];assert!(!apply(&mut c,&b,&rows,&[false;7],ci,&[1],false));assert_eq!(before,c.op_count());}
}
