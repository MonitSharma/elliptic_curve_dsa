// Exact queries never introduce atoms, cuts or assumptions.
#[derive(Default)]
struct Witnesses(std::collections::HashMap<P,BTreeSet<usize>>,std::collections::HashMap<M,BTreeSet<usize>>);
impl Witnesses {
 fn insert(&mut self,q:usize,value:&P){if !value.is_empty()&&value!=&one(){self.0.entry(value.clone()).or_default().insert(q);for m in value.iter().filter(|m|!m.is_empty()){self.1.entry(m.clone()).or_default().insert(q);}}}
 fn remove(&mut self,q:usize,value:&P){if let Some(s)=self.0.get_mut(value){assert!(s.remove(&q));if s.is_empty(){self.0.remove(value);}}for m in value.iter().filter(|m|!m.is_empty()){let s=self.1.get_mut(m).expect("current monomial index");assert!(s.remove(&q));if s.is_empty(){self.1.remove(m);}}}
 fn find(&self,product:&P,a:usize,b:usize,target:usize,cap:usize)->Option<(usize,bool)>{
  let permitted=|q:&&usize|**q!=a&&**q!=b&&**q!=target;
  if let Some(q)=self.0.get(product).and_then(|s|s.iter().find(permitted)){return Some((*q,false));}
  let mut complement=product.clone();
  if complement.first().is_some_and(|m|m.is_empty()){complement.remove(0);}else{complement.insert(0,vec![]);}
  if complement.len()>cap{return None;}
  self.0.get(&complement).and_then(|s|s.iter().find(permitted)).map(|&q|(q,true))
 }
}

// Pure symmetric difference: queries never allocate abstract atoms or lose terms.
fn exact_xor(a:&P,b:&P)->P{let(mut i,mut j)=(0,0);let mut out=vec![];while i<a.len()||j<b.len(){if j==b.len()||(i<a.len()&&a[i]<b[j]){out.push(a[i].clone());i+=1;}else if i==a.len()||b[j]<a[i]{out.push(b[j].clone());j+=1;}else{i+=1;j+=1;}}out}
impl Witnesses{
 fn find_pair(&self,p:&P,values:&[P],a:usize,b:usize,t:usize)->Option<(usize,usize,bool)>{
  // Any nonconstant term in p occurs in exactly one member of an XOR pair.
  // Enumerating all live wires containing its rarest term is therefore complete.
  let m=p.iter().filter(|m|!m.is_empty()).min_by_key(|m|self.1.get(*m).map_or(0,|s|s.len()))?;
  let permitted=|q:usize|q!=a&&q!=b&&q!=t;
  for &u in self.1.get(m)?{if !permitted(u){continue;}let wanted=exact_xor(p,&values[u]);
   for complement in [false,true]{let mut key=wanted.clone();if complement{if key.first().is_some_and(|m|m.is_empty()){key.remove(0);}else{key.insert(0,vec![]);}}
    if let Some(&v)=self.0.get(&key).and_then(|s|s.iter().find(|&&v|v!=u&&permitted(v))){return Some((u.min(v),u.max(v),complement));}
   }
  }None
 }
}
