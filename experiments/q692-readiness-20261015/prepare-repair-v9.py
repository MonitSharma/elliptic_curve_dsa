"""Preserve failed v8; correct SZ9 handling and update explicit configuration checks."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path(sys.argv[1]); original=root/'candidate-repair-v8'; dest=root/'candidate-repair-v9'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-hardlinks',str(original),str(dest)],check=True)
shutil.copytree(original/'src/point_add',dest/'src/point_add',dirs_exist_ok=True)
p=dest/'src/point_add/midg.rs';s=p.read_text(encoding='utf8');assert s.count('assert_eq!(sz.len(),8);assert!(sy.len()>=7);')==1
s=s.replace('assert_eq!(sz.len(),8);assert!(sy.len()>=7);','assert!(sz.len()==8 || sz.len()==9);assert!(sy.len()>=7);');p.write_text(s,encoding='utf8',newline='\n')
p=dest/'src/point_add/tests_frogdrop.rs';s=p.read_text(encoding='utf8')
old='assert!(!cp.sw && cp.emax == 21 && cp.n == 275);';assert s.count(old)==1
s=s.replace(old,'assert!(!cp.sw && cp.emax == super::pointadd_frogdrop::EMAX && cp.n == 275);')
old='(275, 21, 28, (0, 0))';assert s.count(old)==1
s=s.replace(old,'(275, super::pointadd_frogdrop::EMAX, 28, (0, 0))');p.write_text(s,encoding='utf8',newline='\n')
subprocess.run(['git','-C',str(dest),'add','--','src/point_add/'],check=True)
patch=subprocess.check_output(['git','-C',str(dest),'diff','--cached','--binary','--full-index','HEAD','--','src/point_add/']);(root/'candidate-repair-v9.patch').write_bytes(patch)
manifest=dict(scope='UNQUALIFIED arithmetic repair prototype; v8 plus SZ9 acceptance and configuration-aware map tests; no nonce change',candidate=str(dest),base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((dest/'src/point_add').rglob('*')) if p.is_file()})
(root/'candidate-repair-v9-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8');print(json.dumps(manifest,indent=2))
