// Independent read-only audit of selected proposal bounds, not a renderer.
use std::{collections::HashMap,fs::File,io::{BufReader,Read},path::Path};
const NONE:u32=u32::MAX;
#[derive(Clone,Copy)]struct Rec{kind:u32,q2:u32,q1:u32,q:u32}
struct Plan{donor:usize,start:usize,end:usize,uses:Vec<usize>,proxy:f64}
fn load(path:&Path)->Vec<Rec>{
 let mut f=BufReader::new(File::open(path).unwrap());let mut header=[0u8;16];f.read_exact(&mut header).unwrap();assert_eq!(&header[..8],b"QECCOPSZ");
 let n=u64::from_le_bytes(header[8..].try_into().unwrap())as usize;assert!(n<=40_000_000);
 let mut d=zstd::stream::read::Decoder::new(f).unwrap();d.window_log_max(27).unwrap();let mut out=Vec::with_capacity(n);
 for _ in 0..n{let mut b=[0u8;56];d.read_exact(&mut b).unwrap();let k=u32::from_le_bytes(b[..4].try_into().unwrap());assert!(k<=16);assert_eq!(&b[4..8],&[0;4]);
  let id=|offset|{let x=u64::from_le_bytes(b[offset..offset+8].try_into().unwrap());if x==u64::MAX{NONE}else{assert!(x<262144);x as u32}};
  out.push(Rec{kind:k,q2:id(8),q1:id(16),q:id(24)});
 }
 let mut extra=[0u8;1];assert_eq!(d.read(&mut extra).unwrap(),0);out
}
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let ops=load(Path::new(&args[1]));
 let text=std::fs::read_to_string(&args[2]).unwrap();let mut plans=vec![];
 for line in text.lines().filter(|s|s.starts_with("LAZY_WINDOW ")){
  let (head,tail)=line.split_once(" uses=[").unwrap();let fields:HashMap<_,_>=head.split_whitespace().skip(1).map(|s|s.split_once('=').unwrap()).collect();
  let uses=tail.strip_suffix(']').unwrap().split(',').map(|v|v.trim().parse::<usize>().unwrap()).collect::<Vec<_>>();
  let p=Plan{donor:fields["donor"].parse().unwrap(),start:fields["start"].parse().unwrap(),end:fields["end"].parse().unwrap(),uses,proxy:fields["proxy"].parse().unwrap()};
  assert!(p.uses.len()>=2&&p.start==p.uses[0]&&p.end==p.uses.last().unwrap()+1&&p.end<=ops.len()&&p.proxy.is_finite());plans.push(p);
 }
 let nq=ops.iter().flat_map(|o|[o.q1,o.q2,o.q]).filter(|q|*q!=NONE).max().unwrap()as usize+1;
 let mut firsts=HashMap::<usize,Vec<usize>>::new();let mut lasts=HashMap::<usize,Vec<usize>>::new();
 for(j,p)in plans.iter().enumerate(){assert!(p.donor<nq);firsts.entry(p.start).or_default().push(j);lasts.entry(*p.uses.last().unwrap()).or_default().push(j);}
 let mut pops=vec![NONE;ops.len()];let mut contexts=HashMap::<usize,Vec<usize>>::new();let mut stack=vec![];
 for (i,o) in ops.iter().enumerate(){
  if firsts.contains_key(&i)||lasts.contains_key(&i){contexts.insert(i,stack.clone());}
  match o.kind{15=>stack.push(i),16=>{let at=stack.pop().unwrap();pops[at]=i as u32;},_=>{}}
 }
 assert!(stack.is_empty());let mut next_write=vec![usize::MAX;nq];let mut next_touch=next_write.clone();
 let mut control_fences=vec![usize::MAX;plans.len()];let mut donor_touches=control_fences.clone();
 for (i,o) in ops.iter().enumerate().rev(){
  if let Some(js)=lasts.get(&i){assert_eq!(o.kind,13);for j in js{control_fences[*j]=next_write[o.q1 as usize].min(next_write[o.q2 as usize]);}}
  match o.kind{6|8|13|11|12=>{next_write[o.q as usize]=i;},10=>{next_write[o.q as usize]=i;next_write[o.q1 as usize]=i;},_=>{}}
  if o.kind!=11{for q in [o.q1,o.q2,o.q]{if q!=NONE{next_touch[q as usize]=i;}}}
  if let Some(js)=firsts.get(&i){for j in js{donor_touches[*j]=next_touch[plans[*j].donor];}}
 }
 let mut early=0;let mut old_control_reject=0;let mut old_donor_reject=0;let mut either_reject=0;let mut distinct_proxy=0.0;let mut details=vec![];
 for (j,p) in plans.iter().enumerate(){
  let a=&contexts[&p.start];let b=&contexts[p.uses.last().unwrap()];let common=a.iter().zip(b).take_while(|(x,y)|x==y).count();
  let old_end=if common==b.len(){p.end}else{assert_ne!(pops[b[common]],NONE);pops[b[common]]as usize+1};
  assert!(control_fences[j]>=p.end&&donor_touches[j]>=p.end);
  let c=control_fences[j]<old_end;let d=donor_touches[j]<old_end;
  if old_end>p.end{early+=1;}if c{old_control_reject+=1;}if d{old_donor_reject+=1;}
  if c||d{either_reject+=1;distinct_proxy+=p.proxy;}
  details.push(serde_json::json!({"donor":p.donor,"start":p.start,"last":p.uses.last(),"new_end":p.end,"old_LCA_end":old_end,"old_control_fence_reject":c,"old_same_donor_reject":d,"source_proxy_only":p.proxy}));
 }
 println!("{}",serde_json::json!({"status":"INDEPENDENT_SELECTED_SCOPE_BOUND_AUDIT_SOURCE_ONLY","ops":ops.len(),"selected":plans.len(),"cleanup_earlier_than_LCA":early,"old_control_fence_reject":old_control_reject,"old_same_donor_fence_reject":old_donor_reject,"either_old_fence_reject":either_reject,"distinct_earlier_proxy_only":distinct_proxy,"not_measured_T_or_global_inadmissibility_of_other_donors":true,"plans":details}));
}
