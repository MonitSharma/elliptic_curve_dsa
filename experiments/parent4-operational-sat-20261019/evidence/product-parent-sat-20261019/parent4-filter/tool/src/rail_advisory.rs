// Diagnostic model of truncated rails and ideal modular payloads. Never rejects
// a nonce by itself: unsupported payload effects require exact confirmation.

#[derive(Clone,Copy,PartialEq,Eq)]struct I512{lo:U256,hi:i64}
impl I512{#[inline(always)]fn is_negative(self)->bool{self.hi<0}}
impl std::ops::Add for I512{type Output=Self;#[inline(always)]fn add(self,b:Self)->Self{let(lo,c)=self.lo.overflowing_add(b.lo);Self{lo,hi:self.hi+b.hi+i64::from(c)}}}
impl std::ops::Sub for I512{type Output=Self;#[inline(always)]fn sub(self,b:Self)->Self{let(lo,c)=self.lo.overflowing_sub(b.lo);Self{lo,hi:self.hi-b.hi-i64::from(c)}}}
impl std::ops::Neg for I512{type Output=Self;#[inline(always)]fn neg(self)->Self{let(lo,c)=(!self.lo).overflowing_add(U256::from(1));Self{lo,hi:!self.hi+i64::from(c)}}}
impl std::fmt::Display for I512{fn fmt(&self,f:&mut std::fmt::Formatter)->std::fmt::Result{if self.hi<0{write!(f,"-{}",(-*self).lo)}else{write!(f,"{}",self.lo)}}}
struct RailAdvisory { steps:Vec<[usize;5]>, anchors:Vec<usize>, p:U256, ps:I512 }
#[derive(Clone,Copy)]
struct Letter { signs:[bool;2], forced:usize, choice:bool, extra:usize }
const fn rail_masks()->[[u64;4];257]{let mut out=[[0;4];257];let mut w=0;while w<=256{let mut j=0;while j<4{let n=if w>64*j{w-64*j}else{0};out[w][j]=if n>=64{u64::MAX}else{(1u64<<n)-1};j+=1;}w+=1;}out}
const SIGN_MASKS:[[u64;4];257]=rail_masks();
#[inline(always)]fn ar(x:I512,n:usize)->I512{if n==0{return x;}let l=x.lo.as_limbs();I512{lo:U256::from_limbs([(l[0]>>n)|(l[1]<<(64-n)),(l[1]>>n)|(l[2]<<(64-n)),(l[2]>>n)|(l[3]<<(64-n)),(l[3]>>n)|((x.hi as u64)<<(64-n))]),hi:x.hi>>n}}
#[inline(always)]fn sx(x:I512,w:usize)->I512{if w>256{let bits=w-256;let m=(1i64<<bits)-1;let h=x.hi&m;return I512{lo:x.lo,hi:if h&(1<<(bits-1))!=0{h|!m}else{h}};}let l=x.lo.as_limbs();let m=SIGN_MASKS[w];let fill=0u64.wrapping_sub((l[(w-1)/64]>>((w-1)%64))&1);I512{lo:U256::from_limbs([(l[0]&m[0])|(fill&!m[0]),(l[1]&m[1])|(fill&!m[1]),(l[2]&m[2])|(fill&!m[2]),(l[3]&m[3])|(fill&!m[3])]),hi:fill as i64}}
#[inline(always)]fn pos(x:U256)->I512{I512{lo:x,hi:0}}
#[inline(always)]fn bit(x:I512,n:usize)->bool{if n<256{x.lo.bit(n)}else{(x.hi>>(n-256))&1!=0}}
impl RailAdvisory {
 fn new(root:&str)->Self {
  let steps=std::fs::read_to_string(format!("{root}/steps.txt")).unwrap().lines().filter(|l|!l.is_empty()&&!l.starts_with('#')).map(|l|{let v:Vec<usize>=l.split_whitespace().map(|x|x.parse().unwrap()).collect();[v[0],v[1],v[2],v[3],v[4]]}).collect();
  let anchors=std::fs::read_to_string(format!("{root}/anchors.txt")).unwrap().split(',').filter_map(|x|x.trim().parse().ok()).collect();
  let p=secp256k1().modulus;Self{steps,anchors,p,ps:pos(p)}
 }
 #[inline(always)]fn add(&self,a:U256,b:U256)->U256{let(s,over)=a.overflowing_add(b);if over{s+U256::from(4294968273u64)}else if s>=self.p{s-self.p}else{s}}
 #[inline(always)]fn sub(&self,a:U256,b:U256)->U256{if a>=b{a-b}else{self.p-(b-a)}}
 #[inline(always)]fn half(&self,a:U256)->U256{if a.bit(0){(a>>1)+(self.p>>1)+U256::from(1)}else{a>>1}}
 #[inline(always)]fn neg(&self,a:U256)->U256{if a.is_zero(){a}else{self.p-a}}
 fn window(&self,x:I512,width:usize,tick:usize)->u64 {
  let mut length=22;for(start,l)in[(1,13),(6,17),(11,22),(90,19),(100,17),(112,15),(118,13),(124,11)]{if tick>=start{length=l;}}
  let k=length-2;let low=self.anchors[tick].saturating_sub(k);
  if width-1<=low{return 0;}
  let raw=if x.is_negative(){!x.lo}else{x.lo};let rawhi=if x.is_negative(){!x.hi}else{x.hi}as u64;
  let mut result=if low<256{(raw>>low).as_limbs()[0]}else{rawhi>>(low-256)};
  if low<256&&256-low<64{result|=rawhi<<(256-low);}
  let count=(k+2).min(width-1-low);result&((1u64<<count)-1)
 }
 fn choice(&self,t:I512,b:I512,tw:usize,bw:usize,tick:usize,before:Option<I512>,forced:bool,old_source:Option<bool>)->(bool,usize){
  let dq=bit(t,1)^bit(b,1);let z2=bit(t,2)^bit(b,2)^dq;let z3=bit(t,3)^bit(b,3)^dq;let z4=bit(t,4)^bit(b,4)^dq;
  let eq=t.is_negative()^b.is_negative()^dq;let a1=!z2&!z3;let a2=a1&!z4;let mut out=dq^true^a2;let mut v3=false;
  if tick==0{out^=eq&z2;}else if let Some(old)=before{
   let y=self.window(t,tw,tick)>2*self.window(b,bw,tick);
   let old_source=old_source.unwrap_or(b.is_negative());let not_flipped=!(old.is_negative()^t.is_negative()^old_source^b.is_negative());let added=!(old.is_negative()^old_source^forced);
   let veto=eq&(y^not_flipped);out^=veto&z2;v3=veto&!z2&z3&added;out^=v3;
  }else{let y=self.window(t,tw,tick)>4*self.window(b,bw,tick);out^=eq&!y&z2;}
  let k2=!z2^a2^v3;let dsel=out^dq;let k1=dsel^!z2^a1^v3;(out,usize::from(k1)+2*usize::from(k2))
 }

