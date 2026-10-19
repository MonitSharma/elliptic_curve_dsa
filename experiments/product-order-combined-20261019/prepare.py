"""Derive compact scheduler and annotation-only allocator without old edits."""
from pathlib import Path
r=Path(__file__).resolve().parent;e=r.parent
s=(e/'product-order-20261019/order.rs').read_text(encoding='utf-8')
(r/'legacy.rs').write_text(s.replace('mod io;','use super::io;').replace('fn schedule(v:&[Op])','pub fn schedule(v:&[Op])'),encoding='utf-8',newline='\n')
s=s.replace('fn priority(o:&Op,a:&Access,live:&[bool],root:bool)->i32{','fn priority(o:&Op,a:&Access,live:&[bool],root:bool,closed:Option<&[usize]>)->i32{')
s=s.replace('let release=matches!(o.kind', 'if let Some(c)=closed{return added-c.len()as i32;}let release=matches!(o.kind')
s=s.replace('fn segment(v:&[Op],offset:usize,nq:usize,slots:usize,live:&mut[bool],root:bool)->Vec<usize>{','fn segment(v:&[Op],offset:usize,nq:usize,_slots:usize,live:&mut[bool],root:bool,closes:Option<&Clean>)->Vec<usize>{')
s=s.replace('let aa:Vec<_>=v.iter().map(|o|access(o,nq)).collect();','''let mut aa:Vec<_>=v.iter().map(|o|access(o,nq)).collect();
 let mut active_slots:Vec<_>=aa.iter().flat_map(|a|a.read.iter().chain(a.write.iter()).copied()).collect();active_slots.sort_unstable();active_slots.dedup();let slots=active_slots.len();
 let mut active_q:Vec<_>=aa.iter().flat_map(|a|a.qs.iter().copied()).collect();active_q.sort_unstable();active_q.dedup();
 for a in &mut aa{for q in a.read.iter_mut().chain(a.write.iter_mut()){*q=active_slots.binary_search(q).unwrap();}}''')
s=s.replace('vec![BTreeSet::new();nq]','vec![BTreeSet::new();active_q.len()]')
s=s.replace('wire_ready[q].insert(i)','wire_ready[active_q.binary_search(&q).unwrap()].insert(i)')
s=s.replace('wire_ready[q].remove(&i)','wire_ready[active_q.binary_search(&q).unwrap()].remove(&i)')
s=s.replace('wire_ready[q].iter()','wire_ready[active_q.binary_search(&q).unwrap()].iter()')
s=s.replace('priority(&v[i],&aa[i],live,root)','priority(&v[i],&aa[i],live,root,closes.map(|c|c.get(offset+i)))')
s=s.replace('priority(&v[j],&aa[j],live,root)','priority(&v[j],&aa[j],live,root,closes.map(|c|c.get(offset+j)))')
needle='  if matches!(v[i].kind,K::R|K::Hmr)&&root&&v[i].c_condition.0==NO{'
s=s.replace(needle,'''  if let Some(c)=closes{for &q in c.get(offset+i){assert!(aa[i].qs.contains(&q));if live[q]{live[q]=false;changes.push(q);}}}
  else if matches!(v[i].kind,K::R|K::Hmr)&&root&&v[i].c_condition.0==NO{''')
