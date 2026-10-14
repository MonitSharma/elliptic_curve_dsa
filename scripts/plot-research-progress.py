"""Plot measured component costs and the generated, unscored full candidate.

The public full-stream count is author-reported. Native component costs and the
candidate full-stream count come from this workspace's preserved server logs.
Neither panel shows the challenge's mean executed Toffoli scoring metric.
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tools/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    evidence = json.loads((ROOT / "docs/data/qubit-experiment.json").read_text())
    prices = evidence["component_suite"]["vform_prices"]
    baseline = evidence["public_baseline_emission"]["emitted_Toffolis"]
    candidate = evidence["full_candidate"]["emitted_Toffolis"]
    saving = baseline - candidate
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4))
    fig.subplots_adjust(left=.08, right=.97, top=.82, bottom=.24, wspace=.35)
    colors = ["#466586", "#d68632"]
    x = np.arange(len(prices))
    old = [p["baseline_emitted_Toffolis"] for p in prices]
    new = [p["candidate_emitted_Toffolis"] for p in prices]
    a = axes[0]
    a.bar(x-.18, old, width=.36, color=colors[0], label="Baseline")
    a.bar(x+.18, new, width=.36, color=colors[1], label="Compact reciprocal")
    a.set_xticks(x, [f'{p["clean_helper_lanes"]} helper lanes' for p in prices])
    a.set_ylim(0, 22500)
    a.set_ylabel("Emitted Toffolis per complete V-form")
    a.set_title("Measured native component costs")
    for i, (o, n) in enumerate(zip(old, new)):
        a.text(i, max(o, n)+650, f'−{o-n:,}', ha="center", fontweight="bold")
    a.legend(loc="lower left", fontsize=8)
    a.grid(axis="y", alpha=.2)
    a.set_axisbelow(True)

    b = axes[1]
    b.barh([1, 0], [baseline/1e6, candidate/1e6], color=colors, height=.48)
    b.set_yticks([1, 0], ["Public Q693\n(author-reported)", "Our Q693\n(generated)"])
    # The truncated axis is explicitly labeled, so the tiny reduction cannot
    # be mistaken for a large fractional improvement or a scored record.
    b.set_xlim(336, 340)
    b.set_xlabel("Emitted Toffolis (millions; axis starts at 336)")
    state = evidence["full_candidate"].get("status", "unknown")
    score = evidence["full_candidate"].get("official_score")
    if score is not None:
        title = "Complete stream: evaluation collected"
        footer = "See the experiment receipt for correctness, scoring and qualification."
    elif "fail" in state.lower():
        title = "Complete stream: validation failed"
        footer = "The full candidate failed validation; see the receipt for its failure channels."
    else:
        title = "Complete stream: scoring still pending"
        footer = "Component checks pass; full correctness and the final score remain pending."
    b.set_title(title)
    for y, value in [(1, baseline), (0, candidate)]:
        b.text(value/1e6+.04, y, f'{value:,}', va="center", fontsize=9)
    b.text(.5, .97, f'{saving:,} fewer emitted Toffolis ({saving/baseline:.3%})',
           transform=b.transAxes, ha="center", va="top", fontsize=10, fontweight="bold")
    b.set_ylim(-.6, 1.8)
    b.grid(axis="x", alpha=.2)
    b.set_axisbelow(True)
    fig.suptitle("FAILED EXPERIMENT · compact reciprocal · 693 qubits", fontsize=15, y=.97,
                 color="#a12525")
    fig.text(.5, .085, "These are emitted counts, not mean executed Toffolis.\n" + footer,
             ha="center", fontsize=10, color="#454b52")
    # Experimental costs belong with the failure report, never in README results.
    out = ROOT / "experiments/qubits/figures/diagnostic-counts.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    plt.close(fig)
    print(out)


if __name__ == "__main__":
    main()
