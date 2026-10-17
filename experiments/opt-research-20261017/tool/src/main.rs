mod io;
mod prove;
use alloy_primitives::U256;
use quantum_ecc::circuit::{analyze_ops, Op, OperationType as K, QubitOrBit, NO_BIT};
use quantum_ecc::weierstrass_elliptic_curve::WeierstrassEllipticCurve;
use sha3::{digest::{ExtendableOutput, Update, XofReader}, Shake256};
use std::io::Write;

fn secp() -> WeierstrassEllipticCurve {
    let h = |s: &str| U256::from_str_radix(s, 16).unwrap();
    WeierstrassEllipticCurve {
        modulus: h("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F"),
        a: U256::from(0),
        b: U256::from(7),
        gx: h("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"),
        gy: h("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8"),
        order: h("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"),
    }
}

struct State {
    q: Vec<u64>,
    b: Vec<u64>,
    phase: u64,
}

fn set_reg(s: &mut State, reg: &[QubitOrBit], val: U256, shot: usize) {
    for (i, it) in reg.iter().enumerate() {
        let bit = (val.bit(i) as u64) << shot;
        let w = match it {
            QubitOrBit::Qubit(q) => &mut s.q[q.0 as usize],
            QubitOrBit::Bit(b) => &mut s.b[b.0 as usize],
        };
        *w = (*w & !(1u64 << shot)) | bit;
    }
}

fn get_reg(s: &State, reg: &[QubitOrBit], shot: usize) -> U256 {
    let mut v = U256::ZERO;
    for (i, it) in reg.iter().enumerate() {
        let x = match it {
            QubitOrBit::Qubit(q) => s.q[q.0 as usize],
            QubitOrBit::Bit(b) => s.b[b.0 as usize],
        };
        v.set_bit(i, (x >> shot) & 1 != 0);
    }
    v
}

