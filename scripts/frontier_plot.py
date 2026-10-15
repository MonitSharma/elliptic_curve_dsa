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
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":12,
        "text.color":white, "axes.labelcolor":muted, "xtick.color":muted,
        "ytick.color":muted, "axes.edgecolor":"#4c7666", "svg.fonttype":"none",
        "svg.hashsalt":"ecdsa-resource-frontier", "axes.spines.top":False,
        "axes.spines.right":False})
    out = ROOT / "docs/figures"; out.mkdir(parents=True, exist_ok=True)
    def save(fig, name):
        fig.savefig(out/(name+".png"), dpi=180, facecolor=bg)
        fig.savefig(out/(name+".svg"), facecolor=bg, metadata={"Date":None})
        svg=out/(name+".svg")
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
        plt.close(fig)
    def base(title, subtitle, height=8.7):
        fig=plt.figure(figsize=(13,height),facecolor=bg)
        fig.text(.065,.947,"ECDSA  /  CIRCUIT RESEARCH",color=muted,fontsize=10,weight="bold")
        fig.text(.065,.895,title,fontsize=26,weight="bold")
        fig.text(.065,.855,subtitle,fontsize=12,color=muted)
        return fig
    def setup(ax):
        ax.set_facecolor(panel)
        ax.grid(color="#80a28e",alpha=.19,linestyle=(0,(2,4)))
        ax.set_axisbelow(True);ax.tick_params(length=0,pad=9)
    def point(ax, m, color, marker="o", size=85):
        ax.scatter(m["qubits"],m["toffoli"],s=size,c=color,marker=marker,
                   edgecolors=white,linewidths=1.4,zorder=6)
    def note(ax,text,xy,xytext,color=white):
        ax.annotate(text,xy,xytext=xytext,color=color,fontsize=11,
            ha="left",va="center",linespacing=1.5,
            arrowprops={"arrowstyle":"-","color":color,"lw":1},
            bbox={"boxstyle":"round,pad=.55","fc":bg,"ec":"none","alpha":.95})
    leaders=summary["leaders"];front=summary["frontier"]
    q=[s["officialMetrics"]["qubits"] for s in front]
    t=[s["officialMetrics"]["toffoli"] for s in front]
    fig=base("One local width improvement. Three independent goals.",
             "Public Pareto frontier + our complete local pass  ·  "+summary["analyzed_at"][:10])
    cards=[
        ("OUR LOCAL WIDTH",str(local["qubits"])+" qubits","9,024-shot pass · not submitted"),
        ("PUBLIC LOW TOFFOLI",f'{leaders["toffoli"]["officialMetrics"]["toffoli"]:,}',"No new local Toffoli record yet"),
        ("PUBLIC BEST Q × T",f'{leaders["product"]["officialScore"]/1e6:,.3f}M',"No local product improvement yet")]
    for i,(label,value,caption) in enumerate(cards):
        x=.065+i*.302
        fig.add_artist(FancyBboxPatch((x,.705),.285,.115,boxstyle="round,pad=.008,rounding_size=.015",
                       transform=fig.transFigure,facecolor=panel,edgecolor="#3f705a",lw=.7))
        fig.text(x+.015,.788,label,fontsize=9,color=muted,weight="bold")
        fig.text(x+.015,.746,value,fontsize=23,weight="bold")
        fig.text(x+.015,.718,caption,fontsize=9,color=muted)
    ax=fig.add_axes([.09,.18,.85,.47]);setup(ax)
    ax.scatter([s["officialMetrics"]["qubits"] for s in points],
               [s["officialMetrics"]["toffoli"] for s in points],
               color=muted,s=10,alpha=.12,rasterized=True,zorder=1)
    ax.step(q+[1460],t+[t[-1]],where="post",color=gold,lw=2,zorder=3)
    ax.scatter(q,t,color=lilac,s=23,edgecolors=white,linewidths=.45,zorder=4)
    point(ax,leaders["product"]["officialMetrics"],gold,size=65)
    point(ax,local,cyan,"D",100)
    if baseline:ax.scatter(baseline["qubits"],baseline["toffoli"],marker="s",s=85,
                          facecolors="none",edgecolors=cyan,linewidths=1.3,zorder=5)
    ax.set(xlim=(665,1460),ylim=(5.5e5,2.7e9),yscale="log",
           xlabel="Peak logical qubits  ·  fewer is better",ylabel="Rounded mean executed Toffolis")
    ax.yaxis.set_major_locator(FixedLocator([1e6,1e7,1e8,1e9]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f"{v/1e9:g}B" if v>=1e9 else f"{v/1e6:g}M"))
    ax.minorticks_off()
    note(ax,"Our Q692 · local pass\n1.481B Toffolis; not an official entry",(local["qubits"],local["toffoli"]),(790,1.18e9),cyan)
    mq=leaders["qubits"]["officialMetrics"]
    note(ax,f'Public low width · Q{mq["qubits"]}\n{mq["toffoli"]/1e6:.3f}M Toffolis',(mq["qubits"],mq["toffoli"]),(790,2.7e8))
    mp=leaders["product"]["officialMetrics"]; mt=leaders["toffoli"]["officialMetrics"]
    note(ax,"Public low-T / best-product region\nExpanded in the second figure",(mp["qubits"],mp["toffoli"]),(1100,4.2e6),gold)
    handles=[Line2D([],[],color=gold,lw=2,label="Public frontier"),
             Line2D([],[],marker="o",ls="",color=lilac,label="Public Pareto points"),
             Line2D([],[],marker="D",ls="",color=cyan,label="Our Q692 local pass"),
             Line2D([],[],marker="s",ls="",markerfacecolor="none",color=cyan,label="Passing C5 reproduction")]
    fig.legend(handles=handles,loc="lower left",bbox_to_anchor=(.066,.085),ncol=4,
               frameon=False,fontsize=10,handlelength=1.5,columnspacing=1.7)
    fig.text(.065,.06,f'Faint dots: eligible public records in view · {len(front)} public frontier points · logarithmic gate axis',
             color=muted,fontsize=9)
    fig.text(.065,.035,"Only official scores and complete local passes. A finite pass is not an all-input proof. Failed candidates are excluded.",
             color=muted,fontsize=9)
    save(fig,"frontier")

    fig=base("A Toffoli record does not have to win the product.",
             "Close-up of the verified results  ·  public leaders and our passing reproductions",7.6)
    ax=fig.add_axes([.105,.24,.82,.53]);setup(ax)
    lo=min(mp["qubits"],mt["qubits"],baseline["qubits"] if baseline else mp["qubits"])
    hi=max(mp["qubits"],mt["qubits"],baseline["qubits"] if baseline else mp["qubits"])
    xs=np.linspace(lo-.4,hi+.5,200)
    ax.plot(xs,leaders["product"]["officialScore"]/xs,color=gold,lw=1.8,ls="--")
    ax.axhline(leaders["toffoli"]["officialMetrics"]["toffoli"],color=lilac,lw=1.4,ls=":")
    point(ax,leaders["product"]["officialMetrics"],gold,size=110)
    point(ax,leaders["toffoli"]["officialMetrics"],lilac,size=110)
    if baseline:
        ax.scatter(baseline["qubits"],baseline["toffoli"],marker="s",s=110,
                   facecolors="none",edgecolors=cyan,linewidths=2,zorder=5)
        note(ax,f'C5 public reproduction\nQ{baseline["qubits"]} · T{baseline["toffoli"]:,}',(baseline["qubits"],baseline["toffoli"]),(lo+.3,baseline["toffoli"]+32),cyan)
    note(ax,f'Best public product\nQ{mp["qubits"]} · T{mp["toffoli"]:,}',(mp["qubits"],mp["toffoli"]),(lo-.34,mp["toffoli"]-321),gold)
    note(ax,f'Lowest public Toffolis\nQ{mt["qubits"]} · T{mt["toffoli"]:,}',(mt["qubits"],mt["toffoli"]),(hi-.35,mt["toffoli"]+264),lilac)
    top=max(mp["toffoli"],mt["toffoli"],baseline["toffoli"] if baseline else 0)
    ax.set(xlim=(lo-.4,hi+.5),ylim=(min(mp["toffoli"],mt["toffoli"])-676,top+212),xlabel="Peak logical qubits",
           ylabel="Rounded mean executed Toffolis")
    ax.set_xticks(sorted({lo,hi,mp["qubits"],mt["qubits"]}));ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f"{v:,.0f}"))
    fig.text(.105,.155,f'At Q{mt["qubits"]}:  T ≤ {mt["toffoli"]-1:,} wins low-Toffoli;  T ≤ {(leaders["product"]["officialScore"]-1)//mt["qubits"]:,} wins the product.',
             color=white,fontsize=12,weight="bold")
    fig.text(.105,.108,"Gold dashed curve: equal to the best product. Purple dotted line: current low-Toffoli record.",
             color=muted,fontsize=10)
    fig.text(.105,.065,"Q692 remains a separate width result. No failed candidate or component-only saving is plotted.",
             color=muted,fontsize=10)
    save(fig,"record-tradeoffs")

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
