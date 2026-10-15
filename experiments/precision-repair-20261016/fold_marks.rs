//! Gate-inert production fold metadata. No gates are emitted here.
use crate::circuit::QubitId;
use std::sync::Mutex;
#[derive(Clone)]struct Mark{at:usize,id:usize,before:bool,rev:bool,t:usize,acc:Vec<QubitId>,e:[QubitId;3],nm:[QubitId;3],shift:[QubitId;2],src:Vec<QubitId>}
static MARKS:Mutex<Vec<Mark>>=Mutex::new(Vec::new());
pub fn begin(at:usize,rev:bool,t:usize,acc:&[QubitId],e:[QubitId;3],nm:[QubitId;3],k1:QubitId,k2:QubitId,src:&[QubitId])->usize{let mut ms=MARKS.lock().unwrap();let id=ms.len();ms.push(Mark{at,id,before:true,rev,t,acc:acc.to_vec(),e,nm,shift:[k1,k2],src:src.to_vec()});id}
pub fn end(id:usize,at:usize){let mut ms=MARKS.lock().unwrap();let mut m=ms.iter().find(|m|m.id==id&&m.before).unwrap().clone();m.at=at;m.before=false;ms.push(m);}
pub fn dump(ops:&[crate::circuit::Op]){use std::io::Write;let root="/home/hclau/ecdsa_research/precision-repair-20261016";let mut ms=MARKS.lock().unwrap().clone();ms.sort_by_key(|m|m.at);let mut f=std::fs::File::create(format!("{root}/fold-marks.tsv")).unwrap();let ids=|q:&[QubitId]|q.iter().map(|q|q.0.to_string()).collect::<Vec<_>>().join(",");for m in &ms{writeln!(f,"{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",m.at,m.id,u8::from(m.before),u8::from(m.rev),m.t,ids(&m.acc),ids(&m.e),ids(&m.nm),ids(&m.shift),if m.src.is_empty(){"-".to_string()}else{ids(&m.src)}).unwrap();}crate::write_ops(ops,std::path::Path::new(&format!("{root}/raw-builder.bin"))).unwrap();eprintln!("PRODUCTION_FOLD_MARKS rows={} raw_ops={} score=NONE",ms.len(),ops.len());}
