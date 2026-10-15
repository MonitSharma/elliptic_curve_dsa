const LIBRARY_SOURCE:&str="/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline";
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


// Fixed-prefix proof of the local edit, using the archived unchanged BDD kernel.
use quantum_ecc::circuit;
#[path="../proof_kernel.rs"] mod proof_kernel;
fn main(){
    let root="/home/hclau/ecdsa_research/arithmetic-repair-20261015";
    let old=load_ops(&format!("{root}/diagnostic-b3/ops.bin")).unwrap();
    let new=load_ops(&format!("{root}/diagnostic-fold104-b3/ops.bin")).unwrap();
    let prefix=old.iter().zip(&new).take_while(|(a,b)|a==b).count();
    let suffix=old[prefix..].iter().rev().zip(new[prefix..].iter().rev()).take_while(|(a,b)|a==b).count();
    let mut depth=0usize;let mut start=0;
    for(i,o)in old[..prefix].iter().enumerate(){
        if depth==0{start=i;}match o.kind{OperationType::PushCondition=>depth+=1,OperationType::PopCondition=>depth-=1,_=>{}}
    }
    if depth==0{start=prefix;}
    let mut oe=old.len()-suffix;let mut ne=new.len()-suffix;
    let mut od=0i32;for o in &old[start..oe]{match o.kind{OperationType::PushCondition=>od+=1,OperationType::PopCondition=>od-=1,_=>{}}}
    while od>0{assert_eq!(old[oe],new[ne]);match old[oe].kind{OperationType::PushCondition=>od+=1,OperationType::PopCondition=>od-=1,_=>{}}oe+=1;ne+=1;}
    assert_eq!(od,0);
    let(nq,nb,_,regs)=analyze_ops(old.iter());
    let text=std::fs::read_to_string(format!("{root}/packets/independent.tsv")).unwrap();
    let rows:Vec<[U256;6]>=text.lines().map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();
    let indices:Vec<_>=(0..15).chain([94]).collect();
    let mut h=Shake256::default();h.update(b"b3-fold104-literal-proof-prefix-v1");let mut rng=h.finalize_xof();
    let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);
    for lane in 0..64{let row=rows[indices[lane%16]];for k in 0..4{sim.set_register(&regs[k],row[k],lane);}}
    sim.apply_iter(old[..start].iter());
    println!("PROOF_SCOPE old={start}..{oe} new={start}..{ne} distinct_original_inputs=16 includes_independent94=true prefix_measurements_fixed=true");
    let audit=proof_kernel::audit(&new[start..ne],&sim.qubits,&sim.bits).expect("repaired local block all-future-measurement proof");
    let mut nrng=sim.xof.clone();
    let mut native=Simulator::new(nq as usize,nb as usize,&mut nrng);
    native.qubits=sim.qubits.clone();native.bits=sim.bits.clone();native.apply_iter(new[start..ne].iter());
    assert_eq!(audit.qubits,native.qubits,"BDD/native local quantum states");assert_eq!(native.phase,0,"local phase increment");
    let target=audit.qubits.iter().position(|w|*w!=0).unwrap();
    let mut fault=new[start..ne].to_vec();let mut z=Op::empty();z.kind=OperationType::Z;z.q_target=QubitId(target as u64);fault.push(z);
    assert!(proof_kernel::audit(&fault,&sim.qubits,&sim.bits).is_err(),"planted phase fault must be detected");
    println!("LOCAL_ALLMR_PASS measurements={} all_quantum_slots={} zero_incremental_phase=true native_matches=true planted_phase_fault_detected=true maximum_phase_size={} maximum_quantum_size={}",audit.measurements,audit.qubits.len(),audit.maximum_phase_size_bound,audit.maximum_quantum_size_bound);
    native.apply_iter(new[ne..].iter());
    for lane in 0..64{let row=rows[indices[lane%16]];assert_eq!(native.get_register(&regs[0],lane),row[4]);assert_eq!(native.get_register(&regs[1],lane),row[5]);}
    println!("NATIVE_SUFFIX_VALUE_PASS distinct_inputs=16 complete_point_addition_values=true score=NONE");
}
