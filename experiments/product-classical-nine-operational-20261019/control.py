"""Lane-0 control: the operational binary on nonces 1..4096 must reproduce the qualified classical9 rows.

Runs the accepted binary exactly as a search worker would (lane 0 of 4, first 1, count
134217728, lookahead 4096) with a stop marker at 4096, so it screens only the first
window. Rows are compared with classical9-filter's qualified baseline-0.jsonl after
removing the operational-only flags (authoritative_rejection, proof_accepted) and
renaming provisional_wrong_value -> certified_wrong_value.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
ws = root.parent
ctl = root / "control"
assert not ctl.exists(), "never overwrite a control run"
ctl.mkdir()
(ctl / "passes").mkdir()
(ctl / "stop.txt").write_text("4096\n")
acc = root / "ACCEPTANCE.json"
env = dict(os.environ, SEARCH_LANE="0", SEARCH_LANES="4", SEARCH_STOP_FILE=str(ctl / "stop.txt"),
           SEARCH_PROGRESS_FILE=str(ctl / "progress.json"), SEARCH_PASS_DIR=str(ctl / "passes"),
           ACCEPTANCE_PATH=str(acc), ACCEPTANCE_SHA256=hashlib.sha256(acc.read_bytes()).hexdigest(),
           OMP_NUM_THREADS="1", RAYON_NUM_THREADS="1")
ops = ws / "product-classical-nine-20261019/candidate/ops.bin"
cmd = [str(root / "tool/target/release/value_prefilter"), str(ops), "1", "134217728", "2",
       str(ctl / "rows.jsonl"), str(ws / "prefilter-20261015/model-source"), "4096"]
with (ctl / "stdout.log").open("w") as out, (ctl / "stderr.log").open("w") as err:
    code = subprocess.run(cmd, env=env, stdout=out, stderr=err).returncode


def norm(row):
    row = dict(row)
    row.pop("authoritative_rejection", None)
    row.pop("proof_accepted", None)
    if "provisional_wrong_value" in row:
        row["certified_wrong_value"] = row.pop("provisional_wrong_value")
    return row


base_path = ws / "product-classical-nine-filter-20261019/baseline-0.jsonl"
assert hashlib.sha256(base_path.read_bytes()).hexdigest() == json.loads(acc.read_text())["qualified_prefix_rows_sha256"]
base = {r["nonce"]: norm(r) for r in map(json.loads, base_path.open())}
rows = {r["nonce"]: norm(r) for r in map(json.loads, (ctl / "rows.jsonl").open())} if code == 0 else {}
mismatch = sorted(n for n in set(base) | set(rows) if base.get(n) != rows.get(n))
progress = json.loads((ctl / "progress.json").read_text()) if (ctl / "progress.json").exists() else None
passes = sorted(int(p.stem.split("-")[1]) for p in (ctl / "passes").glob("pass-*.json"))
ok = code == 0 and not mismatch and len(rows) == 4096 and progress and progress["first"] == 1 and progress["last"] == 4096
result = {"status": "CONTROL_ROWS_EQUAL_QUALIFIED_PREFIX" if ok else "CONTROL_FAIL",
          "exit_code": code, "rows": len(rows), "baseline_rows": len(base), "mismatched_nonces": mismatch[:50],
          "mismatch_count": len(mismatch), "progress": progress, "passes_in_1_4096": passes,
          "rows_sha256": hashlib.sha256((ctl / "rows.jsonl").read_bytes()).hexdigest() if (ctl / "rows.jsonl").exists() else None,
          "binary_sha256": hashlib.sha256(Path(cmd[0]).read_bytes()).hexdigest()}
(root / "CONTROL.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
assert ok
