"""Exact integer model of low-window fold carry and post-rotation correction.

This is an algebraic design check, not a quantum circuit or a resource result.
No packet or circuit hash is selected or modified.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def production_core_k(low, e, nm, shift):
    """Boolean transcription of fold_fwd_v2's k construction, before addend_prog."""
    bit = lambda v, i: (v >> i) & 1
    maj = lambda a, b, c: (a & b) ^ (a & c) ^ (b & c)
    a, eb, nb = [bit(low, i) for i in range(6)], [bit(e, i) for i in range(3)], [bit(nm, i) for i in range(3)]
    k1, k2 = (shift - 3) & 1, (shift - 3) >> 1
    c1 = a[0] & eb[0]
    c2 = maj(a[1], eb[1], c1)
    c3 = maj(a[2], eb[2], c2)
    c4 = a[3] & c3
    tt = k1 & k2
    g1 = k1 ^ k2 ^ tt
    r1 = nb[0] & a[0]
    k = [nb[0] ^ a[0], nb[1] ^ a[1] ^ r1]
    r2 = maj(nb[1], a[1], r1)
    k.append(nb[2] ^ a[2] ^ r2)
    r3 = maj(nb[2], a[2], r2)
    a4, a5 = k[0], k[1] ^ k[0]
    y3 = g1 & (a[3] ^ c3)
    y4 = k2 & (a[4] ^ c4 ^ a4)
    c5 = maj(a[4], a4, c4)
    y5 = tt & (a[5] ^ c5 ^ a5)
    moving = r3 ^ c3
    k.append(y3 ^ moving)
    carry = moving & (y3 ^ c3)
    k.append(y4 ^ carry)
    carry &= y4 ^ c3
    k.append(y5 ^ carry)
    carry &= y5 ^ c3
    k.extend([carry, carry & c3])
    encoded = sum(v << i for i, v in enumerate(k))
    return encoded - 256 if encoded >= 128 else encoded


def fold(nbits, f, target, source, signs, shift, window):
    modulus = 1 << nbits
    p = modulus - f
    assert 0 <= target < modulus and 0 <= source < modulus
    assert 3 <= shift <= 6 and shift <= window <= nbits and f % 2 == 1
    nm = sum(bit << i for i, bit in enumerate(signs))
    unsigned_sum = target + sum((source if bit == 0 else modulus - 1 - source) << i for i, bit in enumerate(signs))
    e, low = divmod(unsigned_sum, modulus)
    a = low + e + (e - nm) * (f - 1)
    d = 1 << shift
    m = (a * pow(f, -1, d)) % d
    correction = e + (e - nm - m) * (f - 1)
    exact_w = low + correction
    assert exact_w % d == m
    c, low_window = divmod((low % (1 << window)) + correction, 1 << window)
    truncated_w = (low >> window << window) + low_window
    assert truncated_w == exact_w - c * (1 << window)
    rotate = lambda w: (w // d) + (w % d) * (1 << (nbits - shift))
    exact_out = rotate(exact_w) % p
    truncated_out = rotate(truncated_w) % p
    corrected_out = (truncated_out + c * (1 << (window - shift))) % p
    signed_sum = target + sum((1 if bit == 0 else -1) * (source << i) for i, bit in enumerate(signs))
    wanted = signed_sum * pow(d, -1, p) % p
    assert exact_out == corrected_out == wanted
    return {"e": e, "nm": nm, "m": m, "signed_window_carry": c,
            "exact_w": exact_w, "truncated_out": truncated_out,
            "corrected_out": corrected_out, "wanted": wanted}


def main():
    core_cases = 0
    for low in range(64):
        for e in range(8):
            for nm in range(8):
                for shift in range(3, 7):
                    f, d = 2**32 + 977, 1 << shift
                    a = low + e + (e - nm) * (f - 1)
                    m = a * pow(f, -1, d) % d
                    assert production_core_k(low, e, nm, shift) == nm + m - e
                    core_cases += 1
    # Exhaust every stored operand, sign letter and shift for a toy pseudo-Mersenne
    # modulus; exercise signed carries of magnitude >1 as well as +/-1.
    counts, failures, cases = Counter(), 0, 0
    for target in range(128):
        for source in range(128):
            for nm in range(8):
                signs = [(nm >> i) & 1 for i in range(3)]
                for shift in range(3, 7):
                    result = fold(7, 17, target, source, signs, shift, max(shift, 5))
                    cases += 1
                    counts[result["signed_window_carry"]] += 1
                    failures += result["truncated_out"] != result["wanted"]
    # Check the two actually observed production widths without fitting constants.
    sources = [ROOT.parent / "equal-division-20261015/evidence" / name
               for name in ("observer-analysis.json", "fold-analysis.json")]
    production = []
    for window, path in zip((56, 57), sources):
        trace = json.loads(path.read_text())["first_tick_divergence"]
        assert trace["tick"] == 120 and trace["shift"] == 3 and trace["coefficient"] == -5
        r = fold(256, 2**32 + 977, int(trace["before_target"], 16), int(trace["source"], 16), [0, 1, 1], 3, window)
        assert r["truncated_out"] == int(trace["actual_target"], 16)
        assert r["wanted"] == int(trace["expected_target"], 16)
        # At this observed tick, the production core's algebra fixes m=0:
        # low(X)=5*f-862, E=1, Nm=6, and shift=3.
        assert production_core_k(5 * (2**32 + 977) - 862, 1, 6, 3) == 5
        production.append({"window": window, **{k: (hex(v) if k.endswith("out") or k == "wanted" else v) for k, v in r.items()}})
    f = 2**32 + 977
    # E in [0,7], Nm in [0,7], m in [0,63] gives a conservative bound.
    lo, hi = -70 * (f - 1), 7 + 7 * (f - 1)
    assert -(1 << 56) < lo <= hi < (1 << 56)
    result = {"score": None, "status": "exact integer identity and finite exhaustive model passed; no quantum implementation",
              "production_quotient_boolean_core_cases": core_cases,
              "toy": {"nbits": 7, "p": 111, "cases": cases, "uncorrected_failures": failures,
                      "corrected_failures": 0, "signed_carry_counts": dict(sorted(counts.items())),
                      "note": "111 is composite; this identity needs only an odd modulus so division by powers of two is invertible."},
              "production_counterexamples": production,
              "production_window_correction_bound": {"min": lo, "max": hi, "carry_values_at_window56_or57": [-1, 0, 1]},
              "source_hashes": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              "limitations": ["No internal production quotient/carry wire was directly observed.",
                  "No gate synthesis, ancilla cleanup or measurement-phase proof.",
                  "No full-point benchmark or resource improvement.",
                  "The mathematical carry correction may be too costly to use at every payload tick."]}
    (ROOT / "fold-boundary-result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
