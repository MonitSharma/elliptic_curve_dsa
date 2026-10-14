"""Save source, Git histories and research evidence without machine runtimes or credentials."""
from pathlib import Path
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import tarfile
import io

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handoff"
EXCLUDED = {".tools", "target", "__pycache__", ".ipynb_checkpoints", "handoff", "source-cache.git"}


def selected(path):
    rel = path.relative_to(ROOT)
    return not (any(part in EXCLUDED or part.startswith(".venv") for part in rel.parts)
                or path.name in {".DS_Store", "HANDOFF_FILE_SHA256.json"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", help="Archive basename (without directories)")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
    name = args.name or f"ecdsa-server-handoff-{stamp}.tar.gz"
    if Path(name).name != name or not name.endswith(".tar.gz"):
        raise SystemExit("--name must be a .tar.gz basename")
    archive = OUT / name
    if archive.exists():
        raise SystemExit(f"Refusing to overwrite existing evidence: {archive}")
    paths = sorted(p for p in ROOT.rglob("*") if p.is_file() and selected(p))
    checksums = {}
    with tarfile.open(archive, "w:gz", compresslevel=1) as tar:
        for path in paths:
            if path.is_symlink():
                raise SystemExit(f"Unexpected file symlink: {path}; inspect before transfer.")
            rel = path.relative_to(ROOT).as_posix()
            # Windows checkout CRLF is not part of the canonical shell source.
            # Normalize only shell scripts in the archive, never source/evidence
            # in the working tree. Manifest hashes refer to archived bytes.
            if path.suffix == ".sh":
                payload = path.read_bytes().replace(b"\r\n", b"\n")
                checksums[rel] = hashlib.sha256(payload).hexdigest()
                info = tar.gettarinfo(str(path), arcname="ecdsa/" + rel)
                info.size = len(payload)
                tar.addfile(info, io.BytesIO(payload))
                continue
            digest = hashlib.sha256()
            with path.open("rb") as source:
                while chunk := source.read(1024 * 1024):
                    digest.update(chunk)
            checksums[rel] = digest.hexdigest()
            tar.add(path, arcname="ecdsa/" + rel, recursive=False)
        payload = (json.dumps(checksums, indent=2) + "\n").encode()
        info = tarfile.TarInfo("ecdsa/HANDOFF_FILE_SHA256.json")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    digest = hashlib.sha256()
    with archive.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    (OUT / (archive.name + ".sha256")).write_text(f"{digest.hexdigest()}  {archive.name}\n")
    print(json.dumps({"archive": str(archive), "bytes": archive.stat().st_size, "files": len(paths), "sha256": digest.hexdigest(), "excluded": sorted(EXCLUDED)}, indent=2))


if __name__ == "__main__":
    main()
