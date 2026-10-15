# Signed64 suffix equivalence argument

This is an advisory input-preparation component. It grants no value rejection,
phase conclusion, circuit correctness change, or production-search authority.

The frozen baseline is `rail-masks-20261016/rail8_masks.c`, SHA256
`ee7adffc1c7f21a6721ede20d722a69d6e3ab8bc648db4a74c403f440b0d7ba3`;
its library SHA256 is
`046dd5f1d11386550ec5234b955f6bc1974431e79a6b80499bda97da0ade3e90`.
`prepare.py` refuses other source/library bytes. It retains the generic loop
verbatim, except for the suffix dispatch. The same literal baseline loop body
is also included as a test entry, separate from the narrow implementation.

## Transition and bounds

The dispatcher scans backwards across the entire remaining table. It permits
a suffix only at an index at least one, and only if **all five** fields
`w,n0,n1,n2,nb` of **every** remaining row are <=61. The original validation
still requires `w>=1`, each `n*>=2`, `nb>=4`, and every width/anchor<=319.
The predicate does not assume table monotonicity. A changed table that violates
the bound postpones the transition or runs the unchanged generic code throughout.

At the end of each generic step, both rails are sign-extended to `wn`, the next
row's `w`. The optional fused trim also sign-extends to a width no larger than
that next `w`, so cannot invalidate the bound. Thus at a permitted transition
both rails are canonical signed integers represented identically by a signed
64-bit lane and by the baseline's five-limb sign extension. The actual frozen
table first qualifies at tick110: 28 tail ticks, maximum width60, with every
width field nonincreasing through the tail. Earlier operations are unchanged.

A signed<=61-bit value lies in [-2^60,2^60-1]. Negation lies in
[-2^60+1,2^60], and a sum or difference of two such values lies in
[-2^61,2^61-1]. These fit signed62 bits, leaving **two bits** of the 64-bit lane
unused for the largest temporary. All forced and predicted additions have
operands freshly sign-extended to at most61 bits. Arithmetic shifting cannot
increase magnitude. All stored rail states are narrowed back to <=61 bits.
There is no multiplication or left-shifted arithmetic rail in the tail.

Correction to the pre-test declaration's shorthand: negation need not fit the
same61-bit signed range when the operand is -2^60; it fits62 bits. The above
sum bound remains62 bits, and is the bound used by this proof. No code change
was necessary for this correction.

## Instruction correspondence

`sx64(a,w)` performs a logical left shift by64-w followed by arithmetic right
shift by64-w. For 1<=w<=61 this is exactly signed extension of the low w bits.
The AVX512 intrinsic operations define bit-level semantics and do not rely on
overflowing signed C arithmetic or implementation-defined C signed shifts.

Both conditional negation and addition are modulo2^64 intrinsics, but the
signed62-bit bound proves that their result is also the exact mathematical
signed result. Therefore their subsequent arithmetic right shift matches the
baseline's320-bit arithmetic shift. The same argument establishes that each
`different` overflow observation is equivalent to comparing the low64-bit
results: both sides already have canonical sign extension outside that lane.
Prior overflow flags are carried into the narrow loop and ORed without loss.

The predictor's sign is bit63 of the narrow canonical integer, equal to bit319
of the generic sign extension. Bits1..4 are unchanged, including negative
values and rails narrower than those positions. Predictor sign masks, boolean
operations, captured states, forced-sign flags and the fused trim schedule are
the same expressions and instruction order as the original loop.

`window64` returns zero before a shift whenever width-1<=low. Otherwise
0<=low<width-1<=60, and count=min(k+2,width-1-low)<=22. Complementing a negative
rail with its sign mask matches the low64 bits of the generic complemented
320-bit rail. No needed bit lies above bit59; the generic next-limb contribution
therefore cannot enter the masked result. The largest subsequent window left
shift is by2, so at most24 significant bits are produced. Anchor319 and other
large anchors take the early-zero path. Every count-derived mask shift is<64.

The variable final shift uses `c.extra` in0..3. It follows sign extension to
`nb>=4`, so the original redundant final sign extension remains redundant.
Reconstructing the high four limbs from the narrow sign bit restores exactly
the generic final representation. The original final +/-1 checks consequently
produce the same nonunit mask, and the complete original population wrapper
keeps all padding, partial-vector and return-code behavior.

## Validation scope and limits

The ordinary corpus is unchanged:262144 population flags,517 specified edge
inputs, six partial lengths, changed valid tables, shortened tables and invalid
table/error controls. The direct test entry compares complete final rails and
overflow against the literal generic loop for arbitrary signed entry states at
every actual suffix tick, both fused/divide and multiply branches. Additional
synthetic-width controls cover every signed width1..61 and arbitrary anchors.
A deliberately logical-right-shift sign-extension variant must fail these
tests. All measurements are component timings under co-running server jobs;
they do not establish an end-to-end operational speedup.
