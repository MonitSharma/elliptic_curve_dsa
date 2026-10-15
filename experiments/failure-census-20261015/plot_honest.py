"""Diagnostic figure: fresh-input failure rate vs diagnostic executed Toffolis.

Not a scored result. Every point is a census of independent inputs on an
unchanged protected simulator; none of these streams has a qualified score.
Usage: python plot_honest.py OUT.png [OUT.svg]
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
RECORD_T = 761_156
PASS90 = -__import__("math").log(0.9)  # expected failed batches for a 90% pass chance

rows = json.loads((HERE / "evidence/all/table.json").read_text())
widen = HERE.parent / "widen-walk-20261015/evidence/table.json"
widen_rows = json.loads(widen.read_text()) if widen.exists() else []
# Pool replicate censuses of byte-identical streams (e.g. non-binding cap variants) into one point.
_pool = {}
for r in widen_rows:
    _pool.setdefault(r["stream_sha256"], []).append(r)
widen_rows = [dict(g[0], failed_batches_per_packet=sum(x["failed_batches_per_packet"] for x in g) / len(g),
                   p_pass=__import__("math").exp(-sum(x["failed_batches_per_packet"] for x in g) / len(g)))
              for g in _pool.values()]

# Fixed categorical order (reference palette slots 1-4), plus marker shapes as secondary encoding.
GROUPS = [
    ("Public baselines and edits (Q1234–1239)", "#2a78d6", "o", lambda r: r["qubits"] <= 1239),
    ("Narrow repairs (Q1267–1282)", "#eb6834", "s", lambda r: 1267 <= r["qubits"] <= 1282),
    ("Wide circuit and its repairs (Q1464)", "#1baf7a", "D", lambda r: r["qubits"] == 1464),
]
WIDEN = ("Walk-table widening (Q1464–1474)", "#eda100", "^")

INK, MUTED, GRID, SURFACE = "#1f1f1e", "#6b6a63", "#e6e5df", "#fcfcfb"
plt.rcParams.update({"font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED})
fig, ax = plt.subplots(figsize=(10, 6.2), dpi=160)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)


def scatter(points, label, color, marker):
    if not points:
        return
    ax.scatter([p["mean_t"] for p in points], [p["failed_batches_per_packet"] for p in points],
               s=64, c=color, marker=marker, label=label, edgecolors=SURFACE, linewidths=2, zorder=3)


for label, color, marker, pred in GROUPS:
    scatter([r for r in rows if pred(r)], label, color, marker)
scatter([r for r in widen_rows if not r["stream"].startswith("parent")], *WIDEN)

ax.axvline(RECORD_T, color=MUTED, lw=1.2, ls="--", zorder=1)
ax.text(RECORD_T + 300, 0.45,"Public Toffoli record\n761,156 (nonce-ground)", color=INK, fontsize=10, va="top")
ax.axhspan(0.01, PASS90, color="#1baf7a", alpha=0.08, zorder=0)
ax.text(750_200, PASS90 * 0.62, "Honest-pass zone: ≥90% chance to pass a fresh 9,024-shot test",
        color=INK, fontsize=10)

b3 = next(r for r in rows if r["stream"].endswith("b3-body-boundaries__run"))
ax.annotate("Public B3 record circuit\nP(pass fresh) ≈ 2–6×10⁻⁹", (b3["mean_t"], b3["failed_batches_per_packet"]),
            xytext=(763_500, 30), color=INK, fontsize=10, arrowprops=dict(arrowstyle="-", color=MUTED))
best = min([r for r in (widen_rows or rows) if r["mean_t"] < RECORD_T and not r["stream"].startswith("parent")], key=lambda r: r["failed_batches_per_packet"])
ax.annotate(f"Best under the record: {best['failed_batches_per_packet']:.1f} failed batches\nP(pass) ≈ {best['p_pass']:.0e}",
            (best["mean_t"], best["failed_batches_per_packet"]), xytext=(751_000, 1.4), color=INK, fontsize=10,
            arrowprops=dict(arrowstyle="-", color=MUTED))

ax.set_yscale("log")
ax.set_ylim(0.05, 45)
ax.set_xlim(749_500, 773_000)
ax.set_xlabel("Diagnostic mean executed Toffolis per shot  ·  fewer is better")
ax.set_ylabel("Expected failed batches per fresh test set\n(log scale · 0 required to pass)")
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}K"))
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
ax.grid(True, color=GRID, lw=0.8, zorder=0)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.legend(loc="lower right", frameon=False, fontsize=10)
fig.suptitle("No candidate yet passes a fresh test set", x=0.07, ha="left", fontsize=16, color=INK, weight="bold")
ax.set_title("Diagnostic census on 131,072–262,144 independent inputs per stream · not scored results",
             loc="left", fontsize=10.5, color=MUTED)
fig.tight_layout()
for out in sys.argv[1:]:
    fig.savefig(out, facecolor=SURFACE)
print("wrote", sys.argv[1:])
