from pathlib import Path
import shutil,hashlib,json
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');new=r/'observer';old=r.parent/'phase-localization-20261016/source-observer-v2'
shutil.copytree(old,new,ignore=shutil.ignore_patterns('.git','target'),dirs_exist_ok=True)
for p in(new/'src').rglob('*.rs'):
 s=p.read_text().replace('/home/hclau/ecdsa_research/phase-localization-20261016',str(r));p.write_text(s)
p=new/'src/point_add/leapfrog.rs';s=p.read_text();begin=s.index('fn seam_add_reduce(');end=s.index('\n/// Tie-safe payload',begin);part=s[begin:end]
part=part.replace('    let w = r.len();','    eprintln!("BACK_BEGIN\\t{}\\t{:?}\\t{:?}\\t{:?}",c.op_count(),r.iter().map(|q|q.0).collect::<Vec<_>>(),add.iter().map(|b|b.0).collect::<Vec<_>>(),cb.iter().map(|b|b.0).collect::<Vec<_>>());\n    let w = r.len();',1)
needle='    super::modular::r5_ripple_add_cbits(c, add, &low, ov);';assert part.count(needle)==1;part=part.replace(needle,needle+'\n    eprintln!("BACK_R5_END\\t{}\\t{}",c.op_count(),ov.0);')
needle='    super::compare::erase_with_compare(c, ov, &low[N - k..], &tv, None);';assert part.count(needle)==1;part=part.replace(needle,'    eprintln!("BACK_COMPARE\\t{}\\t{}\\t{}\\t{}\\t{}",c.op_count(),ov.0,low[N-k-1].0,cb[N-k-1].0,k);\n'+needle)
needle='    low\n}';assert part.count(needle)==1;part=part.replace(needle,'    eprintln!("BACK_END\\t{}",c.op_count());\n'+needle)
s=s[:begin]+part+s[end:];p.write_text(s)
(r/'observer-source-hashes.json').write_text(json.dumps({str(p.relative_to(new)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(new/'src').rglob('*')if p.is_file()},indent=2)+'\n')
