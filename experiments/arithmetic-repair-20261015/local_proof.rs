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
