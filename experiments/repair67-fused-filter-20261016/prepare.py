from pathlib import Path
import shutil,hashlib,json,difflib
r=Path(__file__).resolve().parent;old=r.parent/'repair67-conditional-filter-20261016';tool=r/'tool'
assert not tool.exists()
assert hashlib.sha256((old/'evidence.tar.gz').read_bytes()).hexdigest()=='db095518788bfafb6cdf0ded3a1172a9e570a14988e48a502d13ab76d71d70f0'
assert (old/'run-v2.exit').read_text().strip()=='0'
for name,digest in json.loads((r/'PRECURSOR_SOURCE_PINS.json').read_text()).items():assert hashlib.sha256((old/name).read_bytes()).hexdigest()==digest,name
shutil.copytree(old/'tool/src',tool/'src')
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
def exact(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
p=tool/'src/guard.rs';s=p.read_text();s=exact(s,'fn guard_safe(points:','fn guard_safe_raw(points:');s='include!("fused_guard.rs");\n'+s;p.write_bytes(s.encode())
shutil.copyfile(r/'fused_guard.rs',tool/'src/fused_guard.rs')
p=tool/'src/packed_body.rs';s=p.read_text()
s=exact(s,'validate_fixed_transfer(&program,original.as_ref().unwrap(),&ops,&regs,nq,nb);','validate_guard_components();validate_fixed_transfer(&program,original.as_ref().unwrap(),&ops,&regs,nq,nb);')
assert 'const PROOF_ACCEPTED:bool=false;' in s and 'assert!(!PROOF_ACCEPTED' in s
p.write_bytes(s.encode())
p=tool/'src/fast_curve_c.rs';s=p.read_text();s=exact(s,'let path=CString::new(path).unwrap();','sha_check(&path,"3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f");let path=CString::new(path).unwrap();');p.write_bytes(s.encode())
pins={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(tool.rglob('*'))if p.is_file()}
(r/'PREPARED_SOURCE.json').write_bytes((json.dumps(pins,indent=2)+'\n').encode())
diff=''
for p in sorted((tool/'src').iterdir()):
 if not p.is_file():continue
 before=old/'tool/src'/p.name
 a=before.read_text().splitlines(True)if before.exists()else[];b=p.read_text().splitlines(True)
 if a!=b:diff+=''.join(difflib.unified_diff(a,b,fromfile='frozen-precursor/'+p.name,tofile='optional-fused/'+p.name))
(r/'SOURCE-DIFF.patch').write_bytes(diff.encode())
print(json.dumps({'status':'PRIVATE_DISABLED_SOURCE_PREPARED','files':len(pins),'proof_accepted':False}))
