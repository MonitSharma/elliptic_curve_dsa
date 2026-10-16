from pathlib import Path
import shutil,json,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');d=r/'source-seed-observer';assert not d.exists()
shutil.copytree(r/'source-observer',d,ignore=shutil.ignore_patterns('.git','target'))
p=d/'src/point_add/payload_trace.rs';s=p.read_text().replace('raw-markers.jsonl','raw-seed-base-markers.jsonl').replace('raw-builder.bin','raw-seed-builder.bin')
s+='''
static SEEDS:Mutex<Vec<String>>=Mutex::new(Vec::new());
pub fn seed_mark(at:usize,id:usize,before:bool,target:&[QubitId])->usize{
let mut ms=SEEDS.lock().unwrap();let id=if before{ms.len()}else{id};let ids=target.iter().map(|q|q.0).collect::<Vec<_>>();ms.push(format!("{{\\\"family\\\":\\\"seed\\\",\\\"id\\\":{id},\\\"at\\\":{at},\\\"before\\\":{before},\\\"target\\\":{ids:?}}}"));id}
'''
needle='pub fn dump(ops:&[Op]){';assert s.count(needle)==1;s=s.replace(needle,needle+'std::fs::write("/home/hclau/ecdsa_research/current-value-attribution-20261016/raw-seed-markers.jsonl",SEEDS.lock().unwrap().join("\\n")+"\\n").unwrap();');p.write_text(s)
p=d/'src/point_add/pingpong.rs';s=p.read_text();sig='fn mod_halve_pm(circ: &mut Builder, target: &[QubitId]) {';assert s.count(sig)==1
s=s.replace(sig,sig.replace('mod_halve_pm','mod_halve_pm_unobserved'));s+='\n'+sig+'\nlet id=super::payload_trace::seed_mark(circ.op_count(),0,true,target);mod_halve_pm_unobserved(circ,target);super::payload_trace::seed_mark(circ.op_count(),id,false,target);\n}\n';p.write_text(s)
(r/'seed-source-files.json').write_text(json.dumps({str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(d/'src/point_add').rglob('*')if p.is_file()},indent=2)+'\n')
print('ALL mod_halve_pm source instances, gate-inert boundary observation; no gate edits')
