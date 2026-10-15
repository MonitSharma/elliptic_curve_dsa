// Loader/curve/seed helpers copied verbatim from the protected evaluator (via wide-phase fixed-replay).
use alloy_primitives::U256;
use quantum_ecc::circuit::{
    analyze_ops, BitId, Op, OperationType, QubitId, QubitOrBit, RegisterId,
};
use quantum_ecc::sim::Simulator;
use quantum_ecc::weierstrass_elliptic_curve::WeierstrassEllipticCurve;
use sha3::{
    digest::{ExtendableOutput, Update, XofReader},
    Shake256,
};
use std::fs::File;
use std::io::{BufReader, Read, Write};
use std::sync::{Arc, Mutex, atomic::{AtomicUsize, Ordering}};



const MAGIC: &[u8; 8] = b"QECCOPSZ";
// Cap the zstd window the decoder will accept (2^27 = 128 MiB). A forged
// ops.bin cannot force a huge decompression-window allocation.
const ZSTD_WINDOW_LOG_MAX: u32 = 27;
const FIELD_BYTES: usize = 8;
const OP_FIELDS: usize = 7;
const OP_BYTES: usize = OP_FIELDS * FIELD_BYTES;
// Resource caps. These are sanity limits to prevent a malicious ops.bin
// from OOM'ing the simulator (each qubit/bit costs 8 bytes in `Simulator::new`).
// Real circuits sit ~3k qubits and a few hundred million ops; caps are
// generous compared to that.
const MAX_OPS: u64 = 4_000_000_000;
const NUM_TESTS: usize = 9024;

fn op_kind_from_u32(v: u32) -> Option<OperationType> {
    Some(match v {
        0 => OperationType::Neg,
        1 => OperationType::Register,
        2 => OperationType::AppendToRegister,
        3 => OperationType::BitInvert,
        4 => OperationType::BitStore0,
        5 => OperationType::BitStore1,
        6 => OperationType::X,
        7 => OperationType::Z,
        8 => OperationType::CX,
        9 => OperationType::CZ,
        10 => OperationType::Swap,
        11 => OperationType::R,
        12 => OperationType::Hmr,
        13 => OperationType::CCX,
        14 => OperationType::CCZ,
        15 => OperationType::PushCondition,
        16 => OperationType::PopCondition,
        17 => OperationType::DebugPrint,
        _ => return None,
    })
}

fn read_u64(bytes: &[u8], off: usize) -> u64 {
    u64::from_le_bytes(bytes[off..off + 8].try_into().unwrap())
}

