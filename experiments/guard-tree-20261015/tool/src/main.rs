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


fn zstd_level() -> i32 {
    std::env::var("ZSTD_LEVEL")
        .ok()
        .and_then(|s| s.trim().parse().ok())
        .unwrap_or(DEFAULT_ZSTD_LEVEL)
}

fn write_ops(ops: &[Op], path: &Path) -> std::io::Result<()> {
    let tmp = path.with_extension("bin.tmp");
    let mut w = BufWriter::new(File::create(&tmp)?);
    // Header stays uncompressed so the trusted loader can read MAGIC and the
    // op count (to bound memory) before touching the compressed body.
    w.write_all(MAGIC)?;
    w.write_all(&(ops.len() as u64).to_le_bytes())?;

    // Compress the record body. The encoder owns the BufWriter; finish()
    // flushes the zstd frame and hands it back.
    let mut enc = zstd::stream::write::Encoder::new(w, zstd_level())?;
    // Serialize each op into a fixed 56-byte record and stream it through the
    // encoder, so we never materialize a second full copy of the op stream.
    let mut rec = [0u8; OP_BYTES];
    for op in ops {
        rec[0..4].copy_from_slice(&(op.kind as u32).to_le_bytes());
        rec[4..8].copy_from_slice(&[0u8; 4]); // pad
        rec[8..16].copy_from_slice(&op.q_control2.0.to_le_bytes());
        rec[16..24].copy_from_slice(&op.q_control1.0.to_le_bytes());
        rec[24..32].copy_from_slice(&op.q_target.0.to_le_bytes());
        rec[32..40].copy_from_slice(&op.c_target.0.to_le_bytes());
        rec[40..48].copy_from_slice(&op.c_condition.0.to_le_bytes());
        rec[48..56].copy_from_slice(&op.r_target.0.to_le_bytes());
        enc.write_all(&rec)?;
    }
    let mut w = enc.finish()?;
    w.flush()?;
    drop(w);
    fs::rename(&tmp, path)?;
    Ok(())
}




use quantum_ecc::{circuit,sim};
use std::{path::Path,io::BufWriter,fs};
const DEFAULT_ZSTD_LEVEL:i32=3;
mod cond_pass;
struct CountRng<R>{inner:R,bytes:usize}
impl<R:XofReader>XofReader for CountRng<R>{fn read(&mut self,b:&mut[u8]){self.inner.read(b);self.bytes+=b.len();}}
fn paired_verify(args:&[String]){
 assert_eq!(args.len(),7);let aops=load_ops(&args[2]).unwrap();let bops=load_ops(&args[3]).unwrap();let text=fs::read_to_string(&args[4]).unwrap();let count=args[5].parse::<usize>().unwrap();let tag=args[6].as_bytes();
 let points:Vec<[U256;6]>=text.lines().filter(|l|!l.trim().is_empty()).map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();
 let(nq,nb,_,ar)=analyze_ops(aops.iter());let(qb,bb,_,br)=analyze_ops(bops.iter());assert_eq!(nq,qb);assert_eq!(ar,br);assert!(bb>=nb);let(mut ta,mut tb,mut shots)=(0u64,0u64,0usize);
 for seed in 0..count{for(batch,rows)in points.chunks(64).enumerate(){let mut h=Shake256::default();h.update(tag);h.update(&(seed as u64).to_le_bytes());h.update(&(batch as u64).to_le_bytes());let rng=h.finalize_xof();let mut ra=CountRng{inner:rng.clone(),bytes:0};let mut rb=CountRng{inner:rng,bytes:0};let mut a=Simulator::new(nq as usize,nb as usize,&mut ra);let mut b=Simulator::new(qb as usize,bb as usize,&mut rb);for v in &mut b.bits[nb as usize..]{*v=0xa5a5a5a5a5a5a5a5;}
 for(lane,row)in rows.iter().enumerate(){for k in 0..4{a.set_register(&ar[k],row[k],lane);b.set_register(&br[k],row[k],lane);}}
 a.apply_iter(aops.iter());b.apply_iter(bops.iter());assert_eq!(a.qubits,b.qubits,"all qubit mismatch seed={seed} batch={batch}");assert_eq!(a.bits,&b.bits[..nb as usize],"old bit mismatch seed={seed} batch={batch}");assert_eq!(a.phase,b.phase,"phase mismatch seed={seed} batch={batch}");assert!(b.bits[nb as usize..].iter().all(|v|*v==0),"fresh bits not clean");ta+=a.stats.toffoli_gates;tb+=b.stats.toffoli_gates;shots+=64;drop(a);drop(b);assert_eq!(ra.bytes,rb.bytes);println!("PAIRED_BATCH seed={seed} batch={batch} all_qubits=true all_old_bits=true phase=true fresh_bits_clean=true rng_bytes={}",ra.bytes);
 }}println!("PAIRED_EQUAL shots={shots} old_t={} new_t={} saved_t={} peak_q={nq} score=NONE",ta as f64/shots as f64,tb as f64/shots as f64,(ta as f64-tb as f64)/shots as f64);
}
fn main(){let a:Vec<_>=std::env::args().collect();if a.get(1).is_some_and(|v|v=="phase"){let ops=cond_pass::phase_expand(load_ops(&a[2]).unwrap());write_ops(&ops,Path::new(&a[3])).unwrap();return;}if a.get(1).is_some_and(|v|v=="values"){return cond_pass::guard_values(&load_ops(&a[2]).unwrap(),a[3].parse().unwrap());}if a.get(1).is_some_and(|v|v=="inspect"){let ops=load_ops(&a[2]).unwrap();use sha3::{Digest,Sha3_256};let mut h=Sha3_256::new();for o in &ops{Digest::update(&mut h,(o.kind as u32).to_le_bytes());Digest::update(&mut h,[0u8;4]);for v in[o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{Digest::update(&mut h,v.to_le_bytes());}}println!("SOURCE_BOUND_OPS len={} raw_sha3={:x}",ops.len(),h.finalize());let s=a[3].parse::<usize>().unwrap();let e=a[4].parse::<usize>().unwrap();for(i,o)in ops.iter().enumerate().take(e).skip(s){println!("{i} {:?} q2={} q1={} t={} bit={} cc={}",o.kind,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0);}return;}if a.get(1).is_some_and(|v|v=="verify"){return paired_verify(&a);}assert_eq!(a.len(),4);let mut ops=load_ops(&a[1]).unwrap();for _ in 0..a[2].parse::<usize>().unwrap(){ops=cond_pass::lazy_single(ops);}write_ops(&ops,Path::new(&a[3])).unwrap();}
