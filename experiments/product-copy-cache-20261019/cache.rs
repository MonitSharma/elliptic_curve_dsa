#[derive(Clone,Copy,Debug)]
struct Event{op:usize,target:usize}
#[derive(Clone,Copy,Debug)]
struct Pair{first:Event,last:Event,storage:usize}
struct CopyCache{
 last:std::collections::HashMap<P,Event>,touch:Vec<Option<usize>>,cache_end:Vec<Option<usize>>,abi:Vec<bool>,used:Vec<bool>,pairs:Vec<Pair>,missed_no_idle:usize,
}
impl CopyCache{
 fn new(v:&[Op],nq:usize)->Self{let mut abi=vec![false;nq];for o in v{if o.kind==K::AppendToRegister&&o.q_target.0!=NO{abi[o.q_target.0 as usize]=true;}}Self{last:Default::default(),touch:vec![None;nq],cache_end:vec![None;nq],abi,used:vec![false;v.len()],pairs:vec![],missed_no_idle:0}}
 fn touch(&mut self,i:usize,o:&Op){for q in [o.q_control1.0,o.q_control2.0,o.q_target.0]{if q!=NO{self.touch[q as usize]=Some(i);}}}
 fn observe(&mut self,i:usize,o:&Op,p:&P,q:&[P]){
  if p.is_empty()||p==&one(){return;}
  if q[o.q_target.0 as usize].is_empty(){if let Some(first)=self.last.get(p).copied(){
   if !self.used[first.op]&&!self.used[i]{
    let storage=(0..q.len()).find(|&slot|!self.abi[slot]&&q[slot].is_empty()&&self.touch[slot].is_none_or(|t|t<first.op)&&self.cache_end[slot].is_none_or(|t|t<first.op));
    if let Some(storage)=storage{self.pairs.push(Pair{first,last:Event{op:i,target:o.q_target.0 as usize},storage});self.used[first.op]=true;self.used[i]=true;self.cache_end[storage]=Some(i);}else{self.missed_no_idle+=1;}
   }
  }}
  self.last.insert(p.clone(),Event{op:i,target:o.q_target.0 as usize});
 }
}
fn cx(a:usize,t:usize)->Op{let mut o=Op::empty();o.kind=K::CX;o.q_control1=QubitId(a as u64);o.q_target=QubitId(t as u64);o.validate();o}
fn apply_pairs(v:&[Op],pairs:&[Pair])->Vec<Op>{
 let starts:std::collections::HashMap<_,_>=pairs.iter().map(|p|(p.first.op,p)).collect();let ends:std::collections::HashMap<_,_>=pairs.iter().map(|p|(p.last.op,p)).collect();assert_eq!(starts.len(),pairs.len());assert_eq!(ends.len(),pairs.len());
 let mut out=Vec::with_capacity(v.len()+2*pairs.len());
 for(i,o)in v.iter().enumerate(){if let Some(p)=starts.get(&i){assert!(!ends.contains_key(&i));assert_eq!(o.kind,K::CCX);let mut first=*o;first.q_target=QubitId(p.storage as u64);first.validate();out.push(first);out.push(cx(p.storage,p.first.target));}else if let Some(p)=ends.get(&i){assert_eq!(o.kind,K::CCX);out.push(cx(p.storage,p.last.target));out.push(cx(p.last.target,p.storage));}else{out.push(*o);}}
 assert_eq!(out.len(),v.len()+2*pairs.len());out
}
