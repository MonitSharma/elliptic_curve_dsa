"""Summarize failure-census JSONL files. Diagnostic only: no score, no packet choice.

Estimates per-shot value/phase/ancilla failure rates, the per-batch failure
rate seen by the evaluator (any failure in a 64-shot batch fails it), and the
probability that the unchanged stream passes a fresh 9,024-shot (141-batch)
Fiat-Shamir packet. Intervals are exact Clopper-Pearson (95%).
"""
import json
import math
import sys
from pathlib import Path

BATCHES_PER_PACKET = 9024 // 64  # 141


def beta_ppf(q, a, b):
    """Inverse regularized incomplete beta via bisection (stdlib only)."""
    def ibeta(x):
        # Continued fraction (Numerical Recipes betacf), adequate for these sizes.
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
        lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        front = math.exp(lbeta + a * math.log(x) + b * math.log1p(-x))
        if x > (a + 1) / (a + b + 2):
            return 1.0 - ibeta_swap(1 - x)
        return front * cf(x, a, b) / a

    def ibeta_swap(x):
        lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        front = math.exp(lbeta + b * math.log(x) + a * math.log1p(-x))
        return front * cf(x, b, a) / b

    def cf(x, a_, b_):
        tiny = 1e-300
        c, d = 1.0, 1.0 - (a_ + b_) * x / (a_ + 1)
        d = 1.0 / (d if abs(d) > tiny else tiny)
        h = d
        for m in range(1, 400):
            m2 = 2 * m
            aa = m * (b_ - m) * x / ((a_ + m2 - 1) * (a_ + m2))
            d = 1 + aa * d
            d = 1 / (d if abs(d) > tiny else tiny)
            c = 1 + aa / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
            aa = -(a_ + m) * (a_ + b_ + m) * x / ((a_ + m2) * (a_ + m2 + 1))
            d = 1 + aa * d
            d = 1 / (d if abs(d) > tiny else tiny)
            c = 1 + aa / c
            c = c if abs(c) > tiny else tiny
            delta = d * c
            h *= delta
            if abs(delta - 1) < 1e-14:
                break
        return h

    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if ibeta(mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cp(k, n):
    lo = 0.0 if k == 0 else beta_ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta_ppf(0.975, k + 1, n - k)
    return lo, hi


def summarize(path):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    batches = len(rows)
    shots = sum(r["shots"] for r in rows)
    value = sum(r["value_shots"] for r in rows)
    phase = sum(r["phase_shots"] for r in rows)
    dirty = sum(r["dirty_shots"] for r in rows)
    any_shot = sum(len(r["failures"]) for r in rows)
    bad_batches = sum(1 for r in rows if r["failures"])
    phase_batches = sum(1 for r in rows if r["phase_shots"])
    tof = [r["toffoli"] / r["shots"] for r in rows]
    mean_t = sum(r["toffoli"] for r in rows) / shots
    sd_batch = math.sqrt(sum((t - mean_t) ** 2 for t in tof) / max(1, batches - 1))
    f = bad_batches / batches
    f_lo, f_hi = cp(bad_batches, batches)
    out = {
        "file": Path(path).name, "batches": batches, "shots": shots,
        "value_shots": value, "phase_shots": phase, "dirty_shots": dirty,
        "any_failure_shots": any_shot, "failed_batches": bad_batches,
        "phase_batches": phase_batches,
        "value_rate": value / shots, "value_rate_ci95": cp(value, shots),
        "phase_shot_rate": phase / shots, "phase_shot_rate_ci95": cp(phase, shots),
        "batch_failure_rate": f, "batch_failure_rate_ci95": (f_lo, f_hi),
        "expected_failed_batches_per_packet": f * BATCHES_PER_PACKET,
        "p_pass_fresh_packet": (1 - f) ** BATCHES_PER_PACKET,
        "p_pass_fresh_packet_ci95": ((1 - f_hi) ** BATCHES_PER_PACKET, (1 - f_lo) ** BATCHES_PER_PACKET),
        "diagnostic_mean_executed_toffoli": mean_t,
        "diagnostic_mean_toffoli_se": sd_batch / math.sqrt(batches) / 1.0,
        "score": None,
    }
    return out


if __name__ == "__main__":
    res = [summarize(p) for p in sys.argv[1:]]
    print(json.dumps(res, indent=2))
