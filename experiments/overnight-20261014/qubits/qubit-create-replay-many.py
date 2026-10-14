"""Extend frozen replay v1 into a separate multi-batch diagnostic crate."""
from pathlib import Path
import sys

v1, dest = map(lambda s: Path(s).resolve(), sys.argv[1:3])
dest.joinpath("src").mkdir(parents=True, exist_ok=True)
source = v1.joinpath("src/main.rs").read_text()
prefix = source[:source.index("fn main()")]
main = r'''
fn main() {
    let a:Vec<String>=std::env::args().collect();
    assert!(a.len()>=4,"usage: replay-many ops.bin packet.tsv comma-separated-batches");
    let ops=load_ops(&a[1]).unwrap();let(nq,nb,_,regs)=analyze_ops(ops.iter());
    eprintln!("DIAGNOSTIC_ONLY ops={} qubits={nq} bits={nb} rng=same_fixed_words_mapping_may_differ",ops.len());
    let packet=std::fs::read_to_string(&a[2]).unwrap();let records:Vec<_>=packet.lines().filter(|s|!s.starts_with('#')).collect();
    for batch in a[3].split(',').map(|s|s.parse::<usize>().unwrap()) {
        let selected=&records[batch*64..records.len().min((batch+1)*64)];
        let values:Vec<Vec<U256>>=selected.iter().map(|s|s.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect()).collect();
        let mut h=Shake256::default();h.update(b"qubit-identical-input-replay-v1");h.update(&(batch as u64).to_le_bytes());let mut xof=h.finalize_xof();
        let mut sim=Simulator::new(nq as usize,nb as usize,&mut xof);
        for(lane,v)in values.iter().enumerate(){for r in 0..4{sim.set_register(&regs[r],v[r],lane);}}
        sim.apply_iter(ops.iter());let mut mismatches=0;
        for(lane,v)in values.iter().enumerate(){let x=sim.get_register(&regs[0],lane);let y=sim.get_register(&regs[1],lane);let ok=x==v[4]&&y==v[5];if !ok{mismatches+=1;}
          println!("SHOT {} ok={ok} target_x={:#x} target_y={:#x} offset_x={:#x} offset_y={:#x} got_x={x:#x} got_y={y:#x} expected_x={:#x} expected_y={:#x}",batch*64+lane,v[0],v[1],v[2],v[3],v[4],v[5]);}
        let live=if selected.len()==64{u64::MAX}else{(1u64<<selected.len())-1};println!("PHASE batch={batch} mask={:#018x}",sim.phase&live);
        for reg in &regs{for q in reg{if let QubitOrBit::Qubit(q)=q{*sim.qubit_mut(*q)=0;}}}
        let mut dirty=0;for q in 0..nq{let v=sim.qubit(QubitId(q))&live;if v!=0{dirty+=1;println!("ANCILLA batch={batch} q={q} mask={v:#018x}");}}
        println!("DIAGNOSTIC_RESULT batch={batch} mismatches={mismatches} phase_nonzero={} dirty_ancillas={dirty} score=NONE",sim.phase&live!=0);
    }
}
'''
dest.joinpath("src/main.rs").write_text(prefix + main)
dest.joinpath("Cargo.toml").write_text(v1.joinpath("Cargo.toml").read_text().replace('name = "qubit_replay_diagnostic"', 'name = "qubit_replay_many_diagnostic"'))
