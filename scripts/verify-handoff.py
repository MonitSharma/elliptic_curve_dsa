"""Verify extracted files before relocation or editing, using only stdlib Python."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = ROOT / "HANDOFF_FILE_SHA256.json"
    expected = json.loads(manifest.read_text())
    failures = []
    for name, checksum in expected.items():
        path = ROOT / name
        if not path.is_file():
            failures.append(f"missing: {name}")
            continue
        digest = hashlib.sha256()
        with path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
        if digest.hexdigest() != checksum:
            failures.append(f"changed: {name}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Verified {len(expected)} files. Relocation and environment recreation can proceed.")


if __name__ == "__main__":
    main()
