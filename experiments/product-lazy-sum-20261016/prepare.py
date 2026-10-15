from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'product-dispatch-filter-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
for name in ['fast_curve_c.rs','lazy.rs']:shutil.copyfile(root/name,tool/'src'/name)
s=(tool/'src/packed_body.rs').read_text();assert 'const PROOF_ACCEPTED:bool=false;' in s
s='include!("lazy.rs");\n'+s
needle='self.cursor+=1;self.attempts+=1;return Some(r);';assert s.count(needle)==1
s=s.replace(needle,'self.cursor+=1;self.attempts+=1;self.packet.expected_one(r.0,r.1,curve);self.packet.assert_expected(r.0,r.1);return Some(r);')
needle='next:usize,batches:Vec<Vec<PointTriple>>';assert s.count(needle)==1
s=s.replace(needle,needle+',expected_ready:Vec<u64>,defer:bool')
needle='curve.points_with_sums(&scalars)';assert s.count(needle)==1;s=s.replace(needle,'curve.prepare(&scalars,self.defer)')
needle='self.batches.push(pts);';assert s.count(needle)==1;s=s.replace(needle,'let ready=if self.defer{0}else{if pts.len()==64{u64::MAX}else{(1u64<<pts.len())-1}};self.expected_ready.push(ready);'+needle)
needle='batches:Vec::new()';assert s.count(needle)==1;s=s.replace(needle,needle+',expected_ready:Vec::new(),defer:curve.deferred()')
# prepare_packets currently has no curve argument; the shared backend was
# initialized before its only call sites, and the mode is immutable.
s=s.replace('defer:curve.deferred()','defer:C_BACKEND.get().unwrap().inputs.is_some()')
needle='let model=RailAdvisory::new(&a[6]);';assert s.count(needle)==1
s=s.replace(needle,'if std::env::var_os("DEFER_SUM_SHADOW").is_some(){validate_lazy_packet(&hash,tail,&curve);}'+needle)
(tool/'src/packed_body.rs').write_text(s)
s=(tool/'src/early.rs').read_text();needle='assert_eq!(packet.next,NUM_TESTS);';assert s.count(needle)==1;s=s.replace(needle,needle+'packet.expected_all(curve);')
needle='batches:Vec::new()';assert s.count(needle)==1;s=s.replace(needle,needle+',expected_ready:Vec::new(),defer:curve.deferred()');(tool/'src/early.rs').write_text(s)
