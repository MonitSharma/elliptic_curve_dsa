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

fn validation_rng(seed:u64)->sha3::Shake256Reader{let mut h=Shake256::default();h.update(b"paired-helper-guard-validation-only-v1");h.update(&seed.to_le_bytes());h.finalize_xof()}
fn dirty_word(x:u64)->u64{let mut x=x.wrapping_add(0x9e3779b97f4a7c15);x=(x^(x>>30)).wrapping_mul(0xbf58476d1ce4e5b9);x=(x^(x>>27)).wrapping_mul(0x94d049bb133111eb);x^(x>>31)}
fn main(){
 let args:Vec<_>=std::env::args().collect();let old=load_ops(&args[1]).unwrap();let new=load_ops(&args[2]).unwrap();
 let prefix:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(&args[3]).unwrap()).unwrap();assert_eq!(prefix["source_sha256"],"1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522");
 let zeros:std::collections::BTreeSet<u64>=prefix["row"]["required_proved_zero_entry_wires"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap()).collect();
 let metadata:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(&args[4]).unwrap()).unwrap();let payload=metadata["acc"][56].as_u64().unwrap()as usize;
 let before=std::time::Instant::now();let co=shadow_value_contract_with_zeros(&old,500000,10000,&zeros);let cn=shadow_value_contract_with_zeros(&new,500000,10000,&zeros);assert_eq!(cn.operation_digest.iter().map(|b|format!("{b:02x}")).collect::<String>(),prefix["row"]["source_region_digest_shake256_256"].as_str().unwrap(),"actual A29/frame digest mismatch");
 let mut report=serde_json::json!({"status":"UNKNOWN_LOCAL_CONTRACT","source_sha256":prefix["source_sha256"],"tick":metadata["tick"],"old_ops":old.len(),"new_ops":new.len(),"payload_next":payload,"required_A29_prefix_zero_qids":zeros,"induction_obligation":prefix["induction_obligation"],"old_local_status":co.status,"new_local_status":cn.status,"old_nodes":co.nodes,"new_nodes":cn.nodes,"old_caps":co.caps,"new_caps":cn.caps,"old_region_digest":co.operation_digest.iter().map(|b|format!("{b:02x}")).collect::<String>(),"new_region_digest":cn.operation_digest.iter().map(|b|format!("{b:02x}")).collect::<String>(),"classical_interface_authority":"Separate exact precision-family29 live-bit theorem required; this probe does not substitute for it."});
 if co.proved&&cn.proved{
  let mut a=GlobalAnf::new(32);let mut q=Vec::new();let mut portmap=Vec::new();
  for id in 0..1234u64{if zeros.contains(&id){q.push(GlobalAnf::constant(0));}else{let node=a.dag.variable(false);portmap.push((id,node));q.push(GlobalAnf::constant(node));}}
  let mut bits=std::collections::BTreeSet::new();for o in old.iter().chain(new.iter()){if o.c_condition.0!=u64::MAX{bits.insert(o.c_condition.0);}if matches!(o.kind,OperationType::Hmr|OperationType::BitInvert|OperationType::BitStore0|OperationType::BitStore1){bits.insert(o.c_target.0);}}
  let mut b=vec![GlobalAnf::constant(0);45701];for wire in &bits{b[*wire as usize]=a.fresh();}
  let initialq=q.clone();let initialb=b.clone();let mut qo=q.clone();let mut bo=b.clone();let mut qn=q;let mut bn=b;
  let mo=shadow_apply_region(&old,&mut a,&mut qo,&mut bo,&GlobalAnf::constant(1),&co);let mn=shadow_apply_region(&new,&mut a,&mut qn,&mut bn,&GlobalAnf::constant(1),&cn);
  let mut differences=Vec::new();let mut guard=0;let mut unknown_deltas=Vec::new();let mut delta=GlobalAnf::constant(0);
  for id in 0..1234{let difference=a.xor(&qo[id],&qn[id]);if id==payload{delta=difference.clone();}if difference.0.iter().all(|(_,c)|a.dag.find(*c)==0){continue;}let rng_terms=difference.0.iter().filter(|(k,c)|!k.is_empty()&&a.dag.find(*c)!=0).count();let input=if rng_terms==0{Some(difference.0.iter().filter(|(k,_)|k.is_empty()).fold(0,|acc,(_,c)|a.dag.xor(acc,*c)))}else{None};if let Some(root)=input{guard=a.or(guard,root);}else{unknown_deltas.push(id);}differences.push(serde_json::json!({"q":id,"rng_terms":rng_terms,"input_root":input}));}
  let unresolved=unknown_deltas;let rng_terms=delta.0.iter().filter(|(k,c)|!k.is_empty()&&a.dag.find(*c)!=0).count();let input_delta=if rng_terms==0{Some(delta.0.iter().filter(|(k,_)|k.is_empty()).fold(0,|acc,(_,c)|a.dag.xor(acc,*c)))}else{None};
  if unresolved.is_empty(){let predicate=GlobalPoly(vec![(vec![u32::MAX-1],guard)]);let program=compile_mask_program(&a,&[&predicate],&portmap.iter().map(|(_,node)|*node).collect::<Vec<_>>());program.save(&format!("{}.bin",args[5]));
   let mut fixture=Vec::new();let mut expected=Vec::new();let mut safe=0u32;let mut unsafe_lanes=0u32;
   for trial in 0..4u64{
    let inputq:Vec<u64>=(0..1234u64).map(|id|if zeros.contains(&id){0}else if trial==0{0}else if trial==1{u64::MAX}else{dirty_word((trial<<32)^id)}).collect();
    let inputb:Vec<u64>=(0..45701u64).map(|id|dirty_word((trial<<40)^id^0x7392)).collect();let words:Vec<_>=portmap.iter().map(|(id,_)|inputq[*id as usize]).collect();
    let guard_word=!program.eval(&words)[0];let mut ro=validation_rng(trial*2);let mut rn=validation_rng(trial*2+1);let mut so=Simulator::new(1234,45701,&mut ro);let mut sn=Simulator::new(1234,45701,&mut rn);so.qubits.copy_from_slice(&inputq);sn.qubits.copy_from_slice(&inputq);so.bits.copy_from_slice(&inputb);sn.bits.copy_from_slice(&inputb);so.apply_iter(old.iter());sn.apply_iter(new.iter());
    let observed=so.qubits.iter().zip(&sn.qubits).fold(0u64,|acc,(x,y)|acc|(*x^*y));assert_eq!(guard_word,observed,"compiled exact guard vs protected full actual quantum helper trial{trial}");
    safe+=(!guard_word).count_ones();unsafe_lanes+=guard_word.count_ones();for word in words{fixture.extend_from_slice(&word.to_le_bytes());}expected.extend_from_slice(&observed.to_le_bytes());
   }
   std::fs::write(format!("{}.input-u64le.bin",args[5]),fixture).unwrap();std::fs::write(format!("{}.expected-guard-u64le.bin",args[5]),expected).unwrap();
   report["protected_actual_helper_quantum_comparison_shots"]=serde_json::json!(256);report["protected_independent_internal_mr_pairs"]=serde_json::json!(4);report["arbitrary_dirty_entry_quantum_and_classical_controls"]=serde_json::json!(true);report["validation_guard_false_lanes"]=serde_json::json!(safe);report["validation_guard_true_lanes"]=serde_json::json!(unsafe_lanes);
report["guard_compiled_nodes"]=serde_json::json!(program.nodes.len());report["guard_compiled_root"]=serde_json::json!(program.roots);}
  report["all_nonzero_q_differences"]=serde_json::json!(differences);report["discrepancy_OR_input_root"]=serde_json::json!(guard);report["declared_theorem"]=serde_json::json!("Under the source-bound exact zero-entry predicates, OR of every input-only quantum output XOR-difference being false implies complete physical quantum-state equality for all independent internal measurements. Classical live-interface and prefix induction remain separate required obligations.");
  let mut dirty=qn[0].clone();dirty=a.xor(&dirty,&GlobalAnf::constant(1));let changed=a.xor(&qo[0],&dirty);assert!(changed.0.iter().any(|(_,c)|a.dag.find(*c)!=0),"negative control missed an unrelated output change");
  report["status"]=serde_json::json!(if unresolved.is_empty()&&rng_terms==0{"PAIRED_FULL_QUANTUM_INTERFACE_PASS_INPUT_ONLY_DIFFERENCE_GUARD"}else{"UNKNOWN_PAIRED_FULL_INTERFACE"});report["unresolved_common_qids"]=serde_json::json!(unresolved);report["delta_rng_terms"]=serde_json::json!(rng_terms);report["delta_input_root"]=serde_json::json!(input_delta);report["input_ports"]=serde_json::json!(portmap);report["local_classical_entry_variables"]=serde_json::json!(bits.len());report["measurement_words_old_new"]=serde_json::json!([mo,mn]);report["input_dag_nodes"]=serde_json::json!(a.dag.nodes.len());report["global_caps"]=serde_json::json!(a.capped);report["shared_input_and_dag_namespace"]=serde_json::json!(true);report["independent_internal_mr_old_new"]=serde_json::json!(true);report["negative_unrelated_q_change_detected"]=serde_json::json!(true);let _=(initialq,initialb);
 }
 report["seconds"]=serde_json::json!(before.elapsed().as_secs_f64());println!("{report}");
}
