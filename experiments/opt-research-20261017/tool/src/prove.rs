//! Local symbolic prover for redundant Toffolis.
//!
//! For a CCX/CCZ at op index i we build the backward liveness slice of the
//! values it reads (controls, target for CCZ, and its classical condition),
//! cut it where at most `cap` resources are live, treat every live resource at
//! the cut and every measurement outcome inside the slice as a FREE Boolean
//! variable, and evaluate the slice forward on truth tables over those
//! variables. Free variables over-approximate the reachable states, so a
//! property that holds on every row holds on every reachable state: the proof
//! is sound for every input and every measurement outcome.
use quantum_ecc::circuit::{Op, OperationType as K, NO_BIT, NO_QUBIT};
use std::collections::{BTreeMap, HashMap, HashSet};

/// Resource id: qubits are 0..nq, classical bits are nq + bit.
pub type Res = u64;

/// Effective condition of every op: list of (bit, time the bit was read).
pub struct Conds {
    /// For op i: index into `pool` and length.
    span: Vec<(u32, u16)>,
    pool: Vec<(u64, u32)>,
}

impl Conds {
    pub fn build(ops: &[Op]) -> Conds {
        let mut stack: Vec<(u64, u32)> = Vec::new();
        let mut span = Vec::with_capacity(ops.len());
        let mut pool = Vec::new();
        for (i, op) in ops.iter().enumerate() {
            let start = pool.len() as u32;
            pool.extend_from_slice(&stack);
            if op.c_condition != NO_BIT && op.kind != K::PushCondition {
                pool.push((op.c_condition.0, i as u32));
            }
            span.push((start, (pool.len() as u32 - start) as u16));
            match op.kind {
                K::PushCondition => stack.push((op.c_condition.0, i as u32)),
                K::PopCondition => {
                    stack.pop();
                }
                _ => {}
            }
        }
        Conds { span, pool }
    }
    pub fn of(&self, i: usize) -> &[(u64, u32)] {
        let (s, l) = self.span[i];
        &self.pool[s as usize..s as usize + l as usize]
    }
}

/// Per-resource sorted list of writer op indices.
pub struct Writers {
    by_res: HashMap<Res, Vec<u32>>,
}

pub fn writes(op: &Op, nq: u64) -> [Option<Res>; 2] {
    match op.kind {
        K::X | K::CX | K::CCX | K::R => [Some(op.q_target.0), None],
        K::Swap => [Some(op.q_target.0), Some(op.q_control1.0)],
        K::Hmr => [Some(op.q_target.0), Some(nq + op.c_target.0)],
        K::BitInvert | K::BitStore0 | K::BitStore1 => [Some(nq + op.c_target.0), None],
        _ => [None, None],
    }
}

impl Writers {
    pub fn build(ops: &[Op], nq: u64) -> Writers {
        let mut by_res: HashMap<Res, Vec<u32>> = HashMap::new();
        for (i, op) in ops.iter().enumerate() {
            for r in writes(op, nq).into_iter().flatten() {
                by_res.entry(r).or_default().push(i as u32);
            }
        }
        Writers { by_res }
    }
    /// Earliest writer of r strictly after time t.
    pub fn first_after(&self, r: Res, t: u32) -> Option<u32> {
        let v = self.by_res.get(&r)?;
        let k = v.partition_point(|&x| x <= t);
        v.get(k).copied()
    }
    /// Latest writer of r strictly before time t.
    pub fn last_before(&self, r: Res, t: u32) -> Option<u32> {
        let v = self.by_res.get(&r)?;
        let k = v.partition_point(|&x| x < t);
        if k == 0 { None } else { Some(v[k - 1]) }
    }
}

/// Truth table over k variables.
#[derive(Clone)]
pub struct TT(pub Vec<u64>);

impl TT {
    fn zero(w: usize) -> TT { TT(vec![0; w]) }
    fn ones(w: usize) -> TT { TT(vec![u64::MAX; w]) }
    fn var(k: usize, v: usize, w: usize) -> TT {
        let mut t = vec![0u64; w];
        if v < 6 {
            let pat: u64 = match v { 0 => 0xAAAA_AAAA_AAAA_AAAA, 1 => 0xCCCC_CCCC_CCCC_CCCC, 2 => 0xF0F0_F0F0_F0F0_F0F0,
                3 => 0xFF00_FF00_FF00_FF00, 4 => 0xFFFF_0000_FFFF_0000, _ => 0xFFFF_FFFF_0000_0000 };
            for x in t.iter_mut() { *x = pat; }
        } else {
            let period = 1usize << (v - 6);
            for (j, x) in t.iter_mut().enumerate() { if (j / period) & 1 == 1 { *x = u64::MAX; } }
        }
        let _ = k;
        TT(t)
    }
    fn and(&self, o: &TT) -> TT { TT(self.0.iter().zip(&o.0).map(|(a, b)| a & b).collect()) }
    fn xor_assign(&mut self, o: &TT) { for (a, b) in self.0.iter_mut().zip(&o.0) { *a ^= b; } }
    fn andnot_assign(&mut self, o: &TT) { for (a, b) in self.0.iter_mut().zip(&o.0) { *a &= !b; } }
    fn is_zero(&self) -> bool { self.0.iter().all(|&x| x == 0) }
}

