# K32 loan schedule: obligations and proposed integration

Status: ideal-state ownership argument and tested arithmetic components.
No complete circuit result, width reduction or submission is claimed.

## Admissible active sizes

For positive extended-Euclid states,
`p = t_j*r_(j-1) + t_(j-1)*r_j`, with `r_(j-1)>r_j>0`.
In the ordinary HR mode, `r_j >= 2^128`; consequently
`t_j < p/r_(j-1) < 2^128`. In the delayed HR crossing, the source chooses
HR only while `bl(r_j)>bl(t_j)` and `bl(r_j)<=128`, so again `t_j<2^128`.
For HT after either crossing, the divisor is `r_j<2^128` and decreases.
Thus every ideal active V call has `1<=SY=bl(Y)<=128`.

The switch column itself has no HR/HT window update on the switching route.
The delayed route takes its HR step, followed by an excluded no-step column.
`frogdrop_col.rs` stage 1 implements `sw`/delayed selection. Stage 2's `cp.psw`
branch explicitly clears and refills the first HT size from Q before entering
`middle`; its larger incoming size describes the top X, not V's divisor Y.
`midg.rs` uses `hr_lits` and `ht_act` to exclude switching, delayed no-step and
done routes. Done lanes may hold a high-Q counter and are not assumed clean.

This proof is conditional on the column's ideal arithmetic invariant. It does
not establish that states corrupted by an earlier failed column are admissible.
The independent original-packet audit checks 2,689,852 ideal stepping states,
including 7,343 delayed-HR states, 21,057 SY98 states, 20,784 SY99 states and
6,065 SY128 states. This is supporting packet evidence, not a universal proof
of emitted gates or finite precision.

## Q121–Q127 at every V call

Keep current QB23: stored quotient bits have indices `kb=0..22`.
For the small branch `SY<=98`, Y occupies only Q0–Q97, and the largest
parked quotient index is `SY+22<=120`.

1. Initial HR V: Q contains Y, quotient owners in the ring/SX are clear.
2. HR inverse V: the paired care rotation has parked quotient bits at
   Q[SY+kb]; all Q121–Q127 remain zero.
3. HT forward V after the exact division/payload: the first quotient parking
   record has returned, X has been reconstructed, then `park` puts its bits
   at the same Q[SY+kb] indices. Q121–Q127 remain zero.
4. Final HT inverse V: reverse search has erased the quotient owners; Q holds
   Y and Q121–Q127 are zero.

Payload adders read Q as a source and restore all temporary source carries.
`ring_cadd2_loan` returns its borrowed bank and carries at each add boundary.
The map and done-counter parking occur outside these four V boundaries.
Active stepping counters are zero; inactive counters are allowed arbitrary
data in these same lanes. The proposed V helper banks must exclude Q121–Q127
when those lanes join the remainder. In the current public parameter range,
the conservative `p_bank_lo=cp.sy.1+ kmax` already often leaves the bank empty;
an explicit exclusion is still required in the candidate.

Future QB24 would require the threshold97, because `SY+23<=120` is needed.
This schedule deliberately leaves the quotient cap unchanged.

## Full size partition and inactive extension

The low seven size bits encode active128 as0. The small positive cubes cover
1–98; the large positive cubes cover99–127 plus0. The generated audit checks
that exactly one cube matches for every eight-bit word. On active sizes
1–128, the split is exact. Inactive values129–255 can alias the small branch;
the window increments retain `act` as an independent control in every cube.
No branch predicate is computed into a clean scratch flag.

SY's low seven bits are read-only across V. `sy7_normal` and the crossing
reserve can modify SY7 around parking, but never the selector bits. The
comparison-size scratch remains SX0, separate from the extended remainder.
It is returned before any increment and after each threshold query. Cube
controls therefore cannot dirty that scratch or depend on arbitrary R data.

On inactive routes, the borrowed remainder may be arbitrary. The odd-divisor
restoring step is a permutation on both `R<D` and `R>=D`, as established by
the solver and exhaustive emitted-gate tests. `fv(window=true)` followed by
inverse `fr(window=false)` restores that arbitrary remainder when `act=0`.
The comparator's virtual divisor has low bit1 and leading bit1 on inactive
routes too; `cmp_csub_carries_vh1` implements the leading bit virtually even
when its physical shared lane contains arbitrary remainder data. The K32
fixture tests this inactive identity directly with arbitrary physical bits.

## Required changed-source checks

K32 v2 passes its partition component and column35 regression, with separate
source hashes and patch recorded in `K32_COMPONENTS.md`. Broader column and
payload phase obligations remain. Use K25 on the large branch and K32 on the small branch, protect all32 divisor
head destinations during the care rotation, and remove Q121–Q127 from helper
banks. Native column tests must cover all four V boundaries, both crossing
modes, first HT refill, SY98/99/128 and inactive high-bit/counter aliases.
They must include payload and measurement phase as well as dirty passengers
and inverse restoration. No full benchmark is approved at this stage.
