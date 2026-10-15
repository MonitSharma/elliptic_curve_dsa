"""Classical model of B3's ping-pong GCD walk. Diagnostic only; score=NONE.

Recurrence (agents/toffoli/src/point_add/pingpong.rs module docs):
  u = p, v = odd-lift(d) = d if d odd else d - p
  round r targets v when r is even, u when r is odd; source is the other register
  target <- (target + s) / 2 if bit1(target ^ source) == 0 else (target - s) / 2
Both registers stay odd. Convergence: |u| = |v| = 1 (absorbing).

For each input we report the first round at which the walk has converged and
the largest excess of a register's signed bit-length over PP_WIDTH_SCHEDULE.
Two candidate denominators are modelled: d1 = xA - xP (forward divide) and
d2 = x3 - xA (the uncompute multiply), with the same recurrence.
"""
import json
import random
import sys

P = 2**256 - 2**32 - 977
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

SCHED = "259,258x19,257x5,256x3,255x4,254x4,253x2,252x4,251x3,250x5,249x2,248x4,247x3,246x2,245x4,244x3,243x3,242x3,241x3,240x3,239x4,238x3,237x2,236x4,235x2,234x3,233x2,232x4,231x4,230x2,229x3,228x3,227x3,226x2,225x4,224x2,223x2,222x3,221x3,220x4,219x3,218x2,217x3,216x3,215x3,214x4,213x2,212x2,211x3,210x4,209x3,208x2,207x2,206x2,205x3,204x2,203x4,202x3,201x3,200x4,199x2,198x2,197x3,196x2,195x2,194x4,193x4,192x2,191x3,190x3,189x2,188x3,187x2,186x3,185x2,184x3,183x4,182x2,181x3,180x4,179x2,178x2,177x3,176x3,175,174x2,173x2,172x4,171x3,170x2,169x2,168x4,167x3,166x3,165x2,164x3,163x3,162x2,161x3,160x2,159x3,158x2,157x3,156x2,155x4,154x2,153x3,152x2,151x3,150x3,149x2,148x2,147x2,146x4,145x4,144x3,143x2,142x2,141x3,140x2,139x2,138x2,137x3,136x2,135x4,134x3,133x3,132x3,131x2,130x3,129x2,128x4,127x3,126x2,125x2,124x3,123x2,122x3,121x3,120x2,119x5,118x2,117x3,116x2,115x3,114x4,113x2,112x2,111x4,110x2,109x2,108x2,107x2,106x2,105x5,104x2,103x2,102x2,101x2,100x4,99x2,98x2,97x2,96x3,95x3,94x3,93x2,92x3,91x2,90x4,89x3,88x2,87x2,86x4,85x2,84,83x4,82x2,81x2,80x2,79x3,78x2,77x2,76x3,75,74x2,73x3,72x3,71x2,70x3,69x3,68x3,67x3,66x2,65x3,64x4,63x2,62x2,61x3,60x2,59x2,58x2,57x2,56x2,55x3,54x3,53x2,52x3,51x2,50x4,49x2,48x2,47x3,46x3,45x2,44x2,43x3,42x2,41x2,40x3,39x2,38x2,37x3,36x4,35x2,34x3,33x2,32x2,31x2,30x2,29x2,28x4,27x2,26x2,25x3,24x2,23x2,22x2,21x3,20x3,19x2,18x3,17x2,16x2,15x3,14x2,13x2,12x2,11x2,10x2,9x4,8x9,8x2"


def parse(spec):
    out = []
    for run in spec.split(","):
        w, _, n = run.partition("x")
        out += [int(w)] * int(n or 1)
    return out


W = parse(SCHED)


def ec_add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    (x1, y1), (x2, y2) = a, b
    if x1 == x2:
        if (y1 + y2) % P == 0:
            return None
        lam = 3 * x1 * x1 * pow(2 * y1, -1, P) % P
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    return x3, (lam * (x1 - x3) - y1) % P


def ec_mul(k):
    r, q = None, (GX, GY)
    while k:
        if k & 1:
            r = ec_add(r, q)
        q = ec_add(q, q)
        k >>= 1
    return r


def walk(d, max_rounds=900):
    d %= P
    u, v = P, (d if d & 1 else d - P)
    converged, excess, exc_round = None, -10**9, None
    for r in range(max_rounds):
        if r % 2 == 0:
            t, s = v, u
        else:
            t, s = u, v
        t = (t + s) // 2 if ((t ^ s) >> 1) & 1 == 0 else (t - s) // 2
        if r % 2 == 0:
            v = t
        else:
            u = t
        if r < len(W):
            # signed width needed: magnitude bits + 1 sign bit
            need = max(abs(u).bit_length(), abs(v).bit_length()) + 1
            if need - W[r] > excess:
                excess, exc_round = need - W[r], r
        if converged is None and abs(u) == 1 and abs(v) == 1:
            converged = r
    return converged, excess, exc_round


def features(k1, k2):
    pt, a = ec_mul(k1), ec_mul(k2)
    x3, _ = ec_add(pt, a)
    c1, e1, r1 = walk(a[0] - pt[0])
    c2, e2, r2 = walk(x3 - a[0])
    return {"conv_d1": c1, "exc_d1": e1, "excr_d1": r1, "conv_d2": c2, "exc_d2": e2, "excr_d2": r2}


if __name__ == "__main__":
    fail_path, n_random, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    fails = [tuple(int(x, 16) for x in l.split()) for l in open(fail_path) if l.strip()]
    rng = random.Random(20261015)
    rand = [(rng.getrandbits(256), rng.getrandbits(256)) for _ in range(n_random)]
    rows = []
    for tag, items in (("fail", fails), ("random", rand)):
        for k1, k2 in items:
            f = features(k1, k2)
            f["set"] = tag
            rows.append(f)
    with open(out, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    for tag in ("fail", "random"):
        sel = [r for r in rows if r["set"] == tag]
        for key in ("conv_d1", "conv_d2", "exc_d1", "exc_d2"):
            vals = sorted(x[key] for x in sel if x[key] is not None)
            q = lambda f: vals[min(len(vals) - 1, int(f * len(vals)))]
            print(f"{tag:6s} {key}: n={len(vals)} min={vals[0]} p50={q(.5)} p99={q(.99)} max={vals[-1]}")
