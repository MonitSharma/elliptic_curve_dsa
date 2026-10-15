"""Refresh/analyze ECDSA.fail data. Raw snapshots are ignored; compact evidence is tracked."""
import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74"
SGT = timezone(timedelta(hours=8))


def eligible(records):
    result = []
    for s in records:
        if not (s.get("status") == "accepted" or (s.get("status") == "rejected" and
                s.get("rejectionReason") == "score did not improve current best")):
            continue
        m = s.get("officialMetrics") or {}
        q, t = m.get("qubits"), m.get("toffoli")
        if all(type(x) is int and x > 0 for x in (q, t)) and s.get("officialScore") == q*t:
            result.append(s)
    return result


def pareto(records):
    frontier = []
    for s in sorted(records, key=lambda s: (s["officialMetrics"]["qubits"],
            s["officialMetrics"]["toffoli"], s.get("createdAt", ""), s["id"])):
        if not frontier or s["officialMetrics"]["toffoli"] < frontier[-1]["officialMetrics"]["toffoli"]:
            frontier.append(s)
    return frontier


def compact(s):
    return {k: s.get(k) for k in ("id", "status", "officialScore", "officialMetrics",
            "createdAt", "submissionCommitSha", "solverUsername", "rejectionReason")}


def analyze(records, benchmark):
    scored = eligible(records)
    if not scored:
        raise ValueError("No eligible official records; refusing to invent targets")
    leaders = {
        "qubits": min(scored, key=lambda s: (s["officialMetrics"]["qubits"], s["officialMetrics"]["toffoli"])),
        "toffoli": min(scored, key=lambda s: (s["officialMetrics"]["toffoli"], s["officialMetrics"]["qubits"])),
        "product": min(scored, key=lambda s: s["officialScore"]),
    }
    score = leaders["product"]["officialScore"]
    return {
        "analyzed_at": datetime.now(SGT).isoformat(), "source": API + "/submissions",
        "record_count": len(records), "status_counts": dict(Counter(s.get("status") for s in records)),
        "eligible_count": len(scored), "benchmark_mode": benchmark.get("mode"),
        "closes_at": benchmark.get("closesAt"),
        "eligibility": "Accepted or score-only rejected; positive integer official metrics; score equals Q*T.",
        "leaders": {k: compact(v) for k, v in leaders.items()},
        "our_low_toffoli": compact(min((s for s in scored if s.get("solverUsername") == "MonitSharma"),
            key=lambda s: (s["officialMetrics"]["toffoli"], s["officialMetrics"]["qubits"])))
            if any(s.get("solverUsername") == "MonitSharma" for s in scored) else None,
        "targets": {"maximum_qubits": leaders["qubits"]["officialMetrics"]["qubits"] - 1,
                    "maximum_toffoli": leaders["toffoli"]["officialMetrics"]["toffoli"] - 1,
                    "maximum_product": score - 1,
                    "maximum_toffoli_for_product": {str(q): (score - 1) // q
                        for q in sorted({692, 693, 877, 1170, 1200, 1230, 1234, 1235, 1464}
                            | {s["officialMetrics"]["qubits"] for s in leaders.values()})}},
        "frontier": [compact(s) for s in pareto(scored)],
    }


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def verified_reproduction(receipt):
    """Admit the complete unchanged baseline replay; fail closed on partial evidence."""
    b = receipt.get("product_baseline") or {}
    if b.get("official_harness_unchanged") is not True or b.get("shots") != 9024:
        return None
    if any(type(b.get(k)) is not int or b[k] != 0 for k in
           ("classical_mismatches", "phase_garbage_batches", "ancilla_garbage_batches")):
        return None
    score = b.get("score") or {}
    metrics = score.get("metrics") or {}
    q, t = metrics.get("qubits"), metrics.get("toffoli")
    if not all(type(v) is int and v > 0 for v in (q, t)) or score.get("score") != q*t:
        return None
    if not all(isinstance(b.get(k), str) and len(b[k]) == n and
               all(c in "0123456789abcdef" for c in b[k])
               for k, n in (("source_revision", 40), ("stream_sha256", 64), ("log_sha256", 64))):
        return None
    return metrics


