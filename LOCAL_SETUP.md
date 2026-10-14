# Local setup

This recovered checkout is on **Windows**, not the earlier Mac. The Mac runtimes,
virtual environment, benchmark streams and uncommitted track helpers are absent.
Historical instructions are preserved under `docs/archive/`.
The current desktop has an i7-12700K, 20 logical CPUs and about 31.7 GiB RAM;
only about 6.4 GiB was free at inspection. The low-width operation vector alone
exceeds local RAM. See `docs/data/local-machine.json`.

## Restore the public tracks

```powershell
git submodule update --init --jobs 3
git submodule status
```

The pins are public source revisions. Submodule initialization never recreates
ignored files or uncommitted research. Use `scripts/audit-workspace.py` to see
what is missing. Do not run the legacy relocation script against these submodules.

## Python research on Windows

This session uses the desktop app's bundled Python 3.12.14 to create an isolated
`.venv-research`. Its interpreter is:

```powershell
& .venv-research/Scripts/python.exe scripts/audit-workspace.py
& .venv-research/Scripts/python.exe scripts/test_leaderboard.py
& .venv-research/Scripts/python.exe scripts/analyze-leaderboard.py --refresh --plot
& .venv-research/Scripts/python.exe scripts/prove-compact-reciprocal.py
```

On another machine with Python installed:

```powershell
python -m venv .venv-research
& .venv-research/Scripts/python.exe -m pip install matplotlib==3.11.2 z3-solver==5.1.0.0
```

The earlier `requirements-research.txt` remains a historical Mac lockfile. The
current research environment is recorded in `docs/data/research-environment.txt`.
These optional packages do not alter the challenge's protected Cargo dependencies.

## Circuit compilation and official scoring

Use [the Linux CPU server](docs/SERVER_HANDOFF.md). No local Rust compiler was
found on this Windows machine. Native benchmark execution on Windows has not
been qualified; the official shell harness runs on Linux.

On Linux with the pinned toolchain installed:

```bash
cd agents/product
export CARGO_BUILD_JOBS=4
cargo +1.93.0 fetch --locked
bash ./benchmark.sh --note "Exact candidate description"
```

For focused qubit component checks:

```bash
cd agents/qubits
CARGO_BUILD_JOBS=4 cargo +1.93.0 test --release --locked --offline \
  --bin build_circuit tests_midg_k24 -- --nocapture
```

Keep research changes in a patch under `experiments/` as well as the submodule
working tree. A root-repository commit cannot preserve uncommitted submodule
files. Public submission candidates must be built from their exact final source
and checked with the unchanged harness.
