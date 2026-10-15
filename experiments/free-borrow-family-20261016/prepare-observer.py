from pathlib import Path
import shutil,json,hashlib
r=Path('/home/hclau/ecdsa_research/free-borrow-family-20261016');r.mkdir(exist_ok=True)
new=r/'observer';old=r.parent/'phase-localization-20261016/source-observer-v2'
shutil.copytree(old,new,ignore=shutil.ignore_patterns('.git','target'),dirs_exist_ok=True)
for p in (new/'src').rglob('*.rs'):
 s=p.read_text().replace('/home/hclau/ecdsa_research/phase-localization-20261016',str(r));p.write_text(s)
p=new/'src/point_add/pingpong.rs';s=p.read_text();needle='            erase_with_compare(circ, carry, &acc[window.clone()], &addend[window], borrow);';assert s.count(needle)==1
s=s.replace(needle,'            eprintln!("FREE_BORROW_CHUNK\\t{}\\t{}\\t{}\\t{}\\t{:?}\\t{:?}\\t{:?}",circ.op_count(),round,multiply as u8,window.start,acc.iter().map(|q|q.0).collect::<Vec<_>>(),addend.iter().map(|q|q.0).collect::<Vec<_>>(),borrow.map(|q|q.0));\n'+needle);p.write_text(s)
p=new/'src/point_add/y15_onefold.rs';s=p.read_text();needle='super::super::compare::cmp_lt_phase(c, &tg[lo..split], &b[lo..split], seed0.map(|sd| b[sd]));';count=s.count(needle);assert count>=1
s=s.replace(needle,'eprintln!("FREE_BORROW_TOP1\\t{}\\t{}\\t{:?}\\t{:?}\\t{:?}",c.op_count(),lo,tg.iter().map(|q|q.0).collect::<Vec<_>>(),b.iter().map(|q|q.0).collect::<Vec<_>>(),seed0.map(|sd| b[sd].0)); '+needle);p.write_text(s)
(r/'source-hashes.json').write_text(json.dumps({str(p.relative_to(new)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(new/'src').rglob('*')if p.is_file()},indent=2)+'\n')
print('source-only gate-inert observers; TOP1 call replacements',count)
