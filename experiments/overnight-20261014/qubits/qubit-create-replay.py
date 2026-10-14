"""Generate a separate diagnostic crate; never modify a contestant harness.

The loader, seed function and curve parameters are copied byte-for-byte from
the protected c95b9325 evaluator supplied as argv[1]. Its shared library is a
path dependency. Diagnostics deliberately write no score.json/results.tsv.
"""
from pathlib import Path
import hashlib
import sys

base = Path(sys.argv[1]).resolve()
dest = Path(sys.argv[2]).resolve()
source = (base / "src/bin/eval_circuit.rs").read_text()
dest.joinpath("src").mkdir(parents=True, exist_ok=True)
prefix = source[source.index("use alloy_primitives"):source.index("const OPS_PATH")]
prefix = prefix.replace("use std::fs::{File, OpenOptions};", "use std::fs::File;")
prefix = prefix.replace("use std::process::Command;", "").replace("use std::time::{SystemTime, UNIX_EPOCH};", "")
constants = source[source.index('const MAGIC:'):source.index("// ─── Bounded ops.bin loader")]
helpers = source[source.index("fn op_kind_from_u32"):source.index("// ─── Test runner")]
main = r'''
fn packet(ops: &[Op], path: &str) -> sha3::Shake256Reader {
    let mut xof = fiat_shamir_seed(ops);
    let curve = secp256k1();
    let mut out = File::create(path).unwrap();
    writeln!(out, "# index target_x target_y offset_x offset_y expected_x expected_y scalar1 scalar2").unwrap();
    let mut i = 0usize;
    for _ in 0..NUM_TESTS {
        let mut rb = [[0u8; 32]; 2];
        XofReader::read(&mut xof, &mut rb[0]);
        XofReader::read(&mut xof, &mut rb[1]);
        let k1 = U256::from_le_bytes(rb[0]);
        let k2 = U256::from_le_bytes(rb[1]);
        let t = curve.mul(curve.gx, curve.gy, k1);
        let o = curve.mul(curve.gx, curve.gy, k2);
        if t.0 == o.0 || (t.0.is_zero() && t.1.is_zero()) || (o.0.is_zero() && o.1.is_zero()) { continue; }
        let e = curve.add(t.0, t.1, o.0, o.1);
        writeln!(out, "{i}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}\t{:#x}", t.0,t.1,o.0,o.1,e.0,e.1,k1,k2).unwrap();
        i += 1;
    }
    eprintln!("PACKET_EXPORTED shots={i} file={path}");
    xof
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    assert!(a.len() >= 4, "usage: replay export|exact|paired ops.bin packet.tsv [batch=18]");
    let ops = load_ops(&a[2]).expect("load stream");
    let (nq, nb, _, regs) = analyze_ops(ops.iter());
    eprintln!("DIAGNOSTIC_ONLY ops={} qubits={nq} bits={nb}",ops.len());
    if a[1] == "export" { packet(&ops, &a[3]); return; }
    let batch: usize = a.get(4).map(|s| s.parse().unwrap()).unwrap_or(18);
    let mut xof = if a[1] == "exact" {
        let mut xof = packet(&ops, &a[3]);
        let nr = ops.iter().filter(|op| matches!(op.kind,OperationType::R|OperationType::Hmr)).count();
        let mut skip = (batch as u64)*(nr as u64)*8;
        eprintln!("EXACT_ORIGINAL_BATCH rng_records_per_batch={nr} skip_bytes={skip}");
        let mut buf = vec![0u8; 1<<20];
        while skip > 0 { let n=skip.min(buf.len() as u64) as usize; XofReader::read(&mut xof,&mut buf[..n]);skip-=n as u64; }
        xof
    } else {
        assert_eq!(a[1],"paired");
        let mut h=Shake256::default(); h.update(b"qubit-identical-input-replay-v1");
        h.update(&(batch as u64).to_le_bytes()); h.finalize_xof()
    };
    let lines=std::fs::read_to_string(&a[3]).unwrap();
    let records: Vec<_> = lines.lines().filter(|s| !s.starts_with('#')).collect();
    let chosen=&records[batch*64..records.len().min((batch+1)*64)];
    let mut sim=Simulator::new(nq as usize,nb as usize,&mut xof);
    let values: Vec<Vec<U256>> = chosen.iter().map(|s|s.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect()).collect();
    for (lane,v) in values.iter().enumerate() { for r in 0..4 { sim.set_register(&regs[r],v[r],lane); } }
    sim.apply_iter(ops.iter());
    let mut mismatches=0;
    for (lane,v) in values.iter().enumerate() {
        let x=sim.get_register(&regs[0],lane);let y=sim.get_register(&regs[1],lane);
        let ok=x==v[4]&&y==v[5]; if !ok {mismatches+=1;}
        println!("SHOT {} ok={ok} got_x={:#x} got_y={:#x} expected_x={:#x} expected_y={:#x}",batch*64+lane,x,y,v[4],v[5]);
    }
    let live=if chosen.len()==64{u64::MAX}else{(1u64<<chosen.len())-1};
    println!("PHASE batch={batch} mask={:#018x}",sim.phase&live);
    for reg in &regs {for q in reg {if let QubitOrBit::Qubit(q)=q {*sim.qubit_mut(*q)=0;}}}
    let mut dirty=0;
    for q in 0..nq {let v=sim.qubit(QubitId(q))&live;if v!=0{dirty+=1;println!("ANCILLA q={q} mask={v:#018x}");}}
    println!("DIAGNOSTIC_RESULT batch={batch} mismatches={mismatches} phase_nonzero={} dirty_ancillas={dirty} score=NONE",sim.phase&live!=0);
}
'''
dest.joinpath("src/main.rs").write_text(prefix + constants + helpers + main)
dest.joinpath("Cargo.toml").write_text(f'''[package]
name = "qubit_replay_diagnostic"
version = "0.1.0"
edition = "2021"
[dependencies]
quantum_ecc = {{ path = "{base.as_posix()}" }}
alloy-primitives = "1.5"
sha3 = "0.10"
zstd = "0.13"
[profile.release]
opt-level = 3
lto = "thin"
codegen-units = 1
''')
print("protected_evaluator_sha256=" + hashlib.sha256((base / "src/bin/eval_circuit.rs").read_bytes()).hexdigest())
print("diagnostic_sha256=" + hashlib.sha256(dest.joinpath("src/main.rs").read_bytes()).hexdigest())
