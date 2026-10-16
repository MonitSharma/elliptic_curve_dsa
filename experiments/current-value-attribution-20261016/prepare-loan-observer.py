from pathlib import Path
import shutil,json,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');d=r/'source-loan-observer';assert not d.exists()
shutil.copytree(r/'source-observer',d,ignore=shutil.ignore_patterns('.git','target'))
p=d/'src/point_add/payload_trace.rs';s=p.read_text().replace('raw-markers.jsonl','raw-loan-base-markers.jsonl').replace('raw-builder.bin','raw-loan-builder.bin')
s+='''
static LOANS:Mutex<Vec<String>>=Mutex::new(Vec::new());
pub fn loan_mark(at:usize,label:&str,phase:&str,rails:&[Vec<QubitId>;2]){let mut out=LOANS.lock().unwrap();let ids=|v:&[QubitId]|v.iter().map(|q|q.0).collect::<Vec<_>>();let id=out.len();out.push(format!("{{\\"family\\":\\"stage\\",\\"id\\":{id},\\"at\\":{at},\\"label\\":\\"{label}\\",\\"phase\\":\\"{phase}\\",\\"rail0\\":{:?},\\"rail1\\":{:?}}}",ids(&rails[0]),ids(&rails[1])));}
'''
needle='pub fn dump(ops:&[Op]){';assert s.count(needle)==1;s=s.replace(needle,needle+'std::fs::write("/home/hclau/ecdsa_research/current-value-attribution-20261016/raw-loan-markers.jsonl",LOANS.lock().unwrap().join("\\n")+"\\n").unwrap();');p.write_text(s)
p=d/'src/point_add/leapfrog.rs';s=p.read_text()
sig='fn n2_loan_out(c: &mut Builder, wk: &mut Walk, fault: bool) {';assert s.count(sig)==1;s=s.replace(sig,sig.replace('n2_loan_out','n2_loan_out_unobserved'))
s+='\n'+sig+'\nassert!(!fault);super::payload_trace::loan_mark(c.op_count(),"out-before",c.current_phase(),&wk.r);n2_loan_out_unobserved(c,wk,fault);super::payload_trace::loan_mark(c.op_count(),"out-after",c.current_phase(),&wk.r);}\n'
sig='fn n2_loan_in(c: &mut Builder, wk: &mut Walk, mul: bool) {';assert s.count(sig)==1;s=s.replace(sig,sig.replace('n2_loan_in','n2_loan_in_unobserved'))
s+='\n'+sig+'\nsuper::payload_trace::loan_mark(c.op_count(),"in-before",c.current_phase(),&wk.r);n2_loan_in_unobserved(c,wk,mul);super::payload_trace::loan_mark(c.op_count(),"in-after",c.current_phase(),&wk.r);}\n';p.write_text(s)
(r/'loan-source-files.json').write_text(json.dumps({str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(d/'src/point_add').rglob('*')if p.is_file()},indent=2)+'\n')
