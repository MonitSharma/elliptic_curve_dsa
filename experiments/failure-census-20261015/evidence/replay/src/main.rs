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


// ─── Failure replay (research diagnostic; never a scored evaluation) ───
//
// Replays census failure inputs (k1 k2 hex per line) under R independent
// measurement-randomness seeds. Reports, per input, how many seeds give a
// wrong value / nonzero phase / dirty ancilla, plus the first wrong output.
// Value failures that persist across all seeds are deterministic arithmetic
// errors; seed-dependent ones involve measurement-conditioned logic.
//
// Usage: failure_replay OPS INPUTS.tsv SEEDS THREADS OUT.jsonl

const REPLAY_DOMAIN: &[u8] = b"ecdsa-research-failure-replay-v1";

fn main() {
    let a: Vec<String> = std::env::args().collect();
    assert_eq!(a.len(), 6, "OPS INPUTS.tsv SEEDS THREADS OUT.jsonl");
    let ops = Arc::new(load_ops(&a[1]).unwrap());
    let (nq, nb, _, regs) = analyze_ops(ops.iter());
    let regs = Arc::new(regs);
    let seeds: u64 = a[3].parse().unwrap();
    let threads: usize = a[4].parse().unwrap();
    let curve = secp256k1();
    let inputs: Vec<(U256, U256)> = std::fs::read_to_string(&a[2]).unwrap().lines()
        .filter(|l| !l.trim().is_empty())
        .map(|l| { let v: Vec<U256> = l.split_whitespace().map(|x| U256::from_str_radix(x.trim_start_matches("0x"), 16).unwrap()).collect(); (v[0], v[1]) })
        .collect();
    let pts: Arc<Vec<_>> = Arc::new(inputs.iter().map(|&(k1, k2)| {
        let t = curve.mul(curve.gx, curve.gy, k1);
        let o = curve.mul(curve.gx, curve.gy, k2);
        (t, o, curve.add(t.0, t.1, o.0, o.1))
    }).collect());
    let chunks: Vec<(usize, usize)> = (0..pts.len()).step_by(64).map(|s| (s, (s + 64).min(pts.len()))).collect();
    let jobs: Arc<Vec<(usize, usize, u64)>> = Arc::new(chunks.iter().flat_map(|&(s, e)| (0..seeds).map(move |r| (s, e, r))).collect());
    let n = pts.len();
    // per input: value count, phase count, dirty count, first wrong (x,y)
    let acc = Arc::new(Mutex::new((vec![0u32; n], vec![0u32; n], vec![0u32; n], vec![None::<(U256, U256)>; n])));
    let next = Arc::new(AtomicUsize::new(0));
    let mut hs = Vec::new();
    for _ in 0..threads {
        let (ops, regs, pts, jobs, acc, next) = (ops.clone(), regs.clone(), pts.clone(), jobs.clone(), acc.clone(), next.clone());
        hs.push(std::thread::spawn(move || loop {
            let j = next.fetch_add(1, Ordering::SeqCst);
            if j >= jobs.len() { break; }
            let (s, e, r) = jobs[j];
            let mut h = Shake256::default();
            h.update(REPLAY_DOMAIN);
            h.update(&(s as u64).to_le_bytes());
            h.update(&r.to_le_bytes());
            let mut xof = h.finalize_xof();
            let mut sim = Simulator::new(nq as usize, nb as usize, &mut xof);
            for (lane, i) in (s..e).enumerate() {
                let (t, o, _) = pts[i];
                sim.set_register(&regs[0], t.0, lane);
                sim.set_register(&regs[1], t.1, lane);
                sim.set_register(&regs[2], o.0, lane);
                sim.set_register(&regs[3], o.1, lane);
            }
            sim.apply_iter(ops.iter());
            let mut got = Vec::new();
            for (lane, _) in (s..e).enumerate() {
                got.push((sim.get_register(&regs[0], lane), sim.get_register(&regs[1], lane)));
            }
            let phase = sim.phase;
            for reg in regs.iter() { for q in reg { if let QubitOrBit::Qubit(q) = q { *sim.qubit_mut(*q) = 0; } } }
            let dirty = sim.qubits.iter().fold(0u64, |m, w| m | w);
            let mut g = acc.lock().unwrap();
            for (lane, i) in (s..e).enumerate() {
                let exp = pts[i].2;
                if got[lane] != exp { g.0[i] += 1; if g.3[i].is_none() { g.3[i] = Some(got[lane]); } }
                if phase >> lane & 1 == 1 { g.1[i] += 1; }
                if dirty >> lane & 1 == 1 { g.2[i] += 1; }
            }
        }));
    }
    for h in hs { h.join().unwrap(); }
    let g = Arc::try_unwrap(acc).unwrap().into_inner().unwrap();
    let mut f = File::create(&a[5]).unwrap();
    for i in 0..n {
        let (k1, k2) = inputs[i];
        let ((px, py), (ax, ay), (ex, ey)) = pts[i];
        let wrong = g.3[i].map(|(x, y)| format!(",\"got_x\":\"{:#x}\",\"got_y\":\"{:#x}\"", x, y)).unwrap_or_default();
        writeln!(f, "{{\"k1\":\"{:#x}\",\"k2\":\"{:#x}\",\"px\":\"{:#x}\",\"py\":\"{:#x}\",\"ax\":\"{:#x}\",\"ay\":\"{:#x}\",\"exp_x\":\"{:#x}\",\"exp_y\":\"{:#x}\",\"seeds\":{seeds},\"value\":{},\"phase\":{},\"dirty\":{}{wrong}}}",
            k1, k2, px, py, ax, ay, ex, ey, g.0[i], g.1[i], g.2[i]).unwrap();
    }
    eprintln!("REPLAY_DONE inputs={n} seeds={seeds} score=NONE");
}
