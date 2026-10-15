# Independent audit of the saved value-failure trace

15 October 2026. Local analysis of saved evidence, not a new circuit run.
**No qualified score or candidate repair.** Original experiment files are preserved.

## Confirmed and corrected results

The full compressed log has 186 completed value-failure cases and 256 completed
independent controls. Both families report observer equality with the protected
simulator. The patch and packet hashes match their manifest; reconstructing the
186-case packet from the census replay reproduces it byte for byte. Every selected
case failed values under all 32 recorded measurement seeds. The saved final stream
hash matches the parent and the saved run exit is zero. The large stream itself
is not stored here and was not rehashed locally.

The first-event counts remain 83 divide rail violations, 72 multiply rail
violations, and 31 failures with no observed event. All 256 controls pass and have
no events. No unmatched-reverse warning is present.

The previous analyzer has two bugs:

1. It keys events by shot number alone, merging families. This does **not** change
   this run's counts because the independent family has no events.
2. It accepts zero as a power of two (`mag & (mag - 1) == 0`). This **does** change
   the reported diagnosis: among 155 first forward violations, only **98** have a
   nonzero power-of-two target delta, **55** have zero target delta, and **2** have
   other nonzero target deltas. The reported 153 power-of-two errors included all
   55 zero deltas.

There are 82 target-labelled and 73 source-labelled violations. A source label
takes precedence when both rails are wrong. Consequently, 55 source-labelled
cases have a correct target and 18 have both rails wrong. This observer does not
record source deltas, so their sizes cannot be inferred from the target delta.

The 31 cases without events remain **unlocalized**. Absence of a detected rail
violation is not proof that the root cause is outside the walk: tape correctness,
unmarked operations and other invariants are not all covered by these checks.
Likewise, a power-of-two delta is compatible with truncation but does not by itself
prove that the expected value exceeds the available signed range.

## Artifacts and checks

- [Corrected analysis](result.json), [provenance checks](evidence-verification.json).
- [Analyzer](analyze.py) preserves family identity and rejects incomplete shot,
  event and completion records. It tests both rail deltas when enriched events
  are available and checks expected-value representability in signed or parked-low
  rail encodings.
- [Thirteen regression tests](tests.log) pass, including zero magnitude, family
  collisions, incomplete logs, signed limits and parked-low parity.
- [Prepared observer patch](observer-detail.patch) adds both rail deltas and their
  expected and observed values. It changes no gate-building code. This follow-up
  is **not compiled or executed**; see [manifest](probe-manifest.json).

Reproduce from the repository root:

```text
.venv-research/Scripts/python.exe experiments/trace-audit-20261015/analyze.py experiments/trace-value-20261015/evidence/trace.log.gz experiments/trace-audit-20261015/result.json
.venv-research/Scripts/python.exe experiments/trace-audit-20261015/verify_evidence.py
.venv-research/Scripts/python.exe experiments/trace-audit-20261015/prepare_probe.py
```

## Next experiment

A separate [exact fold-boundary derivation](FOLD-BOUNDARY.md) now identifies
the signed correction for the earlier equal-input division counterexample.
It passes 16,384 Boolean quotient-core combinations and 524,288 exhaustive
integer-model cases, reproducing both saved production widths. This is an
algebraic repair design, not a compiled quantum repair or scored result.

Run the enriched observer in a new isolated copy on the unchanged packets. Preserve
the old observer; verify compilation, protected simulator equality and final stream
identity. Separate unrepresentable expected targets, unrepresentable sources and
representable-but-corrupted values before choosing an envelope or arithmetic repair.
The existing trace supports prioritizing rail failures, while the precise mechanism
still needs these observations. Any repair then requires independent census and
the unchanged official benchmark; these diagnostic counts are not resource records.

Server access was not retried after automatic approval review reported a usage
limit. The rejected request was not executed and was not classified as unsafe.
This work used only local saved evidence.
