// Evaluator run_tests, copied verbatim from protected src/bin/eval_circuit.rs (via failure-census-20261015).
// ─── Evaluator run_tests, copied verbatim from protected src/bin/eval_circuit.rs (validation control) ───
struct SeedReport {
    ok: bool,
    avg_cliff: f64,
    avg_tof: f64,
    tot_tof: u64,
    tot_cliff: u64,
    n_shots: usize,
    classical_failures: usize,
    phase_garbage_batches: usize,
    ancilla_garbage_batches: usize,
    fail_reason: Option<String>,
}

fn run_tests(
    ops: &[Op],
    layout_regs: &[Vec<QubitOrBit>],
    total_qubits: u64,
    num_bits: u64,
    mut xof: sha3::Shake256Reader,
    target_shots: usize,
) -> SeedReport {
    let curve = secp256k1();

    let mut targets = Vec::with_capacity(target_shots);
    let mut offsets = Vec::with_capacity(target_shots);
    let mut expected = Vec::with_capacity(target_shots);
    for _ in 0..target_shots {
        let mut rb = [[0u8; 32]; 2];
        // Disambiguate from std::io::Read (in scope for the zstd loader).
        XofReader::read(&mut xof, &mut rb[0]);
        XofReader::read(&mut xof, &mut rb[1]);
        let k1 = U256::from_le_bytes(rb[0]);
        let k2 = U256::from_le_bytes(rb[1]);
        let t = curve.mul(curve.gx, curve.gy, k1);
        let o = curve.mul(curve.gx, curve.gy, k2);
        if t.0 == o.0 {
            continue;
        }
        if t.0.is_zero() && t.1.is_zero() {
            continue;
        }
        if o.0.is_zero() && o.1.is_zero() {
            continue;
        }
        let e = curve.add(t.0, t.1, o.0, o.1);
        targets.push(t);
        offsets.push(o);
        expected.push(e);
    }
    let n = targets.len();

    let mut sim = Simulator::new(total_qubits as usize, num_bits as usize, &mut xof);
    let mut ok = true;
    let mut fail_reason: Option<String> = None;
    let mut classical_failures = 0usize;
    let mut phase_garbage_batches = 0usize;
    let mut ancilla_garbage_batches = 0usize;

    const BATCH: usize = 64;
    let num_batches = (n + BATCH - 1) / BATCH;
    for batch in 0..num_batches {
        let bs = BATCH.min(n - batch * BATCH);
        let cond_mask: u64 = if bs == 64 { u64::MAX } else { (1u64 << bs) - 1 };

        sim.clear_for_shot();
        for shot in 0..bs {
            let i = batch * BATCH + shot;
            sim.set_register(&layout_regs[0], targets[i].0, shot);
            sim.set_register(&layout_regs[1], targets[i].1, shot);
            sim.set_register(&layout_regs[2], offsets[i].0, shot);
            sim.set_register(&layout_regs[3], offsets[i].1, shot);
        }

        sim.apply_iter(ops.iter());

        for shot in 0..bs {
            let i = batch * BATCH + shot;
            let gx = sim.get_register(&layout_regs[0], shot);
            let gy = sim.get_register(&layout_regs[1], shot);
            if gx != expected[i].0 || gy != expected[i].1 {
                classical_failures += 1;
                if fail_reason.is_none() {
                    fail_reason = Some(format!(
                        "CLASSICAL MISMATCH shot {i}: got ({:#x},{:#x}) exp ({:#x},{:#x})",
                        gx, gy, expected[i].0, expected[i].1
                    ));
                }
                ok = false;
            }
        }

        let phase = sim.phase & cond_mask;
        if phase != 0 {
            phase_garbage_batches += 1;
            let msg = format!(
                "PHASE GARBAGE: global_phase = {:#018x} across {} live shots (must be 0)",
                phase, bs
            );
            if fail_reason.is_none() {
                fail_reason = Some(msg);
            }
            ok = false;
        }

        for register in layout_regs {
            for qb in register {
                if let QubitOrBit::Qubit(q) = *qb {
                    *sim.qubit_mut(q) = 0;
                }
            }
        }
        let mut garbage_q: Option<u64> = None;
        for q in 0..total_qubits {
            let v = sim.qubit(QubitId(q)) & cond_mask;
            if v != 0 {
                garbage_q = Some(q);
                break;
            }
        }
        if let Some(q) = garbage_q {
            ancilla_garbage_batches += 1;
            let v = sim.qubit(QubitId(q)) & cond_mask;
            let msg = format!(
                "ANCILLA GARBAGE: qubit {} = {:#018x} (live shots) at end of forward; \
                 every non-register qubit must be |0⟩ on every live shot",
                q, v
            );
            if fail_reason.is_none() {
                fail_reason = Some(msg);
            }
            ok = false;
        }
    }

    let _ = num_bits;
    let denom = n.max(1) as f64;
    SeedReport {
        ok,
        avg_cliff: sim.stats.clifford_gates as f64 / denom,
        avg_tof: sim.stats.toffoli_gates as f64 / denom,
        tot_tof: sim.stats.toffoli_gates,
        tot_cliff: sim.stats.clifford_gates,
        n_shots: n,
        classical_failures,
        phase_garbage_batches,
        ancilla_garbage_batches,
        fail_reason,
    }
}
