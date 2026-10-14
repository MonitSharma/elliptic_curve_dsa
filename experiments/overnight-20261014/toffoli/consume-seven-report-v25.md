# Low13 consumer boundary

Version24 extends the constructor through seven further written accumulator
bits, retaining the complete higher consumer obligations. All2,097,152
assignments to21 primitive inputs match26 independent integer outputs:
U3..U6, sign, H0..H6, low result0..12, and carry13.
The original correction field mapping places Q2..Q5 at bits6..9 and U0..U2
at bits10..12. Thus this consumes seven next bits; it does not consume all
seven U fields. That initial mapping ambiguity was corrected before generation.

Every remaining correction bit13..55 is reconstructed independently, including
the distinct17..31 and39..55 sign bands. The largest low total is16305, so
the retained carry13 captures all low overflow. All seven new accumulator bits
are arbitrary. The source uses38 ANDs; raw rank is22, target-inclusive rank46,
and the complete source span has rank60. The necessary value bound is24 ANDs.
This fourteen-direction rank gap is not an achievable saving or a width result.

Version25 runs one exact rank-minimum closure of that rank46 target interface.
It constructs four legal prefix ANDs (rank26), then returns trusted Z3 UNSAT
for every next affine product that extends that prefix while remaining in the
target span. The complete query and source descriptors are preserved. There
is no formal UNSAT certificate. This selected rank-minimum closure failure
does not exclude34-AND circuits using ten additional auxiliary directions,
other changed nonlinear output interfaces, or more general quantum circuits.

No native candidate follows. The higher ladder must accept carry13 with its
remaining fields; constructor erasures that used removed Q/U values need new
phase identities; all seven new carry coefficients and retained chunk endpoints
must be discharged; and the physical schedule must count all live fields and
garbage. Cleanup, arbitrary higher coordinates, exact source producer admission,
classical scratch, width and full executed cost remain unqualified.
