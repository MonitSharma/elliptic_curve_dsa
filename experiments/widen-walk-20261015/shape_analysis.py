"""Slow-walk shape analysis from WALKBINS lines (value_trace_margin.rs). Diagnostic; score=NONE.

For every random walk leg (divide or multiply) we have the max rail excess per
10-tick bin (excess >= 1 is an overflow at the variant's own widths). A walk leg
survives an envelope that adds delta[b] bits to bin b iff excess[b] <= delta[b]
for every bin. We report per-bin tails, the per-walk "lag shape", the survival of
candidate envelopes, and a greedy allocation under a Toffoli budget.

Caveat: widening also moves the YP8 anchors, which changes later choices; this
analysis treats trajectories as fixed, so every design must be gated by a census.
Usage: shape_analysis.py OUT.json LOG.gz [LOG.gz ...]
"""
import gzip
import json
import math
import os
import re
import sys
from collections import Counter

out_path, logs = sys.argv[1], sys.argv[2:]
NB = 15
legs = []          # (bins list) for random family legs that had no earlier event
bad_legs = []      # legs of random inputs whose final point was wrong
fail_family = []   # legs of the variant's own census failures
for path in logs:
    for line in gzip.open(path, "rt"):
        m = re.match(r"WALKBINS family=(\S+) shot=(\d+) phase=(\S+) bad=(\S+) bins=(\S+)", line)
        if not m:
            continue
        b = [int(x) for x in m[5].split(",")]
        if m[1] == "random":
            (bad_legs if m[4] == "true" else legs).append(b)
        elif m[1] == "valuefail186":
            fail_family.append(b)

n = len(legs) + len(bad_legs)
print(f"random walk legs: {n} ({len(bad_legs)} on wrong final points); failure-family legs: {len(fail_family)}")

def tail(rows, b, x):
    vals = [r[b] for r in rows if r[b] > -999]
    return sum(v >= x for v in vals) / max(1, len(vals)), len(vals)

all_rand = legs + bad_legs
print("bin  ticks    P(ex>=1)   P(ex>=0)   P(ex>=-1)  P(ex>=-2)  fail-family P(ex>=1)")
for b in range(NB):
    r = [tail(all_rand, b, x)[0] for x in (1, 0, -1, -2)]
    f = tail(fail_family, b, 1)[0]
    print(f"{b:3d}  {b*10:3d}-{b*10+9:<3d}  " + "  ".join(f"{v:9.2e}" for v in r) + f"   {f:9.2e}")

def survive(rows, delta):
    return sum(all(v <= d for v, d in zip(r, delta) if v > -999) for r in rows) / max(1, len(rows))

# Tail decay of the walk-level slack: P(max_b excess_b >= x) for a uniform delta.
print("walk-level P(max excess >= x) on random legs:")
for x in range(-6, 3):
    p = sum(max(v for v in r if v > -999) >= x for r in all_rand) / len(all_rand)
    print(f"  x={x:>2}: {p:.3e}")

# Per-bit decay estimated from the walk-level tail between x = -3 and x = 0.
p_at = {x: sum(max(v for v in r if v > -999) >= x for r in all_rand) / len(all_rand) for x in range(-6, 3)}
decay = (p_at[0] / p_at[-3]) ** (1 / 3) if p_at[-3] > 0 and p_at[0] > 0 else float("nan")
print(f"estimated tail decay per extra bit (from x=-3..0): {decay:.3f}")

COST_TICK_BIT = 17.4  # measured: +2 bits on 135 ticks cost ~4.7K T
designs = {
    "uniform+0": [0] * NB,
    "uniform+2": [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0],
    "ramp 0->4": [0] + [round(4 * b / 13) for b in range(1, 14)] + [0],
    "late+3 (ticks>=70)": [0] * 7 + [3] * 7 + [0],
    "late+4 (ticks>=90)": [0] * 9 + [4] * 5 + [0],
}
res = {}
print("design survival on random legs (fail rate per leg) and Toffoli cost:")
for name, d in designs.items():
    f = 1 - survive(all_rand, d)
    cost = sum(d[b] * 10 for b in range(NB)) * COST_TICK_BIT
    res[name] = {"delta": d, "fail_per_leg": f, "cost_T": cost}
    print(f"  {name:22s} fail/leg {f:.2e}  cost +{cost:,.0f} T")

# Greedy: add one bit to the bin with the best (fail reduction)/(cost), to a cost budget.
budget = float(os.environ.get("BUDGET", 7000))
delta = [0] * NB
steps = []
while True:
    base = 1 - survive(all_rand, delta)
    best = None
    for b in range(1, NB - 1):
        trial = delta.copy(); trial[b] += 1
        gain = base - (1 - survive(all_rand, trial))
        cost = 10 * COST_TICK_BIT
        if gain > 0 and (best is None or gain / cost > best[0]):
            best = (gain / cost, b)
    spent = sum(delta[b] * 10 for b in range(NB)) * COST_TICK_BIT
    if best is None or spent + 10 * COST_TICK_BIT > budget:
        break
    delta[best[1]] += 1
    steps.append((best[1], 1 - survive(all_rand, delta)))
print(f"greedy within {budget:.0f} T: delta={delta} fail/leg {1 - survive(all_rand, delta):.2e} "
      f"(observed; resolution 1/{len(all_rand)})")
json.dump({"legs": n, "bad_legs": len(bad_legs), "fail_family_legs": len(fail_family), "p_walk_tail": p_at,
           "decay_per_bit": decay, "designs": res, "greedy_delta": delta, "greedy_steps": steps, "score": None},
          open(out_path, "w"), indent=1)
