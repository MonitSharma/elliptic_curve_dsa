"""Create an external research crate to inspect exact known-zero peak wires.

Copies the public conservative abstraction, appending a read-only query. The
candidate checkout, protected harness, manifests and toolchain are untouched.
"""
import argparse
import hashlib
import json
from pathlib import Path

QUERY = r'''
pub(crate) fn audit_zero(ops: &[Op], target: usize) {
    let mut state = Support::new(ops);
    let mut affine = AffineSupport::new(ops);
    let mut quadratic = QuadraticSupport::new(ops);
    for (i, op) in ops.iter().enumerate() {
        if i == target {
            let zeros: Vec<usize> = state.qubits.iter().enumerate()
                .filter_map(|(q, value)| value.is_zero().then_some(q)).collect();
            println!("EXACT_ZERO_AUDIT before_op={} zero_wires={:?}", i, zeros);
            println!("AFFINE_ZERO_AUDIT before_op={} zero_wires={:?}", i, affine.zero_qubits());
            println!("QUADRATIC_ZERO_AUDIT before_op={} zero_wires={:?}", i, quadratic.zero_qubits());
            println!("EXACT_ZERO_AUDIT gate={:?}", op);
            return;
        }
        state.step(op);
        affine.step(op);
        quadratic.step(op);
    }
    panic!("Peak index beyond stream");
}
'''

MAIN = r'''
pub mod circuit { pub use quantum_ecc::circuit::*; }
mod affine_simplify;
mod quadratic_simplify;
mod truth_simplify;
use circuit::{Op, OperationType as K, QubitId, BitId, RegisterId};
use std::io::Read;
fn main() {
    let args:Vec<String>=std::env::args().collect();
    assert_eq!(args.len(),3,"stream peak-op-index");
    let mut file=std::fs::File::open(&args[1]).unwrap();
    let mut header=[0u8;16]; file.read_exact(&mut header).unwrap();
    assert_eq!(&header[..8],b"QECCOPSZ");
    let n=u64::from_le_bytes(header[8..].try_into().unwrap()) as usize;
    assert!(n<=4_000_000_000);
    let mut decoder=zstd::stream::read::Decoder::new(std::io::BufReader::new(file)).unwrap();
    decoder.window_log_max(27).unwrap();
    let mut ops=Vec::with_capacity(n);
    let kinds=[K::Neg,K::Register,K::AppendToRegister,K::BitInvert,K::BitStore0,K::BitStore1,
               K::X,K::Z,K::CX,K::CZ,K::Swap,K::R,K::Hmr,K::CCX,K::CCZ,K::PushCondition,K::PopCondition,K::DebugPrint];
    let mut rec=[0u8;56];
    for _ in 0..n {
        decoder.read_exact(&mut rec).unwrap();
        let kind=u32::from_le_bytes(rec[..4].try_into().unwrap()) as usize;
        assert!(kind<18);
        let field=|start|u64::from_le_bytes(rec[start..start+8].try_into().unwrap());
        let op=Op{kind:kinds[kind],q_control2:QubitId(field(8)),q_control1:QubitId(field(16)),
            q_target:QubitId(field(24)),c_target:BitId(field(32)),c_condition:BitId(field(40)),r_target:RegisterId(field(48))};
        op.validate(); ops.push(op);
    }
    assert_eq!(decoder.read(&mut [0u8;1]).unwrap(),0);
    truth_simplify::audit_zero(&ops,args[2].parse().unwrap());
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    baseline = args.baseline.resolve()
    dest = args.destination.resolve()
    (dest / "src").mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name in ("affine_simplify.rs", "quadratic_simplify.rs", "truth_simplify.rs", "product_simplify.rs"):
        data = (baseline / "src/point_add" / name).read_bytes()
        hashes[name] = hashlib.sha256(data).hexdigest()
        text = data.decode().replace("\r\n", "\n")
        if name == "truth_simplify.rs":
            text += QUERY
        elif name in ("affine_simplify.rs", "quadratic_simplify.rs"):
            text += '\nimpl Support { pub(super) fn zero_qubits(&self) -> Vec<usize> {\n' \
                    'self.qubits.iter().enumerate().filter_map(|(q,v)| v.is_zero().then_some(q)).collect()\n} }\n'
        (dest / "src" / name).write_text(text, encoding="utf-8")
    (dest / "src/main.rs").write_text(MAIN, encoding="utf-8")
    manifest = '[package]\nname="wire_zero_audit"\nversion="0.1.0"\nedition="2021"\n\n' \
               '[dependencies]\nquantum_ecc={path=' + json.dumps(str(baseline)) + '}\nzstd="0.13"\n'
    (dest / "Cargo.toml").write_text(manifest, encoding="utf-8")
    (dest / "rust-toolchain").write_bytes((baseline / "rust-toolchain").read_bytes())
    (dest / "provenance.json").write_text(json.dumps({"baseline": str(baseline), "public_source_sha256": hashes,
             "scope": "Read-only exact known-zero abstraction; not complete liveness, candidate or scored result."}, indent=2)+"\n")
    print(dest)


if __name__ == "__main__":
    main()
