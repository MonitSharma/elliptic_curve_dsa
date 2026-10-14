# At least27 ANDs for the fixed constructor value contract

For the specified14-input constructor and its28 retained scalar output
functions, a straight-line XOR/AND program needs at least27 ANDs. This statement
uses the exact all16,384-input truth contract and trusted Z3 UNSAT. It does not
assert quantum optimality, a mean executed Toffoli lower bound, complete cleanup
cost or a new point-addition resource record. No formal solver certificate is
saved. The existing31-AND source is not proved optimal.

## Spaces and independently checked ranks

Let I be the raw affine input space, W the span of I and every required output,
and S the saved eight-AND closed space. Constant1 belongs to I and S. The
source is c5bb1ec876db859a3f9f8a9052c140a145df834e and canonical y15 LF hash
879b85060f6a5cfa412561d64860f1cab697f7a334f180f5be9102070d5a23b9.

| Space | Dimension |
|---|---:|
| I |15|
| S |23|
| W |40|
| P2(S) |228|
| P2(S)+W |245|
| P2(S) intersect W |23|
| P3(S) |1266|
| P3(S)+W |1282|
| P3(S) intersect W |24|

Pk spans S and all products of at most k basis functions of S. The independent
low-pivot rank implementation agrees with the search's high-pivot construction
on all primitive truth rows. In particular, I is contained in S, and
P2(S) intersect W equals S. Thus any AND of affine S functions that lands in W
already belongs to S.

## Why any26-AND program must have an escape

Suppose such a program exists. The span F of all raw inputs and all computed
AND functions has dimension at most15+26=41 and contains W. If F is contained
in W, all gates stay in S by the closed-space induction and cannot compute W.
Consequently F has dimension41 and is W plus one outside direction. A zero or
redundant AND would reduce its rank to at most40, forcing F=W and the same
contradiction. Fewer ANDs are already excluded by rank and closure.

Let p be the first AND output outside W. Earlier functions lie in S, so p is
a product u*v of arbitrary affine S forms. F=W+span(p). Until the first AND q
outside S+span(p), every available function lies in that smaller space. Such
a q must exist because its dimension24 cannot contain W of dimension40.
Since q belongs to F, there is epsilon in{0,1} such that
q+epsilon*p belongs to W outside S.

Each operand of q is an affine S form plus zero or one copy of p. If neither
uses p, q+epsilon*p lies in P2(S), and its intersection with W is S; this cannot
escape. If one uses p, swap operands if necessary to write q=(a+p)*b. If both
use p, the Boolean identity

`(a+p)*(b+p) = (a+p)*(a+b) + a + p`

gives a one-p product modulo S+span(p). The known affine term a can be removed
without changing whether the result lies in W outside S, and the additional p
is absorbed into epsilon. Thus every possible first escape is covered by

`p=u*v; q=(a+p)*b; q+epsilon*p in W outside S`.

## Constants and redundant representations

Write u=u0+c and v=v0+d, where u0/v0 have no constant coefficients. Replacing p
by p0=u0*v0 changes it by l=c*v0+d*u0+c*d in S. This preserves both W+span(p)
and S+span(p), and rewrites q as `(a+l+p0)*b`. The extra epsilon*l lies in S.
Removing a constant from a changes q by a known S multiple of b. Removing a
constant from b changes q by a known S term plus p, which epsilon absorbs.
Thus the solver may set all four operand constant coefficients to zero without
excluding an escape. No independence of the23 S basis functions as Boolean
indeterminates is assumed: their exact truth relations enter the equations.
Changing the affine basis of S or W only changes coordinates, not the spaces
or the existence of an escape.

## Exact query and independent encoding audit

The [description](sequential-escape-v19-description.json) spans231 quadratic
and1540 cubic monomials of the22 nonconstant S basis functions. Their projection
modulo W gives1242 membership equations,529 kernel relations and one extension
coordinate modulo S. Repeated indices reduce by x*x=x. Two thousand direct
truth tests additionally check the numeric square-free coefficient construction.

The [solver receipt](sequential-escape-v19-summary.json) returns UNSAT for all
four arbitrary affine operand forms and epsilon, in0.397 seconds. The exported
SMT query has1,130,577 bytes and SHA256
75298062d5e70372c92e010ecafbe132ac8aac4aa86f92cc5684dff3ee845791.

The [independent audit](sequential-escape-v19-audit-summary.json) parses that
actual SMT query and expands its Boolean expressions into canonical ANFs in
all89 coefficient variables. Independently generated polynomial multiplication
matches every membership, extension and implied outside-p equation exactly.
This covers every assignment to those89 coefficient variables. A removed real
cubic coefficient is detected, and independently implemented low-pivot truth
ranks reproduce the table above. The audit checks the encoding and ranks; it
does not replace a formal UNSAT certificate or independent SAT solver.

The missing first escape contradicts any program with26 ANDs under this fixed
value contract. At least27 are therefore necessary, leaving at most four ANDs
of possible construction savings against the31-AND source. Neither an
attaining27-AND witness nor a full arithmetic/cleanup implementation is known.
