// Sound value abstraction. Unknown means either Boolean value, independently.
#[derive(Clone,Copy,Debug,Default)]struct Tri{v:u64,u:u64}
impl Tri{
 fn known(v:u64)->Self{Self{v,u:0}}
 fn unknown()->Self{Self{v:0,u:u64::MAX}}
 #[inline(always)]fn not(self)->Self{Self{v:!self.v&!self.u,u:self.u}}
 #[inline(always)]fn and(self,b:Self)->Self{let one=self.v&b.v;let zero=(!self.v&!self.u)|(!b.v&!b.u);Self{v:one,u:!(one|zero)}}
 #[inline(always)]fn or(self,b:Self)->Self{let one=self.v|b.v;let zero=(!self.v&!self.u)&(!b.v&!b.u);Self{v:one,u:!(one|zero)}}
 #[inline(always)]fn xor(self,b:Self)->Self{let u=self.u|b.u;Self{v:(self.v^b.v)&!u,u}}
 #[inline(always)]fn mux(c:Self,a:Self,b:Self)->Self{let same=!(a.u|b.u)&!(a.v^b.v);let yes=c.v;let no=!c.v&!c.u;let known=(yes&!a.u)|(no&!b.u)|(c.u&same);Self{v:((yes&a.v)|(no&b.v)|(c.u&same&a.v))&known,u:!known}}
 fn contains(self,value:u64)->bool{(self.v^value)&!self.u==0}
}
struct TriSim{q:Vec<Tri>,b:Vec<Tri>}
struct CutQuery{site:usize,deleted:bool,survivor:usize,removed:usize}
impl TriSim{
 fn new(nq:usize,nb:usize)->Self{Self{q:vec![Tri::known(0);nq],b:vec![Tri::known(0);nb]}}
 fn set(&mut self,reg:&[QubitOrBit],value:U256,lane:usize){for(i,w)in reg.iter().enumerate(){let p=match w{QubitOrBit::Qubit(id)=>&mut self.q[id.0 as usize],QubitOrBit::Bit(id)=>&mut self.b[id.0 as usize]};p.v|=(value.bit(i)as u64)<<lane;}}
 fn apply(&mut self,p:&Compact,queries:&[CutQuery])->u64{let mut base=Tri::known(u64::MAX);let mut stack=Vec::new();let(mut next,mut possible)=(0,0);for(site,o)in p.ops.iter().enumerate(){let c=base.and(if o.c==u16::MAX{Tri::known(u64::MAX)}else{self.b[o.c as usize]});let(t,a,b,bt)=(o.t as usize,o.a as usize,o.b as usize,o.bt as usize);if next<queries.len()&&queries[next].site==site{let query=&queries[next];assert_eq!(o.k,13);let pred=if query.deleted{c.and(self.q[a]).and(self.q[b])}else{c.and(self.q[query.survivor]).and(self.q[query.removed].not())};possible|=pred.v|pred.u;next+=1;}match o.k{
  0|7|9|14=>{},3=>self.b[bt]=self.b[bt].xor(c),4=>self.b[bt]=self.b[bt].and(c.not()),5=>self.b[bt]=self.b[bt].or(c),
  6=>self.q[t]=self.q[t].xor(c),8=>self.q[t]=self.q[t].xor(c.and(self.q[a])),13=>self.q[t]=self.q[t].xor(c.and(self.q[a]).and(self.q[b])),
  10=>{let x=self.q[t];let y=self.q[a];self.q[t]=Tri::mux(c,y,x);self.q[a]=Tri::mux(c,x,y);},
  11|12=>{self.q[t]=self.q[t].and(c.not());if o.k==12{self.b[bt]=Tri::mux(c,Tri::unknown(),self.b[bt]);}},
  15=>{stack.push(base);base=base.and(self.b[o.c as usize]);},16=>base=stack.pop().unwrap(),_=>unreachable!()}}
  assert!(stack.is_empty());assert_eq!(next,queries.len());possible}
}
fn abstract_tests(){let states=[Tri::known(0),Tri::known(u64::MAX),Tri::unknown()];let mut checks=0;
 for a in states{for b in states{for c in states{for av in [0,u64::MAX]{for bv in [0,u64::MAX]{for cv in [0,u64::MAX]{if a.contains(av)&&b.contains(bv)&&c.contains(cv){assert!(a.and(b).contains(av&bv));assert!(a.or(b).contains(av|bv));assert!(a.xor(b).contains(av^bv));assert!(a.not().contains(!av));assert!(Tri::mux(c,a,b).contains((cv&av)|(!cv&bv)));checks+=5;}}}}}}}
 println!("ABSTRACT_PRIMITIVE_CONTAINMENT checks={checks}");}
