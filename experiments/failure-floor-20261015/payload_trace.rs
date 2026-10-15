//! Gate-inert payload transition observer. No circuit gates emitted.
use crate::circuit::{analyze_ops,Op,QubitId};
use alloy_primitives::U256;
use sha3::{Shake256,digest::{Update,ExtendableOutput}};
use std::{collections::HashMap,sync::Mutex};
#[derive(Clone)]
struct Mark{at:usize,id:usize,before:bool,phase:&'static str,t:usize,rev:bool,skip:bool,pay:[Vec<QubitId>;2],letter:Vec<QubitId>}
static MARKS:Mutex<Vec<Mark>>=Mutex::new(Vec::new());
#[derive(Clone)]
struct Fold{at:usize,id:usize,before:bool,phase:&'static str,t:usize,rev:bool,acc:Vec<QubitId>,e:[QubitId;3],nm:[QubitId;3],shift:[QubitId;2],src:Vec<QubitId>}
static FOLDS:Mutex<Vec<Fold>>=Mutex::new(Vec::new());
#[derive(Clone)]
struct Stage{at:usize,label:&'static str,x:Vec<QubitId>,y:Vec<QubitId>,offset:U256}
static STAGES:Mutex<Vec<Stage>>=Mutex::new(Vec::new());
#[derive(Clone)]
struct Window{at:usize,id:usize,before:bool,inv:bool,shift:usize,value:Vec<QubitId>,out:Vec<QubitId>,cin:Option<QubitId>}
static WINDOWS:Mutex<Vec<Window>>=Mutex::new(Vec::new());
pub fn window_begin(at:usize,inv:bool,shift:usize,value:&[QubitId],out:&[QubitId],cin:Option<QubitId>)->usize{let mut ws=WINDOWS.lock().unwrap();let id=ws.len();ws.push(Window{at,id,before:true,inv,shift,value:value.to_vec(),out:out.to_vec(),cin});id}
pub fn window_end(id:usize,at:usize){let mut ws=WINDOWS.lock().unwrap();let mut w=ws.iter().find(|w|w.id==id&&w.before).unwrap().clone();w.before=false;w.at=at;ws.push(w);}
fn unsigned(q:&[QubitId],words:&[u64],lane:usize)->U256{let mut v=U256::ZERO;assert!(q.len()<=256);for(i,q)in q.iter().enumerate(){if words[q.0 as usize]>>lane&1!=0{v|=U256::from(1)<<i;}}v}
pub fn stage(at:usize,label:&'static str,x:&[QubitId],y:&[QubitId],offset:U256){STAGES.lock().unwrap().push(Stage{at,label,x:x.to_vec(),y:y.to_vec(),offset});}
fn pow(mut a:U256,mut n:U256,p:U256)->U256{let mut r=U256::from(1);while n!=U256::ZERO{if n.bit(0){r=r.mul_mod(a,p);}a=a.mul_mod(a,p);n>>=1;}r}
fn stage_word(qs:&[QubitId],words:&[u64],lane:usize,p:U256)->U256{let f=U256::from(0x1000003d1u64);let mut v=U256::ZERO;for(i,q)in qs.iter().enumerate(){if words[q.0 as usize]>>lane&1!=0{v=v.add_mod(if i<256{U256::from(1)<<i}else{f<<(i-256)},p);}}if qs.len()>256&&words[qs.last().unwrap().0 as usize]>>lane&1!=0{v=sub(v,f<<(qs.len()-256),p);}v}
pub fn fold_begin(at:usize,acc:&[QubitId],e:[QubitId;3],nm:[QubitId;3],k1:QubitId,k2:QubitId,rev:bool,src:&[QubitId])->usize{
 let marks=MARKS.lock().unwrap();let (phase,t)=marks.last().map(|m|(m.phase,m.t)).unwrap_or(("divide",0));let mut fs=FOLDS.lock().unwrap();let id=fs.len();fs.push(Fold{at,id,before:true,phase,t,rev,acc:acc.to_vec(),e,nm,shift:[k1,k2],src:src.to_vec()});id
}
pub fn fold_end(id:usize,at:usize){let mut fs=FOLDS.lock().unwrap();let mut f=fs.iter().find(|f|f.id==id&&f.before).unwrap().clone();f.at=at;f.before=false;fs.push(f);}
fn small(q:&[QubitId],words:&[u64],lane:usize)->i128{assert!(q.len()<=63);q.iter().enumerate().map(|(i,q)|((words[q.0 as usize]>>lane&1)as i128)<<i).sum()}
pub fn begin(at:usize,phase:&'static str,t:usize,rev:bool,pay:&[Vec<QubitId>;2])->usize{
 let mut m=MARKS.lock().unwrap();let id=m.len();m.push(Mark{at,id,before:true,phase,t,rev,skip:false,pay:pay.clone(),letter:vec![]});id
}
pub fn end(id:usize,at:usize,pay:&[Vec<QubitId>;2],letter:&[QubitId],skip:bool){
 let mut ms=MARKS.lock().unwrap();let mut m=ms.iter().find(|m|m.id==id&&m.before).unwrap().clone();m.at=at;m.before=false;m.pay=pay.clone();m.letter=letter.to_vec();m.skip=skip;ms.push(m);
}
pub fn set_letter(id:usize,letter:&[QubitId]){let mut ms=MARKS.lock().unwrap();let m=ms.iter_mut().find(|m|m.id==id&&m.before).unwrap();m.letter=letter.to_vec();}
fn sub(a:U256,b:U256,p:U256)->U256{if a>=b{a-b}else{p-(b-a)}}
fn half(v:U256,p:U256)->U256{if v.bit(0){(v>>1)+(p>>1)+U256::from(1)}else{v>>1}}
fn word(q:&[QubitId],w:&[u64],lane:usize)->U256{assert_eq!(q.len(),256);let mut v=U256::ZERO;for(i,q)in q.iter().enumerate(){if w[q.0 as usize]>>lane&1!=0{v|=U256::from(1)<<i;}}v}
fn norm(v:U256,p:U256)->U256{if v>=p{v-p}else{v}}
pub fn run(ops:&[Op]){
 let root="/home/hclau/ecdsa_research/failure-floor-20261015";let p=super::SECP256K1_P;
 let marks=MARKS.lock().unwrap().clone();assert!(marks.windows(2).all(|v|v[0].at<=v[1].at));
 let folds=FOLDS.lock().unwrap().clone();assert!(folds.windows(2).all(|v|v[0].at<=v[1].at));
 let stages=STAGES.lock().unwrap().clone();
 let windows=WINDOWS.lock().unwrap().clone();
 let(nq,nb,_,regs)=analyze_ops(ops.iter());eprintln!("PAY_MARKS total={}",marks.len());
 for family in ["floor31","independent"]{
 let txt=std::fs::read_to_string(format!("{root}/packets/{family}.tsv")).unwrap();
 let rows:Vec<[U256;6]>=txt.lines().filter(|l|!l.trim().is_empty()).map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();
 let mut total_bad=0;let mut total_event=0;
 for(batch,rows)in rows.chunks(64).enumerate(){
 let mut h=Shake256::default();h.update(b"failure-floor-20261015");h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut rr=rng.clone();
 let mut sim=super::observed_sim::Simulator::new(nq as usize,nb as usize,&mut rng);let mut reference=crate::sim::Simulator::new(nq as usize,nb as usize,&mut rr);
 for(lane,row)in rows.iter().enumerate(){for k in 0..4{sim.set_register(&regs[k],row[k],lane);reference.set_register(&regs[k],row[k],lane);}}
 let mut entries=HashMap::<usize,Vec<[U256;2]>>::new();let mut tapes=HashMap::<usize,Vec<Vec<u64>>>::new();let mut cursor=0;let mut first=vec![false;rows.len()];
 let mut fcursor=0;let mut fold_values=HashMap::<usize,Vec<(i128,i128,i128,i128,i128,i128,i128)>>::new();
 let slopes:Vec<_>=rows.iter().map(|r|sub(r[1],r[3],p).mul_mod(pow(sub(r[0],r[2],p),p-U256::from(2),p),p)).collect();let mut stage_cursor=0;let mut stage_first=vec![false;rows.len()];
 let mut window_cursor=0;let mut window_entries=HashMap::<usize,Vec<(U256,U256,u64)>>::new();
 sim.apply_observed(ops.iter(),|idx,s,_,_|{
 while window_cursor<windows.len()&&windows[window_cursor].at==idx{let m=&windows[window_cursor];window_cursor+=1;if m.before{window_entries.insert(m.id,(0..rows.len()).map(|lane|(unsigned(&m.out,&s.qubits,lane),unsigned(&m.value,&s.qubits,lane),m.cin.map_or(0,|q|s.qubits[q.0 as usize]>>lane&1))).collect());}else{let vs=window_entries.remove(&m.id).unwrap();for lane in 0..rows.len(){let(a,b,cin)=vs[lane];let add=b.add_mod(U256::from(cin),p).mul_mod(U256::from(1)<<m.shift,p);let want=if m.inv{sub(norm(a,p),add,p)}else{norm(a,p).add_mod(add,p)};let got=norm(unsigned(&m.out,&s.qubits,lane),p);if got!=want{eprintln!("WINDOW_EVENT family={family} shot={} at={} shift={} value_width={} inv={} cin={cin} a={a:#x} b={b:#x} got={got:#x} want={want:#x} diff={:#x}",batch*64+lane,m.at,m.shift,m.value.len(),m.inv,sub(got,want,p));assert_ne!(family,"independent","window observer false positive");}}}}
 while stage_cursor<stages.len()&&stages[stage_cursor].at==idx{let m=&stages[stage_cursor];stage_cursor+=1;for lane in 0..rows.len(){let r=rows[lane];let slope=slopes[lane];let q=slope.mul_mod(slope,p);let u=sub(r[0].add_mod(r[2].add_mod(r[2],p),p),q,p);let (wx,wy)=match m.label{"divide"=>(r[0].add_mod(r[2].add_mod(r[2],p),p).add_mod(m.offset,p),slope),"square"=>(u,slope),"multiply"=>(r[4],r[5].add_mod(r[3],p)),_=>unreachable!()};let x=stage_word(&m.x,&s.qubits,lane,p);let y=stage_word(&m.y,&s.qubits,lane,p);let bad=x!=wx||y!=wy;if bad&&!stage_first[lane]{stage_first[lane]=true;eprintln!("STAGE_EVENT family={family} shot={} stage={} at={} x={x:#x} want_x={wx:#x} y={y:#x} want_y={wy:#x} x_width={}",batch*64+lane,m.label,m.at,m.x.len());}if family=="floor31"&&(batch*64+lane==20||batch*64+lane==26){eprintln!("STAGE_CHECK family={family} shot={} stage={} x_ok={} y_ok={} x={x:#x} want_x={wx:#x} y={y:#x} want_y={wy:#x}",batch*64+lane,m.label,x==wx,y==wy);}}}
 while fcursor<folds.len()&&folds[fcursor].at==idx{let f=&folds[fcursor];fcursor+=1;let w=f.acc.len();let ww=1i128<<w;
 if f.before{let vs=(0..rows.len()).map(|lane|{let l=small(&f.acc,&s.qubits,lane);let e=small(&f.e,&s.qubits,lane);let nm=small(&f.nm,&s.qubits,lane);let sh=3+small(&f.shift,&s.qubits,lane);let d=1i128<<sh;let ff=0x1000003d1i128;let m=if f.rev{let b=small(&f.src,&s.qubits,lane);let kr=(0..3).map(|i|((b ^ if (nm>>i)&1!=0 {63}else{0})<<i)).sum::<i128>();(l-kr).rem_euclid(d)}else{let a=l+e+(e-nm)*(ff-1);(0..d).find(|m|(m*ff-a).rem_euclid(d)==0).unwrap()};let cst=e+(e-nm+if f.rev{m}else{-m})*(ff-1);let c=(l+cst).div_euclid(ww);(l,e,nm,sh,m,cst,c)}).collect();fold_values.insert(f.id,vs);}
 else{let vs=fold_values.remove(&f.id).unwrap();for lane in 0..rows.len(){let(l,e,nm,sh,m,cst,c)=vs[lane];let got=small(&f.acc,&s.qubits,lane);let want=(l+cst).rem_euclid(ww);assert_eq!(got,want,"fold low-window observer mismatch");if c!=0{eprintln!("FOLD_BOUNDARY family={family} shot={} phase={} tick={} rev={} window={w} shift={sh} low_L={l} E={e} Nm={nm} m={m} C={cst} c={c} observed_low={got} low_matches=true",batch*64+lane,f.phase,f.t,f.rev);}}}
 }
 while cursor<marks.len()&&marks[cursor].at==idx{
 let m=&marks[cursor];cursor+=1;let vals:Vec<_>=(0..rows.len()).map(|lane|[word(&m.pay[0],&s.qubits,lane),word(&m.pay[1],&s.qubits,lane)]).collect();
 if m.before{entries.insert(m.id,vals);if m.rev{tapes.insert(m.id,(0..rows.len()).map(|lane|m.letter.iter().map(|q|s.qubits[q.0 as usize]>>lane&1).collect()).collect());}continue;}let before=entries.remove(&m.id).unwrap();let saved_tape=tapes.remove(&m.id);
 for lane in 0..rows.len(){if first[lane]{continue;}let(ti,si)=(m.t%2,1-m.t%2);let a=before[lane][ti];let b=before[lane][si];let source=norm(b,p);let mut want=norm(a,p);
 let tape:Vec<_>=if m.rev{saved_tape.as_ref().unwrap()[lane].clone()}else{m.letter.iter().map(|q|s.qubits[q.0 as usize]>>lane&1).collect()};assert!(tape.len()>=3);let ns=tape.len()-2;let extra=if m.skip{0}else{tape[ns]+2*tape[ns+1]};
 if !m.rev{for &sign in &tape[..ns]{want=half(if sign==0{want.add_mod(source,p)}else{sub(want,source,p)},p);}for _ in 0..extra{want=half(want,p);}}
 else{for _ in 0..extra{want=want.add_mod(want,p);}for &sign in tape[..ns].iter().rev(){want=want.add_mod(want,p);want=if sign==0{sub(want,source,p)}else{want.add_mod(source,p)};}}
 if norm(vals[lane][ti],p)!=want||norm(vals[lane][si],p)!=source{first[lane]=true;total_event+=1;
 eprintln!("PAY_EVENT family={family} shot={} at={} phase={} tick={} rev={} skip={} tape={tape:?} a={a:#x} b={b:#x} got_t={:#x} want_t={want:#x} got_s={:#x} want_s={source:#x} diff={:#x}",batch*64+lane,m.at,m.phase,m.t,m.rev,m.skip,vals[lane][ti],vals[lane][si],sub(norm(vals[lane][ti],p),want,p));}
 }
 }});
 assert_eq!(cursor,marks.len());assert_eq!(fcursor,folds.len());assert_eq!(stage_cursor,stages.len());assert_eq!(window_cursor,windows.len());assert!(entries.is_empty()&&fold_values.is_empty()&&window_entries.is_empty());reference.apply_iter(ops.iter());assert_eq!(sim.qubits,reference.qubits);assert_eq!(sim.bits,reference.bits);assert_eq!(sim.phase,reference.phase);assert_eq!(sim.stats.toffoli_gates,reference.stats.toffoli_gates);if family=="independent"{assert!(stage_first.iter().all(|b|!*b),"stage observer false positives");}
 for(lane,row)in rows.iter().enumerate(){let bad=sim.get_register(&regs[0],lane)!=row[4]||sim.get_register(&regs[1],lane)!=row[5];total_bad+=usize::from(bad);eprintln!("PAY_SHOT family={family} shot={} final_bad={bad} event={} observer_equal=true",batch*64+lane,first[lane]);}
 }
 eprintln!("PAY_SUMMARY family={family} shots={} final_bad={total_bad} first_events={total_event} observer_equal=true score=NONE",rows.len());
 }
}