def plot(summary, records):
    from frontier_plot import render, verified_width
    local = verified_width(json.loads((ROOT / "experiments/verification-20261015/independent-verification.json").read_text()))
    if local is None:
        raise ValueError("Local width result lacks complete passing evidence")
    baseline = verified_reproduction(json.loads((ROOT / "docs/data/server-verification.json").read_text()))
    render(summary, eligible(records), baseline, local)


def markdown(summary):
    own = summary.get("our_low_toffoli")
    own_caption = (f'The cyan star marks our officially scored submission `{own["id"][:8]}` '
        f'(Q{own["officialMetrics"]["qubits"]}/T{own["officialMetrics"]["toffoli"]:,}). '
        if own else "")
    rows = ["# Public resource frontier", "", f'Snapshot analyzed {summary["analyzed_at"]} (Singapore time).', "",
        f'[{summary["record_count"]:,} public submissions]({API}/submissions) contain '
        f'{summary["eligible_count"]:,} eligible records and **{len(summary["frontier"])} nondominated resource pairs**.', "",
        "Accepted and explicitly score-only rejected records qualify; failures and claimed-only metrics do not. "
        "This is a dated snapshot, not independent reproduction. Promotion uses the scalar product.", "",
        "![Resource frontier](figures/frontier.png)", "",
        "The gold step is the public frontier. " + own_caption +
        ("It was rejected solely because its product did not improve the scalar leader. "
         if own and own.get("rejectionReason") == "score did not improve current best" else "") +
        "The cyan diamond is our separately verified local Q692 pass; it is not an official submission. "
        "Failed correctness experiments are excluded.", "",
        "![Independent Toffoli and product objectives](figures/record-tradeoffs.png)", "",
        "| Qubits | Rounded mean Toffolis | Product | Submission |", "|---:|---:|---:|---|"]
    for s in summary["frontier"]:
        m = s["officialMetrics"]
        rows.append(f'| {m["qubits"]:,} | {m["toffoli"]:,} | {s["officialScore"]:,} | '
                    f'[{s["id"][:8]}](https://api.ecdsa.fail/api/submissions/{s["id"]}) |')
    rows += ["", "Refresh with `python scripts/analyze-leaderboard.py --refresh --plot`. "
             "Use `--snapshot <directory>` to analyze a saved dated snapshot. "
             "Regenerate both figures offline with `python scripts/frontier_plot.py`. "
             "Compact records, source hashes and targets: [data/latest-leaderboard.json](data/latest-leaderboard.json).", ""]
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    folder = args.snapshot or ROOT / "research-output" / ("public-" + datetime.now(SGT).strftime("%Y%m%d"))
    if args.refresh:
        for filename, endpoint in (("submissions.json", API + "/submissions"), ("benchmark.json", API)):
            with urllib.request.urlopen(endpoint, timeout=60) as response:
                write_json(folder / filename, json.load(response))
    paths = [folder / "submissions.json", folder / "benchmark.json"]
    raw = [p.read_bytes() for p in paths]
    records = json.loads(raw[0])["submissions"]
    summary = analyze(records, json.loads(raw[1])["benchmark"])
    summary["input_sha256"] = {p.name: hashlib.sha256(b).hexdigest() for p, b in zip(paths, raw)}
    write_json(ROOT / "docs/data/latest-leaderboard.json", summary)
    write_json(folder / "summary.json", summary)
    for name, leader in summary["leaders"].items():
        record = next(s for s in records if s["id"] == leader["id"])
        (folder / f"leader-{name}.md").write_text(record.get("note") or "No public note.", encoding="utf-8")
    write_json(ROOT / "docs/data/public-plot-points.json", [compact(s) for s in eligible(records)])
    if args.plot:
        plot(summary, records)
    (ROOT / "docs/frontier-results.md").write_text(markdown(summary), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("record_count", "eligible_count", "leaders", "targets")}, indent=2))


if __name__ == "__main__":
    main()
