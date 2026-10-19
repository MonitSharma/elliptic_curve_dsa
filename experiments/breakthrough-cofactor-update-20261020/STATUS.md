# Native signed cofactor update and inverse

Positive arithmetic component; no point-add integration or resource record.
Implements Cnew=C+(7-2s0-4s1-8s3)D, variable sign-aware scaling Dnew=2^eD,
four-flag erasure and explicit inverse. Uses the existing phase-correct Gidney
carry ladder through a diagnostic wrapper. Protected17 files remain unchanged.

Six native controls pass: the three history-codec controls,131072 exhaustive
eight-bit signed-adder inputs,1792 signed sixteen-bit edge/wrap cases with
inverse, and every physical measurement-phase coefficient on64 basis states.
The phase probe checks that random outcomes only control single phase gates;
therefore its one-hot probes cover the linear phase coefficients for those
bases, including reset draws. At16-bit word size, a forward component emits
93 Toffolis including scaling and history cleanup. This is a component count,
not an extrapolated scored result. Integer use requires a proved coefficient
bound and excludes overflowing source shifts; target-word wrap is tested.

The18-member native evidence archive has been locally verified. The code is
not part of the accepted circuit. Fixed allocation, GCD endpoint, variable
normalization and complete multiply/cleanup budget remain unresolved.
