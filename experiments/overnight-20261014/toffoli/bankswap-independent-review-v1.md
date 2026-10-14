# Independent HT25 bank-swap source review

The reviewed prototype is `candidate-ht25-bankswap-v1`, derived from frozen
HT25-v9. Its `midg.rs` raw SHA256 is
`9526185c20d58b8e251ebcfc43ec3eba0c7c9e26fcbed234557f1edba1c7a1af`.
No blocking source-level operator or ownership issue was found under the
explicit admitted caller contract below. This review does not qualify native
measurement phase, a full operation stream, or a point-addition resource score.
Neither v9 nor its full-generation job was changed by this reviewer.

The saved activity wire is `act=sc.g`, separate from both work and reserve
banks. The transfer predicate is ACT and low-SY bits3..6 equal96..103.
Its control excludes PH and SY7, both of which are reserve data targets.
`SX0` must be clean zero at entry: the two XOR computations of the predicate
surround eight controlled swaps and return SX0 to zero before reciprocal use.
This clean-flag requirement is an existing V-entry owner obligation, not a
claim of correctness on a dirty SX0 input.

On selected active shots, the parked quotient is confined to Q indices
SY+kb<=103+24=127. Hence the eight reserve fields are clean, whereas
Q120..127 may hold arbitrary parked data. The first controlled swap sends
that data to reserve and supplies clean Q work lanes to the R32 driver.
The driver does not read reserve; the inverse transfer restores both banks.
ACT and low-SY selector bits survive the driver, so the two transfers use
the same quantum predicate even if PH and SY7 carry arbitrary parked data
between them. This is coherent controlled conjugation, not a classical
branch assumption.

The production read sets are R24/Q120..127, the full32-bit divisor head,
window, SZ, SX0, and explicitly separate dirty/helper lanes. The source's
traversal constructor allocates ring, Q, SY, SX, PH and pool in distinct live
registers. Narrow `ColScr::carve_col` maps SZ to pool0..7, SW to pool8,
and the bank's other pool roles to9..11; ACT is pool12. Thus SW is absent
from narrow SZ and the full ring head is disjoint from every reserve field.
The prototype asserts reserve disjointness from R, window, helpers, controls
and dirty lanes. As future-caller hardening, assertions against full `z32`
and `sc.sz` would make the currently source-established disjointness explicit;
their absence is not a demonstrated alias in this constructor.

The old global `size_partition` remains SY1..95 versus96..128. Only the
HT-specific merged driver extends its small selector to1..103; its R24
complement is104..128. These cubes are disjoint over all256 SY words.
The low-seven-bit96..103 predicate also selects224..231, but those words
are outside admitted active HT/HR callers; the new fixture assigns ACT zero
there and arbitrary bank data. When ACT zero, the transfer is the identity
and the paired driver must restore arbitrary remainder data and phase.
For active SY104..128 the R32 window predicate is false and its counter
forward/inverse must likewise be identity; the unchanged R24 path supplies V.
These paired-driver phase claims remain native/ALLMR verification obligations.

There is one additional admission nuance: the merged R32 call uses
`small=true`, enabling SZ clipping that the old96..103 bank call bypassed.
For admitted active bank shots, positive `Z*Y<p<2^256` gives
`SZ+SY<=257`, hence SZ<=161. The source has26 reciprocal iterations,
j<=25, so SZ+j<=186 and clipping never changes those active window gates.
Therefore the conjugation argument is on this admitted arithmetic domain;
it is not unrestricted operator equality for arbitrary active SZ255/SY96.
Inactive arbitrary states and the wide-SZ path remain separate tests.

The HT guard requires the whole SZ envelope at most255. A wide column with
SW serving as ninth SZ bit therefore takes the original non-bank branch,
with unchanged selector boundary. The final HT exit's PH normalization is
still outside the entire inverse V form: flip PH, replay inverse V, flip PH,
then uncompute ACT. Inside transfer and V, PH is data rather than a selector.

The transfer primitive itself contains no measurement. Its empty temporary
list selects a five-control borrowed-dirty MCX, implemented by twelve exact
CCXs. An independent exhaustive Boolean calculation checks all512 assignments
to its five controls, target and three dirty ancillas, including arbitrary
dirty values and restoration. Eight Fredkin swaps contribute eight CCXs,
giving32 CCXs per transfer,64 for the conjugating pair around one V form.
These are primitive emitted costs, not a complete candidate resource count.
The unitary permutation argument preserves arbitrary incoming phase;
measurement phases inside the reused reciprocal driver still require the
prototype's native and all-measurement fixtures.

Review evidence binds exact parent/prototype source, patch and helper hashes.
The reviewer launched no server workload and made no candidate source edits.
