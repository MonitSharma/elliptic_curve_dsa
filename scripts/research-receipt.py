"""Preserve source and terminal evidence without admitting partial runs as scores.

Run in an experiment environment; diagnostic and full-benchmark receipts are
explicitly distinguished. Generated results.tsv is recorded separately from
the candidate patch. No checkout files are modified.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(checkout, *args):
    return subprocess.check_output(["git", "-C", str(checkout), *args])


def collect(checkout, evidence, log_path=None, exit_path=None, stream_path=None,
            score_path=None, full_benchmark=False):
    checkout = checkout.resolve()
    evidence = evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    revision = git(checkout, "rev-parse", "HEAD").decode().strip()
    patch = git(checkout, "diff", "--binary", "HEAD", "--", "src/point_add/")
    (evidence / "candidate.patch").write_bytes(patch)
    changed = git(checkout, "diff", "--name-only", "HEAD").decode().splitlines()
    untracked = git(checkout, "ls-files", "--others", "--exclude-standard").decode().splitlines()
    # New contestant files must be included, without altering the Git index.
    for name in untracked:
        if name.startswith("src/point_add/"):
            proc = subprocess.run(["git", "diff", "--no-index", "--binary", "--",
                                   "/dev/null" if __import__("os").name != "nt" else "NUL", name],
                                  cwd=checkout, capture_output=True)
            if proc.returncode not in (0, 1):
                raise RuntimeError(proc.stderr.decode(errors="replace"))
            patch += proc.stdout
    (evidence / "candidate.patch").write_bytes(patch)
    source_files = sorted(set(name for name in changed + untracked if name.startswith("src/point_add/")))
    protected_changes = [name for name in changed if not name.startswith("src/point_add/") and name != "results.tsv"]
    receipt = {
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "checkout": str(checkout), "baseline_revision": revision,
        "candidate_patch_sha256": hashlib.sha256(patch).hexdigest(),
        "source_sha256": {name: sha256(checkout / name) if (checkout / name).is_file() else None
                          for name in source_files},
        "protected_tracked_changes": protected_changes,
        "generated_results_tsv_changed": "results.tsv" in changed,
        "other_untracked_files": [name for name in untracked if not name.startswith("src/point_add/")],
        "evidence_kind": "unchanged_full_benchmark" if full_benchmark else "research_diagnostic",
        "status": "pending", "qualified_score": None,
    }
    for name in ("benchmark.sh", "Cargo.toml", "Cargo.lock", "rust-toolchain", "src/bin/eval_circuit.rs",
                 "src/bin/build_circuit.rs", "src/circuit.rs", "src/sim.rs", "src/weierstrass_elliptic_curve.rs"):
        path = checkout / name
        if path.is_file():
            receipt.setdefault("protected_sha256", {})[name] = sha256(path)
    if stream_path and stream_path.is_file():
        receipt["stream"] = {"path": str(stream_path.resolve()), "sha256": sha256(stream_path),
                             "bytes": stream_path.stat().st_size}
    log = ""
    if log_path and log_path.is_file():
        receipt["log"] = {"path": str(log_path.resolve()), "sha256": sha256(log_path)}
        log = log_path.read_text(encoding="utf-8", errors="replace")
    exit_status = None
    if exit_path and exit_path.is_file():
        exit_status = int(exit_path.read_text().strip())
        receipt["exit_status"] = exit_status
        receipt["status"] = "failed" if exit_status != 0 else "completed_diagnostic"
    score = None
    if score_path and score_path.is_file():
        receipt["score_file_sha256"] = sha256(score_path)
        score = json.loads(score_path.read_text())
    complete = re.search(r"all\s+9,?024\s+shots OK", log) is not None
    failure_counts = {}
    for label, key in (("classical mismatches", "classical_mismatches"),
                       ("phase-garbage batches", "phase_garbage_batches"),
                       ("ancilla-garbage batches", "ancilla_garbage_batches")):
        matches = re.findall(re.escape(label) + r"\s*:\s*(\d+)", log)
        failure_counts[key] = int(matches[-1]) if matches else None
    receipt["failure_counts"] = failure_counts
    metrics = score.get("metrics", {}) if isinstance(score, dict) else {}
    q, t = metrics.get("qubits"), metrics.get("toffoli")
    valid_score = type(q) is int and type(t) is int and q > 0 and t > 0 and score.get("score") == q * t
    if full_benchmark and exit_status == 0 and complete and all(value == 0 for value in failure_counts.values()) \
            and valid_score and not protected_changes and receipt.get("stream"):
        receipt["status"] = "locally_qualified_full_benchmark"
        receipt["qualified_score"] = score
        receipt["limitations"] = "Finite unchanged benchmark qualification; not an all-input proof or official platform score."
    elif full_benchmark and exit_status == 0:
        receipt["status"] = "incomplete_or_inadmissible_evidence"
    (evidence / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--exit", dest="exit_path", type=Path)
    parser.add_argument("--stream", type=Path)
    parser.add_argument("--score", type=Path)
    parser.add_argument("--full-benchmark", action="store_true")
    args = parser.parse_args()
    receipt = collect(args.checkout, args.evidence, args.log, args.exit_path,
                      args.stream, args.score, args.full_benchmark)
    print(json.dumps({key: receipt[key] for key in ("status", "baseline_revision",
                      "candidate_patch_sha256", "protected_tracked_changes", "qualified_score")}, indent=2))


if __name__ == "__main__":
    main()
