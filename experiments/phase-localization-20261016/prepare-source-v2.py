from pathlib import Path
import shutil,hashlib,json
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016');old=r/'source-observer';new=r/'source-observer-v2'
shutil.copytree(old,new,ignore=shutil.ignore_patterns('.git','target'),dirs_exist_ok=True)
p=new/'src/point_add/compare.rs';s=p.read_text();needle='    let n = u.len();';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    eprintln!("PHASE_CMP\\t{}\\t{:?}\\t{:?}\\t{:?}\\t{:?}",circ.op_count(),u.iter().map(|q|q.0).collect::<Vec<_>>(),v.iter().map(|q|q.0).collect::<Vec<_>>(),borrow_in.map(|q|q.0),super::leapfrog::C35_AT.with(|x|x.get()));')
p.write_text(s)
p=new/'src/point_add/pingpong.rs';s=p.read_text();needle='    pub(crate) fn y15_erase_cmp(';assert s.count(needle)==1;s=s.replace(needle,'    #[track_caller]\n'+needle);p.write_text(s)
(r/'source-observer-v2-hashes.json').write_text(json.dumps({str(p.relative_to(new)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(new/'src').rglob('*')if p.is_file()},indent=2)+'\n')
