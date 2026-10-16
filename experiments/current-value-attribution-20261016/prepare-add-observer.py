from pathlib import Path
import shutil,json,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');d=r/'source-add-observer'
assert not d.exists();shutil.copytree(r/'source-observer',d,ignore=shutil.ignore_patterns('.git','target'))
p=d/'src/point_add/payload_trace.rs';s=p.read_text().replace('raw-markers.jsonl','raw-add-base-markers.jsonl').replace('raw-builder.bin','raw-add-builder.bin')
s+='''
static ADDS:Mutex<Vec<String>>=Mutex::new(Vec::new());
pub fn add_mark(at:usize,id:usize,before:bool,b:&[QubitId],acc:&[QubitId],carry:Option<QubitId>)->usize{
let mut adds=ADDS.lock().unwrap();let id=if before{adds.len()}else{id};let marks=MARKS.lock().unwrap();let m=marks.last().unwrap();let ids=|v:&[QubitId]|v.iter().map(|q|q.0).collect::<Vec<_>>();adds.push(format!("{{\\"family\\":\\"add\\",\\"id\\":{id},\\"at\\":{at},\\"before\\":{before},\\"phase\\":\\"{}\\",\\"tick\\":{},\\"rev\\":{},\\"b\\":{:?},\\"acc\\":{:?},\\"carry\\":{}}}",m.phase,m.t,m.rev,ids(b),ids(acc),carry.map_or("null".to_string(),|q|q.0.to_string())));id}
'''
needle='pub fn dump(ops:&[Op]){';assert s.count(needle)==1;s=s.replace(needle,needle+'std::fs::write("/home/hclau/ecdsa_research/current-value-attribution-20261016/raw-add-markers.jsonl",ADDS.lock().unwrap().join("\\n")+"\\n").unwrap();')
p.write_text(s)
p=d/'src/point_add/y15_onefold.rs';s=p.read_text();sig='fn low_keep_add(c: &mut Builder, b: &[QubitId], acc: &[QubitId], proxy: usize, rev: bool, keep: usize) -> (QubitId, Vec<QubitId>) {';assert s.count(sig)==1;s=s.replace(sig,sig.replace('low_keep_add','low_keep_add_unobserved'))
s+='\n'+sig+'\nlet id=super::super::payload_trace::add_mark(c.op_count(),0,true,b,acc,None);let out=low_keep_add_unobserved(c,b,acc,proxy,rev,keep);super::super::payload_trace::add_mark(c.op_count(),id,false,b,acc,Some(out.0));out\n}\n';p.write_text(s)
(r/'add-source.patch').write_text('RESEARCH SOURCE CLONE ONLY; parent snapshot unchanged\n')
(r/'add-source-files.json').write_text(json.dumps({str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (d/'src/point_add').rglob('*')if p.is_file()},indent=2)+'\n')
print('Prepared source-bound generic low_keep_add marker family; all calls, no gate changes.')
