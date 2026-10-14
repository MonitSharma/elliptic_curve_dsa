"""Prepare fin3/drop1 lazy C4/TT cleanup with exact four-MR cost census."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
here = Path(__file__).parent
area = root / 'research-output/overnight-20261014/toffoli'
base = (area / 'actual-lean-v3r3-source/y15_onefold.rs').read_bytes()
assert hashlib.sha256(base).hexdigest() == '5682c6bd7844546e0ed88933b3720f89fa0e5cf92932fe8b96df7e078baee750'
text = base.decode().replace('toffoli_actual_lean_cleanup_v3', 'toffoli_actual_lean_cleanup_v5').replace('toffoli_actual_lean_tests_v3', 'toffoli_actual_lean_tests_v5').replace('toffoli_actual_lean_phase_kernel_v3', 'toffoli_actual_lean_phase_kernel_v5')
text = text.replace('static TOFFOLI_ACTUAL_LEAN_C6:', 'static TOFFOLI_ACTUAL_LEAN_BOUNDARY:std::cell::Cell<usize>=const{std::cell::Cell::new(0)}; static TOFFOLI_ACTUAL_LAZY_TARGETS:std::cell::Cell<Option<[QubitId;4]>>=const{std::cell::Cell::new(None)}; static TOFFOLI_ACTUAL_LEAN_C6:')
start = text.index('    if TOFFOLI_ACTUAL_LEAN_MODE.with(')
text = text[:start] + '''    TOFFOLI_ACTUAL_LEAN_BOUNDARY.with(|x|x.set(c.op_count()));
    let tq=|i:usize|match &recs[i] {Rec::And(q,_,_)|Rec::Maj(q,_,_,_)=>*q,_=>panic!("prefix index")};
    TOFFOLI_ACTUAL_LAZY_TARGETS.with(|x|x.set(Some([c6,tq(9),tq(7),tq(4)])));
''' + text[start:]
text = text.replace('        toffoli_actual_lean_cleanup_v5::run(c,acc,e,nm,[k1,k2],c3,c6,&a4,&a5,recs);', '        let recs=toffoli_actual_lean_cleanup_v5::erase_tables(c,c3,recs);\n        toffoli_actual_lean_cleanup_v5::run(c,acc,e,nm,[k1,k2],c3,c6,&a4,&a5,recs);')
out = area / 'actual-lazy-v5-source';out.mkdir(parents=True, exist_ok=True)
(out / 'y15_onefold.rs').write_bytes(text.encode())
(out / 'toffoli_actual_lean_cleanup_v5.rs').write_bytes((here / 'toffoli_actual_lean_cleanup_v5.rs').read_bytes().replace(b'\r\n', b'\n'))
tests = (area / 'actual-lean-v3r3-source/toffoli_actual_lean_tests_v3.rs').read_text()
tests = tests.replace('toffoli_actual_lean_phase_kernel_v3', 'toffoli_actual_lean_phase_kernel_v5').replace('_v3()', '_v5()')
tests = tests.replace('Vec<QubitId>,usize,u32,usize)', 'Vec<QubitId>,[usize;4],u32,usize)')
old = '''    let c6=TOFFOLI_ACTUAL_LEAN_C6.with(|x|x.get()).unwrap();let ops=c.take_ops();let mut mr=0usize;let mut c6_mr=None;
    for op in &ops {if matches!(op.kind,OperationType::Hmr|OperationType::R) {if op.q_target==c6 && c6_mr.is_none() {c6_mr=Some(mr);}mr+=1;}}
    (ops,acc,controls,abi,pads,c6_mr.unwrap(),peak,hits)'''
new = '''    let targets=TOFFOLI_ACTUAL_LAZY_TARGETS.with(|x|x.get()).unwrap();let boundary=TOFFOLI_ACTUAL_LEAN_BOUNDARY.with(|x|x.get());
    let ops=c.take_ops();let mut mr=0usize;let mut indices=[None;4];
    for (i,op) in ops.iter().enumerate() {if matches!(op.kind,OperationType::Hmr|OperationType::R) {
        if i>=boundary {for j in 0..4 {if op.q_target==targets[j] && indices[j].is_none() {indices[j]=Some(mr);}}}mr+=1;
    }}
    (ops,acc,controls,abi,pads,indices.map(Option::unwrap),peak,hits)'''
assert tests.count(old) == 1;tests = tests.replace(old, new)
tests = tests.replace('c6:usize,c6_word:u64', 'critical:[usize;4],pattern:u8')
tests = tests.replace('let word=if self.index==self.c6 {self.c6_word}else{self.seed};', 'let word=if let Some(j)=self.critical.iter().position(|&i|i==self.index) {if self.pattern>>j&1!=0 {u64::MAX}else{0}}else{self.seed};')
tests = tests.replace('for c6_word in [0,u64::MAX,0xAAAA_AAAA_AAAA_AAAA]', 'for pattern in 0..16u8').replace('c6:c6_mr,c6_word', 'critical:c6_mr,pattern')
tests = tests.replace('c6_mr={c6_mr}', 'critical_mr={c6_mr:?}').replace('assert_eq!(costs[0].0,costs[1].0+1);', 'assert_eq!(costs[0].0+1,costs[1].0);').replace('(costs[0].2/2) as u64', '(7*costs[0].2/8) as u64').replace('total*3)', 'total*16)')
tests = tests.replace('TOFFOLI_ACTUAL_LEAN_', 'TOFFOLI_ACTUAL_LAZY_LOG_')
# Restore source metadata names after giving only log markers their own prefix.
tests = tests.replace('TOFFOLI_ACTUAL_LAZY_LOG_MODE', 'TOFFOLI_ACTUAL_LEAN_MODE').replace('TOFFOLI_ACTUAL_LAZY_LOG_HITS', 'TOFFOLI_ACTUAL_LEAN_HITS').replace('TOFFOLI_ACTUAL_LAZY_LOG_DROPS', 'TOFFOLI_ACTUAL_LEAN_DROPS').replace('TOFFOLI_ACTUAL_LAZY_LOG_BOUNDARY', 'TOFFOLI_ACTUAL_LEAN_BOUNDARY')
tests += '''
#[test]
fn toffoli_actual_lean_lazy_build_faults_v5() {
    let (ops,acc,controls,_,_,_,_,_)=fixture(3,true);
    let boundary=TOFFOLI_ACTUAL_LEAN_BOUNDARY.with(|x|x.get());
    let ccx:Vec<_>=ops.iter().enumerate().skip(boundary).filter(|(_,op)|op.kind==OperationType::CCX).map(|(i,_)|i).collect();
    assert_eq!(ccx.len(),7,"two lowcarry+conditionalC4+factor+three lazyTT branches");
    for (name,remove) in [("C4_OR_build",ccx[2]),("TT_first_build",ccx[4])] {
        let mut faulty=ops.clone();faulty.remove(remove);let (nq,_,_,_)=analyze_ops(faulty.iter());let mut detected=false;
        for base in (0..1usize<<14).step_by(64) {let mut input=vec![0u64;nq as usize];
            for shot in 0..64 {let raw=(base+shot) as u64;
                for (i,&q) in acc.iter().take(6).enumerate() {input[q.0 as usize]|=(raw>>i&1)<<shot;}
                for (i,&q) in controls.iter().enumerate() {input[q.0 as usize]|=(raw>>(i+6)&1)<<shot;}
            }
            if let Err(why)=super::toffoli_actual_lean_phase_kernel_v5::audit(&faulty,&input,&[]) {
                if why.starts_with("nonzero phase polynomial") {detected=true;break;}
            }
        }
        assert!(detected,"missing {name} must produce detected nonzero phase");
    }
}
'''
(out / 'toffoli_actual_lean_tests_v5.rs').write_bytes(tests.encode())
kernel = (here.parent / 'coordinator/phase-polynomial-v1.rs').read_bytes().replace(b'\r\n', b'\n')
assert hashlib.sha256(kernel).hexdigest() == '330d91852ddc82740ac9bec4b8d8fb94d2ca5c5ca843fd4e56d1fed6123fab98'
(out / 'toffoli_actual_lean_phase_kernel_v5.rs').write_bytes(kernel)
record = {
    'status': 'fin3_drop1_lazy_cleanup_prepared_native_pending',
    'source_sha256': {file.name: hashlib.sha256(file.read_bytes()).hexdigest() for file in out.iterdir()},
    'guard_truth_sha256': hashlib.sha256((here / 'actual-lazy-guards-v5.json').read_bytes()).hexdigest(),
    'domain': 'All14 input bits, fourhigherwords, actualonedroppedchunk, dirty512classABI, ALLMR proof and16 equallyweighted semanticC6/T3/Y5/Y3 outcome patterns for exactcompletecomponentmean.',
    'source_caller': 'cap1234 room39 tick129; allocation/cost only',
    'prospective_mean_Toffoli_delta': '-7/8', 'emitted_CCX_delta': 1,
    'limits': 'Narrowfin3only; correspondingall18 fin4 producer lifetime andnativeproof separate. No full record.',
    'qualified_score': None,
}
(here / 'actual-lazy-v5-preparation.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
print(json.dumps(record))
