// Existing fixed packets; unchanged reference/simulator. Never a scored evaluation.
fn main(){
    let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3,"ops packet.tsv");
    let ops=load_ops(&args[1]).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());
    let text=std::fs::read_to_string(&args[2]).unwrap();
    let rows:Vec<[U256;6]>=text.lines().map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();
    let(mut bad,mut phases,mut dirty)=(0,0,0);let mut total=0u64;
    for(batch,points)in rows.chunks(64).enumerate(){
        let mut h=Shake256::default();h.update(b"arithmetic-repair-stage-v1");
        let family=std::path::Path::new(&args[2]).file_stem().unwrap().to_str().unwrap();
        h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();
        let mut sim=Simulator::new(nq as usize,nb as usize,&mut rng);
        for(lane,v)in points.iter().enumerate(){for k in 0..4{sim.set_register(&regs[k],v[k],lane);}}
        sim.apply_iter(ops.iter());let mask=if points.len()==64{u64::MAX}else{(1u64<<points.len())-1};
        for(lane,v)in points.iter().enumerate(){
            let xb=sim.get_register(&regs[0],lane)!=v[4];let yb=sim.get_register(&regs[1],lane)!=v[5];
            if xb||yb{bad+=1;println!("FINAL_BAD shot={} x_bad={xb} y_bad={yb}",batch*64+lane);}
        }
        phases+=(sim.phase&mask).count_ones();total+=sim.stats.toffoli_gates;
        for reg in &regs{for q in reg{if let QubitOrBit::Qubit(q)=q{*sim.qubit_mut(*q)=0;}}}
        dirty+=usize::from(sim.qubits.iter().any(|w|w&mask!=0));
    }
    println!("FIXED_DIAGNOSTIC shots={} bad={bad} phase_shots={phases} dirty_batches={dirty} diagnostic_only_total_executed_t={total} score=NONE",rows.len());
}
