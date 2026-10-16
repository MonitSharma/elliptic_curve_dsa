// Loader/curve/seed helpers copied verbatim from the protected evaluator (via failure-census-20261015).
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

// â”€â”€â”€ secp256k1 parameters â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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

// â”€â”€â”€ Fiat-Shamir seed â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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



fn hash_op(o:&Op)->u64{let mut h=0x243f6a8885a308d3u64;for v in[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h=h.rotate_left(11)^v.wrapping_mul(0x9e3779b97f4a7c15);}h}
fn main(){let a:Vec<_>=std::env::args().collect();let old=load_ops(&a[1]).unwrap();let new=load_ops(&a[2]).unwrap();let hints:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(&a[3]).unwrap()).unwrap();let hints=hints["hints"].as_array().unwrap();const K:usize=16;const B:u64=0x100000001b3;let pow=(0..K-1).fold(1u64,|p,_|p.wrapping_mul(B));let wh=|ops:&[Op],at:usize|ops[at..at+K].iter().fold(0u64,|h,o|h.wrapping_mul(B).wrapping_add(hash_op(o)));
let mut index=std::collections::HashMap::<u64,Vec<(usize,usize,usize)>>::new();for(i,x)in hints.iter().enumerate(){let lo=x["old_start"].as_u64().unwrap()as usize;let hi=x["old_end_exclusive"].as_u64().unwrap()as usize;for(boundary,at)in[(0,lo),(1,hi-K)]{assert!(at+K<=old.len());index.entry(wh(&old,at)).or_default().push((i,boundary,at));}}
let mut hits=vec![[Vec::<usize>::new(),Vec::new()];hints.len()];let mut rolling=wh(&new,0);for at in 0..=new.len()-K{if let Some(markers)=index.get(&rolling){for(i,boundary,oldat)in markers{if old[*oldat..*oldat+K]==new[at..at+K]&&hits[*i][*boundary].len()<512{hits[*i][*boundary].push(at);}}}if at+K<new.len(){rolling=rolling.wrapping_sub(hash_op(&new[at]).wrapping_mul(pow)).wrapping_mul(B).wrapping_add(hash_op(&new[at+K]));}}
let mut reset=Vec::new();let mut shadow=Vec::new();let mut rows=Vec::new();for(i,hint)in hints.iter().enumerate(){let oldlo=hint["old_start"].as_u64().unwrap()as usize;let oldhi=hint["old_end_exclusive"].as_u64().unwrap()as usize;let len=oldhi-oldlo;let mut pairs=std::collections::BTreeSet::new();for lo in &hits[i][0]{for en in &hits[i][1]{let hi=en+K;if hi>*lo&&(hi-*lo).abs_diff(len)<=1024{pairs.insert((*lo,hi));}}}if pairs.len()!=1{for lo in &hits[i][0]{let hi=lo+len;if hi<=new.len()&&old[oldlo..oldhi]==new[*lo..hi]{pairs.insert((*lo,hi));}}for en in &hits[i][1]{let hi=en+K;if hi>=len&&old[oldlo..oldhi]==new[hi-len..hi]{pairs.insert((hi-len,hi));}}}
if pairs.len()>1{let exact:std::collections::BTreeSet<_>=pairs.iter().copied().filter(|(lo,hi)|old[oldlo..oldhi]==new[*lo..*hi]).collect();if exact.len()==1{pairs=exact;}}if pairs.len()>1{let guide:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(&a[4]).unwrap()).unwrap();let nearest=guide["rows"].as_array().unwrap().iter().filter(|r|!r["mapping"].is_null()).min_by_key(|r|r["hint"]["old_start"].as_u64().unwrap().abs_diff(oldlo as u64));if let Some(g)=nearest{let offset=g["mapping"]["start"].as_i64().unwrap()-g["hint"]["old_start"].as_i64().unwrap();let predicted=(oldlo as i64+offset).max(0)as usize;let mut ranked:Vec<_>=pairs.iter().copied().collect();ranked.sort_by_key(|(lo,hi)|(lo.abs_diff(predicted),(hi-lo).abs_diff(len)));if ranked.len()==1||ranked[0].0.abs_diff(predicted)<ranked[1].0.abs_diff(predicted){pairs=std::collections::BTreeSet::from([ranked[0]]);}}}
let mapping=if pairs.len()==1{let(lo,hi)=*pairs.first().unwrap();let identical=old[oldlo..oldhi]==new[lo..hi];if hint["kind"]=="reset"{reset.push((lo,hi-1));}else{shadow.push((lo,hi));}serde_json::json!({"start":lo,"end_exclusive":hi,"actual_full_region_byte_identical":identical})}else{serde_json::Value::Null};rows.push(serde_json::json!({"hint":hint,"prefix_matches":hits[i][0].len(),"suffix_matches":hits[i][1].len(),"candidate_pairs":pairs.len(),"mapping":mapping}));}
let report=serde_json::json!({"status":"ACTUAL_OPERATION_ANCHOR_AND_OFFSET_CANDIDATES_REQUIRE_FRESH_LOCAL_PROOFS","original_operation_count":old.len(),"full_operation_count":new.len(),"candidate_reset_regions":reset,"candidate_shadow_regions":shadow,"hints":hints.len(),"mapped_reset":reset.len(),"mapped_shadow":shadow.len(),"unmapped":hints.len()-reset.len()-shadow.len(),"rows":rows,"old_masks_loaded":false});println!("{report}");}
