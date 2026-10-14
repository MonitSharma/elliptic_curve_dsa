"""Repair shared-clone object paths after extracting the complete workspace.

Uses paths relative to each Git object directory; does not reset or edit sources.
Run with the standard-library Python on the destination before invoking Git.
"""
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def link(object_dir, source):
    if not source.is_dir():
        raise SystemExit(f"Missing object store: {source}. Extract the complete handoff archive.")
    info = object_dir / "info"
    info.mkdir(parents=True, exist_ok=True)
    (info / "alternates").write_text(os.path.relpath(source, object_dir) + "\n")


def main():
    # Restored tracks are normal Git submodules. Their .git files and
    # core.worktree paths are relative and survive moving the whole archive.
    tracks = [ROOT / "agents" / name for name in ("qubits", "toffoli", "product")]
    if all((folder / ".git").is_file() for folder in tracks):
        subprocess.run(["git", "submodule", "sync"], cwd=ROOT, check=True)
        for folder in tracks:
            revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=folder, text=True).strip()
            subprocess.run(["git", "fsck", "--connectivity-only", "--no-dangling"], cwd=folder, check=True)
            print(f"{folder.name}: {revision}, portable submodule accessible")
        return
    if not all((folder / ".git").is_dir() for folder in tracks):
        raise SystemExit("Tracks are missing or mixed. Run git submodule update --init; do not invent Git metadata.")
    # Legacy complete Mac archives used shared standalone clones.
    cache = ROOT / "agents/source-cache.git/objects"
    link(cache, ROOT / ".git/objects")
    subprocess.run(["git", "--git-dir", str(cache.parent), "config", "remote.origin.url",
                    "https://github.com/Layr-Labs/ecdsafail-challenge.git"], check=True)
    for track in ("qubits", "toffoli", "product"):
        folder = ROOT / "agents" / track
        link(folder / ".git/objects", cache)
        subprocess.run(["git", "remote", "set-url", "origin", str(cache.parent)], cwd=folder, check=True)
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=folder, text=True).strip()
        subprocess.run(["git", "fsck", "--connectivity-only", "--no-dangling"], cwd=folder, check=True)
        print(f"{track}: {revision}, shared Git objects accessible")


if __name__ == "__main__":
    main()
