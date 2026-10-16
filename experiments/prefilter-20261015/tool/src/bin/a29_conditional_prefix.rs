#![recursion_limit = "256"]
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


include!("../input_anf_dag_trace.rs");
include!("../global_rng_anf_retained_masks.rs");
mod coeff_projection{use super::*;include!("../reset_projection.rs");pub(super)fn prove(ops:&[Op])->bool{reset_projection_certificate(ops,200000,1000).proved}}
mod symbol_projection{use super::*;include!("../reset_projection_symbols.rs");pub(super)fn prove(ops:&[Op])->bool{reset_projection_certificate(ops,200000,1000).proved}}
include!("../shadow_value_contract_bound.rs");
include!("../shadow_apply_region_bound.rs");
include!("../a29_mask_program_trace.rs");

fn compose_local_discrepancy(a:&mut GlobalAnf,q:&[GlobalPoly],result:&serde_json::Value,path:&str)->u32{
 let data=std::fs::read(path).unwrap();assert_eq!(&data[..8],b"MRMASK01");let n=read_u64(&data,8)as usize;let np=read_u64(&data,16)as usize;let nr=read_u64(&data,24)as usize;assert_eq!(nr,1);assert_eq!(data.len(),32+n*16+4);let ports=result["input_ports"].as_array().unwrap();assert_eq!(ports.len(),np);let mut input=Vec::new();
 for port in ports{let id=port[0].as_u64().unwrap()as usize;assert!(id<q.len());assert!(q[id].0.iter().all(|(key,c)|key.is_empty()||a.dag.find(*c)==0),"local guard quantum port is not universally MR-free");let value=q[id].0.iter().filter(|(key,_)|key.is_empty()).fold(0,|v,(_,c)|a.dag.xor(v,*c));input.push(value);}
 let mut map=Vec::new();for i in 0..n{let at=32+i*16;let field=|j|u32::from_le_bytes(data[at+j..at+j+4].try_into().unwrap());let(k,x,y,aux)=(field(0),field(4),field(8),field(12));assert_eq!(aux,0);let value=match k{0=>0,1=>1,2=>{assert!((x as usize)<np);input[x as usize]},3|4|5=>{assert!((x as usize)<i&&(y as usize)<i);if k==3{a.dag.xor(map[x as usize],map[y as usize])}else if k==4{a.dag.and(map[x as usize],map[y as usize])}else{a.or(map[x as usize],map[y as usize])}},_=>panic!("unknown local guard opcode")};map.push(value);}
 let root=u32::from_le_bytes(data[32+n*16..].try_into().unwrap())as usize;assert!(root<n);map[root]
}
fn coefficient_values(a:&GlobalAnf,inputs:&[(u32,QubitOrBit)],iq:&[u64],ib:&[u64])->Vec<u64>{let mut v=vec![0u64;a.dag.nodes.len()];v[1]=u64::MAX;for(id,wire)in inputs{v[*id as usize]=match wire{QubitOrBit::Qubit(q)=>iq[q.0 as usize],QubitOrBit::Bit(b)=>ib[b.0 as usize]};}for(i,n)in a.dag.nodes.iter().enumerate().skip(2){assert!(!n.random);match n.kind{2=>{},3=>v[i]=v[n.a as usize]^v[n.b as usize],4=>v[i]=v[n.a as usize]&v[n.b as usize],7=>v[i]=a.dag.large_defs[n.a as usize].iter().fold(0,|s,m|s^a.dag.monomials[*m as usize].iter().fold(u64::MAX,|s,j|s&v[*j as usize])),8=>v[i]=[n.a,n.b].iter().fold(u64::MAX,|s,m|s&a.dag.monomials[*m as usize].iter().fold(u64::MAX,|s,j|s&v[*j as usize])),_=>panic!("undeclared coefficient node")}}v}
fn finish_guard_prefix(ops:&[Op],stop:usize,args:&[String],a:&mut GlobalAnf,q:&[GlobalPoly],b:&[GlobalPoly],regs:&[Vec<QubitOrBit>],inputs:&[(u32,QubitOrBit)],iq:&[u64],ib:&[u64],guard:u32,receipts:&[serde_json::Value],contracts:&[serde_json::Value],mr:usize,seconds:f64){
 assert_eq!(inputs.len(),1024);let predicate=GlobalPoly(vec![(vec![u32::MAX-1],guard)]);let program=compile_mask_program(a,&[&predicate],&inputs.iter().map(|(id,_)|*id).collect::<Vec<_>>());program.save("a29-conditional-prefix-v1/public-discrepancy-guard.bin");let values=coefficient_values(a,inputs,iq,ib);let public:Vec<_>=inputs.iter().map(|(_,wire)|match wire{QubitOrBit::Qubit(id)=>iq[id.0 as usize],QubitOrBit::Bit(id)=>ib[id.0 as usize]}).collect();let safe=program.eval(&public)[0];assert_eq!(!safe,values[guard as usize]);let write=|path:&str,words:&[u64]|{let mut out=Vec::new();for word in words{out.extend_from_slice(&word.to_le_bytes());}std::fs::write(path,out).unwrap();};write("a29-conditional-prefix-v1/audit-input-u64le.bin",&public);write("a29-conditional-prefix-v1/audit-discrepancy-u64le.bin",&[!safe]);write("a29-conditional-prefix-v1/audit-safe-u64le.bin",&[safe]);
 let concrete=|p:&GlobalPoly|{let mut c=0;let mut d=0;for(key,value)in&p.0{if key.is_empty(){c^=values[*value as usize];}else{d|=values[*value as usize];}}(c,!d)};
 for seed in 0..4{let mut random=seeded(seed);let mut sim=Simulator::new(q.len(),b.len(),&mut random);sim.qubits.copy_from_slice(iq);sim.bits.copy_from_slice(ib);sim.apply_iter(ops[..stop].iter());for(i,p)in q.iter().enumerate(){let(c,k)=concrete(p);assert_eq!((sim.qubits[i]^c)&k,0,"protected prefix q{i} seed{seed}");}for(i,p)in b.iter().enumerate(){let(c,k)=concrete(p);assert_eq!((sim.bits[i]^c)&k,0,"protected prefix b{i} seed{seed}");}}
 let original=load_ops("../product-exact-20261015/tip/ops.bin").unwrap();for seed in 0..4{let mut ro=seeded(seed*2);let mut rn=seeded(seed*2+1);let mut old=Simulator::new(q.len(),b.len(),&mut ro);let mut new=Simulator::new(q.len(),b.len(),&mut rn);old.qubits.copy_from_slice(iq);new.qubits.copy_from_slice(iq);old.bits.copy_from_slice(ib);new.bits.copy_from_slice(ib);old.apply_iter(original[..3985789].iter());new.apply_iter(ops[..stop].iter());for wire in 0..q.len(){assert_eq!((old.qubits[wire]^new.qubits[wire])&safe,0,"guard-false protected original/A29 prefix equality q{wire}");}}
 let shots=std::fs::read_to_string(&args[2]).unwrap().lines().filter(|l|!l.trim().is_empty()).take(64).count();let lane_mask=if shots==64{u64::MAX}else{(1u64<<shots)-1};let ports:Vec<_>=inputs.iter().enumerate().map(|(port,(node,wire))|serde_json::json!({"port":port,"coefficient_node":node,"physical":match wire{QubitOrBit::Qubit(id)=>format!("q{}",id.0),QubitOrBit::Bit(id)=>format!("b{}",id.0)}})).collect();
 let report=serde_json::json!({"status":"FINITE_A29_PREFIX_COMPOSED_ALL29_INPUT_ONLY_DISCREPANCY_GUARD_REQUIRES_INDEPENDENT_REVIEW","source_old":"2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e","source_new":"1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522","stop_new":stop,"stop_old":3985789,"guard_input_only_dag_root":guard,"input_only_dag_nodes":a.dag.nodes.len(),"compiled_nodes":program.nodes.len(),"compiled_roots":program.roots,"input_ports":ports,"quantum_guard_ports_all_mr_free":true,"composed_guards":receipts,"prefix_shadow_contracts":contracts,"physical_mr_draws_in_prefix":mr,"protected_full_state_prefix_seeds":4,"protected_guard_false_original_A29_prefix_pairs":4,"audit_shots":shots,"audit_guard_false_shots":(safe&lane_mask).count_ones(),"audit_guard_true_shots":((!safe)&lane_mask).count_ones(),"polarity":"Raw root G=OR(delta) is discrepancy. G=0 permits transfer. MaskProgram.eval returns safe=NOT(G). Future combined old-mask dependency must be olddep OR G.","seconds":seconds,"authority":"Universal local contracts plus exact live-classical interface and all-input induction are required. Finite controls supplement those proofs; no runtime enabled."});println!("{report}");
}

