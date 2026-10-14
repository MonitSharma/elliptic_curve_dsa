"""Prepare producer-aware fin4 top1/direct/nondeep/drop2 candidate.

Run the source-bound v3r3 preparer first to create the prerequisite source.
"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
here = Path(__file__).parent
area = root / 'research-output/overnight-20261014/toffoli'
base = (area / 'actual-lean-v3r3-source/y15_onefold.rs').read_bytes()
assert hashlib.sha256(base).hexdigest() == '5682c6bd7844546e0ed88933b3720f89fa0e5cf92932fe8b96df7e078baee750'
text = base.decode().replace('toffoli_actual_lean_cleanup_v3', 'toffoli_actual_lean_cleanup_v4').replace('toffoli_actual_lean_tests_v3', 'toffoli_actual_lean_tests_v4').replace('toffoli_actual_lean_phase_kernel_v3', 'toffoli_actual_lean_phase_kernel_v4')
text = text.replace('static TOFFOLI_ACTUAL_LEAN_C6:', 'static TOFFOLI_ACTUAL_LEAN_BOUNDARY:std::cell::Cell<usize>=const{std::cell::Cell::new(0)}; static TOFFOLI_ACTUAL_LEAN_C6:')
start = text.index('    if TOFFOLI_ACTUAL_LEAN_MODE.with(')
end = text.index('    let (c4, c5) = if lean_m {', start)
text = text[:start] + '''    TOFFOLI_ACTUAL_LEAN_BOUNDARY.with(|x|x.set(c.op_count()));
    if TOFFOLI_ACTUAL_LEAN_MODE.with(|x|x.get()) && loan && fin==4 && ttm && lean_m && drop==2
        && esh.as_deref().is_some_and(|st|st.direct && st.top1 && st.deep_c.is_empty()) {
        let before=c.active_qubits();
        let recs=toffoli_actual_lean_cleanup_v4::erase_tables(c,c3,recs);
        assert_eq!(c.active_qubits()+14,before,"all14 table helpers returned beforeESH");
        let st=esh.as_deref_mut().unwrap();
        for q in [st.x256,st.x257,st.t255,st.b1,st.b2,st.b3,st.cq3] {
            assert!(!acc.contains(&q),"narrow ESHproducer outsidefold payload");
        }
        esh_in(c,st);assert_eq!(c.active_qubits()+11,before,"exactlythree ESHtargets restored");
        let fresh_e=[st.x256,st.x257,st.x258];
        toffoli_actual_lean_cleanup_v4::run(c,acc,fresh_e,nm,[k1,k2],c3,c6,&a4,&a5,recs);
        TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.set(x.get()+1));LOAN_ACTIVE.with(|x|x.set(false));return plan;
    }
''' + text[end:]
out = area / 'actual-lean-v4-source'
out.mkdir(parents=True, exist_ok=True)
(out / 'y15_onefold.rs').write_bytes(text.encode())
for name in ['toffoli_actual_lean_cleanup_v4.rs', 'toffoli_actual_lean_tests_v4.rs']:
    (out / name).write_bytes((here / name).read_bytes().replace(b'\r\n', b'\n'))
kernel = (here.parent / 'coordinator/phase-polynomial-v1.rs').read_bytes().replace(b'\r\n', b'\n')
assert hashlib.sha256(kernel).hexdigest() == '330d91852ddc82740ac9bec4b8d8fb94d2ca5c5ca843fd4e56d1fed6123fab98'
(out / 'toffoli_actual_lean_phase_kernel_v4.rs').write_bytes(kernel)
record = {
    'status': 'producer_aware_actual_fin4_prepared_native_pending',
    'prerequisite_y15_sha256': hashlib.sha256(base).hexdigest(),
    'source_sha256': {file.name: hashlib.sha256(file.read_bytes()).hexdigest() for file in out.iterdir()},
    'guard': 'mode &&loan&&fin4&&ttm&&lean_m&&drop2&&ESHtop1/direct/deepempty; mode defaults false',
    'domain': 'all18 inputs:6 payloadlow +7 independent admittedtop1 ESHproducer +3Nm +2shift; fourhigherwords; actual2droppedchunks asserted',
    'producer_contract_sha256': hashlib.sha256((here / 'actual-esh-contract-v4.json').read_bytes()).hexdigest(),
    'direct_phase_proof_sha256': hashlib.sha256((here / 'actual-lean-direct-v3.json').read_bytes()).hexdigest(),
    'scope': 'EarlyESHrestore onlyafter14 table helpers returned; new Ewire mapping passed explicitly, allheld producerinputs outsidefoldwindow asserted. No genericfin4/deep extension.',
    'qualified_score': None,
}
(here / 'actual-lean-v4-preparation.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
print(json.dumps(record))
