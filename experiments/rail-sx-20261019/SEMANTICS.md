# Sign-extension equivalence and limits of the timing result

For a fixed width w in1..319, both helpers map each output bit to either its
unchanged low input bit or input bit w-1. The original helper masks low bits
and fills higher bits from that sign bit. The new helper preserves complete
low limbs, shifts the partial limb left then arithmetically right, and fills
higher limbs from its sign. Shift counts lie in0..63. Branches depend only on
w, and AVX512 lanes are independent.

These are linear maps over the320 input bits. The executed tests include zero
and every single-bit basis vector at every valid width, so equality of those
basis images establishes equality for arbitrary320-bit input words under the
documented bitwise shift/sign-copy semantics. Single-clear-bit, alternating,
extreme and fresh random vectors add implementation checks. Invalid widths
are rejected by the test entry, and all callers in the unchanged rail kernel
derive supported widths from the unchanged checked step table.

All other rail-kernel source stays identical. Thus replacing this helper
preserves advisory flags for every supported call. The frozen262144-point
reference population,517 adversarial denominator pairs, partial vectors and
a changed step table all match in the executed controls.

The initial dynamic-index implementation is correct but substantially slower.
The fixed-limb branch implementation is about1.173x faster in five alternating
kernel trials. In the complete disabled512-nonce prefix, the median ratio is
1.0496, but two of three paired trials are slower. This does not establish a
reliable complete-search improvement. Keep the active runtime unchanged.

The prefix experiment uses only the already gate-eligible parent4 source and
matches every row of its existing qualified prefix. It adds6x512+11=3083
repeated diagnostic attempts, all within the already screened1..4096 range;
it adds no unique nonce beyond the live operational prefix and selects none.
Disclose these repeats if parent4 is eventually submitted. No new-source
nonce is screened, no circuit is changed and no resource record is claimed.
