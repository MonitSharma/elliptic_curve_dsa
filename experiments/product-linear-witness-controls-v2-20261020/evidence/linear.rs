// Every row is an exact current-wire identity. Dropping rows only loses opportunities.
#[derive(Clone,Debug)]struct LinearRow{p:P,wires:BTreeSet<usize>,constant:bool}
struct LinearWitnesses{rows:std::collections::BTreeMap<M,LinearRow>,reverse:std::collections::HashMap<usize,BTreeSet<M>>,term_limit:usize,wire_limit:usize}
impl Default for LinearWitnesses{fn default()->Self{Self{rows:Default::default(),reverse:Default::default(),term_limit:1024,wire_limit:32}}}
fn xor_support(a:&BTreeSet<usize>,b:&BTreeSet<usize>)->BTreeSet<usize>{a.symmetric_difference(b).copied().collect()}
fn nonconstant(p:&P)->(P,bool){let mut out=p.clone();let c=out.first().is_some_and(|m|m.is_empty());if c{out.remove(0);}(out,c)}
impl LinearWitnesses{
 fn reduce(&self,mut row:LinearRow)->Option<LinearRow>{
  while let Some(pivot)=row.p.last(){let Some(other)=self.rows.get(pivot)else{break};
   row.p=exact_xor(&row.p,&other.p);row.wires=xor_support(&row.wires,&other.wires);row.constant^=other.constant;
   if row.p.len()>self.term_limit||row.wires.len()>self.wire_limit{return None;}
  }Some(row)
 }
 fn insert(&mut self,q:usize,value:&P){
  let(p,constant)=nonconstant(value);if p.is_empty()||p.len()>self.term_limit{return;}
  let Some(row)=self.reduce(LinearRow{p,wires:BTreeSet::from([q]),constant})else{return;};
  let Some(pivot)=row.p.last().cloned()else{return;};assert!(!self.rows.contains_key(&pivot));
  for &wire in &row.wires{assert!(self.reverse.entry(wire).or_default().insert(pivot.clone()));}
  self.rows.insert(pivot,row);
 }
 fn invalidate(&mut self,q:usize){
  let pivots=self.reverse.remove(&q).unwrap_or_default();
  for pivot in pivots{let row=self.rows.remove(&pivot).expect("registered pivot");
   for wire in row.wires{if wire==q{continue;}let members=self.reverse.get_mut(&wire).expect("registered support");assert!(members.remove(&pivot));if members.is_empty(){self.reverse.remove(&wire);}}
  }
 }
 fn find(&self,p:&P,a:usize,b:usize,t:usize)->Option<(Vec<usize>,bool)>{
  let(p,constant)=nonconstant(p);if p.is_empty()||p.len()>self.term_limit{return None;}
  let row=self.reduce(LinearRow{p,wires:BTreeSet::new(),constant})?;
  if !row.p.is_empty()||row.wires.is_empty()||[a,b,t].iter().any(|w|row.wires.contains(w)){return None;}
  Some((row.wires.into_iter().collect(),row.constant))
 }
}
