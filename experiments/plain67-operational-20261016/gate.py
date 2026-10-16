"""Evaluate PLAIN67's predeclared fresh cohort under the AGENTS.md statistical failure-rate gate.

The cohort (label product67-frozen-20261016, 32,768 batches per source, parent =
public product record 4b2ec52f stream 2a522394) was declared and run before this
rule existed; it also passed the older candidate<=parent rule. No new sample is drawn.
"""
import hashlib
import json
from math import comb
from pathlib import Path

ws = Path("/home/hclau/ecdsa_research")
run = ws / "product67-native-20261016/product67"
files = {"parent": run / "parent-census.jsonl", "candidate": run / "candidate-census.jsonl"}
expected = {"parent": "1cab583d7af943943e1778168494791dbd3bc93a65552e17e8d6fae7a1f816c9",
            "candidate": "2f32c7d8da73b1dd29be200ab71b0cf912f2a208f3967fbdf4640ea70d79f7da"}
for k, p in files.items():
    assert hashlib.sha256(p.read_bytes()).hexdigest() == expected[k], k
P, C = ({r["batch"]: r for r in map(json.loads, p.open())} for p in files.values())
assert set(P) == set(C) and len(P) == 32768
n = len(P)
failed = {k: sum(1 for r in d.values() if r["failures"]) for k, d in (("parent", P), ("candidate", C))}
value = {k: sum(r["value_shots"] for r in d.values()) for k, d in (("parent", P), ("candidate", C))}
dirty = {k: sum(r["dirty_shots"] for r in d.values()) for k, d in (("parent", P), ("candidate", C))}
b = sum(1 for k in P if C[k]["failures"] and not P[k]["failures"])
c = sum(1 for k in P if P[k]["failures"] and not C[k]["failures"])
p_one_sided = sum(comb(b + c, x) for x in range(b, b + c + 1)) / 2 ** (b + c)
lam = {k: 141 * v / n for k, v in failed.items()}
rules = {"1_value_failures_not_above_parent": value["candidate"] <= value["parent"],
         "2_mcnemar_one_sided_p_at_least_0.05": p_one_sided >= 0.05,
         "3_failed_batches_per_packet_at_most_18": lam["candidate"] <= 18,
         "4_zero_dirty_shots": dirty["candidate"] == 0}
out = {"status": "FAILURE_GATE_PASS" if all(rules.values()) else "FAILURE_GATE_FAIL",
       "rule": "AGENTS.md statistical failure-rate gate, 16 October 2026",
       "label": "product67-frozen-20261016", "batches": n, "shots_each": 64 * n,
       "parent_stream_sha256": "2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e",
       "candidate_stream_sha256": "268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d",
       "census_sha256": expected, "failed_batches": failed, "failed_batches_per_packet": lam,
       "value_shots": value, "dirty_shots": dirty, "newly_failing_b": b, "newly_passing_c": c,
       "mcnemar_one_sided_p": p_one_sided, "rules": rules,
       "also_passed_old_rule_candidate_le_parent": failed["candidate"] <= failed["parent"],
       "new_sample_drawn": False}
(Path(__file__).resolve().parent / "GATE.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
assert out["status"] == "FAILURE_GATE_PASS"
