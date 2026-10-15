"""Publication figures: only public scored points and complete local passes."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def verified_width(receipt):
    if receipt.get("status") != "INDEPENDENTLY_VERIFIED_LOCAL_Q692_PASS_SUBMISSION_NOT_READY":
        return None
    if receipt.get("shots") != 9024:
        return None
    if any(type(receipt.get("failures", {}).get(k)) is not int or receipt["failures"][k] != 0
           for k in ("value", "phase_batches", "ancilla_batches")):
        return None
    q, t = receipt.get("qubits"), receipt.get("rounded_mean_executed_toffoli")
    if not all(type(v) is int and v > 0 for v in (q, t)) or receipt.get("product") != q*t:
        return None
    total=receipt.get("total_executed_toffoli")
    if type(total) is not int or (total+receipt["shots"]//2)//receipt["shots"] != t:
        return None
    if receipt.get("full_stream_rescan", {}).get("referenced_qubits") != q:
        return None
    for k in ("candidate_patch_sha256", "full_stream_sha256", "benchmark_log_sha256"):
        value = receipt.get(k)
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            return None
    return {"qubits": q, "toffoli": t}

def frontier_limits(summary, local):
    metrics = [s["officialMetrics"] for s in summary["frontier"]] + [local]
    return min(m["qubits"] for m in metrics) - 15, max(m["qubits"] for m in metrics) + 60


def render(summary, points, baseline, local):
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".tools/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FuncFormatter, FixedLocator
    import numpy as np

    bg, panel, white, muted = "#103b31", "#194c3f", "#f4f5e9", "#b3cdc0"
    gold, lilac, cyan = "#f2cc72", "#cbb6f4", "#80e2db"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
        "text.color": white, "axes.labelcolor": muted, "xtick.color": muted,
        "ytick.color": muted, "axes.edgecolor": "#4c7666", "svg.fonttype": "none",
        "svg.hashsalt": "ecdsa-resource-frontier", "axes.spines.top": False,
        "axes.spines.right": False})
    out = ROOT / "docs/figures"
    out.mkdir(parents=True, exist_ok=True)

    def save(fig, name):
        fig.savefig(out / (name + ".png"), dpi=180, facecolor=bg)
        fig.savefig(out / (name + ".svg"), facecolor=bg, metadata={"Date": None})
        svg = out / (name + ".svg")
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
        plt.close(fig)

    def base(title, subtitle, height=9.2):
        fig = plt.figure(figsize=(13, height), facecolor=bg)
        fig.text(.065, .947, "ECDSA  /  CIRCUIT RESEARCH", color=muted, fontsize=10, weight="bold")
        fig.text(.065, .895, title, fontsize=25, weight="bold")
        fig.text(.065, .855, subtitle, fontsize=11, color=muted)
        return fig

    def setup(ax):
        ax.set_facecolor(panel)
        ax.grid(color="#80a28e", alpha=.19, linestyle=(0, (2, 4)))
        ax.set_axisbelow(True)
        ax.tick_params(length=0, pad=8)

    def point(ax, m, color, marker="o", size=85):
        ax.scatter(m["qubits"], m["toffoli"], s=size, c=color, marker=marker,
                   edgecolors=white, linewidths=1.2, zorder=6)

    def note(ax, text, xy, xytext, color=white, fontsize=10):
        ax.annotate(text, xy, xytext=xytext, color=color, fontsize=fontsize,
            ha="left", va="center", linespacing=1.45,
            arrowprops={"arrowstyle": "-", "color": color, "lw": 1},
            bbox={"boxstyle": "round,pad=.5", "fc": bg, "ec": "none", "alpha": .95})

    leaders, front = summary["leaders"], summary["frontier"]
    mq = leaders["qubits"]["officialMetrics"]
    mp = leaders["product"]["officialMetrics"]
    mt = leaders["toffoli"]["officialMetrics"]
    own = min((s for s in points if s.get("solverUsername") == "MonitSharma"),
        key=lambda s: (s["officialMetrics"]["toffoli"], s["officialMetrics"]["qubits"]), default=None)
    q = [s["officialMetrics"]["qubits"] for s in front]
    t = [s["officialMetrics"]["toffoli"] for s in front]
    xmin, xmax = frontier_limits(summary, local)
    fig = base("Official scores. Three independent goals.",
        "Our submission is now publicly scored; product promotion is separate.  ·  " + summary["analyzed_at"][:16].replace("T", " ") + " Singapore")
    cards = [
        ("PUBLIC LOW WIDTH", f'{mq["qubits"]:,} qubits', f'Our Q{local["qubits"]} remains a local pass'),
        ("PUBLIC LOW TOFFOLI", f'{mt["toffoli"]:,}', "Our officially scored submission" if own and own["id"] == leaders["toffoli"]["id"] else "Lowest eligible official metric"),
        ("PUBLIC BEST Q × T", f'{leaders["product"]["officialScore"] / 1e6:,.3f}M', "No product improvement from our entry")]
    for i, (label, value, caption) in enumerate(cards):
        x = .065 + i * .302
        fig.add_artist(FancyBboxPatch((x, .705), .285, .115, boxstyle="round,pad=.008,rounding_size=.015",
            transform=fig.transFigure, facecolor=panel, edgecolor="#3f705a", lw=.7))
        fig.text(x + .015, .788, label, fontsize=9, color=muted, weight="bold")
        fig.text(x + .015, .746, value, fontsize=23, weight="bold")
        fig.text(x + .015, .718, caption, fontsize=9, color=muted)
    ax = fig.add_axes([.09, .23, .85, .42])
    setup(ax)
    ax.scatter([s["officialMetrics"]["qubits"] for s in points],
        [s["officialMetrics"]["toffoli"] for s in points], color=muted, s=10, alpha=.12, rasterized=True, zorder=1)
    ax.step(q + [xmax], t + [t[-1]], where="post", color=gold, lw=2, zorder=3)
    ax.scatter(q, t, color=lilac, s=23, edgecolors=white, linewidths=.45, zorder=4)
    point(ax, mp, gold, size=80)
    point(ax, local, cyan, "D", 100)
    if own:
        point(ax, own["officialMetrics"], cyan, "*", 260)
    ax.set(xlim=(xmin, xmax), ylim=(5.5e5, 2.7e9), yscale="log",
        xlabel="Peak logical qubits  ·  fewer is better", ylabel="Rounded mean executed Toffolis")
    ax.yaxis.set_major_locator(FixedLocator([1e6, 1e7, 1e8, 1e9]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v / 1e9:g}B" if v >= 1e9 else f"{v / 1e6:g}M"))
    ax.minorticks_off()
    note(ax, f'Our Q{local["qubits"]} · local pass\n{local["toffoli"] / 1e9:.3f}B Toffolis; not submitted',
        (local["qubits"], local["toffoli"]), (810, 1.1e9), cyan)
    note(ax, f'Public low width · Q{mq["qubits"]}\n{mq["toffoli"] / 1e6:.3f}M Toffolis',
        (mq["qubits"], mq["toffoli"]), (810, 2.2e8))
    note(ax, f'Best product · Q{mp["qubits"]}\nT{mp["toffoli"]:,}', (mp["qubits"], mp["toffoli"]), (1000, 2.8e6), gold)
    if own:
        m = own["officialMetrics"]
        note(ax, f'Our official score · Q{m["qubits"]}\nT{m["toffoli"]:,} · submission {own["id"][:8]}',
            (m["qubits"], m["toffoli"]), (1185, 2.2e7), cyan)
    handles = [Line2D([], [], color=gold, lw=2, label="Official public frontier"),
        Line2D([], [], marker="*", markersize=12, ls="", color=cyan, label="Our officially scored Toffoli entry"),
        Line2D([], [], marker="o", ls="", color=lilac, label="Official public Pareto points"),
        Line2D([], [], marker="D", ls="", color=cyan, label="Our separate Q692 local pass")]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(.065, .105), ncol=2,
        frameon=False, fontsize=10, handlelength=1.5, columnspacing=2.8)
    fig.text(.065, .072, f'{summary["eligible_count"]:,} eligible scored records · {len(front)} public frontier points · logarithmic gate axis', color=muted, fontsize=9)
    fig.text(.065, .045, 'Our entry: official metrics; score-only rejection because Q × T did not beat the product leader.', color=muted, fontsize=9)
    fig.text(.065, .022, 'Only official scores and complete local passes. A finite pass is not an all-input proof.', color=muted, fontsize=9)
    save(fig, "frontier")

    fig = base("Lower Toffolis. More qubits. A different product.",
        "Officially scored tradeoffs  ·  the current product leader, prior low-Toffoli entry and our submission", 8.8)
    reference = next((s for s in points if s["id"] == "26dd1d00-8e45-4f13-adcf-5eac665ca15f"), None)
    ax = fig.add_axes([.09, .30, .52, .45])
    setup(ax)
    lowq = min(mp["qubits"], mt["qubits"])
    highq = max(mp["qubits"], mt["qubits"])
    xs = np.linspace(lowq - 10, highq + 15, 250)
    product = leaders["product"]["officialScore"]
    ax.plot(xs, product / xs, color=gold, lw=1.8, ls="--")
    ax.axhline(mt["toffoli"], color=lilac, lw=1.2, ls=":")
    point(ax, mp, gold, size=110)
    if reference:
        point(ax, reference["officialMetrics"], lilac, size=75)
    point(ax, mt, cyan if own and own["id"] == leaders["toffoli"]["id"] else lilac, "*", 240)
    note(ax, f'Product leader\nQ{mp["qubits"]} · T{mp["toffoli"]:,}', (mp["qubits"], mp["toffoli"]), (lowq + 25, 783000), gold)
    note(ax, f'Lowest public Toffolis\nQ{mt["qubits"]} · T{mt["toffoli"]:,}', (mt["qubits"], mt["toffoli"]), (highq - 100, 722000), cyan)
    ax.set(xlim=(lowq - 15, highq + 20), ylim=(min(product / (highq + 15), mt["toffoli"]) * .97, max(mp["toffoli"], mt["toffoli"]) * 1.055),
        xlabel="Peak logical qubits", ylabel="Rounded mean executed Toffolis")
    ax.set_xticks(sorted({mp["qubits"], mt["qubits"], 1300, 1400}))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v / 1000:.0f}K"))
    ax.text(.04, .05, "Gold curve: equal to the best Q × T", transform=ax.transAxes, color=muted, fontsize=9)
    xcard = .66
    fig.add_artist(FancyBboxPatch((xcard, .30), .28, .45, boxstyle="round,pad=.012,rounding_size=.012",
        transform=fig.transFigure, facecolor=panel, edgecolor="#3f705a", lw=.7))
    fig.text(xcard + .018, .71, "OUR ENTRY VS PRIOR LOW-T (B3)", fontsize=9, color=muted, weight="bold")
    if own and reference:
        a, b = own["officialMetrics"], reference["officialMetrics"]
        dt = b["toffoli"] - a["toffoli"]
        fig.text(xcard + .018, .655, f'−{dt:,} Toffolis', fontsize=21, weight="bold", color=cyan)
        fig.text(xcard + .018, .62, f'{dt / b["toffoli"]:.2%} fewer executed gates', fontsize=10, color=muted)
        fig.text(xcard + .018, .555, f'+{a["qubits"] - b["qubits"]:,} qubits', fontsize=21, weight="bold")
        fig.text(xcard + .018, .52, f'{a["qubits"]:,} peak logical qubits', fontsize=10, color=muted)
        fig.text(xcard + .018, .455, f'+{own["officialScore"] / product - 1:.2%} product', fontsize=21, weight="bold", color=gold)
        fig.text(xcard + .018, .42, "Compared with the product leader", fontsize=10, color=muted)
        fig.text(xcard + .018, .35, "Official metrics; no product promotion", fontsize=9, color=muted)
    fig.text(.09, .21, f'Next low-T target: T ≤ {mt["toffoli"] - 1:,}.  At Q{mt["qubits"]}, product improvement needs T ≤ {(product - 1) // mt["qubits"]:,}.', fontsize=11, weight="bold")
    fig.text(.09, .165, f'At Q{mp["qubits"]}, the strict product target remains T ≤ {(product - 1) // mp["qubits"]:,}.', fontsize=10, color=muted)
    fig.text(.09, .105, f'Official Toffoli minimum: {leaders["toffoli"]["id"][:8]}. Product promotion belongs to {leaders["product"]["id"][:8]}.', fontsize=10, color=muted)
    fig.text(.09, .065, 'Q692 remains a separate local result. Failed correctness and component-only results are excluded.', fontsize=9, color=muted)
    save(fig, "record-tradeoffs")

if __name__=="__main__":
    import importlib.util
    spec=importlib.util.spec_from_file_location("leaderboard",ROOT/"scripts/analyze-leaderboard.py")
    lb=importlib.util.module_from_spec(spec);spec.loader.exec_module(lb)
    summary=json.loads((ROOT/"docs/data/latest-leaderboard.json").read_text())
    points=json.loads((ROOT/"docs/data/public-plot-points.json").read_text())
    local=verified_width(json.loads((ROOT/"experiments/verification-20261015/independent-verification.json").read_text()))
    if local is None:raise ValueError("No admissible local width evidence")
    baseline=lb.verified_reproduction(json.loads((ROOT/"docs/data/server-verification.json").read_text()))
    render(summary,lb.eligible(points),baseline,local)
