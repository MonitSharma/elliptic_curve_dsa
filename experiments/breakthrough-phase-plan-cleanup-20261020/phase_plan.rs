//! Weighted chunk schedules including retained carry phase-erasure space.
use crate::circuit::QubitId;
use std::collections::{BTreeMap,BTreeSet};
#[derive(Clone,Debug,PartialEq,Eq,PartialOrd,Ord)]
pub(super) struct Chunk{pub width:usize,pub drops:Vec<usize>,pub phase_drops:Option<Vec<usize>>}
#[derive(Clone,Debug)]pub(super) struct Plan{pub extra_x4:usize,pub chunks:Vec<Chunk>}
fn rank(a:&[QubitId],b:&[QubitId])->usize{if a.is_empty()||b.is_empty()||a.iter().map(|q|q.0).collect::<BTreeSet<_>>()==b.iter().map(|q|q.0).collect::<BTreeSet<_>>(){1}else{2}}
fn fit(rows:&[Vec<QubitId>],need:usize)->Option<Vec<usize>>{
 if need==0{return Some(Vec::new());}let m=rows.len().saturating_sub(2);if m<3||need>(m-1)/2{return None;}
 super::phase_fit::choose(rows,need,false,&vec![true;rows.len()])
}
pub(super) fn choose(rows:&[Vec<QubitId>],budget:usize)->Option<Plan>{
 fn solve(rows:&[Vec<QubitId>],budget:usize,pos:usize,kept:usize,memo:&mut BTreeMap<(usize,usize),Option<Plan>>)->Option<Plan>{
  if let Some(answer)=memo.get(&(pos,kept)){return answer.clone();}let mut best:Option<Plan>=None;
  if kept<=budget{let room=budget-kept;for width in 1..=rows.len()-pos{
   let last=pos+width==rows.len();let word=&rows[pos..pos+width];let owned=if last{width.saturating_sub(2)}else{width};
   let need=owned.saturating_sub(room);let mut extended=word.to_vec();if !last{extended.push(Vec::new());}
   let Some(drops)=fit(&extended,need)else{continue;};
   let mut extra=2*drops.iter().map(|&j|rank(&extended[j-1],&extended[j])).sum::<usize>();
   let phase_drops=if !last&&width-1>room{
    let Some(pd)=fit(word,(width-2).saturating_sub(room))else{continue;};
    extra+=2*(rank(&word[width-2],&word[width-1])-1)+pd.iter().map(|&j|rank(&word[j-1],&word[j])).sum::<usize>();Some(pd)
   }else{None};
   if !last{extra+=2*(width-1);}
   let tail=if last{Some(Plan{extra_x4:0,chunks:Vec::new()})}else{solve(rows,budget,pos+width,kept+1,memo)};let Some(mut tail)=tail else{continue;};
   tail.extra_x4+=extra;tail.chunks.insert(0,Chunk{width,drops,phase_drops});
   if best.as_ref().is_none_or(|old|(tail.extra_x4,tail.chunks.len(),&tail.chunks)<(old.extra_x4,old.chunks.len(),&old.chunks)){best=Some(tail);}
  }}memo.insert((pos,kept),best.clone());best
 }
 if rows.is_empty(){return None;}solve(rows,budget,0,0,&mut BTreeMap::new())
}
