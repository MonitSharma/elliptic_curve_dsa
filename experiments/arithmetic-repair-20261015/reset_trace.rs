//! Locate reset operands that are nonzero. External diagnostic only.
use crate::circuit::{analyze_ops, Op, OperationType};
use alloy_primitives::U256;
use sha3::{Shake256, digest::{Update, ExtendableOutput}};
use std::{collections::HashMap, panic::Location, sync::Mutex};
static RESETS: Mutex<Vec<(usize, &'static str, &'static Location<'static>)>> = Mutex::new(Vec::new());
pub fn record(at: usize, stage: &'static str, loc: &'static Location<'static>) { RESETS.lock().unwrap().push((at, stage, loc)); }
pub fn run(ops: &[Op]) {
    let root = "/home/hclau/ecdsa_research/arithmetic-repair-20261015";
    let (nq, nb, _, regs) = analyze_ops(ops.iter());
    let resets: HashMap<_,_> = RESETS.lock().unwrap().iter().map(|&(i,s,l)| (i,(s,l))).collect();
    for family in ["independent", "structured", "candidate"] {
        let text = std::fs::read_to_string(format!("{root}/packets/{family}.tsv")).unwrap();
        let points: Vec<[U256; 6]> = text.lines().map(|line| {
            let v: Vec<_> = line.split_whitespace().skip(1).map(|v| U256::from_str_radix(v.trim_start_matches("0x"), 16).unwrap()).collect();
            v.try_into().unwrap()
        }).collect();
        let (mut bad,mut phase_shots) = (0,0);
        for (batch, rows) in points.chunks(64).enumerate() {
            let mut h = Shake256::default(); h.update(b"arithmetic-repair-stage-v1");
            h.update(family.as_bytes()); h.update(&(batch as u64).to_le_bytes());
            let mut rng = h.finalize_xof(); let mut reference_rng = rng.clone();
            let mut sim = super::observed_sim::Simulator::new(nq as usize, nb as usize, &mut rng);
            let mut reference = crate::sim::Simulator::new(nq as usize, nb as usize, &mut reference_rng);
            for (lane,v) in rows.iter().enumerate() { for k in 0..4 { sim.set_register(&regs[k],v[k],lane); reference.set_register(&regs[k],v[k],lane); } }
            let mask = if rows.len()==64 {u64::MAX} else {(1u64<<rows.len())-1};
            let mut first = vec![None; rows.len()];
            sim.apply_observed(ops.iter(), |i,s,o,cond| {
                if o.kind!=OperationType::R {return;}
                let nz=s.qubits[o.q_target.0 as usize]&cond&mask;
                if nz==0 {return;}
                let provenance=resets.get(&i);
                for lane in 0..rows.len() {
                    if nz>>lane&1!=0 && first[lane].is_none() {
                        first[lane]=Some(i);
                        eprintln!("FIRST_NONZERO_RESET family={family} shot={} op={i} q={} provenance={provenance:?}",batch*64+lane,o.q_target.0);
                    }
                }
            });
            reference.apply_iter(ops.iter());
            assert_eq!(sim.qubits,reference.qubits,"observer qubits differ");
            assert_eq!(sim.bits,reference.bits,"observer bits differ");
            assert_eq!(sim.phase,reference.phase,"observer phase differs");
            assert_eq!(sim.stats.toffoli_gates,reference.stats.toffoli_gates);
            for (lane,v) in rows.iter().enumerate() {
                let xb=sim.get_register(&regs[0],lane)!=v[4]; let yb=sim.get_register(&regs[1],lane)!=v[5];
                if xb||yb {bad+=1;eprintln!("FINAL_BAD family={family} shot={} x_bad={xb} y_bad={yb} first_nonzero_reset={:?}",batch*64+lane,first[lane]);}
            }
            phase_shots+=(sim.phase&mask).count_ones();
        }
        eprintln!("RESET_DIAGNOSTIC family={family} shots={} final_bad={bad} phase_shots={phase_shots} observer_equal=true score=NONE",points.len());
    }
}
