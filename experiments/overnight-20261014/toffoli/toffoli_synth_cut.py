"""Exact XOR/AND synthesis on source-bound cut targets, not benchmark samples.

Duplicate source rows are removed only when all input/output truth bits agree.
The entire 16,384-row constructor domain is checked on any solution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import z3


def synth(bundle, gate_count, timeout):
    inputs = [int(v, 16) for v in bundle["input_columns_hex"]]
    targets = [int(v, 16) for v in bundle["target_columns_hex"]]
    rows = {}
    for r in range(1 << 14):
        packet = tuple(v >> r & 1 for v in inputs)
        want = tuple(v >> r & 1 for v in targets)
        assert packet not in rows or rows[packet] == want, "Cut interface loses required information"
        rows[packet] = want
    ordered = list(rows.items())
    n = len(ordered)
    packed = [sum(bits[i] << r for r, (bits, _) in enumerate(ordered)) for i in range(len(inputs))]
    wanted = [sum(bits[i] << r for r, (_, bits) in enumerate(ordered)) for i in range(len(targets))]
    solver = z3.Solver()
    solver.set(timeout=timeout * 1000)
    vals = [z3.BitVecVal(v, n) for v in packed]
    choices = []
    def combination(name, basis):
        sel = z3.BitVec(name, len(basis))
        value = z3.BitVecVal(0, n)
        for i, v in enumerate(basis):
            value = value ^ z3.If(z3.Extract(i, i, sel) == 1, v, z3.BitVecVal(0, n))
        return sel, value
    for j in range(gate_count):
        sa, a = combination(f"a{j}", vals)
        sb, b = combination(f"b{j}", vals)
        solver.add(z3.ULT(sa, sb))
        solver.add(sa != 0, sb != 0)
        q = z3.BitVec(f"g{j}", n)
        solver.add(q == a & b)
        vals.append(q)
        choices.append((sa, sb))
    out_choices = []
    for i, target in enumerate(wanted):
        s, value = combination(f"out{i}", vals)
        solver.add(value == z3.BitVecVal(target, n))
        out_choices.append(s)
    start = time.monotonic()
    status = solver.check()
    report = {"cut": bundle["cut"], "requested_AND_count": gate_count,
              "compressed_exact_rows": n, "source_rows": 1 << 14,
              "status": str(status), "seconds": time.monotonic()-start,
              "solver": z3.get_version_string(), "timeout_seconds": timeout}
    if status == z3.sat:
        model = solver.model()
        gates = [[model.eval(a).as_long(), model.eval(b).as_long()] for a, b in choices]
        outputs = [model.eval(s).as_long() for s in out_choices]
        def comb(mask, vals):
            v = 0
            for i, x in enumerate(vals):
                if mask >> i & 1:
                    v ^= x
            return v
        exact = list(inputs)
        for a, b in gates:
            exact.append(comb(a, exact) & comb(b, exact))
        assert [comb(s, exact) for s in outputs] == targets
        report.update(gates=gates, outputs=outputs, all_source_rows_pass=True)
    elif status == z3.unknown:
        report["reason"] = solver.reason_unknown()
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("targets", type=Path)
    p.add_argument("--index", type=int, default=0)
    p.add_argument("--gates", type=int, default=4)
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    raw = args.targets.read_bytes()
    report = synth(json.loads(raw)[args.index], args.gates, args.timeout)
    report["targets_sha256"] = hashlib.sha256(raw).hexdigest()
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