/// Run one 64-shot batch with fresh random curve inputs; add executed shot
/// counts of CCX/CCZ to `counts`. Returns (failing shot mask, phase word, dirty).
fn run_batch(ops: &[Op], regs: &[Vec<QubitOrBit>], nq: usize, nb: usize, label: &str, batch: u64, counts: &mut [u32]) -> (u64, u64, bool) {
    let curve = secp();
    let mut h = Shake256::default();
    h.update(b"opt-research-profile-v1");
    h.update(&(label.len() as u64).to_le_bytes());
    h.update(label.as_bytes());
    h.update(&batch.to_le_bytes());
    let mut x = h.finalize_xof();
    let mut s = State { q: vec![0; nq], b: vec![0; nb], phase: 0 };
    let mut expected = Vec::new();
    let mut shot = 0;
    while shot < 64 {
        let mut rb = [[0u8; 32]; 2];
        x.read(&mut rb[0]);
        x.read(&mut rb[1]);
        let k1 = U256::from_le_bytes(rb[0]);
        let k2 = U256::from_le_bytes(rb[1]);
        let t = curve.mul(curve.gx, curve.gy, k1);
        let o = curve.mul(curve.gx, curve.gy, k2);
        if t.0 == o.0 || (t.0.is_zero() && t.1.is_zero()) || (o.0.is_zero() && o.1.is_zero()) {
            continue;
        }
        set_reg(&mut s, &regs[0], t.0, shot);
        set_reg(&mut s, &regs[1], t.1, shot);
        set_reg(&mut s, &regs[2], o.0, shot);
        set_reg(&mut s, &regs[3], o.1, shot);
        expected.push(curve.add(t.0, t.1, o.0, o.1));
        shot += 1;
    }
    let mut stack: Vec<u64> = Vec::new();
    let mut base = u64::MAX;
    for (i, op) in ops.iter().enumerate() {
        let mut cond = base;
        if op.c_condition != NO_BIT {
            cond &= s.b[op.c_condition.0 as usize];
        }
        let t = op.q_target.0 as usize;
        let c1 = op.q_control1.0 as usize;
        let c2 = op.q_control2.0 as usize;
        match op.kind {
            K::CCX => {
                counts[4 * i] += cond.count_ones();
                let v = cond & s.q[c1] & s.q[c2];
                counts[4 * i + 1] += v.count_ones();
                counts[4 * i + 2] += (cond & s.q[c1]).count_ones();
                counts[4 * i + 3] += (cond & s.q[c2]).count_ones();
                s.q[t] ^= v;
            }
            K::CCZ => {
                counts[4 * i] += cond.count_ones();
                let v = cond & s.q[t] & s.q[c1] & s.q[c2];
                counts[4 * i + 1] += v.count_ones();
                counts[4 * i + 2] += (cond & s.q[c1] & s.q[c2]).count_ones();
                counts[4 * i + 3] += (cond & s.q[t]).count_ones();
                s.phase ^= v;
            }
            K::CX => {
                let v = cond & s.q[c1];
                s.q[t] ^= v;
            }
            K::Swap => {
                let mut a = s.q[c1];
                let mut b = s.q[t];
                a ^= b;
                b ^= cond & a;
                a ^= b;
                s.q[c1] = a;
                s.q[t] = b;
            }
            K::X => s.q[t] ^= cond,
            K::CZ => s.phase ^= cond & s.q[t] & s.q[c1],
            K::Z => s.phase ^= cond & s.q[t],
            K::Neg => s.phase ^= cond,
            K::Hmr => {
                let mut buf = [0u8; 8];
                x.read(&mut buf);
                let r = u64::from_le_bytes(buf);
                let ct = op.c_target.0 as usize;
                s.b[ct] &= !cond;
                s.b[ct] ^= r & cond;
                s.phase ^= s.q[t] & r & cond;
                s.q[t] &= !cond;
            }
            K::R => {
                let mut buf = [0u8; 8];
                x.read(&mut buf);
                let r = u64::from_le_bytes(buf);
                s.phase ^= s.q[t] & r & cond;
                s.q[t] &= !cond;
            }
            K::BitInvert => s.b[op.c_target.0 as usize] ^= cond,
            K::BitStore0 => s.b[op.c_target.0 as usize] &= !cond,
            K::BitStore1 => s.b[op.c_target.0 as usize] |= cond,
            K::PushCondition => {
                stack.push(base);
                base &= s.b[op.c_condition.0 as usize];
            }
            K::PopCondition => {
                if let Some(v) = stack.pop() {
                    base = v;
                }
            }
            _ => {}
        }
    }
    let mut fail = 0u64;
    for shot in 0..64 {
        let gx = get_reg(&s, &regs[0], shot);
        let gy = get_reg(&s, &regs[1], shot);
        if gx != expected[shot].0 || gy != expected[shot].1 {
            fail |= 1u64 << shot;
        }
    }
    for r in regs {
        for it in r {
            if let QubitOrBit::Qubit(q) = it {
                s.q[q.0 as usize] = 0;
            }
        }
    }
    let dirty = s.q.iter().any(|&v| v != 0);
    (fail, s.phase, dirty)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    match a[1].as_str() {
        // profile OPS LABEL BATCHES THREADS OUT_COUNTS
        "profile" => {
            let ops = io::load_ops(&a[2]);
            let label = a[3].clone();
            let batches: u64 = a[4].parse().unwrap();
            let threads: u64 = a[5].parse().unwrap();
            let (nq, nb, _, regs) = analyze_ops(ops.iter());
            eprintln!("ops={} qubits={} bits={}", ops.len(), nq, nb);
            let results: Vec<(Vec<u32>, u64, u64, u64)> = std::thread::scope(|sc| {
                let hs: Vec<_> = (0..threads)
                    .map(|t| {
                        let (ops, regs, label) = (&ops, &regs, &label);
                        sc.spawn(move || {
                            let mut counts = vec![0u32; 4 * ops.len()];
                            let (mut fails, mut phase, mut dirty) = (0u64, 0u64, 0u64);
                            let mut bidx = t;
                            while bidx < batches {
                                let (f, p, d) = run_batch(ops, regs, nq as usize, nb as usize, label, bidx, &mut counts);
                                if f != 0 || p != 0 { fails += 1; }
                                if p != 0 { phase += 1; }
                                if d { dirty += 1; }
                                bidx += threads;
                            }
                            (counts, fails, phase, dirty)
                        })
                    })
                    .collect();
                hs.into_iter().map(|h| h.join().unwrap()).collect()
            });
            let mut counts = vec![0u64; 4 * ops.len()];
            let (mut fails, mut phase, mut dirty) = (0, 0, 0);
            for (c, f, p, d) in &results {
                for (i, v) in c.iter().enumerate() {
                    counts[i] += *v as u64;
                }
                fails += f;
                phase += p;
                dirty += d;
            }
            let shots = (batches * 64) as f64;
            let total: u64 = counts.iter().step_by(4).sum();
            println!("shots={} mean_T={:.4} failed_batches={} phase_batches={} dirty_batches={}", shots, total as f64 / shots, fails, phase, dirty);
            let mut f = std::io::BufWriter::new(std::fs::File::create(&a[6]).unwrap());
            for c in &counts {
                f.write_all(&(*c as u32).to_le_bytes()).unwrap();
            }
        }
        // analyze OPS STATS SHOTS: classify Toffoli cost by empirical firing pattern
        "analyze" => {
            let ops = io::load_ops(&a[2]);
            let raw = std::fs::read(&a[3]).unwrap();
            let shots: f64 = a[4].parse().unwrap();
            let st = |i: usize, k: usize| u32::from_le_bytes(raw[16 * i + 4 * k..16 * i + 4 * k + 4].try_into().unwrap()) as u64;
            let mut cat = std::collections::BTreeMap::<&str, (u64, f64)>::new();
            let mut add = |name: &'static str, e: u64| {
                let x = cat.entry(name).or_insert((0, 0.0));
                x.0 += 1;
                x.1 += e as f64 / shots;
            };
            let buckets = 50usize;
            let mut region = vec![0f64; buckets];
            for (i, op) in ops.iter().enumerate() {
                let (e, f, c1, c2) = (st(i, 0), st(i, 1), st(i, 2), st(i, 3));
                match op.kind {
                    K::CCX => {
                        region[i * buckets / ops.len()] += e as f64 / shots;
                        if e == 0 { add("ccx_never_executed", e); }
                        else if f == 0 && (c1 == 0 || c2 == 0) { add("ccx_nofire_dead_control", e); }
                        else if f == 0 && (c1 as f64) > 0.01 * e as f64 && (c2 as f64) > 0.01 * e as f64 { add("ccx_nofire_exclusive_frequent", e); }
                        else if f == 0 { add("ccx_nofire_exclusive_rare", e); }
                        else if f == c1 && f == c2 { add("ccx_and_eq_c1_eq_c2", e); }
                        else if f == c1 { add("ccx_and_eq_c1", e); }
                        else if f == c2 { add("ccx_and_eq_c2", e); }
                        else if (f as f64) < 1e-3 * e as f64 { add("ccx_rare_fire_lt1e-3", e); }
                        else { add("ccx_other", e); }
                    }
                    K::CCZ => {
                        region[i * buckets / ops.len()] += e as f64 / shots;
                        if e == 0 { add("ccz_never_executed", e); }
                        else if f == 0 { add("ccz_executed_never_fires", e); }
                        else if f == c1 { add("ccz_t_always1_given_c1c2", e); }
                        else if f == c2 { add("ccz_c1c2_always1_given_t", e); }
                        else if (f as f64) < 1e-3 * e as f64 { add("ccz_rare_fire_lt1e-3", e); }
                        else { add("ccz_other", e); }
                    }
                    _ => {}
                }
            }
            let mut total = 0.0;
            for (k, (n, t)) in &cat {
                println!("{k:32} sites={n:9} T={t:12.3}");
                total += t;
            }
            println!("total_T={total:.3}");
            for (b, t) in region.iter().enumerate() {
                println!("region {b:2} ops {:9}..{:9} T={t:10.1}", b * ops.len() / buckets, (b + 1) * ops.len() / buckets);
            }
        }
        // prove OPS STATS SHOTS CAP THREADS OUT_TSV
        "prove" => {
            let ops = io::load_ops(&a[2]);
            let raw = std::fs::read(&a[3]).unwrap();
            let shots: f64 = a[4].parse().unwrap();
            let cap: usize = a[5].parse().unwrap();
            let threads: usize = a[6].parse().unwrap();
            let st = |i: usize, k: usize| u32::from_le_bytes(raw[16 * i + 4 * k..16 * i + 4 * k + 4].try_into().unwrap()) as u64;
            let (nq, _, _, _) = analyze_ops(ops.iter());
            let conds = prove::Conds::build(&ops);
            let wr = prove::Writers::build(&ops, nq);
            let mut cands: Vec<(usize, u8, f64)> = Vec::new();
            for (i, op) in ops.iter().enumerate() {
                let (e, f, c1, c2) = (st(i, 0), st(i, 1), st(i, 2), st(i, 3));
                if e == 0 { continue; }
                match op.kind {
                    K::CCX if f == 0 => cands.push((i, 0, e as f64 / shots)),
                    K::CCX if f == c1 => cands.push((i, 1, e as f64 / shots)),
                    K::CCX if f == c2 => cands.push((i, 2, e as f64 / shots)),
                    K::CCZ if f == 0 => cands.push((i, 3, e as f64 / shots)),
                    _ => {}
                }
            }
            eprintln!("candidates={}", cands.len());
            let next = std::sync::atomic::AtomicUsize::new(0);
            let rows: Vec<Vec<String>> = std::thread::scope(|sc| {
                let hs: Vec<_> = (0..threads).map(|_| {
                    let (ops, conds, wr, cands, next) = (&ops, &conds, &wr, &cands, &next);
                    sc.spawn(move || {
                        let mut out = Vec::new();
                        loop {
                            let k = next.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                            if k >= cands.len() { break; }
                            let (i, c, t) = cands[k];
                            let claim = match c { 0 => prove::Claim::CcxNeverFires, 1 => prove::Claim::CcxEqC1, 2 => prove::Claim::CcxEqC2, _ => prove::Claim::CczNeverFires };
                            let o = prove::prove(ops, nq, conds, wr, i, &claim, cap, 2_000_000);
                            out.push(format!("{i}\t{c}\t{}\t{}\t{}\t{}\t{t:.6}", o.proven as u8, o.vars, o.slice_ops, o.reason));
                        }
                        out
                    })
                }).collect();
                hs.into_iter().map(|h| h.join().unwrap()).collect()
            });
            let mut all: Vec<String> = rows.into_iter().flatten().collect();
            all.sort_by_key(|r| r.split('\t').next().unwrap().parse::<usize>().unwrap());
            let mut saved = [0f64; 4];
            let mut n = [0usize; 4];
            for r in &all {
                let f: Vec<&str> = r.split('\t').collect();
                if f[2] == "1" { let c: usize = f[1].parse().unwrap(); saved[c] += f[6].parse::<f64>().unwrap(); n[c] += 1; }
            }
            println!("proven never-fire CCX: {} sites, {:.3} T", n[0], saved[0]);
            println!("proven CCX==CX(c1): {} sites, {:.3} T", n[1], saved[1]);
            println!("proven CCX==CX(c2): {} sites, {:.3} T", n[2], saved[2]);
            println!("proven never-fire CCZ: {} sites, {:.3} T", n[3], saved[3]);
            std::fs::write(&a[7], all.join("\n") + "\n").unwrap();
        }
        // show OPS STATS SHOTS INDEX DEPTH: print op INDEX and the latest writers of its operands, recursively
        "show" => {
            let ops = io::load_ops(&a[2]);
            let raw = std::fs::read(&a[3]).unwrap();
            let shots: f64 = a[4].parse().unwrap();
            let idx: usize = a[5].parse().unwrap();
            let depth: usize = a[6].parse().unwrap();
            let st = |i: usize, k: usize| u32::from_le_bytes(raw[16 * i + 4 * k..16 * i + 4 * k + 4].try_into().unwrap()) as u64;
            let (nq, _, _, _) = analyze_ops(ops.iter());
            let conds = prove::Conds::build(&ops);
            let wr = prove::Writers::build(&ops, nq);
            let fmt = |i: usize| {
                let o = &ops[i];
                let q = |x: u64| if x == u64::MAX { "-".to_string() } else { format!("q{x}") };
                let b = |x: u64| if x == u64::MAX { "-".to_string() } else { format!("b{x}") };
                let c: Vec<String> = conds.of(i).iter().map(|(bb, t)| format!("b{bb}@{t}")).collect();
                format!("{i:9} {:?} t={} c1={} c2={} ct={} cond=[{}] exec={:.4} fire={:.4} s2={:.4} s3={:.4}", o.kind, q(o.q_target.0), q(o.q_control1.0), q(o.q_control2.0), b(o.c_target.0), c.join(","),
                    st(i, 0) as f64 / shots, st(i, 1) as f64 / shots, st(i, 2) as f64 / shots, st(i, 3) as f64 / shots)
            };
            let mut frontier = vec![(idx, 0usize)];
            let mut seen = std::collections::HashSet::new();
            while let Some((i, d)) = frontier.pop() {
                if !seen.insert(i) { continue; }
                println!("{}{}", "  ".repeat(d), fmt(i));
                if d >= depth { continue; }
                let o = &ops[i];
                let mut rd = vec![];
                for x in [o.q_control1.0, o.q_control2.0, o.q_target.0] { if x != u64::MAX { rd.push(x); } }
                for (bb, _) in conds.of(i) { rd.push(nq + bb); }
                for r in rd { if let Some(w) = wr.last_before(r, i as u32) { frontier.push((w as usize, d + 1)); } }
            }
        }
        // list OPS STATS SHOTS: print exclusive-frequent never-firing CCX sites
        "list" => {
            let ops = io::load_ops(&a[2]);
            let raw = std::fs::read(&a[3]).unwrap();
            let shots: f64 = a[4].parse().unwrap();
            let st = |i: usize, k: usize| u32::from_le_bytes(raw[16 * i + 4 * k..16 * i + 4 * k + 4].try_into().unwrap()) as u64;
            for (i, op) in ops.iter().enumerate() {
                let (e, f, c1, c2) = (st(i, 0), st(i, 1), st(i, 2), st(i, 3));
                if op.kind == K::CCX && e > 0 && f == 0 && (c1 as f64) > 0.01 * e as f64 && (c2 as f64) > 0.01 * e as f64 {
                    println!("{i}	{:.4}	{:.4}	{:.4}	q{}	q{}	q{}", e as f64 / shots, c1 as f64 / e as f64, c2 as f64 / e as f64, op.q_control1.0, op.q_control2.0, op.q_target.0);
                }
            }
        }
        // liveness OPS: max simultaneous live qubits, where a qubit is dead between an
        // unconditional R/HMR and its next reference (and before its first reference).
        "liveness" => {
            let ops = io::load_ops(&a[2]);
            let (nq, _, _, regs) = analyze_ops(ops.iter());
            let nq = nq as usize;
            let mut is_reg = vec![false; nq];
            for r in &regs { for it in r { if let QubitOrBit::Qubit(q) = it { is_reg[q.0 as usize] = true; } } }
            // depth of condition stack per op
            let mut depth = 0usize;
            let mut delta = vec![0i32; ops.len() + 2];
            let mut open: Vec<Option<usize>> = vec![None; nq]; // start of current live interval
            let mut last: Vec<usize> = vec![0; nq];
            let mut intervals = 0usize;
            let close = |q: usize, open: &mut Vec<Option<usize>>, last: &Vec<usize>, delta: &mut Vec<i32>, intervals: &mut usize| {
                if let Some(s) = open[q] { delta[s] += 1; delta[last[q] + 1] -= 1; open[q] = None; *intervals += 1; }
            };
            for (i, op) in ops.iter().enumerate() {
                match op.kind { K::PushCondition => depth += 1, K::PopCondition => depth = depth.saturating_sub(1), _ => {} }
                let uncond_reset = matches!(op.kind, K::R | K::Hmr) && depth == 0 && op.c_condition == NO_BIT;
                for q in [op.q_target.0, op.q_control1.0, op.q_control2.0] {
                    if q == u64::MAX { continue; }
                    let q = q as usize;
                    if open[q].is_none() { open[q] = Some(i); }
                    last[q] = i;
                }
                if uncond_reset { close(op.q_target.0 as usize, &mut open, &last, &mut delta, &mut intervals); }
            }
            for q in 0..nq { close(q, &mut open, &last, &mut delta, &mut intervals); }
            let mut cur = 0i64; let mut best = 0i64; let mut at = 0usize; let mut hist = std::collections::BTreeMap::<i64, usize>::new();
            for i in 0..ops.len() { cur += delta[i] as i64; if cur > best { best = cur; at = i; } *hist.entry(cur).or_default() += 1; }
            println!("qubit_ids={} intervals={} max_live={} first_at_op={}", nq, intervals, best, at);
            for (k, v) in hist.iter().rev().take(6) { println!("  live={k} ops={v}"); }
            let _ = is_reg;
        }
        // pairs OPS STATS SHOTS: CCX(a,b->t) ... CCX(a,b->t) with a,b,t not written in between
        "pairs" => {
            let ops = io::load_ops(&a[2]);
            let raw = std::fs::read(&a[3]).unwrap();
            let shots: f64 = a[4].parse().unwrap();
            let st = |i: usize, k: usize| u32::from_le_bytes(raw[16 * i + 4 * k..16 * i + 4 * k + 4].try_into().unwrap()) as u64;
            let (nq, _, _, _) = analyze_ops(ops.iter());
            let conds = prove::Conds::build(&ops);
            let wr = prove::Writers::build(&ops, nq);
            let mut n = [0usize; 4];
            let mut t_saved = [0f64; 4];
            for (i, op) in ops.iter().enumerate() {
                if op.kind != K::CCX { continue; }
                let t = op.q_target.0;
                // next writer of t after i
                let nxt = |r: u64| -> Option<u32> { wr.last_before(r, u32::MAX).and_then(|_| None) };
                let _ = nxt;
                let after = |r: u64| -> Option<usize> {
                    // first writer strictly after i
                    let mut lo = i as u32 + 1;
                    let _ = &mut lo;
                    let w = wr.first_after(r, i as u32)?;
                    Some(w as usize)
                };
                let Some(j) = after(t) else { continue };
                let o = &ops[j];
                if o.kind != K::CCX { continue; }
                let same = (o.q_control1 == op.q_control1 && o.q_control2 == op.q_control2) || (o.q_control1 == op.q_control2 && o.q_control2 == op.q_control1);
                if !same { continue; }
                let clean_a = after(op.q_control1.0).map_or(true, |w| w > j) ;
                let clean_b = after(op.q_control2.0).map_or(true, |w| w > j);
                let same_cond = conds.of(i).iter().map(|x| x.0).collect::<Vec<_>>() == conds.of(j).iter().map(|x| x.0).collect::<Vec<_>>();
                let k = (clean_a && clean_b) as usize * 2 + same_cond as usize;
                n[k] += 1;
                t_saved[k] += st(j, 0) as f64 / shots;
                if k == 2 && n[k] % 400 == 1 {
                    let fc = |x: usize| conds.of(x).iter().map(|(b, t)| format!("b{b}@{t}")).collect::<Vec<_>>().join(",");
                    println!("EX i={i} j={j} gap={} t=q{} a=q{} b=q{} cond_i=[{}] cond_j=[{}] exec_i={:.4} exec_j={:.4} fire_i={:.4} fire_j={:.4}", j - i, t, op.q_control1.0, op.q_control2.0, fc(i), fc(j), st(i,0) as f64/shots, st(j,0) as f64/shots, st(i,1) as f64/shots, st(j,1) as f64/shots);
                    // ops between i and j touching t
                    let mut shown = 0;
                    for x in i + 1..j { let o = &ops[x]; if o.q_control1.0 == t || o.q_control2.0 == t { if shown < 6 { println!("    read at {x}: {:?} t=q{} c1=q{} c2=q{} cond=[{}]", o.kind, o.q_target.0, o.q_control1.0, o.q_control2.0, fc(x)); } shown += 1; } }
                    if let Some(w) = wr.first_after(t, j as u32) { let o = &ops[w as usize]; println!("    next write of t at {w}: {:?} cond=[{}] ct=b{}", o.kind, fc(w as usize), o.c_target.0); }
                    if let Some(w) = wr.last_before(t, i as u32) { let o = &ops[w as usize]; println!("    prev write of t at {w}: {:?} cond=[{}]", o.kind, fc(w as usize)); }
                }
            }
            for k in 0..4 { println!("pairs controls_unchanged={} same_cond={} : {} pairs, second-gate T={:.3}", k / 2, k % 2, n[k], t_saved[k]); }
        }
        _ => panic!("unknown command"),
    }
}
