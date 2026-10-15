"""Summarize first-divergence events from the value-failure observer. Diagnostic; score=NONE.

Fixed after the independent audit (trace-audit-20261015): zero is not a power of two,
and only the value-failure family is read, so families never merge.
"""
import json
import re
import sys
from collections import Counter, defaultdict

P = 2**256 - 2**32 - 977
ev = defaultdict(list)
for line in open(sys.argv[1]):
    m = re.match(r"\s*EVENT family=(\S+) shot=(\d+) at=(\d+) (\S+) (.*)", line)
    if m and m[1] == "valuefail186":
        ev[int(m[2])].append((int(m[3]), m[4], m[5]))
shots = range(int(sys.argv[2]))
first = {}
for s in shots:
    e = sorted(ev.get(s, []))
    first[s] = e[0] if e else None


def kv(rest):
    return dict(re.findall(r"(\w+)=(\[[^\]]*\]|\S+)", rest))


out = {"shots": len(first), "first_kind": Counter(), "fwd": []}
for s, e in first.items():
    if e is None:
        out["first_kind"]["NONE (no walk-rail event)"] += 1
        continue
    kind = e[1]
    d = kv(e[2])
    out["first_kind"][f"{kind} {d.get('phase')}"] += 1
    if kind == "FWD_RAIL":
        widths = json.loads(d["widths"])
        diff = int(d["diff_t"], 16)
        mag = min(diff, P - diff)
        pow2 = mag != 0 and mag & (mag - 1) == 0
        w_t = widths[int(d["tick"]) % 2]
        out["fwd"].append({"shot": s, "phase": d["phase"], "tick": int(d["tick"]), "corrupt": d["corrupt"],
                           "widths": widths, "tape": d["tape"], "diff_log2": mag.bit_length() - 1, "target_delta_zero": mag == 0,
                           "diff_is_pow2": pow2, "diff_eq_2^w": pow2 and mag.bit_length() - 1 == w_t,
                           "diff_eq_2^(w-1)": pow2 and mag.bit_length() - 1 == w_t - 1})
f = out["fwd"]
print("first divergence:", dict(out["first_kind"]))
print("forward rail first events:", len(f))
print(" corrupt:", Counter(x["corrupt"] for x in f), " zero target delta:", sum(x["target_delta_zero"] for x in f))
print(" diff is +-power of two:", sum(x["diff_is_pow2"] for x in f),
      " = 2^width:", sum(x["diff_eq_2^w"] for x in f), " = 2^(width-1):", sum(x["diff_eq_2^(w-1)"] for x in f))
for ph in ("divide", "multiply"):
    ticks = Counter((x["tick"] // 10) * 10 for x in f if x["phase"] == ph)
    print(f" {ph} tick deciles:", dict(sorted(ticks.items())))
print(" top (phase,tick):", Counter((x["phase"], x["tick"]) for x in f).most_common(12))
json.dump({k: (dict(v) if isinstance(v, Counter) else v) for k, v in out.items()},
          open(sys.argv[3], "w"), indent=1)
