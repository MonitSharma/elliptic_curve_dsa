"""Exact all-input model of the forward fold's 31-AND value constructor.

Research diagnostics only: no sampled-domain restrictions or scored claims.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("foldcore", ROOT / "scripts/analyze-fold-core.py")
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)
SOURCE = ROOT / "agents/product/src/point_add/y15_onefold.rs"
N = 1 << 14
ONE = (1 << N) - 1

class Model:
    def __init__(self):
        self.names = ["1"] + [f"raw{i}" for i in range(14)]
        self.vals = [ONE] + [sum(((r >> i) & 1) << r for r in range(N)) for i in range(14)]
        self.gates = []
        self.dep = []
        self.pivots = {}
        for i, v in enumerate(self.vals):
            self.insert(v, 1 << i)

    def insert(self, v, mask):
        while v:
            bit = v.bit_length() - 1
            if bit not in self.pivots:
                self.pivots[bit] = v, mask
                return None
            x, m = self.pivots[bit]
            v ^= x
            mask ^= m
        return mask

    def AND(self, name, a, b):
        v = a & b
        j = len(self.vals)
        rel = self.insert(v, 1 << j)
        self.gates.append((name, a, b, v))
        self.vals.append(v)
        self.names.append(name)
        if rel is not None:
            self.dep.append({"gate": name, "relation": [self.names[i] for i in range(j + 1) if rel >> i & 1]})
        return v

    def MAJ(self, name, a, b, c):
        return self.AND(name, a ^ c, b ^ c) ^ c


def constructor():
    m = Model()
    a = m.vals[1:7]
    e = m.vals[7:10]
    nm = m.vals[10:13]
    k1, k2 = m.vals[13:15]
    c1 = m.AND("c1", a[0], e[0])
    c2 = m.MAJ("c2", a[1], e[1], c1)
    c3 = m.MAJ("c3", a[2], e[2], c2)
    c4 = m.AND("c4", a[3], c3)
    tt = m.AND("tt", k1, k2)
    r1 = m.AND("r1", nm[0], a[0])
    k = [nm[0] ^ a[0], nm[1] ^ a[1] ^ r1]
    r2 = m.MAJ("r2", nm[1], a[1], r1)
    k.append(nm[2] ^ a[2] ^ r2)
    r3 = m.MAJ("r3", nm[2], a[2], r2)
    a4, a5 = k[0], k[1] ^ k[0]
    y3 = m.AND("y3", k1 ^ k2 ^ tt, a[3] ^ c3)
    y4 = m.AND("y4", k2, a[4] ^ c4 ^ a4)
    c5 = m.MAJ("c5", a[4], a4, c4)
    y5 = m.AND("y5", tt, a[5] ^ c5 ^ a5)
    c6 = m.MAJ("c6", a[5], a5, c5)
    p = r3 ^ c3
    k.append(y3 ^ p)
    t = m.AND("upper3", p, y3 ^ c3)
    k.append(y4 ^ t)
    t = m.AND("upper4", t, y4 ^ c3)
    k.append(y5 ^ t)
    t = m.AND("upper5", t, y5 ^ c3)
    k.append(t)
    k.append(m.AND("sign", t, c3))
    gates, outputs = fc.tables(SOURCE.read_text(), "FWD")
    basis = [ONE] + k
    for j, (x, y) in enumerate(gates):
        basis.append(m.AND(f"Y16_{j}", fc.combination(x, basis), fc.combination(y, basis)))
    out = [fc.combination(x, basis) for x in outputs]
    low = [a[0] ^ e[0], a[1] ^ e[1] ^ c1, a[2] ^ e[2] ^ c2, a[3] ^ c3,
           a[4] ^ a4 ^ c4, a[5] ^ a5 ^ c5]
    assert len(m.gates) == 31
    for raw in range(N):
        kval = sum((v >> raw & 1) << i for i, v in enumerate(k))
        acc, ev, nv = raw & 63, raw >> 6 & 7, raw >> 9 & 7
        actual = fc.field_value([v >> raw & 1 for v in out])
        signed = kval - 256 if kval >= 128 else kval
        assert actual == (-(2**32 + 976) * signed) % 2**54
        assert sum((v >> raw & 1) << i for i, v in enumerate(low)) == (acc + ev + (actual & 63)) % 64
    return m, out + low + [c6]


def main():
    model, targets = constructor()
    target_pivots = {}
    for v in model.vals[:15] + targets:
        while v:
            bit = v.bit_length() - 1
            if bit not in target_pivots:
                target_pivots[bit] = v
                break
            v ^= target_pivots[bit]
    outside = []
    for name, _, _, v in model.gates:
        while v and (bit := v.bit_length() - 1) in target_pivots:
            v ^= target_pivots[bit]
        if v:
            outside.append(name)
    report = {"source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "cases": N, "gates": len(model.gates), "dependent_gates": model.dep,
              "internal_span_rank": len(model.pivots),
              "intermediates_outside_final_value_span": outside,
              "interface_AND_lower_bound": fc.rank(model.vals[:15] + targets) - 15,
              "status": "value analysis only; complete phase/cleanup not established"}
    destination = Path(__file__).with_name("constructor-analysis.json")
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
