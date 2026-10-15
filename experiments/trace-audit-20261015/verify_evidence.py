"""Verify saved trace provenance and independently reconstruct census packet."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
evidence = root.parent / "trace-value-20261015/evidence"
manifest = json.loads((evidence / "manifest.json").read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(evidence / "observer.patch") == manifest["patch_sha256"]
for name, expected in manifest["packets"].items():
    assert sha(evidence / "packets" / name) == expected
assert (evidence / "stream.sha256").read_text().split()[0] == manifest["expected_final_stream"]
assert (evidence / "equality.log").read_text().strip() == "BYTE_IDENTICAL_STREAM=true"
assert (evidence / "run.exit").read_text().strip() == "0"
replay = root.parent / "failure-census-20261015/evidence/results/wide-replay.jsonl"
rows = [json.loads(line) for line in replay.read_text().splitlines() if line.strip()]
failed = [r for r in rows if r["value"]]
assert len(failed) == 186 and all(r["value"] == r["seeds"] == 32 for r in failed)
packet = "".join(f"{i} {r['px']} {r['py']} {r['ax']} {r['ay']} {r['exp_x']} {r['exp_y']}\n" for i, r in enumerate(failed))
assert packet.encode() == (evidence / "packets/valuefail186.tsv").read_bytes()
test = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(root), "-p", "test_analyze.py", "-v"], capture_output=True, text=True)
(root / "tests.log").write_text(test.stdout + test.stderr, encoding="utf-8")
assert test.returncode == 0
files = [evidence / "manifest.json", evidence / "observer.patch", evidence / "trace.log.gz",
         evidence / "events.txt", evidence / "stream.sha256", replay,
         *sorted((evidence / "packets").iterdir()),
         root.parent / "trace-value-20261015/analyze.py", root.parent / "trace-value-20261015/value_trace.rs"]
out = {"score": None, "status": "local saved-evidence audit passed",
       "packet_reconstruction": "all 186 value failures in original order; all fail 32/32 measurement seeds",
       "protected_simulator_equality": "reported true for both complete families in saved log",
       "stream_identity": "saved hash and equality report agree; large stream not present locally, not rehashed here",
       "server_status": "not freshly checked; automatic approval review previously unavailable due usage limit",
       "inputs": {str(p.relative_to(root.parent.parent)): sha(p) for p in files},
       "tests_exit": test.returncode}
(root / "evidence-verification.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
