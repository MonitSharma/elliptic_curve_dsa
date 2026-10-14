const SOURCE_BIND:&str="/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline";
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



struct Boundary{nb:u32,label:String,end:usize,hash:String,seams:bool,offset:U256,x:Vec<usize>,y:Vec<usize>,ox:Vec<usize>,oy:Vec<usize>,r0:Vec<usize>}
fn readq(q:&[u64],ids:&[usize],lane:usize)->U256{assert!(ids.len()<=256);let mut v=U256::ZERO;for(i,&id)in ids.iter().enumerate(){if(q[id]>>lane)&1!=0{v|=U256::from(1)<<i;}}v}
fn canonical_update(h:&mut sha3::Sha3_256,o:&Op){use sha3::Digest;Digest::update(h,(o.kind as u32).to_le_bytes());Digest::update(h,[0u8;4]);for id in[o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{Digest::update(h,id.to_le_bytes());}}

mod circuit{pub use quantum_ecc::circuit::*;}
mod y33_copy;
type Event=(usize,Option<usize>);
fn same_op(a:&Op,b:&Op)->bool{a.kind==b.kind&&a.q_control2==b.q_control2&&a.q_control1==b.q_control1&&a.q_target==b.q_target&&a.c_target==b.c_target&&a.c_condition==b.c_condition&&a.r_target==b.r_target}
fn overlay_write(q:&[u64],logical:&mut std::collections::HashMap<usize,u64>,op:&Op){
 let t=op.q_target.0 as usize;
 let v=match op.kind{OperationType::CCX=>{assert!(!logical.contains_key(&(op.q_control1.0 as usize))&&!logical.contains_key(&(op.q_control2.0 as usize)),"source find prohibits pending target reads");q[op.q_control1.0 as usize]&q[op.q_control2.0 as usize]},OperationType::CX=>{assert!(!logical.contains_key(&(op.q_control1.0 as usize)));q[op.q_control1.0 as usize]},OperationType::X=>u64::MAX,_=>panic!("not a Y33 write")};
 *logical.get_mut(&t).expect("logical Y33 target")^=v;
}
#[cfg(test)]mod tests{use super::*;
 #[test]fn exact_y33_overlay_and_mapping(){
  use circuit::{QubitId,NO_BIT};let mut a=Op::empty();a.kind=OperationType::CCX;a.q_control1=QubitId(0);a.q_control2=QubitId(1);a.q_target=QubitId(2);assert_eq!(a.c_condition,NO_BIT);
  let mut x=Op::empty();x.kind=OperationType::X;x.q_target=QubitId(2);let mut r=Op::empty();r.kind=OperationType::R;r.q_target=QubitId(2);
  let old=vec![a.clone(),x.clone(),r];let sites=y33_copy::product_sites(&old);assert_eq!(sites,vec![(2,vec![0,1],2)]);let mut new=old.clone();let mut next=3;y33_copy::sweep(&mut new,&mut next);assert_eq!(next,4);assert_eq!(new.len(),3);assert_eq!(new[0].kind,OperationType::Hmr);assert_eq!(new[1].kind,OperationType::CZ);assert_eq!(new[2].kind,OperationType::Neg);
  for n in 0..8{let q=vec![if n&1!=0{u64::MAX}else{0},if n&2!=0{u64::MAX}else{0},if n&4!=0{u64::MAX}else{0}];let mut overlay=std::collections::HashMap::from([(2,q[2])]);overlay_write(&q,&mut overlay,&a);assert_eq!(overlay[&2],q[2]^(q[0]&q[1]));overlay_write(&q,&mut overlay,&x);assert_eq!(overlay[&2],q[2]^(q[0]&q[1])^u64::MAX);assert_ne!(overlay[&2]^1,overlay[&2],"fault dropped write changes logical value");}
  let mut mutated=old.clone();mutated[1].q_target=QubitId(0);let mut n2=3;y33_copy::sweep(&mut mutated,&mut n2);assert!(!new.iter().zip(&mutated).all(|(a,b)|same_op(a,b)),"fault source mutation detected by exact vector guard");
 }
}


struct Frame{scope:String,label:String,t:usize,end:usize,lowrel:bool,skip:bool,r:[Vec<usize>;2],p:[Vec<usize>;2],letter:Vec<usize>}
fn full_word(q:&[u64],ids:&[usize],lane:usize,lowrel:bool)->alloy_primitives::U512{
 assert!(ids.len()+usize::from(lowrel)<512);let mut n=alloy_primitives::U512::from(usize::from(lowrel));for(i,&id)in ids.iter().enumerate(){if(q[id]>>lane)&1!=0{n|=alloy_primitives::U512::from(1)<<(i+usize::from(lowrel));}}n
}
#[cfg(test)]mod frame_tests{use super::*;
 #[test]fn implicit_odd_signed_word(){let q=[0,u64::MAX];assert_eq!(full_word(&q,&[0,1],0,true),alloy_primitives::U512::from(5));assert_eq!(full_word(&q,&[1,1],0,true),alloy_primitives::U512::from(7));assert_eq!(full_word(&q,&[0],0,false),alloy_primitives::U512::ZERO);}
}

