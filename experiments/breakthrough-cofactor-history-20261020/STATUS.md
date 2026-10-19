# Integer-cofactor history reconstruction component

Positive mathematical and native component result; no complete point-addition
circuit, width reduction, statistical gate, nonce search or scored record.
For C divisible8,D odd, q=7-2s0-4s1-8s3 and e=3+k1+2k2, define
Cnew=C+qD,Dnew=2^eD. The two forced signs follow from low cofactor bits; the
two exponent flags follow from the2-adic valuation of Dnew. Thus four flags
can be reversibly erased while retaining s3. The first macro-step is exceptional.

Unbounded-integer solver checks:13 UNSAT domain queries, plus a SAT negative
control showing why the first-step admission is necessary. Native codec:
14 Toffolis, at most3 clean scratch, zero measurements or phase gates. Three
native tests pass: all128 quantum lookup cases,3072 signed coefficient residue
cases with exact inverse, and an incorrect-history dirty-flag negative control.
The initial test-helper generic-type compile failure is preserved separately;
the passing v2 changes only that helper type and leaves primitive gates intact.

The4096-field-input integer model and67584 decoder controls pass determinant,
modular-scaling and inverse checks. Model history averages128 bits versus621
for five-bit records. These are model dimensions, not physical resources:
cofactors grow, and observed maxima must not become allocation cuts.
bounds-study.py enumerates all inputs of11 small primes and4096 field inputs
per rule. Neither the generic nor minimum-next-target rule gives a constant
multiple-of-p cofactor bound; growth remains a serious allocation issue.

The28-member native evidence archive is locally verified. SMT/model evidence
is preserved alongside it. Complete coefficient bounds, endpoint handling,
final power-of-two normalization, multiplication and cleanup remain unimplemented.
