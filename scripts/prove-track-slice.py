"""Prove a local gate rewrite on arbitrary inputs and measurement outcomes.

Models the unchanged simulator's Boolean value, classical capture and phase
semantics. Added private classical scratch is not part of the observable ABI.
This is a local equivalence check, not a complete point-add correctness proof.
"""
from pathlib import Path
import json
import time
import numpy as np
import z3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research-output/parallel-20261014"
NONE = 2**32 - 1


class Proof:
    def __init__(self, premises=None):
        self.solver = z3.Solver()
        self.solver.set(timeout=15000)
        self.interned = {}
        self.count = 0
        self.premises = premises or {"q": {}, "b": {}}

    def initial(self, kind, key):
        known = self.premises[kind].get(str(key))
        return z3.Bool(f"input_{kind}_{key}") if known is None else z3.BoolVal(bool(known))

    def value(self, expression):
        expression = z3.simplify(expression)
        if z3.is_const(expression):
            return expression
        key = expression.get_id()
        if key not in self.interned:
            value = z3.Bool(f"gate_{self.count}")
            self.count += 1
            self.solver.add(value == expression)
            self.interned[key] = value
        return self.interned[key]

    def run(self, ops, depth):
        q, b, measurements, resets = {}, {}, {}, {}
        phase = z3.BoolVal(False)
        captures = self.premises.get("stack", [-1] * depth)
        stack = [z3.Bool(f"entry_stack_{i}") if v == -1 else z3.BoolVal(bool(v)) for i, v in enumerate(captures)]
        base_value = self.premises.get("base", -1)
        base = z3.Bool("entry_condition") if base_value == -1 else z3.BoolVal(bool(base_value))

        def quantum(i):
            assert i != NONE
            return q.setdefault(i, self.initial("q", i))

        def bit(i):
            assert i != NONE
            return b.setdefault(i, self.initial("b", i))

        for row in ops:
            kind, c2, c1, target, ct, cc, reg = map(int, row)
            cond = base if cc == NONE else self.value(z3.And(base, bit(cc)))
            if kind in (1, 2, 17):
                continue
            if kind == 15:
                stack.append(base)
                base = cond
            elif kind == 16:
                if not stack:
                    raise ValueError("slice has an unmatched condition pop")
                base = stack.pop()
            elif kind in (6, 8, 13):
                v = cond
                if kind != 6:
                    v = self.value(z3.And(v, quantum(c1)))
                if kind == 13:
                    v = self.value(z3.And(v, quantum(c2)))
                q[target] = self.value(z3.Xor(quantum(target), v))
            elif kind == 10:
                a, t = quantum(c1), quantum(target)
                q[c1] = self.value(z3.If(cond, t, a))
                q[target] = self.value(z3.If(cond, a, t))
            elif kind in (0, 7, 9, 14):
                v = cond
                if kind != 0:
                    v = self.value(z3.And(v, quantum(target)))
                if kind in (9, 14):
                    v = self.value(z3.And(v, quantum(c1)))
                if kind == 14:
                    v = self.value(z3.And(v, quantum(c2)))
                phase = self.value(z3.Xor(phase, v))
            elif kind in (11, 12):
                counts, key = (measurements, ct) if kind == 12 else (resets, target)
                occurrence = counts.get(key, 0)
                counts[key] = occurrence + 1
                rng = z3.Bool(f"{'hmr' if kind == 12 else 'reset'}_{key}_{occurrence}")
                phase = self.value(z3.Xor(phase, z3.And(quantum(target), rng, cond)))
                q[target] = self.value(z3.And(quantum(target), z3.Not(cond)))
                if kind == 12:
                    b[ct] = self.value(z3.If(cond, rng, bit(ct)))
            elif kind == 3:
                b[ct] = self.value(z3.Xor(bit(ct), cond))
            elif kind == 4:
                b[ct] = self.value(z3.And(bit(ct), z3.Not(cond)))
            elif kind == 5:
                b[ct] = self.value(z3.Or(bit(ct), cond))
            else:
                raise ValueError(f"unknown operation {kind}")
        return q, b, phase, stack, base

    def equivalent(self, original, candidate, depth):
        a, b = self.run(original, depth), self.run(candidate, depth)
        if len(a[3]) != len(b[3]):
            return "condition_stack_mismatch", None
        differences = []
        labels = []
        for key in a[0].keys() | b[0].keys():
            differences.append(a[0].get(key, self.initial("q", key)) != b[0].get(key, self.initial("q", key)))
            labels.append(f"q:{key}")
        for key in a[1]:
            differences.append(a[1][key] != b[1].get(key, self.initial("b", key)))
            labels.append(f"b:{key}")
        differences.extend([a[2] != b[2], a[4] != b[4]])
        labels.extend(["phase", "condition"])
        differences.extend(x != y for x, y in zip(a[3], b[3]))
        labels.extend(f"stack:{i}" for i in range(len(a[3])))
        self.solver.add(z3.Or(differences))
        result = self.solver.check()
        detail = self.solver.reason_unknown() if result == z3.unknown else None
        if result == z3.sat:
            model = self.solver.model()
            detail = {"mismatched_outputs": [label for label, expression in zip(labels, differences) if z3.is_true(model.eval(expression, model_completion=True))]}
        return str(result), detail


if __name__ == "__main__":
    candidates = json.loads((OUT / "proof-candidates.json").read_text())
    stream = np.memmap(ROOT / "agents/product/research-output/pre-extra-guards.u32", dtype="<u4", mode="r").reshape(-1, 7)
    depth = np.cumsum((stream[:, 0] == 15).astype(np.int32) - (stream[:, 0] == 16).astype(np.int32))
    results = []
    known_path = OUT / "known-prefix.json"
    known = json.loads(known_path.read_text()) if known_path.exists() else {}
    for item in sorted(candidates, key=lambda x: x["ops"]):
        path = ROOT / item["path"]
        original = np.fromfile(str(path) + "-original.u32", dtype="<u4").reshape(-1, 7)
        candidate = np.fromfile(str(path) + "-candidate.u32", dtype="<u4").reshape(-1, 7)
        start = time.monotonic()
        proof = Proof(known.get(str(item["start"])))
        try:
            verdict, detail = proof.equivalent(original, candidate, int(depth[item["start"] - 1]))
        except ValueError as error:
            verdict, detail = "incomplete_slice", str(error)
        result = {**item, "verdict": verdict, "detail": detail, "seconds": time.monotonic() - start, "proof_gates": proof.count, "uses_known_prefix": str(item["start"]) in known}
        print(json.dumps(result), flush=True)
        results.append(result)
        (OUT / "slice-proof-results.json").write_text(json.dumps(results, indent=2) + "\n")
