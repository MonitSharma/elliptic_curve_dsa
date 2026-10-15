// Diagnostic model of truncated rails and ideal modular payloads. Never rejects
// a nonce by itself: unsupported payload effects require exact confirmation.
use alloy_primitives::U512;
#[derive(Clone,Copy,PartialEq,Eq)]struct I512{lo:U256,hi:i64}
impl I512{#[inline(always)]fn is_negative(self)->bool{self.hi<0}}
impl std::ops::Add for I512{type Output=Self;#[inline(always)]fn add(self,b:Self)->Self{let(lo,c)=self.lo.overflowing_add(b.lo);Self{lo,hi:self.hi+b.hi+i64::from(c)}}}
impl std::ops::Sub for I512{type Output=Self;#[inline(always)]fn sub(self,b:Self)->Self{let(lo,c)=self.lo.overflowing_sub(b.lo);Self{lo,hi:self.hi-b.hi-i64::from(c)}}}
impl std::ops::Neg for I512{type Output=Self;#[inline(always)]fn neg(self)->Self{let(lo,c)=(!self.lo).overflowing_add(U256::from(1));Self{lo,hi:!self.hi+i64::from(c)}}}
impl std::fmt::Display for I512{fn fmt(&self,f:&mut std::fmt::Formatter)->std::fmt::Result{if self.hi<0{write!(f,"-{}",(-*self).lo)}else{write!(f,"{}",self.lo)}}}
struct WalkModel { steps:Vec<[usize;5]>, anchors:Vec<usize>, p:U256, ps:I512 }
#[derive(Clone,Copy)]
struct Letter { signs:[bool;2], forced:usize, choice:bool, extra:usize }
#[inline(always)]fn ar(x:I512,n:usize)->I512{if n==0{return x;}assert!(n<64);I512{lo:(x.lo>>n)|(U256::from(x.hi as u64)<<(256-n)),hi:x.hi>>n}}
#[inline(always)]fn sx(x:I512,w:usize)->I512{if w>256{let bits=w-256;let mask=(1i64<<bits)-1;let h=x.hi&mask;I512{lo:x.lo,hi:if h&(1<<(bits-1))!=0{h|!mask}else{h}}}else if w==256{I512{lo:x.lo,hi:if x.lo.bit(255){-1}else{0}}}else{let mask=(U256::from(1)<<w)-U256::from(1);let lo=x.lo&mask;if lo.bit(w-1){I512{lo:lo|!mask,hi:-1}}else{I512{lo,hi:0}}}}
#[inline(always)]fn pos(x:U256)->I512{I512{lo:x,hi:0}}
#[inline(always)]fn bit(x:I512,n:usize)->bool{if n<256{x.lo.bit(n)}else{(x.hi>>(n-256))&1!=0}}
impl WalkModel {
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
 fn choice(&self,t:I512,b:I512,tw:usize,bw:usize,tick:usize,before:Option<I512>,forced:bool)->(bool,usize){
  let dq=bit(t,1)^bit(b,1);let z2=bit(t,2)^bit(b,2)^dq;let z3=bit(t,3)^bit(b,3)^dq;let z4=bit(t,4)^bit(b,4)^dq;
  let eq=t.is_negative()^b.is_negative()^dq;let a1=!z2&!z3;let a2=a1&!z4;let mut out=dq^true^a2;let mut v3=false;
  if tick==0{out^=eq&z2;}else if let Some(old)=before{
   let y=self.window(t,tw,tick)>2*self.window(b,bw,tick);
   let not_flipped=old.is_negative()==t.is_negative();let added=!(old.is_negative()^b.is_negative()^forced);
   let veto=eq&(y^not_flipped);out^=veto&z2;v3=veto&!z2&z3&added;out^=v3;
  }else{let y=self.window(t,tw,tick)>4*self.window(b,bw,tick);out^=eq&!y&z2;}
  let k2=!z2^a2^v3;let dsel=out^dq;let k1=dsel^!z2^a1^v3;(out,usize::from(k1)+2*usize::from(k2))
 }
 fn walk(&self,d:U256,forward:bool,payload:Option<U256>)->(U256,[I512;2],Option<usize>){
  let r0=if d.bit(0){pos(d)}else{pos(d)-self.ps};let mut r=[r0,ar(r0+if bit(r0,1){self.ps}else{-self.ps},1)];
  let trace=std::env::var_os("WALK_TRACE").is_some();let initial=payload.unwrap_or(U256::from(1));let mut c=[initial,self.half(initial)];let mut tape=Vec::with_capacity(self.steps.len());let mut overflow=None;
  for(tick,&[w,n0,n1,n2,nb])in self.steps.iter().enumerate(){
   let ti=tick%2;let si=1-ti;let wn=self.steps[(tick+1).min(self.steps.len()-1)][0];let fused=forward&&tick>=42;
   let bw=|n:usize|if fused{n.min(w).min(wn)}else{n};let payload_before=c;let forced=if tick+1<self.steps.len(){2}else{0};let mut signs=[false;2];let mut before=None;
   for(j,(nk,nnext))in[(n0,n1),(n1,n2)].iter().copied().take(forced).enumerate(){
    for(side,width)in[(ti,nk),(si,bw(nk))]{let v=sx(r[side],width);if v!=r[side]&&overflow.is_none(){overflow=Some(tick);}r[side]=v;}
    if trace&&tick==0{eprintln!("FORCED_BEFORE {j} {} {}",r[ti],r[si]);}
    let old=r[ti];let sign=bit(r[ti],1)^bit(r[si],1);let v=ar(r[ti]+if sign{-r[si]}else{r[si]},1);r[ti]=sx(v,nk-1);if r[ti]!=v&&overflow.is_none(){overflow=Some(tick);}
    if forward{c[ti]=self.half(if sign{self.sub(c[ti],c[si])}else{self.add(c[ti],c[si])});}
    signs[j]=sign;if j==1{before=Some(old);}
    if fused&&j==0{r[ti]=sx(r[ti],(nk-1).min(nnext));r[si]=sx(r[si],bw(nk).min(w).min(wn));}
   }
   r[ti]=sx(r[ti],n2);r[si]=sx(r[si],bw(n2));let(sign,extra)=self.choice(r[ti],r[si],n2.max(6),bw(n2).max(6),tick,before,signs[1]);
   let v=ar(r[ti]+if sign{-r[si]}else{r[si]},1);r[ti]=sx(v,n2-1);if r[ti]!=v&&overflow.is_none(){overflow=Some(tick);}
   if forward{c[ti]=self.half(if sign{self.sub(c[ti],c[si])}else{self.add(c[ti],c[si])});for _ in 0..extra{c[ti]=self.half(c[ti]);}}
   if forward&&payload.is_some()&&tick+1<self.steps.len(){let count=self.fold_c(payload_before[ti],payload_before[si],&[signs[0],signs[1],sign],extra,tick,false);let w=if tick<=99{57}else{56};c[ti]=self.correct(c[ti],count,w-3-extra);}
   let v=ar(sx(r[ti],nb),extra);r[ti]=sx(v,nb-extra);for side in 0..2{let v=sx(r[side],wn);if v!=r[side]&&overflow.is_none(){overflow=Some(tick);}r[side]=v;}
   if trace{eprintln!("TRACE {tick} {} {} {} {} {} {}",r[0],r[1],signs[0],signs[1],sign,extra);}
   tape.push(Letter{signs,forced,choice:sign,extra});
  }
  if forward{return(if r[0].is_negative(){self.neg(c[0])}else{c[0]},r,overflow);}
  c=[if r[0].is_negative(){self.neg(initial)}else{initial},if r[1].is_negative(){self.neg(initial)}else{initial}];
  for tick in(0..tape.len()).rev(){let ti=tick%2;let si=1-ti;let l=tape[tick];let payload_before=c;for _ in 0..l.extra{c[ti]=self.add(c[ti],c[ti]);}for s in std::iter::once(l.choice).chain(l.signs[..l.forced].iter().rev().copied()){let d=self.add(c[ti],c[ti]);c[ti]=if s{self.add(d,c[si])}else{self.sub(d,c[si])};}if payload.is_some()&&(1..127).contains(&tick){let count=self.fold_c(payload_before[ti],payload_before[si],&[l.signs[0],l.signs[1],l.choice],l.extra,tick,true);c[ti]=self.correct(c[ti],count,56);}}
  (self.add(c[1],c[1]),r,overflow)
 }
 fn correct(&self,ideal:U256,c:i64,shift:usize)->U256{if c==0{return ideal;}let delta=U256::from(c.unsigned_abs())<<shift;if c>0{self.sub(ideal,delta)}else{self.add(ideal,delta)}}
 fn fold_c(&self,a:U256,b:U256,signs:&[bool;3],extra:usize,tick:usize,reverse:bool)->i64{
  let shift=3+extra;let mask=(1i64<<shift)-1;let initial=if reverse{(a<<shift)|(a>>(256-shift))}else{a};
  let mut x=U512::from(initial);let mut nm=0i64;
  for(i,si)in signs.iter().enumerate(){let s=*si^reverse;nm+=i64::from(s)<<i;let source=if s{!b}else{b};x+=U512::from(source)<<i;}
  let e=(x>>256usize).as_limbs()[0]as i64;let low=x.as_limbs()[0];let fminus1=4294968272i64;
  let m=if reverse{initial.as_limbs()[0]as i64&mask}else{let inv=[0i64,1,1,1,1,17,49][shift];let aa=(low as i64&mask)+e+(e-nm)*fminus1;aa.wrapping_mul(inv)&mask};
  let c=e+(e-nm+if reverse{m}else{-m})*fminus1;let w=if !reverse&&tick<=99{57}else{56};
  (((low&((1u64<<w)-1))as i64)+c).div_euclid(1i64<<w)
 }
 fn predict(&self,t:(U256,U256),o:(U256,U256),expected:(U256,U256),folds:bool)->(bool,bool){
  let d=self.sub(t.0,o.0);let y=self.sub(t.1,o.1);let(co,_,of1)=self.walk(d,true,if folds{Some(y)}else{None});let slope=if folds{co}else{co.mul_mod(y,self.p)};
  let square=self.sub(self.add(t.0,self.add(o.0,o.0)),slope.mul_mod(slope,self.p));let(cm,_,of2)=self.walk(square,false,if folds{Some(slope)}else{None});
  let x=self.sub(o.0,square);let y=self.sub(if folds{cm}else{cm.mul_mod(slope,self.p)},o.1);((x,y)!=expected,of1.is_some()||of2.is_some())
 }
}
fn native_main(){
 let a:Vec<_>=std::env::args().collect();let model=WalkModel::new(&a[1]);let rows=std::fs::read_to_string(&a[2]).unwrap();let mut out=std::io::BufWriter::new(File::create(&a[3]).unwrap());let(mut tp,mut fp,mut tn,mut fnc,mut warnings,mut n)=(0usize,0usize,0usize,0usize,0usize,0usize);let start=std::time::Instant::now();let mut model_seconds=0f64;
 for row in rows.lines().skip(1){let f:Vec<_>=row.split('\t').collect();let v=|i|U256::from_str_radix(f[i],16).unwrap();let inputs=((v(4),v(5)),(v(6),v(7)),(v(8),v(9)));let model_start=std::time::Instant::now();let(pred,warn)=model.predict(inputs.0,inputs.1,inputs.2,a.get(4).map(|x|x=="--folds").unwrap_or(false));model_seconds+=model_start.elapsed().as_secs_f64();let truth=f[10]=="1";match(truth,pred){(true,true)=>tp+=1,(false,true)=>fp+=1,(false,false)=>tn+=1,(true,false)=>fnc+=1};warnings+=usize::from(warn);n+=1;if truth||pred||warn{writeln!(out,"{{\"batch\":{},\"lane\":{},\"value\":{},\"predicted_wrong_value\":{pred},\"rail_warning\":{warn}}}",f[0],f[1],usize::from(truth)).unwrap();}}
 println!("{{\"shots\":{n},\"tp\":{tp},\"fp\":{fp},\"tn\":{tn},\"fn\":{fnc},\"rail_warnings\":{warnings},\"microseconds_per_shot\":{:.3},\"model_microseconds_per_shot\":{:.3},\"status\":\"DIAGNOSTIC_ONLY_REQUIRES_EXACT_CONFIRMATION\"}}",start.elapsed().as_secs_f64()*1e6/n as f64,model_seconds*1e6/n as f64);
}
#[cfg(test)]mod signed_tests{
 use super::*;
 fn raw(x:I512)->U512{let v=U512::from(x.lo)|(U512::from(x.hi as u64)<<256);if x.hi<0{v|(U512::MAX<<320)}else{v}}
 #[test]fn compact_signed_arithmetic_against_independent512bit_words(){
  let mut seed=289344239u64;
  for _ in 0..256{let mut limbs=[0u64;4];for l in&mut limbs{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1);*l=seed;}let a=I512{lo:U256::from_limbs(limbs),hi:(seed%7)as i64-3};let b=I512{lo:!a.lo,hi:2};
   assert_eq!(raw(a+b),raw(a).overflowing_add(raw(b)).0);assert_eq!(raw(a-b),raw(a).overflowing_sub(raw(b)).0);assert_eq!(raw(-a),U512::ZERO.overflowing_sub(raw(a)).0);
   for n in 0..=6{let expected=if n==0{raw(a)}else{(raw(a)>>n)|if a.is_negative(){U512::MAX<<(512-n)}else{U512::ZERO}};assert_eq!(raw(ar(a,n)),expected);}
   for width in 3usize..=259{let mask:U512=(U512::from(1)<<width)-U512::from(1);let low=raw(a)&mask;let expected=if low.bit(width-1){low|!mask}else{low};assert_eq!(raw(sx(a,width)),expected);}
  }
 }
}
