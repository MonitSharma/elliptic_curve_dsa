//! Weighted, retained-boundary chunk plans. Component experiment only.
use crate::circuit::QubitId;
use std::collections::BTreeMap;
#[derive(Clone,Debug,PartialEq,Eq,PartialOrd,Ord)]
pub(super) struct Chunk {pub width:usize,pub drops:Vec<usize>}
#[derive(Clone,Debug)]
pub(super) struct Plan {pub extra_x2:usize,pub chunks:Vec<Chunk>}
fn rank(a:&[QubitId],b:&[QubitId])->usize {
    if a.is_empty()||b.is_empty()||a.iter().map(|q|q.0).collect::<std::collections::BTreeSet<_>>()==b.iter().map(|q|q.0).collect::<std::collections::BTreeSet<_>>(){1}else{2}
}
pub(super) fn choose(rows:&[Vec<QubitId>],budget:usize)->Option<Plan>{
    fn solve(rows:&[Vec<QubitId>],budget:usize,pos:usize,kept:usize,memo:&mut BTreeMap<(usize,usize),Option<Plan>>)->Option<Plan>{
        if let Some(answer)=memo.get(&(pos,kept)){return answer.clone();}
        let mut best:Option<Plan>=None;
        if kept<=budget {for width in 1..=rows.len()-pos{
            let last=pos+width==rows.len();let owned=if last{width.saturating_sub(2)}else{width};
            let need=owned.saturating_sub(budget-kept);let m=if last{width.saturating_sub(2)}else{width-1};
            if need>0&&(m<3||need>(m-1)/2){continue;}
            let mut word=rows[pos..pos+width].to_vec();if !last{word.push(Vec::new());}
            let drops=if need==0{Vec::new()}else{match super::phase_fit::choose(&word,need,false,&vec![true;word.len()]){Some(d)=>d,None=>continue}};
            let tail=if last{Some(Plan{extra_x2:0,chunks:Vec::new()})}else{solve(rows,budget,pos+width,kept+1,memo)};
            let Some(mut tail)=tail else{continue;};
            let extra=(if last{0}else{width-1})+drops.iter().map(|&j|rank(&word[j-1],&word[j])).sum::<usize>();
            tail.extra_x2+=extra;tail.chunks.insert(0,Chunk{width,drops});
            if best.as_ref().is_none_or(|old|(tail.extra_x2,tail.chunks.len(),&tail.chunks)<(old.extra_x2,old.chunks.len(),&old.chunks)){best=Some(tail);}
        }}
        memo.insert((pos,kept),best.clone());best
    }
    if rows.is_empty(){return None;}solve(rows,budget,0,0,&mut BTreeMap::new())
}
