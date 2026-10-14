"""Freeze physical integration and isolated native fixtures from exact proof."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[3];here=Path(__file__).parent
out=root/'research-output/overnight-20261014/toffoli/carry-cleanup-v1-source';out.mkdir(parents=True,exist_ok=True)
source=(root/'agents/product/src/point_add/y15_onefold.rs').read_bytes().replace(b'\r\n',b'\n')
assert hashlib.sha256(source).hexdigest()=='879b85060f6a5cfa412561d64860f1cab697f7a334f180f5be9102070d5a23b9'
text=source.decode();declaration='thread_local! { static TOFFOLI_CARRY_CLEANUP_MODE:std::cell::Cell<bool>=const{std::cell::Cell::new(false)}; static TOFFOLI_CARRY_CLEANUP_HITS:std::cell::Cell<usize>=const{std::cell::Cell::new(0)}; }\n'
text=text.replace('use super::*;\n','use super::*;\n'+declaration,1)
old='    ladder_d(c, acc, &add, 6, c6, &plan, &drops);\n    let (c4, c5) = if lean_m {'
assert text.count(old)==1
insert='''    ladder_d(c, acc, &add, 6, c6, &plan, &drops);
    if TOFFOLI_CARRY_CLEANUP_MODE.with(|x|x.get()) && loan && fin==0 && !ttm && !lean45 && drop==0 {
        assert_eq!(recs.len(),27,"exact constructor record interface");
        let q=|i:usize|match &recs[i] {Rec::And(q,_,_)|Rec::Maj(q,_,_,_)=>*q,_=>panic!("cleanup record is carry marker")};
        let bank:[QubitId;30]=[c1,c2,c4,q(0),q(1),q(2),q(3),q(4),q(5),c5,q(7),c6,q(9),q(10),q(11),q(12),q(13),q(14),q(15),q(16),q(17),q(18),q(19),q(20),q(21),q(22),q(23),q(24),q(25),q(26)];
        let unique:std::collections::HashSet<_>=bank.iter().copied().collect();assert_eq!(unique.len(),30);
        assert!(!unique.contains(&c3));
        for input in acc.iter().chain(e.iter()).chain(nm.iter()).chain([k1,k2].iter()) {assert!(!unique.contains(input));}
        lin_xor_into(c,&a4,acc[4]);c.cx(c4,acc[4]);lin_xor_into(c,&a5,acc[5]);c.cx(c5,acc[5]);
        c.cx(e[0],acc[0]);c.cx(e[1],acc[1]);c.cx(c1,acc[1]);c.cx(e[2],acc[2]);c.cx(c2,acc[2]);
        toffoli_carry_cleanup_v1::run(c,acc,e,nm,[k1,k2],&bank);
        TOFFOLI_CARRY_CLEANUP_HITS.with(|x|x.set(x.get()+1));LOAN_ACTIVE.with(|x|x.set(false));return plan;
    }
    let (c4, c5) = if lean_m {'''
text=text.replace(old,insert)
text+='\n#[path="toffoli_carry_cleanup_v1.rs"]\nmod toffoli_carry_cleanup_v1;\n#[cfg(test)]\n#[path="toffoli_native_fold.rs"]\nmod toffoli_native_fold;\n#[cfg(test)]\n#[path="toffoli_carry_cleanup_tests_v1.rs"]\nmod toffoli_carry_cleanup_tests_v1;\n'
(out/'y15_onefold.rs').write_bytes(text.encode())
for name in ['toffoli_carry_cleanup_v1.rs','toffoli_carry_cleanup_tests_v1.rs']:(out/name).write_bytes((here/name).read_bytes().replace(b'\r\n',b'\n'))
native=(here/'toffoli_native_fold.rs').read_bytes().replace(b'\r\n',b'\n').decode().replace('fn expected(','pub(super) fn expected(').replace('fn run_native(','pub(super) fn run_native(')
(out/'toffoli_native_fold.rs').write_bytes(native.encode())
receipt={'status':'native_joint_cleanup_source_prepared','baseline_source_lf_sha256':hashlib.sha256(source).hexdigest(),
         'guard':'loan && fin==0 && !ttm && !lean45 && drop==0; experiment mode defaultsfalse',
         'source_sha256':{file.name:hashlib.sha256(file.read_bytes()).hexdigest() for file in out.iterdir()},
         'proof_sha256':hashlib.sha256((here/'carry-cleanup-rebase-v1.json').read_bytes()).hexdigest(),
         'scope':'Changed consumer phase basis; no protected edits; native fixture pending, no fullrecord.'}
(here/'carry-cleanup-v1-preparation.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
