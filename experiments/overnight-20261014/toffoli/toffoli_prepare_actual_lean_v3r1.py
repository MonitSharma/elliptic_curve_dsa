"""Prepare narrowed fin3/drop0 candidate and frozen ALLMR kernel."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[3];here=Path(__file__).parent
out=root/'research-output/overnight-20261014/toffoli/actual-lean-v3r1-source';out.mkdir(parents=True,exist_ok=True)
source=(root/'agents/product/src/point_add/y15_onefold.rs').read_bytes().replace(b'\r\n',b'\n')
assert hashlib.sha256(source).hexdigest()=='879b85060f6a5cfa412561d64860f1cab697f7a334f180f5be9102070d5a23b9'
text=source.decode();declaration='thread_local! { static TOFFOLI_ACTUAL_LEAN_MODE:std::cell::Cell<bool>=const{std::cell::Cell::new(false)}; static TOFFOLI_ACTUAL_LEAN_HITS:std::cell::Cell<usize>=const{std::cell::Cell::new(0)}; static TOFFOLI_ACTUAL_LEAN_C6:std::cell::Cell<Option<QubitId>>=const{std::cell::Cell::new(None)}; }\n'
text=text.replace('use super::*;\n','use super::*;\n'+declaration,1)
begin=text.index('fn fold_fwd_v2(');needle='    recs.push(Rec::UndoC6);';at=text.index(needle,begin)+len(needle)
text=text[:at]+'\n    TOFFOLI_ACTUAL_LEAN_C6.with(|x|x.set(Some(c6)));'+text[at:]
old='    ladder_d(c, acc, &add, 6, c6, &plan, &drops);\n    let (c4, c5) = if lean_m {';assert text.count(old)==1
new='''    ladder_d(c, acc, &add, 6, c6, &plan, &drops);
    if TOFFOLI_ACTUAL_LEAN_MODE.with(|x|x.get()) && loan && fin==3 && ttm && lean_m && drop==0 {
        assert!(esh.is_none(),"narrowed fin3 has original E available");
        toffoli_actual_lean_cleanup_v3::run(c,acc,e,nm,[k1,k2],c3,c6,&a4,&a5,recs);
        TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.set(x.get()+1));LOAN_ACTIVE.with(|x|x.set(false));return plan;
    }
    let (c4, c5) = if lean_m {'''
text=text.replace(old,new)
text+='\n#[path="toffoli_actual_lean_cleanup_v3.rs"]\nmod toffoli_actual_lean_cleanup_v3;\n#[cfg(test)]\n#[path="toffoli_actual_lean_tests_v3.rs"]\nmod toffoli_actual_lean_tests_v3;\n#[cfg(test)]\n#[path="toffoli_actual_lean_phase_kernel_v3.rs"]\nmod toffoli_actual_lean_phase_kernel_v3;\n'
(out/'y15_onefold.rs').write_bytes(text.encode())
for name in ['toffoli_actual_lean_cleanup_v3.rs','toffoli_actual_lean_tests_v3.rs']:
    data=(here/name).read_bytes().replace(b'\r\n',b'\n')
    if name.endswith('tests_v3.rs'):
        text_test=data.decode().replace('let (nq,nb,emitted,_)=analyze_ops(ops.iter());', 'let (nq,nb,_,_)=analyze_ops(ops.iter());let emitted=ops.iter().filter(|op|op.kind==OperationType::CCX).count();').replace('let (_,_,emitted,_)=analyze_ops(ops.iter());', 'let emitted=ops.iter().filter(|op|op.kind==OperationType::CCX).count();')
        data=text_test.encode()
    (out/name).write_bytes(data)
kernel=(here.parent/'coordinator/phase-polynomial-v1.rs').read_bytes().replace(b'\r\n',b'\n')
assert hashlib.sha256(kernel).hexdigest()=='330d91852ddc82740ac9bec4b8d8fb94d2ca5c5ca843fd4e56d1fed6123fab98'
(out/'toffoli_actual_lean_phase_kernel_v3.rs').write_bytes(kernel)
receipt={'status':'narrowed_actual_fin3_source_prepared_native_pending','source_sha256':{file.name:hashlib.sha256(file.read_bytes()).hexdigest() for file in out.iterdir()},
         'guard':'loan&&fin3&&ttm&&lean_m&&drop0; experimentmodefalse; noESH read/move inthisversion',
         'direct_proof_sha256':hashlib.sha256((here/'actual-lean-direct-v3.json').read_bytes()).hexdigest(),
         'kernel_sha256':hashlib.sha256(kernel).hexdigest(),'qualified_score':None}
(here/'actual-lean-v3r1-preparation.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
