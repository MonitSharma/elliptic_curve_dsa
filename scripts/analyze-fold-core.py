"""Bind Y16 fold-network truth tables to source and check their arithmetic domain.

This produces synthesis targets, not a circuit optimization or phase proof.
GF(2) span growth is a necessary AND-count lower bound, not an optimality proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def tables(source, tag):
    def body(name):
        match = re.search(r"const " + name + r"\s*:[^=]+?=\s*\[(.*?)\];", source, re.S)
        if not match:
            raise ValueError(f"Missing source table {name}")
        return match[1]
    gates = [tuple(int(x, 16) for x in pair) for pair in
             re.findall(r"\(\s*(0x[0-9a-f]+),\s*(0x[0-9a-f]+)\s*\)", body(f"Y16_{tag}_GATES"))]
    outputs = [int(x, 16) for x in re.findall(r"0x[0-9a-f]+", body(f"Y16_{tag}_OUT"))]
    assert len(outputs) == 21
    for j, pair in enumerate(gates):
        assert all(x < (1 << (9+j)) for x in pair), "Forward reference in source netlist"
    assert all(x < 1 << (9+len(gates)) for x in outputs)
    return gates, outputs


def combination(mask, basis):
    result = 0
    for i, value in enumerate(basis):
        if mask >> i & 1:
            result ^= value
    return result


def evaluate(x, gates, outputs):
    basis = [1] + [(x >> i) & 1 for i in range(8)]
    for a, b in gates:
        basis.append(combination(a, basis) & combination(b, basis))
    return [combination(m, basis) for m in outputs]


def field_value(fields, width=54):
    value = 0
    for bit in range(width):
        if bit < 4:
            v = 0
        elif bit <= 9:
            v = fields[bit - 4]
        elif bit <= 16:
            v = fields[6 + bit - 10]
        elif bit <= 31 or bit >= 39:
            v = fields[13]
        else:
            v = fields[14 + bit - 32]
        value |= v << bit
    return value


def rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            bit = vector.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = vector
                break
            vector ^= pivots[bit]
    return len(pivots)


def analyze(source, tag):
    gates, outputs = tables(source, tag)
    domain = list(range(-7, 71))
    columns = [0] * 21
    faults = []
    for row, x in enumerate(domain):
        fields = evaluate(x & 255, gates, outputs)
        value = field_value(fields)
        expected = ((-1 if tag == "FWD" else 1) * (2**32 + 976) * x) % 2**54
        assert value == expected, f"Arithmetic mismatch {tag}, x={x}"
        for i, field in enumerate(fields):
            columns[i] |= field << row
        # Fault injection: erase the last AND everywhere it is read.
        bit = 1 << (9 + len(gates) - 1)
        broken = evaluate(x & 255, gates[:-1], [m & ~bit for m in outputs])
        if field_value(broken) != expected:
            faults.append(x)
    affine = [(1 << len(domain)) - 1] + [sum(((x & 255) >> i & 1) << row
        for row, x in enumerate(domain)) for i in range(8)]
    affine_rank = rank(affine)
    combined_rank = rank(affine + columns)
    assert faults, "Negative control did not detect a removed AND"
    return {"source_table": tag, "domain": {"minimum": -7, "maximum": 70, "size": len(domain)},
            "arithmetic": ("-" if tag == "FWD" else "+") + "(2^32 + 976) * x mod 2^54",
            "arithmetic_mismatches": 0, "forward_AND_count": len(gates),
            "affine_span_rank": affine_rank, "affine_plus_outputs_rank": combined_rank,
            "AND_count_lower_bound": combined_rank - affine_rank,
            "removed_last_AND_counterexamples": faults,
            "output_truth_columns_hex": [hex(x) for x in columns],
            "limits": "The source caller must establish this domain. This checks output values, not ancilla allocation, cleanup or phase. The rank bound need not be attainable."}


def joint_forward(source):
    """Complete forward construction in fold_fwd_v2, including its low carry ABI."""
    gates, masks = tables(source, "FWD")
    count = 1 << 14
    columns = [0] * 28  # 21 addend fields, six low result bits, carry into bit six
    reachable = set()
    for raw in range(count):
        acc, e, nm = raw & 63, (raw >> 6) & 7, (raw >> 9) & 7
        k1, k2 = (raw >> 12) & 1, (raw >> 13) & 1
        c3 = int((acc & 7) + e >= 8)
        c4 = (acc >> 3 & 1) & c3
        low_sum = nm + (acc & 7)
        a4, a5 = low_sum & 1, ((low_sum >> 1) ^ low_sum) & 1
        a, z = acc >> 4 & 1, acc >> 5 & 1
        c5 = (a & a4) | (a & c4) | (a4 & c4)
        c6 = (z & a5) | (z & c5) | (a5 & c5)
        y3 = (k1 | k2) & ((acc >> 3 & 1) ^ c3)
        y4 = k2 & (a ^ c4 ^ a4)
        y5 = (k1 & k2) & (z ^ c5 ^ a5)
        k = low_sum + 8 * (y3 + 2*y4 + 4*y5 - c3)
        assert -7 <= k <= 70
        reachable.add(k)
        fields = evaluate(k & 255, gates, masks)
        addend = field_value(fields)
        assert addend == (-(2**32 + 976) * k) % 2**54
        low = acc + e + (addend & 63)
        assert low // 64 == c6
        values = fields + [(low >> i) & 1 for i in range(6)] + [c6]
        for i, value in enumerate(values):
            columns[i] |= value << raw
    affine = [(1 << count) - 1] + [sum(((raw >> i) & 1) << raw for raw in range(count)) for i in range(14)]
    lower = rank(affine + columns) - rank(affine)
    targets = {"input_order": "acc[0..6), E[0..3), Nm[0..3), k1, k2", "input_count": 14,
               "output_order": "Q[0..6), U[0..7), sign, H[0..7), low_result[0..6), carry6",
               "case_count": count, "truth_columns_hex": [hex(x) for x in columns]}
    destination = ROOT / "research-output/fold-core/joint-forward-targets.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(targets, indent=2) + "\n").encode()
    destination.write_bytes(payload)
    return {"case_count": count, "input_count": 14, "output_count": 28,
            "reachable_k_values": sorted(reachable), "arithmetic_mismatches": 0,
            "AND_count_lower_bound_for_value_interface": lower,
            "target_file": destination.relative_to(ROOT).as_posix(),
            "target_sha256": hashlib.sha256(payload).hexdigest(),
            "limits": "Derived from the unshed forward constructor. Retained carry layouts, measurement cleanup, phase and integration remain to be verified. This is not an emitted circuit."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "agents/product/src/point_add/y15_onefold.rs")
    args = parser.parse_args()
    raw = args.source.read_bytes()
    result = {"source": args.source.relative_to(ROOT).as_posix(),
              "source_sha256": hashlib.sha256(raw).hexdigest(),
              "cores": [analyze(raw.decode(), tag) for tag in ("FWD", "REV")],
              "joint_forward": joint_forward(raw.decode())}
    dest = ROOT / "docs/data/fold-core-analysis.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_sha256": result["source_sha256"], "cores": [
        {k: v for k, v in core.items() if k != "output_truth_columns_hex"} for core in result["cores"]]}, indent=2))
    print(json.dumps(result["joint_forward"], indent=2))


if __name__ == "__main__":
    main()
