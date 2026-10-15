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


// Independent reconstruction of every rewrite, followed by event-aligned replay.
#[derive(Debug)]
struct Lease{donor:u64,start:usize,end:usize,uses:Vec<usize>}
fn newop(k:OperationType,a:Option<u64>,b:Option<u64>,t:Option<u64>,bt:Option<u64>,c:Option<u64>)->Op {
    let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a.unwrap_or(u64::MAX));o.q_control2=QubitId(b.unwrap_or(u64::MAX));
    o.q_target=QubitId(t.unwrap_or(u64::MAX));o.c_target=BitId(bt.unwrap_or(u64::MAX));o.c_condition=BitId(c.unwrap_or(u64::MAX));o.validate();o
}
fn reconstruction(left:&[Op],right:&[Op],log:&str,nb:u64)->(Vec<usize>,usize){
    use OperationType as K;use std::collections::HashMap;
    let mut plans=vec![];
    for line in log.lines().filter(|l|l.starts_with("LAZY_WINDOW ")){
        let field=|name:&str|->u64{line.split_whitespace().find_map(|s|s.strip_prefix(name)).unwrap().parse().unwrap()};
        let uses=line.split_once("uses=[").unwrap().1.trim_end_matches(']').split(',').map(|s|s.trim().parse().unwrap()).collect();
        plans.push(Lease{donor:field("donor="),start:field("start=") as usize,end:field("end=") as usize,uses});
    }
    assert!(!plans.is_empty());let mut start=HashMap::<usize,Vec<usize>>::new();let mut end=HashMap::<usize,Vec<usize>>::new();let mut use_at=HashMap::new();
    for (j,p) in plans.iter().enumerate(){start.entry(p.start).or_default().push(j);end.entry(p.end).or_default().push(j);for i in &p.uses{assert!(use_at.insert(*i,j).is_none());}}
    let mut live=HashMap::<u64,usize>::new();let mut cursor=0;let mut old_mr=0;let mut map=vec![];
    let mut emit=|o:Op,origin:usize|{assert_eq!(right.get(cursor),Some(&o),"reconstruction differs at candidate op {cursor}");cursor+=1;if matches!(o.kind,K::Hmr|K::R){map.push(origin);}};
    let store=|b:u64,one:bool|newop(if one{K::BitStore1}else{K::BitStore0},None,None,None,Some(b),None);
    let push=|b:u64|newop(K::PushCondition,None,None,None,None,Some(b));let pop=||newop(K::PopCondition,None,None,None,None,None);
    let mut skipped=0;
    for i in 0..=left.len(){
        if let Some(js)=end.get(&i){for &j in js{
            let p=&plans[j];let v=nb+3*j as u64;let o=left[*p.uses.last().unwrap()];
            emit(push(v),usize::MAX);emit(newop(K::Hmr,None,None,Some(p.donor),Some(v+2),None),usize::MAX);
            emit(newop(K::CZ,Some(o.q_control1.0),None,Some(o.q_control2.0),None,Some(v+2)),usize::MAX);emit(pop(),usize::MAX);
            for b in v..v+3{emit(store(b,false),usize::MAX);}assert_eq!(live.remove(&p.donor),Some(j));
        }}
        if let Some(js)=start.get(&i){for &j in js{let p=&plans[j];assert!(live.insert(p.donor,j).is_none());for b in nb+3*j as u64..nb+3*j as u64+3{emit(store(b,false),usize::MAX);}}}
        if i==left.len(){break;}let o=left[i];let is_mr=matches!(o.kind,K::Hmr|K::R);
        if let Some(&j)=use_at.get(&i){
            assert_eq!(o.kind,K::CCX);let p=&plans[j];let v=nb+3*j as u64;
            if o.c_condition.0!=u64::MAX{emit(push(o.c_condition.0),usize::MAX);}
            emit(store(v+1,true),usize::MAX);emit(newop(K::BitInvert,None,None,None,Some(v+1),Some(v)),usize::MAX);emit(push(v+1),usize::MAX);
            emit(newop(K::CCX,Some(o.q_control1.0),Some(o.q_control2.0),Some(p.donor),None,None),usize::MAX);emit(store(v,true),usize::MAX);emit(pop(),usize::MAX);
            emit(newop(K::CX,Some(p.donor),None,Some(o.q_target.0),None,None),usize::MAX);emit(store(v+1,false),usize::MAX);
            if o.c_condition.0!=u64::MAX{emit(pop(),usize::MAX);}
        }else if o.kind==K::R&&live.contains_key(&o.q_target.0){skipped+=1;}else{emit(o,if is_mr{old_mr}else{usize::MAX});}
        if is_mr{old_mr+=1;}
    }
    assert_eq!(cursor,right.len());assert!(live.is_empty());
    println!("RECONSTRUCTION_OK leases={} old_MR={old_mr} new_MR={} skipped_zero_R={skipped} original_tail_preserved=true",plans.len(),map.len());(map,old_mr)
}
struct Words{words:Vec<u64>,at:usize}
impl XofReader for Words{fn read(&mut self,out:&mut [u8]){assert_eq!(out.len(),8);out.copy_from_slice(&self.words[self.at].to_le_bytes());self.at+=1;}}
fn main(){
    let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),6,"left right build-log mode packet.tsv");
    let left=load_ops(&args[1]).unwrap();let right=load_ops(&args[2]).unwrap();
    let(nq,nb,_,regs)=analyze_ops(left.iter());let(rq,rb,_,rregs)=analyze_ops(right.iter());assert!(rq>=nq);assert_eq!(regs,rregs);
    let(map,nold)=reconstruction(&left,&right,&std::fs::read_to_string(&args[3]).unwrap(),nb);
    let mode=&args[4];let curve=secp256k1();let mut packets=vec![];
    let mut xof=if mode=="candidate"{fiat_shamir_seed(&right)}else{let mut h=Shake256::default();h.update(b"product-b3-independent-structured-v1");h.finalize_xof()};
    let size=if mode=="candidate"{NUM_TESTS}else{256};
    let beta=U256::from(2).pow_mod((curve.modulus-U256::from(1))/U256::from(3),curve.modulus);
    assert!(beta!=U256::from(1));assert_eq!(beta.pow_mod(U256::from(3),curve.modulus),U256::from(1));
    let mut file=File::create(&args[5]).unwrap();
    for i in 0..size{
        let mut a=[0u8;32];let mut b=[0u8;32];XofReader::read(&mut xof,&mut a);XofReader::read(&mut xof,&mut b);
        let mut t=curve.mul(curve.gx,curve.gy,U256::from_le_bytes(a));let o=curve.mul(curve.gx,curve.gy,U256::from_le_bytes(b));
        if mode=="structured"{if i%2==0{let d=curve.add(o.0,o.1,o.0,o.1);t=(d.0,curve.modulus-d.1);}else{t=(o.0.mul_mod(beta,curve.modulus),o.1);}}
        if t.0==o.0||(t.0.is_zero()&&t.1.is_zero())||(o.0.is_zero()&&o.1.is_zero()){continue;}
        assert!(curve.is_on_curve(t.0,t.1)&&curve.is_on_curve(o.0,o.1));let e=curve.add(t.0,t.1,o.0,o.1);
        writeln!(file,"{} {:#x} {:#x} {:#x} {:#x} {:#x} {:#x}",packets.len(),t.0,t.1,o.0,o.1,e.0,e.1).unwrap();packets.push([t.0,t.1,o.0,o.1,e.0,e.1]);
    }
    let(mut unequal,mut lb,mut rbads,mut lp,mut rp,mut ld,mut rd)=(0,0,0,0,0,0,0);let(mut lt,mut rt)=(0u64,0u64);
    for(batch,points)in packets.chunks(64).enumerate(){
        let mut seed=Shake256::default();seed.update(b"product-b3-paired-fixed-measurement-v1");seed.update(&(batch as u64).to_le_bytes());let mut independent=seed.finalize_xof();
        let mut lw=vec![0u64;nold];let mut rw=Vec::with_capacity(map.len());
        for &old in &map{let mut b=[0u8;8];if mode=="candidate"{XofReader::read(&mut xof,&mut b);}else{XofReader::read(&mut independent,&mut b);}let v=u64::from_le_bytes(b);rw.push(v);if old!=usize::MAX{lw[old]=v;}}
        let mut lx=Words{words:lw,at:0};let mut rx=Words{words:rw,at:0};
        let mut l=Simulator::new(nq as usize,nb as usize,&mut lx);let mut r=Simulator::new(rq as usize,rb as usize,&mut rx);
        for(lane,v)in points.iter().enumerate(){for k in 0..4{l.set_register(&regs[k],v[k],lane);r.set_register(&regs[k],v[k],lane);}}
        l.apply_iter(left.iter());r.apply_iter(right.iter());let mask=if points.len()==64{u64::MAX}else{(1u64<<points.len())-1};
        let equal=l.qubits.iter().zip(&r.qubits).all(|(a,b)|(a^b)&mask==0)&&l.bits.iter().zip(&r.bits).all(|(a,b)|(a^b)&mask==0)&&(l.phase^r.phase)&mask==0&&r.bits[nb as usize..].iter().all(|b|b&mask==0)&&r.qubits[nq as usize..].iter().all(|q|q&mask==0);
        unequal+=usize::from(!equal);lp+=usize::from(l.phase&mask!=0);rp+=usize::from(r.phase&mask!=0);
        for(lane,v)in points.iter().enumerate(){lb+=usize::from(l.get_register(&regs[0],lane)!=v[4]||l.get_register(&regs[1],lane)!=v[5]);rbads+=usize::from(r.get_register(&regs[0],lane)!=v[4]||r.get_register(&regs[1],lane)!=v[5]);}
        lt+=l.stats.toffoli_gates;rt+=r.stats.toffoli_gates;
        for reg in &regs{for q in reg{if let QubitOrBit::Qubit(q)=q{*l.qubit_mut(*q)=0;*r.qubit_mut(*q)=0;}}}
        ld+=usize::from(l.qubits.iter().any(|v|v&mask!=0));rd+=usize::from(r.qubits.iter().any(|v|v&mask!=0));
        println!("PAIRED_BATCH batch={batch} equal={equal} diagnostic_gate_saving={}",l.stats.toffoli_gates as i64-r.stats.toffoli_gates as i64);
        drop(l);drop(r);assert_eq!(lx.at,nold);assert_eq!(rx.at,map.len());
    }
    println!("DIAGNOSTIC_ONLY shots={} unequal_batches={unequal} left_bad={lb} right_bad={rbads} left_phase_batches={lp} right_phase_batches={rp} left_dirty_batches={ld} right_dirty_batches={rd} paired_gate_saving_total={} paired_gate_saving_mean={} score=NONE",packets.len(),lt as i64-rt as i64,(lt as f64-rt as f64)/packets.len() as f64);
    assert_eq!(unequal,0,"point-addition states or original classical bits changed");
}
