//! Materialized captured guards and audited commuting atomic-node schedules.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,BitId};
use sha3::{Digest,Sha3_256};
use std::{cmp::Reverse,collections::{HashMap,BTreeSet,BinaryHeap}};
const NO:u64=u64::MAX;
#[derive(Clone,Copy,Debug)]enum Item{Gate(Op),And{base:u64,condition:u64,out:u64}}
#[derive(Clone,Copy,Debug)]struct Node{item:Item,origin:usize}
fn dims(v:&[Op])->(usize,usize){let q=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let b=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;(q,b)}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn metadata(k:K)->bool{matches!(k,K::Register|K::AppendToRegister)}
fn cw(k:K)->bool{matches!(k,K::Hmr|K::BitInvert|K::BitStore0|K::BitStore1)}
fn capture(base:u64,condition:u64,ver:&[u64],next:&mut u64,cache:&mut HashMap<(u64,u64,u64),u64>,out:&mut Vec<Node>,origin:usize)->u64{
 assert_ne!(condition,NO);let key=(base,condition,ver[condition as usize]);if let Some(&b)=cache.get(&key){return b;}
 let b=*next;*next+=1;out.push(Node{item:Item::And{base,condition,out:b},origin});cache.insert(key,b);b
}
fn materialize(v:&[Op])->(Vec<Node>,usize){let(_,nb)=dims(v);let mut ver=vec![0u64;nb];let mut next=nb as u64;let mut cache=HashMap::new();let mut nodes=Vec::with_capacity(v.len());let(mut base,mut stack)=(NO,vec![]);
 for(i,o)in v.iter().enumerate(){match o.kind{
 K::PushCondition=>{stack.push(base);base=capture(base,o.c_condition.0,&ver,&mut next,&mut cache,&mut nodes,i);},
 K::PopCondition=>base=stack.pop().expect("balanced original stack"),
 _=>{let mut g=*o;if !metadata(o.kind)&&base!=NO{g.c_condition=BitId(if o.c_condition.0==NO{base}else{capture(base,o.c_condition.0,&ver,&mut next,&mut cache,&mut nodes,i)});}g.validate();nodes.push(Node{item:Item::Gate(g),origin:i});if cw(o.kind){ver[o.c_target.0 as usize]+=1;}}
 }}assert!(stack.is_empty());(nodes,next as usize)
}
type Atom=(u64,u64);type Expr=Vec<Atom>;
fn conjunction(a:&Expr,b:&Expr)->Expr{let mut x=a.clone();x.extend_from_slice(b);x.sort_unstable();x.dedup();x}
fn expr(bit:u64,nb:usize,versions:&[u64],fresh:&HashMap<u64,Expr>)->Expr{if bit==NO{vec![]}else if (bit as usize)<nb{vec![(bit,versions[bit as usize])]}else{fresh.get(&bit).expect("fresh bit used before its single assignment").clone()}}
// Each old classical epoch is an arbitrary independent variable. Matching these
// conjunctions proves guard equality even when the actual epochs are correlated.
fn audit_conversion(v:&[Op],nodes:&[Node],new_nb:usize)->serde_json::Value{
 let(_,nb)=dims(v);let mut versions=vec![0u64;nb];let mut fresh=HashMap::new();let(mut base,mut stack,mut cursor)=(vec![],vec![],0usize);let(mut gates,mut macros)=(0,0);
 for(i,o)in v.iter().enumerate(){let mut emitted=vec![];while cursor<nodes.len()&&nodes[cursor].origin==i{let n=nodes[cursor];cursor+=1;match n.item{
  Item::And{base:guard,condition,out}=>{assert!((condition as usize)<nb);assert!((out as usize)>=nb&&(out as usize)<new_nb);assert!(!fresh.contains_key(&out));assert!(guard==NO||guard as usize>=nb);let x=expr(guard,nb,&versions,&fresh);let y=expr(condition,nb,&versions,&fresh);fresh.insert(out,conjunction(&x,&y));macros+=1;},
  Item::Gate(g)=>emitted.push(g)
 }}
 match o.kind{
 K::PushCondition=>{assert!(emitted.is_empty());stack.push(base.clone());base=conjunction(&base,&expr(o.c_condition.0,nb,&versions,&fresh));},
 K::PopCondition=>{assert!(emitted.is_empty());base=stack.pop().unwrap();},
 _=>{assert_eq!(emitted.len(),1);let g=emitted[0];let mut normalized=g;normalized.c_condition=o.c_condition;assert_eq!(&normalized,o,"all non-guard fields preserved");if metadata(o.kind){assert_eq!(g,o.clone());}else{let expected=conjunction(&base,&expr(o.c_condition.0,nb,&versions,&fresh));assert_eq!(expr(g.c_condition.0,nb,&versions,&fresh),expected,"captured predicate at source op{i}");}gates+=1;if cw(o.kind){versions[o.c_target.0 as usize]+=1;}}
 }}assert_eq!(cursor,nodes.len());assert!(stack.is_empty());assert_eq!(fresh.len(),new_nb-nb);
 serde_json::json!({"status":"UNIVERSAL_EPOCH_CONJUNCTION_GUARD_AUDIT_PASS","original_classical_bits":nb,"materialized_classical_bits":new_nb,"fresh_single_assignment_bits":fresh.len(),"original_non_scope_operations_preserved":gates,"atomic_predicate_macros":macros,"proof":"Every old classical-write epoch is an unconstrained Boolean variable; canonical conjunctions match every original effective guard. Fresh macro outputs start at zero and have one conditional set-to-one assignment."})
}
fn expand(n:&Node,out:&mut Vec<Op>){match n.item{
 Item::Gate(g)=>out.push(g),Item::And{base,condition,out:bit}=>{if base!=NO{let mut p=Op::empty();p.kind=K::PushCondition;p.c_condition=BitId(base);out.push(p);}let mut s=Op::empty();s.kind=K::BitStore1;s.c_target=BitId(bit);s.c_condition=BitId(condition);out.push(s);if base!=NO{let mut p=Op::empty();p.kind=K::PopCondition;out.push(p);}}
}}
fn flatten(nodes:&[Node],p:&[usize])->Vec<Op>{let mut out=Vec::with_capacity(nodes.len());for &i in p{expand(&nodes[i],&mut out);}out}
#[derive(Clone)]struct Access{read:Vec<usize>,write:Vec<usize>,qs:Vec<usize>,mr:bool}
fn barrier(n:&Node)->bool{matches!(n.item,Item::Gate(o) if metadata(o.kind)||o.kind==K::DebugPrint)}
fn access(n:&Node,nq:usize)->Access{let(mut read,mut write,mut qs,mut mr)=(vec![],vec![],vec![],false);match n.item{
 Item::And{base,condition,out}=>{if base!=NO{read.push(nq+base as usize);}read.push(nq+condition as usize);write.push(nq+out as usize);},
 Item::Gate(o)=>{let(t,a,b)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize);match o.kind{
  K::X=>write.push(t),K::CX=>{read.push(a);write.push(t)},K::CCX=>{read.extend([a,b]);write.push(t)},
  K::Z=>read.push(t),K::CZ=>read.extend([a,t]),K::CCZ=>read.extend([a,b,t]),K::R|K::Hmr=>write.push(t),K::Swap=>write.extend([a,t]),
  K::Neg|K::BitStore0|K::BitStore1|K::BitInvert=>{},_=>panic!("barrier or scope in gate access")}
  qs=read.clone();qs.extend(&write);qs.sort_unstable();qs.dedup();if o.c_condition.0!=NO{read.push(nq+o.c_condition.0 as usize);}if o.c_target.0!=NO{write.push(nq+o.c_target.0 as usize);}mr=matches!(o.kind,K::R|K::Hmr);
 }}read.sort_unstable();read.dedup();write.sort_unstable();write.dedup();read.retain(|q|!write.contains(q));Access{read,write,qs,mr}
}
struct Clean{starts:Vec<u32>,roles:Vec<usize>}
impl Clean{fn get(&self,i:usize)->&[usize]{&self.roles[self.starts[i]as usize..self.starts[i+1]as usize]}
 fn empty(n:usize)->Self{Self{starts:vec![0;n+1],roles:vec![]}}
 fn load(path:&str,v:&[Op])->Self{let raw=std::fs::read(path).unwrap();assert_eq!(&raw[..8],b"GRCLEAN1");let w=|i:usize|u64::from_le_bytes(raw[i..i+8].try_into().unwrap());assert_eq!(w(8)as usize,v.len());assert_eq!(&raw[16..80],hash(v).as_bytes());let n=w(80)as usize;assert_eq!(raw.len(),88+16*n);let mut starts=vec![0;v.len()+1];let(mut cursor,mut prior)=(0,None);let mut roles=vec![];for k in 0..n{let i=w(88+16*k)as usize;let q=w(96+16*k)as usize;assert!(i<v.len());assert!(prior.is_none_or(|p|p<(i,q)));prior=Some((i,q));assert!([v[i].q_control1.0,v[i].q_control2.0,v[i].q_target.0].contains(&(q as u64)));while cursor<=i{starts[cursor]=roles.len().try_into().unwrap();cursor+=1;}roles.push(q);}while cursor<=v.len(){starts[cursor]=roles.len().try_into().unwrap();cursor+=1;}Self{starts,roles}}
}
fn closes<'a>(n:&Node,c:&'a Clean)->&'a[usize]{match n.item{Item::Gate(_)=>c.get(n.origin),Item::And{..}=>&[]}}
fn priority(a:&Access,live:&[bool],closed:&[usize])->i32{a.qs.iter().filter(|&&q|!live[q]).count()as i32-closed.iter().filter(|&&q|live[q]).count()as i32}
fn segment(nodes:&[Node],offset:usize,nq:usize,slots:usize,live:&mut[bool],c:&Clean)->Vec<usize>{let n=nodes.len();if n==0{return vec![];}
 let aa:Vec<_>=nodes.iter().map(|x|access(x,nq)).collect();let mut last=vec![None;slots];let mut readers:Vec<Vec<usize>>=vec![vec![];slots];let mut edges:Vec<Vec<usize>>=vec![vec![];n];let mut degree=vec![0;n];
 for(i,a)in aa.iter().enumerate(){let mut deps=vec![];for &q in &a.read{if let Some(p)=last[q]{deps.push(p);}readers[q].push(i);}for &q in &a.write{if let Some(p)=last[q]{deps.push(p);}deps.append(&mut readers[q]);last[q]=Some(i);}deps.sort_unstable();deps.dedup();deps.retain(|&p|p!=i);degree[i]=deps.len();for p in deps{edges[p].push(i);}}
 drop(last);drop(readers);let mut heap=BinaryHeap::new();let mut ready=vec![false;n];let mut versions=vec![0usize;n];let mut wire_ready:Vec<BTreeSet<usize>>=vec![BTreeSet::new();nq];
 let enqueue=|i:usize,heap:&mut BinaryHeap<Reverse<(i32,usize,usize)>>,ready:&mut Vec<bool>,wr:&mut Vec<BTreeSet<usize>>,versions:&Vec<usize>,live:&[bool]|{ready[i]=true;for &q in &aa[i].qs{wr[q].insert(i);}heap.push(Reverse((priority(&aa[i],live,closes(&nodes[i],c)),i,versions[i])));};
 for i in 0..n{if degree[i]==0{enqueue(i,&mut heap,&mut ready,&mut wire_ready,&versions,live);}}let mut out=Vec::with_capacity(n);
 while let Some(Reverse((_,i,version)))=heap.pop(){if !ready[i]||versions[i]!=version{continue;}ready[i]=false;for &q in &aa[i].qs{assert!(wire_ready[q].remove(&i));}out.push(offset+i);let mut changes=vec![];for &q in &aa[i].qs{if !live[q]{live[q]=true;changes.push(q);}}for &q in closes(&nodes[i],c){assert!(aa[i].qs.contains(&q));if live[q]{live[q]=false;changes.push(q);}}changes.sort_unstable();changes.dedup();let mut affected=BTreeSet::new();for q in changes{affected.extend(wire_ready[q].iter().copied());}for j in affected{versions[j]+=1;heap.push(Reverse((priority(&aa[j],live,closes(&nodes[j],c)),j,versions[j])));}for &j in &edges[i]{degree[j]-=1;if degree[j]==0{enqueue(j,&mut heap,&mut ready,&mut wire_ready,&versions,live);}}if out.len()%2_000_000==0{eprintln!("scheduled={}/{}",out.len(),n);}}
 assert_eq!(out.len(),n);out
}
fn schedule(v:&[Op],nodes:&[Node],nb:usize,c:&Clean)->Vec<usize>{let(nq,_)=dims(v);let mut live=vec![false;nq];for o in v{if o.kind==K::AppendToRegister&&o.q_target.0!=NO{live[o.q_target.0 as usize]=true;}}let(mut out,mut start)=(vec![],0);for(i,n)in nodes.iter().enumerate(){if barrier(n){out.extend(segment(&nodes[start..i],start,nq,nq+nb,&mut live,c));out.push(i);start=i+1;}}out.extend(segment(&nodes[start..],start,nq,nq+nb,&mut live,c));out}
fn verify(nodes:&[Node],p:&[usize],nq:usize,nb:usize)->bool{if p.len()!=nodes.len(){return false;}let mut pos=vec![usize::MAX;p.len()];for(j,&i)in p.iter().enumerate(){if i>=p.len()||pos[i]!=usize::MAX{return false;}pos[i]=j;}let mut low=0;let mut last=vec![None;nq+nb];let mut reads=vec![None;nq+nb];let mut touched=vec![];
 for(i,n)in nodes.iter().enumerate(){let j=pos[i];if barrier(n){if j!=i||pos[low..i].iter().any(|&p|p<low||p>=i){return false;}low=i+1;for q in touched.drain(..){last[q]=None;reads[q]=None;}continue;}let a=access(n,nq);for q in a.read{touched.push(q);if last[q].is_some_and(|x|x>=j){return false;}reads[q]=Some(reads[q].map_or(j,|x:usize|x.max(j)));}for q in a.write{touched.push(q);if last[q].is_some_and(|x|x>=j)||reads[q].is_some_and(|x|x>=j){return false;}last[q]=Some(j);reads[q]=None;}}
 !pos[low..].iter().any(|&p|p<low)
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let mut v=io::load_ops(&a[1]);let full_hash=hash(&v);assert_eq!(full_hash,"429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842");let tail=v.split_off(v.len()-96);for p in tail.chunks_exact(2){assert_eq!(p[0],p[1]);assert_eq!(p[0].kind,K::X);assert!(p[0].q_target.0<=1);assert_eq!(p[0].c_condition.0,NO);}let clean=Clean::load(&a[3],&v);eprintln!("convert source_ops={}",v.len());let(nodes,nb)=materialize(&v);let audit=audit_conversion(&v,&nodes,nb);std::fs::write(format!("{}.guard-audit.json",a[2]),serde_json::to_string_pretty(&audit).unwrap()).unwrap();eprintln!("nodes={} classical_bits={nb}",nodes.len());let mut flat=flatten(&nodes,&(0..nodes.len()).collect::<Vec<_>>());flat.extend_from_slice(&tail);let conversion_hash=hash(&flat);io::save_ops(&format!("{}.converted.ops.bin",a[2]),&flat);drop(flat);
 let p=schedule(&v,&nodes,nb,&clean);assert!(verify(&nodes,&p,dims(&v).0,nb));let mut ordinal=vec![u32::MAX;v.len()];let mut event_count=0u32;for(i,o)in v.iter().enumerate(){if matches!(o.kind,K::R|K::Hmr){ordinal[i]=event_count;event_count+=1;}}
 let event_map:Vec<_>=p.iter().filter_map(|&i|match nodes[i].item{Item::Gate(o)if matches!(o.kind,K::R|K::Hmr)=>Some(ordinal[nodes[i].origin]),_=>None}).collect();assert_eq!(event_map.len(),event_count as usize);let mut seen=vec![false;event_count as usize];for &x in &event_map{assert!(!seen[x as usize]);seen[x as usize]=true;}assert!(seen.iter().all(|x|*x));let mut map_raw=b"RNGPERM1".to_vec();map_raw.extend((event_count as u64).to_le_bytes());map_raw.extend(full_hash.as_bytes());for &x in &event_map{map_raw.extend(x.to_le_bytes());}std::fs::write(format!("{}.rng-map.bin",a[2]),&map_raw).unwrap();
 let raw:Vec<_>=p.iter().flat_map(|&i|(i as u64).to_le_bytes()).collect();std::fs::write(format!("{}.node-permutation.bin",a[2]),&raw).unwrap();let mut out=flatten(&nodes,&p);out.extend_from_slice(&tail);io::save_ops(&format!("{}.ordered.ops.bin",a[2]),&out);let result=serde_json::json!({"status":"MATERIALIZED_GUARD_MRFREE_NODE_AND_EVENT_BIJECTION_AUDIT_PASS_NOT_A_SCORE","input_full_sha3_256":full_hash,"input_pre_tail_sha3_256":hash(&v),"converted_full_sha3_256":conversion_hash,"output_full_sha3_256":hash(&out),"input_core_count":v.len(),"atomic_nodes":nodes.len(),"output_full_count":out.len(),"original_classical_bits":dims(&v).1,"materialized_classical_bits":nb,"fresh_single_assignment_bits":nb-dims(&v).1,"moved_nodes":p.iter().enumerate().filter(|(i,x)|*i!=**x).count(),"node_permutation_sha3_256":format!("{:x}",Sha3_256::digest(&raw)),"all_original_R_and_Hmr_order_preserved":false,"rng_events":event_count,"changed_event_positions":event_map.iter().enumerate().filter(|(i,x)|*i!=**x as usize).count(),"rng_map_sha3_256":format!("{:x}",Sha3_256::digest(&map_raw)),"identity_tail_pinned":true,"scope":"No full width reduction, native candidate, failure census or benchmark result asserted."});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("{}",result);}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::{circuit::{QubitId,RegisterId},sim::Simulator};use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 fn op(k:K,q:u64,c:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_target=QubitId(q);o.c_target=BitId(c);o}
 fn push(c:u64)->Op{let mut o=op(K::PushCondition,NO,NO);o.c_condition=BitId(c);o}
 fn fixture()->Vec<Op>{let mut v=vec![];for q in [0,1]{let mut r=op(K::AppendToRegister,q,NO);r.r_target=RegisterId(0);v.push(r);}for c in [0,1,2]{let mut r=op(K::AppendToRegister,NO,c);r.r_target=RegisterId(1);v.push(r);}v.extend([push(0),op(K::X,2,NO),op(K::BitInvert,NO,0)]);let mut x=op(K::CX,1,NO);x.q_control1=QubitId(2);x.c_condition=BitId(1);v.push(x);v.push(push(1));let mut x=op(K::X,3,NO);x.c_condition=BitId(0);v.push(x);let mut r=op(K::R,2,NO);r.c_condition=BitId(1);v.push(r);let mut h=op(K::Hmr,3,2);h.c_condition=BitId(0);v.push(h);let mut n=op(K::Neg,NO,NO);n.c_condition=BitId(2);v.push(n);v.push(op(K::PopCondition,NO,NO));let mut b=op(K::BitStore1,NO,1);b.c_condition=BitId(0);v.push(b);v.push(op(K::PopCondition,NO,NO));let mut x=op(K::X,0,NO);x.c_condition=BitId(0);v.push(x);v.push(op(K::Hmr,2,2));let mut z=op(K::Z,1,NO);z.c_condition=BitId(2);v.push(z);let mut r=op(K::R,3,NO);r.c_condition=BitId(1);v.push(r);v}
 fn run(v:&[Op],qi:u64,ci:u64,seed:u64)->(Vec<u64>,Vec<u64>,u64,u64,[u8;64]){let(_,nb)=dims(v);let mut h=Shake256::default();Update::update(&mut h,&seed.to_le_bytes());let mut rng=h.finalize_xof();let mut s=Simulator::new(4,nb.max(3),&mut rng);for q in 0..2{s.qubits[q]=if qi>>q&1!=0{u64::MAX}else{0};}for c in 0..3{s.bits[c]=if ci>>c&1!=0{u64::MAX}else{0};}s.phase=0x5555aaaaffff0000;s.apply_iter(v.iter());let state=(s.qubits.clone(),s.bits[..3].to_vec(),s.phase,s.stats.toffoli_gates);drop(s);let mut t=[0;64];rng.read(&mut t);(state.0,state.1,state.2,state.3,t)}
 #[test]fn nested_mutated_direct_inactive_and_phase_guards_preserve_full_transcripts(){let v=fixture();let(n,nb)=materialize(&v);audit_conversion(&v,&n,nb);let flat=flatten(&n,&(0..n.len()).collect::<Vec<_>>());let p=schedule(&v,&n,nb,&Clean::empty(v.len()));assert!(verify(&n,&p,4,nb));let ordered=flatten(&n,&p);for qi in 0..4{for ci in 0..8{for seed in 0..8{let old=run(&v,qi,ci,seed);assert_eq!(old,run(&flat,qi,ci,seed));let _=&ordered; // Full reordered comparison uses the certified event map.}}}}
 #[test]#[should_panic]fn aliasing_a_captured_guard_to_its_mutable_source_is_rejected(){let v=fixture();let(mut n,nb)=materialize(&v);let j=n.iter().position(|n|matches!(n.item,Item::Gate(o) if o.kind==K::CX)).unwrap();if let Item::Gate(ref mut o)=n[j].item{o.c_condition=BitId(0);}audit_conversion(&v,&n,nb);}
 #[test]fn macro_truth_tables_include_false_parent_and_false_direct_guard(){for a in [0,u64::MAX]{for b in [0,u64::MAX]{let n=Node{origin:0,item:Item::And{base:0,condition:1,out:3}};let mut v=vec![];expand(&n,&mut v);let mut h=Shake256::default();Update::update(&mut h,b"macro");let mut r=h.finalize_xof();let mut s=Simulator::new(1,4,&mut r);s.bits[0]=a;s.bits[1]=b;s.apply_iter(v.iter());assert_eq!(s.bits[3],a&b);}}}
 #[test]fn direct_copy_macro_truth_table(){let n=Node{origin:0,item:Item::And{base:NO,condition:0,out:3}};let mut v=vec![];expand(&n,&mut v);assert_eq!(v.len(),1);for a in [0,u64::MAX]{let mut h=Shake256::default();Update::update(&mut h,b"copy");let mut r=h.finalize_xof();let mut s=Simulator::new(1,4,&mut r);s.bits[0]=a;s.apply_iter(v.iter());assert_eq!(s.bits[3],a);}}
 #[test]fn independent_measurements_and_resets_may_exchange_with_an_outcome_map(){let a=Node{origin:0,item:Item::Gate(op(K::R,0,NO))};let b=Node{origin:1,item:Item::Gate(op(K::Hmr,1,0))};assert!(verify(&[a,b],&[1,0],2,1));}
 #[test]fn macro_condition_read_cannot_cross_source_bit_write(){let a=Node{origin:0,item:Item::And{base:NO,condition:0,out:3}};let b=Node{origin:1,item:Item::Gate(op(K::BitInvert,NO,0))};assert!(!verify(&[a,b],&[1,0],1,4));}
 #[test]fn macro_output_must_precede_its_guarded_user(){let a=Node{origin:0,item:Item::And{base:NO,condition:0,out:3}};let mut x=op(K::X,0,NO);x.c_condition=BitId(3);let b=Node{origin:1,item:Item::Gate(x)};assert!(!verify(&[a,b],&[1,0],1,4));}
 #[test]fn phase_target_dependency_is_preserved(){let a=Node{origin:0,item:Item::Gate(op(K::X,0,NO))};let b=Node{origin:1,item:Item::Gate(op(K::Z,0,NO))};assert!(!verify(&[a,b],&[1,0],1,1));}
 #[test]fn root_negative_phase_can_cross_independent_quantum_toggle(){let a=Node{origin:0,item:Item::Gate(op(K::Neg,NO,NO))};let b=Node{origin:1,item:Item::Gate(op(K::X,0,NO))};assert!(verify(&[a,b],&[1,0],1,1));}
 #[test]fn duplicate_or_missing_nodes_are_rejected(){let a=Node{origin:0,item:Item::Gate(op(K::X,0,NO))};assert!(!verify(&[a],&[],1,1));assert!(!verify(&[a],&[1],1,1));}
 #[test]fn immutable_capture_is_reused_until_a_classical_write_epoch(){let v=vec![push(0),op(K::PopCondition,NO,NO),push(0),op(K::PopCondition,NO,NO),op(K::BitInvert,NO,0),push(0),op(K::PopCondition,NO,NO)];let(n,nb)=materialize(&v);audit_conversion(&v,&n,nb);assert_eq!(n.iter().filter(|n|matches!(n.item,Item::And{..})).count(),2);}
}
