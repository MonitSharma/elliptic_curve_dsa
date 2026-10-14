"""Freeze native bank evidence and prepare a production-enabled width tradeoff."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
AREA=ROOT/"research-output/overnight-20261014/toffoli"
SOURCE=AREA/"source/src/point_add"
BASE="c5bb1ec876db859a3f9f8a9052c140a145df834e"

def digest(b):return hashlib.sha256(b).hexdigest()
def original(name):
    return subprocess.check_output(["git","-C",str(ROOT/"agents/product"),"show",f"{BASE}:src/point_add/{name}"])
def patch(files):
    out=[]
    for name,value in files.items():
        try:before=original(name)
        except subprocess.CalledProcessError:before=b""
        out+=list(difflib.unified_diff(before.decode().splitlines(keepends=True),value.decode().splitlines(keepends=True),
            fromfile=f"a/src/point_add/{name}" if before else "/dev/null",tofile=f"b/src/point_add/{name}"))
    return "".join(out).encode()

def main():
    y15=SOURCE.joinpath("y15_onefold.rs").read_text()
    # Reconstruct the exact earlier correctness-tested source before adding
    # allocation diagnostics; its hash must match the preserved native settings.
    added='''let bank_plan=if toffoli_bank_loan::enabled() && toffoli_bank_loan::head_plan() && !rev && !swap01 && drop_n==0 && !deep && !carry_loan_selected(rev,t) {
        let r=shed_for(shed_fixed-6,fmax);
        (r.4==0 && room_now+r.0+r.1>=31).then_some(r)
    } else {None};
    let (ttm, (shed, tops, c3m, gsh, fin)) = if let Some(r)=bank_plan {(false,r)} else if Y28_TT_FWD'''
    oldy=y15.replace(added,'let (ttm, (shed, tops, c3m, gsh, fin)) = if Y28_TT_FWD')
    oldy=oldy.replace('\n#[cfg(test)]\n#[path = "toffoli_bank_receipts.rs"]\nmod toffoli_bank_receipts;\n','')
    helper=SOURCE.joinpath("toffoli_bank_loan.rs").read_text()
    head='''#[cfg(test)] thread_local! { static HEAD_PLAN: std::cell::Cell<bool> = const { std::cell::Cell::new(false) }; }
#[cfg(test)] pub(super) fn head_plan() -> bool { HEAD_PLAN.with(|x|x.get()) }
#[cfg(not(test))] pub(super) fn head_plan() -> bool { false }
#[cfg(test)] pub(super) fn with_head_plan<R>(on:bool,f:impl FnOnce()->R)->R {
    let before=HEAD_PLAN.with(|x|x.replace(on));let result=f();HEAD_PLAN.with(|x|x.set(before));result
}'''
    oldhelper=helper.replace('\n'+head,'')
    frozen={"y15_onefold.rs":oldy.encode(),"toffoli_bank_loan.rs":oldhelper.encode(),
            "toffoli_bank_tests.rs":SOURCE.joinpath("toffoli_bank_tests.rs").read_bytes().replace(b'\r\n',b'\n'),
            "toffoli_native_fold.rs":SOURCE.joinpath("toffoli_native_fold.rs").read_bytes().replace(b'\r\n',b'\n')}
    settings=AREA.joinpath('toffoli-bank-loan-native-20261014.settings').read_text()
    for name,value in frozen.items():
        recorded=re.search(r'([0-9a-f]{64})  src/point_add/'+re.escape(name),settings).group(1)
        assert digest(value)==recorded,(name,digest(value),recorded)
    HERE.joinpath('bank-loan-native.patch').write_bytes(patch(frozen))
    candidate=AREA/"bank-product-source/src/point_add";candidate.mkdir(parents=True,exist_ok=True)
    for name in ['toffoli_native_fold','toffoli_bank_tests','toffoli_bank_receipts']:
        y15=re.sub(r'\n#\[cfg\(test\)\]\n#\[path = "'+name+r'\.rs"\]\nmod '+name+r';\n','',y15)
    helper=helper.replace('#[cfg(not(test))] pub(super) fn enabled() -> bool { false }','#[cfg(not(test))] pub(super) fn enabled() -> bool { true }')
    helper=helper.replace('#[cfg(not(test))] pub(super) fn head_plan() -> bool { false }','#[cfg(not(test))] pub(super) fn head_plan() -> bool { true }')
    helper=helper.replace('assert!(Y16_CORE && !carry_loan_on());','''assert!(Y16_CORE && !carry_loan_on());
    eprintln!("TOFFOLI_BANK_CALL payload={:?} width={} active={}",PAYLOAD_AT.with(|x|x.get()),acc.len(),c.active_qubits());''')
    candidate.joinpath('y15_onefold.rs').write_bytes(y15.encode())
    candidate.joinpath('toffoli_bank_loan.rs').write_bytes(helper.encode())
    candidate.joinpath('mod.rs').write_bytes(original('mod.rs')+b'\nmod rebind;\n')
    initial={name:p.read_bytes() for name in ['y15_onefold.rs','toffoli_bank_loan.rs','mod.rs'] for p in [candidate/name]}
    HERE.joinpath('bank-product-initial.patch').write_bytes(patch(initial))
    report={"base_revision":BASE,"candidate_status":"prepared_not_built",
            "native_correctness_patch_sha256":digest(HERE.joinpath('bank-loan-native.patch').read_bytes()),
            "native_correctness_source_sha256":{name:digest(v) for name,v in frozen.items()},
            "production_recipe":"31 construction ANDs, six exact early phase erasures, 25-bank ladder, six unconditional regenerations, restored original cleanup. Effective forward allocation reduced by six only when complete 31-wire construction fits, fin=0, no existing carry loan, no dropped ladder carries, no deep shed. Constructor helper used only fin=0/no tt/no drop/no old loan.",
            "candidate_source_sha256":{name:digest(v) for name,v in initial.items()},
            "additional_source_required":"143731ef rebind.rs/rebind_anchors.txt/y42_bound_pass.rs/linear_restore.rs only; preserve binary rewrite tables, nonce, protected harness and every other baseline source. Final source-only receipt required before launch.",
            "semantic_scope":"Initial bank rebase/phase/restore identities exhaustive over all 16384 constructor inputs. Native phase tests cover 38 upper words, not arbitrary upper words. Changed ladder plans retain the original source algorithm and may inherit its approximation. Rebinding requires unchanged local region/window signatures and normalized allocator boundary; a match is binding evidence, not a proof that inherited approximate edits are globally correct."}
    HERE.joinpath('bank-product-preparation.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report,indent=2))

if __name__=='__main__':main()
