"""Verify extracted files before relocation or editing, using only stdlib Python."""
from pathlib import Path
import argparse
import hashlib
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Verify an archive in place, without extraction")
    args = parser.parse_args()
    if args.archive:
        with tarfile.open(args.archive, "r:gz") as archive:
            members = archive.getmembers()
            names = [m.name for m in members]
            if len(names) != len(set(names)):
                raise SystemExit("Duplicate archive members")
            expected = json.load(archive.extractfile("ecdsa/HANDOFF_FILE_SHA256.json"))
            failures = []
            for name, checksum in expected.items():
                if Path(name).is_absolute() or ".." in Path(name).parts:
                    raise SystemExit(f"Unsafe manifest path: {name}")
                member = archive.getmember("ecdsa/" + name)
                if not member.isfile():
                    raise SystemExit(f"Unexpected non-file member: {name}")
                digest = hashlib.sha256()
                with archive.extractfile(member) as source:
                    while chunk := source.read(1024 * 1024):
                        digest.update(chunk)
                if digest.hexdigest() != checksum:
                    failures.append(name)
            if failures:
                raise SystemExit("Changed archive files: " + ", ".join(failures))
            print(f"Verified {len(expected)} archived files without extraction.")
        return
    manifest = ROOT / "HANDOFF_FILE_SHA256.json"
    expected = json.loads(manifest.read_text())
    failures = []
    for name, checksum in expected.items():
        if Path(name).is_absolute() or ".." in Path(name).parts:
            raise SystemExit(f"Unsafe manifest path: {name}")
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
