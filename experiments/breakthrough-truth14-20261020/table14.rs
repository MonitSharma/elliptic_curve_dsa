/// Exact bounded truth tables, with bit-parallel lifting and cofactor removal.
const WORDS:usize=1<<(SUPPORT_CAP-6);
const LOW:[u64;6]=[0x5555555555555555,0x3333333333333333,0x0f0f0f0f0f0f0f0f,0x00ff00ff00ff00ff,0x0000ffff0000ffff,0x00000000ffffffff];
#[derive(Clone,Copy,Debug)]
struct Table{words:[u64;WORDS],used:usize}
impl PartialEq for Table{fn eq(&self,b:&Self)->bool{self.used==b.used&&self.words[..self.used]==b.words[..b.used]}}
impl Eq for Table{}
impl std::hash::Hash for Table{fn hash<H:std::hash::Hasher>(&self,h:&mut H){std::hash::Hash::hash(&self.used,h);std::hash::Hash::hash(&self.words[..self.used],h);}}
impl Table{
 fn low(x:u64)->Self{let mut t=Self{words:[0;WORDS],used:usize::from(x!=0)};t.words[0]=x;t}
 fn bit(&self,row:usize)->u64{assert!(row<1usize<<SUPPORT_CAP);self.words[row/64]>>(row%64)&1}
 fn set(&mut self,row:usize,v:u64){assert!(row<1usize<<SUPPORT_CAP&&v<2);if v!=0{self.words[row/64]|=v<<(row%64);self.used=self.used.max(row/64+1);}}
 fn word(&self,i:usize)->u64{if i<self.used{self.words[i]}else{0}}
 fn put(&mut self,i:usize,v:u64){assert!(i<WORDS);self.words[i]=v;if v!=0{self.used=self.used.max(i+1);}}
 fn trim(&mut self){while self.used>0&&self.words[self.used-1]==0{self.used-=1;}}
 fn mask(n:usize)->Self{assert!(n<=SUPPORT_CAP);let bits=1usize<<n;let mut t=Self::low(0);for i in 0..bits/64{t.put(i,u64::MAX);}if bits%64!=0{t.put(bits/64,(1u64<<(bits%64))-1);}t}
 fn xor(self,b:Self)->Self{let mut out=Self::low(0);for i in 0..self.used.max(b.used){out.put(i,self.words[i]^b.words[i]);}out.trim();out}
 fn and(self,b:Self)->Self{let mut out=Self::low(0);for i in 0..self.used.min(b.used){out.put(i,self.words[i]&b.words[i]);}out.trim();out}
 fn duplicate32(x:u32,j:usize)->u64{
  assert!(j<6);let g=1usize<<j;let mut v=x as u64;
  for (shift,mask)in[(16,0x0000ffff0000ffffu64),(8,0x00ff00ff00ff00ff),(4,0x0f0f0f0f0f0f0f0f),(2,0x3333333333333333),(1,0x5555555555555555)]{if shift>=g{v=(v|(v<<shift))&mask;}}
  v|(v<<g)
 }
 fn compact32(x:u64,j:usize)->u32{
  assert!(j<6);let mut v=x&LOW[j];let mut shift=1usize<<j;
  while shift<32{let mask=if shift==16{0x00000000ffffffff}else{LOW[(shift.trailing_zeros()+1)as usize]};v=(v|(v>>shift))&mask;shift*=2;}
  v as u32
 }
 fn insert(self,j:usize,old_n:usize)->Self{
  assert!(old_n<SUPPORT_CAP&&j<=old_n);let mut out=Self::low(0);
  if j<6{for i in 0..self.used{let w=self.words[i];out.put(2*i,Self::duplicate32(w as u32,j));out.put(2*i+1,Self::duplicate32((w>>32)as u32,j));}}
  else{let g=1usize<<(j-6);for i in 0..self.used{let to=(i&(g-1))|((i&!(g-1))<<1);out.put(to,self.words[i]);out.put(to+g,self.words[i]);}}
  out.trim();out
 }
 fn remove(self,j:usize,n:usize)->Self{
  assert!(j<n&&n<=SUPPORT_CAP);let mut out=Self::low(0);
  if j<6{for i in 0..self.used{let w=(Self::compact32(self.words[i],j)as u64)<<(32*(i%2));let to=i/2;out.put(to,out.words[to]|w);}}
  else{let g=1usize<<(j-6);for i in 0..self.used{if i&g==0{let to=(i&(g-1))|((i>>(j-5))<<(j-6));out.put(to,self.words[i]);}}}
  out.trim();out
 }
 fn essential(&self,j:usize,n:usize)->bool{
  assert!(j<n&&n<=SUPPORT_CAP);
  if j<6{let shift=1usize<<j;(0..self.used).any(|i|((self.words[i]^(self.words[i]>>shift))&LOW[j])!=0)}
  else{let g=1usize<<(j-6);(0..self.used).any(|i|i&g==0&&self.word(i)!=self.word(i+g))}
 }
 fn lift(self,positions:&[usize],total:usize)->Self{
  assert!(positions.len()<=total&&total<=SUPPORT_CAP&&positions.iter().all(|&p|p<total)&&positions.windows(2).all(|p|p[0]<p[1]));let mut value=self;let mut count=positions.len();for j in 0..total{if positions.binary_search(&j).is_err(){value=value.insert(j,count);count+=1;}}assert_eq!(count,total);value
 }
}
fn support_cap()->usize{SUPPORT_CAP}
impl Truth{
 fn row_mask(count:usize)->Table{Table::mask(count)}
 fn constant(value:bool)->Self{Self{atoms:vec![],table:Table::low(value as u64)}}
 fn is_zero(&self)->bool{self.atoms.is_empty()&&self.table==Table::low(0)}
 fn is_one(&self)->bool{self.atoms.is_empty()&&self.table==Table::low(1)}
 fn complement(&self)->Self{Self{atoms:self.atoms.clone(),table:self.table.xor(Self::row_mask(self.atoms.len()))}}
 fn complements(&self,b:&Self)->bool{self.atoms==b.atoms&&self.table.xor(b.table)==Self::row_mask(self.atoms.len())}
 fn canonical(mut atoms:Vec<u64>,mut table:Table)->Self{
  assert!(atoms.len()<=SUPPORT_CAP&&atoms.windows(2).all(|p|p[0]<p[1]));table=table.and(Self::row_mask(atoms.len()));let mut j=0;
  while j<atoms.len(){if table.essential(j,atoms.len()){j+=1;}else{table=table.remove(j,atoms.len());atoms.remove(j);}}Self{atoms,table}
 }
 fn value_in_union(&self,positions:&[usize],row:usize)->u64{let mut own=0;for(i,&j)in positions.iter().enumerate(){own|=((row>>j)&1)<<i;}self.table.bit(own)}
}
