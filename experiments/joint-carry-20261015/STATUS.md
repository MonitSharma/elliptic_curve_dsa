# Exact diagnosis of the Y21 joint-carry phase error

Completed 15 October 2026. **Diagnosis only; no qualified resource score.**

The full raw-circuit observer identifies forward tick 124 as the source of
the preserved phase witness. The reconstructed carry is correct on this
input. The statistical comparison seed is wrong.

## Production evidence

At entry, target T=0, source B=p (the secp256k1 modulus), and all three sign
bits are zero. Exact integer addition gives X0=p, g0=0 and h1=1. The observer
checks the complete X1 sum against the actual after-add state. At the measured
cleanup, m0=g0 XOR h1=1.

Flipping the selected measurement activates the intended correction branch.
The rebuilt h1 is 1, correctly cancelling the measurement's phase. The
following 18-bit comparison then sees **equal words 0x3ffff and 0x3ffff**, but
its source-bit borrow predictor is 1. It consequently emits a phase of 1
instead of the required g0=0, reintroducing the error. The reconstructed
comparison window also equals the exact X0 window.

The selected event is raw operation 3609779, random read 278924 (counting both
Hmr and reset operations), Hmr qubit221 / bit1566. This corresponds to the
optimized stream's previously certified measurement278924. The observer
explicitly checks the selected classical bit after measurement.

Both runs match the unchanged protected simulator in every quantum word,
classical bit, phase and executed Toffoli count. Both return the correct point
value. All-zero measurement outcomes give phase0; flipping only the selected
event gives phase0xffffffffffffffff across the64 identical lanes. This covers
one fixed input and two measurement assignments, not all inputs or outcomes.

## Independent finite model

The [arithmetic model](model.json) exhausts349184 cases at widths4–8, with all
target/source words and independent complement choices. It confirms that
truncated carry reconstruction and a source-bit comparison seed can each
fail. Supplying the true carry at the reconstruction boundary reproduces the
exact carry and comparison window; using the true low-word borrow makes the
combined modeled correction exact in every case.

The model omits the production fold and rails. It is not a quantum phase
proof and has no measured gate cost. The correct production carry in the
observed case does not establish universal correctness of its reconstruction.

## Preserved attempts and evidence

| Attempt | PID | Exit | Status |
|---|---:|---:|---|
| state | 3147702 | 1 | Preparation match was not scoped to `body`; no workload |
| state2 | 3148110 | 101 | Observer needed an explicit U256 shift type |
| state3 | 3150016 | 0 | Intended flip misaligned: counted Hmr but omitted reset random reads; invalidated as a measurement counterexample |
| state4 | 3152831 | 0 | Correct alignment, explicit measurement check, native state/phase agreement |

All attempts are terminal. The two generated raw streams are byte-identical;
the correction changed only observation bookkeeping. They are pre-Y33 raw
streams, not a new final candidate or scored benchmark.

All83 artifacts, four candidate/observer patches and the external runner patch
pass [local verification](local-verification.json). Protected harness, simulator,
reference and Cargo sources match B3. Failed attempts and invalidated evidence
remain in the [receipt](evidence/receipt.json).

## Next experiment

Test a uniform Y15 boundary-comparison policy that removes source-bit predictors
and includes the former seed bit in the compared window. `y15_split_spec`
returns statistical source indices, so this policy need not discard genuine
retained carry wires. Preserve existing window coverage even when refinement
changes its width. Measure its full fixed-input arithmetic/phase behavior and
width/Toffoli tradeoff in isolated narrow and wide candidates. A seedless
truncated comparison is still approximate; passing this counterexample alone
will not qualify it or resolve the five rail and zero-multiplicand failures.
