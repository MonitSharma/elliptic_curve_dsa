"""Save source, Git histories and research evidence without machine runtimes or credentials."""
from pathlib import Path
import hashlib
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handoff"
EXCLUDED = {".tools", ".venv", "target", "__pycache__", ".ipynb_checkpoints", "handoff"}


def selected(path):
    rel = path.relative_to(ROOT)
    return not (any(part in EXCLUDED for part in rel.parts) or path.name in {".DS_Store", "HANDOFF_FILE_SHA256.json"})


def main():
    OUT.mkdir(exist_ok=True)
    archive = OUT / "ecdsa-server-handoff-20261014.tar.gz"
    paths = sorted(p for p in ROOT.rglob("*") if p.is_file() and selected(p))
    checksums = {}
    with tarfile.open(archive, "w:gz", compresslevel=1) as tar:
        for path in paths:
            if path.is_symlink():
                raise SystemExit(f"Unexpected file symlink: {path}; inspect before transfer.")
            rel = path.relative_to(ROOT).as_posix()
            digest = hashlib.sha256()
            with path.open("rb") as source:
                while chunk := source.read(1024 * 1024):
                    digest.update(chunk)
            checksums[rel] = digest.hexdigest()
            tar.add(path, arcname="ecdsa/" + rel, recursive=False)
        import io
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
