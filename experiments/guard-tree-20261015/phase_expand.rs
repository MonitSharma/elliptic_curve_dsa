// Exact quadratic/cubic phase substitution; every original MR stays aligned.
fn phase_poly(fa:&(Vec<u32>,bool),fb:&(Vec<u32>,bool),z:Option<u32>,cc:u32)->Vec<L>{
 let terms=|f:&(Vec<u32>,bool)|{let mut v:Vec<Vec<u32>>=f.0.iter().map(|&w|vec![w]).collect();if f.1{v.push(vec![]);}v};
 let mut poly=HashSet::<Vec<u32>>::new();for x in terms(fa){for y in terms(fb){let mut m=x.clone();m.extend(y);if let Some(z)=z{m.push(z);}m.sort_unstable();m.dedup();if !poly.remove(&m){poly.insert(m);}}}
 let mut poly:Vec<_>=poly.into_iter().collect();poly.sort();poly.iter().map(|m|match m.as_slice(){[]=>L{kind:K_NEG,c2:NQ,c1:NQ,t:NQ,ct:NQ,cc,rt:NQ},[x]=>op(K_Z,NQ,*x,cc),[x,y]=>op(K_CZ,*x,*y,cc),[x,y,z]=>L{kind:K_CCZ,c2:*x,c1:*y,t:*z,ct:NQ,cc,rt:NQ},_=>unreachable!()}).collect()
}
pub fn phase_expand(ops:Vec<Op>)->Vec<Op>{
 let l:Vec<_>=ops.iter().map(to_l).collect();drop(ops);let a=analyze(&l);let mut ed=Edits::new();
 let mut reads=HashMap::<u32,Vec<usize>>::new();for(j,o)in l.iter().enumerate(){let qs=match o.kind{K_CCX=>[o.c1,o.c2,NQ],K_CX=>[o.c1,NQ,NQ],K_Z=>[o.t,NQ,NQ],K_CZ=>[o.c1,o.t,NQ],K_CCZ=>[o.c1,o.c2,o.t],_=>[NQ;3]};for q in qs{if q!=NQ{reads.entry(q).or_default().push(j);}}}
 let mut kept=Vec::<(u32,u32,u32,Vec<(u32,u32)>)>::new();let mut selected=0;let mut predicted=0.0;
 for(ci,c)in a.contribs.iter().enumerate(){
  if c.ctx!=0||c.swapped||c.end_kind!=E_HMR||!c.end_sole{continue;}let(p,e)=(c.op as usize,c.end_op as usize);if l[p].cc!=NQ||l[e].cc!=NQ||a.opctx[e]!=0||ed.touched(c.op){continue;}
  let Some(all)=reads.get(&c.wire)else{continue;};let first=all.partition_point(|&j|j<=p);let last=all.partition_point(|&j|j<e);let mut rr=all[first..last].to_vec();rr.dedup();if rr.is_empty()||rr.iter().any(|&j|!matches!(l[j].kind,K_Z|K_CZ)||ed.touched(j as u32)){continue;}
  if(p+1..e).any(|j|{let o=l[j];o.t==c.wire&&matches!(o.kind,K_X|K_CX|K_CCX|K_R|K_HMR|K_SWAP)||o.kind==K_SWAP&&o.c1==c.wire}){continue;}
  let Some(fixes)=a.fixcz.get(&c.end_bit)else{continue;};let fixes:Vec<_>=fixes.iter().filter(|&&(j,x,y)|((x==c.va&&y==c.vb)||(x==c.vb&&y==c.va))&&a.cx.sets[a.opctx[j as usize]as usize]==vec![c.end_bit]).collect();if fixes.len()!=1||ed.touched(fixes[0].0){continue;}let fix=fixes[0].0;
  let affine=forms_at(&l,&a,p,&[l[p].c1,l[p].c2],&rr);let mut replacements=vec![];let mut uses=vec![];let mut bad=false;let mut cost=0.0;
  for(ri,&at)in rr.iter().enumerate(){
   let alias=a.guard_readhold.get(&(ci as u32,at as u32)).copied().filter(|&(x,y)|x!=c.wire&&y!=c.wire);
   let fs=if let Some((x,y))=alias{vec![(vec![x],false),(vec![y],false)]}else if let Some(ref f)=affine{f[ri].clone()}else{bad=true;break;};
   if fs.iter().any(|f|f.0.contains(&c.wire)){bad=true;break;}let z=if l[at].kind==K_CZ{let other=if l[at].c1==c.wire{l[at].t}else{l[at].c1};if other==c.wire{None}else{Some(other)}}else{None};
   let out=phase_poly(&fs[0],&fs[1],z,l[at].cc);cost+=out.iter().filter(|o|o.kind==K_CCZ).count()as f64*0.5f64.powi(a.cx.sets[a.opctx[at]as usize].len()as i32);
   for f in &fs{for &q in &f.0{uses.push((q,at as u32));}}if let Some(z)=z{uses.push((z,at as u32));}replacements.push((at as u32,out));
  }
  if bad||cost>=1.0{continue;}
  if uses.iter().any(|&(w,t)|kept.iter().any(|&(q,s,z,_)|w==q&&s<t&&t<=z))||kept.iter().any(|(_,_,_,u)|u.iter().any(|&(w,t)|w==c.wire&&c.op<t&&t<=fix)){continue;}
  ed.delete.insert(c.op);ed.delete.insert(fix);for(at,out)in replacements{ed.replace.insert(at,out);}kept.push((c.wire,c.op,fix,uses));selected+=1;predicted+=1.0-cost;
  println!("PHASE_EXPAND_SITE producer={} erase={} fix={fix} wire={} reads={} estimated_saving={}",c.op,c.end_op,c.wire,rr.len(),1.0-cost);
 }
 println!("PHASE_EXPAND_SUMMARY selected={selected} predicted_saving={predicted} quantum_width_unchanged=true measurements_unchanged=true");ed.apply(&l).iter().map(from_l).collect()
}
#[cfg(test)]mod phase_expand_tests{
 use super::*;use quantum_ecc::{circuit::analyze_ops,sim::Simulator};
 struct Word(u64);impl sha3::digest::XofReader for Word{fn read(&mut self,b:&mut[u8]){b.copy_from_slice(&self.0.to_le_bytes());}}
 #[test]fn phase_expand_all_basis_and_mr(){
  let mut p=vec![];let mut o=Op::empty();o.kind=K::Register;o.r_target=RegisterId(0);p.push(o);for q in[0,1,3]{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);p.push(o);}let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.c_target=BitId(0);p.push(o);
  p.extend([L{kind:K_CCX,c2:1,c1:0,t:2,ct:NQ,cc:NQ,rt:NQ},op(K_CX,0,1,NQ),op(K_CZ,2,3,0),op(K_CX,0,1,NQ),L{kind:K_HMR,c2:NQ,c1:NQ,t:2,ct:1,cc:NQ,rt:NQ},op(K_CZ,0,1,1)].iter().map(from_l));
  let q=phase_expand(p.clone());assert!(q.len()>0&&q!=p);let(nq,nb,_,_)=analyze_ops(p.iter());let(rq,rb,_,_)=analyze_ops(q.iter());assert_eq!((nq,nb),(rq,rb));
  for m in[0,u64::MAX]{let(mut ra,mut rr)=(Word(m),Word(m));let mut a=Simulator::new(nq as usize,nb as usize,&mut ra);let mut b=Simulator::new(rq as usize,rb as usize,&mut rr);for(i,q)in[0,1,3].iter().enumerate(){let v=(0..64).fold(0u64,|x,l|x|((((l>>i)&1)as u64)<<l));a.qubits[*q]=v;b.qubits[*q]=v;}let v=(0..64).fold(0u64,|x,l|x|((((l>>3)&1)as u64)<<l));a.bits[0]=v;b.bits[0]=v;a.apply_iter(p.iter());b.apply_iter(q.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits);assert_eq!(a.phase,b.phase);assert!(a.stats.toffoli_gates>b.stats.toffoli_gates);}
 }
 #[test]fn phase_expand_polynomial_all_affine_pairs(){
  let words:Vec<u64>=(0..5).map(|i|(0..64).fold(0u64,|w,l|w|((((l>>i)&1)as u64)<<l))).collect();
  for ma in 0..16{for mb in 0..16{for ca in[false,true]{for cb in[false,true]{for z in[None,Some(0),Some(1),Some(2),Some(3)]{
   let fa=((0..4).filter(|i|ma>>i&1!=0).collect::<Vec<u32>>(),ca);let fb=((0..4).filter(|i|mb>>i&1!=0).collect::<Vec<u32>>(),cb);let ops:Vec<_>=phase_poly(&fa,&fb,z,0).iter().map(from_l).collect();let mut rng=Word(0);let mut sim=Simulator::new(4,1,&mut rng);sim.qubits.copy_from_slice(&words[..4]);sim.bits[0]=words[4];let initial=0x55aa55aa55aa55aau64;sim.phase=initial;sim.apply_iter(ops.iter());
   let eval=|f:&(Vec<u32>,bool)|f.0.iter().fold(if f.1{u64::MAX}else{0},|v,&i|v^words[i as usize]);let expected=initial^(words[4]&eval(&fa)&eval(&fb)&z.map_or(u64::MAX,|z|words[z as usize]));assert_eq!(sim.phase,expected);assert_eq!(sim.qubits,&words[..4]);
  }}}}}
 }
 #[test]fn phase_expand_missing_cubic_is_detected(){let ops:Vec<_>=phase_poly(&(vec![0],false),&(vec![1],false),Some(2),NQ).iter().map(from_l).collect();assert_eq!(ops.len(),1);assert_eq!(ops[0].kind,K::CCZ);let mut rng=Word(0);let mut sim=Simulator::new(3,0,&mut rng);sim.qubits.fill(u64::MAX);sim.apply_iter(ops.iter());assert_eq!(sim.phase,u64::MAX);assert_ne!(sim.phase,0);}
}
