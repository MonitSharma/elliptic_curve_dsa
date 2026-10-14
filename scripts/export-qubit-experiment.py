"""Save the current tracked qubit diff with source hashes and its exact public base."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "agents/qubits"
OUT = ROOT / "experiments/qubits"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base = subprocess.check_output(["git", "-C", str(TRACK), "rev-parse", "HEAD"], text=True).strip()
    names = subprocess.check_output(["git", "-C", str(TRACK), "diff", "--name-only"], text=True).splitlines()
    if any(not name.startswith("src/point_add/") for name in names):
        raise SystemExit("Experimental tracked diff includes protected/out-of-scope files")
    patch = OUT / "compact-reciprocal.patch"
    subprocess.run(["git", "-C", str(TRACK), "diff", "--binary", "--output=" + str(patch)], check=True)
    manifest = {"base_revision": base, "patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
                "source_sha256": {name: hashlib.sha256((TRACK / name).read_bytes()).hexdigest() for name in names},
                "qualification": "Component suite passing; full unchanged-harness candidate evaluation pending. No public submission.",
                "apply_to": "A clean checkout of base_revision only; do not apply twice."}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
