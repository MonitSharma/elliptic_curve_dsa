// Exact semantic keys for small classical Boolean supports. Large functions
// remain opaque symbols of their actual immutable expressions; no sampling.
#[derive(Clone,Debug,PartialEq,Eq,Hash)]struct SemTruth{atoms:Vec<u32>,table:u64}
impl SemTruth{
 fn mask(n:usize)->u64{if n==6{u64::MAX}else{(1u64<<(1usize<<n))-1}}
 fn complement(&self)->Self{Self{atoms:self.atoms.clone(),table:self.table^Self::mask(self.atoms.len())}}
 fn shrink(mut self)->Self{let mut bit=0;while bit<self.atoms.len(){let n=self.atoms.len();let step=1usize<<bit;let independent=(0..1usize<<n).filter(|r|r&step==0).all(|r|(self.table>>r)&1==(self.table>>(r|step))&1);if independent{let mut out=0u64;for row in 0..1usize<<(n-1){let old=(row&(step-1))|((row&!(step-1))<<1);out|=((self.table>>old)&1)<<row;}self.atoms.remove(bit);self.table=out;}else{bit+=1;}}self}
 fn key(&self)->(Self,u32){let neg=(self.table&1)as u32;if neg==0{(self.clone(),0)}else{(self.complement(),1)}}
}
impl Expr{
 fn semantic(&self,v:u32)->SemTruth{if v<=1{return SemTruth{atoms:vec![],table:v as u64};}let t=&self.truths[(v/2-1)as usize];if v&1==0{t.clone()}else{t.complement()}}
 fn combine_semantic(&self,k:u8,a:u32,b:u32)->Option<SemTruth>{let a=self.semantic(a);let b=self.semantic(b);let mut atoms=a.atoms.clone();atoms.extend_from_slice(&b.atoms);atoms.sort_unstable();atoms.dedup();if atoms.len()>6{return None;}let ap:Vec<_>=a.atoms.iter().map(|v|atoms.binary_search(v).unwrap()).collect();let bp:Vec<_>=b.atoms.iter().map(|v|atoms.binary_search(v).unwrap()).collect();let project=|row:usize,positions:&[usize]|positions.iter().enumerate().fold(0usize,|v,(i,&bit)|v|(((row>>bit)&1)<<i));let mut table=0;for row in 0..1usize<<atoms.len(){let av=(a.table>>project(row,&ap))&1;let bv=(b.table>>project(row,&bp))&1;table|=(if k==1{av&bv}else{av^bv})<<row;}Some(SemTruth{atoms,table}.shrink())}
 fn semantic_node(&mut self,k:u8,a:u32,b:u32)->u32{let summary=self.combine_semantic(k,a,b);if let Some(t)=&summary{if t.atoms.is_empty(){return(t.table&1)as u32;}let(key,neg)=t.key();if let Some(&v)=self.canonical.get(&key){return v^neg;}}let id=self.atom();*self.nodes.last_mut().unwrap()=(k,a,b);if let Some(t)=summary{let(key,neg)=t.key();*self.truths.last_mut().unwrap()=t;self.canonical.insert(key,id^neg);}id}
}
