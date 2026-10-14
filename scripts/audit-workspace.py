"""Audit source includes, restored tracks and missing legacy research artifacts."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LEGACY = [
    "HANDOFF_FILE_SHA256.json",
    "research-output/parallel-20261014/campaign-status.json",
    "research-output/parallel-20261014/proof-candidates.json",
    "research-output/parallel-20261014/square-match-blocks.json",
    "research-output/optimization-baseline/ops.bin",
    "research-output/cleanup-v1-ops.bin",
    "research-output/canonical-inheritance.json",
    "agents/qubits/activate-track.sh",
    "agents/qubits/research-output/k24-compact-tests.log",
    "agents/product/src/point_add/tests_phase_readers.rs",
    "agents/product/research-output/default-byte-identity.log",
    "agents/product/research-output/pre-extra-guards.u32",
    "agents/toffoli/src/point_add/tests_phase_readers.rs",
    "agents/toffoli/research-output/final.u32",
]


def git(folder, *args):
    return subprocess.check_output(["git", "-C", str(folder), *args], text=True).strip()


def main():
    result = {"audited_at": datetime.now(timezone.utc).isoformat(), "tracks": {},
              "missing_source_includes": [], "missing_legacy_artifacts": []}
    folders = [ROOT] + [ROOT / "agents" / name for name in ("qubits", "toffoli", "product")]
    for folder in folders:
        name = "." if folder == ROOT else folder.relative_to(ROOT).as_posix()
        try:
            result["tracks"][name] = {"revision": git(folder, "rev-parse", "HEAD"),
                                      "branch": git(folder, "branch", "--show-current")}
        except subprocess.CalledProcessError:
            result["tracks"][name] = {"error": "Checkout unavailable; run git submodule update --init"}
        for source in (folder / "src").rglob("*.rs"):
            for match in re.finditer(r'include_(?:bytes|str)!\(\s*"([^"]+)"\s*\)', source.read_text(encoding="utf-8")):
                included = source.parent / match[1]
                if not included.is_file():
                    result["missing_source_includes"].append({"source": source.relative_to(ROOT).as_posix(), "include": match[1]})
    result["missing_legacy_artifacts"] = [p for p in LEGACY if not (ROOT / p).exists()]
    result["interpretation"] = "Legacy claims remain unverified where their artifacts were not transferred. Public sources do not recover uncommitted research."
    destination = ROOT / "docs/data/workspace-audit.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["missing_source_includes"] or any("error" in r for r in result["tracks"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
