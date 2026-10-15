from pathlib import Path
import shutil,hashlib,json
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016');old=r.parent/'prefilter-macro-20261016/observer-tip';new=r/'source-observer'
shutil.copytree(old,new,ignore=shutil.ignore_patterns('.git','target'),dirs_exist_ok=True)
for owned in(new/'src').rglob('*.rs'):
 s=owned.read_text();s=s.replace('/home/hclau/ecdsa_research/prefilter-macro-20261016',str(r));owned.write_text(s)
p=new/'src/point_add/builder.rs';s=p.read_text();needle='    pub fn hmr(&mut self, q: QubitId, c: BitId) {';assert s.count(needle)==1
s=s.replace(needle,'    #[track_caller]\n'+needle+'\n        let caller=std::panic::Location::caller();\n        eprintln!("PHASE_HMR\\t{}\\t{}\\t{}\\t{}\\t{}",self.op_count(),q.0,c.0,caller.file(),caller.line());')
p.write_text(s)
(r/'source-observer-hashes.json').write_text(json.dumps({str(p.relative_to(new)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(new/'src').rglob('*')if p.is_file()},indent=2)+'\n')