fn load_ops(path: &str) -> Result<Vec<Op>, String> {
    let mut file = File::open(path).map_err(|e| format!("open {path}: {e}"))?;

    // Plaintext header: MAGIC + u64 op count. Read and validate before
    // decompressing so the op count bounds every allocation below.
    let mut header = [0u8; MAGIC.len() + 8];
    file.read_exact(&mut header)
        .map_err(|e| format!("{path}: too short to read header: {e}"))?;
    if &header[..MAGIC.len()] != MAGIC {
        return Err(format!("{path}: bad magic"));
    }
    let n = u64::from_le_bytes(header[MAGIC.len()..].try_into().unwrap());
    if n > MAX_OPS {
        return Err(format!("{path}: op count {n} exceeds cap {MAX_OPS}"));
    }
    let n = n as usize;

    // Stream-decompress the record body. We read exactly n * OP_BYTES bytes
    // out of the decoder, so a forged frame cannot expand without bound; the
    // window cap limits the decoder's own buffer allocation.
    let mut dec = zstd::stream::read::Decoder::new(BufReader::new(file))
        .map_err(|e| format!("{path}: zstd init: {e}"))?;
    dec.window_log_max(ZSTD_WINDOW_LOG_MAX)
        .map_err(|e| format!("{path}: zstd window cap: {e}"))?;

    let mut ops = Vec::with_capacity(n);
    let mut rec = [0u8; OP_BYTES];
    for i in 0..n {
        dec.read_exact(&mut rec)
            .map_err(|e| format!("op {i}: short read from compressed body: {e}"))?;
        let kind_raw = u32::from_le_bytes(rec[0..4].try_into().unwrap());
        let kind = op_kind_from_u32(kind_raw)
            .ok_or_else(|| format!("op {i}: unknown kind {kind_raw}"))?;
        // rec[4..8] are reserved padding for 8-byte alignment.
        let q_control2 = QubitId(read_u64(&rec, 8));
        let q_control1 = QubitId(read_u64(&rec, 16));
        let q_target = QubitId(read_u64(&rec, 24));
        let c_target = BitId(read_u64(&rec, 32));
        let c_condition = BitId(read_u64(&rec, 40));
        let r_target = RegisterId(read_u64(&rec, 48));

        let op = Op {
            kind,
            q_control2,
            q_control1,
            q_target,
            c_target,
            c_condition,
            r_target,
        };
        // Op::validate() panics on aliasing or per-kind field-shape errors.
        // Catch the unwind to convert into a clean rejection.
        let validated = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| op.validate()));
        if let Err(e) = validated {
            let msg = e
                .downcast_ref::<String>()
                .cloned()
                .or_else(|| e.downcast_ref::<&'static str>().map(|s| s.to_string()))
                .unwrap_or_else(|| "validation panic".to_string());
            return Err(format!("op {i}: {msg}"));
        }
        ops.push(op);
    }

    // Reject trailing data: exactly n records must decompress, no more.
    let mut extra = [0u8; 1];
    match dec.read(&mut extra) {
        Ok(0) => {}
        Ok(_) => return Err(format!("{path}: trailing data after {n} ops")),
        Err(e) => return Err(format!("{path}: error checking for trailing data: {e}")),
    }
    Ok(ops)
}

// ─── secp256k1 parameters ──────────────────────────────────────────────────

fn secp256k1() -> WeierstrassEllipticCurve {
    WeierstrassEllipticCurve {
        modulus: U256::from_str_radix(
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
            16,
        )
        .unwrap(),
        a: U256::from(0),
        b: U256::from(7),
        gx: U256::from_str_radix(
            "79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798",
            16,
        )
        .unwrap(),
        gy: U256::from_str_radix(
            "483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8",
            16,
        )
        .unwrap(),
        order: U256::from_str_radix(
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
            16,
        )
        .unwrap(),
    }
}

// ─── Fiat-Shamir seed ──────────────────────────────────────────────────────
//
// SHAKE256 over the op stream. Determines test inputs, simulator RNG for
// R/Hmr phase randomization, etc.

fn fiat_shamir_seed(ops: &[Op]) -> sha3::Shake256Reader {
    let mut hasher = Shake256::default();
    hasher.update(b"quantum_ecc-fiat-shamir-v2");
    hasher.update(&(ops.len() as u64).to_le_bytes());
    for op in ops {
        hasher.update(&[op.kind as u8]);
        hasher.update(&op.q_control2.0.to_le_bytes());
        hasher.update(&op.q_control1.0.to_le_bytes());
        hasher.update(&op.q_target.0.to_le_bytes());
        hasher.update(&op.c_target.0.to_le_bytes());
        hasher.update(&op.c_condition.0.to_le_bytes());
        hasher.update(&op.r_target.0.to_le_bytes());
    }
    hasher.finalize_xof()
}


// ─── Failure-rate census (research diagnostic; never a scored evaluation) ───
//
// Inputs are drawn exactly as the evaluator draws them (two 32-byte scalars,
// same degenerate-pair skips), but from an independent labelled SHAKE256 per
// batch instead of the stream's Fiat-Shamir hash. The same XOF then seeds the
// simulator's measurement randomness, as in the evaluator. Every batch is full
// (64 accepted shots). The purpose is to estimate per-shot failure rates and
// hence the probability that an unmodified circuit passes a fresh packet. It
// must never be used to choose a stream, nonce or packet.
//
// Usage: failure_census OPS LABEL FIRST_BATCH NUM_BATCHES THREADS OUT.jsonl

