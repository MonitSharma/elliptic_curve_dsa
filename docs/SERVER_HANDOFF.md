# CPU server: working ECDSA environment

**Active overnight cycle, 15 October 2026 Singapore:** use
[the cycle report](overnight-20261014.md) and its source-bound experiment receipts
for current jobs. The capacity and compact-Q693 completion details below describe
the earlier setup, before this cycle's separate N275 and head-selector work.
The new full evaluator uses about200GiB; a sequential second evaluator waits
for its terminal marker before allocating about183GiB. Preserve both streams
and refresh available memory before launching anything else.

Verified on 14 October 2026 via SSH alias **`smu_server`**. Hostname:
`LHC-104-070`. ECDSA work is isolated at **`/home/hclau/ecdsa_research`**.
The pre-existing `/home/hclau/quantum_chemistry` checkout and active jobs were
inspected and left untouched.

## Capacity and limits

Observed: 144 logical CPUs, 503 GiB RAM, approximately 277 GiB available, 4.7 TiB
free disk, and load around 35–36. Two active jobs each use about 18 CPU threads
and together roughly 210 GiB RAM. Neither Slurm's `squeue` nor `qstat` was found.
These are observations, not permanent reservations; refresh before each launch.

Use four build threads initially and one numerical-library thread. The product
baseline's full benchmark peaked at about **4.03 GiB RSS** under a 16 GiB process
virtual-memory limit. The Q693 stream has 1,128,700,062 operations; its 56-byte
vector alone is approximately **58.9 GiB**, before copies and builder overhead.
Use one low-width full benchmark at a time, plan conservatively for 128 GiB and
measure actual memory. The official scorer is sequential across its batches.

## Installed and reproduced

- Rust **1.93.0**, installed alongside the pre-existing stable toolchain.
- GCC and Python **3.12.3**; isolated `.venv` with Z3 **5.1.0.0**.
- Independent public worktrees: `product` (`c5bb1ec8`), `toffoli` (`b3c9fdd6`),
  `qubits` (`c95b9325`), sharing the `upstream` Git repository.
- Unchanged product benchmark: **Q1234/T761,658/product939,885,972**, all 9,024
  shots passing, stream SHA256
  `49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4`.
- Public Q693 focused K24 suite: 14 passing tests, one existing ignored test,
  before adding the new experiment.

That reproduced product base is now historical: the refreshed public leader is
`143731ef`, Q1234/T761,492/product939,681,128. The server worktree remains on the
reproduced c5bb1ec8 source until a deliberate, separately verified rebase.

The server lacks bubblewrap. The unchanged benchmark used its documented local
development fallback; this replay is not an official platform evaluation.
Evidence: [verification receipt](data/server-verification.json). Full logs are
under `research-output/server-20261014/` locally and `logs/` on the server.

## Inspect and resume

```bash
ssh smu_server
cd /home/hclau/ecdsa_research
python3 server-preflight.py
cat logs/product-baseline.exit
cat logs/product-baseline-score.json
tail -30 logs/compact-fixed.log
```

Each long job runs with `nohup`, a dedicated log and a recorded PID. Check both
the process and exit marker; a stale PID alone does not establish a live job.
At the 14 October 2026 17:31 Singapore inspection, the parent job was PID
2277715 and trusted scorer PID2283149. Both were detached from a terminal and
ignored SIGHUP; the scorer used about 59 GiB RSS and one CPU core. It was executing
the unchanged `eval_circuit` over 9,024 shots. It exposes no reliable batch
progress or completion estimate. Check the receipt for the latest observation.
The setup, baseline and compact-candidate jobs are complete. The compact
candidate's build succeeded but full validation **failed** after all 9,024 shots:
6 classical mismatches, 3 phase-garbage batches and 6 ancilla-garbage batches.
Exit status is 1; no valid score was produced. The first mismatch was shot 1170.
The full benchmark took 38:17.50 and peaked at about 59.7 GiB RSS. Its job
processes have exited; no ECDSA calculation is currently running.
The 203-column integration fixture passed with a 64 GiB allocation allowance
(19.2 GiB measured RSS), which is narrower evidence than this failing full run.
New experimental jobs and outcomes are documented in
[the research plan](research-plan.md) and [receipt](data/qubit-experiment.json).
The terminal log, exit marker and stream hash are preserved. The
`ECDSA benchmark follow-up` automation is paused after collecting the result.
The next calculation should diagnose the failed packet against the unchanged
base; do not rerun or submit the current failed candidate as a validated result.

For a new fully prepared candidate, use the unchanged track benchmark after
inspecting jobs, available memory, source revision and working-tree status:

```bash
cd /home/hclau/ecdsa_research/qubits
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH
mkdir -p ../logs
nohup /usr/bin/time -v bash ./benchmark.sh --note "Exact verified candidate" \
  > ../logs/qubits-candidate.log 2>&1 < /dev/null &
echo $! > ../logs/qubits-candidate.pid
```

Do not run another full stream job concurrently or overwrite existing evidence.
An integrated candidate must preserve all quotient owners, delayed-crossing pad
lanes, seven crossing-reserve lanes, precision and measurement phase semantics.
An isolated fixture is not a record.

## Transfer and preservation

The obsolete Mac shared-clone relocation procedure is archived at
`docs/archive/server-handoff-mac-20261014.md`. Fresh recovery uses pinned public
submodules, plus tracked experiment patches. To transfer this working tree and
ignored evidence, use `scripts/create-handoff.py`; runtimes and build caches are
excluded. Research patches, raw logs, stream hashes and compact receipts must
travel with the source. Shell scripts are normalized to canonical LF in the
archive; manifest hashes describe those archived bytes. The source working tree
is not rewritten. Recreate runtimes on the destination.
