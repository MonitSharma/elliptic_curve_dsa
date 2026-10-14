"""Prove the compact restoring step's two-domain permutation extension.

This establishes an arithmetic extension for arbitrary remainder bits. It
does not by itself prove emitted gates, ancilla ownership, or measurement
phase. Those are separately admitted native component experiments.
"""
import hashlib
import json
from pathlib import Path
import sys
import z3


def prove(k):
    d, r = z3.BitVecs(f"dirty_divisor_{k} dirty_remainder_{k}", k)
    dw, rw = z3.ZeroExt(1, d), z3.ZeroExt(1, r)
    m = z3.BitVecVal(1 << k, k + 1)
    one = z3.BitVecVal(1, k + 1)
    n = 2 * rw + one
    low = z3.Extract(k - 1, 0, n)
    high = z3.Extract(k, k, n) == 1
    flag = z3.Xor(high, z3.UGE(low, d))
    out = low - z3.If(flag, d, z3.BitVecVal(0, k))
    valid = z3.ULT(r, d)
    quotient = z3.UGE(n, dw)
    valid_out = n - z3.If(quotient, dw, z3.BitVecVal(0, k + 1))
    complement = m - dw
    u = rw - dw
    uv = 2 * u + one
    invalid_out = dw + uv - z3.If(z3.UGE(uv, complement), complement, z3.BitVecVal(0, k + 1))
    expected = z3.If(valid, valid_out, invalid_out)
    domain = [z3.Extract(k - 1, k - 1, d) == 1, d & 1 == 1]
    s = z3.Solver()
    s.set(timeout=60000)
    s.add(*domain, z3.Or(z3.ZeroExt(1, out) != expected,
                        z3.ULT(out, d) != valid))
    result = s.check()
    assert result == z3.unsat, f"extension k={k}: {result} {s.reason_unknown()}"
    # Explicit inverse of each odd-modulus doubling map.
    ow = z3.ZeroExt(1, out)
    inv_valid = z3.LShR(ow + z3.If(out & 1 == 0, dw, z3.BitVecVal(0, k + 1)) - one, 1)
    uo = ow - dw
    inv_invalid = dw + z3.LShR(uo + z3.If(uo & 1 == 0, complement, z3.BitVecVal(0, k + 1)) - one, 1)
    inverse = z3.If(z3.ULT(out, d), inv_valid, inv_invalid)
    si = z3.Solver()
    si.set(timeout=60000)
    si.add(*domain, inverse != rw)
    inverse_result = si.check()
    assert inverse_result == z3.unsat, f"inverse k={k}: {inverse_result} {si.reason_unknown()}"
    negative = z3.Solver()
    negative.add(*domain, z3.UGE(r, d), z3.ZeroExt(1, out) != valid_out)
    negative_result = negative.check()
    assert negative_result == z3.sat, f"outside-domain negative control k={k}: {negative_result}"
    model = negative.model()
    return dict(width=k, partition_extension="unsat", inverse="unsat",
                unconditional_mod_D_negative_control="sat",
                counterexample=dict(divisor=model.eval(d).as_long(), remainder=model.eval(r).as_long()))


if __name__ == "__main__":
    output = Path(sys.argv[1])
    reports = []
    for k in [*range(2, 9), 16, 24, 25, 32]:
        report = prove(k)
        reports.append(report)
        print(json.dumps(report), flush=True)
    body = dict(scope="Arithmetic partition/inverse proof only; no circuit score",
                proof_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                z3_version=z3.get_version_string(), results=reports,
                theorem="R<D: 2R+1 modulo D. R=D+u: D+(2u+1 modulo (2^k-D)). Both odd-modulus branches have the stated inverse.")
    output.write_text(json.dumps(body, indent=2) + "\n")
