from pathlib import Path
import shutil,json,hashlib,difflib
r=Path(__file__).resolve().parent;old=r.parent/'repair67-fused-filter-20261016';tool=r/'tool';assert not tool.exists()
assert hashlib.sha256((old/'evidence.tar.gz').read_bytes()).hexdigest()=='7af8c67adb7698f01a43af981b8f1a6c78930d1178dc65ac5fbc69bbcf2de85b'
for name,h in json.loads((r/'PRECURSOR_SOURCE_PINS.json').read_text()).items():assert hashlib.sha256((old/name).read_bytes()).hexdigest()==h,name
shutil.copytree(old/'tool/src',tool/'src')
for n in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/n,tool/n)
def exact(s,a,b,n=1):assert s.count(a)==n,(a,s.count(a),n);return s.replace(a,b)
shutil.copyfile(r/'profile.rs',tool/'src/profile.rs')
p=tool/'src/main.rs';p.write_bytes(('mod profile;\n'+p.read_text()).encode())
p=tool/'src/packed_body.rs';s=p.read_text()
a='fn next_witness(&mut self,curve:&FastCurveC,model:&RailAdvisory)->Option<(usize,usize)>{';s=exact(s,a,a+'let _t=profile::span(33);')
s=exact(s,'self.candidates=rail_flags(model,&self.packet.batches[batch]).iter().enumerate().filter_map(|(i,f)|(*f!=0).then_some((batch,i))).collect();self.cursor=0;',
 'let flags=rail_flags(model,&self.packet.batches[batch]);self.candidates=profile::measure(30,||flags.iter().enumerate().filter_map(|(i,f)|(*f!=0).then_some((batch,i))).collect());profile::units(30,self.candidates.len()as u64);self.cursor=0;')
a='fn ensure(&mut self,batch:usize,curve:&FastCurveC)->bool{';s=exact(s,a,a+'let _t=profile::span(31);')
s=exact(s,'let mut pts=Vec::with_capacity(64);','let mut pts=profile::measure(24,||Vec::with_capacity(64));')
s=exact(s,'let mut raw=vec![0u8;count*64];XofReader::read(&mut self.reader,&mut raw);let mut scalars=Vec::with_capacity(count*2);\n    for r in raw.chunks_exact(64){scalars.push(U256::from_le_slice(&r[..32]));scalars.push(U256::from_le_slice(&r[32..]));}self.next+=count;',
 'let mut raw=profile::measure(16,||vec![0u8;count*64]);profile::measure(17,||XofReader::read(&mut self.reader,&mut raw));profile::units(17,raw.len()as u64);let scalars=profile::measure(18,||{let mut v=Vec::with_capacity(count*2);for r in raw.chunks_exact(64){v.push(U256::from_le_slice(&r[..32]));v.push(U256::from_le_slice(&r[32..]));}v});self.next+=count;')
s=exact(s,'for(t,o,e)in curve.points_with_sums(&scalars){if t.0!=o.0&&!(t.0.is_zero()&&t.1.is_zero())&&!(o.0.is_zero()&&o.1.is_zero()){pts.push((t,o,e));}}',
 'let triples=curve.points_with_sums(&scalars);profile::measure(23,||{for(t,o,e)in triples{if t.0!=o.0&&!(t.0.is_zero()&&t.1.is_zero())&&!(o.0.is_zero()&&o.1.is_zero()){pts.push((t,o,e));}}});')
s=exact(s,'self.batches.push(pts);','profile::measure(34,||self.batches.push(pts));')
a='fn prepare_packets(_base:&Shake8,hash:&Shake256,tail:&[Op],nonces:[u64;8],valid:[bool;8])->Vec<CandidatePacket>{';s=exact(s,a,a+'let _t=profile::span(15);profile::units(15,valid.iter().filter(|v|**v).count()as u64);')
s=exact(s,'fn main(){','fn main(){profile::begin_main();')
s=exact(s,'sha_check(&a[1],"0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b");let ops=load_ops(&a[1]).unwrap();',
 'profile::measure(0,||sha_check(&a[1],"0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b"));let ops=profile::measure(1,||load_ops(&a[1]).unwrap());')
s=exact(s,'bind_transfer();','profile::measure(2,||bind_transfer());')
s=exact(s,'let(nq,nb,_,regs)=analyze_ops(ops.iter());','let(nq,nb,_,regs)=profile::measure(3,||analyze_ops(ops.iter()));')
s=exact(s,'let mut base=Shake8::new();','let prefix_clock=profile::span(5);let mut base=profile::measure(4,||Shake8::new());')
s=exact(s,'base.same(bytes);hash.update(bytes);','profile::measure(6,||base.same(bytes));profile::measure(7,||hash.update(bytes));')
s=exact(s,'base.same(&encoded);hash.update(&encoded);','profile::measure(6,||base.same(&encoded));profile::measure(7,||hash.update(&encoded));',2)
s=exact(s,'\n if std::env::var_os("CANDIDATE_SEED_SHADOW")','\n drop(prefix_clock);\n if std::env::var_os("CANDIDATE_SEED_SHADOW")')
s=exact(s,'check_candidate_seeds(&ops,&hash,tail);','profile::measure(8,||check_candidate_seeds(&ops,&hash,tail));')
s=exact(s,'let curve=FastCurveC::new(20);let model=RailAdvisory::new(&a[6]);let program=zero_program();mask_program();let full=Compact::compile(&ops[..n-TAIL]);',
 'let curve=profile::measure(9,||FastCurveC::new(20));let model=profile::measure(11,||RailAdvisory::new(&a[6]));let program=profile::measure(12,||zero_program());profile::measure(13,||mask_program());let full=profile::measure(14,||Compact::compile(&ops[..n-TAIL]));')
