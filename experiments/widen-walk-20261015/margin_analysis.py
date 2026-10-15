"""Per-tick rail margin from the observer's HIST lines. Diagnostic; score=NONE.

excess = bits the exact value needs - rail width (>= 1 means overflow).
For each (phase, rail, tick) we estimate tail probabilities P(excess >= x) on the
random family, then greedily give single ticks one extra bit where the summed
tail mass drops most, until a target walk-failure budget is met.
Usage: margin_analysis.py TRACE_LOG [budget_per_walk] [toffoli_per_tick_bit]
"""
import gzip
import json
import re
import sys
from collections import defaultdict

path = sys.argv[1]
budget = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-5
cost_bit = float(sys.argv[3]) if len(sys.argv) > 3 else 17.0
opener = gzip.open if path.endswith(".gz") else open
hist = defaultdict(lambda: defaultdict(int))  # (fam, phase, rail, tick) -> excess -> count
for line in opener(path, "rt"):
    m = re.match(r"HIST family=(\S+) rail=(\S) phase=(\S+) tick=(\d+) excess=(-?\d+) count=(\d+)", line)
    if m:
        hist[(m[1], m[3], m[2], int(m[4]))][int(m[5])] += int(m[6])

def tail(h, x):
    n = sum(h.values())
    return sum(c for e, c in h.items() if e >= x) / n if n else 0.0

rand = {k[1:]: v for k, v in hist.items() if k[0] == "random"}
fail = {k[1:]: v for k, v in hist.items() if k[0] == "valuefail186"}
n_rand = max((sum(v.values()) for v in rand.values()), default=0)
print(f"random walks per tick: {n_rand}")

# Observed overflow (excess >= 1) on random inputs, and near-misses.
rows = []
for key, h in sorted(rand.items()):
    rows.append({"phase": key[0], "rail": key[1], "tick": key[2],
                 "p_ge1": tail(h, 1), "p_ge0": tail(h, 0), "p_ge-1": tail(h, -1), "p_ge-2": tail(h, -2),
                 "max_excess": max(h)})
for d in (1, 0, -1, -2, -3):
    tot = sum(tail(h, d) for h in rand.values())
    print(f"sum over ticks/rails of P(excess >= {d:>2}) on random inputs: {tot:.3g}")
tight = sorted(rows, key=lambda r: -r["p_ge-1"])[:15]
print("tightest (phase rail tick: P>=1 P>=0 P>=-1 P>=-2 max):")
for r in tight:
    print(f"  {r['phase']:8s} {r['rail']} {r['tick']:3d}: {r['p_ge1']:.2e} {r['p_ge0']:.2e} {r['p_ge-1']:.2e} {r['p_ge-2']:.2e} {r['max_excess']}")

# Failing inputs: where did the eventual failure walks run closest to their rails?
fx = defaultdict(int)
for key, h in fail.items():
    for e, c in h.items():
        if e >= 0:
            fx[(key[0], key[2] // 10 * 10)] += c
print("failing-family near-overflow (excess>=0) by phase/tick decade:", dict(sorted(fx.items())))

# Greedy per-tick allocation. Tail beyond the observed range is extrapolated by halving per bit,
# conservative compared with the observed per-bit decay of the near-miss tail.
def p_after(h, extra):
    x = 1 + extra
    observed = tail(h, x)
    if observed > 0:
        return observed
    lo = max(e for e in h) if h else 0
    base = tail(h, lo)
    return base * 0.5 ** (x - lo)

alloc = defaultdict(int)
keys = list(rand)
def total():
    return sum(p_after(rand[k], alloc[k[2]]) for k in keys)
t0 = total(); steps = 0
while total() > budget and steps < 2000:
    best, gain = None, 0.0
    for tick in {k[2] for k in keys}:  # the steps table is shared by both legs: buy a bit per tick
        cur = sum(p_after(rand[k], alloc[tick]) for k in keys if k[2] == tick)
        new = sum(p_after(rand[k], alloc[tick] + 1) for k in keys if k[2] == tick)
        if cur - new > gain:
            best, gain = tick, cur - new
    if best is None:
        break
    alloc[best] += 1; steps += 1
print(f"greedy: tail mass {t0:.3g} -> {total():.3g} with {steps} tick-bits, est. +{steps * cost_bit:.0f} T "
      f"(at {cost_bit} T per tick-bit); budget {budget:g}")
out = {"random_walks": n_rand, "rows": rows, "alloc": {str(k): v for k, v in sorted(alloc.items()) if v},
       "tick_bits": steps, "est_toffoli": steps * cost_bit, "budget": budget, "score": None}
json.dump(out, open(path.rsplit("/", 1)[0] + "/margin-analysis.json", "w"), indent=1)