 // Heuristic ONLY: no return value is a rejection certificate.
 fn rail_walk(&self,d:U256,divide:bool)->(bool,bool){
  let r0=if d.bit(0){pos(d)}else{pos(d)-self.ps};let mut r=[r0,ar(r0+if bit(r0,1){self.ps}else{-self.ps},1)];let mut overflow=false;
  for(tick,&[w,n0,n1,n2,nb])in self.steps.iter().enumerate(){
   let ti=tick%2;let si=1-ti;let wn=self.steps[(tick+1).min(self.steps.len()-1)][0];let fused=divide&&(42..131).contains(&tick);let bw=|n:usize|if fused{n.min(w).min(wn)}else{n};let forced=if tick+1<self.steps.len(){2}else{0};let mut before=None;let mut lastsign=false;let mut captured=None;
   for(j,(nk,nnext))in[(n0,n1),(n1,n2)].iter().copied().take(forced).enumerate(){
    for(side,width)in[(ti,nk),(si,bw(nk))]{let v=sx(r[side],width);overflow|=v!=r[side];r[side]=v;}
    let old=r[ti];let sign=bit(r[ti],1)^bit(r[si],1);let v=ar(r[ti]+if sign{-r[si]}else{r[si]},1);r[ti]=sx(v,nk-1);overflow|=r[ti]!=v;
    if j==1{before=Some(old);lastsign=sign;if tick!=0{let tw=nk-1;let sw=bw(nk).min(tw);captured=Some(self.choice(r[ti],sx(r[si],sw),tw.max(6),sw.max(6),tick,Some(old),sign,Some(r[si].is_negative())));}}
    if fused&&j==0{r[ti]=sx(r[ti],(nk-1).min(nnext));r[si]=sx(r[si],bw(nk).min(w).min(wn));}
   }
   r[ti]=sx(r[ti],n2);r[si]=sx(r[si],bw(n2));let(sign,extra)=captured.unwrap_or_else(||self.choice(r[ti],r[si],n2.max(6),bw(n2).max(6),tick,before,lastsign,None));
   let v=ar(r[ti]+if sign{-r[si]}else{r[si]},1);r[ti]=sx(v,n2-1);overflow|=r[ti]!=v;
   r[ti]=sx(ar(sx(r[ti],nb),extra),nb-extra);for side in 0..2{let v=sx(r[side],wn);overflow|=v!=r[side];r[side]=v;}
   if fused&&tick<130{let next=self.steps[tick+1];let wnn=self.steps[(tick+2).min(self.steps.len()-1)][0];r[ti]=sx(r[ti],next[1].min(next[0]).min(wnn));}
  }
  let unit=|v:I512|v==pos(U256::from(1))||v==-pos(U256::from(1));(!unit(r[0])||!unit(r[1]),overflow)
 }
 fn flags(&self,t:(U256,U256),o:(U256,U256),expected:(U256,U256))->u8{let(a,b)=self.rail_walk(self.sub(t.0,o.0),true);let(c,d)=self.rail_walk(self.sub(o.0,expected.0),false);u8::from(a||c)|(u8::from(b||d)<<1)}
}
