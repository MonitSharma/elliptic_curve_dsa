// Exact queries never introduce atoms, cuts or assumptions.
#[derive(Default)]
struct Witnesses(std::collections::HashMap<P,BTreeSet<usize>>);
impl Witnesses {
 fn insert(&mut self,q:usize,value:&P){if !value.is_empty()&&value!=&one(){self.0.entry(value.clone()).or_default().insert(q);}}
 fn remove(&mut self,q:usize,value:&P){if let Some(s)=self.0.get_mut(value){assert!(s.remove(&q));if s.is_empty(){self.0.remove(value);}}}
 fn find(&self,product:&P,a:usize,b:usize,target:usize,cap:usize)->Option<(usize,bool)>{
  let permitted=|q:&&usize|**q!=a&&**q!=b&&**q!=target;
  if let Some(q)=self.0.get(product).and_then(|s|s.iter().find(permitted)){return Some((*q,false));}
  let mut complement=product.clone();
  if complement.first().is_some_and(|m|m.is_empty()){complement.remove(0);}else{complement.insert(0,vec![]);}
  if complement.len()>cap{return None;}
  self.0.get(&complement).and_then(|s|s.iter().find(permitted)).map(|&q|(q,true))
 }
}