pub enum Claim {
    /// cond & c1 & c2 == 0  (CCX never fires: delete)
    CcxNeverFires,
    /// cond & c1 & !c2 == 0  (CCX equals CX from c1)
    CcxEqC1,
    /// cond & c2 & !c1 == 0  (CCX equals CX from c2)
    CcxEqC2,
    /// cond & t & c1 & c2 == 0  (CCZ never fires: delete)
    CczNeverFires,
}

pub struct Outcome {
    pub proven: bool,
    pub vars: usize,
    pub slice_ops: usize,
    pub reason: &'static str,
}

/// Try to prove `claim` for op i. `cap` bounds the free variables (<= 24).
pub fn prove(ops: &[Op], nq: u64, conds: &Conds, wr: &Writers, i: usize, claim: &Claim, cap: usize, max_back: usize) -> Outcome {
    let op = &ops[i];
    // Values needed at time i (read by op i).
    let mut reads: Vec<Res> = vec![op.q_control1.0, op.q_control2.0];
    if op.kind == K::CCZ { reads.push(op.q_target.0); }
    // Backward liveness. `need` maps resource -> true; pending stack-bit reads keyed by time.
    let mut need: HashSet<Res> = reads.iter().copied().collect();
    let mut pending: BTreeMap<u32, Vec<Res>> = BTreeMap::new();
    for &(b, t) in conds.of(i) {
        if t as usize == i { need.insert(nq + b); } else { pending.entry(t).or_default().push(nq + b); }
    }
    let mut slice: Vec<u32> = Vec::new();
    // cut candidates: (time, live count). time = index of first op AFTER the cut.
    let mut best_cut: Option<(usize, usize)> = None;
    let mut j = i;
    let lower = i.saturating_sub(max_back);
    // Walk writers only: next event = max over needed resources of last writer before j, or pending time.
    loop {
        // record cut at current position j (values live at time j, before op j executes... i.e. after op j-1)
        if need.len() + pending.values().map(|v| v.len()).sum::<usize>() <= cap {
            best_cut = Some((j, slice.len()));
        }
        // find next event time < j
        let mut next: Option<u32> = None;
        for &r in &need {
            if let Some(w) = wr.last_before(r, j as u32) { if w as usize >= lower { next = Some(next.map_or(w, |n: u32| n.max(w))); } }
        }
        if let Some((&pt, _)) = pending.range(..j as u32).next_back() {
            // pending read at time pt: the bit value at time pt is needed (before op pt executes).
            if next.map_or(true, |n| pt >= n) {
                // advance to pt: insert the resource (value at time pt, i.e. after writers < pt)
                let rs = pending.remove(&pt).unwrap();
                // A writer at exactly time pt cannot exist for a Push op (it writes nothing).
                for r in rs { need.insert(r); }
                j = pt as usize;
                continue;
            }
        }
        let Some(w) = next else { break };
        let w = w as usize;
        let o = &ops[w];
        let ws = writes(o, nq);
        // op w writes something needed (it is the latest writer of some needed resource)
        slice.push(w as u32);
        // compute reads of op w
        let mut rd: Vec<Res> = Vec::new();
        match o.kind {
            K::X => rd.push(o.q_target.0),
            K::CX => { rd.push(o.q_target.0); rd.push(o.q_control1.0); }
            K::CCX => { rd.push(o.q_target.0); rd.push(o.q_control1.0); rd.push(o.q_control2.0); }
            K::Swap => { rd.push(o.q_target.0); rd.push(o.q_control1.0); }
            K::R => rd.push(o.q_target.0),
            K::Hmr => { rd.push(o.q_target.0); rd.push(nq + o.c_target.0); }
            K::BitInvert | K::BitStore0 | K::BitStore1 => rd.push(nq + o.c_target.0),
            _ => {}
        }
        let cl = conds.of(w);
        let unconditional = cl.is_empty();
        // Unconditional resets do not read their target.
        if unconditional {
            match o.kind {
                K::R => { rd.clear(); }
                K::Hmr => { rd.clear(); }
                K::BitStore0 | K::BitStore1 => { rd.clear(); }
                _ => {}
            }
        }
        for r in ws.into_iter().flatten() { need.remove(&r); }
        for r in rd { need.insert(r); }
        for &(b, t) in cl {
            if t as usize == w { need.insert(nq + b); } else { pending.entry(t).or_default().push(nq + b); }
        }
        j = w;
        if slice.len() > 200_000 || need.len() > 3 * cap + 20 { break; }
    }
    // If the walk ended with nothing needed at all, the earliest point is a perfect cut.
    if need.is_empty() && pending.is_empty() { best_cut = Some((j, slice.len())); }
    let Some((cut, nslice)) = best_cut else { return Outcome { proven: false, vars: 0, slice_ops: slice.len(), reason: "no_cut_within_cap" } };
    // Slice ops after the cut, in forward order.
    let mut fwd: Vec<u32> = slice[..nslice].to_vec();
    fwd.reverse();
    // Count variables: live resources at cut + HMR outcomes in fwd.
    // Recompute live set at cut by replaying the backward pass is complex; instead
    // assign variables lazily: any resource read before being written in fwd (from the cut) is a variable.
    // Variables: resources read before being written in fwd (live at the cut),
    // stack-captured condition bits read before the cut whose bit changes between
    // the read and the cut (separate variables), and HMR outcomes.
    let mut var_of: HashMap<Res, usize> = HashMap::new();
    let mut snap_var: HashMap<(u64, u32), usize> = HashMap::new();
    let mut n_hmr = 0usize;
    {
        let mut written: HashSet<Res> = HashSet::new();
        let mut note = |r: Res, written: &HashSet<Res>, var_of: &mut HashMap<Res, usize>| {
            if !written.contains(&r) && !var_of.contains_key(&r) { let n = var_of.len(); var_of.insert(r, n); }
        };
        let mut cond_note = |idx: usize, written: &HashSet<Res>, var_of: &mut HashMap<Res, usize>, snap_var: &mut HashMap<(u64, u32), usize>| {
            for &(b, t) in conds.of(idx) {
                if (t as usize) < cut {
                    let changed = wr.last_before(nq + b, cut as u32).map_or(false, |x| x >= t);
                    if changed { snap_var.entry((b, t)).or_insert(usize::MAX); continue; }
                }
                if (t as usize) >= cut && written.contains(&(nq + b)) { continue; }
                note(nq + b, written, var_of);
            }
        };
        for &w in &fwd {
            let o = &ops[w as usize];
            cond_note(w as usize, &written, &mut var_of, &mut snap_var);
            let uncond = conds.of(w as usize).is_empty();
            match o.kind {
                K::X => note(o.q_target.0, &written, &mut var_of),
                K::CX => { note(o.q_target.0, &written, &mut var_of); note(o.q_control1.0, &written, &mut var_of); }
                K::CCX => { for r in [o.q_target.0, o.q_control1.0, o.q_control2.0] { note(r, &written, &mut var_of); } }
                K::Swap => { note(o.q_target.0, &written, &mut var_of); note(o.q_control1.0, &written, &mut var_of); }
                K::R | K::Hmr => { if !uncond { note(o.q_target.0, &written, &mut var_of); if o.kind == K::Hmr { note(nq + o.c_target.0, &written, &mut var_of); } } }
                K::BitInvert => note(nq + o.c_target.0, &written, &mut var_of),
                K::BitStore0 | K::BitStore1 => { if !uncond { note(nq + o.c_target.0, &written, &mut var_of); } }
                _ => {}
            }
            if o.kind == K::Hmr { n_hmr += 1; }
            for r in writes(o, nq).into_iter().flatten() { written.insert(r); }
        }
        cond_note(i, &written, &mut var_of, &mut snap_var);
        for r in &reads { note(*r, &written, &mut var_of); }
    }
    let base_vars = var_of.len();
    for (n, v) in snap_var.values_mut().enumerate() { *v = base_vars + n; }
    let nvars = base_vars + snap_var.len() + n_hmr;
    if nvars > 24 { return Outcome { proven: false, vars: nvars, slice_ops: fwd.len(), reason: "too_many_vars" }; }
    let k = nvars.max(6);
    let w = 1usize << (k - 6);
    let mut val: HashMap<Res, TT> = HashMap::new();
    for (&r, &v) in &var_of { val.insert(r, TT::var(k, v, w)); }
    let mut next_fresh = base_vars + snap_var.len();
    let mut snap: HashMap<(u64, u32), TT> = HashMap::new();
    for (&key, &v) in &snap_var { snap.insert(key, TT::var(k, v, w)); }
    let mut snap_times: BTreeMap<u32, Vec<u64>> = BTreeMap::new();
    for &wi in fwd.iter().chain(std::iter::once(&(i as u32))) {
        for &(b, t) in conds.of(wi as usize) { if !snap.contains_key(&(b, t)) { snap_times.entry(t).or_default().push(b); } }
    }
    let get = |val: &HashMap<Res, TT>, r: Res| -> TT { val.get(&r).cloned().unwrap_or_else(|| TT::zero(w)) };
    let take_snaps = |upto: u32, val: &HashMap<Res, TT>, snap: &mut HashMap<(u64, u32), TT>, snap_times: &mut BTreeMap<u32, Vec<u64>>| {
        let keys: Vec<u32> = snap_times.range(..=upto).map(|(k, _)| *k).collect();
        for t in keys {
            for b in snap_times.remove(&t).unwrap() { snap.entry((b, t)).or_insert_with(|| get(val, nq + b)); }
        }
    };
    let cond_of = |idx: usize, snap: &HashMap<(u64, u32), TT>| -> TT {
        let mut c = TT::ones(w);
        for &(b, t) in conds.of(idx) { c = c.and(snap.get(&(b, t)).expect("snapshot")); }
        c
    };
    for &wi in &fwd {
        take_snaps(wi, &val, &mut snap, &mut snap_times);
        let o = &ops[wi as usize];
        let c = cond_of(wi as usize, &snap);
        match o.kind {
            K::X => { let mut t = get(&val, o.q_target.0); t.xor_assign(&c); val.insert(o.q_target.0, t); }
            K::CX => { let f = c.and(&get(&val, o.q_control1.0)); let mut t = get(&val, o.q_target.0); t.xor_assign(&f); val.insert(o.q_target.0, t); }
            K::CCX => { let f = c.and(&get(&val, o.q_control1.0)).and(&get(&val, o.q_control2.0)); let mut t = get(&val, o.q_target.0); t.xor_assign(&f); val.insert(o.q_target.0, t); }
            K::Swap => {
                let a = get(&val, o.q_control1.0); let b = get(&val, o.q_target.0);
                let mut d = a.clone(); d.xor_assign(&b); let d = d.and(&c);
                let mut a2 = a; a2.xor_assign(&d); let mut b2 = b; b2.xor_assign(&d);
                val.insert(o.q_control1.0, a2); val.insert(o.q_target.0, b2);
            }
            K::R => { let mut t = get(&val, o.q_target.0); t.andnot_assign(&c); val.insert(o.q_target.0, t); }
            K::Hmr => {
                let mut t = get(&val, o.q_target.0); t.andnot_assign(&c); val.insert(o.q_target.0, t);
                let fresh = TT::var(k, next_fresh, w); next_fresh += 1;
                let mut b = get(&val, nq + o.c_target.0); b.andnot_assign(&c); b.xor_assign(&fresh.and(&c));
                val.insert(nq + o.c_target.0, b);
            }
            K::BitInvert => { let mut b = get(&val, nq + o.c_target.0); b.xor_assign(&c); val.insert(nq + o.c_target.0, b); }
            K::BitStore0 => { let mut b = get(&val, nq + o.c_target.0); b.andnot_assign(&c); val.insert(nq + o.c_target.0, b); }
            K::BitStore1 => { let mut b = get(&val, nq + o.c_target.0); let mut nb = b.clone(); nb.andnot_assign(&c); b = nb; b.xor_assign(&c); val.insert(nq + o.c_target.0, b); }
            _ => {}
        }
    }
    take_snaps(i as u32, &val, &mut snap, &mut snap_times);
    let c = cond_of(i, &snap);
    let a = get(&val, op.q_control1.0);
    let b = get(&val, op.q_control2.0);
    let bad = match claim {
        Claim::CcxNeverFires => c.and(&a).and(&b),
        Claim::CcxEqC1 => { let mut nb = TT::ones(w); nb.andnot_assign(&b); c.and(&a).and(&nb) }
        Claim::CcxEqC2 => { let mut na = TT::ones(w); na.andnot_assign(&a); c.and(&b).and(&na) }
        Claim::CczNeverFires => c.and(&a).and(&b).and(&get(&val, op.q_target.0)),
    };
    let _ = NO_QUBIT;
    Outcome { proven: bad.is_zero(), vars: nvars, slice_ops: fwd.len(), reason: if bad.is_zero() { "proven" } else { "counterexample_in_free_model" } }
}
