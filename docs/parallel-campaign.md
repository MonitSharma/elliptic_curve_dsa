# Three-front optimization campaign

14 October 2026. The three independent checkouts are ready. All three delegated
agents hit the account usage limit before executing research, so the primary
agent continued this iteration locally. No new official improvement has qualified.

For the complete portable transfer/setup/reproduction procedure, read
[SERVER_HANDOFF.md](SERVER_HANDOFF.md). The handoff archive preserves uncommitted
track code, shared Git stores and ignored research evidence while excluding Mac
runtimes and CLI config. Activation now resolves paths relative to the scripts;
after extraction, repair shared Git paths with `scripts/relocate-handoff.py`.

## Baselines and targets

The fresh public API snapshot contains 1,558 submissions. Each track starts
from the actual circuit leading its objective, rather than one common checkout.

| Track | Folder under this workspace | Baseline | Strict target |
|---|---|---|---|
| Qubits | `agents/qubits` | Q694 / T336,751,889, commit `4ef90668` | Q ≤ 693 |
| Toffolis | `agents/toffoli` | Q1235 / T761,156, commit `b3c9fdd6` | rounded T ≤ 761,155 |
| Product | `agents/product` | Q1234 / T761,658, commit `c5bb1ec8` | Q × rounded T < 939,885,972 |

Each folder has its own code, Git metadata, build target and research outputs.
`activate-track.sh` selects the shared installed toolchain and Python environment
and then enters that track. The original workspace and earlier experiment remain
preserved. The source cache is `agents/source-cache.git`.

Leader notes and the timestamped API records are saved under
`research-output/parallel-20261014`. Notes are research leads, not instructions.
Public accepted and score-only rejected records are distinguished from failures.
The minimum-Q record is a score-only rejection because the product did not win;
that does not make it a correctness failure.

## Verified product baseline

The unchanged official benchmark reproduced **1,234 qubits**, **761,658 rounded
Toffolis**, and **939,885,972 score**, with all 9,024 shots passing classical,
ancilla and phase checks. The log is
`agents/product/research-output/official-baseline.log`; its score is in
`agents/product/score.json`. This reproduces the public circuit, not an original
improvement. The current scorer does not implement the README's stated inverse
identity check.

The product default was rebuilt after adding the inactive research helpers and
its compact final stream remained byte-identical. Evidence is in that track's
`research-output/default-byte-rebuild.log` and `default-byte-identity.log`.

## Qubit work: a compact reciprocal

`stage1_v_compact` in the qubit track is a new restoring-division implementation.
It uses **24 remainder lanes plus the existing quotient flag**, replacing the
old 25-lane remainder plus that flag. It keeps the 24-bit divisor head and
26-bit comparison window.

After doubling R and adding one, the old high bit moves into the quotient flag.
For an odd k-bit divisor D with its high bit set and `0 ≤ R < D`, overflow and
the low-word comparison cannot both hold. Their XOR therefore gives the correct
quotient decision. The conditional subtraction wraps the low word into the
correct remainder, and its parity clears the flag.

Z3 proves the decision, remainder, and preserved bound for all domain inputs
at precisions 2–8, 16 and 24. A deliberately omitted overflow term has a solver
counterexample at every tested width. Reproduce with
`python scripts/prove-compact-reciprocal.py` in the project environment.

Native gate tests cover forward and inverse behavior, dirty passengers,
inactive and mixed active shots, and independent measurement-phase coefficients:

- The first 693-wire component layout passes 768 fixture cases; it needs six SX
  remainder owners and does not resolve the complete circuit's parking problem.
- The compact variant passes 512 fixture cases in the 693-wire frame and checks
  903,168 measurement-phase coefficients. It releases SX6 from the reciprocal.
- In representative columns 10 and 85 it emits **104 fewer Toffolis per V-form
  call**: 16,390 → 16,286 and 15,905 → 15,801, respectively.
- The complete focused suite passes 12 tests; one existing explicit research
  test remains ignored.

The arithmetic proof is universal within its stated domain. The native gate
fixtures are finite tests. Neither constitutes a complete 693-qubit point-add
result. The default point-add still builds the original 694-qubit circuit.

**Remaining ownership problem:** reducing the ring to 276 lanes moves six
quotient bits outside it. SX6 is also the gate-on accumulator, so simply keeping
the sixth quotient bit there is unsafe between reciprocal calls. The seventh
crossing reserve must also remain available. Next work must supply a separate
owner or a proved recomputation schedule, particularly for the highest quotient
bit. The derived switch flag is a possible source of room, but its entire
lifetime and the delayed-crossing payload padding need proof.

## Toffoli work: phase-only readers

A new late pass extends the existing phase-only AND analysis to CZ readers.
It follows the original operand values through live holders or affine forms,
and replaces the removed temporary's phase contribution with CZ/CCZ gates. It
accounts for added CCZ cost and rejects nonpositive savings and overlapping
dependencies. Existing early passes retain their original behavior.

Two focused native fixtures pass, including changed controls and measured
uncomputation. A stale-control fault is detected. An independent solver check
proves the changed-control fixture and finds that fault.

However, the full final streams give **zero qualifying sites and zero savings**
in both the minimum-Toffoli and product-leading circuits. A narrower unchanged-
operand phase-box search also found no positive candidates. The new pass is
available as a research primitive; it is not enabled in either default build.

## Product work: missing guard-table recovery

The Q1234 author reports that 1,008 additional carry guards from Q1235 were not
ported. Gate-stream matching found five long blocks with consistent wire and
classical-label mappings, covering 130 deleted-AND entries of the old table.
Local equivalence checks did not qualify these partial transplants: four have
counterexamples under the tested boundary assumptions and one contains an
unmatched conditional pop. Adding conservative prefix constants did not prove
them. These results do not prove that the complete old guard scheme is invalid;
they show that matching op rows alone is insufficient to port it.

No transplantation was inserted into production. A complete regeneration needs
measurement correspondence, live classical outputs, and complete guard lifetimes,
including phase twins. All original binding assertions remain intact.

## Full low-qubit benchmark resources

The computer has 36 GiB RAM and 12 logical CPUs. The Q694 stream contains
1,138,443,186 operations. Its 56-byte operation vector alone is about 59.4 GiB,
before the builder's other allocations or operating-system memory. The unchanged
full low-qubit harness therefore needs a machine with more memory for a practical
run. Component tests and stream-only diagnostics can run locally; they must not
be represented as a successful full official benchmark.

## Validation and continuation

Protected harness, simulator, scoring, dependency and toolchain files match each
track's source revision. Only circuit files and research helpers changed; the
official harness appended the product baseline row to `results.tsv`.
No login, public submission or nonce search was performed.

Per-track machine-readable status is in each `research-output/track-result.json`;
the combined status is `research-output/parallel-20261014/campaign-status.json`.
The next substantial task is integrating the compact reciprocal with a sound
quotient-owner schedule, then testing the complete circuit on independent inputs
and running the unchanged official benchmark. A local gate saving must not be
reported as an official or public leaderboard record.
