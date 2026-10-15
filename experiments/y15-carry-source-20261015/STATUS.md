# Opposite borrow requirements in the joint cleanup

Completed 15 October 2026. **Verified diagnosis and finite designs only;
no qualified resource score.**

## Exact production observation

The source observer reproduces the wide Y15-seedless stream byte for byte:
`0e5b5f6f2640da7e50c6bb0ae788f093d4df7fedba811007b6a2894879dd6b3e`.
Wire135 / bit1555 are reused at many locations, so the exact-state observer
selects the full random-read ordinal780824, counting Hmr and reset operations.
It explicitly checks that the intended measurement bit flips.

This identifies **reverse multiply tick1**, the Y21 top-cut joint cleanup in
`y15_onefold.rs:2770`. Raw operation9548660 corresponds to optimized
operation9553940. Exact arithmetic from the routine's entry operands gives
g0=1, h1=1 and m0=g0 XOR h1=0. The complete after-add sum agrees with that
calculation. The active reconstructed h1 is also1, so the carry reconstruction
is correct for this case.

The21-bit comparison sees equal upper words0x1fffff and0x1fffff. Its seedless
borrow0 returns false, but the exact g0 is1: the omitted lower bits require
borrow1. The correction therefore introduces a phase of1. Both all-zero and
single-flip runs match the protected simulator in all quantum words, classical
bits, phase and executed Toffoli count. Both produce the correct point value;
their phases are0 and0xffffffffffffffff respectively across64 replicated lanes.

The earlier forward tick124 witness required borrow0 for equal upper words,
where its source predictor supplied1. This reverse witness requires borrow1,
where the seedless rule supplies0. **A constant predictor cannot repair both.**
These observations cover one fixed input and two measurement assignments per
case; they do not prove that carry reconstruction is always correct.

The raw state-observer stream is
`84f472d7a58784bf49014031c74c6885a5914448c3e547a4aa5f415eb419809f`.
It is pre-Y33 diagnostic evidence, not a final candidate stream or score.

## Rejected shortcut

The [carry model](chain-model.json) evaluates three policies on348160 inputs
each, exhausting widths5–8 with all words and independent complement choices.
At width8, the original source-seeded chain has7872 wrong joint corrections;
forcing its initial carry to0 gives14848, and adding one reconstruction bit
still gives10752. The latter has fewer wrong top carries alone, but worse
combined phase correction. Thus separate approximation-error counts do not
justify this shortcut: their correlations matter. The model omits folds and
is not a quantum phase proof or a production failure-rate estimate.

## Exact zero-payload design

The [zero-wrapper model](zero-wrapper-model.json) verifies42576 cases for
division and multiplication across seven small primes. For nonzero x, separate
flags identify physical zero encodings0 andp:

1. Normalize a flagged p to0 while retaining its flag.
2. For division, replace a flagged zero payload with x. Nonzero division gives1;
   XOR1 on the flagged branch to restore0.
3. For multiplication, replace a flagged zero payload with1. Nonzero multiplication
   gives x; XOR x on the flagged branch to restore0.
4. Restore the p encoding when its flag is set, then uncompute both flags from
   the resulting zero encoding.

Every tested mapping is a permutation and returns its flags to zero. This
extends the earlier multiplication-only design with a division wrapper that
does not require a second inverse computation. It assumes a phase-correct
nonzero oracle with canonical nonzero outputs. No quantum implementation,
gate count or production phase proof has yet been established.

Next verify the actual divide/multiply interfaces, coordinate seams and seed
fusion before implementing the wrappers. Division needs the true denominator
x2-ox; disabling fused coordinate seams is one explicit option whose cost must
be measured. The wrappers address zero payload y only. They do not solve
zero multiplier x, the independent P=-2A failures, or residual rail errors.
Keep Toffoli and product qualification separate and run unchanged full benchmarks
only on final source after the required correctness checks.

## Evidence

Origin PID3165882 and state PID3169457 exited0. All57 artifacts, both source
patches and the external runner patch pass
[local verification](local-verification.json). Protected files match B3.
[Receipt](evidence/receipt.json) · [Exact diagnosis](analysis.json).
No job from this cycle remains active; the separate failure census was left
untouched.
