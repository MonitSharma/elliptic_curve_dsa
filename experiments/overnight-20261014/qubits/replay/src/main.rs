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
