# Front-seam carry-phase precision

The existing phase comparator is correct for its stated predicate. Its original
local proof quantifies every measurement and arbitrary data/classical inputs,
with only allocated scratch assumed zero. The new comparator has the analogous
universal proof. This repair improves the predictor's precision; it does not
correct a missing Clifford in the original comparator.

Let N=256 and let x and o be the original unsigned coordinate words. The
source-bound exact R5 prefix complements x, adds the classical o with full
carry, and complements the result. Hence it produces

    D = (x - o) mod 2^N,       ov = [x < o],
    D + o = x + ov*2^N.

The R5 carry induction is exact: with classical addend bit a, quantum bit b
and incoming carry c, its next carry is
`((c XOR a) AND (b XOR c)) XOR c = MAJ(a,b,c)`; the sum bit is
`a XOR b XOR c`. Bit zero uses a classically conditioned CNOT. The descending
measurement erases cancel each carry's AND phase using those same controls.
Thus complement/add/complement gives the identities above for every N-bit
x and o, including noncanonical values. No distributional assumption is used.

The entire actual subtraction prefix [56381,62509) equals the original raw
source prefix. Conservative propagation through the complete public prefix
proves every subtraction auxiliary q512..767 zero at entry for arbitrary
declared quantum/classical inputs and all measurements. Input x has not been
written earlier, and classical ox is immutable throughout the circuit.

The actual intervening low fold contains two inherited edits. They remain
verbatim. A gate-level interface check proves that q235 is untouched, each
q236..255 receives exactly its original unconditional complement, and ovq767
receives four unconditional X gates with no other quantum writes. Consequently
the high comparison bits still represent D, regardless of any finite-fold
approximation, inherited low-fold cut, or dirty low-fold temporary. This proof
does not assume that the low fold computes an ideal modular value.

Write H_k(z)=floor(z/2^(N-k)). The original k=20-bit comparison predicts

    P_k = [H_k(D) + H_k(o) >= 2^k].

The next lower bits d and a give the widened predictor

    P_(k+1) = [H_k(D) + H_k(o) + (d AND a) >= 2^k].

This is the carry out of the same high window with the exact one-bit lower
borrow. Here a is the immutable classical ox bit235. After the original HMR,
ovq767 is zero. Under its outcome m, a conditioned CNOT from q235 computes
d AND a into this same wire. The comparator receives it as its borrow and
restores it. A second conditioned CNOT clears it. Two extra CNOTs in the
first-carry conjugation connect and restore this borrow. There are no new
qubits, Toffolis, measurements, classical writes or condition-stack changes.
The first AND and its measured phase erase use the same new borrow form.

For every x and o, P_k <= P_(k+1). If ov=0, D+o=x<2^N, so no high-prefix
sum can overflow and both predictors are zero. Therefore

    P_k <= P_(k+1) <= ov,
    (ov XOR P_(k+1)) <= (ov XOR P_k).

The component's residual phase coefficient can only improve. Both local
helpers prove `phase_delta = m*(ov XOR predictor)` for every internal MR.
Every quantum output is restored/cleared and every classical output is
identical under the unchanged measurement-word coupling. An independent
local ternary replay proves all comparator scratch clean at entry; it permits
all input data/classical bits and every earlier MR to be arbitrary.

The complete circuit can still have another phase error that previously
cancelled this one, so component improvement does not imply paired global
shot-by-shot monotonicity. The separately predeclared fresh full-circuit gate
checks the actual failure rate. Its result is required before eligibility.

Because the classical and MR/snapshot operation skeletons and the ordered
Toffoli condition skeletons are identical, every executed Toffoli count is
identical under coupled inputs and MR words, not just the mean. All original
operations outside the named seam are byte-identical; the two inherited cuts
and all original table assertions are retained.
