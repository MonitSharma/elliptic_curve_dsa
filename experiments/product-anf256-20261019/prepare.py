import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
s=(ws/'product-anf-20261019/anf.rs').read_text()
old='assert_eq!(a.len(),3);let v=io::load_ops(&a[1]);let mut alg=Algebra{next:1,cap:64,degree:8,cuts:0};'
assert s.count(old)==1;s=s.replace(old,'assert_eq!(a.len(),4);let v=io::load_ops(&a[1]);assert_eq!(hash(&v),a[3]);let mut alg=Algebra{next:1,cap:256,degree:12,cuts:0};')
s+='\n#[cfg(test)] #[path="tests_large.rs"] mod large_tests;\n'
(r/'anf.rs').write_text(s,newline='\n');shutil.copy2(ws/'product-classical-cap11-20261019/io.rs',r/'io.rs');shutil.copy2(ws/'product-classical-cap11-20261019/factor_trace.rs',r/'factor_trace.rs')
(r/'PREPARATION.json').write_text(json.dumps({'status':'SOURCE_ONLY_FIXED_ANF256_DEGREE12_PREPARED','source_parent':'product-anf-20261019/anf.rs','parent_sha256':hashlib.sha256((ws/'product-anf-20261019/anf.rs').read_bytes()).hexdigest(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.glob('*.rs')},'source_sha3_expected':'2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265','no_nonce_or_gate':True},indent=2)+'\n')
