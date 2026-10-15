"""Diagnostic figure: expected nonce-screen cost versus fresh-input failure rate.

Not a scored result. The curve is the expected thread-time for our exact
early-abort screener to find a passing identity-tail nonce. It uses the
measured 0.25 s per 64-shot batch per thread (screen logs) and assumes failed
batches arrive independently across the 141 batches of an official packet.
Points are census-measured streams. Usage: python plot_search_cost.py OUT.png [OUT.svg]
"""

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
BATCHES = 141
SEC_PER_BATCH = 0.25  # measured: 0.236 (wide), 0.249 (tip), 0.277 (B3) s per batch per thread


def expected_thread_hours(lam):
    """Expected nonces (1/P(pass)) times expected batches simulated per nonce."""
    q = lam / BATCHES
    p_pass = (1 - q) ** BATCHES
    batches_per_nonce = sum((1 - q) ** k for k in range(BATCHES))
    return batches_per_nonce * SEC_PER_BATCH / p_pass / 3600


# Census-measured failure rates (262,144 fresh shots each; see each STATUS.md).
POINTS = [
    ("Public product record 4b2ec52f (Q1234, 17.69)\nand former Toffoli record B3 (Q1235, 17.73)", 17.69, "left"),
    ("Our official Toffoli record\n(Q1464), actual: 593 nonces", 5.47, "right"),
    ("Wide +2 rails/anchors\n(diagnostic, Q1464)", 4.18, "left"),
]
ACTUAL_SMOOTH_THREAD_HOURS = 118.2 * 32 / 3600  # SCREEN_DONE elapsed_s x 32 threads

INK, MUTED, GRID, SURFACE, SERIES = "#1f1f1e", "#6b6a63", "#e6e5df", "#fcfcfb", "#2a78d6"
plt.rcParams.update({"font.size": 11, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED})
fig, ax = plt.subplots(figsize=(10, 6.2), dpi=160)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

lams = [x / 20 for x in range(0, 20 * 20 + 1)]
ax.plot(lams, [expected_thread_hours(x) for x in lams], color=SERIES, lw=2, zorder=2)

for label, lam, side in POINTS:
    y = expected_thread_hours(lam)
    ax.scatter([lam], [y], s=64, c=INK, edgecolors=SURFACE, linewidths=2, zorder=3)
    dx = 0.35 if side == "right" else -0.35
    ax.text(lam + dx, y, label, color=INK, fontsize=9.5, va="center",
            ha="left" if side == "right" else "right")
ax.scatter([5.47], [ACTUAL_SMOOTH_THREAD_HOURS], s=64, marker="D", facecolors=SURFACE,
           edgecolors=INK, linewidths=1.6, zorder=3)

for hours, text in ((1536, "1 day on 64 threads"), (32, "1 hour on 32 threads")):
    ax.axhline(hours, color=MUTED, lw=1, ls=":", zorder=1)
    ax.text(0.3, hours * 1.25, text, color=MUTED, fontsize=9.5)
ax.axvline(18, color=MUTED, lw=1.2, ls="--", zorder=1)
ax.text(17.85, 2e-3, "Community cap\n18 failed batches", color=INK, fontsize=9.5, ha="right", va="bottom")

ax.set_yscale("log")
ax.set_xlim(0, 20)
ax.set_ylim(1e-3, 1e6)
ax.set_xlabel("Fresh-input failed batches per 9,024-shot packet (census)")
ax.set_ylabel("Expected screener thread-hours to a passing nonce")
ax.set_title("Nonce-search cost grows exponentially with failure rate (diagnostic, not a scored result)", color=INK, loc="left")
ax.grid(True, which="major", color=GRID, lw=0.8)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
fig.text(0.01, 0.01, "Exact gate-level early-abort screener, 0.25 s per 64-shot batch per thread. "
         "Open diamond: the realized screen of our official entry (118 s on 32 threads).",
         color=MUTED, fontsize=8.5)
fig.tight_layout(rect=(0, 0.03, 1, 1))
for out in sys.argv[1:]:
    fig.savefig(out, facecolor=SURFACE)
print({label.split(chr(10))[0]: round(expected_thread_hours(lam), 2) for label, lam, _ in POINTS})
for hours in (32, 1536):
    print("lambda at", hours, "thread-hours:", max(x for x in lams if expected_thread_hours(x) <= hours))
