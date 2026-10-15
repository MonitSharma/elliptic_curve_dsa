//! Observation-only arithmetic-stage trace. Not a scored candidate.
use crate::circuit::{analyze_ops, Op, QubitId};
use crate::sim::Simulator;
use alloy_primitives::U256;
use sha3::{Shake256, digest::{Update, ExtendableOutput}};
use std::sync::Mutex;
static MARKS: Mutex<Vec<(&'static str, usize)>> = Mutex::new(Vec::new());
pub fn mark(name: &'static str, at: usize) { MARKS.lock().unwrap().push((name, at)); }
fn sub(a: U256, b: U256, p: U256) -> U256 { if a >= b { a-b } else { p-(b-a) } }
fn add(a: U256, b: U256, p: U256) -> U256 { a.add_mod(b, p) }
pub fn run(ops: &[Op], offset: U256) {
    let root = "/home/hclau/ecdsa_research/arithmetic-repair-20261015";
    let (nq, nb, _, regs) = analyze_ops(ops.iter());
    let p = super::SECP256K1_P;
    let mut marks = MARKS.lock().unwrap().clone();
    marks.push(("end", ops.len()));
    eprintln!("TRACE_METADATA ops={} nq={nq} nb={nb} offset={offset:#x} marks={marks:?}", ops.len());
    for family in ["independent", "structured", "candidate"] {
        let text = std::fs::read_to_string(format!("{root}/packets/{family}.tsv")).unwrap();
        let points: Vec<[U256; 6]> = text.lines().map(|line| {
            let v: Vec<_> = line.split_whitespace().skip(1).map(|v| U256::from_str_radix(v.trim_start_matches("0x"), 16).unwrap()).collect();
            v.try_into().unwrap()
        }).collect();
        let mut first_stage = vec![None; points.len()];
        let mut final_bad = 0;
        let mut final_phase = 0;
        let mut final_dirty = 0;
        for (batch, rows) in points.chunks(64).enumerate() {
            let mut h = Shake256::default(); h.update(b"arithmetic-repair-stage-v1");
            h.update(family.as_bytes()); h.update(&(batch as u64).to_le_bytes());
            let mut rng = h.finalize_xof();
            let mut sim = Simulator::new(nq as usize, nb as usize, &mut rng);
            for (lane, v) in rows.iter().enumerate() { for k in 0..4 { sim.set_register(&regs[k], v[k], lane); } }
            let mask = if rows.len() == 64 { u64::MAX } else { (1 << rows.len())-1 };
            let mut cursor = 0;
            for &(stage, at) in &marks {
                // Top-level phase boundaries have balanced condition stacks.
                sim.apply_iter(ops[cursor..at].iter()); cursor = at;
                let mut bad_x = 0; let mut bad_y = 0;
                for (lane, v) in rows.iter().enumerate() {
                    let slope = sub(v[1], v[3], p).mul_mod(sub(v[0], v[2], p).pow_mod(p-U256::from(2), p), p);
                    let expected = match stage {
                        "coord_y_sub" => [v[0], v[1]],
                        "divide" => [v[0], sub(v[1], v[3], p)],
                        "square" => [add(add(v[0], v[2], p), add(v[2], offset, p), p), slope],
                        "multiply" => [sub(v[2], v[4], p), slope],
                        "coord_y_sub_final" => [v[4], add(v[5], v[3], p)],
                        "end" => [v[4], v[5]],
                        _ => continue,
                    };
                    let got = [sim.get_register(&regs[0], lane), sim.get_register(&regs[1], lane)];
                    bad_x += usize::from(got[0] != expected[0]); bad_y += usize::from(got[1] != expected[1]);
                    if got != expected {
                        let shot = batch*64+lane;
                        if first_stage[shot].is_none() {
                            first_stage[shot] = Some(stage);
                            eprintln!("FIRST_BAD family={family} shot={shot} stage={stage} x_bad={} y_bad={} got_x={:#x} expected_x={:#x} got_y={:#x} expected_y={:#x}",got[0]!=expected[0],got[1]!=expected[1],got[0],expected[0],got[1],expected[1]);
                        }
                    }
                }
                eprintln!("STAGE family={family} batch={batch} stage={stage} bad_x={bad_x} bad_y={bad_y} phase_mask={:#x}", sim.phase&mask);
                if stage == "end" { final_bad += (0..rows.len()).filter(|&i| sim.get_register(&regs[0],i)!=rows[i][4] || sim.get_register(&regs[1],i)!=rows[i][5]).count(); }
            }
            final_phase += (sim.phase & mask).count_ones();
            let dirty = sim.qubits.iter().enumerate().filter(|(i, _)| *i >= 512).any(|(_, w)| w&mask != 0);
            final_dirty += usize::from(dirty);
            let _ = QubitId(0);
        }
        eprintln!("RAW_DIAGNOSTIC family={family} shots={} final_bad={final_bad} phase_shots={final_phase} dirty_batches={final_dirty} score=NONE", points.len());
    }
}