const CENSUS_DOMAIN: &[u8] = b"ecdsa-research-failure-census-v1";

fn hex(v: U256) -> String { format!("{:#x}", v) }

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() == 3 && a[2] == "@official" {
        let ops = load_ops(&a[1]).unwrap();
        let (nq, nb, _, regs) = analyze_ops(ops.iter());
        let r = run_tests(&ops, &regs, nq, nb, fiat_shamir_seed(&ops), NUM_TESTS);
        println!("OFFICIAL_REPLAY ok={} shots={} classical={} phase_batches={} ancilla_batches={} tot_tof={} avg_tof={:.6} qubits={nq} reason={:?} score=NONE_DIAGNOSTIC_REPLAY",
            r.ok, r.n_shots, r.classical_failures, r.phase_garbage_batches, r.ancilla_garbage_batches, r.tot_tof, r.avg_tof, r.fail_reason);
        return;
    }
    assert_eq!(a.len(), 7, "OPS LABEL FIRST_BATCH NUM_BATCHES THREADS OUT.jsonl");
    let (label, first, count, threads) = (a[2].clone(), a[3].parse::<u64>().unwrap(),
        a[4].parse::<u64>().unwrap(), a[5].parse::<usize>().unwrap());
    let ops = Arc::new(load_ops(&a[1]).unwrap());
    let (nq, nb, _, regs) = analyze_ops(ops.iter());
    // Fiat-Shamir hash of the stream identifies it; reported, never used for inputs.
    let mut fs = [0u8; 32];
    XofReader::read(&mut fiat_shamir_seed(&ops), &mut fs);
    let fs_hex: String = fs.iter().map(|b| format!("{b:02x}")).collect();
    eprintln!("CENSUS_START ops={} qubits={nq} bits={nb} label={label} first={first} count={count} threads={threads} fs={fs_hex}", ops.len());
    let regs = Arc::new(regs);
    let next = Arc::new(AtomicUsize::new(0));
    let out = Arc::new(Mutex::new(Vec::<(u64, String)>::new()));
    let t0 = std::time::Instant::now();
    let mut handles = Vec::new();
    for _ in 0..threads {
        let (ops, regs, next, out, label) = (ops.clone(), regs.clone(), next.clone(), out.clone(), label.clone());
        handles.push(std::thread::spawn(move || {
            let curve = secp256k1();
            loop {
                let i = next.fetch_add(1, Ordering::SeqCst) as u64;
                if i >= count { break; }
                let batch = first + i;
                let mut h = Shake256::default();
                h.update(CENSUS_DOMAIN);
                h.update(&(label.len() as u64).to_le_bytes());
                h.update(label.as_bytes());
                h.update(&batch.to_le_bytes());
                let mut xof = h.finalize_xof();
                let (mut ks, mut pts) = (Vec::new(), Vec::new());
                let mut skipped = 0u32;
                while pts.len() < 64 {
                    let mut rb = [[0u8; 32]; 2];
                    XofReader::read(&mut xof, &mut rb[0]);
                    XofReader::read(&mut xof, &mut rb[1]);
                    let (k1, k2) = (U256::from_le_bytes(rb[0]), U256::from_le_bytes(rb[1]));
                    let t = curve.mul(curve.gx, curve.gy, k1);
                    let o = curve.mul(curve.gx, curve.gy, k2);
                    if t.0 == o.0 || (t.0.is_zero() && t.1.is_zero()) || (o.0.is_zero() && o.1.is_zero()) {
                        skipped += 1;
                        continue;
                    }
                    let e = curve.add(t.0, t.1, o.0, o.1);
                    ks.push((k1, k2));
                    pts.push((t, o, e));
                }
                let mut sim = Simulator::new(nq as usize, nb as usize, &mut xof);
                for (lane, (t, o, _)) in pts.iter().enumerate() {
                    sim.set_register(&regs[0], t.0, lane);
                    sim.set_register(&regs[1], t.1, lane);
                    sim.set_register(&regs[2], o.0, lane);
                    sim.set_register(&regs[3], o.1, lane);
                }
                sim.apply_iter(ops.iter());
                let mut value_mask = 0u64;
                for (lane, (_, _, e)) in pts.iter().enumerate() {
                    if sim.get_register(&regs[0], lane) != e.0 || sim.get_register(&regs[1], lane) != e.1 {
                        value_mask |= 1u64 << lane;
                    }
                }
                let phase_mask = sim.phase;
                for reg in regs.iter() { for q in reg { if let QubitOrBit::Qubit(q) = q { *sim.qubit_mut(*q) = 0; } } }
                let dirty_mask = sim.qubits.iter().fold(0u64, |m, w| m | w);
                let bad = value_mask | phase_mask | dirty_mask;
                let shots: Vec<String> = (0..64).filter(|l| bad >> l & 1 == 1).map(|l| {
                    format!("{{\"lane\":{l},\"value\":{},\"phase\":{},\"dirty\":{},\"k1\":\"{}\",\"k2\":\"{}\"}}",
                        value_mask >> l & 1, phase_mask >> l & 1, dirty_mask >> l & 1, hex(ks[l].0), hex(ks[l].1))
                }).collect();
                let line = format!("{{\"batch\":{batch},\"shots\":64,\"skipped\":{skipped},\"toffoli\":{},\"value_shots\":{},\"phase_shots\":{},\"dirty_shots\":{},\"failures\":[{}]}}",
                    sim.stats.toffoli_gates, value_mask.count_ones(), phase_mask.count_ones(), dirty_mask.count_ones(), shots.join(","));
                let mut g = out.lock().unwrap();
                g.push((batch, line));
                if g.len() % 16 == 0 {
                    eprintln!("CENSUS_PROGRESS done={} elapsed_s={:.1}", g.len(), t0.elapsed().as_secs_f64());
                }
            }
        }));
    }
    for h in handles { h.join().unwrap(); }
    let mut rows = Arc::try_unwrap(out).unwrap().into_inner().unwrap();
    rows.sort();
    let mut f = File::create(&a[6]).unwrap();
    for (_, l) in &rows { writeln!(f, "{l}").unwrap(); }
    eprintln!("CENSUS_DONE batches={} elapsed_s={:.1} score=NONE", rows.len(), t0.elapsed().as_secs_f64());
}

