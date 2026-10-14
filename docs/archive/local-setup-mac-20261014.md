# Archived pre-recovery document

This describes the earlier Mac workspace. Referenced ignored artifacts and uncommitted track changes were not transferred. Use the current root README and setup documentation.

# Local setup and portable activation

For moving to another computer/CPU server, use [docs/SERVER_HANDOFF.md](docs/SERVER_HANDOFF.md).
The current Mac environment is installed locally; server runtimes must be recreated.

## This Mac

From the workspace root:

```bash
source ./activate.sh
cargo --version
python -c 'import numpy, z3; print(numpy.__version__, z3.get_version_string())'
./scripts/benchmark-local.sh --note "Describe the experiment"
```

Activation supports bash and zsh and resolves paths from its own location. It
selects the root virtual environment, Rust1.93.0 and root `target/`. When the
project-local Rust installation exists it uses `.tools/cargo` and `.tools/rustup`;
otherwise it sources the destination's existing rustup environment. It does not
change shell startup files. CLI config stays under `.tools/config`.

For a separate track:

```bash
source agents/qubits/activate-track.sh
# Other terminals can select agents/toffoli or agents/product instead.
```

Track activation changes directory and selects that track's `target/`. Each track
has independent code/build outputs; dependencies are shared. Always activate from
a known workspace location or use the script's full path after changing directories.

## Installed tools

- Rust1.93.0, matching `rust-toolchain`, and a C linker.
- Python3.13.7 with NumPy, pandas, Matplotlib, ipykernel and Z3-solver5.1.0.0.
- Bun1.4.3 and the official ecdsafail CLI v2026.10.13-1 on this Mac.
- `requirements-research.txt`: pinned Python versions; recreate this environment
  rather than moving the existing `.venv` across operating systems.
- The CLI is optional for direct local benchmarks. Installation/authentication
  on a new machine are separate from source transfer.

## Benchmark interpretation

The official `./benchmark.sh` builds the untrusted circuit generator, confines it,
then validates `ops.bin` in the trusted scorer. All9,024 shots must pass output,
phase and ancilla checks. Score = rounded mean executed T × peak logical Q.
The scorer does not implement the archived README's forward/reverse identity test.
Use separate inverse/population checks; a passing canonical packet is not a
universal-correctness proof for inherited approximate arithmetic.

The root baseline is Q1235/T761156/product940027660. The product track reproduces
Q1234/T761658/product939885972. No original improvement has qualified. Low-Q
component fixtures must not be confused with full point-add verification.

Edit only `src/point_add/` for candidate submissions. Preserve the harness, scorer,
simulator, Cargo dependencies/toolchain and prefix bindings. Let the harness append
`results.tsv`. Research helpers/documentation are outside contestant scope.

## Transfer

```bash
python3 scripts/create-handoff.py
```

The archive under `handoff/` includes source, shared Git stores and ignored research
evidence. It excludes `.tools`, `.venv`, `target/` and caches. This omits CLI credentials
and incompatible binaries. On the destination, verify files, repair Git object paths
with `scripts/relocate-handoff.py`, then recreate the environment as documented in
[SERVER_HANDOFF.md](docs/SERVER_HANDOFF.md). The low-Q operation vector alone is
59.4GiB; use a suitably provisioned server for the complete unchanged benchmark.
