# Compact reciprocal on the public Q693 baseline

Base revision: `c95b9325913abacca9c86bdebad10a20633cd04e`.
The accompanying `compact-reciprocal.patch` contains the complete local change,
including the production integration and finite native tests. Preserve it when
transferring this repository: uncommitted submodule files do not travel with a
root Git commit.

Apply only to a clean checkout of that exact public source:

```bash
git -C agents/qubits apply --check ../../experiments/qubits/compact-reciprocal.patch
git -C agents/qubits apply ../../experiments/qubits/compact-reciprocal.patch
```

Do not apply it again to this session's already-modified working tree.
The focused suite passes 17 tests (one existing research test remains ignored).
The full candidate finished on `smu_server` and **failed** its 9,024-shot packet:
6 classical mismatches, 3 phase-garbage batches and 6 ancilla-garbage batches.
The first reported mismatch is shot 1170. It has no qualified score and is not
ready to submit. The patch is preserved for diagnosis, not as a validated full
circuit improvement. See `docs/data/qubit-experiment.json` for the receipt.

The [outcome report](../../docs/experiment-outcomes.md) records what worked and
what failed, including the diagnostic cost chart. Regenerate that research-only
chart with `python scripts/plot-research-progress.py`; it is excluded from README
result plots.

The new k-lane remainder stores overflow in the existing quotient flag, uses a
virtual leading-one comparator, and appends the dividend one **after** the zero
carry-in comparison. The first implementation's premature append failed at
`k=2, D=3, R=1`; that defect is fixed and retained in the research log.

Precision, comparison width, quotient cap, map envelope, crossing reserve and
the inherited nonce remain unchanged. No test-packet tuning was performed.
See [the research plan](../../docs/research-plan.md) for results and proof limits.
