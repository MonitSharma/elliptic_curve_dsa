// Separate measurement polynomials from arbitrary input-only Boolean functions.
// A capped expression becomes a NEW unconstrained RNG-tainted symbol. This may
// lose a proof, but cannot prove randomness-independence from unknown semantics.
#[derive(Clone,PartialEq,Eq)]struct Poly(Vec<(Vec<u32>,u32)>);
struct Coeff { dag:Dag, next:u32, capped:usize, cap:usize }
impl Coeff {
 fn constant(x:u32)->Poly{if x==0{Poly(Vec::new())}else{Poly(vec![(vec![],x)])}}
 fn var(&mut self)->Poly{let n=self.next;self.next+=1;Poly(vec![(vec![n],1)])}
 fn unknown(&mut self)->Poly{self.capped+=1;self.var()}
 fn xor(&mut self,a:&Poly,b:&Poly)->Poly{let mut terms=std::collections::BTreeMap::<Vec<u32>,u32>::new();for(k,v)in a.0.iter().chain(&b.0){let old=terms.get(k).copied().unwrap_or(0);let new=self.dag.xor(old,*v);if new==0{terms.remove(k);}else{terms.insert(k.clone(),new);}}if terms.len()>self.cap{return self.unknown();}Poly(terms.into_iter().collect())}
 fn and(&mut self,a:&Poly,b:&Poly)->Poly{
  if a.0.is_empty()||b.0.is_empty(){return Self::constant(0);}if a.0.len()*b.0.len()>self.cap*self.cap{return self.unknown();}
  let mut terms=std::collections::BTreeMap::<Vec<u32>,u32>::new();for(ka,va)in&a.0{for(kb,vb)in&b.0{let coefficient=self.dag.and(*va,*vb);if coefficient==0{continue;}let mut key=ka.clone();key.extend(kb);key.sort_unstable();key.dedup();if key.len()>16{return self.unknown();}let old=terms.get(&key).copied().unwrap_or(0);let coefficient=self.dag.xor(old,coefficient);if coefficient==0{terms.remove(&key);}else{terms.insert(key,coefficient);}}}
  if terms.len()>self.cap{return self.unknown();}Poly(terms.into_iter().collect())
 }
 fn not(&mut self,a:&Poly)->Poly{self.xor(a,&Self::constant(1))}
}
fn coeff_main(){
 let a:Vec<_>=std::env::args().collect();let ops=load_ops(&a[1]).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());let cap=a.get(2).map(|s|s.parse().unwrap()).unwrap_or(32);let mut alg=Coeff{dag:Dag::new(),next:0,capped:0,cap};
 let mut q=vec![Coeff::constant(0);nq as usize];let mut b=vec![Coeff::constant(0);nb as usize];for reg in&regs{for x in reg{let id=alg.dag.variable(false);let p=Coeff::constant(id);match x{QubitOrBit::Qubit(x)=>q[x.0 as usize]=p,QubitOrBit::Bit(x)=>b[x.0 as usize]=p}}}
 let mut stack=Vec::new();let mut base=Coeff::constant(1);let start=std::time::Instant::now();let mut measurements=0;
 for(i,o)in ops.iter().enumerate(){use OperationType::*;let c=if o.c_condition==quantum_ecc::circuit::NO_BIT{base.clone()}else{alg.and(&base,&b[o.c_condition.0 as usize])};let t=o.q_target.0 as usize;let bt=o.c_target.0 as usize;
  match o.kind{
   CCX=>{let v=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);let v=alg.and(&v,&c);q[t]=alg.xor(&q[t],&v);},
   CX=>{let v=alg.and(&q[o.q_control1.0 as usize],&c);q[t]=alg.xor(&q[t],&v);},X=>q[t]=alg.xor(&q[t],&c),
   Swap=>{let a=o.q_control1.0 as usize;let v=alg.xor(&q[t],&q[a]);let v=alg.and(&v,&c);q[t]=alg.xor(&q[t],&v);q[a]=alg.xor(&q[a],&v);},
   R|Hmr=>{let nc=alg.not(&c);q[t]=alg.and(&q[t],&nc);if o.kind==Hmr{let random=alg.var();measurements+=1;let old=alg.and(&b[bt],&nc);let new=alg.and(&random,&c);b[bt]=alg.xor(&old,&new);}},
   BitStore0=>{let nc=alg.not(&c);b[bt]=alg.and(&b[bt],&nc);},BitStore1=>{let nc=alg.not(&c);let old=alg.and(&b[bt],&nc);b[bt]=alg.xor(&old,&c);},BitInvert=>b[bt]=alg.xor(&b[bt],&c),
   PushCondition=>{stack.push(base);base=c;},PopCondition=>base=stack.pop().unwrap(),_=>{}
  }
  if i%500000==0{eprintln!("COEFF_PROGRESS ops={i} input_nodes={} caps={} symbols={} seconds={:.1}",alg.dag.nodes.len(),alg.capped,alg.next,start.elapsed().as_secs_f64());}
 }
 let(mut dependency,mut bits)=(0,0);for reg in&regs[..2]{for x in reg{let p=match x{QubitOrBit::Qubit(x)=>&q[x.0 as usize],QubitOrBit::Bit(x)=>&b[x.0 as usize]};dependency+=usize::from(p.0.iter().any(|(k,_)|!k.is_empty()));bits+=1;}}
 println!("{{\"ops\":{},\"input_only_DAG_nodes\":{},\"measurement_variables\":{measurements},\"opaque_RNG_unknowns\":{},\"term_cap\":{cap},\"output_bits\":{bits},\"unresolved_rng_dependent_bits\":{dependency},\"proved_value_rng_independent\":{},\"seconds\":{:.3},\"method\":\"exactRNGpolynomials_inputonlyDAGcoefficients\"}}",ops.len(),alg.dag.nodes.len(),alg.capped,dependency==0,start.elapsed().as_secs_f64());
}
#[cfg(test)]mod coeff_tests{
 use super::*;
 #[test]fn rng_coefficient_cancellation_and_taint(){let mut a=Coeff{dag:Dag::new(),next:0,capped:0,cap:32};let input=a.dag.variable(false);let f=Coeff::constant(input);let m=a.var();let guarded=a.and(&m,&f);let nm=a.not(&m);let killed=a.and(&guarded,&nm);assert!(killed.0.is_empty());let unguarded=a.and(&nm,&f);assert!(unguarded.0.iter().any(|(k,_)|!k.is_empty()));a.cap=0;let unknown=a.xor(&f,&m);assert_eq!(a.capped,1);assert!(unknown.0.iter().any(|(k,_)|!k.is_empty()));}
}
