"""Classify replayed census failures. Diagnostic only; score=NONE."""
import json, sys
from collections import Counter
P = 2**256 - 2**32 - 977

def cls(r):
    s = r["seeds"]
    kinds = []
    if r["value"]:
        kinds.append("value-deterministic" if r["value"] == s else "value-seed-dependent")
    if r["phase"]:
        kinds.append("phase-always" if r["phase"] == s else "phase-seed-dependent")
    if r["dirty"]:
        kinds.append("dirty")
    if not kinds:
        kinds.append("not-reproduced")
    return "+".join(kinds)

def shape(r):
    if "got_x" not in r:
        return None
    gx, gy = int(r["got_x"], 16), int(r["got_y"], 16)
    ex, ey = int(r["exp_x"], 16), int(r["exp_y"], 16)
    xs = "x-ok" if gx == ex else "x-bad"
    ys = "y-ok" if gy == ey else "y-bad"
    d = []
    for g, e in ((gx, ex), (gy, ey)):
        if g == e:
            continue
        diff = (g - e) % P
        small = min(diff, P - diff)
        # Integer (non-modular) difference shows truncated-carry style errors.
        raw = abs(g - e)
        d.append({"log2_mod_diff": small.bit_length(), "raw_diff_hex": hex(raw)[:24],
                  "is_pm_p": raw == P, "popcount_xor": bin(g ^ e).count("1"),
                  "xor_span": ((g ^ e).bit_length(), ((g ^ e) & -(g ^ e)).bit_length())})
    return xs + "/" + ys, d

for path in sys.argv[1:]:
    rows = [json.loads(l) for l in open(path)]
    c = Counter(cls(r) for r in rows)
    shapes = Counter(shape(r)[0] for r in rows if shape(r))
    print(f"== {path}: {len(rows)} inputs")
    for k, v in c.most_common():
        print(f"  {k:45s} {v}")
    print("  value shapes:", dict(shapes))
    spans = Counter()
    for r in rows:
        s = shape(r)
        if s:
            for d in s[1]:
                spans[(d["log2_mod_diff"] > 200, d["popcount_xor"] <= 16)] += 1
    print("  (diff>2^200, xor-popcount<=16) counts:", dict(spans))
    ex = [shape(r) for r in rows if shape(r)][:4]
    for e in ex:
        print("   e.g.", e)
