"""Private copy of the wide (cap1536) B3 circuit with a widened leapfrog walk.

Spec: name mid_delta tail_mode(keep|smooth) extra_park_rows [anch_delta [win_delta [cap]]].
- mid_delta widens rows 2..136 of the steps table; the form b<d0>,<d1>,... gives one delta per
  10-tick bin, and r<a>-<b>:<d>,... gives explicit tick ranges (convergence-aware, tapered envelopes)
  (src/point_add/leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt).
- tail_mode=smooth replaces rows 137/138 to remove the 3-bit cliff after tick 136; tail_mode
  t:W-n0-n1-n2-nb/... replaces everything after tick 136 with these descent rows plus park rows
  (padded to keep the row-count parity), and gives the inserted ticks anchors n2-3 (floor 3).
- extra_park_rows appends park rows. Park rows (6 6 6 6 5) are never widened:
  the walk must end on 5-wire rails (leapfrog.rs n2_loan_out).
- anch_delta (an integer, or f to follow the per-tick rail delta) shifts the YP8 choice-window anchors (leapfrog_data/yp8_L22_138_anch.txt)
  for ticks 2..136, so the window follows a widened register top.
- win_delta lengthens every LF_YP8 / LF_YP8_LATE window in leapfrog.rs's recipe.
- cap replaces the recipe's HEO_PIN_PP_WALK_MAX_QUBITS (1536 in the wide parent).
Defaults 0 reproduce the earlier variants byte for byte. Diagnostic only; score=NONE.
"""
from pathlib import Path
import hashlib, json, re, subprocess, sys

root = Path("/home/hclau/ecdsa_research/widen-walk-20261015")
src = Path("/home/hclau/ecdsa_research/dynamic-pool-20261015/wide-b3")
name, mid_spec, tail_mode, extra = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
if mid_spec.startswith("r"):
    ranges = [(int(a), int(b), int(d)) for a, b, d in
              (re.match(r"(\d+)-(\d+):(-?\d+)$", e).groups() for e in mid_spec[1:].split(","))]
    assert all(2 <= a <= b <= 136 for a, b, _ in ranges), "ranges must stay within ticks 2..136"
    tick_delta = lambda t: sum(d for a, b, d in ranges if a <= t <= b)
elif mid_spec.startswith("b"):
    bins_d = [int(x) for x in mid_spec[1:].split(",")]
    tick_delta = lambda t: bins_d[min(t // 10, len(bins_d) - 1)]
else:
    tick_delta = lambda t, d=int(mid_spec): d
mid = mid_spec
anch_spec = sys.argv[5] if len(sys.argv) > 5 else "0"
anch_delta = (lambda t: tick_delta(t)) if anch_spec == "f" else (lambda t, a=int(anch_spec): a)
anch = anch_spec != "0"
win = int(sys.argv[6]) if len(sys.argv) > 6 else 0
cap = int(sys.argv[7]) if len(sys.argv) > 7 else 0
assert tail_mode in ("keep", "smooth") or tail_mode.startswith("t:")
custom_tail = [list(map(int, r.split("-"))) for r in tail_mode[2:].split("/")] if tail_mode.startswith("t:") else None
assert extra % 2 == 0, "append rows in pairs to keep the final target parity"
dest = root / name / "src-b3"
assert not dest.exists()
dest.mkdir(parents=True)
subprocess.run(f"cd {src} && tar cf - --exclude=./ops.bin --exclude=./target . | (cd {dest} && tar xf -)", shell=True, check=True)
changed = []

rel = "src/point_add/leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt"
lines, out, row = (dest / rel).read_text().splitlines(), [], 0
for line in lines:
    if not line.strip() or line.startswith("#"):
        out.append(line); continue
    v = list(map(int, line.split())); assert len(v) == 5
    if 2 <= row <= 136:
        v = [min(x + tick_delta(row), 258) for x in v]
    elif custom_tail is not None and row >= 137:
        row += 1
        continue
    elif tail_mode == "smooth" and row == 137:
        v = [9, 9, 8, 7, 6]
    elif tail_mode == "smooth" and row == 138:
        v = [7, 7, 6, 6, 5]
    out.append(" ".join(map(str, v))); row += 1
assert row == 140, row
if custom_tail is not None:
    assert all(len(r) == 5 for r in custom_tail)
    out += [" ".join(map(str, r)) for r in custom_tail]
    n_rows = 137 + len(custom_tail)
    park = 1 if (n_rows + 1) % 2 == 0 else 2   # keep the original even row count
    out += ["6 6 6 6 5"] * park
    row = n_rows + park
else:
    assert out[-1].split() == ["6", "6", "6", "6", "5"]
out += ["6 6 6 6 5"] * extra
(dest / rel).write_text("\n".join(out) + "\n")
changed.append(rel)

if anch or custom_tail is not None:
    arel = "src/point_add/leapfrog_data/yp8_L22_138_anch.txt"
    text = (dest / arel).read_text()
    vals = [v.strip() for v in text.split(",")]
    nums = [int(v) for v in vals if v]
    shifted = [min(a + anch_delta(t), 255) if 2 <= t <= 136 else a for t, a in enumerate(nums)]
    if custom_tail is not None:
        for i, r in enumerate(custom_tail):
            shifted[137 + i] = max(3, r[3] - 3)
    (dest / arel).write_text(",".join(map(str, shifted)) + ("\n" if text.endswith("\n") else ""))
    changed.append(arel)

if win:
    lrel = "src/point_add/leapfrog.rs"
    s = (dest / lrel).read_text()
    n_yp8 = len(re.findall(r'\("LF_YP8", "\d+"\)', s))
    n_late = len(re.findall(r'\("LF_YP8_LATE", "[^"]*"\)', s))
    assert n_yp8 >= 1 and n_late >= 1, (n_yp8, n_late)
    s = re.sub(r'\("LF_YP8", "(\d+)"\)', lambda m: f'("LF_YP8", "{int(m[1]) + win}")', s)
    s = re.sub(r'\("LF_YP8_LATE", "([^"]*)"\)', lambda m: '("LF_YP8_LATE", "' + ",".join(
        f"{a}:{int(b) + win}" for a, b in (e.split(":") for e in m[1].split(","))) + '")', s)
    (dest / lrel).write_text(s)
    changed.append(lrel)

if cap:
    lrel = "src/point_add/leapfrog.rs"
    s = (dest / lrel).read_text()
    old = '("HEO_PIN_PP_WALK_MAX_QUBITS", "1536")'
    assert s.count(old) == 1, s.count(old)
    (dest / lrel).write_text(s.replace(old, f'("HEO_PIN_PP_WALK_MAX_QUBITS", "{cap}")'))
    if lrel not in changed:
        changed.append(lrel)

diff = subprocess.run(["diff", "-ruN", "-x", "target", "-x", "ops.bin", "-x", ".git", str(src / "src"), str(dest / "src")],
                      capture_output=True).stdout
(root / name / "table.patch").write_bytes(diff)
(root / name / "manifest.json").write_text(json.dumps({
    "name": name, "mid_delta": mid, "tail_mode": tail_mode, "extra_park_rows": extra,
    "anch_delta": anch_spec, "win_delta": win, "cap": cap or 1536, "rows": row + extra, "custom_tail": custom_tail, "source": str(src), "changed": changed,
    "patch_sha256": hashlib.sha256(diff).hexdigest(), "score": None}, indent=2) + "\n")
print("prepared", name, row + extra, changed)