s=exact(s,'let start=std::time::Instant::now();','profile::end_startup();let start=std::time::Instant::now();')
s=exact(s,'start.elapsed().as_secs_f64());','start.elapsed().as_secs_f64());profile::report();')
assert 'const PROOF_ACCEPTED:bool=false;'in s;p.write_bytes(s.encode())
p=tool/'src/fast_curve_c.rs';s=p.read_text()
s=exact(s,'assert_ne!(init(window as u32),0,','assert_ne!(profile::measure(10,||unsafe{init(window as u32)}),0,')
s=exact(s,'let mut input=Vec::with_capacity(scalars.len()*32);for scalar in scalars{input.extend_from_slice(&scalar.to_be_bytes::<32>());}let mut output=vec![0u8;count*192];',
 'let input=profile::measure(19,||{let mut v=Vec::with_capacity(scalars.len()*32);for scalar in scalars{v.extend_from_slice(&scalar.to_be_bytes::<32>());}v});let mut output=profile::measure(20,||vec![0u8;count*192]);profile::units(21,count as u64);')
s=exact(s,'assert_ne!(unsafe{(C_BACKEND.get().unwrap().pairs)(count as u32,input.as_ptr(),output.as_mut_ptr())},0);',
 'assert_ne!(profile::measure(21,||unsafe{(C_BACKEND.get().unwrap().pairs)(count as u32,input.as_ptr(),output.as_mut_ptr())}),0);')
s=exact(s,'output.chunks_exact(192).map(|row|{let point=|off| (U256::from_be_slice(&row[off..off+32]),U256::from_be_slice(&row[off+32..off+64]));(point(0),point(64),point(128))}).collect()',
 'profile::measure(22,||output.chunks_exact(192).map(|row|{let point=|off| (U256::from_be_slice(&row[off..off+32]),U256::from_be_slice(&row[off+32..off+64]));(point(0),point(64),point(128))}).collect())')
p.write_bytes(s.encode())
p=tool/'src/rail_fast_ffi.rs';s=p.read_text()
s=exact(s,'get_or_init(||unsafe{let path=','get_or_init(||unsafe{let _init=profile::span(25);let path=')
s=exact(s,'let mut input=Vec::with_capacity(points.len()*8);for(t,o,e)in points{input.extend_from_slice(model.sub(t.0,o.0).as_limbs());input.extend_from_slice(model.sub(o.0,e.0).as_limbs());}let mut flags=vec![0u8;points.len()];',
 'let input=profile::measure(26,||{let mut v=Vec::with_capacity(points.len()*8);for(t,o,e)in points{v.extend_from_slice(model.sub(t.0,o.0).as_limbs());v.extend_from_slice(model.sub(o.0,e.0).as_limbs());}v});let mut flags=profile::measure(27,||vec![0u8;points.len()]);profile::units(28,points.len()as u64);')
s=exact(s,'assert_eq!(unsafe{(backend.run)(backend.steps.as_ptr(),backend.steps.len(),input.as_ptr(),points.len(),flags.as_mut_ptr())},0);',
 'assert_eq!(profile::measure(28,||unsafe{(backend.run)(backend.steps.as_ptr(),backend.steps.len(),input.as_ptr(),points.len(),flags.as_mut_ptr())}),0);')
s=exact(s,'if backend.shadow{for((t,o,e),flag)in points.iter().zip(&flags){assert_eq!(*flag,model.flags(*t,*o,*e),"SIMD advisory mismatch");}}',
 'if backend.shadow{profile::measure(29,||{for((t,o,e),flag)in points.iter().zip(&flags){assert_eq!(*flag,model.flags(*t,*o,*e),"SIMD advisory mismatch");}});}')
p.write_bytes(s.encode())
pins={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(tool.rglob('*'))if p.is_file()}
(r/'PREPARED_SOURCE.json').write_bytes((json.dumps(pins,indent=2)+'\n').encode())
diff=''
for p in sorted((tool/'src').iterdir()):
 if p.is_file():
  a=old/'tool/src'/p.name;before=a.read_text().splitlines(True)if a.exists()else[]
  diff+=''.join(difflib.unified_diff(before,p.read_text().splitlines(True),fromfile='frozen-ab8/'+p.name,tofile='instrumented/'+p.name))
(r/'SOURCE-DIFF.patch').write_bytes(diff.encode());print(json.dumps({'status':'INSTRUMENTATION_ONLY_DISABLED_SOURCE_PREPARED','source_files':len(pins)}))
