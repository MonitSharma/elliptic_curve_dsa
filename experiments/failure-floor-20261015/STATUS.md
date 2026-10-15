# Failure-floor localization: all 31 cases now attributed

15 October 2026, night. **New source-bound diagnosis; no repaired circuit,
qualified resource result, nonce search, or submission.**

The 31 saved wide-circuit value failures that previously had no observed walk
rail event now have directly observed incorrect arithmetic transitions:

| First observed faulty arithmetic | Inputs | Mechanism |
|---|---:|---|
| Divide payload, forward Y15 fold | 17 | Signed carry discarded across the 56/57-bit fold window: 16 borrows and one positive overflow |
| Multiply payload, reverse Y15 fold | 12 | Positive carry discarded across the 56-bit fold window; every output error is exactly −2^56 |
| Square, merged C-product windows | 2 | One input loses a carry at bit 156; the other first loses a borrow at bit 154 and then a carry at bit 156 |

This replaces “unlocalized” for these particular 31 inputs. It does not establish
that every fresh failure has the same cause, and it does not prove universal
correctness of unobserved intermediate invariants.

## Source and verification

This study uses the **unsmoothed wide parent** from
`dynamic-pool-20261015/wide-b3`, based on B3 commit
`b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7`. It is **not** our officially
scored smoothed nonce-375 circuit. Their failure rates must not be interchanged.

The observation copy is a new detached worktree at
`/home/hclau/ecdsa_research/failure-floor-20261015/observer-b3`.
Instrumentation changes only `src/point_add/`, records operation indices and
wire identities, and emits no gates. Its final stream remains exactly:

`95e771bae57bd96e75c11b569faf2f87cd7dfa52b227b40dd16e40a301d8e122`.

On all 31 failing inputs and all 256 independent controls, the observer equals
the unchanged protected simulator in every quantum word, classical bit, phase
and executed Toffoli count. All 31 saved inputs still fail final values. All
256 controls pass, with zero payload, fold-boundary, square-window or stage
events. Seventeen tracked protected files match the B3 base byte for byte.

The observer now covers ordinary fused forward/reverse ticks, payload-only
ticks, terminal kernels and the optimized initial tick. Inverse tape values
are sampled before popped tape wires can be released/reused. It also reads
the actual forward/reverse fold input wires and checks every observed fold's
output window against the exact signed equation. The 29 physical fold
boundaries match the independently reconstructed whole-tick model exactly.

## Fold equations and possible exact control

Let `f=2^32+977`, `p=2^256−f`, `s=3+extra`, `w` the fold width,
`E=floor(X/2^256)`, `L=X mod 2^256`, and `Nm` the weighted complemented-source
sign bits. Forward:

```text
A = L + E + (E−Nm)(f−1)
m = A / f mod 2^s
C = E + (E−Nm−m)(f−1)
c = floor(((L mod 2^w)+C)/2^w)
correct output = observed output + c·2^(w−s) mod p
```

Reverse, with `W=ROL256(entry_target,s)` and complemented inverse signs:

```text
m = W mod 2^s
C = E + (E−Nm+m)(f−1)
c = floor(((L mod 2^w)+C)/2^w)
correct output = observed output + c·2^w mod p
```

For the production ranges, `|C|<2^39`, so `c` can only be −1, 0 or +1 at
these widths. Direct production wire observations confirm both signs occur.
A borrow-only repair is insufficient.

The existing addend already exposes `sign(C)` as a linear form:
`addend_prog` feeds `o[13]` to `field_map`, which sign-extends it into the high
addend bits. The final `ladder_chunk` deliberately omits its outgoing carry.
Retaining the unsigned outgoing carry `r` would give **`c=r−sign(C)`**;
a new sign comparator is unnecessary. An exact chunk comparison can erase
that retained carry while the addend forms remain live, provided the subsequent
repair leaves its low comparison window unchanged. This is a design observation,
not an integrated phase proof.

The remaining difficulty is exact propagation through the arbitrary upper
payload and field wrap. The repository's ordinary unbound controlled constant
ladder for `±2^k` uses `255−k` Toffolis and as many carry wires: 199–205 for
the powers in these witnesses, **before** modular wrap, the boundary predicate
and its cleanup. That is a count of this existing primitive, not a lower bound
on all possible circuits or a measured complete repair. A naive repair at every
tick is too expensive for the present product margin. Reusing the supplied sign
and retaining a carry may still permit a better integrated construction; none
has been demonstrated here.

