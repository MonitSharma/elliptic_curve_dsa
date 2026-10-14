# Cubic arithmetic and conservative producer-domain probes

These are exact finite value-interface results. They produce no complete
constructor, native phase qualification, or resource record.

The source-bound 14-input constructor has a unique cubic extension of the
closed rank23 prefix inside its rank40 target span. Version20 identifies it as
`F = Q3 + C3 + A + L = OR(k1,k2)*v3 + e2(acc2,Nm2,R1,D+L)`, where
`A=acc2+Nm2`, `D=acc1+Nm1`, `L=R2+(acc0+Nm0)*D`, and `v3=acc3+C3`.
All16,384 truth rows verify both identities. The explicit four-AND construction
adds three independent outside directions and gives a rank43 desired interface,
with a necessary28-AND value budget. Version23 independently verifies every
prefix gate and mapped target on all16,384 rows, then finds trusted solver
UNSAT for the first further rank-increasing affine product inside that interface.
This closes this selected prefix/interface; it does not exclude other28-AND
constructors.

Version22 asks whether this scalar can be built with at most three ANDs from
seven independent inputs. It includes all128 scalar truth assignments. The
restriction `acc0=Nm0=R1`, `acc1=h`, `Nm1=R1`, `acc2=a`, `Nm2=n`,
`acc3=v`, and `E=acc4=acc5=0` makes every rank23 seed value affine in those
seven inputs. The solver returns UNSAT in13.86 seconds. Operand constants may
be removed sequentially because `(a+1)b=ab+b` and
`(a+1)(b+1)=ab+a+b+1`; substituting each normalized gate preserves subsequent
affine operands and final affine output. The output constant is zero because
all normalized inputs/gates and the target vanish at the origin. Only
commutative operand ordering is added, and unused/redundant gates are allowed.
This is a scalar/restriction negative, not a global27-AND constructor lower
bound. The restriction is not claimed admitted by the genuine producer filter.

Version21 separately tests a conservative source-integer producer filter.
The baseline `y15_onefold.rs` header specifies the259-bit integer
`X=T+S0+2*S1+4*S2`, with each `Si` the256-bit source or its complement.
The forward body broadcasts each sign into the source before its corresponding
add, and passes its original three high wires into `fold_fwd_v2` before ESh
cleanup/reconstruction. For arbitrary unsigned256-bit `T,B`, not a canonical
field restriction, this gives
`X=T+(7-2*Nm)*B+Nm*(2^256-1)`, `E=floor(X/2^256)`.
With `M=2^256-1` and `a=7-2*Nm`, monotonicity yields
`X_min=(Nm+min(0,a))*M`, `X_max=(Nm+1+max(0,a))*M`.
The resulting E ranges by Nm are0..7,0..6,1..5,2..4,2..4,1..5,0..6,0..7.
All46 pairs, all64 low-accumulator values, and all4 shift patterns are retained:
11,776 rows in the original16,384-position truth layout. Exhaustive4-,6-,8-bit
three-add arithmetic checks cover559,104 inputs and attain all46 support pairs.

This reduced domain retains ranks raw15, target40, closed seed23. Its quadratic
span remains228 (union target245); its cubic span is1262 (union target1278).
The general one-auxiliary sequential escape query returns trusted UNSAT in
0.342 seconds. An independent parser verifies the exported SMT as exact
coefficient ANFs for all89 coefficient assignments, including1238 membership
equations, the nonzero extension, and implied outside-direction clauses;
it detects a removed cubic-term fault and recomputes ranks with low pivots.
The source-integer argument does not certify every producer gate recurrence,
open-carry normalization, higher-coordinate quantum phase, or full circuit.
Therefore this result stays a restricted arithmetic-domain negative; the
all14-input lower-bound report is not automatically transferred to fullbody.

All solver negatives are trusted Z3 results without formal UNSAT certificates.
Compact summaries bind raw query, log, PID/exit and settings hashes; raw evidence
is preserved under `research-output/overnight-20261014/toffoli/`.