// ─── Evaluator run_tests, copied verbatim from protected src/bin/eval_circuit.rs (validation control) ───
struct SeedReport {
    ok: bool,
    avg_cliff: f64,
    avg_tof: f64,
    tot_tof: u64,
    tot_cliff: u64,
    n_shots: usize,
    classical_failures: usize,
    phase_garbage_batches: usize,
    ancilla_garbage_batches: usize,
    fail_reason: Option<String>,
}

fn run_tests(
    ops: &[Op],
    layout_regs: &[Vec<QubitOrBit>],
    total_qubits: u64,
    num_bits: u64,
    mut xof: sha3::Shake256Reader,
    target_shots: usize,
) -> SeedReport {
    let curve = secp256k1();

    let mut targets = Vec::with_capacity(target_shots);
    let mut offsets = Vec::with_capacity(target_shots);
    let mut expected = Vec::with_capacity(target_shots);
    for _ in 0..target_shots {
        let mut rb = [[0u8; 32]; 2];
        // Disambiguate from std::io::Read (in scope for the zstd loader).
        XofReader::read(&mut xof, &mut rb[0]);
        XofReader::read(&mut xof, &mut rb[1]);
        let k1 = U256::from_le_bytes(rb[0]);
        let k2 = U256::from_le_bytes(rb[1]);
        let t = curve.mul(curve.gx, curve.gy, k1);
        let o = curve.mul(curve.gx, curve.gy, k2);
        if t.0 == o.0 {
            continue;
        }
        if t.0.is_zero() && t.1.is_zero() {
            continue;
        }
        if o.0.is_zero() && o.1.is_zero() {
            continue;
        }
        let e = curve.add(t.0, t.1, o.0, o.1);
        targets.push(t);
        offsets.push(o);
        expected.push(e);
    }
    let n = targets.len();

    let mut sim = Simulator::new(total_qubits as usize, num_bits as usize, &mut xof);
    let mut ok = true;
    let mut fail_reason: Option<String> = None;
    let mut classical_failures = 0usize;
    let mut phase_garbage_batches = 0usize;
    let mut ancilla_garbage_batches = 0usize;

    const BATCH: usize = 64;
    let num_batches = (n + BATCH - 1) / BATCH;
    for batch in 0..num_batches {
        let bs = BATCH.min(n - batch * BATCH);
        let cond_mask: u64 = if bs == 64 { u64::MAX } else { (1u64 << bs) - 1 };

        sim.clear_for_shot();
        for shot in 0..bs {
            let i = batch * BATCH + shot;
            sim.set_register(&layout_regs[0], targets[i].0, shot);
            sim.set_register(&layout_regs[1], targets[i].1, shot);
            sim.set_register(&layout_regs[2], offsets[i].0, shot);
            sim.set_register(&layout_regs[3], offsets[i].1, shot);
        }

        sim.apply_iter(ops.iter());

        for shot in 0..bs {
            let i = batch * BATCH + shot;
            let gx = sim.get_register(&layout_regs[0], shot);
            let gy = sim.get_register(&layout_regs[1], shot);
            if gx != expected[i].0 || gy != expected[i].1 {
                classical_failures += 1;
                if fail_reason.is_none() {
                    fail_reason = Some(format!(
                        "CLASSICAL MISMATCH shot {i}: got ({:#x},{:#x}) exp ({:#x},{:#x})",
                        gx, gy, expected[i].0, expected[i].1
                    ));
                }
                ok = false;
            }
        }

        let phase = sim.phase & cond_mask;
        if phase != 0 {
            phase_garbage_batches += 1;
            let msg = format!(
                "PHASE GARBAGE: global_phase = {:#018x} across {} live shots (must be 0)",
                phase, bs
            );
            if fail_reason.is_none() {
                fail_reason = Some(msg);
            }
            ok = false;
        }

        for register in layout_regs {
            for qb in register {
                if let QubitOrBit::Qubit(q) = *qb {
                    *sim.qubit_mut(q) = 0;
                }
            }
        }
        let mut garbage_q: Option<u64> = None;
        for q in 0..total_qubits {
            let v = sim.qubit(QubitId(q)) & cond_mask;
            if v != 0 {
                garbage_q = Some(q);
                break;
            }
        }
        if let Some(q) = garbage_q {
            ancilla_garbage_batches += 1;
            let v = sim.qubit(QubitId(q)) & cond_mask;
            let msg = format!(
                "ANCILLA GARBAGE: qubit {} = {:#018x} (live shots) at end of forward; \
                 every non-register qubit must be |0⟩ on every live shot",
                q, v
            );
            if fail_reason.is_none() {
                fail_reason = Some(msg);
            }
            ok = false;
        }
    }

    let _ = num_bits;
    let denom = n.max(1) as f64;
    SeedReport {
        ok,
        avg_cliff: sim.stats.clifford_gates as f64 / denom,
        avg_tof: sim.stats.toffoli_gates as f64 / denom,
        tot_tof: sim.stats.toffoli_gates,
        tot_cliff: sim.stats.clifford_gates,
        n_shots: n,
        classical_failures,
        phase_garbage_batches,
        ancilla_garbage_batches,
        fail_reason,
    }
}
