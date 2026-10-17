"""Write ACCEPTANCE.json for the PRODUCT95 ascending nonce search (queue mode).

Binds the frozen PRODUCT95 stream, its native byte identity, the original-source mask,
the universal 95-stage cache certificate and per-input transfer, the declared
statistical failure gate (PASS against both the public record and PLAIN67), the build,
the ordering tests, the tool-diff audit and the filter qualification.
"""
import datetime
import hashlib
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parent
ws = root.parent
S95 = "ba87b9ceb0691ccfe8c509539cfc38e774ee02134363c19e3541c6e942723e84"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


assert not (root / "ACCEPTANCE.json").exists(), "never overwrite an acceptance receipt"
assert (root / "build.exit").read_text().strip() == "0"
assert "1 passed; 0 failed" in (root / "order-tests.log").read_text()
assert read(root / "TOOL_DIFF_AUDIT.json")["status"] == "ONLY_PRODUCT95_BINDINGS_DIFFER"
native_dir = ws / "product95-native-20261017"
native = read(native_dir / "NATIVE_IDENTITY.json")
assert native["status"] == "NATIVE_BYTE_IDENTITY_PASS" and native["generated"] == S95
gate = read(native_dir / "GATE.json")
assert gate["candidate_stream_sha256"] == S95 and gate["label"] == "product95-gate-20261017-v1" and gate["batches"] == 32768
for name, v in gate["verdicts"].items():
    assert v["status"] == "FAILURE_GATE_PASS" and all(v["rules"].values()), name
qual = read(ws / "product95-filter-20261017/RESULT.json")
assert qual["status"] == "DISABLED_PRODUCT95_PIPELINE_QUALIFICATION_PASS" and qual["all4096_rows_identical"] and qual["candidate_sha256"] == S95
pilot67 = read(ws / "plain67-persistent-pilot-20261016/RESULT.json")

cert = ws / "product-exact-20261015/cache-certificate95-20261017"
required = {
    ws / "product-exact-20261015/product-to95-rank-20261016/product-95-retained-1024-proxy.bin": S95,
    cert / "CACHE_EQUIVALENCE_CERTIFICATE.json": sha(cert / "CACHE_EQUIVALENCE_CERTIFICATE.json"),
    cert / "PER_INPUT_MASK_TRANSFER.json": sha(cert / "PER_INPUT_MASK_TRANSFER.json"),
    ws / "prefilter-20261015/evidence/mr-mask-tip-v3.bin": "560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d",
    ws / "prefilter-20261015/evidence/mr-mask-tip-v3-fused.bin": "1ccbbfc4a45b8d359be9ce21eb4640c72bb9bfe9bffb35f5630c0d13da3f2f8a",
    ws / "prefilter-20261015/libmask_fused.so": "dc8219ae84c21e244ec0e1b92a14e9d0705faf7ebced04a2663499a75a6af1a0",
    ws / "scalar-fast-20261015/libscalar_fast_batch.so": "3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f",
}
for p, h in required.items():
    assert sha(p) == h, p
c = read(cert / "CACHE_EQUIVALENCE_CERTIFICATE.json")
assert c["status"] == "UNIVERSAL_CACHE_EQUIVALENCE_AUDIT_PASS" and c["stage_count"] == 95 and c["candidate_stream_sha256"] == S95

lam = gate["verdicts"]["plain67_final"]["failed_batches_per_packet"]["candidate"]
mean_nonces = math.exp(-141 * math.log1p(-lam / 141))
rate_per_thread = pilot67["trials"][2]["observed_four_core_amortized_nonces_per_second"] / 4
threads = 56
record = {
    "status": "SOURCE_BOUND_MASK_TRANSFER_AND_RUNTIME_ACCEPTED_FOR_ASCENDING_SEARCH",
    "accepted_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "candidate": "PRODUCT95 (95-stage exact cache chain on public product record 4b2ec52f)",
    "candidate_stream_sha256": S95,
    "mask_sha256": "560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d",
    "lowest_pass_from": 1, "submission_mode": "queue",
    "failure_gate_pass": True, "failure_gate": gate,
    "cost_gate_pass": True,
    "expected_nonces": mean_nonces,
    "rate_estimate_source": "PLAIN67 persistent pilot (17.9M ops); PRODUCT95 has 20.3M ops, so the true rate may be lower. Estimate only.",
    "pilot_rate_nonces_per_thread_second_plain67": rate_per_thread,
    "expected_hours_at_56_threads_ideal_linear_plain67_rate": mean_nonces / (rate_per_thread * threads) / 3600,
    "wall_limit_hours": 48,
    "runtime_artifacts": {str(p): h for p, h in required.items()},
    "derivation": "PLAIN67 operational patches (prepare.py, search.rs) applied to the PRODUCT95-qualified product95-filter tool; TOOL_DIFF_AUDIT.json proves the sources differ from PLAIN67's operational tool only in PRODUCT95 bindings.",
    "remaining_gates": ["Lane-0 control equals qualified rows 1..4096 (CONTROL.json)",
                        "Every lower nonce accounted before selecting the lowest pass",
                        "Native source with selected TAIL_NONCE reproduces the pre-tail stream",
                        "Unchanged official benchmark.sh on the final source"],
    "score": None,
}
(root / "ACCEPTANCE.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"status": record["status"], "sha256": sha(root / "ACCEPTANCE.json"), "expected_nonces": mean_nonces,
                  "expected_hours_56": record["expected_hours_at_56_threads_ideal_linear_plain67_rate"]}, indent=2))