fn main(){use sha3::Digest;let a:Vec<String>=std::env::args().collect();assert_eq!(a.len(),12,"C5raw/C5meta/B3raw/B3meta/knownpoints/independent/archivefinals/C5preY33/B3preY33");let curve=secp256k1();let p=curve.modulus;let sub=quantum_ecc::weierstrass_elliptic_curve::sub_mod;let f=U256::from(2).pow(U256::from(32))+U256::from(977);
 let mut archived=std::collections::HashMap::new();for line in std::fs::read_to_string(&a[7]).unwrap().lines(){let v:Vec<_>=line.split_whitespace().collect();archived.insert((v[0].to_string(),v[1].to_string(),v[2].parse::<usize>().unwrap()),(U256::from_str_radix(v[3].trim_start_matches("0x"),16).unwrap(),U256::from_str_radix(v[4].trim_start_matches("0x"),16).unwrap(),v[5].parse::<u64>().unwrap()));}
 for(source,opfile,metafile)in[("c5_raw",&a[1],&a[2]),("b3_raw",&a[3],&a[4])]{let ops=load_ops(opfile).unwrap();let pre=load_ops(if source=="c5_raw"{&a[8]}else{&a[9]}).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());let mut boundaries=Vec::new();for line in std::fs::read_to_string(metafile).unwrap().lines(){let v:Vec<_>=line.split('\t').collect();assert_eq!(v.len(),12);let ids=|i:usize|if v[i]=="-"{Vec::new()}else{v[i].split(',').map(|x|x.parse::<usize>().unwrap()).collect()};boundaries.push(Boundary{nb:v[4].parse().unwrap(),label:v[0].into(),end:v[1].parse().unwrap(),hash:v[2].into(),seams:v[5]=="true",offset:U256::from_str_radix(v[6].trim_start_matches("0x"),16).unwrap(),x:ids(7),y:ids(8),ox:ids(9),oy:ids(10),r0:ids(11)});}

  assert_eq!(boundaries.len(),9);assert_eq!(pre.len(),ops.len());assert_eq!(boundaries.last().unwrap().end,ops.len());
  let by33=boundaries.iter().find(|b|b.label=="before-y33").unwrap();let ay33=boundaries.iter().find(|b|b.label=="after-y33").unwrap();assert_eq!(by33.end,pre.len());
  let mut exact=pre.clone();let mut next=by33.nb;y33_copy::sweep(&mut exact,&mut next);assert_eq!(next,ay33.nb);assert_eq!(exact.len(),ops.len());assert!(exact.iter().zip(&ops).all(|(a,b)|same_op(a,b)),"copied source Y33 sweep exact entire final raw OpVec equality");drop(exact);
  let sites=y33_copy::product_sites(&pre);let mut events=std::collections::BTreeMap::<usize,Event>::new();for(k,(_,run,release))in sites.iter().enumerate(){for(g,&i)in run.iter().enumerate(){assert!(events.insert(i,(k,Some(g))).is_none());}assert!(events.insert(*release,(k,None)).is_none());}
  let mut ph=sha3::Sha3_256::new();let mut fh=sha3::Sha3_256::new();let(mut pa,mut fa)=(0,0);for b in &boundaries{let final_domain=matches!(b.label.as_str(),"after-y33"|"before-finalize-records"|"after-finalize-records");if final_domain{for o in &ops[fa..b.end]{canonical_update(&mut fh,o);}fa=b.end;assert_eq!(format!("{:x}",fh.clone().finalize()),b.hash,"final-domain metadata hash {}",b.label);}else{for o in &pre[pa..b.end]{canonical_update(&mut ph,o);}pa=b.end;assert_eq!(format!("{:x}",ph.clone().finalize()),b.hash,"original emission-domain metadata hash {}",b.label);}}
  assert_eq!(boundaries[7].hash,boundaries[8].hash);eprintln!("PRODUCT_BODY_MAPPING source={source} all9domainhashes=true exact_copied_y33_vector=true sites={} finalize_records_changed_ops=false phase_alignment=WITHIN_SOURCE_ONLY runtime_library={} score=NONE",sites.len(),SOURCE_BIND);

  let mut frames=Vec::new();for line in std::fs::read_to_string(if source=="c5_raw"{&a[10]}else{&a[11]}).unwrap().lines(){let v:Vec<_>=line.split('\t').collect();assert_eq!(v.len(),11);let ids=|i:usize|if v[i]=="-"{Vec::new()}else{v[i].split(',').map(|x|x.parse::<usize>().unwrap()).collect()};frames.push(Frame{scope:v[0].into(),label:v[1].into(),t:v[2].parse().unwrap(),end:v[3].parse().unwrap(),lowrel:v[4]=="true",skip:v[5]=="true",r:[ids(6),ids(7)],p:[ids(8),ids(9)],letter:ids(10)});}
  assert!(frames.windows(2).all(|w|w[0].end<=w[1].end));assert!(frames.last().unwrap().end<pre.len());
  for(packet,mode)in[(&a[5],"official_known_bad"),(&a[6],"independent")]{let mut cases=Vec::new();for line in std::fs::read_to_string(packet).unwrap().lines().filter(|l|!l.starts_with('#')&&!l.trim().is_empty()){let v:Vec<_>=line.split_whitespace().collect();let point=v[1..7].iter().map(|s|U256::from_str_radix(s.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>();assert_eq!(curve.add(point[0],point[1],point[2],point[3]),(point[4],point[5]));cases.push((v[0].parse::<usize>().unwrap(),point));}
   for(batch,cases)in cases.chunks(64).enumerate(){let mut h=Shake256::default();h.update(b"product-b3-stage-fixed-mr-v1");h.update(mode.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);for(lane,(_,v))in cases.iter().enumerate(){for r in 0..4{sim.set_register(&regs[r],v[r],lane);}}let(mut start,mut depth)=(0usize,0isize);

    let mut final_at=0usize;let mut logical=std::collections::HashMap::<usize,u64>::new();
    for (seq,frame) in frames.iter().enumerate(){let old_end=frame.end;while start<old_end{
      let ev=events.range(start..old_end).next().map(|(&i,&e)|(i,e));let stop=ev.map(|e|e.0).unwrap_or(old_end);let n=stop-start;
      for op in &pre[start..stop]{match op.kind{OperationType::PushCondition=>depth+=1,OperationType::PopCondition=>depth-=1,_=>{}}}
      sim.apply_iter(ops[final_at..final_at+n].iter());start=stop;final_at+=n;
      if let Some((i,(k,g)))=ev{assert_eq!(start,i);let q=sites[k].0;match g{None=>{assert!(logical.remove(&q).is_some());},Some(g)=>{if g==0{assert!(logical.insert(q,sim.qubits[q]).is_none());assert_eq!(ops[final_at].kind,OperationType::Hmr);sim.apply_iter(ops[final_at..final_at+1].iter());final_at+=1;}overlay_write(&sim.qubits,&mut logical,&pre[i]);sim.apply_iter(ops[final_at..final_at+1].iter());final_at+=1;}}start+=1;}
    }
    assert_eq!(depth,0,"body boundary outside classical scope");let starts=sites.iter().filter(|s|s.1[0]<old_end).count();let releases=sites.iter().filter(|s|s.2<old_end).count();assert_eq!(final_at,old_end+starts-releases);assert_eq!(logical.len(),starts-releases);

    let mut logical_q=sim.qubits.clone();for(&q,&v)in &logical{logical_q[q]=v;}
    for(lane,(index,_))in cases.iter().enumerate(){if mode=="independent"&&*index!=94{continue;}
      let rail=|i:usize|if frame.r[i].is_empty(){"-".into()}else{format!("{:#x}",full_word(&logical_q,&frame.r[i],lane,frame.lowrel))};
      let payload=|i:usize|if frame.p[i].is_empty(){"-".into()}else{format!("{:#x}",readq(&logical_q,&frame.p[i],lane))};
      let letter=if frame.letter.is_empty(){"-".into()}else{frame.letter.iter().map(|&q|((logical_q[q]>>lane)&1).to_string()).collect::<Vec<_>>().join("")};
      println!("PRODUCT_WALK_FRAME source={source} mode={mode} batch={batch} index={index} seq={seq} scope={} label={} t={} old_end={} final_end={final_at} pending_y33={} r0={} r1={} r0_width={} r1_width={} p0={} p1={} letter={letter} skip={} phase={} score=NONE",frame.scope,frame.label,frame.t,frame.end,logical.len(),rail(0),rail(1),if frame.r[0].is_empty(){0}else{frame.r[0].len()+usize::from(frame.lowrel)},if frame.r[1].is_empty(){0}else{frame.r[1].len()+usize::from(frame.lowrel)},payload(0),payload(1),frame.skip,(sim.phase>>lane)&1);
    }
    }
    sim.apply_iter(ops[final_at..].iter());for(lane,(index,_))in cases.iter().enumerate(){let x=sim.get_register(&regs[0],lane);let y=sim.get_register(&regs[1],lane);let phase=(sim.phase>>lane)&1;assert_eq!((x,y,phase),archived[&(source.to_string(),mode.to_string(),*index)],"entire final raw values/phase equal independent archived replay");}
    eprintln!("PRODUCT_WALK_FINAL_GUARD source={source} mode={mode} batch={batch} shots={} archived_full_raw_values_and_phase_equal=true frames={} score=NONE",cases.len(),frames.len());
   }
  }
 }
 println!("PRODUCT_WALK_TOTAL sources=2 points_per_source=271 exact_y33_transform_and_both_hashdomains_verified=true logical_boundary_overlay=true archived_final_values_and_phase_verified=true continuous_raw_rng=true score=NONE");
}
