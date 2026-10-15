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


// Byte-locality certificate and event-aligned diagnostic pairing; no score.
struct Words { values: Vec<u64>, at: usize }
impl XofReader for Words { fn read(&mut self,out:&mut[u8]) { assert_eq!(out.len(),8);out.copy_from_slice(&self.values[self.at].to_le_bytes());self.at+=1; } }
fn is_mr(o:&Op)->bool{matches!(o.kind,OperationType::R|OperationType::Hmr)}
fn main(){
    let root="/home/hclau/ecdsa_research/arithmetic-repair-20261015";
    let old=load_ops(&format!("{root}/diagnostic-b3/ops.bin")).unwrap();
    let new=load_ops(&format!("{root}/diagnostic-fold104-b3/ops.bin")).unwrap();
    let prefix=old.iter().zip(&new).take_while(|(a,b)|a==b).count();
    let suffix=old[prefix..].iter().rev().zip(new[prefix..].iter().rev()).take_while(|(a,b)|a==b).count();
    let old_end=old.len()-suffix;let new_end=new.len()-suffix;
    let mpre=old[..prefix].iter().filter(|o|is_mr(o)).count();
    let mold=old[prefix..old_end].iter().filter(|o|is_mr(o)).count();
    let mnew=new[prefix..new_end].iter().filter(|o|is_mr(o)).count();
    let msuffix=old[old_end..].iter().filter(|o|is_mr(o)).count();
    println!("RAW_LOCALITY prefix={prefix} old_end={old_end} new_end={new_end} suffix={suffix} added_ops={} old_span_mr={mold} new_span_mr={mnew} all_outside_ops_identical=true",new.len() as i64-old.len() as i64);
    assert!(prefix>0&&suffix>0);assert_eq!(new.len(),old.len()+201);
    let(nq,nb,_,regs)=analyze_ops(old.iter());let(rq,rb,_,rregs)=analyze_ops(new.iter());assert_eq!((nq,nb,&regs),(rq,rb,&rregs));
    for family in ["independent","structured","candidate"]{
        let text=std::fs::read_to_string(format!("{root}/packets/{family}.tsv")).unwrap();
        let rows:Vec<[U256;6]>=text.lines().map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();
        let(mut old_bad,mut new_bad,mut introduced,mut corrected,mut phase_diff,mut dirty_old,mut dirty_new,mut old_phase,mut new_phase)=(0,0,0,0,0,0,0,0,0);
        for(batch,points)in rows.chunks(64).enumerate(){
            let mut h=Shake256::default();h.update(b"fold104-event-aligned-v1");h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();
            let mut draw=|n:usize|->Vec<u64>{(0..n).map(|_|{let mut b=[0u8;8];XofReader::read(&mut rng,&mut b);u64::from_le_bytes(b)}).collect()};
            let pre=draw(mpre);let lcore=draw(mold);let rcore=draw(mnew);let post=draw(msuffix);
            let mut lr=Words{values:pre.iter().chain(&lcore).chain(&post).copied().collect(),at:0};
            let mut rr=Words{values:pre.iter().chain(&rcore).chain(&post).copied().collect(),at:0};
            let mut l=Simulator::new(nq as usize,nb as usize,&mut lr);let mut r=Simulator::new(rq as usize,rb as usize,&mut rr);
            for(lane,v)in points.iter().enumerate(){for k in 0..4{l.set_register(&regs[k],v[k],lane);r.set_register(&regs[k],v[k],lane);}}
            l.apply_iter(old.iter());r.apply_iter(new.iter());let mask=if points.len()==64{u64::MAX}else{(1u64<<points.len())-1};
            phase_diff+=((l.phase^r.phase)&mask).count_ones();
            old_phase+=(l.phase&mask).count_ones();new_phase+=(r.phase&mask).count_ones();
            for(lane,v)in points.iter().enumerate(){
                if (l.phase^r.phase)>>lane&1!=0 {println!("PHASE_CHANGE family={family} shot={} old_phase={} new_phase={}",batch*64+lane,l.phase>>lane&1,r.phase>>lane&1);}
                let lb=l.get_register(&regs[0],lane)!=v[4]||l.get_register(&regs[1],lane)!=v[5];
                let rb=r.get_register(&regs[0],lane)!=v[4]||r.get_register(&regs[1],lane)!=v[5];
                old_bad+=usize::from(lb);new_bad+=usize::from(rb);introduced+=usize::from(!lb&&rb);corrected+=usize::from(lb&&!rb);
                if lb!=rb {println!("CHANGED_CORRECTNESS family={family} shot={} old_bad={lb} new_bad={rb}",batch*64+lane);}
            }
            for reg in &regs{for q in reg{if let QubitOrBit::Qubit(q)=q{*l.qubit_mut(*q)=0;*r.qubit_mut(*q)=0;}}}
            dirty_old+=usize::from(l.qubits.iter().any(|v|v&mask!=0));dirty_new+=usize::from(r.qubits.iter().any(|v|v&mask!=0));
        }
        println!("PAIRED_REPAIR family={family} shots={} old_bad={old_bad} new_bad={new_bad} corrected={corrected} introduced={introduced} phase_diff_shots={phase_diff} old_phase_shots={old_phase} new_phase_shots={new_phase} old_dirty_batches={dirty_old} new_dirty_batches={dirty_new} score=NONE",rows.len());
        assert_eq!(introduced,0,"new value regression on fixed packet");assert_eq!(dirty_new,0);
        if family=="independent"{assert_eq!(old_bad,1);assert_eq!(new_bad,0);assert_eq!(corrected,1);}
    }
}
