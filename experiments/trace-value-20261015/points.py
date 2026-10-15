"""Convert census value failures (k1 k2) to observer packet rows "i px py ax ay ex ey". Diagnostic."""
import json, sys
sys.path.insert(0, sys.argv[3])
from walk_model import ec_mul, ec_add  # guard-sweep-20261015/walk_model.py (EC helpers only)
rows = []
for line in open(sys.argv[1]):
    r = json.loads(line)
    for f in r["failures"]:
        if f["value"]:
            rows.append((int(f["k1"], 16), int(f["k2"], 16)))
with open(sys.argv[2], "w") as out:
    for i, (k1, k2) in enumerate(rows):
        p, a = ec_mul(k1), ec_mul(k2)
        e = ec_add(p, a)
        out.write(f"{i} {p[0]:#x} {p[1]:#x} {a[0]:#x} {a[1]:#x} {e[0]:#x} {e[1]:#x}\n")
print(len(rows))
