//! Revisit exact support identities after the prefix-bound rewrites.
//! The earlier simplifier cannot see gates introduced by the later tables.
//! Keep measurement, reset, phase and allocation operations unchanged.
use crate::circuit::{Op, OperationType};

fn nonlinear_count(ops: &[Op]) -> usize {
    ops.iter()
        .filter(|op| matches!(op.kind, OperationType::CCX | OperationType::CCZ))
        .count()
}

pub(super) fn run(mut ops: Vec<Op>) -> Vec<Op> {
    for round in 0..2 {
        let before_ops = ops.len();
        let before_t = nonlinear_count(&ops);
        ops = super::truth_simplify::simplify_implications(ops);
        let after_t = nonlinear_count(&ops);
        assert!(
            after_t <= before_t,
            "final cleanup increased nonlinear gates"
        );
        eprintln!(
            "FINAL_CLEANUP round={round} ops={before_ops}->{} nonlinear={before_t}->{after_t}",
            ops.len()
        );
        if after_t == before_t && ops.len() == before_ops {
            break;
        }
    }
    ops
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::circuit::{BitId, QubitId};
    use crate::sim::Simulator;
    use sha3::digest::{ExtendableOutput, Update};

    #[test]
    fn exact_cleanup_preserves_values_phase_and_measurement_history() {
        let mut b = super::super::builder::Builder::new();
        let data = b.alloc_qubits(2);
        let t = b.alloc_qubit();
        let outcome = b.alloc_bit();
        b.ccx(data[0], data[1], t);
        b.cx(data[0], t);
        // a & (a XOR (a & b)) == a XOR (a & b).
        b.ccx(data[0], t, data[1]);
        b.cz(t, data[1]);
        b.hmr(t, outcome);
        b.cz_if(data[0], data[1], outcome);
        b.declare_qubit_register(&data);
        let original = b.take_ops();
        let cleaned = run(original.clone());
        assert!(nonlinear_count(&cleaned) < nonlinear_count(&original));
        for seed in 0u64..32 {
            let random = || {
                let mut h = sha3::Shake256::default();
                h.update(&seed.to_le_bytes());
                h.finalize_xof()
            };
            let mut ra = random();
            let mut rb = random();
            let mut a = Simulator::new(3, 1, &mut ra);
            let mut c = Simulator::new(3, 1, &mut rb);
            for sim in [&mut a, &mut c] {
                for lane in 0..64 {
                    *sim.qubit_mut(QubitId(data[0].0)) |= ((lane & 1) as u64) << lane;
                    *sim.qubit_mut(QubitId(data[1].0)) |= (((lane >> 1) & 1) as u64) << lane;
                }
            }
            a.apply_iter(original.iter());
            c.apply_iter(cleaned.iter());
            assert_eq!(a.qubits, c.qubits, "values at seed {seed}");
            assert_eq!(a.bits, c.bits, "measurement history at seed {seed}");
            assert_eq!(a.phase, c.phase, "phase at seed {seed}");
            assert_eq!(a.bit(BitId(outcome.0)), c.bit(BitId(outcome.0)));
            assert!(c.stats.toffoli_gates < a.stats.toffoli_gates);
        }
    }

    #[test]
    fn mutated_control_is_not_treated_as_its_old_value() {
        let mut b = super::super::builder::Builder::new();
        let data = b.alloc_qubits(3);
        let t = b.alloc_qubit();
        b.ccx(data[0], data[1], t);
        b.cx(data[0], t);
        b.cx(data[2], data[0]);
        b.ccx(data[0], t, data[1]);
        b.declare_qubit_register(&data);
        let original = b.take_ops();
        let cleaned = run(original.clone());
        assert_eq!(nonlinear_count(&cleaned), 2);
        let rng = || sha3::Shake256::default().finalize_xof();
        let mut ra = rng();
        let mut rb = rng();
        let mut a = Simulator::new(4, 0, &mut ra);
        let mut c = Simulator::new(4, 0, &mut rb);
        for sim in [&mut a, &mut c] {
            for lane in 0..64 {
                for i in 0..3 {
                    sim.qubits[i] |= (((lane >> i) & 1) as u64) << lane;
                }
            }
        }
        a.apply_iter(original.iter());
        c.apply_iter(cleaned.iter());
        assert_eq!(a.qubits, c.qubits);
        // The tempting stale-value CX replacement must actually be wrong.
        let mut broken = original.clone();
        let at = broken
            .iter()
            .rposition(|o| o.kind == OperationType::CCX)
            .unwrap();
        broken[at].kind = OperationType::CX;
        broken[at].q_control1 = t;
        broken[at].q_control2 = crate::circuit::NO_QUBIT;
        broken[at].validate();
        let mut rc = rng();
        let mut bad = Simulator::new(4, 0, &mut rc);
        for lane in 0..64 {
            for i in 0..3 {
                bad.qubits[i] |= (((lane >> i) & 1) as u64) << lane;
            }
        }
        bad.apply_iter(broken.iter());
        assert_ne!(
            a.qubits, bad.qubits,
            "negative control failed to detect a stale relation"
        );
    }

    #[test]
    fn implication_uses_captured_condition_not_mutated_bit_slot() {
        let mut b = super::super::builder::Builder::new();
        let data = b.alloc_qubits(2);
        let copy = b.alloc_qubit();
        let m = b.alloc_bit();
        b.hmr(copy, m);
        b.x_if_bit(copy, m);
        b.push_condition(m);
        b.bit_store0(m);
        b.ccx(copy, data[0], data[1]);
        b.pop_condition();
        // Outside the captured condition, neither control implies the other.
        b.ccx(copy, data[0], data[1]);
        b.cz(copy, data[1]);
        b.declare_qubit_register(&data);
        let original = b.take_ops();
        let cleaned = run(original.clone());
        assert_eq!(nonlinear_count(&original), 2);
        assert_eq!(nonlinear_count(&cleaned), 1);
        for seed in 0u64..32 {
            let rng = || {
                let mut h = sha3::Shake256::default();
                h.update(&seed.to_le_bytes());
                h.finalize_xof()
            };
            let mut ra = rng();
            let mut rb = rng();
            let mut a = Simulator::new(3, 1, &mut ra);
            let mut c = Simulator::new(3, 1, &mut rb);
            for sim in [&mut a, &mut c] {
                for lane in 0..64 {
                    for i in 0..2 {
                        sim.qubits[i] |= (((lane >> i) & 1) as u64) << lane;
                    }
                }
            }
            a.apply_iter(original.iter());
            c.apply_iter(cleaned.iter());
            assert_eq!(a.qubits, c.qubits);
            assert_eq!(a.bits, c.bits);
            assert_eq!(a.phase, c.phase);
        }
    }

    fn load_stream(path: &str) -> Vec<Op> {
        use std::io::Read;
        let mut f = std::fs::File::open(path).unwrap();
        let mut head = [0u8; 16];
        f.read_exact(&mut head).unwrap();
        assert_eq!(&head[..8], b"QECCOPSZ");
        let count = u64::from_le_bytes(head[8..].try_into().unwrap()) as usize;
        assert!(count < 20_000_000);
        let mut dec = zstd::stream::read::Decoder::new(f).unwrap();
        let mut ops = Vec::with_capacity(count);
        let mut r = [0u8; 56];
        let kinds = [
            OperationType::Neg,
            OperationType::Register,
            OperationType::AppendToRegister,
            OperationType::BitInvert,
            OperationType::BitStore0,
            OperationType::BitStore1,
            OperationType::X,
            OperationType::Z,
            OperationType::CX,
            OperationType::CZ,
            OperationType::Swap,
            OperationType::R,
            OperationType::Hmr,
            OperationType::CCX,
            OperationType::CCZ,
            OperationType::PushCondition,
            OperationType::PopCondition,
            OperationType::DebugPrint,
        ];
        for _ in 0..count {
            dec.read_exact(&mut r).unwrap();
            let mut o = Op::empty();
            o.kind = kinds[u32::from_le_bytes(r[..4].try_into().unwrap()) as usize];
            let u = |p| u64::from_le_bytes(r[p..p + 8].try_into().unwrap());
            o.q_control2 = QubitId(u(8));
            o.q_control1 = QubitId(u(16));
            o.q_target = QubitId(u(24));
            o.c_target = BitId(u(32));
            o.c_condition = BitId(u(40));
            o.r_target = crate::circuit::RegisterId(u(48));
            o.validate();
            ops.push(o);
        }
        let mut tail = [0u8; 1];
        assert_eq!(dec.read(&mut tail).unwrap(), 0);
        ops
    }

    fn save_stream(path: &str, ops: &[Op]) {
        use std::io::Write;
        let mut file = std::fs::File::create(path).unwrap();
        file.write_all(b"QECCOPSZ").unwrap();
        file.write_all(&(ops.len() as u64).to_le_bytes()).unwrap();
        let mut enc = zstd::stream::write::Encoder::new(file, 3).unwrap();
        for o in ops {
            enc.write_all(&(o.kind as u32).to_le_bytes()).unwrap();
            enc.write_all(&[0u8; 4]).unwrap();
            for v in [
                o.q_control2.0,
                o.q_control1.0,
                o.q_target.0,
                o.c_target.0,
                o.c_condition.0,
                o.r_target.0,
            ] {
                enc.write_all(&v.to_le_bytes()).unwrap();
            }
        }
        enc.finish().unwrap();
    }

    #[test]
    #[ignore = "explicit full-stream research check; requires saved baseline"]
    fn full_stream_equivalence() {
        use crate::circuit::{analyze_ops, QubitOrBit};
        use sha3::digest::XofReader;
        let original = load_stream("research-output/optimization-baseline/ops.bin");
        let cleaned = run(original.clone());
        let (nq, nb, nr, regs) = analyze_ops(original.iter());
        let (cq, cb, cr, cregs) = analyze_ops(cleaned.iter());
        assert_eq!((nq, nb, nr, &regs), (cq, cb, cr, &cregs));
        let mut seed = sha3::Shake256::default();
        seed.update(b"final-cleanup-held-out-inputs-v1");
        let mut inputs = seed.finalize_xof();
        let mut ma = sha3::Shake256::default();
        ma.update(b"final-cleanup-aligned-measurements-v1");
        let mut ra = ma.clone().finalize_xof();
        let mut rb = ma.finalize_xof();
        let mut a = Simulator::new(nq as usize, nb as usize, &mut ra);
        let mut c = Simulator::new(nq as usize, nb as usize, &mut rb);
        for batch in 0..32 {
            a.clear_for_shot();
            c.clear_for_shot();
            for r in &regs {
                for slot in r {
                    let mut v = [0u8; 8];
                    inputs.read(&mut v);
                    let word = u64::from_le_bytes(v);
                    match slot {
                        QubitOrBit::Qubit(q) => {
                            a.qubits[q.0 as usize] = word;
                            c.qubits[q.0 as usize] = word;
                        }
                        QubitOrBit::Bit(b) => {
                            a.bits[b.0 as usize] = word;
                            c.bits[b.0 as usize] = word;
                        }
                    }
                }
            }
            a.apply_iter(original.iter());
            c.apply_iter(cleaned.iter());
            assert_eq!(a.qubits, c.qubits, "all quantum values at batch {batch}");
            assert_eq!(a.bits, c.bits, "all classical values at batch {batch}");
            assert_eq!(a.phase, c.phase, "phase at batch {batch}");
        }
        eprintln!("FULL_STREAM_EQUIVALENCE shots=2048 peak={nq} baseline_T={:.6} candidate_T={:.6} saved_T={:.6}",
            a.stats.toffoli_gates as f64/2048.,c.stats.toffoli_gates as f64/2048.,
            (a.stats.toffoli_gates-c.stats.toffoli_gates) as f64/2048.);
        assert!(c.stats.toffoli_gates <= a.stats.toffoli_gates);
        save_stream("research-output/cleanup-candidate-ops.bin", &cleaned);
    }

    #[test]
    #[ignore = "replay the candidate's canonical packet through both streams"]
    fn canonical_packet_inheritance() {
        use crate::circuit::{analyze_ops, QubitOrBit};
        use alloy_primitives::U256;
        use sha3::digest::XofReader;
        let original = load_stream("research-output/optimization-baseline/ops.bin");
        let candidate = load_stream("research-output/cleanup-v1-ops.bin");
        let (nq, nb, _, regs) = analyze_ops(original.iter());
        let (cq, cb, _, cregs) = analyze_ops(candidate.iter());
        assert_eq!((nq, nb, &regs), (cq, cb, &cregs));
        let hex = |s| U256::from_str_radix(s, 16).unwrap();
        let curve = crate::weierstrass_elliptic_curve::WeierstrassEllipticCurve {
            modulus: hex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F"),
            a: U256::ZERO,
            b: U256::from(7),
            gx: hex("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"),
            gy: hex("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8"),
            order: hex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"),
        };
        let mut h = sha3::Shake256::default();
        h.update(b"quantum_ecc-fiat-shamir-v2");
        h.update(&(candidate.len() as u64).to_le_bytes());
        for o in &candidate {
            h.update(&[o.kind as u8]);
            for v in [
                o.q_control2.0,
                o.q_control1.0,
                o.q_target.0,
                o.c_target.0,
                o.c_condition.0,
                o.r_target.0,
            ] {
                h.update(&v.to_le_bytes());
            }
        }
        let mut xof = h.finalize_xof();
        let mut inputs = Vec::new();
        for _ in 0..9024 {
            let mut a = [0u8; 32];
            let mut b = [0u8; 32];
            xof.read(&mut a);
            xof.read(&mut b);
            let t = curve.mul(curve.gx, curve.gy, U256::from_le_bytes(a));
            let o = curve.mul(curve.gx, curve.gy, U256::from_le_bytes(b));
            if t.0 == o.0 || (t.0.is_zero() && t.1.is_zero()) || (o.0.is_zero() && o.1.is_zero()) {
                continue;
            }
            inputs.push((t, o, curve.add(t.0, t.1, o.0, o.1)));
        }
        assert_eq!(inputs.len(), 9024);
        let mut ra = xof.clone();
        let mut rb = xof;
        let mut a = Simulator::new(nq as usize, nb as usize, &mut ra);
        let mut c = Simulator::new(nq as usize, nb as usize, &mut rb);
        // Reverse checks use separate random words, so they cannot perturb
        // the canonical forward measurement stream used by the scorer.
        let mut inverse_seed = sha3::Shake256::default();
        inverse_seed.update(b"final-cleanup-independent-inverse-v1");
        let mut ira = inverse_seed.clone().finalize_xof();
        let mut irb = inverse_seed.finalize_xof();
        let mut inverse_a = Simulator::new(nq as usize, nb as usize, &mut ira);
        let mut inverse_c = Simulator::new(nq as usize, nb as usize, &mut irb);
        let mut wrong = [0usize; 2];
        let mut phase = [0usize; 2];
        let mut ancilla = [0usize; 2];
        let mut forward_t = [0u64; 2];
        let mut output = vec![false; nq as usize];
        for reg in &regs[..2] {
            for slot in reg {
                if let QubitOrBit::Qubit(q) = slot {
                    output[q.0 as usize] = true;
                }
            }
        }
        for batch in 0..141 {
            a.clear_for_shot();
            c.clear_for_shot();
            for s in 0..64 {
                let (t, o, _) = inputs[batch * 64 + s];
                for sim in [&mut a, &mut c] {
                    sim.set_register(&regs[0], t.0, s);
                    sim.set_register(&regs[1], t.1, s);
                    sim.set_register(&regs[2], o.0, s);
                    sim.set_register(&regs[3], o.1, s);
                }
            }
            let before = [a.stats.toffoli_gates, c.stats.toffoli_gates];
            a.apply_iter(original.iter());
            c.apply_iter(candidate.iter());
            assert_eq!(a.qubits, c.qubits, "forward quantum state at batch {batch}");
            assert_eq!(a.bits, c.bits, "forward classical state at batch {batch}");
            assert_eq!(a.phase, c.phase, "forward phase at batch {batch}");
            for (i, sim) in [&a, &c].into_iter().enumerate() {
                forward_t[i] += sim.stats.toffoli_gates - before[i];
                phase[i] += usize::from(sim.phase != 0);
                ancilla[i] += usize::from(
                    sim.qubits
                        .iter()
                        .enumerate()
                        .any(|(q, v)| !output[q] && *v != 0),
                );
                for s in 0..64 {
                    let (_, _, e) = inputs[batch * 64 + s];
                    wrong[i] += usize::from(
                        sim.get_register(&regs[0], s) != e.0
                            || sim.get_register(&regs[1], s) != e.1,
                    );
                }
            }
            inverse_a.qubits.copy_from_slice(&a.qubits);
            inverse_a.bits.copy_from_slice(&a.bits);
            inverse_a.phase = a.phase;
            inverse_c.qubits.copy_from_slice(&c.qubits);
            inverse_c.bits.copy_from_slice(&c.bits);
            inverse_c.phase = c.phase;
            inverse_a.apply_iter(original.iter().rev());
            inverse_c.apply_iter(candidate.iter().rev());
            assert_eq!(
                inverse_a.qubits, inverse_c.qubits,
                "reverse quantum state at batch {batch}"
            );
            assert_eq!(
                inverse_a.bits, inverse_c.bits,
                "reverse classical state at batch {batch}"
            );
            assert_eq!(
                inverse_a.phase, inverse_c.phase,
                "reverse phase at batch {batch}"
            );
        }
        assert_eq!(wrong[0], wrong[1]);
        assert_eq!(phase[0], phase[1]);
        assert_eq!(ancilla[0], ancilla[1]);
        let delta = (forward_t[0] - forward_t[1]) as f64 / 9024.;
        eprintln!("CANONICAL_INHERITANCE shots=9024 mismatches={wrong:?} phase_batches={phase:?} ancilla_batches={ancilla:?} saved_T={delta:.6}");
        std::fs::write("research-output/canonical-inheritance.json",format!(
            "{{\"shots\":9024,\"classical_mismatches\":{wrong:?},\"phase_batches\":{phase:?},\"ancilla_batches\":{ancilla:?},\"baseline_forward_T\":{},\"candidate_forward_T\":{},\"saved_average_T\":{delta},\"all_forward_reverse_states_equal\":true}}\n",forward_t[0],forward_t[1])).unwrap();
    }
}
