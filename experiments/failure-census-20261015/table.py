"""Markdown/JSON table over census results. Diagnostic only; score=NONE."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze import summarize  # noqa: E402

res_dir, log_dir = Path(sys.argv[1]), Path(sys.argv[2])
rows = []
for f in sorted(res_dir.glob("*.jsonl")):
    if f.name.endswith("-replay.jsonl"):
        continue
    name = f.stem
    err = (log_dir / f"{name}.err").read_text()
    m = re.search(r"ops=(\d+) qubits=(\d+) .* fs=([0-9a-f]+)", err)
    sha = (res_dir / f"{name}.stream.sha256").read_text().split()[0]
    s = summarize(f)
    pure_phase = sum(1 for l in f.read_text().splitlines()
                     for x in json.loads(l)["failures"] if x["phase"] and not x["value"])
    rows.append({"stream": name, "stream_sha256": sha, "ops": int(m[1]), "qubits": int(m[2]),
                 "mean_t": s["diagnostic_mean_executed_toffoli"], "mean_t_se": s["diagnostic_mean_toffoli_se"],
                 "value_per_1e4": 1e4 * s["value_rate"], "phase_only_per_1e4": 1e4 * pure_phase / s["shots"],
                 "dirty_shots": s["dirty_shots"],
                 "failed_batches_per_packet": s["expected_failed_batches_per_packet"],
                 "p_pass": s["p_pass_fresh_packet"], "p_pass_ci95": s["p_pass_fresh_packet_ci95"],
                 "shots": s["shots"], "score": None})
rows.sort(key=lambda r: r["failed_batches_per_packet"])
Path(sys.argv[3]).write_text(json.dumps(rows, indent=2) + "\n")
print("| Stream | Q | Diag. mean T | Value fails /10⁴ | Phase-only /10⁴ | Failed batches /packet | P(pass fresh) |")
print("|---|---:|---:|---:|---:|---:|---:|")
for r in rows:
    print(f"| `{r['stream']}` | {r['qubits']} | {r['mean_t']:,.0f} | {r['value_per_1e4']:.2f} | "
          f"{r['phase_only_per_1e4']:.2f} | {r['failed_batches_per_packet']:.2f} | {r['p_pass']:.1e} |")
