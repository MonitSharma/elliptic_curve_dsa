from pathlib import Path
import shutil,hashlib,json
r=Path('/home/hclau/ecdsa_research/quantum-borrow-family-20261016')
old=r.parent/'free-borrow-family-20261016/observer';new=r/'frame-observer'
shutil.copytree(old,new,ignore=shutil.ignore_patterns('.git','target'),dirs_exist_ok=True)
for p in (new/'src').rglob('*.rs'):
 s=p.read_text().replace('/home/hclau/ecdsa_research/free-borrow-family-20261016',str(r));p.write_text(s)
p=new/'src/point_add/pingpong.rs';s=p.read_text();needle='        erase_with_compare(circ, overflow, &target[N - k..], &source[N - k..], borrow);';assert s.count(needle)==1
s=s.replace(needle,'        eprintln!("QUANTUM_FLAG_FRAME\\t{}\\t{}\\t{}\\t{}\\t{}\\t{:?}\\t{:?}\\t{:?}",circ.op_count(),round,multiply as u8,k,overflow.0,target.iter().map(|q|q.0).collect::<Vec<_>>(),source.iter().map(|q|q.0).collect::<Vec<_>>(),borrow.map(|q|q.0));\n'+needle);p.write_text(s)
(r/'frame-observer-source-hashes.json').write_text(json.dumps({str(p.relative_to(new)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(new/'src').rglob('*')if p.is_file()},indent=2)+'\n')
print('Gate-inert full flag_erase frames inserted exactly once in source function')