s=s.replace('fn schedule(v:&[Op])->Vec<usize>{','fn schedule(v:&[Op],closes:Option<&Clean>)->Vec<usize>{')
s=s.replace('live,depth==0))','live,depth==0,closes))')
# Independent checker resets only slots actually touched since the last fence.
s=s.replace('let mut mr=None;\n for(i,o)in v.iter().enumerate(){let p=position[i];','let mut mr=None;let mut touched=vec![];\n for(i,o)in v.iter().enumerate(){let p=position[i];')
s=s.replace('last_write.fill(None);max_read.fill(None);','for q in touched.drain(..){last_write[q]=None;max_read[q]=None;}')
s=s.replace('let a=access(o,nq);for q in a.read{','let a=access(o,nq);for q in a.read{touched.push(q);')
s=s.replace('for q in a.write{if last_write','for q in a.write{touched.push(q);if last_write')
start=s.index('fn main(){');end=s.index('\n#[cfg(test)]mod tests{',start)
main=r'''struct Clean{starts:Vec<u32>,roles:Vec<usize>}
impl Clean{fn get(&self,i:usize)->&[usize]{&self.roles[self.starts[i]as usize..self.starts[i+1]as usize]}
 fn load(path:&str,v:&[Op])->Self{let raw=std::fs::read(path).unwrap();assert_eq!(&raw[..8],b"GRCLEAN1");let word=|i:usize|u64::from_le_bytes(raw[i..i+8].try_into().unwrap());assert_eq!(word(8)as usize,v.len());assert_eq!(&raw[16..80],hash(v).as_bytes());let n=word(80)as usize;assert_eq!(raw.len(),88+n*16);let mut starts=vec![0u32;v.len()+1];let mut roles=vec![];let mut cursor=0;let mut prior=None;
  for k in 0..n{let i=word(88+k*16)as usize;let q=word(96+k*16)as usize;assert!(i<v.len());assert!(prior.is_none_or(|p|p<(i,q)));prior=Some((i,q));assert!([v[i].q_control1.0,v[i].q_control2.0,v[i].q_target.0].contains(&(q as u64)));while cursor<=i{starts[cursor]=roles.len().try_into().unwrap();cursor+=1;}roles.push(q);}
  while cursor<=v.len(){starts[cursor]=roles.len().try_into().unwrap();cursor+=1;}Self{starts,roles}
 }}
fn main(){let a:Vec<_>=std::env::args().collect();assert!(a.len()==4||a.len()==5);let mode=&a[3];assert!(["full","core","clean"].contains(&mode.as_str()));let mut v=io::load_ops(&a[1]);let full_hash=hash(&v);let full_count=v.len();let tail=if mode=="full"{vec![]}else{let t=v.split_off(v.len()-96);for x in t.chunks_exact(2){assert_eq!(x[0],x[1]);assert_eq!(x[0].kind,K::X);assert!(x[0].q_target.0<=1);assert_eq!(x[0].c_condition.0,NO);}t};let core_hash=hash(&v);let clean=if mode=="clean"{assert_eq!(a.len(),5);Some(Clean::load(&a[4],&v))}else{None};let mut p=schedule(&v,clean.as_ref());assert!(verify(&v,&p));let core_len=v.len();p.extend(core_len..full_count);v.extend(tail);assert!(verify(&v,&p));let out:Vec<_>=p.iter().map(|&i|v[i]).collect();io::save_ops(&format!("{}.ops.bin",a[2]),&out);let moved=p.iter().enumerate().filter(|(a,b)|*a!=**b).count();let raw:Vec<_>=p.iter().flat_map(|&i|(i as u64).to_le_bytes()).collect();std::fs::write(format!("{}.permutation.bin",a[2]),&raw).unwrap();let d=serde_json::json!({"status":"EXACT_COMMUTATION_PERMUTATION_AUDIT_PASS_NOT_A_RESOURCE_SCORE","mode":mode,"ops":v.len(),"input_full_sha3_256":full_hash,"core_sha3_256":core_hash,"output_full_sha3_256":hash(&out),"permutation_sha3_256":format!("{:x}",Sha3_256::digest(&raw)),"moved_operations":moved,"identity_tail_pinned":mode!="full","all_original_R_Hmr_and_conflict_orders_preserved":true,"clean_annotations_affect_only_heuristic":mode=="clean"});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&d).unwrap()).unwrap();println!("mode={mode} moved={moved}");}
'''
s=s[:start]+main+s[end:]
s=s.replace('let p=schedule(&v);','let p=schedule(&v,None);')
s += '''\n#[cfg(test)]#[path="legacy.rs"]mod legacy;\n#[cfg(test)]mod compact_controls{use super::*;#[test]fn random_source_permutations_equal_legacy(){use quantum_ecc::circuit::QubitId;let mut seed=43u64;for _ in 0..100{let mut v=vec![];for _ in 0..64{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1);let t=seed%8;let a=(t+1+(seed>>8)%7)%8;let mut o=Op::empty();o.kind=if seed>>16&1!=0{K::CX}else{K::X};o.q_target=QubitId(t);if o.kind==K::CX{o.q_control1=QubitId(a);}v.push(o);}assert_eq!(schedule(&v,None),legacy::schedule(&v));}}}\n'''
(r/'order_fast.rs').write_text(s,encoding='utf-8',newline='\n')
g=(e/'product-guard-lifetimes-20261019/guard_color.rs').read_text(encoding='utf-8')
g=g.replace('fn color(v:&[Op])->(Vec<Op>,serde_json::Value){','fn color(v:&[Op])->(Vec<Op>,serde_json::Value,Vec<(u64,u64)>){')
g=g.replace('let mut examples=vec![];','let mut examples=vec![];let mut clean_events=vec![];')
g=g.replace('zero_releases+=1;','zero_releases+=1;clean_events.push((i as u64,role));')
g=g.replace('(out,result)\n}', '(out,result,clean_events)\n}')
g=g.replace('let(out,mut result)=color(&v);','let(out,mut result,events)=color(&v);let mut raw=b"GRCLEAN1".to_vec();raw.extend((v.len()as u64).to_le_bytes());raw.extend(hash(&v).as_bytes());raw.extend((events.len()as u64).to_le_bytes());for(i,q)in events{raw.extend(i.to_le_bytes());raw.extend(q.to_le_bytes());}std::fs::write(format!("{}.clean-events.bin",a[2]),&raw).unwrap();result["clean_event_file_sha3_256"]=serde_json::json!(format!("{:x}",Sha3_256::digest(&raw)));')
g=g.replace('let(w,r)=color(', 'let(w,r,_)=color(').replace('let(_,r)=color(', 'let(_,r,_)=color(').replace('let(w,_)=color(', 'let(w,_,_)=color(')
(r/'guard_annotated.rs').write_text(g,encoding='utf-8',newline='\n')
for name in ('io.rs','preflight.py'):(r/name).write_bytes((e/'product-guard-lifetimes-20261019'/name).read_bytes())
print('Prepared compact scheduler, legacy controls and annotation-only allocator')
