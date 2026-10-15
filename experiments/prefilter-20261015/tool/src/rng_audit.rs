// Exact conservative symbolic certificate: abstract flags may overestimate
// randomness, but false means the Boolean output has no measurement variables.
#[derive(Clone,Copy)]struct Expr{kind:u8,a:u32,b:u32,random:bool}
struct Dag{nodes:Vec<Expr>,cache:std::collections::HashMap<(u8,u32,u32),u32>}
impl Dag{
 fn new()->Self{Self{nodes:vec![Expr{kind:0,a:0,b:0,random:false},Expr{kind:1,a:0,b:0,random:false}],cache:std::collections::HashMap::new()}}
 fn variable(&mut self,random:bool)->u32{let id=self.nodes.len()as u32;self.nodes.push(Expr{kind:2,a:id,b:0,random});id}
 fn complementary(&self,a:u32,b:u32)->bool{let x=self.nodes[a as usize];let y=self.nodes[b as usize];(x.kind==3&&x.a==1&&x.b==b)||(y.kind==3&&y.a==1&&y.b==a)}
 fn node(&mut self,k:u8,a:u32,b:u32)->u32{let key=(k,a,b);if let Some(id)=self.cache.get(&key){return *id;}let id=self.nodes.len()as u32;self.nodes.push(Expr{kind:k,a,b,random:self.nodes[a as usize].random||self.nodes[b as usize].random});self.cache.insert(key,id);id}
 fn factors(&self,k:u8,id:u32,out:&mut Vec<u32>){let n=self.nodes[id as usize];if n.kind==k&&out.len()<15{self.factors(k,n.a,out);self.factors(k,n.b,out);}else{out.push(id);}}
 fn xor(&mut self,a:u32,b:u32)->u32{if a==b{return 0;}if a==0{return b;}if b==0{return a;}let mut terms=Vec::with_capacity(20);self.factors(3,a,&mut terms);self.factors(3,b,&mut terms);terms.sort_unstable();let mut result=0;let mut i=0;while i<terms.len(){let x=terms[i];let mut j=i+1;while j<terms.len()&&terms[j]==x{j+=1;}if(j-i)%2==1&&x!=0{result=if result==0{x}else{let(a,b)=if result<x{(result,x)}else{(x,result)};self.node(3,a,b)};}i=j;}result}
 fn not(&mut self,a:u32)->u32{self.xor(1,a)}
 fn and(&mut self,a:u32,b:u32)->u32{if a==0||b==0{return 0;}if a==1{return b;}if b==1||a==b{return a;}let mut terms=Vec::with_capacity(20);self.factors(4,a,&mut terms);self.factors(4,b,&mut terms);terms.sort_unstable();terms.dedup();for(i,x)in terms.iter().enumerate(){if *x==0{return 0;}for y in &terms[i+1..]{if self.complementary(*x,*y){return 0;}}}let mut result=1;for x in terms{if x!=1{result=if result==1{x}else{let(a,b)=if result<x{(result,x)}else{(x,result)};self.node(4,a,b)};}}result}
}
fn audit_main(){
 let a:Vec<_>=std::env::args().collect();let ops=load_ops(&a[1]).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());let mut dag=Dag::new();let mut q=vec![0;nq as usize];let mut b=vec![0;nb as usize];for reg in &regs{for x in reg{let v=dag.variable(false);match x{QubitOrBit::Qubit(x)=>q[x.0 as usize]=v,QubitOrBit::Bit(x)=>b[x.0 as usize]=v}}}
 let mut stack=Vec::new();let mut base=1;let start=std::time::Instant::now();let mut measurements=0;
 for(i,o)in ops.iter().enumerate(){use OperationType::*;let c=if o.c_condition==quantum_ecc::circuit::NO_BIT{base}else{dag.and(base,b[o.c_condition.0 as usize])};let t=o.q_target.0 as usize;let bt=o.c_target.0 as usize;
  match o.kind{
   CCX=>{let v=dag.and(q[o.q_control1.0 as usize],q[o.q_control2.0 as usize]);let v=dag.and(v,c);q[t]=dag.xor(q[t],v);},
   CX=>{let v=dag.and(q[o.q_control1.0 as usize],c);q[t]=dag.xor(q[t],v);},X=>q[t]=dag.xor(q[t],c),
   Swap=>{let a=o.q_control1.0 as usize;let v=dag.xor(q[t],q[a]);let v=dag.and(v,c);q[t]=dag.xor(q[t],v);q[a]=dag.xor(q[a],v);},
   R|Hmr=>{let nc=dag.not(c);q[t]=dag.and(q[t],nc);if o.kind==Hmr{let random=dag.variable(true);measurements+=1;let old=dag.and(b[bt],nc);let new=dag.and(random,c);b[bt]=dag.xor(old,new);}},
   BitStore0=>{let nc=dag.not(c);b[bt]=dag.and(b[bt],nc);},BitStore1=>{let nc=dag.not(c);let old=dag.and(b[bt],nc);b[bt]=dag.xor(old,c);},BitInvert=>b[bt]=dag.xor(b[bt],c),
   PushCondition=>{stack.push(base);base=c;},PopCondition=>base=stack.pop().unwrap(),_=>{}
  }
  if i%500000==0{eprintln!("AUDIT_PROGRESS ops={i} nodes={} seconds={:.1}",dag.nodes.len(),start.elapsed().as_secs_f64());}
 }
 let mut dependency=0;let mut bits=0;for reg in &regs[..2]{for x in reg{let v=match x{QubitOrBit::Qubit(x)=>q[x.0 as usize],QubitOrBit::Bit(x)=>b[x.0 as usize]};dependency+=usize::from(dag.nodes[v as usize].random);bits+=1;}}
 println!("{{\"ops\":{},\"symbolic_nodes\":{},\"measurement_variables\":{measurements},\"output_bits\":{bits},\"unresolved_rng_dependent_bits\":{dependency},\"proved_value_rng_independent\":{},\"seconds\":{:.3},\"method\":\"exactBooleanDAG_ABC_identity_rules_only\"}}",ops.len(),dag.nodes.len(),dependency==0,start.elapsed().as_secs_f64());
}
#[cfg(test)]mod tests{
 use super::*;
 fn eval(d:&Dag,id:u32,assignment:u64)->bool{let n=d.nodes[id as usize];match n.kind{0=>false,1=>true,2=>(assignment>>(n.a-2))&1!=0,3=>eval(d,n.a,assignment)^eval(d,n.b,assignment),4=>eval(d,n.a,assignment)&eval(d,n.b,assignment),_=>unreachable!()}}
 #[test]fn conditional_compute_reset_is_zero(){let mut d=Dag::new();let c=d.variable(true);let a=d.variable(false);let b=d.variable(false);let ab=d.and(a,b);let q=d.and(ab,c);let nc=d.not(c);let cleared=d.and(q,nc);assert_eq!(cleared,0);let unguarded=d.and(ab,nc);assert!(d.nodes[unguarded as usize].random,"negativecontrol lost measurementdependency");}
 #[test]fn exact_boolean_rewrites_exhaustive(){let mut d=Dag::new();let vars:Vec<_>=(0..6).map(|i|d.variable(i>=3)).collect();let mut expressions=vars.clone();let mut seed=413283u64;for i in 0..300{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1);let a=expressions[(seed as usize)%expressions.len()];seed=seed.rotate_left(19);let b=expressions[(seed as usize)%expressions.len()];let and=i%3==0;let result=if and{d.and(a,b)}else{d.xor(a,b)};for bits in 0..64{let x=eval(&d,a,bits);let y=eval(&d,b,bits);assert_eq!(eval(&d,result,bits),if and{x&y}else{x^y});}expressions.push(result);}}
}
