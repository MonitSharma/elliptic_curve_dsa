"""Independent random packet for margin histograms: rows "i px py ax ay ex ey".
Usage: gen_random.py N OUT EC_HELPER_DIR [START_COUNTER]
Scalars come from SHAKE256("ecdsa-research-margin-random-v1", i); never the evaluator's seed. Diagnostic."""
import hashlib, sys
sys.path.insert(0, sys.argv[3])
from walk_model import ec_mul, ec_add  # guard-sweep-20261015/walk_model.py EC helpers
n, out = int(sys.argv[1]), sys.argv[2]
start = int(sys.argv[4]) if len(sys.argv) > 4 else 0  # independent chunks use disjoint counter ranges
with open(out, "w") as fh:
    i, j = 0, start
    while i < n:
        b = hashlib.shake_256(b"ecdsa-research-margin-random-v1" + j.to_bytes(8, "little")).digest(64); j += 1
        k1, k2 = int.from_bytes(b[:32], "little"), int.from_bytes(b[32:], "little")
        p, a = ec_mul(k1), ec_mul(k2)
        if p is None or a is None or p[0] == a[0]:
            continue  # evaluator's degenerate-pair skips
        e = ec_add(p, a)
        fh.write(f"{i} {p[0]:#x} {p[1]:#x} {a[0]:#x} {a[1]:#x} {e[0]:#x} {e[1]:#x}\n"); i += 1
print(n)