include!("../a29_conditional_prefix_body.rs");

#[cfg(test)]mod prefix_guard_tests{use super::*;
 #[test]fn composition_uses_only_universally_input_only_quantum_ports(){
  let path=std::env::temp_dir().join(format!("conditional-guard-port-test-{}.bin",std::process::id()));let program=MaskProgram{nodes:vec![MaskNode{kind:0,a:0,b:0,aux:0},MaskNode{kind:1,a:0,b:0,aux:0},MaskNode{kind:2,a:0,b:0,aux:0}],roots:vec![2],inputs:1,old_live:0};program.save(path.to_str().unwrap());
  let result=serde_json::json!({"input_ports":[[0,2]]});let mut a=GlobalAnf::new(32);let x=a.dag.variable(false);let pure=GlobalAnf::constant(x);assert_eq!(compose_local_discrepancy(&mut a,&[pure],&result,path.to_str().unwrap()),x);
  let mr=a.fresh();assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(||compose_local_discrepancy(&mut a,&[mr],&result,path.to_str().unwrap()))).is_err(),"MR-dependent quantum entry may never become a public guard input");
  let bad=serde_json::json!({"input_ports":[[1,2]]});assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(||compose_local_discrepancy(&mut a,&[GlobalAnf::constant(x)],&bad,path.to_str().unwrap()))).is_err());std::fs::remove_file(path).unwrap();
 }
}
