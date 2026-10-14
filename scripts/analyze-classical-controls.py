"""Conservative dependency census, not sampled circuit control-pattern deletion.

Track four abstract value kinds: constants 0/1, an arbitrary classical function,
or a quantum-dependent function. Missing cancellation facts lose opportunities;
they never turn a quantum-dependent value into a classical value. Counts are
research leads, not proposed gate deletions or scored results.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import time

SPEC = importlib.util.spec_from_file_location("wire", Path(__file__).with_name("analyze-wire-lifetimes.py"))
WIRE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WIRE)
ZERO, ONE, CLASSICAL, QUANTUM = range(4)
NO = WIRE.NO


def conjunction(a, b):
    if a == ZERO or b == ZERO:
        return ZERO
    if a == ONE:
        return b
    if b == ONE:
        return a
    return max(a, b)


def xor(a, b):
    if a == ZERO:
        return b
    if b == ZERO:
        return a
    if a < CLASSICAL and b < CLASSICAL:
        return a ^ b
    return max(a, b)


def join(a, b):
    if a == b:
        return a
    return max(CLASSICAL, a, b)


def analyze(path):
    began = time.monotonic()
    abi_q, abi_b = set(), set()
    nq = nb = 0
    operations = 0
    for i, row in WIRE.records(path):
        kind, pad, c2, c1, target, bit, condition, reg = row
        for q in (c2, c1, target):
            if q != NO:
                nq = max(nq, q + 1)
        for b in (bit, condition):
            if b != NO:
                nb = max(nb, b + 1)
        if kind == 2:
            if target != NO:
                abi_q.add(target)
            if bit != NO:
                abi_b.add(bit)
        operations = i + 1
    qubits = [QUANTUM if q in abi_q else ZERO for q in range(nq)]
    bits = [CLASSICAL if b in abi_b else ZERO for b in range(nb)]
    stack = []
    base = ONE
    hits = []
    constants = []
    for i, row in WIRE.records(path):
        kind, pad, c2, c1, target, bit, condition, reg = row
        cond = base if condition == NO else conjunction(base, bits[condition])
        if kind == 15:
            stack.append(base)
            base = cond
        elif kind == 16:
            if not stack:
                raise ValueError("Unbalanced condition stack")
            base = stack.pop()
        elif kind == 6:
            qubits[target] = xor(qubits[target], cond)
        elif kind == 8:
            qubits[target] = xor(qubits[target], conjunction(cond, qubits[c1]))
        elif kind == 13:
            if cond != ZERO:
                controls = qubits[c1], qubits[c2]
                info = {"op": i, "controls": [c1, c2], "target": target,
                        "control_kinds": controls, "condition_depth": len(stack),
                        "explicit_condition": condition != NO}
                if CLASSICAL in controls:
                    hits.append(info)
                elif ZERO in controls or ONE in controls:
                    constants.append(info)
            delta = conjunction(cond, conjunction(qubits[c1], qubits[c2]))
            qubits[target] = xor(qubits[target], delta)
        elif kind == 10:
            if cond == ONE:
                qubits[c1], qubits[target] = qubits[target], qubits[c1]
            elif cond != ZERO:
                merged = join(qubits[c1], qubits[target])
                qubits[c1] = qubits[target] = merged
        elif kind in (11, 12):
            if cond == ONE:
                qubits[target] = ZERO
            elif cond != ZERO:
                qubits[target] = join(qubits[target], ZERO)
            if kind == 12 and cond != ZERO:
                bits[bit] = CLASSICAL
        elif kind == 3:
            bits[bit] = xor(bits[bit], cond)
        elif kind == 4:
            if cond == ONE:
                bits[bit] = ZERO
            elif cond != ZERO:
                bits[bit] = join(bits[bit], ZERO)
        elif kind == 5:
            if cond == ONE:
                bits[bit] = ONE
            elif cond != ZERO:
                bits[bit] = join(bits[bit], ONE)
        elif kind not in (0, 1, 2, 7, 9, 14, 17):
            raise ValueError(f"Unknown operation {kind}")
    if stack:
        raise ValueError("Unclosed conditions")
    return {"status": "conservative_dependency_analysis_only", "operations": operations,
            "abi_quantum": len(abi_q), "abi_classical": len(abi_b),
            "classical_control_sites": hits, "constant_control_sites": constants,
            "classical_control_count": len(hits), "constant_control_count": len(constants),
            "condition_depth_proxy": sum(0.5 ** (h["condition_depth"] + h["explicit_condition"]) for h in hits),
            "elapsed_seconds": time.monotonic() - began,
            "limits": "No shadow computation implemented, no gate deletion, no source candidate or qualification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stream", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = analyze(args.stream)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "classical_control_count", "constant_control_count",
                     "condition_depth_proxy", "elapsed_seconds")}, indent=2))


if __name__ == "__main__":
    main()
