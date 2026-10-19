// Exact local carry replacement. Research tool, never a scored result.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId};
use std::collections::{HashMap,HashSet};
const NO:u64=u64::MAX;
#[derive(Clone,Debug)]
struct Hold { start:usize,end:usize,a:u64,b:u64,c:u64,t:u64,bit:u64,compact:bool,reverse_length:usize }
impl Hold {fn forward_len(&self)->usize{if self.compact{4}else{6}}fn reverse_len(&self)->usize{self.reverse_length}fn measurement_offset(&self)->usize{if self.compact{1}else{3}}}
fn cx(o:&Op,c:u64,t:u64)->bool {o.kind==K::CX&&o.q_control1.0==c&&o.q_target.0==t&&o.c_condition.0==NO}
fn pair(o:&Op,k:K,a:u64,b:u64)->bool {o.kind==k&&((o.q_control1.0==a&&o.q_control2.0==b)||(o.q_control1.0==b&&o.q_control2.0==a))}
fn opening(v:&[Op],i:usize)->Option<Hold>{
 let w=v.get(i..i+4)?; let(c,a,b,t)=(w[0].q_control1.0,w[0].q_target.0,w[1].q_target.0,w[2].q_target.0);
 if [a,b,c,t].iter().copied().collect::<HashSet<_>>().len()!=4||[a,b,c,t].contains(&NO){return None;}
 if !(cx(&w[0],c,a)&&cx(&w[1],c,b)&&pair(&w[2],K::CCX,a,b)&&w[2].c_condition.0==NO){return None;}
 if cx(&w[3],c,t){return Some(Hold{start:i,end:0,a:b,b:a,c,t,bit:NO,compact:true,reverse_length:0});}
 let w=v.get(i..i+6)?;
 (cx(&w[3],c,b)&&cx(&w[4],c,t)&&cx(&w[5],c,a)).then_some(Hold{start:i,end:0,a,b,c,t,bit:NO,compact:false,reverse_length:0})
}
fn closing(v:&[Op],i:usize,s:&Hold)->Option<(u64,usize)>{
 if s.compact{
  let w=v.get(i..i+6)?;let(a,b,c,t)=(s.a,s.b,s.c,s.t);let bit=w[1].c_target.0;
  if !(cx(&w[0],c,t)&&w[1].kind==K::Hmr&&w[1].q_target.0==t&&w[1].c_condition.0==NO&&w[2].kind==K::CZ&&((w[2].q_control1.0==a&&w[2].q_target.0==b)||(w[2].q_control1.0==b&&w[2].q_target.0==a))&&w[2].c_condition.0==bit){return None;}
  if cx(&w[3],b,a)&&cx(&w[4],c,b)&&cx(&w[5],c,a){return Some((bit,6));}
  if cx(&w[3],c,b)&&cx(&w[4],b,a){return Some((bit,5));}
  if w[3].kind==K::R&&w[3].q_target.0==t&&w[3].c_condition.0==NO&&cx(&w[4],c,b)&&cx(&w[5],b,a){return Some((bit,6));}
  return None;
 }
 let w=v.get(i..i+9)?;let(a,b,c,t)=(s.a,s.b,s.c,s.t);let bit=w[3].c_target.0;
 (cx(&w[0],c,t)&&cx(&w[1],c,a)&&cx(&w[2],c,b)&&w[3].kind==K::Hmr&&w[3].q_target.0==t&&w[3].c_condition.0==NO&&w[4].kind==K::CZ&&((w[4].q_control1.0==a&&w[4].q_target.0==b)||(w[4].q_control1.0==b&&w[4].q_target.0==a))&&w[4].c_condition.0==bit&&cx(&w[5],c,b)&&cx(&w[6],c,a)&&cx(&w[7],b,a)&&cx(&w[8],c,a)).then_some((bit,9))
}
fn qubits(o:&Op)->impl Iterator<Item=u64>{[o.q_control2.0,o.q_control1.0,o.q_target.0].into_iter().filter(|&x|x!=NO)}
fn discover(v:&[Op],minimum:u64)->Vec<Hold>{
 let nq=v.iter().flat_map(qubits).max().unwrap()as usize+1;
 let pinned_b:HashSet<_>=v.iter().filter(|o|o.kind==K::AppendToRegister&&o.c_target.0!=NO).map(|o|o.c_target.0).collect();
 let pinned:HashSet<_>=v.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=NO).map(|o|o.q_target.0).collect();
 // Prove that the removed measurement's bit has no further reader before a
 // definite unconditional overwrite. Unknown enclosing guards are excluded.
 let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&x|x!=NO).max().unwrap_or(0)as usize+1;
 let mut depth=0;let mut depths=vec![0u16;v.len()];
 for(i,o)in v.iter().enumerate(){depths[i]=depth;if o.kind==K::PushCondition{depth+=1;}if o.kind==K::PopCondition{depth-=1;}}
 assert_eq!(depth,0);
 let mut safe=vec![true;nb];let mut hmr_safe=HashSet::new();
 for(i,o)in v.iter().enumerate().rev(){
  // Capture suffix safety before the one immediate phase-correction reader.
  if i>0&&o.kind==K::CZ&&o.c_condition.0!=NO&&v[i-1].kind==K::Hmr&&v[i-1].c_target.0==o.c_condition.0&&safe[o.c_condition.0 as usize]{hmr_safe.insert(i-1);}
  if o.c_target.0!=NO {let b=o.c_target.0 as usize;safe[b]=matches!(o.kind,K::Hmr|K::BitStore0|K::BitStore1)&&depths[i]==0&&o.c_condition.0==NO;}
  if o.c_condition.0!=NO{safe[o.c_condition.0 as usize]=false;}
 }
 let mut known_zero=vec![true;nq];for &q in &pinned{known_zero[q as usize]=false;}
 let mut last=vec![None;nq];let mut open:HashMap<u64,Hold>=HashMap::new();let mut found=vec![];
 let mut pending:HashMap<usize,Hold>=HashMap::new();
 for(i,o)in v.iter().enumerate(){
  if let Some(s)=pending.remove(&i){open.insert(s.t,s);}
  if depths[i]==0&&o.kind==K::CX {
   let t=o.q_target.0;
   if let Some(s)=open.get(&t){
    if let Some((bit,length))=closing(v,i,s){
     if [s.a,s.b,s.c].iter().all(|&q|last[q as usize].map_or(true,|at|at<s.start+s.forward_len()))&&hmr_safe.contains(&(i+s.measurement_offset()))&&!pinned_b.contains(&bit){
      let mut s=s.clone();s.end=i;s.bit=bit;s.reverse_length=length;found.push(s);
     }
    }
   }
  }
  if depths[i]==0 {if let Some(s)=opening(v,i){if s.t>=minimum&&!pinned.contains(&s.t)&&known_zero[s.t as usize]{pending.insert(i+s.forward_len(),s);}}}
  if matches!(o.kind,K::X|K::CX|K::CCX|K::R|K::Hmr|K::Swap){if o.q_target.0!=NO{last[o.q_target.0 as usize]=Some(i);}if o.kind==K::Swap&&o.q_control1.0!=NO{last[o.q_control1.0 as usize]=Some(i);}}
  if o.q_target.0!=NO {
   let t=o.q_target.0 as usize;
   if !matches!(o.kind,K::Register|K::AppendToRegister|K::Z|K::CZ|K::CCZ|K::DebugPrint){
    // A held carry must be read-only between its constructor and cleanup.
    open.remove(&(t as u64));
    known_zero[t]=matches!(o.kind,K::R|K::Hmr)&&depths[i]==0&&o.c_condition.0==NO;
   }
   if o.kind==K::Swap&&o.q_control1.0!=NO{known_zero[o.q_control1.0 as usize]=false;open.remove(&o.q_control1.0);}
  }
 }
 found.sort_by_key(|s|s.start);
 found
}

fn gate(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_target=QubitId(t);o.q_control1=QubitId(a);if k==K::CCX{o.q_control2=QubitId(b);}o.validate();o}
fn resolve(mut q:u64,m:&HashMap<u64,u64>)->u64{let mut n=0;while let Some(&p)=m.get(&q){q=p;n+=1;assert!(n<=m.len());}q}
