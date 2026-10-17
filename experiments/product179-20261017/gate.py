"""Evaluate PRODUCT179's declared gate (GATE-DECLARATION.json) against the official PLAIN67 record."""
import hashlib, json
from math import comb
from pathlib import Path
d = Path("/home/hclau/ecdsa_research/product179-native-20261017")
decl = json.loads((d / "GATE-DECLARATION.json").read_text())
def rows(p):
    r = {x["batch"]: x for x in map(json.loads, p.open())}
    assert sorted(r) == list(range(decl["batch_count"])) and all(x["shots"] == 64 for x in r.values())
    return r
C, P = rows(d / "gate-candidate.jsonl"), rows(d / "gate-parent.jsonl")
n = len(C)
cf = sum(1 for r in C.values() if r["failures"]); pf = sum(1 for r in P.values() if r["failures"])
cv = sum(r["value_shots"] for r in C.values()); pv = sum(r["value_shots"] for r in P.values())
cd = sum(r["dirty_shots"] for r in C.values())
b = sum(1 for k in P if C[k]["failures"] and not P[k]["failures"])
c = sum(1 for k in P if P[k]["failures"] and not C[k]["failures"])
p = sum(comb(b + c, x) for x in range(b, b + c + 1)) / 2 ** (b + c)
delta = [(P[k]["toffoli"] - C[k]["toffoli"]) / 64 for k in range(n)]
mean = sum(delta) / n; se = (sum((x - mean) ** 2 for x in delta) / (n * (n - 1))) ** 0.5
rules = {"1_value_failures_not_above_parent": cv <= pv, "2_mcnemar_one_sided_p_at_least_0.05": p >= 0.05,
         "3_failed_batches_per_packet_at_most_18": 141 * cf / n <= 18, "4_zero_dirty_shots": cd == 0}
ident = json.loads((d / "NATIVE_IDENTITY.json").read_text())
out = {"status": "FAILURE_GATE_PASS" if all(rules.values()) else "FAILURE_GATE_FAIL", "label": decl["label"], "batches": n,
       "candidate_stream_sha256": ident["generated"], "parent_stream_sha256": decl["parent"]["stream_sha256"],
       "census_sha256": {k: hashlib.sha256((d / f).read_bytes()).hexdigest() for k, f in [("candidate", "gate-candidate.jsonl"), ("parent", "gate-parent.jsonl")]},
       "failed_batches": {"parent": pf, "candidate": cf}, "failed_batches_per_packet": {"parent": 141 * pf / n, "candidate": 141 * cf / n},
       "value_shots": {"parent": pv, "candidate": cv}, "dirty_shots_candidate": cd, "newly_failing_b": b, "newly_passing_c": c,
       "mcnemar_one_sided_p": p, "rules": rules, "paired_mean_T_saving": mean, "saving_standard_error": se,
       "mean_T": {"parent": sum(P[k]["toffoli"] for k in range(n)) / (64 * n), "candidate": sum(C[k]["toffoli"] for k in range(n)) / (64 * n)}}
(d / "GATE.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
