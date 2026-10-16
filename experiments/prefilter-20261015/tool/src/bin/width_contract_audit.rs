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



fn qrefs(o:&Op)->Vec<u64>{[o.q_control1.0,o.q_control2.0,o.q_target.0].into_iter().filter(|q|*q!=u64::MAX).collect()}
fn row(o:&Op)->serde_json::Value{serde_json::json!([o.kind as u8,o.q_control1.0,o.q_control2.0,o.q_target.0,o.c_target.0,o.c_condition.0])}
fn writes(o:&Op,q:u64)->bool{use OperationType::*; match o.kind{X|CX|CCX|R|Hmr=>o.q_target.0==q,Swap=>o.q_control1.0==q||o.q_target.0==q,_=>false}}
fn cx(o:&Op,a:u64,t:u64)->bool{o.kind==OperationType::CX&&o.q_control1.0==a&&o.q_target.0==t&&o.c_condition.0==u64::MAX}
fn ccx(o:&Op,a:u64,b:u64,t:u64)->bool{o.kind==OperationType::CCX&&o.q_target.0==t&&((o.q_control1.0==a&&o.q_control2.0==b)||(o.q_control1.0==b&&o.q_control2.0==a))&&o.c_condition.0==u64::MAX}
fn phase(o:&Op,a:u64,b:u64,m:u64)->bool{o.kind==OperationType::CZ&&((o.q_control1.0==a&&o.q_target.0==b)||(o.q_control1.0==b&&o.q_target.0==a))&&o.c_condition.0==m}
fn main(){use OperationType::*;let args:Vec<_>=std::env::args().collect();let ops=load_ops(&args[1]).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());assert_eq!(nq,1234);let z=nq-1;let mut isabi=vec![false;nb as usize];for reg in &regs{for q in reg{if let QubitOrBit::Bit(b)=q{isabi[b.0 as usize]=true;}}}
let mut dep=vec![0u32;ops.len()];let mut d=0u32;let mut spans=Vec::new();let mut begin=None;let mut used=0;let mut uses=vec![Vec::<(usize,bool)>::new();nb as usize];
for(i,o)in ops.iter().enumerate(){dep[i]=d;if o.c_condition.0!=u64::MAX{uses[o.c_condition.0 as usize].push((i,false));}if o.c_target.0!=u64::MAX{let kill=matches!(o.kind,Hmr|BitStore0|BitStore1)&&d==0&&o.c_condition.0==u64::MAX;uses[o.c_target.0 as usize].push((i,kill));}if qrefs(o).contains(&z){used+=1;if begin.is_none(){begin=Some(i);}if matches!(o.kind,R|Hmr)&&d==0&&o.c_condition.0==u64::MAX{spans.push((begin.take().unwrap(),i));}}if o.kind==PushCondition{d+=1;}if o.kind==PopCondition{d-=1;}}
assert_eq!(d,0);if let Some(s)=begin{spans.push((s,ops.len()-1));}
let death=|m:u64,end:usize|->(bool,serde_json::Value){if isabi[m as usize]{return(false,serde_json::json!({"reason":"ABI_BIT"}));}let list=&uses[m as usize];let p=list.partition_point(|(i,_)|*i<=end);if p==list.len(){return(true,serde_json::json!({"reason":"NO_LATER_REFERENCE"}));}let(i,kill)=list[p];(kill,serde_json::json!({"next_op":i,"kill":kill,"row":row(&ops[i])}))};
let mut out=Vec::new();let mut counts=std::collections::BTreeMap::new();let mut delta=0u64;
for(s,e)in spans{let mut reason=String::new();let mut accept=false;let mut cost=0;let mut detail=serde_json::json!({});let mut family="UNHANDLED";
if s==e&&ops[s].kind==R&&dep[s]==0{family="REDUNDANT_ZERO_RESET";accept=true;}
else if ops[s].kind==CCX&&ops[s].q_target.0==z&&ops[s].c_condition.0==u64::MAX&&dep[s]==0&&ops[e].kind==Hmr&&ops[e].q_target.0==z&&ops[e].c_condition.0==u64::MAX&&dep[e]==0&&e+1<ops.len(){let(a,b,m)=(ops[s].q_control1.0,ops[s].q_control2.0,ops[e].c_target.0);let(ph,di)=death(m,e+1);if !phase(&ops[e+1],a,b,m){reason="NO_EXACT_PHASE_CORRECTION".into();}else if !ph{reason="REMOVED_MR_BIT_LIVE".into();detail=di;}else{
if e>=s+3&&ops[s+1].kind==CX&&ops[s+1].q_target.0==z&&ops[s+1].c_condition.0==u64::MAX{let c=ops[s+1].q_control1.0;let last=&ops[e-1];if cx(last,c,z)&&c!=a&&c!=b&&c!=z{
let interior=&ops[s+2..e-1];let cclean=interior.iter().all(|o|!qrefs(o).contains(&c));let abstable=interior.iter().all(|o|!writes(o,a)&&!writes(o,b));let zread=interior.iter().all(|o|!writes(o,z));let balanced=dep[s+2..e].iter().all(|v|*v>=dep[s]);
if cclean&&abstable&&zread&&balanced{family="BORROWED_MIXED_CARRY";accept=true;cost=1;detail=serde_json::json!({"A":a,"B":b,"borrow_C":c,"MR":m,"death":di,"interior_C_no_reference":cclean,"A_B_stable":abstable,"Z_readonly":zread,"replacement":"CCX(A,B,C); interior Z->C; CCX(A,B,C); delete final HMR+conditionalCZ"});}else{reason=format!("BORROW_PREMISES_FAIL:C_absent={cclean},ABstable={abstable},Zreadonly={zread},balanced={balanced}");}
}}
if !accept&&e==s+16{let c=ops[s+1].q_control1.0;let dd=ops[s+4].q_target.0;let ee=ops[s+6].q_target.0;let distinct=[a,b,c,dd,ee,z].into_iter().collect::<std::collections::BTreeSet<_>>().len()==6;let ok=distinct&&cx(&ops[s+1],c,a)&&cx(&ops[s+2],c,z)&&cx(&ops[s+3],c,b)&&cx(&ops[s+4],z,dd)&&cx(&ops[s+5],z,a)&&ccx(&ops[s+6],a,dd,ee)&&cx(&ops[s+7],z,a)&&cx(&ops[s+8],z,ee)&&cx(&ops[s+9],z,dd)&&cx(&ops[s+10],a,ee)&&cx(&ops[s+11],a,dd)&&cx(&ops[s+12],z,dd)&&cx(&ops[s+13],c,z)&&cx(&ops[s+14],c,b)&&cx(&ops[s+15],c,a);if ok{family="SCRATCHFREE_FOUR_TOFFOLI_CARRY";accept=true;cost=2;detail=serde_json::json!({"A":a,"B":b,"C":c,"D":dd,"E":ee,"MR":m,"death":di,"proof":"peak-carry4-boolean-proof.json"});}}
if !accept&&e>s&&ops[s+1..e].iter().all(|o|o.kind==CX&&o.q_control1.0==z&&o.c_condition.0==u64::MAX&&o.q_target.0!=a&&o.q_target.0!=b){let targets=ops[s+1..e].iter().map(|o|o.q_target.0).collect::<Vec<_>>();let donor=(0..z).find(|q|*q!=a&&*q!=b&&!targets.contains(q)).unwrap();family="DIRTY_BORROW_AND_FANOUT";accept=true;cost=1;detail=serde_json::json!({"A":a,"B":b,"donor":donor,"targets":targets,"MR":m,"death":di});}
}}
if accept{delta+=cost;}*counts.entry(family).or_insert(0usize)+=1;out.push(serde_json::json!({"start":s,"end_inclusive":e,"length":e-s+1,"accepted":accept,"family":family,"delta_T_static_unconditional":cost,"reason":reason,"detail":detail,"first8":ops[s..=e].iter().take(8).map(row).collect::<Vec<_>>(),"last8":ops[s..=e].iter().rev().take(8).map(row).collect::<Vec<_>>()}));}
let report=serde_json::json!({"status":"SOURCE_BOUND_METADATA_CONTRACT_AUDIT_NO_FULL_CANDIDATE","source":args[1],"nq":nq,"nb":nb,"ops":ops.len(),"top":z,"top_reference_ops":used,"spans":out.len(),"family_counts":counts,"accepted_delta_T_static":delta,"all_spans":out,"not_claimed":["Q1233","all spans covered","actual executedT","phase/MR native primitive proof","full source generation"]});println!("{report}");}
