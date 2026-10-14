"""Prove overflow-flag reuse for each restoring-division step.

The proof requires an odd k-bit divisor with its high bit set and 0 <= R < D.
It proves the arithmetic identity. The emitted gates and phase cleanup are
tested independently by the native Rust reciprocal fixtures.
"""
from pathlib import Path
import json
import z3

ROOT = Path(__file__).resolve().parents[1]


def prove(k):
    divisor = z3.BitVec(f"divisor_{k}", k)
    remainder = z3.BitVec(f"remainder_{k}", k)
    wide_divisor = z3.ZeroExt(1, divisor)
    wide_next = 2 * z3.ZeroExt(1, remainder) + 1
    low = z3.Extract(k - 1, 0, wide_next)
    high = z3.Extract(k, k, wide_next) == 1
    quotient = z3.Xor(high, z3.UGE(low, divisor))
    next_remainder = low - z3.If(quotient, divisor, z3.BitVecVal(0, k))
    domain = [z3.Extract(k - 1, k - 1, divisor) == 1, divisor & 1 == 1, z3.ULT(remainder, divisor)]
    bad = z3.Or(
        quotient != z3.UGE(wide_next, wide_divisor),
        z3.UGE(next_remainder, divisor),
        z3.ZeroExt(1, next_remainder) != wide_next - z3.If(quotient, wide_divisor, z3.BitVecVal(0, k + 1)),
    )
    solver = z3.Solver()
    solver.add(*domain, bad)
    result = solver.check()
    assert result == z3.unsat, f"identity failed at k={k}"
    # A low-word comparison alone loses overflow. The solver must expose it.
    fault = z3.Solver()
    fault.add(*domain, z3.UGE(low, divisor) != z3.UGE(wide_next, wide_divisor))
    assert fault.check() == z3.sat, f"negative control failed at k={k}"
    model = fault.model()
    return {
        "precision": k,
        "identity_counterexample": "unsat",
        "missing_overflow_fault": "sat",
        "fault_example": {"divisor": model.eval(divisor).as_long(), "remainder": model.eval(remainder).as_long()},
    }


if __name__ == "__main__":
    results = [prove(k) for k in [*range(2, 9), 16, 24]]
    path = ROOT / "agents/qubits/research-output/compact-step-arithmetic-proof.json"
    path.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
