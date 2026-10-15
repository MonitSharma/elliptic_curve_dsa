"""Private copy of the wide (cap1536) B3 circuit with a widened leapfrog walk table.

Only src/point_add/leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt changes.
Spec: name mid_delta tail_mode(keep|smooth) extra_park_rows. Park rows (6 6 6 6 5) are never widened:
the walk must end on 5-wire rails (leapfrog.rs n2_loan_out). Diagnostic only; score=NONE.
"""
from pathlib import Path
import hashlib, json, subprocess, sys

root = Path("/home/hclau/ecdsa_research/widen-walk-20261015")
src = Path("/home/hclau/ecdsa_research/dynamic-pool-20261015/wide-b3")
name, mid, tail_mode, extra = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
assert tail_mode in ("keep", "smooth")
assert extra % 2 == 0, "append rows in pairs to keep the final target parity"
dest = root / name / "src-b3"
assert not dest.exists()
dest.mkdir(parents=True)
subprocess.run(f"cd {src} && tar cf - --exclude=./ops.bin --exclude=./target . | (cd {dest} && tar xf -)", shell=True, check=True)
rel = "src/point_add/leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt"
lines, out, row = (dest / rel).read_text().splitlines(), [], 0
for line in lines:
    if not line.strip() or line.startswith("#"):
        out.append(line); continue
    v = list(map(int, line.split())); assert len(v) == 5
    if 2 <= row <= 136:
        v = [min(x + mid, 258) for x in v]
    elif tail_mode == "smooth" and row == 137:
        v = [9, 9, 8, 7, 6]
    elif tail_mode == "smooth" and row == 138:
        v = [7, 7, 6, 6, 5]
    out.append(" ".join(map(str, v))); row += 1
assert row == 140, row
assert out[-1].split() == ["6", "6", "6", "6", "5"]
out += ["6 6 6 6 5"] * extra
(dest / rel).write_text("\n".join(out) + "\n")
diff = subprocess.run(["diff", "-u", str(src / rel), str(dest / rel)], capture_output=True).stdout
(root / name / "table.patch").write_bytes(diff)
(root / name / "manifest.json").write_text(json.dumps({
    "name": name, "mid_delta": mid, "tail_mode": tail_mode, "extra_park_rows": extra,
    "rows": row + extra, "source": str(src), "only_changed": rel,
    "patch_sha256": hashlib.sha256(diff).hexdigest(), "score": None}, indent=2) + "\n")
print("prepared", name, row + extra)