## The two square failures

Exact stage checks show both cases correct after division. Their full signed
square-preseed rail is then wrong while the slope register remains correct.
The signed preseed is decoded in full, including its extension; reading only
the low 256 bits would create false errors.

The precise faulty primitive is `square.rs::wcin_windows`, on C's 130-bit high
limb with 20 guard bits. Each event is checked against both exact field
arithmetic and the actual truncated integer replacement:

| Local / original 186-case input | First event | Additional event | Total square error |
|---|---|---|---|
| 20 / 136 | Shift 6 positive overflow past bit 156 | None | −2^156 |
| 26 / 156 | Shift 4 subtraction borrow past bit 154 | Shift 6 positive overflow past bit 156 | +2^154−2^156 = −3·2^154 |

The supplied carry-in is zero for all three faulty windows. Every directly
observed error exactly sums to the full square-stage delta. Subsequent multiply
work propagates that wrong square result. This mechanism is distinct from an
approximate phase-only borrow predictor.

## Uniform actual Y15 window +4: diagnostic only

A separate detached `window4-b3` increases the actual Y15 fold windows from
56/57 to 60/61 in both directions, uniformly over the source. Previous
`FOLD_GUARD` sweeps did not change this constant. **This is a capacity
experiment, not an exact repair:** widening does not fix the earlier negative
`W` equal-input counterexample, nor establish universal correctness.

Complete paired fresh censuses use label `failure-floor-window4`, batches
0–4095, 262,144 inputs per source:

| Diagnostic | Unsmoothed wide parent | Window +4 |
|---|---:|---:|
| Peak Q | 1,464 | 1,464 |
| Mean executed T on fresh census | 753,725.13 | 754,789.83 |
| Failed batches / 4,096 | 223 | 190 |
| Expected failed batches / 9,024 shots | 7.68 | 6.54 |
| Wrong-value shots | 202 | 167 |
| Phase-failing batches | 124 | 95 |
| Dirty batches | 0 | 0 |

Paired cost is **+1,064.71 T, standard error 0.96**. It cures 35 value-failing
inputs and creates zero new value failures on this paired census. Phase events
are not a monotone comparison because measurement consumption changes. This
variant is too expensive for the current product or our own Toffoli record and
remains incorrect. It was not screened or benchmark-qualified.

Its stream is
`40abbe691df74bec714c1f0f62ab3465f60bbcc73a16ced8e6c493fe481ac3af`.

## Evidence and reproduction

- [Verified diagnosis](boundary-verification.json), [29 exact fold reconstructions](boundary-reconstruction.json), [full first-transition data](result.json), [square deltas](square-first-stage.json).
- [Paired census analysis](window4-census-analysis.json), both complete census JSONLs in `evidence/`.
- [Complete source snapshots](source-snapshots.tar.gz): all 162 observer source files match the source manifest; both observer and window candidate are included.
- [Terminal logs, launchers, packets, patches and failed attempts](evidence.tar.gz), [archive hashes](evidence/collect-result.json), [protected-file check](evidence/protected-verification.json).
- [Final observer source manifest](evidence/manifest.json), final stream and binary hashes in `evidence/`.

Run locally from the repository root:

```text
.venv-research/Scripts/python.exe experiments/failure-floor-20261015/analyze.py
.venv-research/Scripts/python.exe experiments/failure-floor-20261015/reconstruct-boundary.py
.venv-research/Scripts/python.exe experiments/failure-floor-20261015/verify-boundaries.py
.venv-research/Scripts/python.exe experiments/failure-floor-20261015/analyze-census.py
```

For a fresh source reconstruction, create a detached B3 worktree and overlay
the relevant `src/point_add/` tree from `source-snapshots.tar.gz`. The observer
reads the preserved packets at the server experiment path. The archive also
contains the complete applicable patch, including new observer modules.

All jobs are terminal. Launchers use `setsid nohup`, dedicated logs and PID/exit
records, four build workers, one library thread, at most sixteen census workers
and a 60 GiB process address-space limit. Resource preflights are saved. Unrelated
workloads were untouched. The first missing-cargo startup, reverse-tape false
positives, and initial fold observer startup failure are retained and explicitly
superseded by the completed checks above.
