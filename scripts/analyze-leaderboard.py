"""Reproduce the frontier analysis from the saved public API snapshot."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter
import json
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research-output"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tools/matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".tools/cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

records = json.loads((OUT / "all-submissions.json").read_text())["submissions"]
benchmark = json.loads((OUT / "public-benchmark.json").read_text())["benchmark"]
scored = [
    s for s in records
    if (s["status"] == "accepted" or
        (s["status"] == "rejected" and s["rejectionReason"] == "score did not improve current best"))
    and s.get("officialScore") is not None
    and (s.get("officialMetrics") or {}).get("qubits", 0) > 0
    and (s.get("officialMetrics") or {}).get("toffoli", 0) > 0
]
for s in scored:
    m = s["officialMetrics"]
    assert s["officialScore"] == m["qubits"] * m["toffoli"], s["id"]

frontier = []
for s in sorted(scored, key=lambda s: (s["officialMetrics"]["qubits"], s["officialMetrics"]["toffoli"], s["createdAt"])):
    if not frontier or s["officialMetrics"]["toffoli"] < frontier[-1]["officialMetrics"]["toffoli"]:
        frontier.append(s)
best = min(scored, key=lambda s: s["officialScore"])
score = best["officialScore"]
summary = {
    "analyzed_at": datetime.now(ZoneInfo("Asia/Singapore")).isoformat(),
    "source": "https://api.ecdsa.fail/api/benchmarks/" + benchmark["id"] + "/submissions",
    "record_count": len(records),
    "status_counts": dict(Counter(s["status"] for s in records)),
    "officially_scored_count": len(scored),
    "frontier_count": len(frontier),
    "notes_available": sum(bool(s["note"]) for s in records),
    "benchmark_mode": benchmark["mode"],
    "best": {k: best[k] for k in ["id", "officialScore", "officialMetrics", "createdAt", "submissionCommitSha"]},
    "strict_gate_by_qubits": {q: (score - 1) // q for q in [1235, 1234, 1230, 1200, 1170, 1100, 893, 877, 694]},
    "eligibility": "accepted, or score-only rejected, with positive official metrics and a consistent official product score; excludes failures and claimed-only scores",
}
(OUT / "leaderboard-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
(OUT / "derived-frontier.json").write_text(json.dumps(frontier, indent=2) + "\n")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6), gridspec_kw={"width_ratios": [1.15, 1]})
fq = [s["officialMetrics"]["qubits"] for s in frontier]
ft = [s["officialMetrics"]["toffoli"] / 1e6 for s in frontier]
for ax in axes:
    for status, color, label in [("accepted", "#9aafad", "Accepted"), ("rejected", "#c4c8d0", "Scored; product did not improve")]:
        pts = [s["officialMetrics"] for s in scored if s["status"] == status]
        ax.scatter([m["qubits"] for m in pts], [m["toffoli"] / 1e6 for m in pts], s=12, color=color, alpha=.35, linewidth=0, label=label)
    ax.plot(fq, ft, "o-", color="#167d8d", markersize=3.5, linewidth=1.5, label="Derived Pareto frontier")
    ax.scatter([1235], [761156 / 1e6], marker="*", color="#d65d38", s=180, zorder=5, label="Current best product")
    ax.grid(alpha=.2)
    ax.set_xlabel("Peak logical qubits")
    ax.set_ylabel("Average Toffoli gates (millions)")
axes[0].set_yscale("log")
axes[0].set_xlim(660, max(s["officialMetrics"]["qubits"] for s in scored) + 80)
axes[0].set_ylim(.6, max(s["officialMetrics"]["toffoli"] for s in scored) / 1e6 * 1.3)
axes[0].set_title("All 1,216 scored records · 41 frontier points", loc="left", fontweight="bold", fontsize=11)
axes[0].annotate("694 Q / 336.8M T", (694, 336.751889), xytext=(900, 560), arrowprops={"arrowstyle": "-", "color": "#777"}, fontsize=9)
axes[0].annotate("877 Q / 2.331M T", (877, 2.331376), xytext=(1050, 6.5), arrowprops={"arrowstyle": "-", "color": "#777"}, fontsize=9)
axes[0].legend(loc="upper right", fontsize=8, frameon=False)
axes[1].set_xlim(1140, 1250)
axes[1].set_ylim(.72, 1.5)
axes[1].set_title("Where a new product record must land", loc="left", fontweight="bold", fontsize=11)
x = np.linspace(1140, 1250, 500)
axes[1].plot(x, score / x / 1e6, "--", color="#d65d38", linewidth=1.5)
axes[1].fill_between(x, .72, score / x / 1e6, color="#d65d38", alpha=.06)
axes[1].text(1143, .747, "Below dashed curve beats 940,027,660", fontsize=9, color="#a83f26")
axes[1].annotate("Skywalk: 1,170 Q / 946,553 T", (1170, .946553), xytext=(1145, 1.045), arrowprops={"arrowstyle": "-", "color": "#777"}, fontsize=9)
axes[1].annotate("Leader: 1,235 Q / 761,156 T", (1235, .761156), xytext=(1187, .91), arrowprops={"arrowstyle": "-", "color": "#777"}, fontsize=9)
fig.suptitle("ECDSA.fail · public results on 14 October 2026", x=.07, y=.97, ha="left", fontsize=15, fontweight="bold")
fig.text(.07, .025, "Official API snapshot: 1,557 records. Scored results establish packet-level benchmark outcomes, not universal circuit correctness.", fontsize=8, color="#555")
fig.subplots_adjust(left=.07, right=.98, bottom=.15, top=.85, wspace=.27)
fig.savefig(OUT / "leaderboard-frontier.png", dpi=180)
fig.savefig(OUT / "leaderboard-frontier.svg")

lines = ["# Full derived Pareto frontier", "", "Snapshot: 14 October 2026. Includes official score-only rejections; excludes benchmark failures and claimed-only scores.", "", "| Qubits | Toffolis | Product score | Submission |", "|---:|---:|---:|---|"]
for s in frontier:
    m = s["officialMetrics"]
    url = "https://api.ecdsa.fail/api/submissions/" + s["id"]
    lines.append(f"| {m['qubits']:,} | {m['toffoli']:,} | {s['officialScore']:,} | [{s['id'][:8]}]({url}) |")
(ROOT / "docs/frontier-results.md").write_text("\n".join(lines) + "\n")
print(json.dumps({k: summary[k] for k in ["record_count", "status_counts", "officially_scored_count", "frontier_count", "best"]}, indent=2))
